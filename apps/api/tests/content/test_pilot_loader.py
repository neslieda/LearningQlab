"""Import of converted pilot files: `qlab.content.pilot.loader` and the `load` command.

Written from docs/pilot/IMPORT_RULES.md sections 2 and 7, the module docstring, constants,
`LoadReport` and function docstrings of `qlab.content.pilot.loader`, and the docstrings of
`qlab.content.service` and `qlab.rights.service`. No function body was read.

Test data is synthetic: the documents are the content tests' own samples wrapped as pilot
questions under a made-up file stem. The one integration test at the end loads the committed
files and asserts on counts and keys only, never on question wording.

Saving a document runs the math check, so every test here needs Node.
"""

from __future__ import annotations

import json
import re
import uuid
from collections.abc import Callable, Iterable, Iterator, Sequence
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from pydantic import ValidationError
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.orm import Session

from qlab.audit import service as audit
from qlab.content import service as svc
from qlab.content.math import RendererUnavailable
from qlab.content.pilot import __main__ as cli
from qlab.content.pilot.loader import (
    ACTOR,
    OWN_CONTENT_LICENSE_REF,
    PILOT_SYLLABUS,
    LoadReport,
    ensure_own_content_rights,
    load_pilot,
    load_pilot_directory,
    read_pilot_files,
)
from qlab.content.pilot.model import PilotFile, source_ref
from qlab.rights import service as rights
from tests.conftest import LOCAL_HOSTS, REPO_ROOT, alembic_config
from tests.content import samples
from tests.content.support import (
    AUTHOR,
    REVIEWER,
    Env,
    Json,
    approve,
    audit_actions,
    audit_for,
    copy_json,
    count,
    data_text,
    failed_critical,
    load_syllabus,
    make_env,
    new_rights,
    now,
    publish,
    set_status_raw,
    snapshot,
    table_counts,
    usable,
)

pytestmark = [pytest.mark.db, pytest.mark.node]

SHA = "a" * 64
SHA_OTHER = "b" * 64
CUSTOM_ACTOR = "system:other_import"
HOLDER = "Synthetic holder"

# Documents without stimuli, so they can be taken all the way to `published`.
SET_A: list[Callable[[], Json]] = [
    samples.data_based_document,
    samples.plain_mcq_document,
    samples.show_that_document,
]
SET_B: list[Callable[[], Json]] = [samples.mcq_document, samples.two_column_mcq_document]


def pilot_file(stem: str, docs: Sequence[Json], sha: str = SHA) -> PilotFile:
    return PilotFile.model_validate(
        {
            "source_file": f"docs/pilot/{stem}-pilot-questions.md",
            "source_sha256": sha,
            "questions": [
                {"source_ref": source_ref(stem, n), "number": n, "document": d}
                for n, d in enumerate(docs, 1)
            ],
        }
    )


def file_a(sha: str = SHA) -> PilotFile:
    return pilot_file("demo-set", [make() for make in SET_A], sha)


def file_b(sha: str = SHA) -> PilotFile:
    return pilot_file("other-set", [make() for make in SET_B], sha)


def revised(doc: Json) -> Json:
    result = copy_json(doc)
    result["stem"]["content"].append(samples.paragraph(samples.text("A revised closing sentence.")))
    return result


def refs(pilot: PilotFile) -> list[str]:
    return [q.source_ref for q in pilot.questions]


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


def run(session: Session, env: Env, files: Iterable[PilotFile], **kwargs: Any) -> LoadReport:
    return load_pilot(
        session,
        files,
        rights_record_id=env.rights_record_id,
        syllabus_version_id=env.syllabus_version_id,
        **kwargs,
    )


def own_rows(session: Session, connection: Connection, key: str) -> Any:
    """What one question holds (the snapshot without its trailing table totals)."""
    return snapshot(session, connection, question_of(session, key).id)[:-1]


def question_of(session: Session, key: str) -> svc.QuestionView:
    found = svc.find_question_by_source_ref(session, key)
    assert found is not None, key
    return found


def latest(session: Session, key: str) -> svc.QuestionVersionView:
    return svc.list_versions(session, question_of(session, key).id)[-1]


def versions(session: Session, key: str) -> list[svc.QuestionVersionView]:
    return svc.list_versions(session, question_of(session, key).id)


def advance(session: Session, connection: Connection, version_id: uuid.UUID, status: str) -> None:
    """Move a draft version on to `status` (the document must be publishable for the last two)."""
    if status == "draft":
        return
    if status == "auto_checking":
        set_status_raw(connection, version_id, "auto_checking")
    elif status == "needs_fix":
        svc.record_check(session, actor=AUTHOR, version_id=version_id, result=failed_critical())
        svc.submit(session, actor=AUTHOR, version_id=version_id)
    else:
        svc.submit(session, actor=AUTHOR, version_id=version_id)
        if status == "rejected":
            svc.reject(session, actor=REVIEWER, version_id=version_id, reason="not suitable")
        elif status != "in_review":
            approve(session, version_id)
            if status in ("published", "withdrawn"):
                publish(session, version_id)
            if status == "withdrawn":
                svc.withdraw(session, actor=REVIEWER, version_id=version_id, reason="taken down")
    assert svc.get_version(session, version_id).status.value == status


def counts_in(report: LoadReport) -> dict[str, int]:
    found = dict(re.findall(r"(created|updated|unchanged|skipped)\D*?(\d+)", report.summary()))
    return {word: int(number) for word, number in found.items()}


# =============================================================================================
# ensure_own_content_rights
# =============================================================================================


def entries(session: Session, record_id: uuid.UUID) -> list[audit.AuditEntry]:
    return audit.entries_for(session, "rights_record", str(record_id))


def test_the_first_call_creates_the_platforms_own_record(session: Session) -> None:
    record_id = ensure_own_content_rights(session, holder=HOLDER)

    record = rights.get_record(session, record_id)
    assert record is not None
    assert record.license_ref == OWN_CONTENT_LICENSE_REF
    assert record.display_scope is rights.DisplayScope.ALL
    assert record.display_organization_id is None
    assert record.allows_ai_processing is True
    assert record.allows_commercial_use is True
    assert record.holder == HOLDER
    assert record.revoked_at is None
    assert record.valid_until is None
    for purpose in rights.Purpose:
        assert rights.is_permitted(session, record_id, purpose)
    assert [r.id for r in rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)] == [
        record_id
    ]


def test_the_first_call_writes_exactly_one_audit_entry_by_the_default_actor(
    session: Session, connection: Connection
) -> None:
    before = count(connection, "audit_log")

    record_id = ensure_own_content_rights(session, holder=HOLDER)

    assert count(connection, "audit_log") == before + 1
    written = entries(session, record_id)
    assert [e.action for e in written] == ["rights_record.created"]
    assert written[0].actor == ACTOR == "system:pilot_import"


def test_a_custom_actor_is_written_to_the_audit_entry(session: Session) -> None:
    record_id = ensure_own_content_rights(session, holder=HOLDER, actor=CUSTOM_ACTOR)

    written = entries(session, record_id)
    assert [e.action for e in written] == ["rights_record.created"]
    assert written[0].actor == CUSTOM_ACTOR


def test_a_second_call_returns_the_same_record_and_writes_nothing(
    session: Session, connection: Connection
) -> None:
    first = ensure_own_content_rights(session, holder=HOLDER)
    audit_rows = count(connection, "audit_log")

    second = ensure_own_content_rights(session, holder=HOLDER)
    third = ensure_own_content_rights(session, holder="Another holder", actor=CUSTOM_ACTOR)

    assert second == first
    assert third == first
    assert count(connection, "audit_log") == audit_rows
    assert len(rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)) == 1
    record = rights.get_record(session, first)
    assert record is not None and record.holder == HOLDER


def test_a_revoked_record_is_not_reused_and_stays_as_history(session: Session) -> None:
    old = ensure_own_content_rights(session, holder=HOLDER)
    rights.revoke(session, old, at=now())

    new = ensure_own_content_rights(session, holder=HOLDER, actor=CUSTOM_ACTOR)

    assert new != old
    stored = rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)
    assert [r.id for r in stored] == [old, new]
    assert stored[0].revoked_at is not None
    assert stored[1].revoked_at is None
    assert rights.is_permitted(session, new, rights.Purpose.DISPLAY)
    assert not rights.is_permitted(session, old, rights.Purpose.DISPLAY)
    written = entries(session, new)
    assert [e.action for e in written] == ["rights_record.created"]
    assert written[0].actor == CUSTOM_ACTOR
    assert [e.action for e in entries(session, old)] == ["rights_record.created"]


def test_after_a_replacement_the_usable_record_is_the_one_that_is_returned(
    session: Session, connection: Connection
) -> None:
    old = ensure_own_content_rights(session, holder=HOLDER)
    rights.revoke(session, old, at=now())
    new = ensure_own_content_rights(session, holder=HOLDER)
    audit_rows = count(connection, "audit_log")

    again = ensure_own_content_rights(session, holder=HOLDER)

    assert again == new
    assert count(connection, "audit_log") == audit_rows


def test_a_revocation_made_with_raw_sql_is_noticed(session: Session) -> None:
    old = ensure_own_content_rights(session, holder=HOLDER)
    session.execute(text("UPDATE rights_record SET revoked_at = now() WHERE id = :id"), {"id": old})

    new = ensure_own_content_rights(session, holder=HOLDER)

    assert new != old


def test_an_expired_record_is_not_reused(session: Session) -> None:
    expired = rights.create_record(
        session,
        holder=HOLDER,
        valid_from=now() - timedelta(days=2),
        valid_until=now() - timedelta(days=1),
        display_scope=rights.DisplayScope.ALL,
        allows_ai_processing=True,
        allows_commercial_use=True,
        license_ref=OWN_CONTENT_LICENSE_REF,
    )

    new = ensure_own_content_rights(session, holder=HOLDER)

    assert new != expired.id
    assert [r.id for r in rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)] == [
        expired.id,
        new,
    ]
    assert rights.is_permitted(session, new, rights.Purpose.DISPLAY)
    assert [e.action for e in entries(session, new)] == ["rights_record.created"]


def test_a_record_that_is_not_yet_valid_is_not_reused(session: Session) -> None:
    future = rights.create_record(
        session,
        holder=HOLDER,
        valid_from=now() + timedelta(days=1),
        display_scope=rights.DisplayScope.ALL,
        allows_ai_processing=True,
        allows_commercial_use=True,
        license_ref=OWN_CONTENT_LICENSE_REF,
    )

    new = ensure_own_content_rights(session, holder=HOLDER)

    assert new != future.id
    assert rights.is_permitted(session, new, rights.Purpose.DISPLAY)


@pytest.mark.parametrize("scope", ["none", "organization"])
def test_a_record_that_does_not_permit_everyone_is_not_reused(session: Session, scope: str) -> None:
    narrow = rights.create_record(
        session,
        holder=HOLDER,
        valid_from=now() - timedelta(days=1),
        display_scope=rights.DisplayScope(scope),
        display_organization_id=uuid.uuid4() if scope == "organization" else None,
        allows_ai_processing=True,
        allows_commercial_use=True,
        license_ref=OWN_CONTENT_LICENSE_REF,
    )

    new = ensure_own_content_rights(session, holder=HOLDER)

    assert new != narrow.id
    record = rights.get_record(session, new)
    assert record is not None and record.display_scope is rights.DisplayScope.ALL
    assert rights.is_permitted(session, new, rights.Purpose.DISPLAY)
    # and now that a usable record exists, it is the one that is found
    assert ensure_own_content_rights(session, holder=HOLDER) == new


def test_a_record_with_another_licence_reference_is_not_taken_for_the_platforms_own(
    session: Session,
) -> None:
    foreign = rights.create_record(
        session,
        holder=HOLDER,
        valid_from=now() - timedelta(days=1),
        display_scope=rights.DisplayScope.ALL,
        license_ref="synthetic:someone-else",
    )
    unlabelled = new_rights(session)

    new = ensure_own_content_rights(session, holder=HOLDER)

    assert new not in (foreign.id, unlabelled)
    assert [r.id for r in rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)] == [new]


# =============================================================================================
# load_pilot: first load
# =============================================================================================


def test_the_first_load_creates_one_authored_draft_per_pilot_question(
    session: Session, env: Env
) -> None:
    pilot = file_a()

    report = run(session, env, [pilot])

    assert report.created == refs(pilot)
    assert report.updated == []
    assert report.unchanged == []
    assert report.skipped == {}
    for question in pilot.questions:
        found = question_of(session, question.source_ref)
        assert found.origin is svc.Origin.AUTHORED
        assert found.rights_record_id == env.rights_record_id
        assert found.syllabus_version_id == env.syllabus_version_id
        assert found.source_ref == question.source_ref
        assert found.created_by == ACTOR
        stored = svc.list_versions(session, found.id)
        assert len(stored) == 1
        assert stored[0].version_no == 1
        assert stored[0].status is svc.VersionStatus.DRAFT
        assert stored[0].document == question.document
        assert stored[0].content_sha256 == svc.content_sha256(question.document)
        assert stored[0].created_by == ACTOR


def test_the_first_load_audits_each_creation_by_the_default_actor(
    session: Session, env: Env
) -> None:
    pilot = file_a()

    run(session, env, [pilot])

    for question in pilot.questions:
        version = latest(session, question.source_ref)
        written = audit_for(session, version.id)
        assert [e.action for e in written] == ["question_version.created"]
        assert written[0].actor == ACTOR
        assert question.source_ref in data_text(written[0])


def test_the_import_never_moves_a_version_beyond_draft(
    session: Session, connection: Connection, env: Env
) -> None:
    pilot = file_a()

    run(session, env, [pilot])
    run(session, env, [pilot])

    statuses = connection.execute(text("SELECT DISTINCT status FROM question_version")).all()
    assert [row[0] for row in statuses] == ["draft"]
    assert count(connection, "question_version") == len(pilot.questions)
    actions = connection.execute(text("SELECT DISTINCT action FROM audit_log")).all()
    assert {row[0] for row in actions} <= {"rights_record.created", "question_version.created"}


def test_the_summary_has_the_four_counts(session: Session, env: Env) -> None:
    report = run(session, env, [file_a()])

    assert counts_in(report) == {"created": 3, "updated": 0, "unchanged": 0, "skipped": 0}
    again = run(session, env, [file_a()])
    assert counts_in(again) == {"created": 0, "updated": 0, "unchanged": 3, "skipped": 0}


def test_an_empty_report_summarises_four_zeros() -> None:
    assert counts_in(LoadReport()) == {"created": 0, "updated": 0, "unchanged": 0, "skipped": 0}


def test_the_summary_counts_every_bucket(session: Session, env: Env) -> None:
    report = LoadReport(
        created=["a", "b"], updated=["c"], unchanged=["d", "e", "f"], skipped={"g": "in_review"}
    )

    assert counts_in(report) == {"created": 2, "updated": 1, "unchanged": 3, "skipped": 1}


def test_two_files_in_one_call_are_reported_in_order(session: Session, env: Env) -> None:
    first, second = file_a(), file_b()

    report = run(session, env, [first, second])

    assert report.created == refs(first) + refs(second)
    assert counts_in(report)["created"] == 5
    for key in report.created:
        assert latest(session, key).version_no == 1


def test_any_iterable_of_files_is_accepted(session: Session, env: Env) -> None:
    report = run(session, env, (pilot for pilot in [file_a(), file_b()]))

    assert len(report.created) == 5


def test_a_custom_actor_is_used_for_questions_and_audit(session: Session, env: Env) -> None:
    pilot = file_a()

    run(session, env, [pilot], actor=CUSTOM_ACTOR)

    key = pilot.questions[0].source_ref
    assert question_of(session, key).created_by == CUSTOM_ACTOR
    version = latest(session, key)
    assert version.created_by == CUSTOM_ACTOR
    assert [e.actor for e in audit_for(session, version.id)] == [CUSTOM_ACTOR]


def test_loading_needs_the_given_rights_record_to_permit_display(
    session: Session, connection: Connection, env: Env
) -> None:
    revoked = new_rights(session, revoked=True)
    counts = table_counts(connection)

    with pytest.raises(rights.RightsDenied):
        load_pilot(
            session,
            [file_a()],
            rights_record_id=revoked,
            syllabus_version_id=env.syllabus_version_id,
        )

    assert svc.find_question_by_source_ref(session, file_a().questions[0].source_ref) is None
    usable(session)
    assert table_counts(connection) == counts


# =============================================================================================
# load_pilot: running it again
# =============================================================================================


def test_a_second_load_of_identical_files_changes_nothing(
    session: Session, connection: Connection, env: Env
) -> None:
    files = [file_a(), file_b()]
    first = run(session, env, files)
    keys = first.created
    before = [snapshot(session, connection, question_of(session, k).id) for k in keys]
    audit_rows = count(connection, "audit_log")
    totals = table_counts(connection)

    second = run(session, env, [file_a(), file_b()])

    assert second.unchanged == keys
    assert second.created == []
    assert second.updated == []
    assert second.skipped == {}
    assert [snapshot(session, connection, question_of(session, k).id) for k in keys] == before
    assert count(connection, "audit_log") == audit_rows
    assert table_counts(connection) == totals


def test_the_source_hash_of_the_file_does_not_make_a_question_changed(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a(SHA)])
    audit_rows = count(connection, "audit_log")

    report = run(session, env, [file_a(SHA_OTHER)])

    assert report.unchanged == refs(file_a())
    assert count(connection, "audit_log") == audit_rows


def test_a_load_with_a_new_subset_creates_only_the_missing_questions(
    session: Session, env: Env
) -> None:
    run(session, env, [file_a()])

    report = run(session, env, [file_a(), file_b()])

    assert report.unchanged == refs(file_a())
    assert report.created == refs(file_b())


# =============================================================================================
# load_pilot: changed content
# =============================================================================================


def changed_a(index: int = 1) -> PilotFile:
    docs = [make() for make in SET_A]
    docs[index] = revised(docs[index])
    return pilot_file("demo-set", docs)


def test_changed_content_of_a_draft_is_updated_in_place(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1)
    key = pilot.questions[1].source_ref
    others = [q.source_ref for q in pilot.questions if q.source_ref != key]
    before_version = latest(session, key)
    before_question = question_of(session, key)
    before_others = [own_rows(session, connection, k) for k in others]

    report = run(session, env, [pilot])

    assert report.updated == [key]
    assert report.unchanged == others
    assert report.created == []
    assert report.skipped == {}
    after_question = question_of(session, key)
    assert after_question.id == before_question.id
    assert after_question.source_ref == key
    stored = svc.list_versions(session, after_question.id)
    assert len(stored) == 1
    assert stored[0].id == before_version.id
    assert stored[0].version_no == 1
    assert stored[0].status is svc.VersionStatus.DRAFT
    assert stored[0].document == pilot.questions[1].document
    assert stored[0].content_sha256 == svc.content_sha256(pilot.questions[1].document)
    assert stored[0].content_sha256 != before_version.content_sha256
    assert [own_rows(session, connection, k) for k in others] == before_others


def test_an_update_is_audited_with_the_new_hash_by_the_import_actor(
    session: Session, env: Env
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(0)
    key = pilot.questions[0].source_ref
    version = latest(session, key)

    run(session, env, [pilot], actor=CUSTOM_ACTOR)

    written = audit_for(session, version.id)
    assert [e.action for e in written] == ["question_version.created", "question_version.updated"]
    assert written[0].actor == ACTOR
    assert written[1].actor == CUSTOM_ACTOR
    assert svc.content_sha256(pilot.questions[0].document) in data_text(written[1])


def test_the_default_actor_audits_an_update(session: Session, env: Env) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(2)

    run(session, env, [pilot])

    version = latest(session, pilot.questions[2].source_ref)
    assert [e.actor for e in audit_for(session, version.id)] == [ACTOR, ACTOR]


def test_changed_content_of_a_version_that_needs_fixing_is_updated_and_becomes_a_draft(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1)
    key = pilot.questions[1].source_ref
    version = latest(session, key)
    advance(session, connection, version.id, "needs_fix")

    report = run(session, env, [pilot])

    assert report.updated == [key]
    assert report.skipped == {}
    after = latest(session, key)
    assert after.id == version.id
    assert after.version_no == 1
    assert after.status is svc.VersionStatus.DRAFT
    assert after.document == pilot.questions[1].document
    assert len(versions(session, key)) == 1


def test_unchanged_content_of_a_version_that_needs_fixing_is_left_alone(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    key = file_a().questions[0].source_ref
    advance(session, connection, latest(session, key).id, "needs_fix")
    before = snapshot(session, connection, question_of(session, key).id)

    report = run(session, env, [file_a()])

    assert key in report.unchanged
    assert key not in report.updated
    assert snapshot(session, connection, question_of(session, key).id) == before
    assert latest(session, key).status is svc.VersionStatus.NEEDS_FIX


LOCKED = ["auto_checking", "in_review", "approved", "published", "withdrawn", "rejected"]


@pytest.mark.parametrize("status", LOCKED)
def test_changed_content_of_a_version_past_editing_is_skipped_and_nothing_changes(
    session: Session, connection: Connection, env: Env, status: str
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1)
    key = pilot.questions[1].source_ref
    advance(session, connection, latest(session, key).id, status)
    question_id = question_of(session, key).id
    before = snapshot(session, connection, question_id)
    audit_before = audit_actions(session, latest(session, key).id)
    audit_rows = count(connection, "audit_log")

    report = run(session, env, [pilot])

    assert report.skipped == {key: status}
    assert key not in report.updated + report.created + report.unchanged
    assert snapshot(session, connection, question_id) == before
    assert audit_actions(session, latest(session, key).id) == audit_before
    assert count(connection, "audit_log") == audit_rows
    assert len(svc.list_versions(session, question_id)) == 1  # no revision was opened
    assert latest(session, key).status.value == status
    # the other two questions of the file are unaffected and unchanged
    assert sorted(report.unchanged) == sorted(r for r in refs(pilot) if r != key)


@pytest.mark.parametrize("status", LOCKED)
def test_unchanged_content_of_a_version_past_editing_is_unchanged_not_skipped(
    session: Session, connection: Connection, env: Env, status: str
) -> None:
    run(session, env, [file_a()])
    key = file_a().questions[1].source_ref
    advance(session, connection, latest(session, key).id, status)
    question_id = question_of(session, key).id
    before = snapshot(session, connection, question_id)

    report = run(session, env, [file_a()])

    assert report.skipped == {}
    assert report.unchanged == refs(file_a())
    assert snapshot(session, connection, question_id) == before


def test_a_published_question_is_not_revised_by_a_changed_file(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(0)
    key = pilot.questions[0].source_ref
    published = latest(session, key)
    advance(session, connection, published.id, "published")

    run(session, env, [pilot])
    run(session, env, [pilot])

    stored = versions(session, key)
    assert [v.version_no for v in stored] == [1]
    assert stored[0].status is svc.VersionStatus.PUBLISHED
    assert stored[0].content_sha256 == published.content_sha256
    assert svc.get_published_version(session, question_of(session, key).id).id == published.id


def test_an_update_followed_by_an_identical_load_is_unchanged(session: Session, env: Env) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1)
    run(session, env, [pilot])

    report = run(session, env, [pilot])

    assert report.unchanged == refs(pilot)
    assert report.updated == []


def test_changing_back_to_the_original_content_updates_again(session: Session, env: Env) -> None:
    run(session, env, [file_a()])
    run(session, env, [changed_a(1)])

    report = run(session, env, [file_a()])

    key = file_a().questions[1].source_ref
    assert report.updated == [key]
    assert latest(session, key).document == file_a().questions[1].document


# =============================================================================================
# load_pilot: errors propagate; the caller's transaction decides
# =============================================================================================


def broken_file() -> PilotFile:
    # a command term the syllabus version does not define: the schema accepts it, the service
    # refuses it
    target = samples.data_based_document()
    target["parts"][0]["command_term"] = "no_such_command_term"
    return pilot_file("broken-set", [make() for make in SET_B[:1]] + [target])


def test_an_invalid_document_raises_and_the_caller_can_roll_everything_back(
    session: Session, connection: Connection, env: Env
) -> None:
    pilot = broken_file()
    good_key = pilot.questions[0].source_ref
    counts = table_counts(connection)

    nested = session.begin_nested()
    with pytest.raises(svc.InvalidDocument):
        run(session, env, [file_a(), pilot])
    nested.rollback()

    assert table_counts(connection) == counts
    assert svc.find_question_by_source_ref(session, good_key) is None
    for key in refs(file_a()) + refs(pilot):
        assert svc.find_question_by_source_ref(session, key) is None
    usable(session)


def test_after_the_failed_load_is_rolled_back_a_corrected_load_works(
    session: Session, env: Env
) -> None:
    nested = session.begin_nested()
    with pytest.raises(svc.InvalidDocument):
        run(session, env, [broken_file()])
    nested.rollback()

    report = run(session, env, [file_a()])

    assert report.created == refs(file_a())


def test_an_invalid_document_does_not_hide_the_error_type_of_the_service(
    session: Session, env: Env
) -> None:
    with pytest.raises(svc.InvalidDocument) as caught:
        run(session, env, [broken_file()])

    assert any("no_such_command_term" in error for error in caught.value.errors)


def test_an_invalid_document_on_update_raises_too(session: Session, env: Env) -> None:
    run(session, env, [file_a()])
    docs = [make() for make in SET_A]
    docs[0]["parts"][0]["command_term"] = "no_such_command_term"
    pilot = pilot_file("demo-set", docs)
    key = pilot.questions[0].source_ref
    before = latest(session, key)

    nested = session.begin_nested()
    with pytest.raises(svc.InvalidDocument):
        run(session, env, [pilot])
    nested.rollback()

    assert latest(session, key).content_sha256 == before.content_sha256


# =============================================================================================
# read_pilot_files
# =============================================================================================


def write(directory: Path, pilot: PilotFile, name: str | None = None) -> Path:
    path = directory / (name if name is not None else f"{pilot.stem}.json")
    path.write_text(pilot.to_json(), encoding="utf-8")
    return path


def test_files_are_read_sorted_by_name(tmp_path: Path) -> None:
    later = pilot_file("zz-set", [samples.plain_mcq_document()])
    middle = file_b()
    earlier = file_a()
    for pilot in (later, earlier, middle):  # written in a different order than sorted
        write(tmp_path, pilot)

    result = read_pilot_files(tmp_path)

    assert [p.stem for p in result] == ["demo-set", "other-set", "zz-set"]
    assert result == [earlier, middle, later]


def test_an_empty_directory_is_a_file_not_found_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_pilot_files(tmp_path)


def test_a_directory_with_only_other_files_counts_as_empty(tmp_path: Path) -> None:
    (tmp_path / "CONVERSION_REPORT.md").write_text("# report\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("{}", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        read_pilot_files(tmp_path)


def test_other_files_in_the_directory_are_ignored(tmp_path: Path) -> None:
    write(tmp_path, file_a())
    (tmp_path / "CONVERSION_REPORT.md").write_text("# report\n", encoding="utf-8")

    assert [p.stem for p in read_pilot_files(tmp_path)] == ["demo-set"]


def test_a_malformed_json_file_is_a_validation_error(tmp_path: Path) -> None:
    write(tmp_path, file_a())
    (tmp_path / "zzz.json").write_text("{ not json", encoding="utf-8")

    with pytest.raises(ValidationError):
        read_pilot_files(tmp_path)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda d: d.update(questions=[]), id="no_questions"),
        pytest.param(lambda d: d.update(source_sha256="xyz"), id="bad_hash"),
        pytest.param(lambda d: d.update(extra_field=1), id="unknown_field"),
        pytest.param(lambda d: d["questions"][0].update(source_ref="pilot/other#1"), id="bad_ref"),
        pytest.param(lambda d: d.pop("source_file"), id="missing_source_file"),
    ],
)
def test_a_file_of_the_wrong_shape_is_a_validation_error(
    tmp_path: Path, mutate: Callable[[Json], object]
) -> None:
    raw = json.loads(file_a().to_json())
    mutate(raw)
    (tmp_path / "demo-set.json").write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValidationError):
        read_pilot_files(tmp_path)


def test_a_file_that_round_trips_through_disk_equals_the_original(tmp_path: Path) -> None:
    original = file_a()
    write(tmp_path, original)

    assert read_pilot_files(tmp_path) == [original]


# =============================================================================================
# load_pilot_directory
# =============================================================================================


def test_the_pilot_syllabus_names_the_reference_that_is_shipped() -> None:
    assert PILOT_SYLLABUS == {"program": "ib_dp", "subject": "physics", "version": "2025"}


def test_without_the_pilot_syllabus_loaded_the_directory_load_raises_lookup_error(
    session: Session, connection: Connection, tmp_path: Path
) -> None:
    write(tmp_path, file_a())
    counts = table_counts(connection)

    with pytest.raises(LookupError):
        load_pilot_directory(session, tmp_path, holder=HOLDER)

    usable(session)
    for key in refs(file_a()):
        assert svc.find_question_by_source_ref(session, key) is None
    assert table_counts(connection) == counts


def test_an_empty_directory_raises_even_when_the_syllabus_is_loaded(
    session: Session, tmp_path: Path
) -> None:
    load_syllabus(session)

    with pytest.raises(FileNotFoundError):
        load_pilot_directory(session, tmp_path, holder=HOLDER)


def test_the_directory_load_resolves_rights_and_syllabus_and_loads_every_file(
    session: Session, tmp_path: Path
) -> None:
    syllabus_id = load_syllabus(session)
    first, second = file_a(), file_b()
    write(tmp_path, second)
    write(tmp_path, first)

    report = load_pilot_directory(session, tmp_path, holder=HOLDER)

    assert report.created == refs(first) + refs(second)  # files by name: demo-set, other-set
    records = rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)
    assert len(records) == 1
    assert records[0].holder == HOLDER
    assert records[0].display_scope is rights.DisplayScope.ALL
    assert [e.action for e in entries(session, records[0].id)] == ["rights_record.created"]
    for key in report.created:
        found = question_of(session, key)
        assert found.rights_record_id == records[0].id
        assert found.syllabus_version_id == syllabus_id
        assert found.created_by == ACTOR
        assert latest(session, key).status is svc.VersionStatus.DRAFT


def test_running_the_directory_load_again_is_a_no_op(
    session: Session, connection: Connection, tmp_path: Path
) -> None:
    load_syllabus(session)
    write(tmp_path, file_a())
    write(tmp_path, file_b())
    load_pilot_directory(session, tmp_path, holder=HOLDER)
    totals = table_counts(connection)

    report = load_pilot_directory(session, tmp_path, holder=HOLDER)

    assert report.created == []
    assert report.updated == []
    assert report.skipped == {}
    assert report.unchanged == refs(file_a()) + refs(file_b())
    assert table_counts(connection) == totals
    assert len(rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)) == 1


# =============================================================================================
# The committed pilot files (integration; counts and keys only)
# =============================================================================================

PILOT_DIR = REPO_ROOT / "content" / "pilot"
KEY_FORM = re.compile(r"pilot/[a-z0-9][a-z0-9-]*#[1-9][0-9]*")


def committed_questions() -> list[tuple[str, Json]]:
    result: list[tuple[str, Json]] = []
    for path in sorted(PILOT_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        for question in raw["questions"]:
            result.append((str(question["source_ref"]), question["document"]))
    return result


def test_the_committed_pilot_files_load_as_130_draft_questions(
    session: Session, connection: Connection
) -> None:
    load_syllabus(session)
    expected = committed_questions()
    expected_classes: dict[str, int] = {}
    for _, doc in expected:
        expected_classes[doc["question_class"]] = expected_classes.get(doc["question_class"], 0) + 1
    expected_visual = sum(1 for _, doc in expected if doc.get("stimuli"))

    report = load_pilot_directory(session, PILOT_DIR, holder="Test holder")

    assert len(expected) == 130
    assert len(report.created) == 130
    assert report.updated == [] and report.unchanged == [] and report.skipped == {}
    assert count(connection, "question") == 130
    assert count(connection, "question_version") == 130
    statuses = connection.execute(
        text("SELECT status, count(*) FROM question_version GROUP BY status")
    ).all()
    assert [(s, n) for s, n in statuses] == [("draft", 130)]
    by_class: dict[str, int] = dict(
        connection.execute(
            text("SELECT question_class, count(*) FROM question_version GROUP BY question_class")
        ).all()
    )
    assert by_class == expected_classes
    assert sorted(by_class.values(), reverse=True) == [101, 24, 5]
    keys = [
        str(k)
        for (k,) in connection.execute(
            text("SELECT source_ref FROM question ORDER BY source_ref")
        ).all()
    ]
    assert len(keys) == len(set(keys)) == 130
    assert all(KEY_FORM.fullmatch(k) for k in keys)
    assert sorted(keys) == sorted(k for k, _ in expected)
    assert sorted(report.created) == keys
    visual = connection.execute(
        text("SELECT count(*) FROM question_version WHERE has_unverified_visuals")
    ).scalar_one()
    assert visual == expected_visual == 24
    origins = connection.execute(text("SELECT DISTINCT origin FROM question")).all()
    assert [o for (o,) in origins] == ["authored"]
    assert len(rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)) == 1


def test_loading_the_committed_pilot_files_twice_reports_130_unchanged(
    session: Session, connection: Connection
) -> None:
    load_syllabus(session)
    load_pilot_directory(session, PILOT_DIR, holder="Test holder")
    totals = table_counts(connection)

    second = load_pilot_directory(session, PILOT_DIR, holder="Test holder")

    assert len(second.unchanged) == 130
    assert second.created == [] and second.updated == [] and second.skipped == {}
    assert counts_in(second) == {"created": 0, "updated": 0, "unchanged": 130, "skipped": 0}
    assert table_counts(connection) == totals


# =============================================================================================
# The `load` command
# =============================================================================================

CLI_ENV = "QLAB_DATABASE_URL"


@pytest.fixture
def cli_engine(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> Iterator[Engine]:
    """A database of its own (the command opens its own engine and commits), migrated, with the
    syllabus reference loaded and committed, created here and dropped afterwards."""
    url = engine.url
    base = url.database
    if base is None or not re.fullmatch(r"[a-z0-9_]+_test", base) or url.host not in LOCAL_HOSTS:
        raise RuntimeError("refusing to create a second database next to a non-test database")
    name = f"{base}_cli"
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    own_url = url.set(database=name)
    own = create_engine(own_url)
    try:
        with own.begin() as connection:
            command.upgrade(alembic_config(connection), "head")
        with Session(own) as setup:
            load_syllabus(setup)
            setup.commit()
        monkeypatch.setenv(CLI_ENV, own_url.render_as_string(hide_password=False))
        yield own
    finally:
        own.dispose()
        with admin.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        admin.dispose()


def repo_shaped(tmp_path: Path, files: Sequence[PilotFile]) -> Path:
    directory = tmp_path / "repo" / "content" / "pilot"
    directory.mkdir(parents=True)
    for pilot in files:
        write(directory, pilot)
    return tmp_path / "repo"


def scalar(engine: Engine, sql: str) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql)).scalar_one())


def load_args(root: Path, *extra: str) -> list[str]:
    return ["load", "--root", str(root), *extra]


def test_the_parser_knows_the_load_options() -> None:
    parsed = cli.build_parser().parse_args(
        ["load", "--root", "/somewhere", "--holder", "Name", "--dry-run"]
    )

    assert parsed.command == "load"
    assert parsed.root == Path("/somewhere")
    assert parsed.holder == "Name"
    assert parsed.dry_run is True
    defaults = cli.build_parser().parse_args(["load"])
    assert defaults.dry_run is False
    assert defaults.root is None
    assert defaults.holder


def test_a_dry_run_reports_and_leaves_nothing_behind(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = repo_shaped(tmp_path, [file_a(), file_b()])

    status = cli.main(load_args(root, "--dry-run"))

    assert status == 0
    lines = capsys.readouterr().out.splitlines()
    summaries = [line for line in lines if line.startswith("dry run:")]
    assert len(summaries) == 1
    assert "created 5" in summaries[0]
    assert scalar(cli_engine, "SELECT count(*) FROM question") == 0
    assert scalar(cli_engine, "SELECT count(*) FROM question_version") == 0
    assert scalar(cli_engine, "SELECT count(*) FROM rights_record") == 0
    assert scalar(cli_engine, "SELECT count(*) FROM audit_log") == 0


def test_a_real_run_commits_the_questions_and_the_rights_record(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = repo_shaped(tmp_path, [file_a(), file_b()])

    status = cli.main(load_args(root, "--holder", "Command line holder"))

    assert status == 0
    out = capsys.readouterr().out
    assert not any(line.startswith("dry run:") for line in out.splitlines())
    assert "created 5" in out
    assert scalar(cli_engine, "SELECT count(*) FROM question") == 5
    assert scalar(cli_engine, "SELECT count(*) FROM question WHERE origin = 'authored'") == 5
    assert scalar(cli_engine, "SELECT count(*) FROM question_version WHERE status = 'draft'") == 5
    assert scalar(cli_engine, "SELECT count(*) FROM question WHERE source_ref LIKE 'pilot/%'") == 5
    with Session(cli_engine) as session:
        (record,) = rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)
        assert record.holder == "Command line holder"
        assert record.display_scope is rights.DisplayScope.ALL
        question = question_of(session, refs(file_a())[0])
        assert question.created_by == ACTOR
        assert question.rights_record_id == record.id


def test_a_further_run_reports_everything_unchanged_and_writes_nothing(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = repo_shaped(tmp_path, [file_a(), file_b()])
    assert cli.main(load_args(root)) == 0
    capsys.readouterr()
    audit_rows = scalar(cli_engine, "SELECT count(*) FROM audit_log")
    versions_rows = scalar(cli_engine, "SELECT count(*) FROM question_version")

    assert cli.main(load_args(root)) == 0

    out = capsys.readouterr().out
    assert "unchanged 5" in out
    assert "created 0" in out
    assert scalar(cli_engine, "SELECT count(*) FROM question") == 5
    assert scalar(cli_engine, "SELECT count(*) FROM audit_log") == audit_rows
    assert scalar(cli_engine, "SELECT count(*) FROM question_version") == versions_rows
    assert scalar(cli_engine, "SELECT count(*) FROM rights_record") == 1


def test_a_dry_run_after_a_real_run_changes_nothing_either(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = repo_shaped(tmp_path, [file_a()])
    cli.main(load_args(root))
    capsys.readouterr()

    assert cli.main(load_args(root, "--dry-run")) == 0

    out = capsys.readouterr().out
    assert any(line.startswith("dry run:") and "unchanged 3" in line for line in out.splitlines())
    assert scalar(cli_engine, "SELECT count(*) FROM question") == 3


def test_a_changed_file_is_updated_by_a_later_run(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = repo_shaped(tmp_path, [file_a()])
    cli.main(load_args(root))
    capsys.readouterr()
    (root / "content" / "pilot" / "demo-set.json").write_text(
        changed_a(1).to_json(), encoding="utf-8"
    )

    assert cli.main(load_args(root)) == 0

    out = capsys.readouterr().out
    assert "updated 1" in out and "unchanged 2" in out
    assert scalar(cli_engine, "SELECT count(*) FROM question_version") == 3


def test_a_skipped_question_is_named_in_the_output(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = repo_shaped(tmp_path, [file_a()])
    cli.main(load_args(root))
    key = file_a().questions[1].source_ref
    with Session(cli_engine) as session:
        advance(session, session.connection(), latest(session, key).id, "in_review")
        session.commit()
    (root / "content" / "pilot" / "demo-set.json").write_text(
        changed_a(1).to_json(), encoding="utf-8"
    )
    capsys.readouterr()

    assert cli.main(load_args(root)) == 0

    out = capsys.readouterr().out
    assert key in out
    assert "in_review" in out
    assert "skipped 1" in out


def test_an_invalid_document_in_a_later_file_leaves_nothing_committed(
    cli_engine: Engine, tmp_path: Path
) -> None:
    root = repo_shaped(tmp_path, [file_a(), broken_file()])  # "broken-set" sorts first

    with pytest.raises(svc.InvalidDocument):
        cli.main(load_args(root))

    assert scalar(cli_engine, "SELECT count(*) FROM question") == 0
    assert scalar(cli_engine, "SELECT count(*) FROM question_version") == 0
    assert scalar(cli_engine, "SELECT count(*) FROM rights_record") == 0
    assert scalar(cli_engine, "SELECT count(*) FROM audit_log") == 0


def test_without_a_usable_renderer_the_command_fails_before_writing_anything(
    cli_engine: Engine, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = repo_shaped(tmp_path, [file_a()])
    monkeypatch.setenv("QLAB_NODE_BIN", str(tmp_path / "no-such-node"))

    with pytest.raises(RendererUnavailable):
        cli.main(load_args(root))

    assert scalar(cli_engine, "SELECT count(*) FROM question") == 0
    assert scalar(cli_engine, "SELECT count(*) FROM rights_record") == 0
    assert scalar(cli_engine, "SELECT count(*) FROM audit_log") == 0


def test_without_a_usable_renderer_a_dry_run_fails_too(
    cli_engine: Engine, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = repo_shaped(tmp_path, [file_a()])
    monkeypatch.setenv("QLAB_NODE_BIN", str(tmp_path / "no-such-node"))

    with pytest.raises(RendererUnavailable):
        cli.main(load_args(root, "--dry-run"))

    assert scalar(cli_engine, "SELECT count(*) FROM question") == 0


def test_a_root_without_converted_files_fails_and_writes_nothing(
    cli_engine: Engine, tmp_path: Path
) -> None:
    root = tmp_path / "empty-repo"
    (root / "content" / "pilot").mkdir(parents=True)

    with pytest.raises(FileNotFoundError):
        cli.main(load_args(root))

    assert scalar(cli_engine, "SELECT count(*) FROM rights_record") == 0
