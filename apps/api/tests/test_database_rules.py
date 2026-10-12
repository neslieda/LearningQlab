"""Rules the database itself enforces, checked with raw SQL (added after the slice 2a reviews).

These hold whatever code path writes to the tables. The role tests show the deployment
requirement in docs/SECURITY.md section 10: the runtime role is neither owner nor superuser.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import CheckConstraint, Connection, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

import qlab.audit.models
import qlab.rights.models
import qlab.syllabus.models  # noqa: F401
from qlab.audit import service as audit
from qlab.database import Base
from qlab.rights import service as rights
from qlab.rights.models import RightsRecord
from qlab.syllabus.reference import SyllabusReference
from qlab.syllabus.service import ReferenceConflict, get_vocabulary, load_reference

pytestmark = pytest.mark.db

NOW = datetime(2026, 6, 1, tzinfo=UTC)


def rejected(connection: Connection, sql: str, **params: object) -> str:
    """Run a statement that must fail; return the database's message."""
    with pytest.raises(DBAPIError) as caught, connection.begin_nested():
        connection.execute(text(sql), params)
    return str(caught.value.orig)


# --- schema drift that alembic's comparison cannot see ---------------------------------------


def test_every_model_check_constraint_exists_under_its_conventional_name(
    connection: Connection,
) -> None:
    expected = {
        (table.name, str(constraint.name))
        for table in Base.metadata.tables.values()
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }
    actual = {
        (row.table, row.name)
        for row in connection.execute(
            text(
                "SELECT c.conrelid::regclass::text AS table, c.conname AS name "
                "FROM pg_constraint c JOIN pg_namespace n ON n.oid = c.connamespace "
                "WHERE c.contype = 'c' AND n.nspname = 'public'"
            )
        )
    }
    assert expected and actual == expected


def test_guard_triggers_fire_even_in_replica_mode(connection: Connection) -> None:
    rows = connection.execute(
        text(
            "SELECT tgrelid::regclass::text AS table, tgname, tgenabled::text AS enabled "
            "FROM pg_trigger WHERE NOT tgisinternal ORDER BY 1, 2"
        )
    ).all()
    assert [(r.table, r.tgname, r.enabled) for r in rows] == [
        ("audit_log", "audit_log_no_truncate", "A"),
        ("audit_log", "audit_log_no_update_delete", "A"),
        ("audit_log", "audit_log_stamp", "A"),
        ("rights_record", "rights_record_guard_row", "A"),
        ("rights_record", "rights_record_guard_truncate", "A"),
    ]


# --- audit log ----------------------------------------------------------------------------


def insert_audit(connection: Connection, **overrides: object) -> None:
    values: dict[str, object] = {
        "id": uuid.uuid4(),
        "actor": "system:test",
        "action": "thing.done",
        "entity_type": "thing",
        "entity_id": "1",
        "data": "{}",
    } | overrides
    connection.execute(
        text(
            "INSERT INTO audit_log (id, actor, action, entity_type, entity_id, data) VALUES "
            "(:id, :actor, :action, :entity_type, :entity_id, CAST(:data AS jsonb))"
        ),
        values,
    )


def test_a_raw_insert_cannot_backdate_an_entry(connection: Connection) -> None:
    entry_id = uuid.uuid4()
    connection.execute(
        text(
            "INSERT INTO audit_log (id, occurred_at, actor, action, entity_type, entity_id) "
            "VALUES (:id, '2001-01-01+00', 'system:test', 'thing.done', 'thing', '1')"
        ),
        {"id": entry_id},
    )
    occurred_at = connection.execute(
        text("SELECT occurred_at FROM audit_log WHERE id = :id"), {"id": entry_id}
    ).scalar_one()
    assert datetime.now(UTC) - occurred_at < timedelta(minutes=1)


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("actor", "someone@example.org"),
        ("actor", "Jane Doe"),
        ("actor", ""),
        ("action", "published"),
        ("action", "Thing.Done"),
        ("entity_type", "Thing"),
        ("entity_id", ""),
        ("entity_id", " 1"),
        ("entity_id", "x" * 201),
        ("data", "[]"),
        ("data", '"text"'),
        ("data", '{"k": "' + "x" * 17000 + '"}'),
    ],
)
def test_a_raw_insert_must_satisfy_the_same_rules_as_the_service(
    connection: Connection, column: str, value: str
) -> None:
    with pytest.raises(DBAPIError, match=f"ck_audit_log_{column}"), connection.begin_nested():
        insert_audit(connection, **{column: value})


def test_entries_keep_the_order_they_were_recorded_in_one_transaction(session: Session) -> None:
    for step in ("first", "second", "third"):
        audit.record(
            session, actor="system:test", action=f"thing.{step}", entity_type="thing", entity_id="7"
        )
    entries = audit.entries_for(session, "thing", "7")
    assert [e.action for e in entries] == ["thing.first", "thing.second", "thing.third"]
    assert entries[0].occurred_at < entries[1].occurred_at < entries[2].occurred_at


@pytest.mark.parametrize(
    "data",
    [{"when": NOW}, {"id": uuid.uuid4()}, {"x": float("nan")}, {"big": "x" * 9000}],
)
def test_unstorable_data_is_a_value_error_and_leaves_the_session_usable(
    session: Session, data: dict[str, object]
) -> None:
    with pytest.raises(ValueError, match="audit: data"):
        audit.record(
            session, actor="system:test", action="a.b", entity_type="t", entity_id="1", data=data
        )
    audit.record(session, actor="system:test", action="a.b", entity_type="t", entity_id="1")
    assert len(audit.entries_for(session, "t", "1")) == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("actor", "someone@example.org"),
        ("actor", "Jane Doe"),
        ("entity_type", "Thing"),
        ("entity_id", " 1 "),
    ],
)
def test_the_service_rejects_personal_or_padded_identifiers(
    session: Session, field: str, value: str
) -> None:
    arguments = {"actor": "u_1", "entity_type": "t", "entity_id": "1"} | {field: value}
    with pytest.raises(ValueError, match="audit"):
        audit.record(
            session,
            actor=arguments["actor"],
            action="a.b",
            entity_type=arguments["entity_type"],
            entity_id=arguments["entity_id"],
        )


@pytest.fixture
def runtime_role(connection: Connection) -> Iterator[Connection]:
    """The connection acting as a role like the one the application must run as."""
    connection.execute(text("CREATE ROLE qlab_runtime_probe NOSUPERUSER"))
    connection.execute(text("GRANT SELECT, INSERT ON audit_log TO qlab_runtime_probe"))
    insert_audit(connection)
    connection.execute(text("SET LOCAL ROLE qlab_runtime_probe"))
    yield connection


def test_the_runtime_role_can_append_and_read(runtime_role: Connection) -> None:
    insert_audit(runtime_role)
    assert runtime_role.execute(text("SELECT count(*) FROM audit_log")).scalar_one() == 2


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE audit_log SET actor = 'system:other'",
        "DELETE FROM audit_log",
        "TRUNCATE audit_log",
        "ALTER TABLE audit_log DISABLE TRIGGER USER",
        "SET LOCAL session_replication_role = replica",
        "DROP TRIGGER audit_log_no_update_delete ON audit_log",
        "CREATE OR REPLACE FUNCTION audit_log_reject_change() RETURNS trigger "
        "LANGUAGE plpgsql AS $$ BEGIN RETURN OLD; END; $$",
        "DROP TABLE audit_log",
    ],
)
def test_the_runtime_role_cannot_rewrite_history_or_disarm_the_guards(
    runtime_role: Connection, statement: str
) -> None:
    message = rejected(runtime_role, statement)
    assert "permission denied" in message or "must be owner" in message
    assert runtime_role.execute(text("SELECT actor FROM audit_log")).scalars().all() == [
        "system:test"
    ]


# --- rights records -----------------------------------------------------------------------


def make_record(session: Session) -> uuid.UUID:
    return rights.create_record(
        session,
        holder="Synthetic holder",
        valid_from=NOW - timedelta(days=1),
        display_scope=rights.DisplayScope.ALL,
    ).id


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE rights_record SET allows_ai_processing = true WHERE id = :id",
        "UPDATE rights_record SET display_scope = 'none' WHERE id = :id",
        "UPDATE rights_record SET valid_until = NULL, holder = 'Other' WHERE id = :id",
        "UPDATE rights_record SET revoked_at = now(), allows_commercial_use = true WHERE id = :id",
        "DELETE FROM rights_record WHERE id = :id",
        "TRUNCATE rights_record",
    ],
)
def test_a_stored_record_cannot_be_widened_edited_or_removed(
    session: Session, connection: Connection, statement: str
) -> None:
    record_id = make_record(session)
    assert "only a first revocation" in rejected(connection, statement, id=record_id)
    assert rights.is_permitted(session, record_id, rights.Purpose.DISPLAY, at=NOW)
    assert not rights.is_permitted(session, record_id, rights.Purpose.AI_PROCESSING, at=NOW)


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE rights_record SET revoked_at = NULL WHERE id = :id",
        "UPDATE rights_record SET revoked_at = revoked_at + interval '1 day' WHERE id = :id",
    ],
)
def test_a_revocation_cannot_be_undone_or_moved(
    session: Session, connection: Connection, statement: str
) -> None:
    record_id = make_record(session)
    rights.revoke(session, record_id, at=NOW)
    assert "only a first revocation" in rejected(connection, statement, id=record_id)
    assert not rights.is_permitted(session, record_id, rights.Purpose.DISPLAY, at=NOW)


def test_a_revocation_made_elsewhere_is_seen_despite_a_cached_row(
    session: Session, connection: Connection
) -> None:
    record_id = make_record(session)
    cached = session.get(RightsRecord, record_id)  # keeps the row alive in the identity map
    assert cached is not None and cached.revoked_at is None
    assert rights.is_permitted(session, record_id, rights.Purpose.DISPLAY, at=NOW)

    connection.execute(
        text("UPDATE rights_record SET revoked_at = now() WHERE id = :id"), {"id": record_id}
    )

    assert not rights.is_permitted(session, record_id, rights.Purpose.DISPLAY, at=NOW)
    with pytest.raises(rights.RightsDenied):
        rights.require(session, record_id, rights.Purpose.DISPLAY, at=NOW)


@pytest.mark.parametrize("assignment", ["valid_from = '-infinity'", "valid_until = 'infinity'"])
def test_infinite_times_are_rejected(connection: Connection, assignment: str) -> None:
    column, value = assignment.split(" = ")
    columns = {"valid_from": "'2026-01-01+00'", "valid_until": "NULL"} | {column: value}
    message = rejected(
        connection,
        "INSERT INTO rights_record (id, holder, valid_from, valid_until) "  # noqa: S608
        f"VALUES (:id, 'h', {columns['valid_from']}, {columns['valid_until']})",
        id=uuid.uuid4(),
    )
    assert "ck_rights_record_finite_times" in message


def test_flags_permit_only_when_they_are_exactly_true() -> None:
    view = rights.RightsRecordView(
        id=uuid.uuid4(),
        holder="h",
        license_ref=None,
        display_scope=rights.DisplayScope.NONE,
        display_organization_id=None,
        allows_ai_processing=1,  # type: ignore[arg-type]  # a truthy non-bool must not permit
        allows_commercial_use="yes",  # type: ignore[arg-type]
        valid_from=NOW - timedelta(days=1),
        valid_until=None,
        revoked_at=None,
    )
    assert rights.evaluate(view, rights.Purpose.AI_PROCESSING, at=NOW) is False
    assert rights.evaluate(view, rights.Purpose.COMMERCIAL_USE, at=NOW) is False


# --- syllabus -----------------------------------------------------------------------------


def reference(format_code: str = "main", status: str = "draft") -> SyllabusReference:
    return SyllabusReference.model_validate(
        {
            "status": status,
            "program": {"code": "demo", "name": "Demo"},
            "subject": {"code": "sub", "name": "Subject"},
            "syllabus_version": {"code": "v1", "title": "Version one"},
            "nodes": [{"code": "X", "title": "X"}],
            "exam_format": {
                "code": format_code,
                "sections": [{"code": "s1", "title": "Section 1"}],
                "command_terms": ["state"],
            },
        }
    )


def test_a_version_has_one_exam_format_and_renaming_it_is_a_conflict(session: Session) -> None:
    version_id = load_reference(session, reference("main"))
    with pytest.raises(ReferenceConflict):
        load_reference(session, reference("other"))
    assert get_vocabulary(session, version_id).exam_sections == {"s1"}
    assert session.execute(text("SELECT code FROM exam_format")).scalars().all() == ["main"]


def test_the_review_status_of_the_reference_is_stored_and_updated(session: Session) -> None:
    load_reference(session, reference(status="draft: unconfirmed"))
    load_reference(session, reference(status="confirmed"))
    assert session.execute(text("SELECT status FROM syllabus_version")).scalars().all() == [
        "confirmed"
    ]


def test_a_node_cannot_have_a_parent_in_another_version(
    session: Session, connection: Connection
) -> None:
    first = load_reference(session, reference())
    other = SyllabusReference.model_validate(
        reference().model_dump() | {"syllabus_version": {"code": "v2", "title": "Version two"}}
    )
    second = load_reference(session, other)
    parent = connection.execute(
        text("SELECT id FROM syllabus_node WHERE syllabus_version_id = :v"), {"v": first}
    ).scalar_one()
    message = rejected(
        connection,
        "INSERT INTO syllabus_node (id, syllabus_version_id, parent_id, code, title, position) "
        "VALUES (:id, :v, :p, 'Z', 'Z', 9)",
        id=uuid.uuid4(),
        v=second,
        p=parent,
    )
    assert "fk_syllabus_node_syllabus_version_id_parent_id_syllabus_node" in message
