"""Import of converted pilot files: `qlab.content.pilot.loader` and the `load` command.

Written from docs/pilot/IMPORT_RULES.md sections 2 and 7, decision D-58, the module docstring,
constants, report class and function docstrings of `qlab.content.pilot.loader`, the docstrings of
`qlab.content.service`, `qlab.rights.service` and `qlab.audit.service`, and the argument parser
and the `run_load` docstring of the command. No function body was read.

Test data is synthetic: the documents are the content tests' own samples wrapped as pilot
questions under made-up file stems, and the "Markdown" files are one made-up line each. The one
integration test at the end loads the committed files and asserts on counts and keys only,
never on question wording.

Saving a document runs the math check, so every test here needs Node.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
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
    OwnContentRightsError,
    SourceMismatch,
    create_own_content_rights,
    find_own_content_rights,
    load_pilot,
    load_pilot_directory,
    read_pilot_files,
    verify_sources,
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
    document,
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
OPERATOR = "u_operator"
EDITOR = "u_editor"
CUSTOM_ACTOR = "system:other_import"
HOLDER = "Synthetic holder"
COMPLETED = "pilot_import.completed"
COUNT_NAMES = ("created", "updated", "unchanged", "skipped", "blocked")

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


def revised(doc: Json, sentence: str = "A revised closing sentence.") -> Json:
    result = copy_json(doc)
    result["stem"]["content"].append(samples.paragraph(samples.text(sentence)))
    return result


def refs(pilot: PilotFile) -> list[str]:
    return [q.source_ref for q in pilot.questions]


def changed_a(index: int = 1, sentence: str = "A revised closing sentence.") -> PilotFile:
    docs = [make() for make in SET_A]
    docs[index] = revised(docs[index], sentence)
    return pilot_file("demo-set", docs)


def broken_file() -> PilotFile:
    # A command term the syllabus version does not define: the schema accepts it, the service
    # refuses it.
    target = samples.data_based_document()
    target["parts"][0]["command_term"] = "no_such_command_term"
    return pilot_file("broken-set", [make() for make in SET_B[:1]] + [target])


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


def run(session: Session, env: Env, files: Sequence[PilotFile], **kwargs: Any) -> LoadReport:
    kwargs.setdefault("operator", OPERATOR)
    return load_pilot(
        session,
        files,
        rights_record_id=env.rights_record_id,
        syllabus_version_id=env.syllabus_version_id,
        **kwargs,
    )


def question_of(session: Session, key: str) -> svc.QuestionView:
    found = svc.find_question_by_source_ref(session, key)
    assert found is not None, key
    return found


def versions(session: Session, key: str) -> list[svc.QuestionVersionView]:
    return svc.list_versions(session, question_of(session, key).id)


def latest(session: Session, key: str) -> svc.QuestionVersionView:
    return versions(session, key)[-1]


def own_rows(session: Session, connection: Connection, key: str) -> Any:
    """What one question holds (the snapshot without its trailing table totals)."""
    return snapshot(session, connection, question_of(session, key).id)[:-1]


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


def find_key(data: object, key: str) -> object:
    """The first value stored under `key`, however deeply the audit data nests it."""
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for value in data.values():
            found = find_key(value, key)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = find_key(item, key)
            if found is not None:
                return found
    return None


def completed(session: Session, operator: str = OPERATOR) -> list[audit.AuditEntry]:
    return audit.entries_for(session, "pilot_import", operator)


def rights_entries(session: Session, record_id: uuid.UUID) -> list[audit.AuditEntry]:
    return audit.entries_for(session, "rights_record", str(record_id))


def rights_rows(connection: Connection) -> int:
    return int(connection.execute(text("SELECT count(*) FROM rights_record")).scalar_one())


def own_rows_count(session: Session) -> int:
    return len(rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF))


# --- a repository-shaped temporary directory ----------------------------------------------------


@dataclass(frozen=True)
class Repo:
    root: Path
    files: list[PilotFile]

    @property
    def json_dir(self) -> Path:
        return self.root / "content" / "pilot"

    def markdown(self, pilot: PilotFile) -> Path:
        return self.root / pilot.source_file


DEFAULT_SPECS: list[tuple[str, list[Callable[[], Json]]]] = [
    ("demo-set", SET_A),
    ("other-set", SET_B),
]


def markdown_text(stem: str) -> str:
    return f"Synthetic stand-in for the source file of {stem}.\n"


def write(directory: Path, pilot: PilotFile, name: str | None = None) -> Path:
    path = directory / (name if name is not None else f"{pilot.stem}.json")
    path.write_text(pilot.to_json(), encoding="utf-8")
    return path


def build_repo(
    base: Path,
    specs: Sequence[tuple[str, Sequence[Callable[[], Json]]]] = DEFAULT_SPECS,
    name: str = "repo",
) -> Repo:
    root = base / name
    (root / "docs" / "pilot").mkdir(parents=True)
    (root / "content" / "pilot").mkdir(parents=True)
    files: list[PilotFile] = []
    for stem, makers in specs:
        body = markdown_text(stem)
        (root / "docs" / "pilot" / f"{stem}-pilot-questions.md").write_text(body, encoding="utf-8")
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        pilot = pilot_file(stem, [make() for make in makers], digest)
        write(root / "content" / "pilot", pilot)
        files.append(pilot)
    return Repo(root, files)


def own_record(session: Session, **overrides: Any) -> rights.RightsRecordView:
    """A record exactly as the import expects it, unless `overrides` say otherwise."""
    params: dict[str, Any] = {
        "holder": HOLDER,
        "valid_from": now() - timedelta(days=1),
        "display_scope": rights.DisplayScope.ALL,
        "allows_ai_processing": True,
        "allows_commercial_use": True,
        "license_ref": OWN_CONTENT_LICENSE_REF,
    }
    params.update(overrides)
    return rights.create_record(session, **params)


# =============================================================================================
# find_own_content_rights
# =============================================================================================


def test_no_record_with_the_reference_means_none(session: Session) -> None:
    assert find_own_content_rights(session, holder=HOLDER) is None


def test_records_with_other_references_do_not_count(session: Session) -> None:
    own_record(session, license_ref="synthetic:someone-else")
    new_rights(session)

    assert find_own_content_rights(session, holder=HOLDER) is None


def test_exactly_one_conforming_record_is_returned(session: Session) -> None:
    record = own_record(session)
    own_record(session, license_ref="synthetic:someone-else")  # unrelated, ignored

    assert find_own_content_rights(session, holder=HOLDER) == record.id


def test_finding_a_record_writes_nothing(session: Session, connection: Connection) -> None:
    own_record(session)
    totals = (rights_rows(connection), count(connection, "audit_log"))

    find_own_content_rights(session, holder=HOLDER)

    assert (rights_rows(connection), count(connection, "audit_log")) == totals


def revoked(session: Session) -> None:
    rights.revoke(session, own_record(session).id, at=now())


def revoked_with_a_valid_one(session: Session) -> None:
    revoked(session)
    own_record(session)


def expired(session: Session) -> None:
    own_record(
        session,
        valid_from=now() - timedelta(days=2),
        valid_until=now() - timedelta(days=1),
    )


def ends_in_the_future(session: Session) -> None:
    own_record(session, valid_until=now() + timedelta(days=30))


def not_yet_valid(session: Session) -> None:
    own_record(session, valid_from=now() + timedelta(days=1))


def two_valid(session: Session) -> None:
    own_record(session)
    own_record(session)


def wrong_holder(session: Session) -> None:
    own_record(session, holder="Somebody else")


def scope_none(session: Session) -> None:
    own_record(session, display_scope=rights.DisplayScope.NONE)


def scope_organization(session: Session) -> None:
    own_record(
        session,
        display_scope=rights.DisplayScope.ORGANIZATION,
        display_organization_id=uuid.uuid4(),
    )


def ai_off(session: Session) -> None:
    own_record(session, allows_ai_processing=False)


def commercial_off(session: Session) -> None:
    own_record(session, allows_commercial_use=False)


UNACCEPTABLE: dict[str, Callable[[Session], None]] = {
    "revoked": revoked,
    "revoked_with_a_valid_one_beside_it": revoked_with_a_valid_one,
    "expired": expired,
    "ends_in_the_future": ends_in_the_future,
    "not_yet_valid": not_yet_valid,
    "two_valid": two_valid,
    "wrong_holder": wrong_holder,
    "scope_none": scope_none,
    "scope_organization": scope_organization,
    "ai_processing_off": ai_off,
    "commercial_use_off": commercial_off,
}


@pytest.mark.parametrize("build", UNACCEPTABLE.values(), ids=UNACCEPTABLE.keys())
def test_a_record_that_is_not_exactly_the_expected_one_stops_the_import(
    session: Session, connection: Connection, build: Callable[[Session], None]
) -> None:
    build(session)
    before = (rights_rows(connection), count(connection, "audit_log"))

    with pytest.raises(OwnContentRightsError):
        find_own_content_rights(session, holder=HOLDER)

    assert (rights_rows(connection), count(connection, "audit_log")) == before
    usable(session)


def test_the_holder_must_match_exactly(session: Session) -> None:
    own_record(session, holder=HOLDER)

    with pytest.raises(OwnContentRightsError):
        find_own_content_rights(session, holder=HOLDER.upper())
    with pytest.raises(OwnContentRightsError):
        find_own_content_rights(session, holder=HOLDER + " ")


def test_a_revoked_record_is_noticed_when_it_was_revoked_by_raw_sql(session: Session) -> None:
    record = own_record(session)
    assert find_own_content_rights(session, holder=HOLDER) == record.id
    session.execute(
        text("UPDATE rights_record SET revoked_at = now() WHERE id = :i"), {"i": record.id}
    )

    with pytest.raises(OwnContentRightsError):
        find_own_content_rights(session, holder=HOLDER)


# =============================================================================================
# create_own_content_rights
# =============================================================================================


def test_the_record_is_created_with_the_decided_permissions(session: Session) -> None:
    before = now()

    record_id = create_own_content_rights(session, holder=HOLDER, operator=OPERATOR)

    record = rights.get_record(session, record_id)
    assert record is not None
    assert record.license_ref == OWN_CONTENT_LICENSE_REF
    assert record.holder == HOLDER
    assert record.display_scope is rights.DisplayScope.ALL
    assert record.display_organization_id is None
    assert record.allows_ai_processing is True
    assert record.allows_commercial_use is True
    assert record.valid_until is None
    assert record.revoked_at is None
    assert record.valid_from <= now()
    assert record.valid_from >= before - timedelta(minutes=1)
    for purpose in rights.Purpose:
        assert rights.is_permitted(session, record_id, purpose)
    assert find_own_content_rights(session, holder=HOLDER) == record_id
    assert own_rows_count(session) == 1


def test_creation_writes_one_audit_entry_that_names_who_what_and_from_when(
    session: Session, connection: Connection
) -> None:
    audit_before = count(connection, "audit_log")

    record_id = create_own_content_rights(session, holder=HOLDER, operator=OPERATOR)

    assert count(connection, "audit_log") == audit_before + 1
    (entry,) = rights_entries(session, record_id)
    assert entry.action == "rights_record.created"
    assert entry.actor == ACTOR
    record = rights.get_record(session, record_id)
    assert record is not None
    data = dict(entry.data)
    assert data["operator"] == OPERATOR
    assert data["holder"] == HOLDER
    assert "valid_from" in data
    assert str(find_key(data, "valid_from")).startswith(str(record.valid_from.year))
    # the three permissions are in the entry, whatever the keys are called
    assert find_key(data, "display_scope") in ("all", rights.DisplayScope.ALL)
    assert find_key(data, "allows_ai_processing") is True
    assert find_key(data, "allows_commercial_use") is True


def test_a_custom_actor_is_the_actor_of_the_audit_entry(session: Session) -> None:
    record_id = create_own_content_rights(
        session, holder=HOLDER, operator=OPERATOR, actor=CUSTOM_ACTOR
    )

    (entry,) = rights_entries(session, record_id)
    assert entry.actor == CUSTOM_ACTOR
    assert dict(entry.data)["operator"] == OPERATOR


@pytest.mark.parametrize("status", ["valid", "revoked", "expired"])
def test_creation_is_refused_when_any_record_with_the_reference_exists(
    session: Session, connection: Connection, status: str
) -> None:
    {"valid": lambda s: own_record(s), "revoked": revoked, "expired": expired}[status](session)
    before = (rights_rows(connection), count(connection, "audit_log"))

    with pytest.raises(OwnContentRightsError):
        create_own_content_rights(session, holder=HOLDER, operator=OPERATOR)

    assert (rights_rows(connection), count(connection, "audit_log")) == before
    usable(session)


def test_creation_is_refused_for_a_second_call(session: Session, connection: Connection) -> None:
    create_own_content_rights(session, holder=HOLDER, operator=OPERATOR)
    before = (rights_rows(connection), count(connection, "audit_log"))

    with pytest.raises(OwnContentRightsError):
        create_own_content_rights(session, holder=HOLDER, operator=OPERATOR)

    assert (rights_rows(connection), count(connection, "audit_log")) == before


@pytest.mark.parametrize("operator", ["Jane Doe", "a@b.c", "", "system:pilot_import"])
def test_an_operator_that_is_not_an_account_identifier_is_refused(
    session: Session, connection: Connection, operator: str
) -> None:
    before = (rights_rows(connection), count(connection, "audit_log"))

    with pytest.raises(ValueError):  # noqa: PT011  # the contract names the type only
        create_own_content_rights(session, holder=HOLDER, operator=operator)

    assert (rights_rows(connection), count(connection, "audit_log")) == before
    assert own_rows_count(session) == 0
    usable(session)


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
    assert report.blocked == []
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
        written = audit_for(session, latest(session, question.source_ref).id)
        assert [e.action for e in written] == ["question_version.created"]
        assert written[0].actor == ACTOR
        assert question.source_ref in data_text(written[0])


def test_the_import_never_moves_a_version_beyond_draft_or_opens_a_revision(
    session: Session, connection: Connection, env: Env
) -> None:
    pilot = file_a()

    run(session, env, [pilot])
    run(session, env, [pilot])
    run(session, env, [changed_a(0)])

    statuses = connection.execute(text("SELECT DISTINCT status FROM question_version")).all()
    assert [row[0] for row in statuses] == ["draft"]
    assert count(connection, "question_version") == len(pilot.questions)
    actions = connection.execute(text("SELECT DISTINCT action FROM audit_log")).all()
    assert {row[0] for row in actions} <= {
        "question_version.created",
        "question_version.updated",
        COMPLETED,
    }


def test_counts_and_summary_have_the_five_counts(session: Session, env: Env) -> None:
    report = run(session, env, [file_a()])

    assert report.counts() == {
        "created": 3,
        "updated": 0,
        "unchanged": 0,
        "skipped": 0,
        "blocked": 0,
    }
    assert list(report.counts()) == list(COUNT_NAMES)
    for name in COUNT_NAMES:
        assert re.search(rf"{name}\D*\d+", report.summary())
    again = run(session, env, [file_a()])
    assert again.counts()["unchanged"] == 3 and again.counts()["created"] == 0


def test_an_empty_report_has_five_zeros() -> None:
    report = LoadReport()

    assert report.counts() == dict.fromkeys(COUNT_NAMES, 0)
    assert report.summary().count("0") >= 5


def test_the_counts_follow_every_bucket() -> None:
    report = LoadReport(
        created=["a", "b"],
        updated=["c"],
        unchanged=["d", "e", "f"],
        skipped={"g": "in_review", "h": "edited"},
        blocked=["i"],
    )

    assert report.counts() == {
        "created": 2,
        "updated": 1,
        "unchanged": 3,
        "skipped": 2,
        "blocked": 1,
    }
    numbers = {name: int(n) for name, n in re.findall(r"([a-z]+)\D*?(\d+)", report.summary())}
    assert numbers == report.counts()


def test_two_files_in_one_call_are_reported_in_order(session: Session, env: Env) -> None:
    first, second = file_a(), file_b()

    report = run(session, env, [first, second])

    assert report.created == refs(first) + refs(second)
    assert report.counts()["created"] == 5


def test_a_custom_actor_is_used_for_questions_and_versions(session: Session, env: Env) -> None:
    pilot = file_a()

    run(session, env, [pilot], actor=CUSTOM_ACTOR)

    key = pilot.questions[0].source_ref
    assert question_of(session, key).created_by == CUSTOM_ACTOR
    version = latest(session, key)
    assert version.created_by == CUSTOM_ACTOR
    assert [e.actor for e in audit_for(session, version.id)] == [CUSTOM_ACTOR]


def test_a_custom_actor_that_ran_the_import_before_can_update_its_own_drafts(
    session: Session, env: Env
) -> None:
    run(session, env, [file_a()], actor=CUSTOM_ACTOR)

    report = run(session, env, [changed_a(1)], actor=CUSTOM_ACTOR)

    assert report.updated == [file_a().questions[1].source_ref]


def test_a_given_rights_record_that_does_not_permit_display_stops_a_new_import(
    session: Session, connection: Connection, env: Env
) -> None:
    revoked_record = new_rights(session, revoked=True)
    counts = table_counts(connection)

    with pytest.raises(rights.RightsDenied):
        load_pilot(
            session,
            [file_a()],
            rights_record_id=revoked_record,
            syllabus_version_id=env.syllabus_version_id,
            operator=OPERATOR,
        )

    assert svc.find_question_by_source_ref(session, file_a().questions[0].source_ref) is None
    assert completed(session) == []
    usable(session)
    assert table_counts(connection) == counts


# =============================================================================================
# load_pilot: running it again
# =============================================================================================


def test_a_second_load_of_identical_files_changes_nothing_but_the_run_record(
    session: Session, connection: Connection, env: Env
) -> None:
    files = [file_a(), file_b()]
    first = run(session, env, files)
    keys = first.created
    before = [own_rows(session, connection, k) for k in keys]
    totals = table_counts(connection)

    second = run(session, env, [file_a(), file_b()])

    assert second.unchanged == keys
    assert second.created == [] and second.updated == []
    assert second.skipped == {} and second.blocked == []
    assert [own_rows(session, connection, k) for k in keys] == before
    after = table_counts(connection)
    assert after["audit_log"] == totals["audit_log"] + 1  # the run record, nothing else
    assert {k: v for k, v in after.items() if k != "audit_log"} == {
        k: v for k, v in totals.items() if k != "audit_log"
    }


def test_the_source_hash_of_the_file_does_not_make_a_question_changed(
    session: Session, env: Env
) -> None:
    run(session, env, [file_a(SHA)])

    report = run(session, env, [file_a(SHA_OTHER)])

    assert report.unchanged == refs(file_a())
    assert report.updated == []


def test_a_load_with_new_questions_creates_only_the_missing_ones(
    session: Session, env: Env
) -> None:
    run(session, env, [file_a()])

    report = run(session, env, [file_a(), file_b()])

    assert report.unchanged == refs(file_a())
    assert report.created == refs(file_b())


# =============================================================================================
# load_pilot: changed content of an untouched draft
# =============================================================================================


def test_changed_content_of_an_untouched_draft_is_updated_in_place(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1)
    key = pilot.questions[1].source_ref
    others = [r for r in refs(pilot) if r != key]
    before_version = latest(session, key)
    before_question = question_of(session, key)
    before_others = [own_rows(session, connection, k) for k in others]

    report = run(session, env, [pilot])

    assert report.updated == [key]
    assert report.unchanged == others
    assert report.created == [] and report.skipped == {} and report.blocked == []
    assert question_of(session, key).id == before_question.id
    stored = versions(session, key)
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
    version = latest(session, pilot.questions[0].source_ref)

    run(session, env, [pilot])

    written = audit_for(session, version.id)
    assert [e.action for e in written] == ["question_version.created", "question_version.updated"]
    assert [e.actor for e in written] == [ACTOR, ACTOR]
    assert svc.content_sha256(pilot.questions[0].document) in data_text(written[1])


def test_the_importers_own_last_write_counts_so_a_second_change_updates_again(
    session: Session, env: Env
) -> None:
    run(session, env, [file_a()])
    key = file_a().questions[1].source_ref
    first_change = changed_a(1, "First wording.")
    second_change = changed_a(1, "Second wording.")

    one = run(session, env, [first_change])
    two = run(session, env, [second_change])
    three = run(session, env, [file_a()])

    assert one.updated == [key]
    assert two.updated == [key]
    assert three.updated == [key]
    assert latest(session, key).document == file_a().questions[1].document
    assert len(versions(session, key)) == 1
    written = audit_actions(session, latest(session, key).id)
    assert written == ["question_version.created"] + ["question_version.updated"] * 3


def test_an_update_followed_by_an_identical_load_is_unchanged(session: Session, env: Env) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1)
    run(session, env, [pilot])

    report = run(session, env, [pilot])

    assert report.unchanged == refs(pilot)
    assert report.updated == []


# =============================================================================================
# load_pilot: a human edit is never overwritten
# =============================================================================================


def edit_as_human(session: Session, key: str, sentence: str = "An editor's sentence.") -> str:
    """Change the imported draft as somebody else; returns the new hash."""
    version = latest(session, key)
    doc = document(revised(version.document.model_dump(mode="json"), sentence))
    svc.update_draft(session, actor=EDITOR, version_id=version.id, document=doc)
    return latest(session, key).content_sha256


def test_a_draft_edited_by_someone_else_is_skipped_as_edited_and_left_as_it_is(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1, "A wording from the file.")
    key = pilot.questions[1].source_ref
    edited_hash = edit_as_human(session, key)
    version = latest(session, key)
    before = own_rows(session, connection, key)
    audit_before = audit_actions(session, version.id)
    assert edited_hash != svc.content_sha256(pilot.questions[1].document)

    report = run(session, env, [pilot])

    assert report.skipped == {key: "edited"}
    assert key not in report.updated + report.created + report.unchanged + report.blocked
    stored = latest(session, key)
    assert stored.id == version.id
    assert stored.content_sha256 == edited_hash
    assert stored.document.model_dump(mode="json") == version.document.model_dump(mode="json")
    assert own_rows(session, connection, key) == before
    assert audit_actions(session, version.id) == audit_before  # nothing was written to the version
    assert len(versions(session, key)) == 1


def test_a_skipped_edit_stays_skipped_on_every_later_run(session: Session, env: Env) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1, "A wording from the file.")
    key = pilot.questions[1].source_ref
    edit_as_human(session, key)

    for _ in range(3):
        assert run(session, env, [pilot]).skipped == {key: "edited"}


def test_an_edited_draft_whose_content_now_equals_the_file_is_unchanged(
    session: Session, env: Env
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1, "Agreed wording.")
    key = pilot.questions[1].source_ref
    edit_as_human(session, key, "Agreed wording.")
    assert latest(session, key).content_sha256 == svc.content_sha256(pilot.questions[1].document)

    report = run(session, env, [pilot])

    assert report.unchanged == refs(pilot)
    assert report.skipped == {}


def test_an_edit_after_an_importer_update_is_protected_too(session: Session, env: Env) -> None:
    run(session, env, [file_a()])
    key = file_a().questions[1].source_ref
    run(session, env, [changed_a(1, "First wording.")])
    edit_as_human(session, key)

    report = run(session, env, [changed_a(1, "Second wording.")])

    assert report.skipped == {key: "edited"}


def test_restoring_the_exact_imported_text_makes_the_draft_importable_again(
    session: Session, env: Env
) -> None:
    # This is the literal rule: "edited" means the stored hash differs from the hash the importer
    # last wrote. An editor who puts back exactly the imported content leaves nothing to protect,
    # so a later change of the file is applied.
    run(session, env, [file_a()])
    key = file_a().questions[1].source_ref
    version = latest(session, key)
    edit_as_human(session, key)
    svc.update_draft(
        session, actor=EDITOR, version_id=version.id, document=file_a().questions[1].document
    )
    assert latest(session, key).content_sha256 == version.content_sha256

    report = run(session, env, [changed_a(1, "A wording from the file.")])

    assert report.updated == [key]
    assert report.skipped == {}


def test_other_questions_in_the_file_are_still_handled_when_one_was_edited(
    session: Session, env: Env
) -> None:
    run(session, env, [file_a()])
    docs = [revised(make(), "From the file.") for make in SET_A]
    pilot = pilot_file("demo-set", docs)
    edited_key = pilot.questions[0].source_ref
    edit_as_human(session, edited_key)

    report = run(session, env, [pilot])

    assert report.skipped == {edited_key: "edited"}
    assert report.updated == refs(pilot)[1:]


def test_a_revision_opened_by_an_editor_on_a_published_question_is_skipped_as_edited(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(0, "A wording from the file.")
    key = pilot.questions[0].source_ref
    first = latest(session, key)
    advance(session, connection, first.id, "published")
    revision = svc.start_revision(session, actor=EDITOR, question_id=first.question_id)
    question_id = question_of(session, key).id
    before = snapshot(session, connection, question_id)[:-1]
    audit_before = audit_actions(session, revision.id)

    report = run(session, env, [pilot])

    assert report.skipped == {key: "edited"}
    assert snapshot(session, connection, question_id)[:-1] == before
    assert audit_actions(session, revision.id) == audit_before
    stored = versions(session, key)
    assert [v.version_no for v in stored] == [1, 2]
    assert stored[0].status is svc.VersionStatus.PUBLISHED
    assert stored[1].status is svc.VersionStatus.DRAFT
    assert stored[1].content_sha256 == first.content_sha256


def test_a_revision_whose_content_equals_the_file_is_unchanged(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    key = file_a().questions[0].source_ref
    first = latest(session, key)
    advance(session, connection, first.id, "published")
    svc.start_revision(session, actor=EDITOR, question_id=first.question_id)

    report = run(session, env, [file_a()])

    assert report.unchanged == refs(file_a())
    assert report.skipped == {}


def test_a_version_that_needs_fixing_is_skipped_under_its_status_and_stays_there(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1)
    key = pilot.questions[1].source_ref
    advance(session, connection, latest(session, key).id, "needs_fix")
    question_id = question_of(session, key).id
    before = snapshot(session, connection, question_id)[:-1]

    report = run(session, env, [pilot])

    assert report.skipped == {key: "needs_fix"}
    assert report.updated == []
    assert latest(session, key).status is svc.VersionStatus.NEEDS_FIX
    assert snapshot(session, connection, question_id)[:-1] == before


def test_a_version_sent_back_by_a_reviewer_is_skipped_as_needs_fix_too(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1)
    key = pilot.questions[1].source_ref
    advance(session, connection, latest(session, key).id, "in_review")
    svc.request_changes(
        session, actor=REVIEWER, version_id=latest(session, key).id, reason="reword the stem"
    )
    assert latest(session, key).status is svc.VersionStatus.NEEDS_FIX

    report = run(session, env, [pilot])

    assert report.skipped == {key: "needs_fix"}
    assert latest(session, key).status is svc.VersionStatus.NEEDS_FIX
    assert latest(session, key).document == file_a().questions[1].document


def test_unchanged_content_of_a_version_that_needs_fixing_is_left_alone(
    session: Session, connection: Connection, env: Env
) -> None:
    run(session, env, [file_a()])
    key = file_a().questions[0].source_ref
    advance(session, connection, latest(session, key).id, "needs_fix")
    before = own_rows(session, connection, key)

    report = run(session, env, [file_a()])

    assert key in report.unchanged
    assert report.skipped == {}
    assert own_rows(session, connection, key) == before
    assert latest(session, key).status is svc.VersionStatus.NEEDS_FIX


LOCKED = ["auto_checking", "in_review", "approved", "published", "withdrawn", "rejected"]


@pytest.mark.parametrize("status", LOCKED)
def test_changed_content_of_a_version_past_editing_is_skipped_under_its_status(
    session: Session, connection: Connection, env: Env, status: str
) -> None:
    run(session, env, [file_a()])
    pilot = changed_a(1)
    key = pilot.questions[1].source_ref
    advance(session, connection, latest(session, key).id, status)
    question_id = question_of(session, key).id
    before = snapshot(session, connection, question_id)
    audit_before = audit_actions(session, latest(session, key).id)

    report = run(session, env, [pilot])

    assert report.skipped == {key: status}
    assert key not in report.updated + report.created + report.unchanged + report.blocked
    after = snapshot(session, connection, question_id)
    assert after[:-1] == before[:-1]
    assert audit_actions(session, latest(session, key).id) == audit_before
    assert len(svc.list_versions(session, question_id)) == 1  # no revision was opened
    assert latest(session, key).status.value == status
    assert sorted(report.unchanged) == sorted(r for r in refs(pilot) if r != key)


@pytest.mark.parametrize("status", ["needs_fix", *LOCKED])
def test_unchanged_content_in_any_status_is_unchanged_not_skipped(
    session: Session, connection: Connection, env: Env, status: str
) -> None:
    run(session, env, [file_a()])
    key = file_a().questions[1].source_ref
    advance(session, connection, latest(session, key).id, status)
    before = own_rows(session, connection, key)

    report = run(session, env, [file_a()])

    assert report.skipped == {}
    assert report.unchanged == refs(file_a())
    assert own_rows(session, connection, key) == before


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


# =============================================================================================
# load_pilot: blocked
# =============================================================================================


def imported_then_blocked(session: Session, env: Env) -> tuple[uuid.UUID, uuid.UUID]:
    """Import under the env's record, revoke it, and return (revoked record, a valid other one)."""
    run(session, env, [file_a()])
    rights.revoke(session, env.rights_record_id, at=now())
    return env.rights_record_id, new_rights(session)


def test_a_question_whose_rights_do_not_permit_display_is_blocked_not_duplicated(
    session: Session, connection: Connection, env: Env
) -> None:
    _, other = imported_then_blocked(session, env)
    totals = table_counts(connection)

    report = load_pilot(
        session,
        [file_a()],
        rights_record_id=other,
        syllabus_version_id=env.syllabus_version_id,
        operator=OPERATOR,
    )

    assert report.blocked == refs(file_a())
    assert report.created == [] and report.updated == []
    assert report.unchanged == [] and report.skipped == {}
    after = table_counts(connection)
    assert {k: v for k, v in after.items() if k != "audit_log"} == {
        k: v for k, v in totals.items() if k != "audit_log"
    }
    assert report.counts()["blocked"] == 3
    assert re.search(r"blocked\D*3", report.summary())
    usable(session)


def test_a_blocked_question_is_blocked_whether_or_not_its_content_changed(
    session: Session, env: Env
) -> None:
    _, other = imported_then_blocked(session, env)

    report = load_pilot(
        session,
        [changed_a(1)],
        rights_record_id=other,
        syllabus_version_id=env.syllabus_version_id,
        operator=OPERATOR,
    )

    assert report.blocked == refs(file_a())
    assert report.updated == []


def test_blocked_questions_do_not_stop_new_ones_from_being_created(
    session: Session, env: Env
) -> None:
    _, other = imported_then_blocked(session, env)

    report = load_pilot(
        session,
        [file_a(), file_b()],
        rights_record_id=other,
        syllabus_version_id=env.syllabus_version_id,
        operator=OPERATOR,
    )

    assert report.blocked == refs(file_a())
    assert report.created == refs(file_b())
    for key in refs(file_b()):
        assert question_of(session, key).rights_record_id == other


def test_a_blocked_question_does_not_come_back_through_the_lookup(
    session: Session, env: Env
) -> None:
    imported_then_blocked(session, env)

    assert svc.find_question_by_source_ref(session, file_a().questions[0].source_ref) is None


# =============================================================================================
# load_pilot: run audit
# =============================================================================================


def test_every_run_ends_with_one_completed_entry_for_the_operator(
    session: Session, connection: Connection, env: Env
) -> None:
    first, second = file_a(SHA), file_b(SHA_OTHER)
    audit_before = count(connection, "audit_log")

    report = run(session, env, [first, second])

    written = completed(session)
    assert [e.action for e in written] == [COMPLETED]
    entry = written[0]
    assert entry.entity_type == "pilot_import"
    assert entry.entity_id == OPERATOR
    assert entry.actor == ACTOR
    assert count(connection, "audit_log") == audit_before + report.counts()["created"] + 1
    data = dict(entry.data)
    assert data["operator"] == OPERATOR
    for name in COUNT_NAMES:
        assert find_key(data, name) == report.counts()[name], name
    text_form = data_text(entry)
    assert first.source_file in text_form and SHA in text_form
    assert second.source_file in text_form and SHA_OTHER in text_form


def test_an_all_unchanged_run_is_recorded_too(session: Session, env: Env) -> None:
    run(session, env, [file_a()])

    report = run(session, env, [file_a()])

    written = completed(session)
    assert [e.action for e in written] == [COMPLETED, COMPLETED]
    last = dict(written[-1].data)
    assert find_key(last, "unchanged") == 3 == report.counts()["unchanged"]
    assert find_key(last, "created") == 0


def test_skipped_and_blocked_counts_are_in_the_run_record(session: Session, env: Env) -> None:
    run(session, env, [file_a()])
    key = file_a().questions[1].source_ref
    edit_as_human(session, key)

    report = run(session, env, [changed_a(1, "From the file.")])

    assert report.counts()["skipped"] == 1
    last = dict(completed(session)[-1].data)
    assert find_key(last, "skipped") == 1
    assert find_key(last, "blocked") == 0


def test_runs_of_different_operators_are_kept_apart(session: Session, env: Env) -> None:
    run(session, env, [file_a()], operator="u_first")
    run(session, env, [file_a()], operator="u_second")

    assert len(completed(session, "u_first")) == 1
    assert len(completed(session, "u_second")) == 1
    assert completed(session, OPERATOR) == []


def test_no_run_record_is_written_when_the_call_raises(session: Session, env: Env) -> None:
    nested = session.begin_nested()
    with pytest.raises(svc.InvalidDocument):
        run(session, env, [file_a(), broken_file()])

    assert completed(session) == []  # even before the caller rolls back
    nested.rollback()
    assert completed(session) == []


@pytest.mark.parametrize("operator", ["Jane Doe", "a@b.c", ""])
def test_an_invalid_operator_is_refused_before_anything_is_written(
    session: Session, connection: Connection, env: Env, operator: str
) -> None:
    counts = table_counts(connection)

    with pytest.raises(ValueError):  # noqa: PT011
        run(session, env, [file_a()], operator=operator)

    assert table_counts(connection) == counts
    assert svc.find_question_by_source_ref(session, file_a().questions[0].source_ref) is None
    usable(session)


def test_the_same_key_in_two_files_is_refused_before_anything_is_written(
    session: Session, connection: Connection, env: Env
) -> None:
    counts = table_counts(connection)

    with pytest.raises(ValueError):  # noqa: PT011
        run(session, env, [file_a(), file_a(SHA_OTHER)])

    assert table_counts(connection) == counts
    assert completed(session) == []
    for key in refs(file_a()):
        assert svc.find_question_by_source_ref(session, key) is None
    usable(session)


# =============================================================================================
# load_pilot: errors propagate; the caller's transaction decides
# =============================================================================================


def test_an_invalid_document_raises_and_the_caller_can_roll_everything_back(
    session: Session, connection: Connection, env: Env
) -> None:
    pilot = broken_file()
    counts = table_counts(connection)

    nested = session.begin_nested()
    with pytest.raises(svc.InvalidDocument):
        run(session, env, [file_a(), pilot])
    nested.rollback()

    assert table_counts(connection) == counts
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


def test_the_invalid_document_error_names_the_problem(session: Session, env: Env) -> None:
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


def test_files_are_read_sorted_by_name(tmp_path: Path) -> None:
    later = pilot_file("zz-set", [samples.plain_mcq_document()])
    middle = file_b()
    earlier = file_a()
    for pilot in (later, earlier, middle):
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
# verify_sources
# =============================================================================================


def test_sources_whose_hashes_match_pass(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)

    verify_sources(repo.root, repo.files)  # returns normally


def test_a_missing_markdown_file_is_a_mismatch(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    repo.markdown(repo.files[0]).unlink()

    with pytest.raises(SourceMismatch):
        verify_sources(repo.root, repo.files)


def test_one_appended_byte_is_a_mismatch(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    with repo.markdown(repo.files[0]).open("ab") as handle:
        handle.write(b" ")

    with pytest.raises(SourceMismatch):
        verify_sources(repo.root, repo.files)


def test_a_mismatch_in_the_second_file_is_found(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    with repo.markdown(repo.files[1]).open("ab") as handle:
        handle.write(b"\n")

    with pytest.raises(SourceMismatch):
        verify_sources(repo.root, repo.files)


def test_a_missing_second_markdown_file_is_found(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    repo.markdown(repo.files[1]).unlink()

    with pytest.raises(SourceMismatch):
        verify_sources(repo.root, repo.files)


def test_a_json_with_the_wrong_hash_is_a_mismatch(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    stale = pilot_file("demo-set", [make() for make in SET_A], SHA)

    with pytest.raises(SourceMismatch):
        verify_sources(repo.root, [stale, repo.files[1]])


def test_the_markdown_is_looked_up_under_the_given_root(tmp_path: Path) -> None:
    repo = build_repo(tmp_path, name="one")
    other = build_repo(tmp_path, [("demo-set", [make for make in SET_A[:1]])], name="two")
    (other.root / "docs" / "pilot" / "demo-set-pilot-questions.md").write_text(
        "different text\n", encoding="utf-8"
    )

    verify_sources(repo.root, repo.files)
    with pytest.raises(SourceMismatch):
        verify_sources(other.root, repo.files[:1])


def test_an_empty_list_of_files_passes(tmp_path: Path) -> None:
    verify_sources(tmp_path, [])  # returns normally


# =============================================================================================
# load_pilot_directory
# =============================================================================================


def directory_load(session: Session, repo: Repo, **kwargs: Any) -> LoadReport:
    kwargs.setdefault("holder", HOLDER)
    kwargs.setdefault("operator", OPERATOR)
    return load_pilot_directory(session, repo.root, **kwargs)


def nothing_written(connection: Connection, before: dict[str, int], rights_before: int) -> None:
    assert table_counts(connection) == before
    assert rights_rows(connection) == rights_before


def test_the_pilot_syllabus_names_the_reference_that_is_shipped() -> None:
    assert PILOT_SYLLABUS == {"program": "ib_dp", "subject": "physics", "version": "2025"}


def test_without_a_rights_record_and_without_permission_to_create_one_nothing_happens(
    session: Session, connection: Connection, tmp_path: Path
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    before = table_counts(connection)
    rights_before = rights_rows(connection)

    with pytest.raises(OwnContentRightsError):
        directory_load(session, repo)
    with pytest.raises(OwnContentRightsError):
        directory_load(session, repo, create_rights=False)

    nothing_written(connection, before, rights_before)
    assert own_rows_count(session) == 0
    usable(session)


def test_with_permission_the_record_is_created_and_the_import_is_done(
    session: Session, tmp_path: Path
) -> None:
    syllabus_id = load_syllabus(session)
    repo = build_repo(tmp_path)

    report = directory_load(session, repo, create_rights=True)

    first, second = repo.files
    assert report.created == refs(first) + refs(second)  # files by name: demo-set, other-set
    (record,) = rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)
    assert record.holder == HOLDER
    assert record.display_scope is rights.DisplayScope.ALL
    assert record.allows_ai_processing and record.allows_commercial_use
    (created,) = rights_entries(session, record.id)
    assert created.action == "rights_record.created"
    assert dict(created.data)["operator"] == OPERATOR
    for key in report.created:
        found = question_of(session, key)
        assert found.rights_record_id == record.id
        assert found.syllabus_version_id == syllabus_id
        assert found.created_by == ACTOR
        assert latest(session, key).status is svc.VersionStatus.DRAFT
    (run_entry,) = completed(session)
    assert run_entry.action == COMPLETED
    for pilot in repo.files:
        assert pilot.source_file in data_text(run_entry)
        assert pilot.source_sha256 in data_text(run_entry)


def test_an_existing_matching_record_is_used_without_permission_to_create(
    session: Session, connection: Connection, tmp_path: Path
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    existing = create_own_content_rights(session, holder=HOLDER, operator=OPERATOR)
    audit_before = count(connection, "audit_log")

    report = directory_load(session, repo)

    assert report.created == refs(repo.files[0]) + refs(repo.files[1])
    assert own_rows_count(session) == 1
    for key in report.created:
        assert question_of(session, key).rights_record_id == existing
    assert count(connection, "audit_log") == audit_before + 5 + 1  # questions + run record
    assert rights_entries(session, existing)[0].action == "rights_record.created"
    assert len(rights_entries(session, existing)) == 1


def test_an_existing_record_is_not_duplicated_when_permission_to_create_is_given(
    session: Session, tmp_path: Path
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    existing = create_own_content_rights(session, holder=HOLDER, operator=OPERATOR)

    directory_load(session, repo, create_rights=True)

    assert [r.id for r in rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)] == [
        existing
    ]
    assert len(rights_entries(session, existing)) == 1


@pytest.mark.parametrize("create_rights", [False, True])
def test_a_revoked_record_stops_the_import_and_no_new_record_is_opened(
    session: Session, connection: Connection, tmp_path: Path, create_rights: bool
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    old = create_own_content_rights(session, holder=HOLDER, operator=OPERATOR)
    rights.revoke(session, old, at=now())
    before = table_counts(connection)
    rights_before = rights_rows(connection)

    with pytest.raises(OwnContentRightsError):
        directory_load(session, repo, create_rights=create_rights)

    nothing_written(connection, before, rights_before)
    assert [r.id for r in rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)] == [old]
    usable(session)


@pytest.mark.parametrize("create_rights", [False, True])
def test_a_wrong_record_stops_the_import_in_both_modes(
    session: Session, connection: Connection, tmp_path: Path, create_rights: bool
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    own_record(session, holder="Somebody else")
    before = table_counts(connection)
    rights_before = rights_rows(connection)

    with pytest.raises(OwnContentRightsError):
        directory_load(session, repo, create_rights=create_rights)

    nothing_written(connection, before, rights_before)


def test_the_holder_given_must_be_the_holder_of_the_existing_record(
    session: Session, tmp_path: Path
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    create_own_content_rights(session, holder=HOLDER, operator=OPERATOR)

    with pytest.raises(OwnContentRightsError):
        directory_load(session, repo, holder="Another holder")


@pytest.mark.parametrize("create_rights", [False, True])
def test_a_stale_json_is_refused_before_anything_is_written(
    session: Session, connection: Connection, tmp_path: Path, create_rights: bool
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    with repo.markdown(repo.files[1]).open("ab") as handle:
        handle.write(b" ")
    before = table_counts(connection)
    rights_before = rights_rows(connection)

    with pytest.raises(SourceMismatch):
        directory_load(session, repo, create_rights=create_rights)

    nothing_written(connection, before, rights_before)
    assert own_rows_count(session) == 0
    assert completed(session) == []
    usable(session)


def test_a_missing_markdown_file_refuses_the_import(
    session: Session, connection: Connection, tmp_path: Path
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    repo.markdown(repo.files[0]).unlink()
    before = table_counts(connection)

    with pytest.raises(SourceMismatch):
        directory_load(session, repo, create_rights=True)

    nothing_written(connection, before, 0)


@pytest.mark.parametrize("create_rights", [False, True])
def test_without_the_pilot_syllabus_loaded_the_import_raises_lookup_error(
    session: Session, connection: Connection, tmp_path: Path, create_rights: bool
) -> None:
    repo = build_repo(tmp_path)
    before = table_counts(connection)

    with pytest.raises(LookupError):
        directory_load(session, repo, create_rights=create_rights)

    nothing_written(connection, before, 0)
    assert own_rows_count(session) == 0
    usable(session)


def test_an_empty_json_directory_raises_even_when_everything_else_is_ready(
    session: Session, tmp_path: Path
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path, [])

    with pytest.raises(FileNotFoundError):
        directory_load(session, repo, create_rights=True)

    assert own_rows_count(session) == 0


def test_an_invalid_operator_writes_nothing_in_the_directory_load(
    session: Session, connection: Connection, tmp_path: Path
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    before = table_counts(connection)

    with pytest.raises(ValueError):  # noqa: PT011
        directory_load(session, repo, create_rights=True, operator="Jane Doe")

    nothing_written(connection, before, 0)
    assert own_rows_count(session) == 0


def test_running_the_directory_load_again_is_a_no_op_but_for_the_run_record(
    session: Session, connection: Connection, tmp_path: Path
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    directory_load(session, repo, create_rights=True)
    totals = table_counts(connection)

    report = directory_load(session, repo)

    assert report.created == [] and report.updated == []
    assert report.skipped == {} and report.blocked == []
    assert report.unchanged == refs(repo.files[0]) + refs(repo.files[1])
    after = table_counts(connection)
    assert after["audit_log"] == totals["audit_log"] + 1
    assert {k: v for k, v in after.items() if k != "audit_log"} == {
        k: v for k, v in totals.items() if k != "audit_log"
    }
    assert own_rows_count(session) == 1
    assert len(completed(session)) == 2


def test_a_changed_json_with_a_matching_markdown_updates_an_untouched_draft(
    session: Session, tmp_path: Path
) -> None:
    load_syllabus(session)
    repo = build_repo(tmp_path)
    directory_load(session, repo, create_rights=True)
    write(
        repo.json_dir,
        changed_a(1).model_copy(update={"source_sha256": repo.files[0].source_sha256}),
    )

    report = directory_load(session, repo)

    assert report.updated == [repo.files[0].questions[1].source_ref]


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

    report = load_pilot_directory(
        session, REPO_ROOT, holder="Test holder", operator=OPERATOR, create_rights=True
    )

    assert len(expected) == 130
    assert len(report.created) == 130
    assert report.updated == [] and report.unchanged == []
    assert report.skipped == {} and report.blocked == []
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
    assert own_rows_count(session) == 1
    (run_entry,) = completed(session)
    assert len(dict(run_entry.data)) > 0


def test_loading_the_committed_pilot_files_twice_reports_130_unchanged(
    session: Session, connection: Connection
) -> None:
    load_syllabus(session)
    load_pilot_directory(
        session, REPO_ROOT, holder="Test holder", operator=OPERATOR, create_rights=True
    )

    second = load_pilot_directory(session, REPO_ROOT, holder="Test holder", operator=OPERATOR)

    assert len(second.unchanged) == 130
    assert second.created == [] and second.updated == []
    assert second.skipped == {} and second.blocked == []
    assert second.counts() == {
        "created": 0,
        "updated": 0,
        "unchanged": 130,
        "skipped": 0,
        "blocked": 0,
    }
    assert count(connection, "question") == 130
    assert count(connection, "question_version") == 130


# =============================================================================================
# The `load` command
# =============================================================================================

CLI_ENV = "QLAB_DATABASE_URL"


def make_cli_database(
    engine: Engine, monkeypatch: pytest.MonkeyPatch, *, syllabus: bool
) -> Iterator[Engine]:
    """A database of its own (the command opens its own engine and commits), migrated, with the
    syllabus reference committed unless `syllabus` is false; created here and dropped afterwards."""
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
        if syllabus:
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


@pytest.fixture
def cli_engine(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> Iterator[Engine]:
    yield from make_cli_database(engine, monkeypatch, syllabus=True)


@pytest.fixture
def cli_engine_without_syllabus(
    engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Engine]:
    yield from make_cli_database(engine, monkeypatch, syllabus=False)


def scalar(engine: Engine, sql: str) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql)).scalar_one())


def nothing_in(engine: Engine) -> None:
    for table in ("question", "question_version", "rights_record", "audit_log"):
        assert scalar(engine, f"SELECT count(*) FROM {table}") == 0, table  # noqa: S608


def load_args(root: Path, *extra: str, operator: str | None = OPERATOR) -> list[str]:
    args = ["load", "--root", str(root)]
    if operator is not None:
        args += ["--operator", operator]
    return args + list(extra)


def test_the_parser_knows_the_load_options() -> None:
    parsed = cli.build_parser().parse_args(
        [
            "load",
            "--root",
            "/somewhere",
            "--holder",
            "Name",
            "--operator",
            "u_op",
            "--create-rights",
            "--dry-run",
        ]
    )

    assert parsed.command == "load"
    assert parsed.root == Path("/somewhere")
    assert parsed.holder == "Name"
    assert parsed.operator == "u_op"
    assert parsed.create_rights is True
    assert parsed.dry_run is True
    defaults = cli.build_parser().parse_args(["load", "--operator", "u_op"])
    assert defaults.dry_run is False
    assert defaults.create_rights is False
    assert defaults.root is None
    assert defaults.holder


def test_the_operator_is_required(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        cli.build_parser().parse_args(["load"])
    assert caught.value.code == 2
    assert "--operator" in capsys.readouterr().err


def test_main_without_an_operator_is_an_argument_error_and_touches_no_database(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(CLI_ENV, raising=False)
    repo = build_repo(tmp_path)

    with pytest.raises(SystemExit) as caught:
        cli.main(load_args(repo.root, operator=None))

    assert caught.value.code == 2
    assert "--operator" in capsys.readouterr().err


def test_without_permission_to_create_the_rights_record_the_command_refuses(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)

    status = cli.main(load_args(repo.root))

    assert status == 2
    captured = capsys.readouterr()
    assert captured.err.startswith("import refused:")
    assert "import refused" not in captured.out
    nothing_in(cli_engine)


def test_with_permission_the_command_creates_the_record_and_imports(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)

    status = cli.main(load_args(repo.root, "--create-rights", "--holder", "Command line holder"))

    assert status == 0
    captured = capsys.readouterr()
    assert "created 5" in captured.out
    assert not any(line.startswith("dry run:") for line in captured.out.splitlines())
    assert captured.err == ""
    assert scalar(cli_engine, "SELECT count(*) FROM question") == 5
    assert scalar(cli_engine, "SELECT count(*) FROM question WHERE origin = 'authored'") == 5
    assert scalar(cli_engine, "SELECT count(*) FROM question_version WHERE status = 'draft'") == 5
    assert scalar(cli_engine, "SELECT count(*) FROM question WHERE source_ref LIKE 'pilot/%'") == 5
    with Session(cli_engine) as session:
        (record,) = rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)
        assert record.holder == "Command line holder"
        assert record.display_scope is rights.DisplayScope.ALL
        question = question_of(session, refs(repo.files[0])[0])
        assert question.created_by == ACTOR
        assert question.rights_record_id == record.id
        (run_entry,) = completed(session)
        assert run_entry.action == COMPLETED


def test_an_existing_record_lets_the_command_import_without_permission_to_create(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)
    with Session(cli_engine) as session:
        create_own_content_rights(session, holder="LearningQlab", operator=OPERATOR)
        session.commit()

    status = cli.main(load_args(repo.root))

    assert status == 0
    assert "created 5" in capsys.readouterr().out
    assert scalar(cli_engine, "SELECT count(*) FROM rights_record") == 1


def test_a_dry_run_with_permission_leaves_no_record_and_no_question(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)

    status = cli.main(load_args(repo.root, "--dry-run", "--create-rights"))

    assert status == 0
    out = capsys.readouterr().out
    summaries = [line for line in out.splitlines() if line.startswith("dry run:")]
    assert len(summaries) == 1
    assert "created 5" in summaries[0]
    nothing_in(cli_engine)


def test_a_further_run_reports_everything_unchanged(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)
    assert cli.main(load_args(repo.root, "--create-rights")) == 0
    capsys.readouterr()
    versions_rows = scalar(cli_engine, "SELECT count(*) FROM question_version")

    assert cli.main(load_args(repo.root)) == 0

    out = capsys.readouterr().out
    assert "unchanged 5" in out and "created 0" in out
    assert scalar(cli_engine, "SELECT count(*) FROM question") == 5
    assert scalar(cli_engine, "SELECT count(*) FROM question_version") == versions_rows
    assert scalar(cli_engine, "SELECT count(*) FROM rights_record") == 1
    assert scalar(cli_engine, f"SELECT count(*) FROM audit_log WHERE action = '{COMPLETED}'") == 2  # noqa: S608


def test_a_dry_run_after_a_real_run_changes_nothing_either(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path, [("demo-set", SET_A)])
    cli.main(load_args(repo.root, "--create-rights"))
    capsys.readouterr()
    audit_rows = scalar(cli_engine, "SELECT count(*) FROM audit_log")

    assert cli.main(load_args(repo.root, "--dry-run")) == 0

    out = capsys.readouterr().out
    assert any(line.startswith("dry run:") and "unchanged 3" in line for line in out.splitlines())
    assert scalar(cli_engine, "SELECT count(*) FROM question") == 3
    assert scalar(cli_engine, "SELECT count(*) FROM audit_log") == audit_rows


def test_a_changed_file_is_updated_by_a_later_run(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path, [("demo-set", SET_A)])
    cli.main(load_args(repo.root, "--create-rights"))
    capsys.readouterr()
    write(
        repo.json_dir,
        changed_a(1).model_copy(update={"source_sha256": repo.files[0].source_sha256}),
    )

    assert cli.main(load_args(repo.root)) == 0

    out = capsys.readouterr().out
    assert "updated 1" in out and "unchanged 2" in out
    assert scalar(cli_engine, "SELECT count(*) FROM question_version") == 3


def test_a_skipped_question_is_named_with_its_reason(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path, [("demo-set", SET_A)])
    cli.main(load_args(repo.root, "--create-rights"))
    edited = repo.files[0].questions[0].source_ref
    in_review = repo.files[0].questions[1].source_ref
    with Session(cli_engine) as session:
        edit_as_human(session, edited)
        advance(session, session.connection(), latest(session, in_review).id, "in_review")
        session.commit()
    pilot = pilot_file(
        "demo-set",
        [revised(make(), "From the file.") for make in SET_A],
        repo.files[0].source_sha256,
    )
    write(repo.json_dir, pilot)
    capsys.readouterr()

    assert cli.main(load_args(repo.root)) == 0

    out = capsys.readouterr().out
    lines = out.splitlines()
    assert any(edited in line and "edited" in line for line in lines), out
    assert any(in_review in line and "in_review" in line for line in lines), out
    assert "skipped 2" in out and "updated 1" in out


def test_a_blocked_question_is_named_with_its_reason(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path, [("demo-set", SET_A)])
    blocked_key = repo.files[0].questions[0].source_ref
    with Session(cli_engine) as session:
        other = new_rights(session)
        svc.create_question(
            session,
            actor=AUTHOR,
            document=repo.files[0].questions[0].document,
            rights_record_id=other,
            syllabus_version_id=find_syllabus(session),
            source_ref=blocked_key,
        )
        rights.revoke(session, other, at=now())
        session.commit()

    status = cli.main(load_args(repo.root, "--create-rights"))

    assert status == 0
    out = capsys.readouterr().out
    assert any(blocked_key in line and "blocked" in line.lower() for line in out.splitlines()), out
    assert "blocked 1" in out and "created 2" in out
    assert scalar(cli_engine, "SELECT count(*) FROM question") == 3


def find_syllabus(session: Session) -> uuid.UUID:
    value = session.execute(text("SELECT id FROM syllabus_version")).scalar_one()
    assert isinstance(value, uuid.UUID)
    return value


def test_a_stale_json_is_refused_with_code_2(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)
    with repo.markdown(repo.files[0]).open("ab") as handle:
        handle.write(b" ")

    status = cli.main(load_args(repo.root, "--create-rights"))

    assert status == 2
    assert capsys.readouterr().err.startswith("import refused:")
    nothing_in(cli_engine)


def test_a_missing_markdown_file_is_refused_with_code_2(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)
    repo.markdown(repo.files[1]).unlink()

    status = cli.main(load_args(repo.root, "--create-rights"))

    assert status == 2
    assert capsys.readouterr().err.startswith("import refused:")
    nothing_in(cli_engine)


def test_a_database_without_the_syllabus_is_refused_with_code_2(
    cli_engine_without_syllabus: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)

    status = cli.main(load_args(repo.root, "--create-rights"))

    assert status == 2
    assert capsys.readouterr().err.startswith("import refused:")
    nothing_in(cli_engine_without_syllabus)


def test_a_revoked_own_content_record_is_refused_with_code_2_and_not_replaced(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)
    cli.main(load_args(repo.root, "--create-rights"))
    with Session(cli_engine) as session:
        (record,) = rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)
        rights.revoke(session, record.id, at=now())
        session.commit()
    capsys.readouterr()

    status = cli.main(load_args(repo.root, "--create-rights"))

    assert status == 2
    assert capsys.readouterr().err.startswith("import refused:")
    assert scalar(cli_engine, "SELECT count(*) FROM rights_record") == 1
    assert scalar(cli_engine, "SELECT count(*) FROM question") == 5


def test_the_database_line_shows_host_and_name_and_never_the_password(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)
    password = cli_engine.url.password
    assert password

    cli.main(load_args(repo.root, "--create-rights"))
    cli.main(load_args(repo.root))
    captured = capsys.readouterr()

    expected = f"database: {cli_engine.url.host}/{cli_engine.url.database}"
    assert expected in captured.out.splitlines()
    assert password not in captured.out + captured.err


def test_the_database_line_is_also_printed_when_the_import_is_refused(
    cli_engine: Engine, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = build_repo(tmp_path)

    assert cli.main(load_args(repo.root)) == 2

    captured = capsys.readouterr()
    assert f"database: {cli_engine.url.host}/{cli_engine.url.database}" in captured.out
    password = cli_engine.url.password
    assert password
    assert password not in captured.out + captured.err


def test_an_invalid_document_in_a_later_file_leaves_nothing_committed(
    cli_engine: Engine, tmp_path: Path
) -> None:
    repo = build_repo(tmp_path, [("a-first", SET_A), ("broken-set", SET_B[:1])])
    broken = broken_file().model_copy(update={"source_sha256": repo.files[1].source_sha256})
    write(repo.json_dir, broken)

    with pytest.raises(svc.InvalidDocument):
        cli.main(load_args(repo.root, "--create-rights"))

    nothing_in(cli_engine)


def test_without_a_usable_renderer_the_command_fails_before_writing_anything(
    cli_engine: Engine, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = build_repo(tmp_path)
    monkeypatch.setenv("QLAB_NODE_BIN", str(tmp_path / "no-such-node"))

    with pytest.raises(RendererUnavailable):
        cli.main(load_args(repo.root, "--create-rights"))

    nothing_in(cli_engine)


def test_without_a_usable_renderer_a_dry_run_fails_too(
    cli_engine: Engine, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = build_repo(tmp_path)
    monkeypatch.setenv("QLAB_NODE_BIN", str(tmp_path / "no-such-node"))

    with pytest.raises(RendererUnavailable):
        cli.main(load_args(repo.root, "--dry-run", "--create-rights"))

    nothing_in(cli_engine)


def test_a_root_without_converted_files_fails_and_writes_nothing(
    cli_engine: Engine, tmp_path: Path
) -> None:
    repo = build_repo(tmp_path, [])

    with pytest.raises(FileNotFoundError):
        cli.main(load_args(repo.root, "--create-rights"))

    nothing_in(cli_engine)
