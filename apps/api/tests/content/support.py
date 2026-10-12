"""Shared setup for the content acceptance tests (plain helpers; the test modules own fixtures).

Written from the frozen contract only (docstrings of qlab.content.service, migration 0002).
Everything here sets up through the merged services (rights, syllabus), the content service, or
raw SQL; no ORM model class of the content module is imported.
"""

from __future__ import annotations

import copy
import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Connection, text
from sqlalchemy.orm import Session

from qlab.content import service as svc
from qlab.content.schema import QuestionDocument
from qlab.rights import service as rights
from qlab.syllabus.reference import SyllabusReference
from qlab.syllabus.service import load_reference
from tests.conftest import REPO_ROOT
from tests.content import samples

Json = dict[str, Any]

REFERENCE_FILE = REPO_ROOT / "content" / "reference" / "dp-physics-2025-syllabus.json"

AUTHOR = "u_author"
REVIEWER = "u_reviewer"
PUBLISHER = "u_publisher"

ALL_STATUSES: tuple[str, ...] = (
    "draft",
    "auto_checking",
    "needs_fix",
    "in_review",
    "approved",
    "published",
    "withdrawn",
    "rejected",
)
WORKING_STATUSES: tuple[str, ...] = ("draft", "auto_checking", "needs_fix", "in_review", "approved")
# The moves docs/DOMAIN_MODEL.md section 4 and migration 0002 allow.
ALLOWED_MOVES: frozenset[tuple[str, str]] = frozenset(
    {
        ("draft", "auto_checking"),
        ("auto_checking", "needs_fix"),
        ("auto_checking", "in_review"),
        ("needs_fix", "draft"),
        ("in_review", "approved"),
        ("in_review", "needs_fix"),
        ("in_review", "rejected"),
        ("approved", "needs_fix"),
        ("approved", "published"),
        ("published", "withdrawn"),
        ("withdrawn", "published"),
    }
)
# Raw status updates that lead a fresh draft to each status along allowed moves only.
RAW_PATH: dict[str, tuple[str, ...]] = {
    "draft": (),
    "auto_checking": ("auto_checking",),
    "needs_fix": ("auto_checking", "needs_fix"),
    "in_review": ("auto_checking", "in_review"),
    "approved": ("auto_checking", "in_review", "approved"),
    "published": ("auto_checking", "in_review", "approved", "published"),
    "withdrawn": ("auto_checking", "in_review", "approved", "published", "withdrawn"),
    "rejected": ("auto_checking", "in_review", "rejected"),
}

# No stimuli: these can be published.
PLAIN_SAMPLES: dict[str, Callable[[], Json]] = {
    "plain_mcq": samples.plain_mcq_document,
    "mcq": samples.mcq_document,
    "two_column_mcq": samples.two_column_mcq_document,
    "roman_mcq": samples.roman_mcq_document,
    "data_based": samples.data_based_document,
    "show_that": samples.show_that_document,
}
# With stimuli: can be reviewed and approved, never published (D-49).
VISUAL_SAMPLES: dict[str, Callable[[], Json]] = {
    "structured": samples.structured_document,
    "figure_options_mcq": samples.figure_options_mcq_document,
    "gallery": samples.gallery_document,
}
ALL_SAMPLES: dict[str, Callable[[], Json]] = {**PLAIN_SAMPLES, **VISUAL_SAMPLES}


def document(sample: Json | None = None) -> QuestionDocument:
    """Validate a sample dict (default: the two-part data-based sample, which has no stimuli)."""
    return QuestionDocument.model_validate(
        sample if sample is not None else samples.data_based_document()
    )


def other_document() -> QuestionDocument:
    """A valid document with different content and more parts than the default."""
    return document(samples.show_that_document())


def stored_json(doc: QuestionDocument) -> Json:
    result: Json = json.loads(doc.model_dump_json())
    return result


# --- edits that produce vocabulary problems (the schema accepts all of them) ---------------


def with_exam_section(value: str, base: Callable[[], Json] = samples.data_based_document) -> Json:
    d = base()
    d["exam_section"] = value
    return d


def with_command_term(value: str, base: Callable[[], Json] = samples.data_based_document) -> Json:
    d = base()
    d["parts"][0]["command_term"] = value
    return d


def with_nodes(
    primary: str,
    secondary: tuple[str, ...] = (),
    base: Callable[[], Json] = samples.data_based_document,
) -> Json:
    """Set the primary and secondary nodes; every part is moved to the primary node so the
    schema's 'part node is listed on the question' rule still holds."""
    d = base()
    d["primary_syllabus_node"] = primary
    d["secondary_syllabus_nodes"] = list(secondary)
    for part in d["parts"]:
        part["syllabus_node"] = primary
    return d


# --- environment ----------------------------------------------------------------------------


@dataclass(frozen=True)
class Env:
    syllabus_version_id: uuid.UUID
    rights_record_id: uuid.UUID


def now() -> datetime:
    return datetime.now(UTC)


def new_rights(
    session: Session,
    *,
    scope: rights.DisplayScope = rights.DisplayScope.ALL,
    valid_from: datetime | None = None,
    valid_until: datetime | None = None,
    revoked: bool = False,
) -> uuid.UUID:
    organization = uuid.uuid4() if scope is rights.DisplayScope.ORGANIZATION else None
    record_id = rights.create_record(
        session,
        holder="Synthetic holder",
        valid_from=valid_from if valid_from is not None else now() - timedelta(days=1),
        valid_until=valid_until,
        display_scope=scope,
        display_organization_id=organization,
    ).id
    if revoked:
        rights.revoke(session, record_id, at=now())
    return record_id


def load_syllabus(session: Session) -> uuid.UUID:
    reference = SyllabusReference.model_validate_json(REFERENCE_FILE.read_text())
    return load_reference(session, reference)


def make_env(session: Session) -> Env:
    return Env(load_syllabus(session), new_rights(session))


def create(
    session: Session,
    env: Env,
    doc: QuestionDocument | None = None,
    *,
    actor: str = AUTHOR,
    rights_record_id: uuid.UUID | None = None,
) -> svc.QuestionVersionView:
    return svc.create_question(
        session,
        actor=actor,
        document=doc if doc is not None else document(),
        rights_record_id=rights_record_id if rights_record_id is not None else env.rights_record_id,
        syllabus_version_id=env.syllabus_version_id,
    )


def failed_critical(code: str = "ext_check") -> svc.CheckResult:
    return svc.CheckResult(
        code=code,
        severity=svc.Severity.CRITICAL,
        outcome=svc.Outcome.FAILED,
        detail={"note": "synthetic"},
    )


def check(
    code: str, severity: svc.Severity, outcome: svc.Outcome, **detail: Any
) -> svc.CheckResult:
    return svc.CheckResult(code=code, severity=severity, outcome=outcome, detail=dict(detail))


def set_status_raw(connection: Connection, version_id: uuid.UUID, status: str) -> None:
    connection.execute(
        text("UPDATE question_version SET status = :s WHERE id = :v"),
        {"s": status, "v": version_id},
    )


def status_of(connection: Connection, version_id: uuid.UUID) -> str:
    status: str = connection.execute(
        text("SELECT status FROM question_version WHERE id = :v"), {"v": version_id}
    ).scalar_one()
    return status


def bring_to(
    session: Session,
    connection: Connection,
    env: Env,
    status: str,
    doc: QuestionDocument | None = None,
    *,
    rights_record_id: uuid.UUID | None = None,
) -> svc.QuestionVersionView:
    """A fresh question whose version 1 is in `status`, reached through the service wherever the
    service can get there (`auto_checking` only by raw SQL). The document must be publishable
    (no stimuli) for `published` and `withdrawn`."""
    view = create(session, env, doc, rights_record_id=rights_record_id)
    vid = view.id
    if status == "draft":
        pass
    elif status == "auto_checking":
        set_status_raw(connection, vid, "auto_checking")
    elif status == "needs_fix":
        svc.record_check(session, actor=AUTHOR, version_id=vid, result=failed_critical())
        svc.submit(session, actor=AUTHOR, version_id=vid)
    else:
        svc.submit(session, actor=AUTHOR, version_id=vid)
        if status == "rejected":
            svc.reject(session, actor=REVIEWER, version_id=vid, reason="not suitable")
        elif status != "in_review":
            svc.approve(session, actor=REVIEWER, version_id=vid)
            if status in ("published", "withdrawn"):
                svc.publish(session, actor=PUBLISHER, version_id=vid)
            if status == "withdrawn":
                svc.withdraw(session, actor=PUBLISHER, version_id=vid, reason="taken down")
    result = svc.get_version(session, vid)
    assert result.status.value == status, (result.status, status)
    return result


def publish_new(
    session: Session, connection: Connection, env: Env, doc: QuestionDocument | None = None
) -> svc.QuestionVersionView:
    return bring_to(session, connection, env, "published", doc)


# --- raw reads ------------------------------------------------------------------------------


def count(connection: Connection, table: str) -> int:
    allowed = {
        "question",
        "question_version",
        "part",
        "mark_point",
        "question_version_syllabus",
        "question_version_check",
        "audit_log",
    }
    assert table in allowed
    return int(connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one())  # noqa: S608


def table_counts(connection: Connection) -> dict[str, int]:
    return {
        t: count(connection, t)
        for t in (
            "question",
            "question_version",
            "part",
            "mark_point",
            "question_version_syllabus",
            "question_version_check",
            "audit_log",
        )
    }


def question_row(connection: Connection, question_id: uuid.UUID) -> Any:
    return connection.execute(
        text("SELECT * FROM question WHERE id = :q"), {"q": question_id}
    ).one()


def version_row(connection: Connection, version_id: uuid.UUID) -> Any:
    return connection.execute(
        text("SELECT * FROM question_version WHERE id = :v"), {"v": version_id}
    ).one()


def parts_of(connection: Connection, version_id: uuid.UUID) -> list[tuple[Any, ...]]:
    rows = connection.execute(
        text(
            "SELECT position, part_key, label, marks, answer_type FROM part "
            "WHERE question_version_id = :v ORDER BY position"
        ),
        {"v": version_id},
    ).all()
    return [tuple(r) for r in rows]


def mark_points_of(
    connection: Connection, version_id: uuid.UUID
) -> dict[str, list[tuple[Any, ...]]]:
    """Mark point rows by part key, each list in position order."""
    rows = connection.execute(
        text(
            "SELECT p.part_key, m.position, m.point_key, m.kind, m.alternative_group, m.route "
            "FROM mark_point m JOIN part p ON p.id = m.part_id "
            "WHERE p.question_version_id = :v ORDER BY p.position, m.position"
        ),
        {"v": version_id},
    ).all()
    result: dict[str, list[tuple[Any, ...]]] = {}
    for key, position, point_key, kind, group, route in rows:
        result.setdefault(key, []).append((position, point_key, kind, group, route))
    return result


def syllabus_rows_of(connection: Connection, version_id: uuid.UUID) -> list[tuple[str, bool]]:
    rows = connection.execute(
        text(
            "SELECT n.code, s.is_primary FROM question_version_syllabus s "
            "JOIN syllabus_node n ON n.id = s.syllabus_node_id "
            "WHERE s.question_version_id = :v ORDER BY n.code"
        ),
        {"v": version_id},
    ).all()
    return [(code, primary) for code, primary in rows]


def checks_raw(connection: Connection, version_id: uuid.UUID) -> list[tuple[str, str, str]]:
    rows = connection.execute(
        text(
            "SELECT check_code, severity, outcome FROM question_version_check "
            "WHERE question_version_id = :v ORDER BY check_code"
        ),
        {"v": version_id},
    ).all()
    return [(c, s, o) for c, s, o in rows]


def expected_parts(doc: QuestionDocument) -> list[tuple[str, str | None, int]]:
    """(part_key, label, marks) for each part, in order; one 'mcq' part for multiple choice."""
    if doc.mcq is not None:
        return [("mcq", None, doc.total_marks)]
    return [(p.id, p.label, p.marks) for p in doc.parts]


def expected_mark_points(
    doc: QuestionDocument,
) -> dict[str, list[tuple[str, str, str | None, str | None]]]:
    return {
        p.id: [(m.id, m.kind.value, m.alternative_group, m.route) for m in p.mark_points]
        for p in doc.parts
    }


def expected_nodes(doc: QuestionDocument) -> list[tuple[str, bool]]:
    nodes = [(doc.primary_syllabus_node, True)]
    nodes += [(n, False) for n in doc.secondary_syllabus_nodes]
    return sorted(nodes)


def snapshot(session: Session, connection: Connection, question_id: uuid.UUID) -> Any:
    """Everything a failed call must leave untouched, as plain comparable data."""
    versions = connection.execute(
        text(
            "SELECT id, version_no, status, content_sha256, document::text AS document, "
            "total_marks, exam_section FROM question_version WHERE question_id = :q "
            "ORDER BY version_no"
        ),
        {"q": question_id},
    ).all()
    snap: list[Any] = [[tuple(v) for v in versions]]
    for v in versions:
        snap.append(parts_of(connection, v.id))
        snap.append(mark_points_of(connection, v.id))
        snap.append(syllabus_rows_of(connection, v.id))
        snap.append(
            connection.execute(
                text(
                    "SELECT check_code, severity, outcome, detail::text "
                    "FROM question_version_check "
                    "WHERE question_version_id = :v ORDER BY check_code"
                ),
                {"v": v.id},
            ).all()
        )
    snap.append(table_counts(connection))
    return snap


def audit_for(session: Session, version_id: uuid.UUID) -> list[Any]:
    from qlab.audit import service as audit

    return audit.entries_for(session, "question_version", str(version_id))


def audit_actions(session: Session, version_id: uuid.UUID) -> list[str]:
    return [e.action for e in audit_for(session, version_id)]


def new_audit(session: Session, version_id: uuid.UUID, before: int) -> list[Any]:
    return audit_for(session, version_id)[before:]


def data_text(entry: Any) -> str:
    """The entry's data rendered as text, to look for a value without fixing key names."""
    return json.dumps(dict(entry.data), default=str)


def usable(session: Session) -> None:
    """After an expected error the session must still run queries."""
    assert session.execute(text("SELECT 1")).scalar_one() == 1


def copy_json(d: Json) -> Json:
    return copy.deepcopy(d)


# --- raw construction (database-rule tests never call the content service) -------------------


def raw_question(
    connection: Connection, env: Env, *, origin: str = "authored", created_by: str = AUTHOR
) -> uuid.UUID:
    question_id = uuid.uuid4()
    connection.execute(
        text(
            "INSERT INTO question (id, origin, rights_record_id, syllabus_version_id, created_by) "
            "VALUES (:id, :origin, :rights, :syllabus, :by)"
        ),
        {
            "id": question_id,
            "origin": origin,
            "rights": env.rights_record_id,
            "syllabus": env.syllabus_version_id,
            "by": created_by,
        },
    )
    return question_id


def raw_version(
    connection: Connection,
    question_id: uuid.UUID,
    doc: QuestionDocument | None = None,
    *,
    version_no: int = 1,
    status: str | None = None,
    created_by: str = AUTHOR,
) -> uuid.UUID:
    """Insert a version row; `status` None leaves the column default."""
    d = doc if doc is not None else document()
    version_id = uuid.uuid4()
    columns = (
        "id, question_id, version_no, schema_version, document, content_sha256, question_class, "
        "exam_section, levels, total_marks, created_by"
    )
    values = (
        ":id, :q, :no, :sv, CAST(:doc AS jsonb), :sha, :cls, :sec, CAST(:levels AS text[]), "
        ":marks, :by"
    )
    params: dict[str, Any] = {
        "id": version_id,
        "q": question_id,
        "no": version_no,
        "sv": d.schema_version,
        "doc": d.model_dump_json(),
        "sha": svc.content_sha256(d),
        "cls": d.question_class.value,
        "sec": d.exam_section,
        "levels": [level.value for level in d.levels],
        "marks": d.total_marks,
        "by": created_by,
    }
    if status is not None:
        columns += ", status"
        values += ", :status"
        params["status"] = status
    connection.execute(
        text(f"INSERT INTO question_version ({columns}) VALUES ({values})"),  # noqa: S608
        params,
    )
    return version_id


def raw_part(
    connection: Connection, version_id: uuid.UUID, key: str, position: int = 0
) -> uuid.UUID:
    part_id = uuid.uuid4()
    connection.execute(
        text(
            "INSERT INTO part (id, question_version_id, position, part_key, label, marks, "
            "answer_type) VALUES (:id, :v, :pos, :key, 'a', 1, 'word_phrase')"
        ),
        {"id": part_id, "v": version_id, "pos": position, "key": key},
    )
    return part_id


def raw_mark_point(
    connection: Connection, part_id: uuid.UUID, key: str, position: int = 0
) -> uuid.UUID:
    point_id = uuid.uuid4()
    connection.execute(
        text(
            "INSERT INTO mark_point (id, part_id, position, point_key, kind) "
            "VALUES (:id, :p, :pos, :key, 'statement')"
        ),
        {"id": point_id, "p": part_id, "pos": position, "key": key},
    )
    return point_id


def node_id(connection: Connection, env: Env, code: str) -> uuid.UUID:
    result: uuid.UUID = connection.execute(
        text("SELECT id FROM syllabus_node WHERE syllabus_version_id = :v AND code = :c"),
        {"v": env.syllabus_version_id, "c": code},
    ).scalar_one()
    return result


def raw_syllabus_row(
    connection: Connection, env: Env, version_id: uuid.UUID, code: str, *, primary: bool = False
) -> None:
    connection.execute(
        text(
            "INSERT INTO question_version_syllabus (question_version_id, syllabus_node_id, "
            "is_primary) VALUES (:v, :n, :p)"
        ),
        {"v": version_id, "n": node_id(connection, env, code), "p": primary},
    )


def raw_check(
    connection: Connection,
    version_id: uuid.UUID,
    code: str = "ext_check",
    severity: str = "critical",
    outcome: str = "failed",
) -> uuid.UUID:
    check_id = uuid.uuid4()
    connection.execute(
        text(
            "INSERT INTO question_version_check (id, question_version_id, check_code, severity, "
            "outcome) VALUES (:id, :v, :code, :sev, :out)"
        ),
        {"id": check_id, "v": version_id, "code": code, "sev": severity, "out": outcome},
    )
    return check_id


def raw_walk(connection: Connection, version_id: uuid.UUID, status: str) -> None:
    """Move a draft version to `status` through allowed raw status updates."""
    for step in RAW_PATH[status]:
        set_status_raw(connection, version_id, step)


@dataclass(frozen=True)
class RawVersion:
    question_id: uuid.UUID
    version_id: uuid.UUID
    part_id: uuid.UUID
    mark_point_id: uuid.UUID
    check_id: uuid.UUID


def raw_full_version(
    connection: Connection, env: Env, doc: QuestionDocument | None = None
) -> RawVersion:
    """A draft version with one part, one mark point, one syllabus row and one check row
    (a passed critical check, so the version can still be published)."""
    question_id = raw_question(connection, env)
    version_id = raw_version(connection, question_id, doc)
    part_id = raw_part(connection, version_id, "p-a")
    point_id = raw_mark_point(connection, part_id, "a-1")
    raw_syllabus_row(connection, env, version_id, "A.1", primary=True)
    check_id = raw_check(connection, version_id, "ext_check", "critical", "passed")
    return RawVersion(question_id, version_id, part_id, point_id, check_id)
