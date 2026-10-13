"""Content service acceptance tests, written from the frozen contract only.

Specification: the module and function docstrings of qlab.content.service (commit cf7c754),
docs/DOMAIN_MODEL.md sections 4 and 6, CLAUDE.md rules 2, 3, 7 and 8, decisions D-50, D-52, D-53.
The owner's clarification of 2026-10-12: content is editable in place in `draft` and `needs_fix`,
and `approved -> needs_fix` exists through `request_changes`.

Every test goes through the service; raw SQL is used only to read what the service stored and to
reach `auto_checking`, which the service itself never leaves in a state a caller can observe.
What the database enforces on its own is in test_content_database_rules.py.
"""

from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import json
import re
import uuid
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import timedelta

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from qlab.content import math as qmath
from qlab.content import service as svc
from qlab.content.math import KATEX_VERSION, RendererUnavailable, math_nodes
from qlab.content.schema import QuestionDocument
from qlab.rights import service as rights
from tests.content import samples
from tests.content.support import (
    ALL_SAMPLES,
    ALL_STATUSES,
    AUTHOR,
    NO_HASH,
    PLAIN_SAMPLES,
    PUBLISHER,
    REQUIRED_CHECKS,
    REVIEWER,
    VISUAL_SAMPLES,
    WORKING_STATUSES,
    Env,
    Json,
    approve,
    audit_actions,
    audit_for,
    bring_to,
    check,
    checks_raw,
    create,
    data_text,
    document,
    expected_mark_points,
    expected_nodes,
    expected_parts,
    failed_critical,
    make_env,
    mark_points_of,
    new_audit,
    new_rights,
    now,
    other_document,
    parts_of,
    publish,
    publish_new,
    raw_check,
    raw_full_version,
    raw_question,
    raw_walk,
    republish,
    set_status_raw,
    snapshot,
    status_of,
    stored_hash,
    stored_json,
    syllabus_rows_of,
    table_counts,
    usable,
    version_row,
    with_command_term,
    with_exam_section,
    with_nodes,
)

pytestmark = pytest.mark.db

OP_ACTOR = "u_operator"
REASON = "needs a clearer stem"


@pytest.fixture(autouse=True)
def clean_math_cache() -> Iterator[None]:
    """Rendering answers are kept per process; each test starts without any, so a test about
    the renderer (missing, unusable) is never satisfied by what an earlier test cached."""
    qmath._CACHE.clear()
    yield
    qmath._CACHE.clear()


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


STATE_FIELDS = {"id", "question_id", "version_no", "status", "content_sha256"}


def assert_state_without_content(result: object) -> None:
    """The answer of a state-changing call is a VersionState: no document, no staff view."""
    assert type(result) is svc.VersionState
    assert isinstance(result, svc.VersionState)
    assert not isinstance(result, svc.QuestionVersionView)
    assert {f.name for f in dataclasses.fields(result)} == STATE_FIELDS
    assert not hasattr(result, "document")


# =============================================================================================
# 1. Round trip and derived rows
# =============================================================================================


@pytest.mark.parametrize("name", list(ALL_SAMPLES))
def test_create_then_get_returns_the_same_document(
    session: Session, connection: Connection, env: Env, name: str
) -> None:
    doc = document(ALL_SAMPLES[name]())
    created = create(session, env, doc, actor="u_creator")

    for view in (created, svc.get_version(session, created.id)):
        assert view.document == doc
        assert view.status is svc.VersionStatus.DRAFT
        assert view.version_no == 1
        assert view.created_by == "u_creator"
        assert view.has_unverified_visuals is bool(doc.stimuli)
        assert svc.content_sha256(view.document) == view.content_sha256
        assert view.content_sha256 == svc.content_sha256(doc)
    assert created.question_id == svc.get_version(session, created.id).question_id
    assert created.updated_at >= created.created_at

    row = version_row(connection, created.id)
    assert row.document == stored_json(doc)
    assert row.content_sha256 == svc.content_sha256(doc)
    assert row.status == "draft"
    assert row.has_unverified_visuals is bool(doc.stimuli)
    assert row.schema_version == doc.schema_version
    assert row.question_class == doc.question_class.value
    assert row.exam_section == doc.exam_section
    assert list(row.levels) == [level.value for level in doc.levels]
    assert row.total_marks == doc.total_marks


@pytest.mark.parametrize("name", list(ALL_SAMPLES))
def test_derived_rows_follow_the_document(
    session: Session, connection: Connection, env: Env, name: str
) -> None:
    doc = document(ALL_SAMPLES[name]())
    view = create(session, env, doc)

    parts = parts_of(connection, view.id)
    assert [(key, label, marks) for _, key, label, marks, _ in parts] == expected_parts(doc)
    assert [p[0] for p in parts] == list(range(len(parts)))  # positions count from 0
    if doc.mcq is None:
        assert [answer_type for *_, answer_type in parts] == [
            p.answer_type.value for p in doc.parts
        ]
    else:
        assert parts[0][4]  # an MCQ part still records an answer type (value not specified)

    points = mark_points_of(connection, view.id)
    expected = expected_mark_points(doc)
    assert set(points) == {key for key, items in expected.items() if items}
    for key, rows in points.items():
        assert [(k, kind, group, route) for _, k, kind, group, route in rows] == expected[key]
        assert [r[0] for r in rows] == list(range(len(rows)))

    rows = syllabus_rows_of(connection, view.id)
    assert rows == expected_nodes(doc)
    assert [code for code, primary in rows if primary] == [doc.primary_syllabus_node]


def test_derived_rows_distinguish_primary_from_secondary_nodes(
    session: Session, connection: Connection, env: Env
) -> None:
    doc = document(samples.show_that_document())
    view = create(session, env, doc)
    assert syllabus_rows_of(connection, view.id) == [("A.2", False), ("A.3", False), ("A.4", True)]


def test_a_multiple_choice_question_has_one_part_without_mark_points(
    session: Session, connection: Connection, env: Env
) -> None:
    view = create(session, env, document(samples.mcq_document()))
    parts = parts_of(connection, view.id)
    assert len(parts) == 1
    _, key, label, marks, _ = parts[0]
    assert (key, label, marks) == ("mcq", None, 1)
    assert mark_points_of(connection, view.id) == {}


def test_the_question_row_records_origin_rights_syllabus_and_creator(
    session: Session, connection: Connection, env: Env
) -> None:
    view = create(session, env, actor="u_creator")
    question = svc.get_question(session, view.question_id)
    assert question.id == view.question_id
    assert question.origin is svc.Origin.AUTHORED
    assert question.rights_record_id == env.rights_record_id
    assert question.syllabus_version_id == env.syllabus_version_id
    assert question.created_by == "u_creator"
    raw = connection.execute(
        text("SELECT origin, syllabus_status FROM question WHERE id = :q"),
        {"q": view.question_id},
    ).one()
    assert tuple(raw) == ("authored", "in_syllabus")


def test_creating_the_same_document_twice_makes_independent_questions(
    session: Session, env: Env
) -> None:
    first = create(session, env)
    second = create(session, env)
    assert first.question_id != second.question_id
    assert first.id != second.id
    assert first.content_sha256 == second.content_sha256
    assert [v.id for v in svc.list_versions(session, first.question_id)] == [first.id]


def test_content_sha256_is_the_sha256_of_the_canonical_json() -> None:
    doc = document()
    expected = hashlib.sha256(doc.model_dump_json().encode()).hexdigest()
    assert svc.content_sha256(doc) == expected
    assert re.fullmatch(r"[0-9a-f]{64}", expected)
    assert svc.content_sha256(other_document()) != expected
    assert svc.content_sha256(QuestionDocument.model_validate_json(doc.model_dump_json())) == (
        expected
    )


# =============================================================================================
# 2. Rights are fail-closed (CLAUDE.md rule 2)
# =============================================================================================

DENIED_RIGHTS: dict[str, Callable[[Session], uuid.UUID]] = {
    "unknown": lambda s: uuid.uuid4(),
    "not_yet_valid": lambda s: new_rights(s, valid_from=now() + timedelta(days=1)),
    "expired": lambda s: new_rights(
        s, valid_from=now() - timedelta(days=2), valid_until=now() - timedelta(days=1)
    ),
    "revoked": lambda s: new_rights(s, revoked=True),
    "scope_none": lambda s: new_rights(s, scope=rights.DisplayScope.NONE),
    "scope_organization": lambda s: new_rights(s, scope=rights.DisplayScope.ORGANIZATION),
}


@pytest.mark.parametrize("case", list(DENIED_RIGHTS))
def test_create_without_display_rights_for_everyone_is_denied_and_writes_nothing(
    session: Session, connection: Connection, env: Env, case: str
) -> None:
    record_id = DENIED_RIGHTS[case](session)
    before = table_counts(connection)
    with pytest.raises(rights.RightsDenied):
        create(session, env, rights_record_id=record_id)
    assert table_counts(connection) == before
    usable(session)


def test_a_valid_record_with_a_future_expiry_is_accepted(session: Session, env: Env) -> None:
    record_id = new_rights(session, valid_until=now() + timedelta(days=30))
    assert create(session, env, rights_record_id=record_id).status is svc.VersionStatus.DRAFT


READS: dict[str, Callable[[Session, svc.QuestionVersionView], object]] = {
    "get_question": lambda s, v: svc.get_question(s, v.question_id),
    "get_version": lambda s, v: svc.get_version(s, v.id),
    "list_versions": lambda s, v: svc.list_versions(s, v.question_id),
    "get_published_version": lambda s, v: svc.get_published_version(s, v.question_id),
    "get_checks": lambda s, v: svc.get_checks(s, v.id),
}


@pytest.mark.parametrize("read", list(READS))
def test_after_revocation_every_read_behaves_as_if_the_question_did_not_exist(
    session: Session, connection: Connection, env: Env, read: str
) -> None:
    record_id = new_rights(session)
    version = publish_new(session, connection, env)  # on the shared record: control
    assert READS[read](session, version) is not None
    own = bring_to(session, connection, env, "published", rights_record_id=record_id)
    assert READS[read](session, own) is not None

    rights.revoke(session, record_id, at=now())

    with pytest.raises(svc.NotFound):
        READS[read](session, own)
    usable(session)
    assert READS[read](session, version) is not None  # other questions are unaffected


def test_after_revocation_get_published_version_is_not_found_not_a_stale_view(
    session: Session, connection: Connection, env: Env
) -> None:
    record_id = new_rights(session)
    own = bring_to(session, connection, env, "published", rights_record_id=record_id)
    assert svc.get_published_version(session, own.question_id).id == own.id
    rights.revoke(session, record_id, at=now())
    with pytest.raises(svc.NotFound):
        svc.get_published_version(session, own.question_id)


REVOKED_WRITES: dict[str, Callable[[Session, svc.QuestionVersionView], object]] = {
    "update_draft": lambda s, v: svc.update_draft(
        s, actor=OP_ACTOR, version_id=v.id, document=other_document()
    ),
    "submit": lambda s, v: svc.submit(s, actor=OP_ACTOR, version_id=v.id),
    "approve": lambda s, v: approve(s, v.id, OP_ACTOR),
    "record_check": lambda s, v: svc.record_check(
        s, actor=OP_ACTOR, version_id=v.id, result=failed_critical()
    ),
    "start_revision": lambda s, v: svc.start_revision(s, actor=OP_ACTOR, question_id=v.question_id),
}


@pytest.mark.parametrize("status", ALL_STATUSES)
@pytest.mark.parametrize("operation", list(REVOKED_WRITES))
def test_after_revocation_writes_are_denied_whatever_the_status_and_change_nothing(
    session: Session, connection: Connection, env: Env, operation: str, status: str
) -> None:
    record_id = new_rights(session)
    version = bring_to(session, connection, env, status, rights_record_id=record_id)
    rights.revoke(session, record_id, at=now())
    before = snapshot(session, connection, version.question_id)

    with pytest.raises(rights.RightsDenied):
        REVOKED_WRITES[operation](session, version)

    assert snapshot(session, connection, version.question_id) == before
    usable(session)


def test_after_revocation_publish_is_refused_with_rights_denied_and_stays_approved(
    session: Session, connection: Connection, env: Env
) -> None:
    record_id = new_rights(session)
    version = bring_to(session, connection, env, "approved", rights_record_id=record_id)
    rights.revoke(session, record_id, at=now())
    with pytest.raises(svc.NotPublishable) as caught:
        publish(session, version.id, OP_ACTOR)
    assert caught.value.reasons == ("rights_denied",)
    assert status_of(connection, version.id) == "approved"
    usable(session)


def test_publish_checks_status_and_hash_before_it_reports_missing_rights(
    session: Session, connection: Connection, env: Env
) -> None:
    record_id = new_rights(session)
    in_review = bring_to(session, connection, env, "in_review", rights_record_id=record_id)
    approved = bring_to(session, connection, env, "approved", rights_record_id=record_id)
    rights.revoke(session, record_id, at=now())
    with pytest.raises(svc.InvalidTransition):
        publish(session, in_review.id, OP_ACTOR)
    with pytest.raises(svc.StaleContent):
        svc.publish(
            session, actor=OP_ACTOR, version_id=approved.id, expected_content_sha256=NO_HASH
        )
    with pytest.raises(svc.NotPublishable) as caught:
        publish(session, approved.id, OP_ACTOR)
    assert "rights_denied" in caught.value.reasons


def test_republish_checks_status_and_hash_before_it_reports_missing_rights(
    session: Session, connection: Connection, env: Env
) -> None:
    record_id = new_rights(session)
    published = bring_to(session, connection, env, "published", rights_record_id=record_id)
    withdrawn = bring_to(session, connection, env, "withdrawn", rights_record_id=record_id)
    rights.revoke(session, record_id, at=now())
    with pytest.raises(svc.InvalidTransition):
        republish(session, published.id, OP_ACTOR)
    with pytest.raises(svc.StaleContent):
        svc.republish(
            session,
            actor=OP_ACTOR,
            version_id=withdrawn.id,
            expected_content_sha256=NO_HASH,
            reason=REASON,
        )
    with pytest.raises(svc.NotPublishable) as caught:
        republish(session, withdrawn.id, OP_ACTOR)
    assert "rights_denied" in caught.value.reasons


def test_publish_lists_every_reason_that_applies(
    session: Session, connection: Connection, env: Env
) -> None:
    record_id = new_rights(session)
    version = bring_to(
        session,
        connection,
        env,
        "approved",
        document(samples.structured_document()),
        rights_record_id=record_id,
    )
    rights.revoke(session, record_id, at=now())
    with pytest.raises(svc.NotPublishable) as caught:
        publish(session, version.id, OP_ACTOR)
    assert set(caught.value.reasons) == {"rights_denied", "unverified_visuals"}


def test_after_revocation_a_published_version_can_still_be_withdrawn(
    session: Session, connection: Connection, env: Env
) -> None:
    record_id = new_rights(session)
    version = bring_to(session, connection, env, "published", rights_record_id=record_id)
    rights.revoke(session, record_id, at=now())
    result = svc.withdraw(session, actor=OP_ACTOR, version_id=version.id, reason=REASON)
    assert_state_without_content(result)
    assert result.status is svc.VersionStatus.WITHDRAWN
    assert status_of(connection, version.id) == "withdrawn"
    assert audit_actions(session, version.id)[-1] == "question_version.withdrawn"


def test_after_revocation_an_in_review_version_can_still_be_rejected(
    session: Session, connection: Connection, env: Env
) -> None:
    record_id = new_rights(session)
    version = bring_to(session, connection, env, "in_review", rights_record_id=record_id)
    rights.revoke(session, record_id, at=now())
    result = svc.reject(session, actor=OP_ACTOR, version_id=version.id, reason=REASON)
    assert_state_without_content(result)
    assert result.status is svc.VersionStatus.REJECTED
    assert status_of(connection, version.id) == "rejected"


@pytest.mark.parametrize("status", ["in_review", "approved"])
def test_after_revocation_changes_can_still_be_requested(
    session: Session, connection: Connection, env: Env, status: str
) -> None:
    record_id = new_rights(session)
    version = bring_to(session, connection, env, status, rights_record_id=record_id)
    rights.revoke(session, record_id, at=now())
    result = svc.request_changes(session, actor=OP_ACTOR, version_id=version.id, reason=REASON)
    assert_state_without_content(result)
    assert result.status is svc.VersionStatus.NEEDS_FIX
    assert status_of(connection, version.id) == "needs_fix"


def test_republish_needs_rights_like_publish(
    session: Session, connection: Connection, env: Env
) -> None:
    record_id = new_rights(session)
    version = bring_to(session, connection, env, "withdrawn", rights_record_id=record_id)
    rights.revoke(session, record_id, at=now())
    with pytest.raises(svc.NotPublishable) as caught:
        republish(session, version.id, OP_ACTOR)
    assert "rights_denied" in caught.value.reasons
    assert status_of(connection, version.id) == "withdrawn"


# =============================================================================================
# 3. Origin is closed (D-52)
# =============================================================================================


@pytest.mark.parametrize("origin", [svc.Origin.GENERATED, svc.Origin.SOURCE_ORIGINAL])
def test_only_authored_origin_is_accepted(
    session: Session, connection: Connection, env: Env, origin: svc.Origin
) -> None:
    before = table_counts(connection)
    with pytest.raises(svc.OriginClosed):
        svc.create_question(
            session,
            actor=AUTHOR,
            document=document(),
            rights_record_id=env.rights_record_id,
            syllabus_version_id=env.syllabus_version_id,
            origin=origin,
        )
    assert table_counts(connection) == before
    usable(session)


@pytest.mark.parametrize("origin", [svc.Origin.GENERATED, svc.Origin.SOURCE_ORIGINAL])
def test_origin_is_checked_before_anything_else(
    session: Session, connection: Connection, origin: svc.Origin
) -> None:
    before = table_counts(connection)
    with pytest.raises(svc.OriginClosed):
        svc.create_question(
            session,
            actor=AUTHOR,
            document=document(with_exam_section("paper_9")),
            rights_record_id=uuid.uuid4(),
            syllabus_version_id=uuid.uuid4(),
            origin=origin,
        )
    assert table_counts(connection) == before


def test_authored_is_the_default_origin(session: Session, env: Env) -> None:
    view = create(session, env)
    assert svc.get_question(session, view.question_id).origin is svc.Origin.AUTHORED


# =============================================================================================
# 4. Vocabulary
# =============================================================================================


def mentions(errors: tuple[str, ...], value: str) -> bool:
    pattern = re.compile(rf"(?<![\w.]){re.escape(value)}(?![\w.])")
    return any(pattern.search(error) for error in errors)


BAD_VOCABULARY: dict[str, tuple[Callable[[], Json], list[str]]] = {
    "unknown_exam_section": (lambda: with_exam_section("paper_9"), ["paper_9"]),
    "unknown_command_term": (lambda: with_command_term("juggle"), ["juggle"]),
    "unknown_primary_node": (lambda: with_nodes("Z.9"), ["Z.9"]),
    "unknown_secondary_node": (lambda: with_nodes("A.1", ("Z.8",)), ["Z.8"]),
    "non_leaf_primary_node": (lambda: with_nodes("A"), ["A"]),
    "non_leaf_secondary_node": (lambda: with_nodes("A.1", ("A",)), ["A"]),
    "non_leaf_on_a_multiple_choice_question": (
        lambda: {**samples.plain_mcq_document(), "primary_syllabus_node": "A"},
        ["A"],
    ),
    "several_problems": (
        lambda: {
            **with_nodes("Z.9", ("Z.8", "A")),
            "exam_section": "paper_9",
            "parts": [{**p, "command_term": "juggle"} for p in with_nodes("Z.9")["parts"]],
        },
        ["Z.9", "Z.8", "A", "paper_9", "juggle"],
    ),
}


@pytest.mark.parametrize("case", list(BAD_VOCABULARY))
def test_create_rejects_labels_the_syllabus_version_does_not_define(
    session: Session, connection: Connection, env: Env, case: str
) -> None:
    build, offending = BAD_VOCABULARY[case]
    doc = document(build())
    before = table_counts(connection)
    with pytest.raises(svc.InvalidDocument) as caught:
        create(session, env, doc)
    for value in offending:
        assert mentions(caught.value.errors, value), (value, caught.value.errors)
    assert table_counts(connection) == before
    usable(session)


def test_every_problem_is_listed_as_its_own_error(session: Session, env: Env) -> None:
    build, offending = BAD_VOCABULARY["several_problems"]
    with pytest.raises(svc.InvalidDocument) as caught:
        create(session, env, document(build()))
    assert len(caught.value.errors) >= len(offending)
    assert str(caught.value) == "; ".join(caught.value.errors)


@pytest.mark.parametrize("case", list(BAD_VOCABULARY))
def test_update_draft_with_such_a_document_changes_nothing(
    session: Session, connection: Connection, env: Env, case: str
) -> None:
    build, offending = BAD_VOCABULARY[case]
    version = create(session, env, document(samples.show_that_document()))
    before = snapshot(session, connection, version.question_id)
    entries = len(audit_for(session, version.id))
    with pytest.raises(svc.InvalidDocument) as caught:
        svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=document(build()))
    for value in offending:
        assert mentions(caught.value.errors, value)
    assert snapshot(session, connection, version.question_id) == before
    assert len(audit_for(session, version.id)) == entries
    assert svc.get_version(session, version.id).content_sha256 == version.content_sha256


def test_update_from_needs_fix_with_a_bad_document_stays_in_needs_fix(
    session: Session, connection: Connection, env: Env
) -> None:
    version = bring_to(session, connection, env, "needs_fix")
    before = snapshot(session, connection, version.question_id)
    with pytest.raises(svc.InvalidDocument):
        svc.update_draft(
            session,
            actor=OP_ACTOR,
            version_id=version.id,
            document=document(with_exam_section("paper_9")),
        )
    assert snapshot(session, connection, version.question_id) == before
    assert status_of(connection, version.id) == "needs_fix"


def test_an_unknown_syllabus_version_is_a_lookup_error(
    session: Session, connection: Connection, env: Env
) -> None:
    before = table_counts(connection)
    with pytest.raises(LookupError):
        svc.create_question(
            session,
            actor=AUTHOR,
            document=document(),
            rights_record_id=env.rights_record_id,
            syllabus_version_id=uuid.uuid4(),
        )
    assert table_counts(connection) == before
    usable(session)


@pytest.mark.parametrize("name", list(ALL_SAMPLES))
def test_every_sample_passes_the_vocabulary_of_the_reference_syllabus(
    session: Session, env: Env, name: str
) -> None:
    create(session, env, document(ALL_SAMPLES[name]()))


# =============================================================================================
# 5. Lifecycle through the service
# =============================================================================================


def test_happy_path_writes_the_documented_audit_sequence(
    session: Session, connection: Connection, env: Env
) -> None:
    created = create(session, env, actor="u_author")
    sha = created.content_sha256
    submitted = svc.submit(session, actor="u_submitter", version_id=created.id)
    assert_state_without_content(submitted)
    assert submitted.status is svc.VersionStatus.IN_REVIEW
    approved = approve(session, created.id, "u_approver")
    assert_state_without_content(approved)
    assert approved.status is svc.VersionStatus.APPROVED
    published = publish(session, created.id, "u_publisher")
    assert_state_without_content(published)
    assert published.status is svc.VersionStatus.PUBLISHED
    assert published.id == created.id
    assert published.content_sha256 == sha

    entries = audit_for(session, created.id)
    assert [(e.action, e.actor) for e in entries] == [
        ("question_version.created", "u_author"),
        ("question_version.submitted", "u_submitter"),
        ("question_version.checks_passed", "u_submitter"),
        ("question_version.approved", "u_approver"),
        ("question_version.published", "u_publisher"),
    ]
    assert all(e.data["content_sha256"] == sha for e in entries)
    assert (entries[3].data["previous_status"], entries[3].data["status"]) == (
        "in_review",
        "approved",
    )
    assert (entries[4].data["previous_status"], entries[4].data["status"]) == (
        "approved",
        "published",
    )
    assert svc.get_published_version(session, created.question_id).id == created.id
    assert status_of(connection, created.id) == "published"


def test_a_reader_gets_the_published_content_and_nothing_else(
    session: Session, connection: Connection, env: Env
) -> None:
    version = publish_new(session, connection, env)
    published = svc.get_published_version(session, version.question_id)
    assert published.id == version.id
    assert published.document == version.document
    assert published.status is svc.VersionStatus.PUBLISHED


@pytest.mark.parametrize("status", ["in_review", "approved"])
def test_request_changes_sends_a_version_back_and_records_the_reason(
    session: Session, connection: Connection, env: Env, status: str
) -> None:
    version = bring_to(session, connection, env, status)
    before = len(audit_for(session, version.id))
    result = svc.request_changes(
        session, actor="u_reviewer", version_id=version.id, reason="  needs a clearer stem  "
    )
    assert result.status is svc.VersionStatus.NEEDS_FIX
    assert result.content_sha256 == version.content_sha256
    (entry,) = new_audit(session, version.id, before)
    assert entry.action == "question_version.changes_requested"
    assert entry.actor == "u_reviewer"
    assert "needs a clearer stem" in data_text(entry)
    assert status_of(connection, version.id) == "needs_fix"


def test_a_version_sent_back_is_edited_in_place_and_becomes_a_draft(
    session: Session, connection: Connection, env: Env
) -> None:
    version = bring_to(session, connection, env, "approved")
    svc.request_changes(session, actor=REVIEWER, version_id=version.id, reason=REASON)
    new_doc = other_document()
    before = len(audit_for(session, version.id))

    result = svc.update_draft(session, actor="u_editor", version_id=version.id, document=new_doc)

    assert result.id == version.id
    assert result.version_no == 1
    assert result.status is svc.VersionStatus.DRAFT
    assert result.document == new_doc
    assert result.content_sha256 == svc.content_sha256(new_doc) != version.content_sha256
    (entry,) = new_audit(session, version.id, before)
    assert entry.action == "question_version.updated"
    assert entry.actor == "u_editor"
    assert entry.data["content_sha256"] == result.content_sha256
    assert entry.data["previous_content_sha256"] == version.content_sha256
    assert status_of(connection, version.id) == "draft"
    assert [p[1] for p in parts_of(connection, version.id)] == [p.id for p in new_doc.parts]
    assert syllabus_rows_of(connection, version.id) == expected_nodes(new_doc)
    stored_points = mark_points_of(connection, version.id)
    assert {key: [r[1:] for r in rows] for key, rows in stored_points.items()} == (
        expected_mark_points(new_doc)
    )


def test_update_draft_in_draft_keeps_the_status_and_rebuilds_derived_rows(
    session: Session, connection: Connection, env: Env
) -> None:
    version = create(session, env, document(samples.show_that_document()))
    new_doc = document(samples.data_based_document())
    result = svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=new_doc)
    assert result.status is svc.VersionStatus.DRAFT
    assert svc.get_version(session, version.id).document == new_doc
    assert [(k, label, m) for _, k, label, m, _ in parts_of(connection, version.id)] == (
        expected_parts(new_doc)
    )
    assert syllabus_rows_of(connection, version.id) == [("A.1", True)]
    row = version_row(connection, version.id)
    assert row.document == stored_json(new_doc)
    assert (row.exam_section, row.total_marks) == (new_doc.exam_section, new_doc.total_marks)
    assert row.updated_at >= row.created_at


def test_update_draft_may_add_stimuli_and_the_flag_follows_the_document(
    session: Session, env: Env
) -> None:
    version = create(session, env)
    assert version.has_unverified_visuals is False
    with_visual = svc.update_draft(
        session,
        actor=OP_ACTOR,
        version_id=version.id,
        document=document(samples.structured_document()),
    )
    assert with_visual.has_unverified_visuals is True
    without = svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=document())
    assert without.has_unverified_visuals is False


def test_reject_is_final(session: Session, connection: Connection, env: Env) -> None:
    version = bring_to(session, connection, env, "in_review")
    result = svc.reject(session, actor=REVIEWER, version_id=version.id, reason="not suitable")
    assert result.status is svc.VersionStatus.REJECTED
    entry = audit_for(session, version.id)[-1]
    assert entry.action == "question_version.rejected"
    assert "not suitable" in data_text(entry)
    for call in OPS.values():
        with pytest.raises(svc.InvalidTransition):
            call.call(session, version.id)
    assert status_of(connection, version.id) == "rejected"


@dataclass(frozen=True)
class OpSpec:
    call: Callable[[Session, uuid.UUID], object]
    allowed: frozenset[str]
    actions: tuple[str, ...]
    result_status: str | None  # None: the status does not change


OPS: dict[str, OpSpec] = {
    "update_draft": OpSpec(
        lambda s, v: svc.update_draft(s, actor=OP_ACTOR, version_id=v, document=other_document()),
        frozenset({"draft", "needs_fix"}),
        ("question_version.updated",),
        "draft",
    ),
    "record_check": OpSpec(
        lambda s, v: svc.record_check(
            s,
            actor=OP_ACTOR,
            version_id=v,
            result=check("lint_ok", svc.Severity.WARNING, svc.Outcome.PASSED),
        ),
        frozenset({"draft", "needs_fix", "auto_checking"}),
        ("question_version.check_recorded",),
        None,
    ),
    "submit": OpSpec(
        lambda s, v: svc.submit(s, actor=OP_ACTOR, version_id=v),
        frozenset({"draft"}),
        ("question_version.submitted", "question_version.checks_passed"),
        "in_review",
    ),
    "request_changes": OpSpec(
        lambda s, v: svc.request_changes(s, actor=OP_ACTOR, version_id=v, reason=REASON),
        frozenset({"in_review", "approved"}),
        ("question_version.changes_requested",),
        "needs_fix",
    ),
    "approve": OpSpec(
        lambda s, v: approve(s, v, OP_ACTOR),
        frozenset({"in_review"}),
        ("question_version.approved",),
        "approved",
    ),
    "reject": OpSpec(
        lambda s, v: svc.reject(s, actor=OP_ACTOR, version_id=v, reason=REASON),
        frozenset({"in_review"}),
        ("question_version.rejected",),
        "rejected",
    ),
    "publish": OpSpec(
        lambda s, v: publish(s, v, OP_ACTOR),
        frozenset({"approved"}),
        ("question_version.published",),
        "published",
    ),
    "withdraw": OpSpec(
        lambda s, v: svc.withdraw(s, actor=OP_ACTOR, version_id=v, reason=REASON),
        frozenset({"published"}),
        ("question_version.withdrawn",),
        "withdrawn",
    ),
    "republish": OpSpec(
        lambda s, v: republish(s, v, OP_ACTOR),
        frozenset({"withdrawn"}),
        ("question_version.republished",),
        "published",
    ),
}

NOT_ALLOWED = [(n, s) for n, spec in OPS.items() for s in ALL_STATUSES if s not in spec.allowed]
ALLOWED = [(n, s) for n, spec in OPS.items() for s in sorted(spec.allowed)]


@pytest.mark.parametrize(("operation", "status"), NOT_ALLOWED)
def test_an_operation_outside_its_statuses_is_an_invalid_transition_and_changes_nothing(
    session: Session, connection: Connection, env: Env, operation: str, status: str
) -> None:
    version = bring_to(session, connection, env, status)
    before = snapshot(session, connection, version.question_id)
    entries = len(audit_for(session, version.id))

    with pytest.raises(svc.InvalidTransition):
        OPS[operation].call(session, version.id)

    assert snapshot(session, connection, version.question_id) == before
    assert len(audit_for(session, version.id)) == entries
    assert svc.get_version(session, version.id).status.value == status
    usable(session)


@pytest.mark.parametrize(("operation", "status"), ALLOWED)
def test_an_operation_in_its_statuses_adds_exactly_the_documented_audit_entries(
    session: Session, connection: Connection, env: Env, operation: str, status: str
) -> None:
    version = bring_to(session, connection, env, status)
    spec = OPS[operation]
    before = len(audit_for(session, version.id))

    result = spec.call(session, version.id)

    new = new_audit(session, version.id, before)
    assert [e.action for e in new] == list(spec.actions)
    assert {e.actor for e in new} == {OP_ACTOR}
    expected = spec.result_status or status
    assert status_of(connection, version.id) == expected
    if operation == "update_draft":
        assert type(result) is svc.QuestionVersionView
    elif operation == "record_check":
        assert result is None
    else:
        assert_state_without_content(result)
    if isinstance(result, svc.QuestionVersionView | svc.VersionState):
        assert result.status.value == expected
        assert result.id == version.id


@pytest.mark.parametrize(
    ("operation", "previous", "new"),
    [
        ("approve", "in_review", "approved"),
        ("reject", "in_review", "rejected"),
        ("request_changes", "in_review", "needs_fix"),
        ("request_changes", "approved", "needs_fix"),
        ("publish", "approved", "published"),
        ("withdraw", "published", "withdrawn"),
        ("republish", "withdrawn", "published"),
    ],
)
def test_transition_entries_carry_the_hash_and_both_statuses(
    session: Session, connection: Connection, env: Env, operation: str, previous: str, new: str
) -> None:
    version = bring_to(session, connection, env, previous)
    OPS[operation].call(session, version.id)
    entry = audit_for(session, version.id)[-1]
    assert entry.data["content_sha256"] == version.content_sha256
    assert entry.data["previous_status"] == previous
    assert entry.data["status"] == new
    if operation in ("reject", "request_changes", "withdraw"):
        assert REASON in data_text(entry)


REASON_OPS: dict[str, tuple[str, Callable[[Session, uuid.UUID, str], object]]] = {
    "request_changes": (
        "in_review",
        lambda s, v, r: svc.request_changes(s, actor=OP_ACTOR, version_id=v, reason=r),
    ),
    "reject": ("in_review", lambda s, v, r: svc.reject(s, actor=OP_ACTOR, version_id=v, reason=r)),
    "withdraw": (
        "published",
        lambda s, v, r: svc.withdraw(s, actor=OP_ACTOR, version_id=v, reason=r),
    ),
    "republish": ("withdrawn", lambda s, v, r: republish(s, v, OP_ACTOR, r)),
}


@pytest.mark.parametrize("operation", list(REASON_OPS))
@pytest.mark.parametrize("reason", ["", "   ", "\n\t ", "x" * 501, "  " + "x" * 501 + "  "])
def test_a_blank_or_overlong_reason_is_a_value_error_and_changes_nothing(
    session: Session, connection: Connection, env: Env, operation: str, reason: str
) -> None:
    status, call = REASON_OPS[operation]
    version = bring_to(session, connection, env, status)
    before = snapshot(session, connection, version.question_id)
    with pytest.raises(ValueError):
        call(session, version.id, reason)
    assert snapshot(session, connection, version.question_id) == before
    usable(session)


@pytest.mark.parametrize("operation", list(REASON_OPS))
@pytest.mark.parametrize("reason", ["x", "x" * 500, "  " + "x" * 500 + "\n"])
def test_a_reason_of_one_to_five_hundred_characters_after_trimming_is_accepted(
    session: Session, connection: Connection, env: Env, operation: str, reason: str
) -> None:
    status, call = REASON_OPS[operation]
    version = bring_to(session, connection, env, status)
    call(session, version.id, reason)
    assert reason.strip() in data_text(audit_for(session, version.id)[-1])
    assert svc.MAX_REASON_LENGTH == 500


UNKNOWN_ID_CALLS: dict[str, Callable[[Session, uuid.UUID], object]] = {
    **{name: spec.call for name, spec in OPS.items()},
    "start_revision": lambda s, i: svc.start_revision(s, actor=OP_ACTOR, question_id=i),
    "get_question": svc.get_question,
    "get_version": svc.get_version,
    "list_versions": svc.list_versions,
    "get_published_version": svc.get_published_version,
    "get_checks": svc.get_checks,
}


@pytest.mark.parametrize("operation", list(UNKNOWN_ID_CALLS))
def test_unknown_ids_are_not_found(
    session: Session, connection: Connection, env: Env, operation: str
) -> None:
    create(session, env)  # something exists, so an empty database is not the reason
    before = table_counts(connection)
    with pytest.raises(svc.NotFound):
        UNKNOWN_ID_CALLS[operation](session, uuid.uuid4())
    assert table_counts(connection) == before
    usable(session)


@pytest.mark.parametrize(
    "operation", ["approve", "get_version", "get_checks", "start_revision", "get_question"]
)
def test_a_question_id_is_not_a_version_id_and_the_other_way_round(
    session: Session, env: Env, operation: str
) -> None:
    version = create(session, env)
    wrong = (
        version.question_id if operation not in ("start_revision", "get_question") else version.id
    )
    with pytest.raises(svc.NotFound):
        UNKNOWN_ID_CALLS[operation](session, wrong)


@pytest.mark.parametrize("status", WORKING_STATUSES)
def test_start_revision_with_a_working_version_is_refused(
    session: Session, connection: Connection, env: Env, status: str
) -> None:
    version = bring_to(session, connection, env, status)
    before = snapshot(session, connection, version.question_id)
    with pytest.raises(svc.WorkingVersionExists):
        svc.start_revision(session, actor=OP_ACTOR, question_id=version.question_id)
    assert snapshot(session, connection, version.question_id) == before
    usable(session)


# =============================================================================================
# 6. Checks
# =============================================================================================


def test_submit_stores_the_services_own_checks(session: Session, env: Env) -> None:
    version = create(session, env)
    assert svc.get_checks(session, version.id) == []
    svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    results = {r.code: r for r in svc.get_checks(session, version.id)}
    assert results["schema_valid"].outcome is svc.Outcome.PASSED
    assert results["vocabulary_valid"].outcome is svc.Outcome.PASSED
    assert results["math_renders"].outcome is svc.Outcome.PASSED
    assert set(svc.REQUIRED_CHECKS) <= set(results)


def test_get_checks_is_ordered_by_code(session: Session, env: Env) -> None:
    version = create(session, env)
    for code in ("zeta_check", "alpha_check", "mid_check"):
        svc.record_check(
            session,
            actor=OP_ACTOR,
            version_id=version.id,
            result=check(code, svc.Severity.WARNING, svc.Outcome.PASSED),
        )
    svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    codes = [r.code for r in svc.get_checks(session, version.id)]
    assert codes == sorted(codes)
    assert {"alpha_check", "mid_check", "zeta_check", "schema_valid"} <= set(codes)


def test_a_failed_critical_check_sends_submit_to_needs_fix(
    session: Session, connection: Connection, env: Env
) -> None:
    version = create(session, env)
    svc.record_check(
        session,
        actor=OP_ACTOR,
        version_id=version.id,
        result=check("units_ok", svc.Severity.CRITICAL, svc.Outcome.FAILED, why="bad unit"),
    )
    before = len(audit_for(session, version.id))

    result = svc.submit(session, actor=OP_ACTOR, version_id=version.id)

    assert result.status is svc.VersionStatus.NEEDS_FIX
    assert status_of(connection, version.id) == "needs_fix"
    new = new_audit(session, version.id, before)
    assert [e.action for e in new] == [
        "question_version.submitted",
        "question_version.checks_failed",
    ]
    assert "units_ok" in data_text(new[-1])
    stored = {r.code: r for r in svc.get_checks(session, version.id)}
    assert stored["units_ok"].outcome is svc.Outcome.FAILED
    assert stored["units_ok"].severity is svc.Severity.CRITICAL
    assert stored["units_ok"].detail == {"why": "bad unit"}
    assert stored["schema_valid"].outcome is svc.Outcome.PASSED


@pytest.mark.parametrize(
    ("severity", "outcome"),
    [
        (svc.Severity.WARNING, svc.Outcome.FAILED),
        (svc.Severity.WARNING, svc.Outcome.PASSED),
        (svc.Severity.WARNING, svc.Outcome.NOT_APPLICABLE),
        (svc.Severity.CRITICAL, svc.Outcome.PASSED),
        (svc.Severity.CRITICAL, svc.Outcome.NOT_APPLICABLE),
    ],
)
def test_only_a_failed_critical_check_sends_submit_to_needs_fix(
    session: Session, env: Env, severity: svc.Severity, outcome: svc.Outcome
) -> None:
    version = create(session, env)
    svc.record_check(
        session, actor=OP_ACTOR, version_id=version.id, result=check("extra", severity, outcome)
    )
    before = len(audit_for(session, version.id))
    result = svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    assert result.status is svc.VersionStatus.IN_REVIEW
    assert [e.action for e in new_audit(session, version.id, before)] == [
        "question_version.submitted",
        "question_version.checks_passed",
    ]


def test_update_draft_discards_earlier_check_results(
    session: Session, connection: Connection, env: Env
) -> None:
    version = create(session, env)
    svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=failed_critical())
    assert [r.code for r in svc.get_checks(session, version.id)] == ["ext_check"]

    svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=other_document())

    assert svc.get_checks(session, version.id) == []
    assert checks_raw(connection, version.id) == []
    result = svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    assert result.status is svc.VersionStatus.IN_REVIEW


def test_saving_the_same_content_again_keeps_a_failed_check(
    session: Session, connection: Connection, env: Env
) -> None:
    version = create(session, env)
    svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=failed_critical())

    saved = svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=document())

    assert saved.content_sha256 == version.content_sha256
    assert [r.code for r in svc.get_checks(session, version.id)] == ["ext_check"]
    assert svc.submit(session, actor=OP_ACTOR, version_id=version.id).status is (
        svc.VersionStatus.NEEDS_FIX
    )


def test_resaving_identical_content_from_needs_fix_returns_to_draft_and_fails_again(
    session: Session, connection: Connection, env: Env
) -> None:
    version = bring_to(session, connection, env, "needs_fix")
    kept = {r.code: r.outcome for r in svc.get_checks(session, version.id)}
    assert kept["ext_check"] is svc.Outcome.FAILED

    saved = svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=document())

    assert saved.status is svc.VersionStatus.DRAFT
    assert {r.code: r.outcome for r in svc.get_checks(session, version.id)} == kept
    assert svc.submit(session, actor=OP_ACTOR, version_id=version.id).status is (
        svc.VersionStatus.NEEDS_FIX
    )


def test_changed_content_discards_the_failed_check_that_identical_content_kept(
    session: Session, connection: Connection, env: Env
) -> None:
    version = create(session, env)
    svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=failed_critical())
    svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=document())
    svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=other_document())
    assert svc.get_checks(session, version.id) == []
    assert svc.submit(session, actor=OP_ACTOR, version_id=version.id).status is (
        svc.VersionStatus.IN_REVIEW
    )


def test_a_version_fixed_after_a_failed_check_can_be_submitted_again(
    session: Session, connection: Connection, env: Env
) -> None:
    version = bring_to(session, connection, env, "needs_fix")
    assert {r.code for r in svc.get_checks(session, version.id)} >= {"ext_check", "schema_valid"}

    fixed = svc.update_draft(
        session, actor=OP_ACTOR, version_id=version.id, document=other_document()
    )

    assert fixed.status is svc.VersionStatus.DRAFT
    assert svc.get_checks(session, version.id) == []
    assert svc.submit(session, actor=OP_ACTOR, version_id=version.id).status is (
        svc.VersionStatus.IN_REVIEW
    )


def test_record_check_replaces_an_earlier_result_with_the_same_code(
    session: Session, connection: Connection, env: Env
) -> None:
    version = create(session, env)
    svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=failed_critical())
    svc.record_check(
        session,
        actor=OP_ACTOR,
        version_id=version.id,
        result=check("ext_check", svc.Severity.CRITICAL, svc.Outcome.PASSED, round=2),
    )
    svc.record_check(
        session,
        actor=OP_ACTOR,
        version_id=version.id,
        result=check("other_check", svc.Severity.WARNING, svc.Outcome.FAILED),
    )
    results = svc.get_checks(session, version.id)
    assert [r.code for r in results] == ["ext_check", "other_check"]
    assert results[0].outcome is svc.Outcome.PASSED
    assert results[0].detail == {"round": 2}
    assert checks_raw(connection, version.id) == [
        ("ext_check", "critical", "passed"),
        ("other_check", "warning", "failed"),
    ]
    # the earlier failure no longer counts
    assert svc.submit(session, actor=OP_ACTOR, version_id=version.id).status is (
        svc.VersionStatus.IN_REVIEW
    )


def test_record_check_is_allowed_while_auto_checking_and_needs_fix(
    session: Session, connection: Connection, env: Env
) -> None:
    auto = bring_to(session, connection, env, "auto_checking")
    svc.record_check(session, actor=OP_ACTOR, version_id=auto.id, result=failed_critical())
    assert [r.code for r in svc.get_checks(session, auto.id)] == ["ext_check"]
    assert status_of(connection, auto.id) == "auto_checking"

    fix = bring_to(session, connection, env, "needs_fix")
    svc.record_check(
        session,
        actor=OP_ACTOR,
        version_id=fix.id,
        result=check("late_check", svc.Severity.WARNING, svc.Outcome.PASSED),
    )
    assert "late_check" in {r.code for r in svc.get_checks(session, fix.id)}
    assert status_of(connection, fix.id) == "needs_fix"


@pytest.mark.parametrize("status", ["in_review", "approved", "published", "withdrawn", "rejected"])
def test_record_check_outside_the_editable_statuses_leaves_results_alone(
    session: Session, connection: Connection, env: Env, status: str
) -> None:
    version = bring_to(session, connection, env, status)
    before = svc.get_checks(session, version.id)
    with pytest.raises(svc.InvalidTransition):
        svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=failed_critical())
    assert svc.get_checks(session, version.id) == before


def test_check_results_are_returned_as_recorded(session: Session, env: Env) -> None:
    version = create(session, env)
    recorded = check("detail_check", svc.Severity.WARNING, svc.Outcome.FAILED, a=1, b=["x", 2])
    svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=recorded)
    assert svc.get_checks(session, version.id) == [recorded]


# =============================================================================================
# 7. Publish conditions (rule 8)
# =============================================================================================


@pytest.mark.parametrize("name", list(VISUAL_SAMPLES))
def test_a_version_with_stimuli_can_be_approved_but_never_published(
    session: Session, connection: Connection, env: Env, name: str
) -> None:
    version = bring_to(session, connection, env, "approved", document(VISUAL_SAMPLES[name]()))
    assert version.has_unverified_visuals is True
    before = snapshot(session, connection, version.question_id)
    entries = len(audit_for(session, version.id))

    with pytest.raises(svc.NotPublishable) as caught:
        publish(session, version.id, OP_ACTOR)

    assert caught.value.reasons == ("unverified_visuals",)
    assert snapshot(session, connection, version.question_id) == before
    assert len(audit_for(session, version.id)) == entries
    with pytest.raises(svc.NotFound):
        svc.get_published_version(session, version.question_id)
    usable(session)


@pytest.mark.parametrize(
    ("severity", "outcome"),
    [
        (svc.Severity.WARNING, svc.Outcome.FAILED),
        (svc.Severity.CRITICAL, svc.Outcome.PASSED),
        (svc.Severity.CRITICAL, svc.Outcome.NOT_APPLICABLE),
    ],
)
def test_check_results_other_than_a_failed_critical_one_do_not_block_publishing(
    session: Session,
    connection: Connection,
    env: Env,
    severity: svc.Severity,
    outcome: svc.Outcome,
) -> None:
    version = create(session, env)
    set_status_raw(connection, version.id, "auto_checking")
    for code in REQUIRED_CHECKS:  # a missing required check is not a pass (rule 8); the service
        raw_check(connection, version.id, code, "critical", "passed")  # refuses to record these
    svc.record_check(
        session, actor=OP_ACTOR, version_id=version.id, result=check("extra", severity, outcome)
    )
    set_status_raw(connection, version.id, "in_review")
    approve(session, version.id, REVIEWER)
    assert publish(session, version.id, OP_ACTOR).status is (svc.VersionStatus.PUBLISHED)


def test_a_failed_critical_check_stops_a_version_before_review_and_fixing_it_clears_the_way(
    session: Session, connection: Connection, env: Env
) -> None:
    version = bring_to(session, connection, env, "needs_fix")
    assert svc.get_version(session, version.id).status is svc.VersionStatus.NEEDS_FIX
    svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=other_document())
    assert svc.get_checks(session, version.id) == []
    svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    approve(session, version.id, REVIEWER)
    assert publish(session, version.id, PUBLISHER).status is (svc.VersionStatus.PUBLISHED)


def check_refused(
    session: Session, connection: Connection, env: Env, result: svc.CheckResult
) -> None:
    version = create(session, env)
    before = snapshot(session, connection, version.question_id)
    entries = len(audit_for(session, version.id))
    with pytest.raises(ValueError):
        svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=result)
    assert snapshot(session, connection, version.question_id) == before
    assert len(audit_for(session, version.id)) == entries
    usable(session)


@pytest.mark.parametrize(
    "code", ["Bad", "1abc", "", "has space", "a-b", "UPPER", "_x", "ü", "z" * 65, "a\n"]
)
def test_record_check_with_a_code_that_is_not_a_lower_case_identifier_is_a_value_error(
    session: Session, connection: Connection, env: Env, code: str
) -> None:
    check_refused(session, connection, env, check(code, svc.Severity.WARNING, svc.Outcome.PASSED))


@pytest.mark.parametrize("code", ["a", "a1", "a_1", "z" * 60, "z" * 64])
def test_record_check_accepts_lower_case_identifiers_of_up_to_64_characters(
    session: Session, env: Env, code: str
) -> None:
    version = create(session, env)
    svc.record_check(
        session,
        actor=OP_ACTOR,
        version_id=version.id,
        result=check(code, svc.Severity.WARNING, svc.Outcome.PASSED),
    )
    assert [r.code for r in svc.get_checks(session, version.id)] == [code]


@pytest.mark.parametrize(
    "detail",
    [
        {"obj": object()},
        {"bytes": b"abc"},
        {"set": {1, 2}},
        {"nan": float("nan")},
        {"pad": "x" * 9000},
        {"many": ["y" * 100] * 100},
    ],
    ids=["object", "bytes", "set", "nan", "over_8k", "many_items_over_8k"],
)
def test_record_check_with_unserialisable_or_oversized_detail_is_a_value_error(
    session: Session, connection: Connection, env: Env, detail: dict[str, object]
) -> None:
    check_refused(
        session,
        connection,
        env,
        svc.CheckResult(
            code="detail_check",
            severity=svc.Severity.WARNING,
            outcome=svc.Outcome.FAILED,
            detail=detail,
        ),
    )


def test_record_check_accepts_a_detail_well_under_8_kb(session: Session, env: Env) -> None:
    version = create(session, env)
    detail = {"pad": "x" * 6000, "list": [1, 2, 3], "nested": {"a": None, "b": True}}
    recorded = svc.CheckResult(
        code="big_detail",
        severity=svc.Severity.WARNING,
        outcome=svc.Outcome.FAILED,
        detail=detail,
    )
    svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=recorded)
    assert svc.get_checks(session, version.id) == [recorded]


def test_record_check_needs_rights_like_create_question_and_stores_nothing_without_them(
    session: Session, connection: Connection, env: Env
) -> None:
    record_id = new_rights(session)
    version = create(session, env, rights_record_id=record_id)
    rights.revoke(session, record_id, at=now())
    with pytest.raises(rights.RightsDenied):
        svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=failed_critical())
    assert checks_raw(connection, version.id) == []
    assert len(audit_for(session, version.id)) == 1
    usable(session)


@pytest.mark.parametrize("name", list(PLAIN_SAMPLES))
def test_every_sample_without_stimuli_can_go_all_the_way_to_published(
    session: Session, connection: Connection, env: Env, name: str
) -> None:
    version = publish_new(session, connection, env, document(PLAIN_SAMPLES[name]()))
    assert version.has_unverified_visuals is False
    assert svc.get_published_version(session, version.question_id).document == version.document


# =============================================================================================
# 8. Versions
# =============================================================================================


def test_start_revision_copies_the_published_version_and_leaves_it_published(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = publish_new(session, connection, env, document(samples.show_that_document()))
    v2 = svc.start_revision(session, actor="u_reviser", question_id=v1.question_id)

    assert v2.question_id == v1.question_id
    assert v2.id != v1.id
    assert v2.version_no == 2
    assert v2.status is svc.VersionStatus.DRAFT
    assert v2.document == v1.document
    assert v2.content_sha256 == v1.content_sha256
    assert v2.created_by == "u_reviser"
    assert svc.get_version(session, v1.id).status is svc.VersionStatus.PUBLISHED
    assert svc.get_version(session, v1.id).content_sha256 == v1.content_sha256
    assert svc.get_published_version(session, v1.question_id).id == v1.id
    assert [v.version_no for v in svc.list_versions(session, v1.question_id)] == [1, 2]
    assert [(k, lb, m) for _, k, lb, m, _ in parts_of(connection, v2.id)] == expected_parts(
        v2.document
    )
    assert syllabus_rows_of(connection, v2.id) == expected_nodes(v2.document)

    (entry,) = audit_for(session, v2.id)
    assert (entry.action, entry.actor) == ("question_version.created", "u_reviser")
    assert entry.data["based_on"] == str(v1.id)
    assert audit_actions(session, v1.id)[-1] == "question_version.published"  # v1 untouched


def test_a_revision_is_edited_without_touching_the_published_version(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = publish_new(session, connection, env)
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    new_doc = other_document()
    svc.update_draft(session, actor=OP_ACTOR, version_id=v2.id, document=new_doc)

    assert svc.get_version(session, v2.id).document == new_doc
    assert svc.get_version(session, v1.id).document == v1.document
    learner_view = svc.get_published_version(session, v1.question_id)
    assert learner_view.id == v1.id
    assert learner_view.document == v1.document


def test_published_content_cannot_be_edited(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = publish_new(session, connection, env)
    with pytest.raises(svc.InvalidTransition):
        svc.update_draft(session, actor=OP_ACTOR, version_id=v1.id, document=other_document())
    assert svc.get_version(session, v1.id).document == v1.document
    assert version_row(connection, v1.id).content_sha256 == v1.content_sha256


def test_publishing_a_revision_withdraws_the_previous_version_in_the_same_call(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = publish_new(session, connection, env)
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    svc.update_draft(session, actor=OP_ACTOR, version_id=v2.id, document=other_document())
    svc.submit(session, actor=OP_ACTOR, version_id=v2.id)
    approve(session, v2.id, OP_ACTOR)
    v1_entries = len(audit_for(session, v1.id))

    published = publish(session, v2.id, "u_publisher")

    assert published.id == v2.id
    assert published.status is svc.VersionStatus.PUBLISHED
    assert svc.get_version(session, v1.id).status is svc.VersionStatus.WITHDRAWN
    assert svc.get_published_version(session, v1.question_id).id == v2.id
    assert svc.get_published_version(session, v1.question_id).document == other_document()
    (superseded,) = new_audit(session, v1.id, v1_entries)
    assert superseded.action == "question_version.superseded"
    assert superseded.actor == "u_publisher"
    assert superseded.data["superseded_by"] == str(v2.id)
    assert audit_actions(session, v2.id)[-1] == "question_version.published"
    published_rows = connection.execute(
        text("SELECT id FROM question_version WHERE question_id = :q AND status = 'published'"),
        {"q": v1.question_id},
    ).all()
    assert [r.id for r in published_rows] == [v2.id]


def test_a_withdrawn_version_can_be_published_again_when_nothing_newer_exists(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = bring_to(session, connection, env, "withdrawn")
    with pytest.raises(svc.NotFound):
        svc.get_published_version(session, v1.question_id)
    before = len(audit_for(session, v1.id))

    result = republish(session, v1.id, "u_publisher")

    assert result.status is svc.VersionStatus.PUBLISHED
    assert result.content_sha256 == v1.content_sha256
    assert svc.get_published_version(session, v1.question_id).id == v1.id
    (entry,) = new_audit(session, v1.id, before)
    assert (entry.action, entry.actor) == ("question_version.republished", "u_publisher")


def test_republish_is_refused_when_another_version_is_published(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = publish_new(session, connection, env)
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    svc.submit(session, actor=OP_ACTOR, version_id=v2.id)
    approve(session, v2.id, OP_ACTOR)
    publish(session, v2.id, OP_ACTOR)  # v1 is withdrawn now
    before = snapshot(session, connection, v1.question_id)

    with pytest.raises(svc.InvalidTransition):
        republish(session, v1.id, OP_ACTOR)

    assert snapshot(session, connection, v1.question_id) == before
    assert svc.get_published_version(session, v1.question_id).id == v2.id
    usable(session)


@pytest.mark.parametrize("newer", ["draft", "in_review", "approved", "rejected"])
def test_republish_is_refused_when_a_newer_version_exists(
    session: Session, connection: Connection, env: Env, newer: str
) -> None:
    v1 = bring_to(session, connection, env, "withdrawn")
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    if newer != "draft":
        svc.submit(session, actor=OP_ACTOR, version_id=v2.id)
    if newer == "approved":
        approve(session, v2.id, OP_ACTOR)
    if newer == "rejected":
        svc.reject(session, actor=OP_ACTOR, version_id=v2.id, reason=REASON)
    before = snapshot(session, connection, v1.question_id)

    with pytest.raises(svc.InvalidTransition):
        republish(session, v1.id, OP_ACTOR)

    assert snapshot(session, connection, v1.question_id) == before
    usable(session)


def test_start_revision_without_a_published_version_copies_the_latest(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = bring_to(session, connection, env, "in_review")
    svc.reject(session, actor=OP_ACTOR, version_id=v1.id, reason=REASON)
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    assert (v2.version_no, v2.status, v2.document) == (2, svc.VersionStatus.DRAFT, v1.document)

    svc.update_draft(session, actor=OP_ACTOR, version_id=v2.id, document=other_document())
    svc.submit(session, actor=OP_ACTOR, version_id=v2.id)
    svc.reject(session, actor=OP_ACTOR, version_id=v2.id, reason=REASON)
    v3 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)

    assert v3.version_no == 3
    assert v3.document == other_document()  # the latest, not the first
    assert [v.version_no for v in svc.list_versions(session, v1.question_id)] == [1, 2, 3]
    assert svc.get_version(session, v1.id).status is svc.VersionStatus.REJECTED
    assert svc.get_version(session, v2.id).status is svc.VersionStatus.REJECTED


def test_start_revision_copies_a_withdrawn_version(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = bring_to(session, connection, env, "withdrawn")
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    assert (v2.version_no, v2.document) == (2, v1.document)
    assert svc.get_version(session, v1.id).status is svc.VersionStatus.WITHDRAWN


def test_start_revision_prefers_the_published_version_over_a_later_rejected_one(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = publish_new(session, connection, env)
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    svc.update_draft(session, actor=OP_ACTOR, version_id=v2.id, document=other_document())
    svc.submit(session, actor=OP_ACTOR, version_id=v2.id)
    svc.reject(session, actor=OP_ACTOR, version_id=v2.id, reason=REASON)

    v3 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)

    assert v3.version_no == 3
    assert v3.document == v1.document != other_document()
    assert svc.get_published_version(session, v1.question_id).id == v1.id


@pytest.mark.parametrize("status", [s for s in ALL_STATUSES if s != "published"])
def test_get_published_version_never_returns_other_statuses(
    session: Session, connection: Connection, env: Env, status: str
) -> None:
    version = bring_to(session, connection, env, status)
    with pytest.raises(svc.NotFound):
        svc.get_published_version(session, version.question_id)
    assert svc.get_version(session, version.id).status.value == status  # staff still see it
    usable(session)


def test_staff_can_list_every_version_oldest_first(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = publish_new(session, connection, env)
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    listed = svc.list_versions(session, v1.question_id)
    assert [(v.id, v.version_no, v.status) for v in listed] == [
        (v1.id, 1, svc.VersionStatus.PUBLISHED),
        (v2.id, 2, svc.VersionStatus.DRAFT),
    ]


def test_a_withdrawn_version_stays_readable_for_staff_after_a_newer_one_is_published(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = publish_new(session, connection, env)
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    svc.submit(session, actor=OP_ACTOR, version_id=v2.id)
    approve(session, v2.id, OP_ACTOR)
    publish(session, v2.id, OP_ACTOR)
    old = svc.get_version(session, v1.id)
    assert old.status is svc.VersionStatus.WITHDRAWN
    assert old.document == v1.document
    assert old.content_sha256 == v1.content_sha256


def test_a_question_goes_through_several_revisions(
    session: Session, connection: Connection, env: Env
) -> None:
    question_id = publish_new(session, connection, env).question_id
    for expected_no in (2, 3, 4):
        revision = svc.start_revision(session, actor=OP_ACTOR, question_id=question_id)
        assert revision.version_no == expected_no
        svc.submit(session, actor=OP_ACTOR, version_id=revision.id)
        approve(session, revision.id, OP_ACTOR)
        publish(session, revision.id, OP_ACTOR)
    versions = svc.list_versions(session, question_id)
    assert [v.status.value for v in versions] == [
        "withdrawn",
        "withdrawn",
        "withdrawn",
        "published",
    ]
    assert svc.get_published_version(session, question_id).version_no == 4


# =============================================================================================
# 9. Audit
# =============================================================================================


def test_create_writes_one_entry_with_the_actor_and_the_hash(session: Session, env: Env) -> None:
    version = create(session, env, actor="u_creator")
    (entry,) = audit_for(session, version.id)
    assert entry.action == "question_version.created"
    assert entry.actor == "u_creator"
    assert entry.entity_type == "question_version"
    assert entry.entity_id == str(version.id)
    assert entry.data["content_sha256"] == version.content_sha256


def test_update_draft_records_the_new_and_the_previous_hash_even_when_unchanged(
    session: Session, env: Env
) -> None:
    version = create(session, env)
    svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=document())
    entry = audit_for(session, version.id)[-1]
    assert entry.action == "question_version.updated"
    assert entry.data["content_sha256"] == version.content_sha256
    assert entry.data["previous_content_sha256"] == version.content_sha256


def test_rejected_calls_write_no_audit_entries(
    session: Session, connection: Connection, env: Env
) -> None:
    version = bring_to(
        session, connection, env, "approved", document(samples.structured_document())
    )
    before = len(audit_for(session, version.id))
    total = table_counts(connection)["audit_log"]
    with pytest.raises(svc.NotPublishable):
        publish(session, version.id, OP_ACTOR)
    with pytest.raises(svc.InvalidTransition):
        approve(session, version.id, OP_ACTOR)
    with pytest.raises(ValueError):
        svc.request_changes(session, actor=OP_ACTOR, version_id=version.id, reason=" ")
    assert len(audit_for(session, version.id)) == before
    assert table_counts(connection)["audit_log"] == total


def test_no_entries_exist_for_a_question_that_failed_to_be_created(
    session: Session, connection: Connection, env: Env
) -> None:
    before = table_counts(connection)["audit_log"]
    with pytest.raises(svc.InvalidDocument):
        create(session, env, document(with_exam_section("paper_9")))
    with pytest.raises(rights.RightsDenied):
        create(session, env, rights_record_id=new_rights(session, revoked=True))
    with pytest.raises(svc.OriginClosed):
        svc.create_question(
            session,
            actor=AUTHOR,
            document=document(),
            rights_record_id=env.rights_record_id,
            syllabus_version_id=env.syllabus_version_id,
            origin=svc.Origin.GENERATED,
        )
    assert table_counts(connection)["audit_log"] == before


# =============================================================================================
# 11. Content the caller looked at (StaleContent) and what the answers contain
# =============================================================================================


def test_approving_content_that_changed_since_it_was_read_is_refused(
    session: Session, connection: Connection, env: Env
) -> None:
    version = bring_to(session, connection, env, "in_review")
    h1 = version.content_sha256
    svc.request_changes(session, actor=REVIEWER, version_id=version.id, reason=REASON)
    svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=other_document())
    svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    h2 = stored_hash(session, version.id)
    assert h1 != h2
    before = snapshot(session, connection, version.question_id)

    with pytest.raises(svc.StaleContent):
        svc.approve(session, actor=REVIEWER, version_id=version.id, expected_content_sha256=h1)

    assert snapshot(session, connection, version.question_id) == before
    assert status_of(connection, version.id) == "in_review"
    usable(session)
    approved = svc.approve(
        session, actor=REVIEWER, version_id=version.id, expected_content_sha256=h2
    )
    assert approved.status is svc.VersionStatus.APPROVED
    assert approved.content_sha256 == h2


def test_publishing_content_that_changed_since_it_was_read_is_refused(
    session: Session, connection: Connection, env: Env
) -> None:
    version = bring_to(session, connection, env, "approved")
    h1 = version.content_sha256
    svc.request_changes(session, actor=REVIEWER, version_id=version.id, reason=REASON)
    svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=other_document())
    svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    approve(session, version.id)
    before = snapshot(session, connection, version.question_id)

    with pytest.raises(svc.StaleContent):
        svc.publish(session, actor=PUBLISHER, version_id=version.id, expected_content_sha256=h1)

    assert snapshot(session, connection, version.question_id) == before
    assert status_of(connection, version.id) == "approved"
    with pytest.raises(svc.NotFound):
        svc.get_published_version(session, version.question_id)
    usable(session)
    assert publish(session, version.id).status is svc.VersionStatus.PUBLISHED


@pytest.mark.parametrize("operation", ["approve", "publish", "republish"])
@pytest.mark.parametrize("wrong", [NO_HASH, "f" * 64, "not a hash", ""])
def test_a_hash_that_is_not_the_current_one_changes_nothing(
    session: Session, connection: Connection, env: Env, operation: str, wrong: str
) -> None:
    status = {"approve": "in_review", "publish": "approved", "republish": "withdrawn"}[operation]
    version = bring_to(session, connection, env, status)
    before = snapshot(session, connection, version.question_id)
    entries = len(audit_for(session, version.id))
    with pytest.raises(svc.StaleContent):
        if operation == "approve":
            svc.approve(
                session, actor=OP_ACTOR, version_id=version.id, expected_content_sha256=wrong
            )
        elif operation == "publish":
            svc.publish(
                session, actor=OP_ACTOR, version_id=version.id, expected_content_sha256=wrong
            )
        else:
            svc.republish(
                session,
                actor=OP_ACTOR,
                version_id=version.id,
                expected_content_sha256=wrong,
                reason=REASON,
            )
    assert snapshot(session, connection, version.question_id) == before
    assert len(audit_for(session, version.id)) == entries
    usable(session)


def test_the_status_is_checked_before_the_hash_on_publish(
    session: Session, connection: Connection, env: Env
) -> None:
    version = bring_to(session, connection, env, "in_review")
    with pytest.raises(svc.InvalidTransition):
        svc.publish(session, actor=OP_ACTOR, version_id=version.id, expected_content_sha256=NO_HASH)


def test_writing_calls_return_the_full_view_only_where_they_create_or_edit_content(
    session: Session, connection: Connection, env: Env
) -> None:
    created = create(session, env)
    assert type(created) is svc.QuestionVersionView
    updated = svc.update_draft(
        session, actor=OP_ACTOR, version_id=created.id, document=other_document()
    )
    assert type(updated) is svc.QuestionVersionView
    published = publish_new(session, connection, env)
    revision = svc.start_revision(session, actor=OP_ACTOR, question_id=published.question_id)
    assert type(revision) is svc.QuestionVersionView
    assert revision.document == published.document


@pytest.mark.parametrize("operation", ["submit", "request_changes", "approve", "reject"])
def test_review_calls_return_a_state_without_content(
    session: Session, connection: Connection, env: Env, operation: str
) -> None:
    status = "draft" if operation == "submit" else "in_review"
    version = bring_to(session, connection, env, status)
    result = OPS[operation].call(session, version.id)
    assert_state_without_content(result)
    assert isinstance(result, svc.VersionState)
    assert (result.id, result.question_id, result.version_no) == (
        version.id,
        version.question_id,
        1,
    )
    assert result.content_sha256 == version.content_sha256


@pytest.mark.parametrize("operation", ["publish", "withdraw", "republish"])
def test_publication_calls_return_a_state_without_content(
    session: Session, connection: Connection, env: Env, operation: str
) -> None:
    status = {"publish": "approved", "withdraw": "published", "republish": "withdrawn"}[operation]
    version = bring_to(session, connection, env, status)
    result = OPS[operation].call(session, version.id)
    assert_state_without_content(result)
    assert isinstance(result, svc.VersionState)
    assert result.content_sha256 == version.content_sha256


# =============================================================================================
# 12. Every writing function is atomic
# =============================================================================================

BAD_ACTORS = ["someone@example.org", "bad actor", ""]


def call_with(
    session: Session, operation: str, version: svc.QuestionVersionView, actor: str
) -> object:
    """Call `operation` against `version` as `actor` (the state it needs is set up by the test)."""
    vid = version.id
    if operation == "update_draft":
        return svc.update_draft(session, actor=actor, version_id=vid, document=other_document())
    if operation == "record_check":
        extra = check("atomic_extra", svc.Severity.WARNING, svc.Outcome.PASSED, round=1)
        return svc.record_check(session, actor=actor, version_id=vid, result=extra)
    if operation == "submit":
        return svc.submit(session, actor=actor, version_id=vid)
    if operation == "request_changes":
        return svc.request_changes(session, actor=actor, version_id=vid, reason=REASON)
    if operation == "approve":
        return approve(session, vid, actor)
    if operation == "reject":
        return svc.reject(session, actor=actor, version_id=vid, reason=REASON)
    if operation == "publish":
        return publish(session, vid, actor)
    if operation == "withdraw":
        return svc.withdraw(session, actor=actor, version_id=vid, reason=REASON)
    if operation == "republish":
        return republish(session, vid, actor)
    if operation == "start_revision":
        return svc.start_revision(session, actor=actor, question_id=version.question_id)
    raise AssertionError(operation)


ATOMIC_CASES = [
    ("update_draft", "draft"),
    ("update_draft", "needs_fix"),
    ("record_check", "draft"),
    ("record_check", "needs_fix"),
    ("submit", "draft"),
    ("request_changes", "in_review"),
    ("request_changes", "approved"),
    ("approve", "in_review"),
    ("reject", "in_review"),
    ("publish", "approved"),
    ("withdraw", "published"),
    ("republish", "withdrawn"),
    ("start_revision", "published"),
    ("start_revision", "withdrawn"),
    ("start_revision", "rejected"),
]


@pytest.mark.parametrize("actor", BAD_ACTORS)
@pytest.mark.parametrize(("operation", "status"), ATOMIC_CASES)
def test_a_call_the_audit_log_refuses_leaves_nothing_behind(
    session: Session, connection: Connection, env: Env, operation: str, status: str, actor: str
) -> None:
    version = bring_to(session, connection, env, status)
    before = snapshot(session, connection, version.question_id)
    entries = [(e.action, e.actor) for e in audit_for(session, version.id)]

    with pytest.raises(ValueError):
        call_with(session, operation, version, actor)

    assert snapshot(session, connection, version.question_id) == before
    assert [(e.action, e.actor) for e in audit_for(session, version.id)] == entries
    assert status_of(connection, version.id) == status
    usable(session)
    call_with(session, operation, version, OP_ACTOR)  # the same call, properly attributed
    assert snapshot(session, connection, version.question_id) != before


@pytest.mark.parametrize("actor", BAD_ACTORS)
def test_a_refused_submit_does_not_leave_the_version_in_auto_checking(
    session: Session, connection: Connection, env: Env, actor: str
) -> None:
    version = create(session, env)
    with pytest.raises(ValueError):
        svc.submit(session, actor=actor, version_id=version.id)
    assert status_of(connection, version.id) == "draft"
    assert checks_raw(connection, version.id) == []
    assert audit_actions(session, version.id) == ["question_version.created"]
    assert svc.submit(session, actor=OP_ACTOR, version_id=version.id).status is (
        svc.VersionStatus.IN_REVIEW
    )


@pytest.mark.parametrize("actor", BAD_ACTORS)
def test_a_refused_publish_keeps_the_previous_version_published(
    session: Session, connection: Connection, env: Env, actor: str
) -> None:
    v1 = publish_new(session, connection, env)
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    svc.update_draft(session, actor=OP_ACTOR, version_id=v2.id, document=other_document())
    svc.submit(session, actor=OP_ACTOR, version_id=v2.id)
    approve(session, v2.id)
    before = snapshot(session, connection, v1.question_id)

    with pytest.raises(ValueError):
        publish(session, v2.id, actor)

    assert snapshot(session, connection, v1.question_id) == before
    assert status_of(connection, v1.id) == "published"
    assert status_of(connection, v2.id) == "approved"
    assert svc.get_published_version(session, v1.question_id).id == v1.id
    publish(session, v2.id)
    assert status_of(connection, v1.id) == "withdrawn"
    assert status_of(connection, v2.id) == "published"


@pytest.mark.parametrize("actor", BAD_ACTORS)
def test_a_refused_create_writes_no_question_version_or_derived_row(
    session: Session, connection: Connection, env: Env, actor: str
) -> None:
    before = table_counts(connection)
    with pytest.raises(ValueError):
        create(session, env, document(samples.show_that_document()), actor=actor)
    assert table_counts(connection) == before
    usable(session)
    create(session, env, document(samples.show_that_document()), actor=OP_ACTOR)
    assert table_counts(connection)["question"] == before["question"] + 1


# =============================================================================================
# 13. Source of a revision, size limits, questions without versions
# =============================================================================================


def test_start_revision_skips_a_rejected_latest_version_when_an_earlier_one_was_not_rejected(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = bring_to(session, connection, env, "withdrawn")
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    svc.update_draft(session, actor=OP_ACTOR, version_id=v2.id, document=other_document())
    svc.submit(session, actor=OP_ACTOR, version_id=v2.id)
    svc.reject(session, actor=OP_ACTOR, version_id=v2.id, reason=REASON)

    v3 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)

    assert v3.version_no == 3
    assert v3.document == v1.document != other_document()
    (entry,) = audit_for(session, v3.id)
    assert entry.data["based_on"] == str(v1.id)


def test_start_revision_with_only_rejected_versions_copies_the_latest(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = bring_to(session, connection, env, "rejected")
    v2 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    svc.update_draft(session, actor=OP_ACTOR, version_id=v2.id, document=other_document())
    svc.submit(session, actor=OP_ACTOR, version_id=v2.id)
    svc.reject(session, actor=OP_ACTOR, version_id=v2.id, reason=REASON)
    v3 = svc.start_revision(session, actor=OP_ACTOR, question_id=v1.question_id)
    assert (v3.version_no, v3.document) == (3, other_document())
    assert audit_for(session, v3.id)[0].data["based_on"] == str(v2.id)


def test_start_revision_of_a_question_without_versions_is_not_found(
    session: Session, connection: Connection, env: Env
) -> None:
    question_id = raw_question(connection, env)
    before = table_counts(connection)
    with pytest.raises(svc.NotFound):
        svc.start_revision(session, actor=OP_ACTOR, question_id=question_id)
    assert table_counts(connection) == before
    usable(session)


def oversized_document() -> QuestionDocument:
    d = samples.data_based_document()
    d["stem"] = samples.line(samples.text("x" * 600_000))
    return document(d)


def nul_document() -> QuestionDocument:
    d = samples.data_based_document()
    d["stem"] = samples.line(samples.text("before\u0000after"))
    return document(d)


BAD_SIZED = {"over_512_kb": oversized_document, "nul_character": nul_document}


@pytest.mark.parametrize("case", list(BAD_SIZED))
def test_create_refuses_documents_over_512_kb_or_with_a_nul_character(
    session: Session, connection: Connection, env: Env, case: str
) -> None:
    doc = BAD_SIZED[case]()
    before = table_counts(connection)
    with pytest.raises(svc.InvalidDocument):
        create(session, env, doc)
    assert table_counts(connection) == before
    usable(session)


@pytest.mark.parametrize("case", list(BAD_SIZED))
def test_update_draft_refuses_such_documents_and_changes_nothing(
    session: Session, connection: Connection, env: Env, case: str
) -> None:
    version = create(session, env)
    svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=failed_critical())
    before = snapshot(session, connection, version.question_id)
    entries = len(audit_for(session, version.id))
    with pytest.raises(svc.InvalidDocument):
        svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=BAD_SIZED[case]())
    assert snapshot(session, connection, version.question_id) == before
    assert len(audit_for(session, version.id)) == entries
    usable(session)


def test_a_large_document_under_the_limit_is_accepted(session: Session, env: Env) -> None:
    d = samples.data_based_document()
    d["stem"] = samples.line(samples.text("x" * 100_000))
    view = create(session, env, document(d))
    assert svc.get_version(session, view.id).document == document(d)


# =============================================================================================
# 10. Properties (rule 8 holds whatever sequence of calls is made)
# =============================================================================================

STEPS = (
    "update_plain",
    "update_visual",
    "record_failed_critical",
    "record_failed_warning",
    "record_passed_critical",
    "record_required_passed",
    "raw_to_auto_checking",
    "raw_to_in_review",
    "submit",
    "approve",
    "request_changes",
    "reject",
    "publish",
    "withdraw",
    "republish",
    "start_revision",
)


def apply_step(session: Session, connection: Connection, question_id: uuid.UUID, step: str) -> None:
    versions = svc.list_versions(session, question_id)
    target = versions[-1]
    if step == "republish":
        withdrawn = [v for v in versions if v.status is svc.VersionStatus.WITHDRAWN]
        target = withdrawn[-1] if withdrawn else target
    vid = target.id
    actor = OP_ACTOR
    if step == "update_plain":
        svc.update_draft(session, actor=actor, version_id=vid, document=document())
    elif step == "update_visual":
        svc.update_draft(
            session, actor=actor, version_id=vid, document=document(samples.structured_document())
        )
    elif step == "record_failed_critical":
        svc.record_check(session, actor=actor, version_id=vid, result=failed_critical())
    elif step == "record_failed_warning":
        svc.record_check(
            session,
            actor=actor,
            version_id=vid,
            result=check("soft", svc.Severity.WARNING, svc.Outcome.FAILED),
        )
    elif step == "record_passed_critical":
        svc.record_check(
            session,
            actor=actor,
            version_id=vid,
            result=check("ext_check", svc.Severity.CRITICAL, svc.Outcome.PASSED),
        )
    elif step == "record_required_passed":
        # the service refuses these codes, so a raw writer stands in for the trusted checker
        if target.status in (
            svc.VersionStatus.DRAFT,
            svc.VersionStatus.AUTO_CHECKING,
            svc.VersionStatus.NEEDS_FIX,
        ):
            for code in REQUIRED_CHECKS:
                with contextlib.suppress(DBAPIError), connection.begin_nested():
                    raw_check(connection, vid, code, "critical", "passed")
    elif step == "raw_to_auto_checking":
        if target.status is svc.VersionStatus.DRAFT:
            set_status_raw(connection, vid, "auto_checking")
    elif step == "raw_to_in_review":
        if target.status is svc.VersionStatus.AUTO_CHECKING:
            # refused by the database while a failed critical check exists
            with contextlib.suppress(DBAPIError), connection.begin_nested():
                set_status_raw(connection, vid, "in_review")
    elif step == "submit":
        svc.submit(session, actor=actor, version_id=vid)
    elif step == "approve":
        approve(session, vid, actor)
    elif step == "request_changes":
        svc.request_changes(session, actor=actor, version_id=vid, reason=REASON)
    elif step == "reject":
        svc.reject(session, actor=actor, version_id=vid, reason=REASON)
    elif step == "publish":
        publish(session, vid, actor)
    elif step == "withdraw":
        svc.withdraw(session, actor=actor, version_id=vid, reason=REASON)
    elif step == "republish":
        republish(session, vid, actor)
    else:
        svc.start_revision(session, actor=actor, question_id=question_id)


def assert_invariants(connection: Connection, question_id: uuid.UUID) -> None:
    rows = connection.execute(
        text(
            "SELECT id, status, has_unverified_visuals, "
            "jsonb_array_length(document -> 'stimuli') AS stimuli "
            "FROM question_version WHERE question_id = :q"
        ),
        {"q": question_id},
    ).all()
    published = [r for r in rows if r.status == "published"]
    for row in rows:
        if row.status in ("in_review", "approved", "published", "withdrawn"):
            blocked = connection.execute(
                text(
                    "SELECT count(*) FROM question_version_check WHERE question_version_id = :v "
                    "AND severity = 'critical' AND outcome = 'failed'"
                ),
                {"v": row.id},
            ).scalar_one()
            assert blocked == 0
            passed = connection.execute(
                text(
                    "SELECT count(*) FROM question_version_check WHERE question_version_id = :v "
                    "AND check_code IN ('schema_valid', 'vocabulary_valid', 'math_renders') "
                    "AND severity = 'critical' AND outcome = 'passed'"
                ),
                {"v": row.id},
            ).scalar_one()
            assert passed == len(REQUIRED_CHECKS)  # a missing required check is not a pass
    assert len(published) <= 1
    assert len([r for r in rows if r.status in WORKING_STATUSES]) <= 1
    for row in published:
        assert row.has_unverified_visuals is False
        assert row.stimuli == 0
        failed = connection.execute(
            text(
                "SELECT count(*) FROM question_version_check WHERE question_version_id = :v "
                "AND severity = 'critical' AND outcome = 'failed'"
            ),
            {"v": row.id},
        ).scalar_one()
        assert failed == 0


@pytest.mark.parametrize("start", ["plain", "visual"])
@settings(
    max_examples=40,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(steps=st.lists(st.sampled_from(STEPS), max_size=16))
def test_no_sequence_of_calls_publishes_unverified_visuals_or_a_failed_critical_check(
    session: Session, connection: Connection, env: Env, start: str, steps: list[str]
) -> None:
    doc = document(samples.structured_document() if start == "visual" else None)
    question_id = create(session, env, doc).question_id
    for step in steps:
        with contextlib.suppress(svc.ContentError, rights.RightsDenied, ValueError):
            apply_step(session, connection, question_id, step)
        assert_invariants(connection, question_id)
        usable(session)


@settings(max_examples=25, deadline=None)
@given(st.sampled_from(sorted(ALL_SAMPLES)))
def test_hash_of_a_document_survives_a_json_round_trip(name: str) -> None:
    doc = document(ALL_SAMPLES[name]())
    again = QuestionDocument.model_validate(json.loads(doc.model_dump_json()))
    assert svc.content_sha256(again) == svc.content_sha256(doc)


# =============================================================================================
# 14. Math is checked when content is saved (CLAUDE.md rule 6)
# =============================================================================================

node = pytest.mark.node


def unique_formula() -> str:
    """A formula that no other test renders, so it has to reach the renderer."""
    return "w" + "".join(chr(ord("a") + int(c, 16)) for c in uuid.uuid4().hex)


def math_document(*latex: str, block: bool = False) -> QuestionDocument:
    d = samples.data_based_document()
    d["stem"] = samples.doc(
        *[samples.math_block(x) if block else samples.paragraph(samples.math(x)) for x in latex],
        samples.paragraph(samples.text("A ball is timed.")),
    )
    return document(d)


def no_renderer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QLAB_NODE_BIN", "no-such-node-binary-" + uuid.uuid4().hex)


def renderer_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("QLAB_NODE_BIN")


BAD_MATH = {
    "refused_command": lambda: rf"{unique_formula()} \href{{http://example.org}}{{x}}",
    "refused_definition": lambda: rf"\def\{unique_formula()}{{1}}",
    "does_not_render": lambda: f"{unique_formula()}^",
    "unbalanced_braces": lambda: f"{{{unique_formula()}",
}


@node
@pytest.mark.parametrize("case", list(BAD_MATH))
@pytest.mark.parametrize("block", [False, True], ids=["inline", "block"])
def test_create_refuses_math_that_is_not_allowed_or_does_not_render(
    session: Session, connection: Connection, env: Env, case: str, block: bool
) -> None:
    latex = BAD_MATH[case]()
    before = table_counts(connection)
    with pytest.raises(svc.InvalidDocument) as caught:
        create(session, env, math_document(latex, block=block))
    assert any(latex[:50] in error for error in caught.value.errors), caught.value.errors
    assert table_counts(connection) == before
    usable(session)


@node
@pytest.mark.parametrize("case", list(BAD_MATH))
def test_update_draft_refuses_such_math_and_changes_nothing(
    session: Session, connection: Connection, env: Env, case: str
) -> None:
    version = create(session, env)
    svc.record_check(session, actor=OP_ACTOR, version_id=version.id, result=failed_critical())
    latex = BAD_MATH[case]()
    before = snapshot(session, connection, version.question_id)
    entries = len(audit_for(session, version.id))

    with pytest.raises(svc.InvalidDocument) as caught:
        svc.update_draft(
            session, actor=OP_ACTOR, version_id=version.id, document=math_document(latex)
        )

    assert any(latex[:50] in error for error in caught.value.errors), caught.value.errors
    assert snapshot(session, connection, version.question_id) == before
    assert len(audit_for(session, version.id)) == entries
    assert svc.get_version(session, version.id).content_sha256 == version.content_sha256
    usable(session)


@node
def test_every_bad_node_is_named_and_good_ones_are_not(session: Session, env: Env) -> None:
    bad_one, bad_two, good = (
        f"{unique_formula()}^",
        rf"\input{{{unique_formula()}}}",
        unique_formula(),
    )
    with pytest.raises(svc.InvalidDocument) as caught:
        create(session, env, math_document(bad_one, good, bad_two))
    errors = " | ".join(caught.value.errors)
    assert bad_one in errors and bad_two in errors
    assert f"`{good}`" not in errors


@node
def test_math_that_is_fine_is_saved_and_returned_unchanged(session: Session, env: Env) -> None:
    doc = math_document(unique_formula(), rf"\frac{{{unique_formula()}}}{{2}}", block=False)
    view = create(session, env, doc)
    assert svc.get_version(session, view.id).document == doc


@node
def test_math_and_vocabulary_problems_together_are_reported_as_observed(
    session: Session, connection: Connection, env: Env
) -> None:
    d = samples.data_based_document()
    d["exam_section"] = "paper_9"
    bad = f"{unique_formula()}^"
    d["stem"] = samples.doc(samples.paragraph(samples.math(bad)))
    before = table_counts(connection)
    with pytest.raises(svc.InvalidDocument) as caught:
        create(session, env, document(d))
    assert mentions(caught.value.errors, "paper_9")  # the vocabulary problem is always reported
    # Whether the math problem is listed as well is not promised by the contract.
    assert table_counts(connection) == before


@node
@pytest.mark.parametrize("operation", ["create_question", "update_draft"])
def test_content_whose_math_cannot_be_checked_is_not_saved(
    session: Session,
    connection: Connection,
    env: Env,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    doc = math_document(unique_formula())
    if operation == "create_question":
        before = table_counts(connection)
        no_renderer(monkeypatch)
        with pytest.raises(RendererUnavailable):
            create(session, env, doc)
        assert table_counts(connection) == before
        usable(session)
        renderer_back(monkeypatch)
        assert create(session, env, doc).document == doc
        return
    version = create(session, env)
    before = snapshot(session, connection, version.question_id)
    entries = len(audit_for(session, version.id))
    no_renderer(monkeypatch)
    with pytest.raises(RendererUnavailable):
        svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=doc)
    assert snapshot(session, connection, version.question_id) == before
    assert len(audit_for(session, version.id)) == entries
    assert status_of(connection, version.id) == "draft"
    usable(session)
    renderer_back(monkeypatch)
    assert (
        svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=doc).document
        == doc
    )


@node
def test_a_revision_is_opened_even_when_the_renderer_cannot_run(
    session: Session, connection: Connection, env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    doc = math_document(unique_formula())
    raw = raw_full_version(connection, env, doc)
    raw_walk(connection, raw.version_id, "published")
    no_renderer(monkeypatch)

    revision = svc.start_revision(session, actor=OP_ACTOR, question_id=raw.question_id)

    assert revision.version_no == 2
    assert revision.status is svc.VersionStatus.DRAFT
    assert revision.document == doc  # copied as it is: the copy is not checked
    assert audit_for(session, revision.id)[0].data["based_on"] == str(raw.version_id)
    assert status_of(connection, raw.version_id) == "published"
    usable(session)
    with pytest.raises(RendererUnavailable):  # the check happens when the content is saved
        svc.update_draft(
            session,
            actor=OP_ACTOR,
            version_id=revision.id,
            document=math_document(unique_formula()),
        )
    with pytest.raises(RendererUnavailable):
        svc.submit(session, actor=OP_ACTOR, version_id=revision.id)
    assert status_of(connection, revision.id) == "draft"


def stale_math_document() -> QuestionDocument:
    """Math that today's rules refuse but that an older version could have stored."""
    return math_document(rf"\href{{http://example.org}}{{{unique_formula()}}}")


def published_with_stale_math(
    connection: Connection, env: Env
) -> tuple[uuid.UUID, uuid.UUID, QuestionDocument]:
    doc = stale_math_document()
    raw = raw_full_version(connection, env, doc)
    raw_walk(connection, raw.version_id, "published")
    return raw.question_id, raw.version_id, doc


@node
def test_a_revision_of_a_version_with_math_the_rules_now_refuse_is_still_opened(
    session: Session, connection: Connection, env: Env
) -> None:
    question_id, source_id, doc = published_with_stale_math(connection, env)

    revision = svc.start_revision(session, actor=OP_ACTOR, question_id=question_id)

    assert revision.status is svc.VersionStatus.DRAFT
    assert revision.document == doc
    assert revision.version_no == 2
    assert svc.get_published_version(session, question_id).id == source_id
    usable(session)


@node
def test_submit_sends_such_a_revision_to_needs_fix_and_it_is_corrected_by_saving(
    session: Session, connection: Connection, env: Env
) -> None:
    question_id, _, doc = published_with_stale_math(connection, env)
    revision = svc.start_revision(session, actor=OP_ACTOR, question_id=question_id)

    result = svc.submit(session, actor=OP_ACTOR, version_id=revision.id)

    assert result.status is svc.VersionStatus.NEEDS_FIX
    failed = audit_for(session, revision.id)[-1]
    assert failed.action == "question_version.checks_failed"
    assert "math_renders" in data_text(failed)
    stored = {r.code: r for r in svc.get_checks(session, revision.id)}
    assert stored["math_renders"].outcome is svc.Outcome.FAILED

    before = snapshot(session, connection, question_id)
    with pytest.raises(svc.InvalidDocument) as caught:
        svc.update_draft(session, actor=OP_ACTOR, version_id=revision.id, document=doc)
    assert any("href" in error for error in caught.value.errors)
    assert snapshot(session, connection, question_id) == before
    usable(session)

    corrected = math_document(unique_formula())
    saved = svc.update_draft(session, actor=OP_ACTOR, version_id=revision.id, document=corrected)
    assert saved.status is svc.VersionStatus.DRAFT
    assert svc.submit(session, actor=OP_ACTOR, version_id=revision.id).status is (
        svc.VersionStatus.IN_REVIEW
    )
    approve(session, revision.id)
    assert publish(session, revision.id).status is svc.VersionStatus.PUBLISHED


@node
def test_a_command_dropped_from_the_list_after_publishing_does_not_block_a_revision(
    session: Session,
    connection: Connection,
    env: Env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    doc = math_document(r"\sin x" + " " + unique_formula())
    published = publish_new(session, connection, env, doc)
    monkeypatch.setattr(
        qmath, "ALLOWED_COMMANDS", {k: v for k, v in qmath.ALLOWED_COMMANDS.items() if k != "sin"}
    )

    revision = svc.start_revision(session, actor=OP_ACTOR, question_id=published.question_id)

    assert revision.document == doc
    assert svc.submit(session, actor=OP_ACTOR, version_id=revision.id).status is (
        svc.VersionStatus.NEEDS_FIX
    )
    with pytest.raises(svc.InvalidDocument):
        create(session, env, doc)
    assert svc.get_published_version(session, published.question_id).id == published.id


@node
def test_submit_without_a_renderer_is_not_stuck_in_auto_checking(
    session: Session, connection: Connection, env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    doc = math_document(unique_formula())
    raw = raw_full_version(connection, env, doc, required=())  # a draft nobody has checked
    connection.execute(
        text("DELETE FROM question_version_check WHERE question_version_id = :v"),
        {"v": raw.version_id},
    )
    before = snapshot(session, connection, raw.question_id)
    no_renderer(monkeypatch)

    with pytest.raises(RendererUnavailable):
        svc.submit(session, actor=OP_ACTOR, version_id=raw.version_id)

    assert snapshot(session, connection, raw.question_id) == before
    assert status_of(connection, raw.version_id) == "draft"
    assert checks_raw(connection, raw.version_id) == []
    assert audit_for(session, raw.version_id) == []
    usable(session)
    renderer_back(monkeypatch)
    assert svc.submit(session, actor=OP_ACTOR, version_id=raw.version_id).status is (
        svc.VersionStatus.IN_REVIEW
    )


@node
def test_submit_stores_math_renders_as_passed_with_the_katex_version(
    session: Session, env: Env
) -> None:
    version = create(session, env, math_document(unique_formula()))
    svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    results = {r.code: r for r in svc.get_checks(session, version.id)}
    result = results["math_renders"]
    assert result.outcome is svc.Outcome.PASSED
    assert result.severity is svc.Severity.CRITICAL
    assert KATEX_VERSION in json.dumps(result.detail)


@node
def test_a_stored_document_with_math_that_does_not_render_sends_submit_to_needs_fix(
    session: Session, connection: Connection, env: Env
) -> None:
    marker = unique_formula()
    version = create(session, env, math_document(marker))
    # Only raw SQL on a draft can put such a document in: the service refuses it at save time.
    bad = f"{marker}^"
    connection.execute(
        text(
            "UPDATE question_version SET document = replace(document::text, "
            "CAST(:old AS text), CAST(:new AS text))::jsonb WHERE id = :v"
        ),
        {"old": f'"latex": "{marker}"', "new": f'"latex": "{bad}"', "v": version.id},
    )
    assert bad in json.dumps(
        connection.execute(
            text("SELECT document FROM question_version WHERE id = :v"), {"v": version.id}
        ).scalar_one()
    )

    result = svc.submit(session, actor=OP_ACTOR, version_id=version.id)

    assert result.status is svc.VersionStatus.NEEDS_FIX
    failed = audit_for(session, version.id)[-1]
    assert failed.action == "question_version.checks_failed"
    assert "math_renders" in data_text(failed)
    stored = {r.code: r for r in svc.get_checks(session, version.id)}
    math_result = stored["math_renders"]
    assert math_result.outcome is svc.Outcome.FAILED
    assert math_result.severity is svc.Severity.CRITICAL
    detail = json.dumps(math_result.detail)
    assert marker not in detail  # a count, not the formula text (which is the author's data)
    assert any(isinstance(v, int) and not isinstance(v, bool) for v in math_result.detail.values())
    assert status_of(connection, version.id) == "needs_fix"


@node
def test_a_version_cannot_leave_needs_fix_for_review_without_passing_the_math_check(
    session: Session, connection: Connection, env: Env
) -> None:
    marker = unique_formula()
    version = create(session, env, math_document(marker))
    connection.execute(
        text(
            "UPDATE question_version SET document = replace(document::text, "
            "CAST(:old AS text), CAST(:new AS text))::jsonb WHERE id = :v"
        ),
        {"old": f'"latex": "{marker}"', "new": f'"latex": "{marker}^"', "v": version.id},
    )
    svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=math_document(marker))
    assert svc.submit(session, actor=OP_ACTOR, version_id=version.id).status is (
        svc.VersionStatus.IN_REVIEW
    )


@pytest.mark.parametrize("code", list(svc.REQUIRED_CHECKS))
@pytest.mark.parametrize(
    ("severity", "outcome"),
    [
        (svc.Severity.CRITICAL, svc.Outcome.PASSED),
        (svc.Severity.CRITICAL, svc.Outcome.FAILED),
        (svc.Severity.WARNING, svc.Outcome.PASSED),
        (svc.Severity.CRITICAL, svc.Outcome.NOT_APPLICABLE),
    ],
)
def test_record_check_refuses_the_services_own_required_codes(
    session: Session,
    connection: Connection,
    env: Env,
    code: str,
    severity: svc.Severity,
    outcome: svc.Outcome,
) -> None:
    version = create(session, env)
    before = snapshot(session, connection, version.question_id)
    entries = len(audit_for(session, version.id))
    with pytest.raises(ValueError):
        svc.record_check(
            session,
            actor=OP_ACTOR,
            version_id=version.id,
            result=check(code, severity, outcome),
        )
    assert snapshot(session, connection, version.question_id) == before
    assert len(audit_for(session, version.id)) == entries
    assert checks_raw(connection, version.id) == []
    usable(session)


def test_a_caller_cannot_pass_review_by_recording_math_renders_itself(
    session: Session, connection: Connection, env: Env
) -> None:
    version = create(session, env)
    with pytest.raises(ValueError):
        svc.record_check(
            session,
            actor=OP_ACTOR,
            version_id=version.id,
            result=check("math_renders", svc.Severity.CRITICAL, svc.Outcome.PASSED),
        )
    set_status_raw(connection, version.id, "auto_checking")
    with pytest.raises(DBAPIError), connection.begin_nested():
        set_status_raw(connection, version.id, "in_review")
    assert status_of(connection, version.id) == "auto_checking"


def test_required_codes_are_refused_in_every_editable_status(
    session: Session, connection: Connection, env: Env
) -> None:
    for status in ("draft", "needs_fix", "auto_checking"):
        version = bring_to(session, connection, env, status)
        before = snapshot(session, connection, version.question_id)
        with pytest.raises(ValueError):
            svc.record_check(
                session,
                actor=OP_ACTOR,
                version_id=version.id,
                result=check("math_renders", svc.Severity.CRITICAL, svc.Outcome.PASSED),
            )
        assert snapshot(session, connection, version.question_id) == before


@node
def test_the_math_renders_detail_counts_the_math_nodes(session: Session, env: Env) -> None:
    doc = math_document(unique_formula(), unique_formula(), unique_formula())
    version = create(session, env, doc)
    svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    detail = {r.code: r for r in svc.get_checks(session, version.id)}["math_renders"].detail
    # every formula of this document is distinct, so "the number of math nodes" is unambiguous
    assert detail["nodes"] == len(list(math_nodes(doc))) >= 3
    assert KATEX_VERSION in json.dumps(detail)


def test_a_document_without_math_has_zero_nodes_in_the_detail(session: Session, env: Env) -> None:
    version = create(session, env, document(samples.plain_mcq_document()))
    svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    result = {r.code: r for r in svc.get_checks(session, version.id)}["math_renders"]
    assert result.outcome is svc.Outcome.PASSED
    assert result.detail["nodes"] == 0


@node
def test_the_failed_math_check_detail_also_holds_the_node_count(
    session: Session, connection: Connection, env: Env
) -> None:
    marker = unique_formula()
    version = create(session, env, math_document(marker, unique_formula()))
    connection.execute(
        text(
            "UPDATE question_version SET document = replace(document::text, "
            "CAST(:old AS text), CAST(:new AS text))::jsonb WHERE id = :v"
        ),
        {"old": f'"latex": "{marker}"', "new": f'"latex": "{marker}^"', "v": version.id},
    )
    svc.submit(session, actor=OP_ACTOR, version_id=version.id)
    detail = {r.code: r for r in svc.get_checks(session, version.id)}["math_renders"].detail
    assert isinstance(detail["nodes"], int) and detail["nodes"] >= 1
    assert marker not in json.dumps(detail)
