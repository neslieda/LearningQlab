"""Rules the database enforces on the question tables whatever code writes to them.

Written from migration 0002 (commit cf7c754), docs/DOMAIN_MODEL.md sections 4 and 6 and
CLAUDE.md rules 7 and 8. Everything here is raw SQL on `connection`; setup uses only the merged
rights and syllabus services and plain INSERTs, so these tests never call the content service.

Two things in the brief for this suite differ from the migration, which was followed: rows of
`part`, `mark_point`, `question_version_syllabus` and `question_version_check` may be DELETEd (and
INSERTed) in the editable statuses, because the service replaces them; and the guard messages are
matched, so that a test fails for the rule it names and not for a foreign key or a type error.
"""

from __future__ import annotations

import re
import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from qlab.content import service as svc
from qlab.syllabus.reference import SyllabusReference, VersionRef
from qlab.syllabus.service import load_reference
from tests.content import samples
from tests.content.support import (
    ALL_STATUSES,
    ALLOWED_MOVES,
    VISUAL_SAMPLES,
    Env,
    RawVersion,
    count,
    document,
    make_env,
    new_rights,
    raw_check,
    raw_full_version,
    raw_mark_point,
    raw_part,
    raw_question,
    raw_syllabus_row,
    raw_version,
    raw_walk,
    status_of,
    table_counts,
)

pytestmark = pytest.mark.db

TABLES = (
    "question",
    "question_version",
    "part",
    "mark_point",
    "question_version_syllabus",
    "question_version_check",
)
EDITABLE = ("draft", "needs_fix")
NOT_EDITABLE = tuple(s for s in ALL_STATUSES if s not in EDITABLE)


def rejected(connection: Connection, sql: str, **params: object) -> str:
    """Run a statement that must fail; return the database's message."""
    with pytest.raises(DBAPIError) as caught, connection.begin_nested():
        connection.execute(text(sql), params)
    return str(caught.value.orig)


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


def version_at(connection: Connection, env: Env, status: str, doc: Any = None) -> RawVersion:
    """A version with one row in each child table, moved to `status` by raw status updates."""
    raw = raw_full_version(connection, env, doc)
    raw_walk(connection, raw.version_id, status)
    return raw


def row_of(connection: Connection, version_id: uuid.UUID) -> tuple[Any, ...]:
    return tuple(
        connection.execute(
            text("SELECT * FROM question_version WHERE id = :v"), {"v": version_id}
        ).one()
    )


# =============================================================================================
# Inserting a version
# =============================================================================================


def test_a_version_inserted_without_a_status_starts_as_draft(
    connection: Connection, env: Env
) -> None:
    version_id = raw_version(connection, raw_question(connection, env))
    assert status_of(connection, version_id) == "draft"


@pytest.mark.parametrize("status", [s for s in ALL_STATUSES if s != "draft"])
def test_a_version_cannot_be_inserted_in_any_other_status(
    connection: Connection, env: Env, status: str
) -> None:
    question_id = raw_question(connection, env)
    before = count(connection, "question_version")
    with pytest.raises(DBAPIError, match="starts as draft"), connection.begin_nested():
        raw_version(connection, question_id, status=status)
    assert count(connection, "question_version") == before


def test_a_version_inserted_as_draft_explicitly_is_accepted(
    connection: Connection, env: Env
) -> None:
    version_id = raw_version(connection, raw_question(connection, env), status="draft")
    assert status_of(connection, version_id) == "draft"


def test_an_unknown_status_is_rejected_by_the_check_constraint(
    connection: Connection, env: Env
) -> None:
    raw = raw_full_version(connection, env)
    message = rejected(
        connection,
        "UPDATE question_version SET status = 'archived' WHERE id = :v",
        v=raw.version_id,
    )
    # The move guard speaks before the CHECK constraint can; either way the value is refused.
    assert (
        "ck_question_version_status" in message or "cannot move from draft to archived" in message
    )
    assert status_of(connection, raw.version_id) == "draft"


@pytest.mark.parametrize(
    ("assignment", "constraint"),
    [
        ("version_no = 0", "ck_question_version_version_no"),
        ("content_sha256 = 'abc'", "ck_question_version_content_sha256"),
        ("content_sha256 = repeat('A', 64)", "ck_question_version_content_sha256"),
        ("content_sha256 = repeat('a', 63)", "ck_question_version_content_sha256"),
    ],
)
def test_version_columns_keep_their_check_constraints(
    connection: Connection, env: Env, assignment: str, constraint: str
) -> None:
    raw = raw_full_version(connection, env)
    # version_no is identity, so the identity guard may speak first; either way it is refused
    with pytest.raises(DBAPIError) as caught, connection.begin_nested():
        connection.execute(
            text(f"UPDATE question_version SET {assignment} WHERE id = :v"),  # noqa: S608
            {"v": raw.version_id},
        )
    message = str(caught.value.orig)
    assert constraint in message or "identity" in message


@pytest.mark.parametrize(
    ("column", "value", "constraint"),
    [
        ("syllabus_status", "elsewhere", "ck_question_syllabus_status"),
    ],
)
def test_question_columns_keep_their_check_constraints(
    connection: Connection, env: Env, column: str, value: str, constraint: str
) -> None:
    params = {"origin": "authored", "syllabus_status": "in_syllabus"} | {column: value}
    message = rejected(
        connection,
        "INSERT INTO question (id, origin, rights_record_id, syllabus_version_id, syllabus_status,"
        " created_by) VALUES (:id, :origin, :rights, :syllabus, :syllabus_status, 'u_author')",
        id=uuid.uuid4(),
        rights=env.rights_record_id,
        syllabus=env.syllabus_version_id,
        **params,
    )
    assert constraint in message


def test_an_unknown_origin_is_refused_before_the_check_constraint_is_reached(
    connection: Connection, env: Env
) -> None:
    # The insert guard (origin <> 'authored') fires first; the CHECK is the second line.
    message = rejected(
        connection,
        "INSERT INTO question (id, origin, rights_record_id, syllabus_version_id, created_by) "
        "VALUES (:id, 'scraped', :r, :s, 'u_author')",
        id=uuid.uuid4(),
        r=env.rights_record_id,
        s=env.syllabus_version_id,
    )
    assert "ck_question_origin" in message or "origin scraped is closed" in message


def test_a_question_needs_existing_rights_and_syllabus_rows(
    connection: Connection, env: Env
) -> None:
    for rights_id, syllabus_id in (
        (uuid.uuid4(), env.syllabus_version_id),
        (env.rights_record_id, uuid.uuid4()),
    ):
        message = rejected(
            connection,
            "INSERT INTO question (id, origin, rights_record_id, syllabus_version_id, created_by) "
            "VALUES (:id, 'authored', :r, :s, 'u_author')",
            id=uuid.uuid4(),
            r=rights_id,
            s=syllabus_id,
        )
        assert "fk_question_" in message


# =============================================================================================
# has_unverified_visuals is computed by the database
# =============================================================================================


@pytest.mark.parametrize("name", sorted(VISUAL_SAMPLES))
def test_stimuli_make_the_flag_true(connection: Connection, env: Env, name: str) -> None:
    raw = raw_full_version(connection, env, document(VISUAL_SAMPLES[name]()))
    assert row_flag(connection, raw.version_id) is True


def test_no_stimuli_make_the_flag_false(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    assert row_flag(connection, raw.version_id) is False


def row_flag(connection: Connection, version_id: uuid.UUID) -> bool:
    return bool(
        connection.execute(
            text("SELECT has_unverified_visuals FROM question_version WHERE id = :v"),
            {"v": version_id},
        ).scalar_one()
    )


def test_the_flag_follows_a_document_edit_in_draft(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    connection.execute(
        text("UPDATE question_version SET document = CAST(:d AS jsonb) WHERE id = :v"),
        {"d": document(samples.structured_document()).model_dump_json(), "v": raw.version_id},
    )
    assert row_flag(connection, raw.version_id) is True
    connection.execute(
        text("UPDATE question_version SET document = CAST(:d AS jsonb) WHERE id = :v"),
        {"d": document().model_dump_json(), "v": raw.version_id},
    )
    assert row_flag(connection, raw.version_id) is False


@pytest.mark.parametrize("value", ["true", "false"])
def test_the_flag_cannot_be_written_directly(connection: Connection, env: Env, value: str) -> None:
    raw = raw_full_version(connection, env)
    before = row_of(connection, raw.version_id)
    message = rejected(
        connection,
        f"UPDATE question_version SET has_unverified_visuals = {value} WHERE id = :v",  # noqa: S608
        v=raw.version_id,
    )
    assert "has_unverified_visuals" in message
    assert row_of(connection, raw.version_id) == before


def test_the_flag_cannot_be_given_on_insert(connection: Connection, env: Env) -> None:
    question_id = raw_question(connection, env)
    doc = document()
    message = rejected(
        connection,
        "INSERT INTO question_version (id, question_id, version_no, schema_version, document, "
        "content_sha256, question_class, exam_section, levels, total_marks, created_by, "
        "has_unverified_visuals) VALUES (:id, :q, 1, '1.0', CAST(:d AS jsonb), repeat('a', 64), "
        "'mcq', 'paper_1a', ARRAY['sl'], 1, 'u_author', false)",
        id=uuid.uuid4(),
        q=question_id,
        d=doc.model_dump_json(),
    )
    assert "has_unverified_visuals" in message


@pytest.mark.parametrize(
    "document_sql",
    [
        "document - 'stimuli'",
        "jsonb_set(document, '{stimuli}', 'null')",
        "jsonb_set(document, '{stimuli}', '{}')",
        "jsonb_set(document, '{stimuli}', '\"none\"')",
    ],
)
def test_a_document_cannot_hide_its_stimuli_from_the_flag(
    connection: Connection, env: Env, document_sql: str
) -> None:
    raw = raw_full_version(connection, env, document(samples.structured_document()))
    before = row_of(connection, raw.version_id)
    with pytest.raises(DBAPIError), connection.begin_nested():
        connection.execute(
            text(f"UPDATE question_version SET document = {document_sql} WHERE id = :v"),  # noqa: S608
            {"v": raw.version_id},
        )
    assert row_of(connection, raw.version_id) == before
    assert row_flag(connection, raw.version_id) is True


# =============================================================================================
# Content is editable in draft and needs_fix only
# =============================================================================================

CONTENT_UPDATES = {
    "document": "document = document || jsonb_build_object('outcome', 'changed')",
    "schema_version": "schema_version = '9.9'",
    "content_sha256": "content_sha256 = repeat('a', 64)",
    "question_class": "question_class = 'long_structured'",
    "exam_section": "exam_section = 'paper_9'",
    "levels": "levels = ARRAY['hl']",
    "total_marks": "total_marks = 99",
}
IDENTITY_UPDATES = {
    "id": "id = gen_random_uuid()",
    "question_id": "question_id = gen_random_uuid()",
    "version_no": "version_no = 7",
    "created_by": "created_by = 'u_other'",
    "created_at": "created_at = created_at + interval '1 day'",
}


@pytest.mark.parametrize("column", list(CONTENT_UPDATES) + list(IDENTITY_UPDATES))
@pytest.mark.parametrize("status", NOT_EDITABLE)
def test_no_column_of_a_version_can_change_outside_draft_and_needs_fix(
    connection: Connection, env: Env, status: str, column: str
) -> None:
    raw = version_at(connection, env, status)
    before = row_of(connection, raw.version_id)
    assignment = (CONTENT_UPDATES | IDENTITY_UPDATES)[column]
    message = rejected(
        connection,
        f"UPDATE question_version SET {assignment} WHERE id = :v",  # noqa: S608
        v=raw.version_id,
    )
    assert f"the content of a {status} question version cannot change" in message
    assert row_of(connection, raw.version_id) == before


@pytest.mark.parametrize("column", list(CONTENT_UPDATES))
@pytest.mark.parametrize("status", EDITABLE)
def test_content_columns_can_change_in_draft_and_needs_fix(
    connection: Connection, env: Env, status: str, column: str
) -> None:
    raw = version_at(connection, env, status)
    before = row_of(connection, raw.version_id)
    connection.execute(
        text(f"UPDATE question_version SET {CONTENT_UPDATES[column]} WHERE id = :v"),  # noqa: S608
        {"v": raw.version_id},
    )
    assert row_of(connection, raw.version_id) != before
    assert status_of(connection, raw.version_id) == status


@pytest.mark.parametrize("column", list(IDENTITY_UPDATES))
@pytest.mark.parametrize("status", EDITABLE)
def test_identity_columns_cannot_change_even_in_draft_and_needs_fix(
    connection: Connection, env: Env, status: str, column: str
) -> None:
    raw = version_at(connection, env, status)
    before = row_of(connection, raw.version_id)
    message = rejected(
        connection,
        f"UPDATE question_version SET {IDENTITY_UPDATES[column]} WHERE id = :v",  # noqa: S608
        v=raw.version_id,
    )
    assert "identity of a question version cannot change" in message
    assert row_of(connection, raw.version_id) == before


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("approved", "needs_fix"),
        ("in_review", "needs_fix"),
        ("approved", "published"),
        ("in_review", "approved"),
        ("published", "withdrawn"),
        ("withdrawn", "published"),
        ("in_review", "rejected"),
    ],
)
def test_a_status_move_cannot_carry_a_content_change_out_of_a_locked_status(
    connection: Connection, env: Env, old: str, new: str
) -> None:
    raw = version_at(connection, env, old)
    before = row_of(connection, raw.version_id)
    message = rejected(
        connection,
        f"UPDATE question_version SET status = '{new}', "  # noqa: S608
        "document = document || jsonb_build_object('outcome', 'sneaked in') WHERE id = :v",
        v=raw.version_id,
    )
    assert "cannot change" in message
    assert row_of(connection, raw.version_id) == before


def test_leaving_needs_fix_may_carry_the_edit(connection: Connection, env: Env) -> None:
    raw = version_at(connection, env, "needs_fix")
    connection.execute(
        text(
            "UPDATE question_version SET status = 'draft', "
            "document = document || jsonb_build_object('outcome', 'edited') WHERE id = :v"
        ),
        {"v": raw.version_id},
    )
    assert status_of(connection, raw.version_id) == "draft"
    outcome = connection.execute(
        text("SELECT document ->> 'outcome' FROM question_version WHERE id = :v"),
        {"v": raw.version_id},
    ).scalar_one()
    assert outcome == "edited"


# =============================================================================================
# Status moves
# =============================================================================================

PAIRS = [(a, b) for a in ALL_STATUSES for b in ALL_STATUSES if a != b]


@pytest.mark.parametrize(("old", "new"), PAIRS, ids=[f"{a}-to-{b}" for a, b in PAIRS])
def test_the_full_matrix_of_status_moves(
    connection: Connection, env: Env, old: str, new: str
) -> None:
    raw = version_at(connection, env, old)
    statement = "UPDATE question_version SET status = :new WHERE id = :v"
    if (old, new) in ALLOWED_MOVES:
        connection.execute(text(statement), {"new": new, "v": raw.version_id})
        assert status_of(connection, raw.version_id) == new
    else:
        message = rejected(connection, statement, new=new, v=raw.version_id)
        assert f"cannot move from {old} to {new}" in message
        assert status_of(connection, raw.version_id) == old


# =============================================================================================
# Publishing (CLAUDE.md rule 8, D-49)
# =============================================================================================


@pytest.mark.parametrize("name", sorted(VISUAL_SAMPLES))
def test_a_version_with_stimuli_cannot_become_published(
    connection: Connection, env: Env, name: str
) -> None:
    raw = version_at(connection, env, "approved", document(VISUAL_SAMPLES[name]()))
    message = rejected(
        connection,
        "UPDATE question_version SET status = 'published' WHERE id = :v",
        v=raw.version_id,
    )
    assert "unverified visuals" in message
    assert status_of(connection, raw.version_id) == "approved"


def test_a_stimuli_version_can_still_reach_in_review_and_approved(
    connection: Connection, env: Env
) -> None:
    raw = version_at(connection, env, "approved", document(samples.structured_document()))
    assert status_of(connection, raw.version_id) == "approved"


def approved_with_check(
    connection: Connection, env: Env, severity: str, outcome: str, doc: Any = None
) -> RawVersion:
    """An approved version that carries one more check row, inserted while `auto_checking`."""
    raw = raw_full_version(connection, env, doc)
    raw_walk(connection, raw.version_id, "auto_checking")
    raw_check(connection, raw.version_id, "second_check", severity, outcome)
    for step in ("in_review", "approved"):
        connection.execute(
            text("UPDATE question_version SET status = :s WHERE id = :v"),
            {"s": step, "v": raw.version_id},
        )
    return raw


@pytest.mark.parametrize(
    ("severity", "outcome"),
    [("warning", "failed"), ("critical", "passed"), ("critical", "not_applicable")],
)
def test_other_check_results_do_not_block_review_or_publishing(
    connection: Connection, env: Env, severity: str, outcome: str
) -> None:
    raw = approved_with_check(connection, env, severity, outcome)
    connection.execute(
        text("UPDATE question_version SET status = 'published' WHERE id = :v"),
        {"v": raw.version_id},
    )
    assert status_of(connection, raw.version_id) == "published"


def test_a_failed_critical_check_stops_auto_checking_from_moving_to_review(
    connection: Connection, env: Env
) -> None:
    raw = raw_full_version(connection, env)
    raw_walk(connection, raw.version_id, "auto_checking")
    raw_check(connection, raw.version_id, "second_check", "critical", "failed")
    before = row_of(connection, raw.version_id)
    message = rejected(
        connection,
        "UPDATE question_version SET status = 'in_review' WHERE id = :v",
        v=raw.version_id,
    )
    assert "cannot move to in_review: a critical check failed" in message
    assert row_of(connection, raw.version_id) == before
    assert status_of(connection, raw.version_id) == "auto_checking"


def test_a_failed_critical_check_still_allows_the_move_to_needs_fix(
    connection: Connection, env: Env
) -> None:
    raw = raw_full_version(connection, env)
    raw_walk(connection, raw.version_id, "auto_checking")
    raw_check(connection, raw.version_id, "second_check", "critical", "failed")
    connection.execute(
        text("UPDATE question_version SET status = 'needs_fix' WHERE id = :v"),
        {"v": raw.version_id},
    )
    assert status_of(connection, raw.version_id) == "needs_fix"


@pytest.mark.parametrize("insert_in", ["draft", "needs_fix", "auto_checking"])
@pytest.mark.parametrize("target", ["in_review", "approved", "published"])
def test_no_route_reaches_review_approval_or_publishing_with_a_failed_critical_check(
    connection: Connection, env: Env, insert_in: str, target: str
) -> None:
    """Failed critical rows can only be inserted in draft, needs_fix and auto_checking, and
    every way out of those toward `target` is refused while the row exists."""
    raw = version_at(connection, env, insert_in)
    raw_check(connection, raw.version_id, "second_check", "critical", "failed")
    # try every status move the lifecycle offers, in order, toward the target
    attempted = {
        "in_review": ["auto_checking", "in_review"],
        "approved": ["auto_checking", "in_review", "approved"],
        "published": ["auto_checking", "in_review", "approved", "published"],
    }[target]
    for step in attempted:
        current = status_of(connection, raw.version_id)
        if current == step:
            continue
        try:
            with connection.begin_nested():
                connection.execute(
                    text("UPDATE question_version SET status = :s WHERE id = :v"),
                    {"s": step, "v": raw.version_id},
                )
        except DBAPIError:
            break
    assert status_of(connection, raw.version_id) in ("draft", "needs_fix", "auto_checking")
    failed = connection.execute(
        text(
            "SELECT count(*) FROM question_version v JOIN question_version_check c "
            "ON c.question_version_id = v.id WHERE c.severity = 'critical' "
            "AND c.outcome = 'failed' AND v.status IN ('in_review', 'approved', 'published')"
        )
    ).scalar_one()
    assert failed == 0


def test_check_rows_cannot_be_added_once_a_version_is_in_review(
    connection: Connection, env: Env
) -> None:
    raw = version_at(connection, env, "in_review")
    with (
        pytest.raises(DBAPIError, match="cannot change while the version is in_review"),
        connection.begin_nested(),
    ):
        raw_check(connection, raw.version_id, "late", "critical", "failed")


def test_removing_the_failed_check_while_in_needs_fix_clears_the_way(
    connection: Connection, env: Env
) -> None:
    raw = raw_full_version(connection, env)
    raw_walk(connection, raw.version_id, "auto_checking")
    failing = raw_check(connection, raw.version_id, "second_check", "critical", "failed")
    connection.execute(
        text("UPDATE question_version SET status = 'needs_fix' WHERE id = :v"),
        {"v": raw.version_id},
    )
    connection.execute(text("DELETE FROM question_version_check WHERE id = :c"), {"c": failing})
    for step in ("draft", "auto_checking", "in_review", "approved", "published"):
        connection.execute(
            text("UPDATE question_version SET status = :s WHERE id = :v"),
            {"s": step, "v": raw.version_id},
        )
    assert status_of(connection, raw.version_id) == "published"


def test_stimuli_are_refused_at_publishing_whatever_the_checks_say(
    connection: Connection, env: Env
) -> None:
    raw = approved_with_check(
        connection, env, "warning", "failed", document(samples.structured_document())
    )
    message = rejected(
        connection,
        "UPDATE question_version SET status = 'published' WHERE id = :v",
        v=raw.version_id,
    )
    assert "unverified visuals" in message
    assert status_of(connection, raw.version_id) == "approved"


def test_a_published_version_keeps_its_content_and_children_for_good(
    connection: Connection, env: Env
) -> None:
    raw = version_at(connection, env, "published")
    before = row_of(connection, raw.version_id)
    counts = table_counts(connection)
    rejected(
        connection,
        "UPDATE question_version SET document = '{}' WHERE id = :v",
        v=raw.version_id,
    )
    rejected(connection, "DELETE FROM part WHERE id = :p", p=raw.part_id)
    rejected(connection, "UPDATE part SET marks = 5 WHERE id = :p", p=raw.part_id)
    assert row_of(connection, raw.version_id) == before
    assert table_counts(connection) == counts


# =============================================================================================
# DELETE and TRUNCATE
# =============================================================================================


def test_a_question_cannot_be_deleted(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    message = rejected(connection, "DELETE FROM question WHERE id = :q", q=raw.question_id)
    assert "DELETE on question is not allowed" in message
    assert count(connection, "question") == 1


@pytest.mark.parametrize("status", ALL_STATUSES)
def test_a_version_cannot_be_deleted_in_any_status(
    connection: Connection, env: Env, status: str
) -> None:
    raw = version_at(connection, env, status)
    message = rejected(connection, "DELETE FROM question_version WHERE id = :v", v=raw.version_id)
    assert "DELETE on question_version is not allowed" in message
    assert status_of(connection, raw.version_id) == status


@pytest.mark.parametrize("table", TABLES)
def test_truncate_is_refused_on_every_question_table(
    connection: Connection, env: Env, table: str
) -> None:
    raw_full_version(connection, env)
    before = table_counts(connection)
    message = rejected(connection, f"TRUNCATE {table} CASCADE")
    assert re.search(r"TRUNCATE on \w+ is not allowed", message)
    assert table_counts(connection) == before


# =============================================================================================
# Rows that hang off a version
# =============================================================================================

CHILD_TABLES = ("part", "mark_point", "question_version_syllabus", "question_version_check")


def editable_statuses(table: str) -> tuple[str, ...]:
    if table == "question_version_check":
        return ("draft", "needs_fix", "auto_checking")
    return EDITABLE


def insert_child(connection: Connection, env: Env, raw: RawVersion, table: str) -> None:
    if table == "part":
        raw_part(connection, raw.version_id, "p-new", position=1)
    elif table == "mark_point":
        raw_mark_point(connection, raw.part_id, "a-new", position=1)
    elif table == "question_version_syllabus":
        raw_syllabus_row(connection, env, raw.version_id, "A.2")
    else:
        raw_check(connection, raw.version_id, "second_check", "warning", "passed")


def delete_child(
    connection: Connection, raw: RawVersion, table: str, *, editable: bool = True
) -> None:
    if table == "part":
        if editable:  # a part with mark points cannot go before them (foreign key)
            connection.execute(
                text("DELETE FROM mark_point WHERE id = :m"), {"m": raw.mark_point_id}
            )
        connection.execute(text("DELETE FROM part WHERE id = :p"), {"p": raw.part_id})
    elif table == "mark_point":
        connection.execute(text("DELETE FROM mark_point WHERE id = :m"), {"m": raw.mark_point_id})
    elif table == "question_version_syllabus":
        connection.execute(
            text("DELETE FROM question_version_syllabus WHERE question_version_id = :v"),
            {"v": raw.version_id},
        )
    else:
        connection.execute(
            text("DELETE FROM question_version_check WHERE id = :c"), {"c": raw.check_id}
        )


CHILD_CASES = [
    (table, status, status in editable_statuses(table))
    for table in CHILD_TABLES
    for status in ALL_STATUSES
]


@pytest.mark.parametrize(
    ("table", "status", "allowed"), CHILD_CASES, ids=[f"{t}-{s}" for t, s, _ in CHILD_CASES]
)
def test_child_rows_can_be_inserted_only_in_the_editable_statuses(
    connection: Connection, env: Env, table: str, status: str, allowed: bool
) -> None:
    raw = version_at(connection, env, status)
    before = table_counts(connection)
    if allowed:
        insert_child(connection, env, raw, table)
        assert count(connection, table) == before[table] + 1
    else:
        with (
            pytest.raises(
                DBAPIError, match=rf"{table} rows cannot change while the version is {status}"
            ),
            connection.begin_nested(),
        ):
            insert_child(connection, env, raw, table)
        assert table_counts(connection) == before


@pytest.mark.parametrize(
    ("table", "status", "allowed"), CHILD_CASES, ids=[f"{t}-{s}" for t, s, _ in CHILD_CASES]
)
def test_child_rows_can_be_deleted_only_in_the_editable_statuses(
    connection: Connection, env: Env, table: str, status: str, allowed: bool
) -> None:
    raw = version_at(connection, env, status)
    before = table_counts(connection)
    if allowed:
        delete_child(connection, raw, table)
        assert count(connection, table) == before[table] - 1
    else:
        with (
            pytest.raises(
                DBAPIError, match=rf"{table} rows cannot change while the version is {status}"
            ),
            connection.begin_nested(),
        ):
            delete_child(connection, raw, table, editable=False)
        assert table_counts(connection) == before


UPDATES = {
    "part": "UPDATE part SET marks = 5 WHERE id = :part",
    "mark_point": "UPDATE mark_point SET route = 'r9' WHERE id = :point",
    "question_version_syllabus": (
        "UPDATE question_version_syllabus SET is_primary = false WHERE question_version_id = :v"
    ),
    "question_version_check": "UPDATE question_version_check SET outcome = 'passed' WHERE id = :c",
}


@pytest.mark.parametrize("status", ALL_STATUSES)
@pytest.mark.parametrize("table", CHILD_TABLES)
def test_child_rows_are_replaced_never_updated_in_any_status(
    connection: Connection, env: Env, table: str, status: str
) -> None:
    raw = version_at(connection, env, status)
    before = table_counts(connection)
    message = rejected(
        connection,
        UPDATES[table],
        part=raw.part_id,
        point=raw.mark_point_id,
        v=raw.version_id,
        c=raw.check_id,
    )
    assert f"rows of {table} are replaced, not updated" in message
    assert table_counts(connection) == before
    if table == "question_version_check":
        outcome = connection.execute(
            text("SELECT outcome FROM question_version_check WHERE id = :c"), {"c": raw.check_id}
        ).scalar_one()
        assert outcome == "passed"  # as inserted by raw_full_version
    if table == "part":
        marks = connection.execute(
            text("SELECT marks FROM part WHERE id = :p"), {"p": raw.part_id}
        ).scalar_one()
        assert marks == 1


def test_a_mark_point_cannot_be_moved_to_a_part_of_another_version(
    connection: Connection, env: Env
) -> None:
    first = raw_full_version(connection, env)
    second = raw_full_version(connection, env)
    message = rejected(
        connection,
        "UPDATE mark_point SET part_id = :other WHERE id = :m",
        other=second.part_id,
        m=first.mark_point_id,
    )
    assert "replaced, not updated" in message


# =============================================================================================
# Other constraints on the child tables
# =============================================================================================


def test_one_part_key_per_version(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    message = rejected(
        connection,
        "INSERT INTO part (id, question_version_id, position, part_key, marks, answer_type) "
        "VALUES (:id, :v, 5, 'p-a', 1, 'word_phrase')",
        id=uuid.uuid4(),
        v=raw.version_id,
    )
    assert "uq_part_question_version_id_part_key" in message


def test_one_mark_point_key_per_part(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    message = rejected(
        connection,
        "INSERT INTO mark_point (id, part_id, position, point_key, kind) "
        "VALUES (:id, :p, 5, 'a-1', 'statement')",
        id=uuid.uuid4(),
        p=raw.part_id,
    )
    assert "uq_mark_point_part_id_point_key" in message


def test_at_most_one_primary_syllabus_node_per_version(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    with (
        pytest.raises(DBAPIError, match="uq_question_version_syllabus_one_primary"),
        connection.begin_nested(),
    ):
        raw_syllabus_row(connection, env, raw.version_id, "A.2", primary=True)
    raw_syllabus_row(connection, env, raw.version_id, "A.2", primary=False)  # secondary is fine


def test_a_node_is_attached_to_a_version_once(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    with pytest.raises(DBAPIError, match="pk_question_version_syllabus"), connection.begin_nested():
        raw_syllabus_row(connection, env, raw.version_id, "A.1")


def test_one_result_per_check_code_per_version(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    with (
        pytest.raises(DBAPIError, match="question_version_id_check_code"),
        connection.begin_nested(),
    ):
        raw_check(connection, raw.version_id, "ext_check", "warning", "passed")


@pytest.mark.parametrize(
    ("code", "severity", "outcome", "constraint"),
    [
        ("Bad-Code", "critical", "passed", "ck_question_version_check_check_code"),
        ("1abc", "critical", "passed", "ck_question_version_check_check_code"),
        ("", "critical", "passed", "ck_question_version_check_check_code"),
        ("fine_code", "fatal", "passed", "ck_question_version_check_severity"),
        ("fine_code", "critical", "unknown", "ck_question_version_check_outcome"),
    ],
)
def test_check_rows_keep_their_check_constraints(
    connection: Connection, env: Env, code: str, severity: str, outcome: str, constraint: str
) -> None:
    raw = raw_full_version(connection, env)
    with pytest.raises(DBAPIError, match=constraint), connection.begin_nested():
        raw_check(connection, raw.version_id, code, severity, outcome)


def test_checks_default_to_an_empty_detail_object(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    detail = connection.execute(
        text("SELECT detail FROM question_version_check WHERE id = :c"), {"c": raw.check_id}
    ).scalar_one()
    assert detail == {}


# =============================================================================================
# The question row is fixed except for syllabus_status
# =============================================================================================


def test_syllabus_status_can_change_and_change_back(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    for value in ("out_of_syllabus", "in_syllabus"):
        connection.execute(
            text("UPDATE question SET syllabus_status = :s WHERE id = :q"),
            {"s": value, "q": raw.question_id},
        )
        assert (
            connection.execute(
                text("SELECT syllabus_status FROM question WHERE id = :q"), {"q": raw.question_id}
            ).scalar_one()
            == value
        )


def test_syllabus_status_keeps_its_check_constraint(connection: Connection, env: Env) -> None:
    raw = raw_full_version(connection, env)
    message = rejected(
        connection,
        "UPDATE question SET syllabus_status = 'maybe' WHERE id = :q",
        q=raw.question_id,
    )
    assert "ck_question_syllabus_status" in message


@pytest.fixture
def other_syllabus_version(session: Session) -> uuid.UUID:
    from tests.content.support import REFERENCE_FILE

    reference = SyllabusReference.model_validate_json(REFERENCE_FILE.read_text())
    other = reference.model_copy(
        update={"syllabus_version": VersionRef(code="other_version", title="Other version")}
    )
    return load_reference(session, other)


@pytest.mark.parametrize("status", ["draft", "published"])
@pytest.mark.parametrize("column", ["origin", "rights_record_id", "syllabus_version_id"])
def test_origin_rights_and_syllabus_version_are_fixed_at_creation(
    session: Session,
    connection: Connection,
    env: Env,
    other_syllabus_version: uuid.UUID,
    column: str,
    status: str,
) -> None:
    raw = version_at(connection, env, status)
    new_values: dict[str, object] = {
        "origin": "generated",
        "rights_record_id": new_rights(session),
        "syllabus_version_id": other_syllabus_version,
    }
    before = tuple(
        connection.execute(
            text("SELECT * FROM question WHERE id = :q"), {"q": raw.question_id}
        ).one()
    )
    message = rejected(
        connection,
        f"UPDATE question SET {column} = :value WHERE id = :q",  # noqa: S608
        value=new_values[column],
        q=raw.question_id,
    )
    assert "only syllabus_status may change" in message
    after = tuple(
        connection.execute(
            text("SELECT * FROM question WHERE id = :q"), {"q": raw.question_id}
        ).one()
    )
    assert after == before


@pytest.mark.parametrize(
    "assignment",
    [
        "id = gen_random_uuid()",
        "created_by = 'u_other'",
        "created_at = created_at + interval '1 day'",
        "origin = 'generated', syllabus_status = 'out_of_syllabus'",
    ],
)
def test_nothing_else_on_the_question_row_changes_either(
    connection: Connection, env: Env, assignment: str
) -> None:
    raw = raw_full_version(connection, env)
    message = rejected(
        connection,
        f"UPDATE question SET {assignment} WHERE id = :q",  # noqa: S608
        q=raw.question_id,
    )
    assert "only syllabus_status may change" in message


# =============================================================================================
# Partial unique indexes: one published and one working version per question
# =============================================================================================


def add_version(connection: Connection, raw: RawVersion, version_no: int) -> uuid.UUID:
    return raw_version(connection, raw.question_id, version_no=version_no)


@pytest.mark.parametrize(
    "working", ["draft", "auto_checking", "needs_fix", "in_review", "approved"]
)
def test_a_question_cannot_have_two_working_versions(
    connection: Connection, env: Env, working: str
) -> None:
    raw = version_at(connection, env, working)
    before = count(connection, "question_version")
    with (
        pytest.raises(DBAPIError, match="uq_question_version_one_working"),
        connection.begin_nested(),
    ):
        add_version(connection, raw, 2)
    assert count(connection, "question_version") == before


@pytest.mark.parametrize("settled", ["published", "withdrawn", "rejected"])
def test_a_question_may_have_a_new_working_version_beside_a_settled_one(
    connection: Connection, env: Env, settled: str
) -> None:
    raw = version_at(connection, env, settled)
    second = add_version(connection, raw, 2)
    assert status_of(connection, second) == "draft"
    assert status_of(connection, raw.version_id) == settled


def test_a_question_cannot_have_two_published_versions(connection: Connection, env: Env) -> None:
    raw = version_at(connection, env, "published")
    second = add_version(connection, raw, 2)
    raw_walk(connection, second, "approved")
    with (
        pytest.raises(DBAPIError, match="uq_question_version_one_published"),
        connection.begin_nested(),
    ):
        connection.execute(
            text("UPDATE question_version SET status = 'published' WHERE id = :v"), {"v": second}
        )
    assert status_of(connection, second) == "approved"
    assert status_of(connection, raw.version_id) == "published"


def test_a_withdrawn_version_cannot_be_republished_beside_a_published_one(
    connection: Connection, env: Env
) -> None:
    raw = version_at(connection, env, "withdrawn")
    second = add_version(connection, raw, 2)
    raw_walk(connection, second, "published")
    with (
        pytest.raises(DBAPIError, match="uq_question_version_one_published"),
        connection.begin_nested(),
    ):
        connection.execute(
            text("UPDATE question_version SET status = 'published' WHERE id = :v"),
            {"v": raw.version_id},
        )
    assert status_of(connection, raw.version_id) == "withdrawn"


def test_version_numbers_are_unique_per_question(connection: Connection, env: Env) -> None:
    raw = version_at(connection, env, "published")
    with pytest.raises(DBAPIError, match="question_id_version_no"), connection.begin_nested():
        add_version(connection, raw, 1)


def test_versions_of_different_questions_may_share_a_number(
    connection: Connection, env: Env
) -> None:
    first = raw_full_version(connection, env)
    second = raw_full_version(connection, env)
    assert first.version_id != second.version_id


# =============================================================================================
# Only authored questions, and only nodes of the question's own syllabus version
# =============================================================================================


@pytest.mark.parametrize("origin", ["generated", "source_original"])
def test_a_question_cannot_be_inserted_with_a_closed_origin(
    connection: Connection, env: Env, origin: str
) -> None:
    before = count(connection, "question")
    with pytest.raises(DBAPIError, match=f"origin {origin} is closed"), connection.begin_nested():
        raw_question(connection, env, origin=origin)
    assert count(connection, "question") == before


def test_an_authored_question_is_accepted(connection: Connection, env: Env) -> None:
    before = count(connection, "question")
    raw_question(connection, env, origin="authored")
    assert count(connection, "question") == before + 1


def test_an_unknown_origin_is_still_refused(connection: Connection, env: Env) -> None:
    before = count(connection, "question")
    with pytest.raises(DBAPIError), connection.begin_nested():
        raw_question(connection, env, origin="scraped")
    assert count(connection, "question") == before


@pytest.fixture
def second_syllabus_version(session: Session) -> uuid.UUID:
    reference = SyllabusReference.model_validate(
        {
            "status": "draft",
            "program": {"code": "demo", "name": "Demo"},
            "subject": {"code": "sub", "name": "Subject"},
            "syllabus_version": {"code": "v2", "title": "Version two"},
            "nodes": [{"code": "A", "title": "A"}, {"code": "A.1", "title": "A.1", "parent": "A"}],
            "exam_format": {
                "code": "main",
                "sections": [{"code": "s1", "title": "Section 1"}],
                "command_terms": ["state"],
            },
        }
    )
    return load_reference(session, reference)


def test_a_node_of_another_syllabus_version_cannot_tag_a_question_version(
    connection: Connection, env: Env, second_syllabus_version: uuid.UUID
) -> None:
    raw = raw_full_version(connection, env)
    foreign = connection.execute(
        text("SELECT id FROM syllabus_node WHERE syllabus_version_id = :s AND code = 'A.1'"),
        {"s": second_syllabus_version},
    ).scalar_one()
    before = count(connection, "question_version_syllabus")
    message = rejected(
        connection,
        "INSERT INTO question_version_syllabus (question_version_id, syllabus_node_id, "
        "is_primary) VALUES (:v, :n, false)",
        v=raw.version_id,
        n=foreign,
    )
    assert "syllabus node belongs to another syllabus version" in message
    assert count(connection, "question_version_syllabus") == before


def test_a_node_of_the_questions_own_syllabus_version_is_accepted(
    connection: Connection, env: Env
) -> None:
    raw = raw_full_version(connection, env)
    before = count(connection, "question_version_syllabus")
    raw_syllabus_row(connection, env, raw.version_id, "A.3")
    assert count(connection, "question_version_syllabus") == before + 1


# =============================================================================================
# The deployment requirement (docs/SECURITY.md section 10)
# =============================================================================================


@pytest.fixture
def runtime_role(connection: Connection, env: Env) -> Iterator[RawVersion]:
    """A published version, then the connection acting as a plain role that may read and write
    the question tables, like the application's runtime role."""
    raw = version_at(connection, env, "published")
    connection.execute(text("CREATE ROLE qlab_content_probe NOSUPERUSER"))
    connection.execute(
        text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON question, question_version, part, "
            "mark_point, question_version_syllabus, question_version_check TO qlab_content_probe"
        )
    )
    connection.execute(text("SET LOCAL ROLE qlab_content_probe"))
    yield raw


@pytest.mark.parametrize(
    "statement",
    [
        "ALTER TABLE question_version DISABLE TRIGGER USER",
        "ALTER TABLE question_version DISABLE TRIGGER question_version_update_guard",
        "DROP TRIGGER question_version_update_guard ON question_version",
        "DROP TRIGGER part_guard ON part",
        "SET LOCAL session_replication_role = replica",
        "CREATE OR REPLACE FUNCTION question_version_update_guard() RETURNS trigger "
        "LANGUAGE plpgsql AS $$ BEGIN RETURN NEW; END; $$",
        "DROP TABLE question_version CASCADE",
    ],
)
def test_the_runtime_role_cannot_disarm_the_guards(
    connection: Connection, runtime_role: RawVersion, statement: str
) -> None:
    message = rejected(connection, statement)
    assert "permission denied" in message or "must be owner" in message


def test_the_guards_hold_for_the_runtime_role(
    connection: Connection, runtime_role: RawVersion
) -> None:
    raw = runtime_role
    assert "cannot change" in rejected(
        connection, "UPDATE question_version SET document = '{}' WHERE id = :v", v=raw.version_id
    )
    assert "is not allowed" in rejected(
        connection, "DELETE FROM question_version WHERE id = :v", v=raw.version_id
    )
    assert "cannot change while the version is published" in rejected(
        connection, "DELETE FROM part WHERE id = :p", p=raw.part_id
    )
    assert "only syllabus_status may change" in rejected(
        connection, "UPDATE question SET origin = 'generated' WHERE id = :q", q=raw.question_id
    )
    assert status_of(connection, raw.version_id) == "published"


def test_the_service_vocabulary_matches_the_database_vocabulary() -> None:
    assert {s.value for s in svc.VersionStatus} == set(ALL_STATUSES)
    assert {o.value for o in svc.Origin} == {"authored", "generated", "source_original"}
    assert {s.value for s in svc.Severity} == {"critical", "warning"}
    assert {o.value for o in svc.Outcome} == {"passed", "failed", "not_applicable"}
