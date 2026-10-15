"""Staff flows through HTTP: editing, review decisions, publishing, revisions.

Specification: docs/slices/M1G-5-YETKILER.md sections 1, 2, 5, 6; docs/slices/M1G-5-SOZLESME.md
sections 3.1, 3.2, 3.5, 4; docs/DOMAIN_MODEL.md section 4; CLAUDE.md rules 6 to 9; decisions
D-53, D-55, D-56, D-59. Written without reading the handlers.

Content is seeded through the content service (`tests.content.support`); everything under test
is done through the HTTP API.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from httpx2 import Response
from sqlalchemy import Connection
from sqlalchemy.orm import Session

from qlab.api import ids
from qlab.api.settings import Environment, Settings
from qlab.content import service as svc
from qlab.content.schema import QuestionDocument
from qlab.organizations.service import Role
from tests.api.support import ApiHarness, make_harness
from tests.content import samples
from tests.content.support import (
    AUTHOR,
    NO_HASH,
    Env,
    audit_for,
    bring_to,
    create,
    document,
    failed_critical,
    make_env,
    new_rights,
    now,
    raw_full_version,
    raw_walk,
    snapshot,
    status_of,
    stored_hash,
    with_exam_section,
)

pytestmark = [pytest.mark.db, pytest.mark.node]

STAFF = (Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN)
PUBLISHERS = (Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN)
REASON = "the wording of part a is ambiguous"
STATE_KEYS = {"id", "question_id", "version_no", "status", "content_sha256"}


# --- helpers ---------------------------------------------------------------------------------


def qid(value: uuid.UUID) -> str:
    return ids.encode(ids.QUESTION, value)


def vid(value: uuid.UUID) -> str:
    return ids.encode(ids.QUESTION_VERSION, value)


def vurl(version_id: uuid.UUID, suffix: str = "") -> str:
    return f"/v1/admin/question-versions/{vid(version_id)}{suffix}"


def stored_document(response: Response) -> QuestionDocument:
    return QuestionDocument.model_validate(response.json()["document"])


def error_codes(response: Response) -> list[str]:
    return [item["code"] for item in response.json().get("errors", [])]


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


@pytest.fixture
def strict_api(connection: Connection, session: Session) -> Iterator[ApiHarness]:
    """The application with separation of duties on."""
    harness = make_harness(
        connection, session, settings=Settings(Environment.LOCAL, forbid_self_approval=True)
    )
    with harness.client:
        yield harness


def seed(
    session: Session,
    connection: Connection,
    env: Env,
    status: str,
    doc: dict[str, Any] | None = None,
    *,
    rights_record_id: uuid.UUID | None = None,
) -> svc.QuestionVersionView:
    view: svc.QuestionVersionView = bring_to(
        session,
        connection,
        env,
        status,
        document(doc) if doc is not None else None,
        rights_record_id=rights_record_id,
    )
    return view


def call(api: ApiHarness, session: Session, role: Role, op: str, view: Any) -> Response:
    """Issue the request for `op` on `view` with a body that is valid for it."""
    headers = api.headers(role)
    sha = stored_hash(session, view.id)
    client = api.client
    if op == "edit":
        return client.put(vurl(view.id), headers=headers, json={"document": samples.mcq_document()})
    if op == "revision":
        return client.post(
            f"/v1/admin/questions/{qid(view.question_id)}/revisions", headers=headers
        )
    if op in ("approve", "publish"):
        return client.post(
            vurl(view.id, f"/{op}"), headers=headers, json={"expected_content_sha256": sha}
        )
    if op in ("request-changes", "reject", "withdraw"):
        return client.post(vurl(view.id, f"/{op}"), headers=headers, json={"reason": REASON})
    if op == "republish":
        return client.post(
            vurl(view.id, "/republish"),
            headers=headers,
            json={"expected_content_sha256": sha, "reason": REASON},
        )
    assert op == "submit"
    return client.post(vurl(view.id, "/submit"), headers=headers)


# op -> (status the version is in before, status code, status after)
OPS: dict[str, tuple[str, int, str]] = {
    "edit": ("draft", 200, "draft"),
    "submit": ("draft", 200, "in_review"),
    "approve": ("in_review", 200, "approved"),
    "request-changes": ("in_review", 200, "needs_fix"),
    "reject": ("in_review", 200, "rejected"),
    "revision": ("published", 201, "draft"),
    "publish": ("approved", 200, "published"),
    "withdraw": ("published", 200, "withdrawn"),
    "republish": ("withdrawn", 200, "published"),
}
STAFF_OPS = ("edit", "submit", "approve", "request-changes", "reject", "revision")
PUBLISHER_OPS = ("publish", "withdraw", "republish")
DECISION_OPS = (
    "submit",
    "approve",
    "request-changes",
    "reject",
    "publish",
    "withdraw",
    "republish",
)


# --- end to end ------------------------------------------------------------------------------


def test_a_question_goes_from_draft_to_a_corrected_published_version(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    created = create(session, env, document(samples.plain_mcq_document()))
    v1, question = created.id, created.question_id
    reviewer, admin = api.headers(Role.REVIEWER), api.headers(Role.CONTENT_ADMIN)

    def newest_actor(version: uuid.UUID) -> str:
        return str(audit_for(session, version)[-1].actor)

    # edit the draft
    edited = api.client.put(vurl(v1), headers=reviewer, json={"document": samples.mcq_document()})
    assert edited.status_code == 200
    assert edited.json()["status"] == "draft"
    assert stored_document(edited) == document(samples.mcq_document())
    assert audit_for(session, v1)[-1].action == "question_version.updated"
    assert newest_actor(v1) == api.actor(Role.REVIEWER)

    # submit
    submitted = api.client.post(vurl(v1, "/submit"), headers=reviewer)
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "in_review"
    assert newest_actor(v1) == api.actor(Role.REVIEWER)

    # approve
    approved = api.client.post(
        vurl(v1, "/approve"),
        headers=api.headers(Role.PLATFORM_ADMIN),
        json={"expected_content_sha256": submitted.json()["content_sha256"]},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert newest_actor(v1) == api.actor(Role.PLATFORM_ADMIN)

    # publish
    published = api.client.post(
        vurl(v1, "/publish"),
        headers=admin,
        json={"expected_content_sha256": approved.json()["content_sha256"]},
    )
    assert published.status_code == 200
    assert published.json()["status"] == "published"
    assert newest_actor(v1) == api.actor(Role.CONTENT_ADMIN)

    # visible to a learner
    seen = api.client.get(f"/v1/questions/{qid(question)}", headers=api.headers(Role.STUDENT))
    assert seen.status_code == 200
    assert seen.json()["version_id"] == vid(v1)

    # check an answer on the published version (nothing is written, nobody is audited)
    audit_before = len(audit_for(session, v1))
    key = document(samples.mcq_document()).mcq
    assert key is not None
    checked = api.client.post(
        f"/v1/questions/{qid(question)}/check",
        headers=api.headers(Role.STUDENT),
        json={"kind": "mcq", "selected_key": key.correct_key},
    )
    assert checked.status_code == 200
    assert checked.json()["kind"] == "mcq"
    assert checked.json()["version_id"] == vid(v1)
    assert checked.json()["correct"] is True
    assert checked.json()["correct_key"] == key.correct_key
    assert len(audit_for(session, v1)) == audit_before

    # open a revision
    revision = api.client.post(f"/v1/admin/questions/{qid(question)}/revisions", headers=reviewer)
    assert revision.status_code == 201
    v2 = ids.decode(ids.QUESTION_VERSION, revision.json()["id"])
    assert revision.json()["version_no"] == 2
    assert revision.json()["status"] == "draft"
    assert stored_document(revision) == document(samples.mcq_document())
    assert newest_actor(v2) == api.actor(Role.REVIEWER)
    assert status_of(connection, v1) == "published"  # the published version is not touched

    # edit, submit, approve, publish the new version
    edit2 = api.client.put(
        vurl(v2),
        headers=api.headers(Role.PLATFORM_ADMIN),
        json={"document": samples.show_that_document()},
    )
    assert edit2.status_code == 200
    assert newest_actor(v2) == api.actor(Role.PLATFORM_ADMIN)
    sub2 = api.client.post(vurl(v2, "/submit"), headers=reviewer)
    assert sub2.json()["status"] == "in_review"
    assert newest_actor(v2) == api.actor(Role.REVIEWER)
    app2 = api.client.post(
        vurl(v2, "/approve"),
        headers=admin,
        json={"expected_content_sha256": sub2.json()["content_sha256"]},
    )
    assert app2.json()["status"] == "approved"
    assert newest_actor(v2) == api.actor(Role.CONTENT_ADMIN)
    pub2 = api.client.post(
        vurl(v2, "/publish"),
        headers=api.headers(Role.PLATFORM_ADMIN),
        json={"expected_content_sha256": app2.json()["content_sha256"]},
    )
    assert pub2.status_code == 200
    assert pub2.json()["status"] == "published"
    assert newest_actor(v2) == api.actor(Role.PLATFORM_ADMIN)

    # the old version is withdrawn, by the publisher, in the same step
    old = api.client.get(vurl(v1), headers=admin)
    assert old.json()["status"] == "withdrawn"
    assert audit_for(session, v1)[-1].action == "question_version.superseded"
    assert newest_actor(v1) == api.actor(Role.PLATFORM_ADMIN)
    now_seen = api.client.get(f"/v1/questions/{qid(question)}", headers=api.headers(Role.STUDENT))
    assert now_seen.json()["version_id"] == vid(v2)


# --- roles inside staff ----------------------------------------------------------------------


@pytest.mark.parametrize("op", STAFF_OPS)
@pytest.mark.parametrize("role", STAFF)
def test_every_staff_role_can_edit_submit_decide_and_open_a_revision(
    api: ApiHarness, session: Session, connection: Connection, env: Env, role: Role, op: str
) -> None:
    before, code, after = OPS[op]
    view = seed(session, connection, env, before)
    response = call(api, session, role, op, view)
    assert response.status_code == code, response.text
    assert response.json()["status"] == after
    assert audit_for(session, view.id)[-1].actor == api.actor(role) or op == "revision"


@pytest.mark.parametrize("op", PUBLISHER_OPS)
@pytest.mark.parametrize("role", PUBLISHERS)
def test_content_admin_and_platform_admin_can_publish_withdraw_and_republish(
    api: ApiHarness, session: Session, connection: Connection, env: Env, role: Role, op: str
) -> None:
    before, code, after = OPS[op]
    view = seed(session, connection, env, before)
    response = call(api, session, role, op, view)
    assert response.status_code == code, response.text
    assert response.json()["status"] == after
    assert audit_for(session, view.id)[-1].actor == api.actor(role)


@pytest.mark.parametrize("op", PUBLISHER_OPS)
def test_a_reviewer_gets_404_on_publish_withdraw_and_republish_and_nothing_changes(
    api: ApiHarness, session: Session, connection: Connection, env: Env, op: str
) -> None:
    before, _, _ = OPS[op]
    view = seed(session, connection, env, before)
    entries = len(audit_for(session, view.id))
    response = call(api, session, Role.REVIEWER, op, view)
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
    assert status_of(connection, view.id) == before
    assert len(audit_for(session, view.id)) == entries


# --- publish gate (rule 8) -------------------------------------------------------------------


@pytest.mark.parametrize("status", ["draft", "needs_fix", "in_review", "rejected", "published"])
def test_publish_from_a_status_other_than_approved_is_invalid_transition(
    api: ApiHarness, session: Session, connection: Connection, env: Env, status: str
) -> None:
    view = seed(session, connection, env, status)
    response = api.client.post(
        vurl(view.id, "/publish"),
        headers=api.headers(Role.CONTENT_ADMIN),
        json={"expected_content_sha256": stored_hash(session, view.id)},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "invalid_transition"
    assert status_of(connection, view.id) == status


def test_a_version_with_stimuli_cannot_be_published_and_the_reasons_are_listed(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = seed(session, connection, env, "approved", samples.structured_document())
    assert view.has_unverified_visuals
    response = api.client.post(
        vurl(view.id, "/publish"),
        headers=api.headers(Role.PLATFORM_ADMIN),
        json={"expected_content_sha256": stored_hash(session, view.id)},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "not_publishable"
    assert "unverified_visuals" in error_codes(response)
    assert status_of(connection, view.id) == "approved"
    assert (
        api.client.get(
            f"/v1/questions/{qid(view.question_id)}", headers=api.headers(Role.STUDENT)
        ).status_code
        == 404
    )


def test_a_failed_critical_check_keeps_a_version_out_of_review_and_so_out_of_publishing(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = create(session, env)
    svc.record_check(session, actor=AUTHOR, version_id=view.id, result=failed_critical())
    submitted = api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.REVIEWER))
    assert submitted.json()["status"] == "needs_fix"
    for op in ("approve", "publish"):
        response = api.client.post(
            vurl(view.id, f"/{op}"),
            headers=api.headers(Role.CONTENT_ADMIN),
            json={"expected_content_sha256": stored_hash(session, view.id)},
        )
        assert response.status_code == 409
        assert response.json()["code"] == "invalid_transition"
    assert status_of(connection, view.id) == "needs_fix"


@pytest.mark.parametrize(
    ("op", "status"),
    [("approve", "in_review"), ("publish", "approved"), ("republish", "withdrawn")],
)
def test_a_decision_on_content_that_changed_is_stale_content(
    api: ApiHarness, session: Session, connection: Connection, env: Env, op: str, status: str
) -> None:
    view = seed(session, connection, env, status)
    body: dict[str, Any] = {"expected_content_sha256": NO_HASH}
    if op == "republish":
        body["reason"] = REASON
    response = api.client.post(
        vurl(view.id, f"/{op}"), headers=api.headers(Role.CONTENT_ADMIN), json=body
    )
    assert response.status_code == 409
    assert response.json()["code"] == "stale_content"
    assert status_of(connection, view.id) == status


@pytest.mark.parametrize("op", ["approve", "publish", "republish"])
@pytest.mark.parametrize("bad", ["", "abc", "G" * 64, "A" * 64, "0" * 63, "0" * 65])
def test_a_malformed_content_hash_is_rejected_by_validation(
    api: ApiHarness, session: Session, connection: Connection, env: Env, op: str, bad: str
) -> None:
    status = OPS[op][0]
    view = seed(session, connection, env, status)
    body: dict[str, Any] = {"expected_content_sha256": bad}
    if op == "republish":
        body["reason"] = REASON
    response = api.client.post(
        vurl(view.id, f"/{op}"), headers=api.headers(Role.CONTENT_ADMIN), json=body
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"
    assert status_of(connection, view.id) == status


@pytest.mark.parametrize("op", ["approve", "publish"])
def test_a_missing_hash_is_rejected_by_validation(
    api: ApiHarness, session: Session, connection: Connection, env: Env, op: str
) -> None:
    view = seed(session, connection, env, OPS[op][0])
    response = api.client.post(
        vurl(view.id, f"/{op}"), headers=api.headers(Role.CONTENT_ADMIN), json={}
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"


def test_publish_is_refused_when_the_rights_record_has_been_revoked(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    rights_id = new_rights(session)
    view = seed(session, connection, env, "approved", rights_record_id=rights_id)
    from qlab.rights import service as rights

    rights.revoke(session, rights_id, at=now())
    session.flush()
    response = api.client.post(
        vurl(view.id, "/publish"),
        headers=api.headers(Role.CONTENT_ADMIN),
        json={"expected_content_sha256": stored_hash(session, view.id)},
    )
    # Spec gap: 404 (rights fail closed) or 409 not_publishable with rights_denied are both
    # defensible; either way the version must not be published.
    assert response.status_code in (404, 409)
    if response.status_code == 409:
        assert response.json()["code"] == "not_publishable"
        assert "rights_denied" in error_codes(response)
    assert status_of(connection, view.id) == "approved"


# --- decisions return no content -------------------------------------------------------------


@pytest.mark.parametrize("op", DECISION_OPS)
def test_a_decision_answers_with_the_version_state_and_no_content(
    api: ApiHarness, session: Session, connection: Connection, env: Env, op: str
) -> None:
    before, _, after = OPS[op]
    view = seed(session, connection, env, before)
    response = call(api, session, Role.CONTENT_ADMIN, op, view)
    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == STATE_KEYS
    assert body["id"] == vid(view.id)
    assert body["question_id"] == qid(view.question_id)
    assert body["version_no"] == 1
    assert body["status"] == after
    assert body["content_sha256"] == stored_hash(session, view.id)
    assert "document" not in response.text


# --- PUT -------------------------------------------------------------------------------------


def test_put_returns_the_stored_document_and_resets_the_status_to_draft(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = seed(session, connection, env, "needs_fix")
    new = samples.show_that_document()
    response = api.client.put(
        vurl(view.id), headers=api.headers(Role.REVIEWER), json={"document": new}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "draft"
    assert body["id"] == vid(view.id)
    assert stored_document(response) == document(new)
    assert svc.get_version(session, view.id).document == document(new)
    assert body["content_sha256"] == svc.content_sha256(document(new))
    assert body["total_marks"] == 5


def test_put_with_math_that_does_not_render_is_invalid_document_and_changes_nothing(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = seed(session, connection, env, "draft")
    bad = samples.data_based_document()
    bad["stem"] = samples.line(samples.math(r"\undefinedcommand{x}"))
    before = snapshot(session, connection, view.question_id)
    response = api.client.put(
        vurl(view.id), headers=api.headers(Role.REVIEWER), json={"document": bad}
    )
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_document"
    assert response.json()["errors"]
    assert snapshot(session, connection, view.question_id) == before


@pytest.mark.parametrize(
    "bad",
    [with_exam_section("paper_99")],
    ids=["unknown exam section"],
)
def test_put_with_unknown_vocabulary_is_invalid_document_and_changes_nothing(
    api: ApiHarness, session: Session, connection: Connection, env: Env, bad: dict[str, Any]
) -> None:
    view = seed(session, connection, env, "draft")
    before = snapshot(session, connection, view.question_id)
    response = api.client.put(
        vurl(view.id), headers=api.headers(Role.REVIEWER), json={"document": bad}
    )
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_document"
    assert snapshot(session, connection, view.question_id) == before


def test_put_with_an_unknown_command_term_is_invalid_document(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = seed(session, connection, env, "draft")
    bad = samples.data_based_document()
    bad["parts"][0]["command_term"] = "frobnicate"
    response = api.client.put(
        vurl(view.id), headers=api.headers(Role.REVIEWER), json={"document": bad}
    )
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_document"


@pytest.mark.parametrize("status", ["in_review", "approved", "published", "withdrawn", "rejected"])
def test_put_on_a_version_that_is_not_editable_is_invalid_transition(
    api: ApiHarness, session: Session, connection: Connection, env: Env, status: str
) -> None:
    view = seed(session, connection, env, status)
    before = snapshot(session, connection, view.question_id)
    response = api.client.put(
        vurl(view.id),
        headers=api.headers(Role.CONTENT_ADMIN),
        json={"document": samples.mcq_document()},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "invalid_transition"
    assert snapshot(session, connection, view.question_id) == before


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"document": {}},
        {"document": {"schema_version": "1.0"}},
        {"document": None},
        {"document": "text"},
        {"document": samples.data_based_document(), "extra": 1},
    ],
    ids=["empty", "empty document", "partial", "null", "string", "extra field"],
)
def test_put_with_a_schema_invalid_body_is_validation_failed(
    api: ApiHarness, session: Session, connection: Connection, env: Env, body: dict[str, Any]
) -> None:
    view = seed(session, connection, env, "draft")
    before = snapshot(session, connection, view.question_id)
    response = api.client.put(vurl(view.id), headers=api.headers(Role.REVIEWER), json=body)
    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"
    assert snapshot(session, connection, view.question_id) == before


def test_put_with_inconsistent_total_marks_is_validation_failed(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = seed(session, connection, env, "draft")
    bad = samples.data_based_document()
    bad["total_marks"] = 99
    response = api.client.put(
        vurl(view.id), headers=api.headers(Role.REVIEWER), json={"document": bad}
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"


def test_put_on_an_unknown_version_is_404(api: ApiHarness) -> None:
    unknown = vid(uuid.uuid4())
    response = api.client.put(
        f"/v1/admin/question-versions/{unknown}",
        headers=api.headers(Role.REVIEWER),
        json={"document": samples.data_based_document()},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


@pytest.mark.parametrize(
    "bad_id",
    [
        "nope",
        "qv_",
        "qv_UPPERCASE0000000000000000",
        "q_" + "0" * 26,
        "qv_" + "u" * 26,
        "qv_" + "0" * 27,
    ],
)
def test_a_malformed_version_id_is_404_on_every_staff_endpoint(
    api: ApiHarness, bad_id: str
) -> None:
    headers = api.headers(Role.CONTENT_ADMIN)
    base = f"/v1/admin/question-versions/{bad_id}"
    sha = {"expected_content_sha256": NO_HASH}
    reason = {"reason": REASON}
    responses = [
        api.client.get(base, headers=headers),
        api.client.get(f"{base}/history", headers=headers),
        api.client.put(base, headers=headers, json={"document": samples.data_based_document()}),
        api.client.post(f"{base}/submit", headers=headers),
        api.client.post(f"{base}/approve", headers=headers, json=sha),
        api.client.post(f"{base}/request-changes", headers=headers, json=reason),
        api.client.post(f"{base}/reject", headers=headers, json=reason),
        api.client.post(f"{base}/publish", headers=headers, json=sha),
        api.client.post(f"{base}/withdraw", headers=headers, json=reason),
        api.client.post(f"{base}/republish", headers=headers, json={**sha, **reason}),
    ]
    for response in responses:
        assert response.status_code == 404, response.request.url
        assert response.json()["code"] == "not_found"


@pytest.mark.parametrize("bad_id", ["nope", "qv_" + "0" * 26, "q_" + "u" * 26])
def test_a_malformed_or_unknown_question_id_is_404_for_get_and_revisions(
    api: ApiHarness, bad_id: str
) -> None:
    headers = api.headers(Role.CONTENT_ADMIN)
    assert api.client.get(f"/v1/admin/questions/{bad_id}", headers=headers).status_code == 404
    assert (
        api.client.post(f"/v1/admin/questions/{bad_id}/revisions", headers=headers).status_code
        == 404
    )


def test_an_unknown_question_and_unknown_versions_are_404_on_every_staff_endpoint(
    api: ApiHarness,
) -> None:
    headers = api.headers(Role.CONTENT_ADMIN)
    unknown_q = qid(uuid.uuid4())
    base = f"/v1/admin/question-versions/{vid(uuid.uuid4())}"
    sha = {"expected_content_sha256": NO_HASH}
    reason = {"reason": REASON}
    responses = [
        api.client.get(f"/v1/admin/questions/{unknown_q}", headers=headers),
        api.client.post(f"/v1/admin/questions/{unknown_q}/revisions", headers=headers),
        api.client.get(base, headers=headers),
        api.client.get(f"{base}/history", headers=headers),
        api.client.post(f"{base}/submit", headers=headers),
        api.client.post(f"{base}/approve", headers=headers, json=sha),
        api.client.post(f"{base}/request-changes", headers=headers, json=reason),
        api.client.post(f"{base}/reject", headers=headers, json=reason),
        api.client.post(f"{base}/publish", headers=headers, json=sha),
        api.client.post(f"{base}/withdraw", headers=headers, json=reason),
        api.client.post(f"{base}/republish", headers=headers, json={**sha, **reason}),
    ]
    for response in responses:
        assert response.status_code == 404, response.request.url
        assert response.json()["code"] == "not_found"


# --- reasons ---------------------------------------------------------------------------------

REASON_OPS = ("request-changes", "reject", "withdraw", "republish")


def reason_body(op: str, session: Session, view: Any, reason: Any) -> dict[str, Any]:
    body: dict[str, Any] = {} if reason is None else {"reason": reason}
    if op == "republish":
        body["expected_content_sha256"] = stored_hash(session, view.id)
    return body


@pytest.mark.parametrize("op", REASON_OPS)
@pytest.mark.parametrize("reason", [None, "", " ", "   \n\t ", "x" * 501, 7, ["a"]], ids=repr)
def test_a_missing_blank_or_too_long_reason_is_rejected_and_nothing_changes(
    api: ApiHarness, session: Session, connection: Connection, env: Env, op: str, reason: Any
) -> None:
    before_status = OPS[op][0]
    view = seed(session, connection, env, before_status)
    entries = len(audit_for(session, view.id))
    response = api.client.post(
        vurl(view.id, f"/{op}"),
        headers=api.headers(Role.CONTENT_ADMIN),
        json=reason_body(op, session, view, reason),
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"
    assert status_of(connection, view.id) == before_status
    assert len(audit_for(session, view.id)) == entries


@pytest.mark.parametrize(
    "reason", ["x", "x" * 500, " " + "y" * 500 + " "], ids=["1", "500", "padded"]
)
def test_reasons_at_the_boundaries_are_accepted_and_trimmed_in_the_history(
    api: ApiHarness, session: Session, connection: Connection, env: Env, reason: str
) -> None:
    view = seed(session, connection, env, "in_review")
    response = api.client.post(
        vurl(view.id, "/request-changes"),
        headers=api.headers(Role.REVIEWER),
        json={"reason": reason},
    )
    assert response.status_code == 200
    history = api.client.get(vurl(view.id, "/history"), headers=api.headers(Role.REVIEWER)).json()
    assert history["items"][-1]["action"] == "changes_requested"
    assert history["items"][-1]["reason"] == reason.strip()


@pytest.mark.parametrize("op", REASON_OPS)
def test_the_reason_appears_in_the_history(
    api: ApiHarness, session: Session, connection: Connection, env: Env, op: str
) -> None:
    view = seed(session, connection, env, OPS[op][0])
    response = call(api, session, Role.CONTENT_ADMIN, op, view)
    assert response.status_code == 200
    history = api.client.get(vurl(view.id, "/history"), headers=api.headers(Role.REVIEWER)).json()
    assert history["items"][-1]["reason"] == REASON


# --- revisions -------------------------------------------------------------------------------


def test_a_revision_is_201_and_a_second_one_is_working_version_exists(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = seed(session, connection, env, "published")
    url = f"/v1/admin/questions/{qid(view.question_id)}/revisions"
    first = api.client.post(url, headers=api.headers(Role.REVIEWER))
    assert first.status_code == 201
    body = first.json()
    assert body["version_no"] == 2
    assert body["status"] == "draft"
    assert body["question_id"] == qid(view.question_id)
    assert stored_document(first) == view.document
    second = api.client.post(url, headers=api.headers(Role.CONTENT_ADMIN))
    assert second.status_code == 409
    assert second.json()["code"] == "working_version_exists"
    versions = api.client.get(
        f"/v1/admin/questions/{qid(view.question_id)}", headers=api.headers(Role.REVIEWER)
    ).json()["versions"]
    assert [v["version_no"] for v in versions] == [1, 2]


@pytest.mark.parametrize("status", ["draft", "needs_fix", "in_review", "approved"])
def test_a_revision_while_a_version_is_being_worked_on_is_refused(
    api: ApiHarness, session: Session, connection: Connection, env: Env, status: str
) -> None:
    view = seed(session, connection, env, status)
    response = api.client.post(
        f"/v1/admin/questions/{qid(view.question_id)}/revisions", headers=api.headers(Role.REVIEWER)
    )
    assert response.status_code == 409
    assert response.json()["code"] == "working_version_exists"


# --- separation of duties (YETKILER section 6, last bullet) -----------------------------------


def approved_entry(session: Session, version_id: uuid.UUID) -> Any:
    return next(
        e for e in audit_for(session, version_id) if e.action == "question_version.approved"
    )


def test_with_the_rule_off_the_last_editor_can_approve_and_the_audit_entry_says_so(
    api: ApiHarness, session: Session, env: Env
) -> None:
    editor = api.actor(Role.REVIEWER)
    view = create(session, env, actor=editor)
    session.flush()
    api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.REVIEWER))
    response = api.client.post(
        vurl(view.id, "/approve"),
        headers=api.headers(Role.REVIEWER),
        json={"expected_content_sha256": stored_hash(session, view.id)},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    entry = approved_entry(session, view.id)
    assert entry.actor == editor
    assert entry.data["approver_is_last_editor"] is True
    history = api.client.get(vurl(view.id, "/history"), headers=api.headers(Role.REVIEWER)).json()
    approved = [i for i in history["items"] if i["action"] == "approved"]
    assert [i["approver_is_last_editor"] for i in approved] == [True]


def test_a_different_approver_is_not_the_last_editor(
    api: ApiHarness, session: Session, env: Env
) -> None:
    view = create(session, env, actor=api.actor(Role.REVIEWER))
    api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.REVIEWER))
    response = api.client.post(
        vurl(view.id, "/approve"),
        headers=api.headers(Role.CONTENT_ADMIN),
        json={"expected_content_sha256": stored_hash(session, view.id)},
    )
    assert response.status_code == 200
    assert approved_entry(session, view.id).data["approver_is_last_editor"] is False


def test_the_last_editor_is_whoever_last_edited_through_the_api(
    api: ApiHarness, session: Session, env: Env
) -> None:
    view = create(session, env, actor=api.actor(Role.CONTENT_ADMIN))
    edit = api.client.put(
        vurl(view.id), headers=api.headers(Role.REVIEWER), json={"document": samples.mcq_document()}
    )
    assert edit.status_code == 200
    api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.CONTENT_ADMIN))
    # The content admin created it, but the reviewer edited it last.
    by_creator = api.client.post(
        vurl(view.id, "/approve"),
        headers=api.headers(Role.CONTENT_ADMIN),
        json={"expected_content_sha256": stored_hash(session, view.id)},
    )
    assert by_creator.status_code == 200
    assert approved_entry(session, view.id).data["approver_is_last_editor"] is False


def test_with_the_rule_on_the_last_editor_is_refused_and_another_account_succeeds(
    strict_api: ApiHarness, session: Session, env: Env
) -> None:
    api = strict_api
    view = create(session, env, actor=api.actor(Role.REVIEWER))
    submitted = api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.CONTENT_ADMIN))
    assert submitted.json()["status"] == "in_review"
    body = {"expected_content_sha256": submitted.json()["content_sha256"]}
    entries = len(audit_for(session, view.id))

    refused = api.client.post(
        vurl(view.id, "/approve"), headers=api.headers(Role.REVIEWER), json=body
    )
    assert refused.status_code == 403
    assert refused.json()["code"] == "self_approval_forbidden"
    assert (
        api.client.get(vurl(view.id), headers=api.headers(Role.REVIEWER)).json()["status"]
        == "in_review"
    )
    assert len(audit_for(session, view.id)) == entries

    allowed = api.client.post(
        vurl(view.id, "/approve"), headers=api.headers(Role.PLATFORM_ADMIN), json=body
    )
    assert allowed.status_code == 200
    assert allowed.json()["status"] == "approved"
    assert approved_entry(session, view.id).data["approver_is_last_editor"] is False


def test_with_the_rule_on_an_edit_through_the_api_makes_the_editor_the_last_editor(
    strict_api: ApiHarness, session: Session, env: Env
) -> None:
    api = strict_api
    view = create(session, env, actor=api.actor(Role.CONTENT_ADMIN))
    api.client.put(
        vurl(view.id), headers=api.headers(Role.REVIEWER), json={"document": samples.mcq_document()}
    )
    api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.CONTENT_ADMIN))
    body = {"expected_content_sha256": stored_hash(session, view.id)}
    refused = api.client.post(
        vurl(view.id, "/approve"), headers=api.headers(Role.REVIEWER), json=body
    )
    assert refused.status_code == 403
    # The creator no longer is the last editor, so the creator may approve.
    allowed = api.client.post(
        vurl(view.id, "/approve"), headers=api.headers(Role.CONTENT_ADMIN), json=body
    )
    assert allowed.status_code == 200


def test_with_the_rule_on_status_and_content_are_checked_before_the_rule(
    strict_api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    api = strict_api
    editor = api.actor(Role.REVIEWER)
    draft = create(session, env, actor=editor)
    wrong_status = api.client.post(
        vurl(draft.id, "/approve"),
        headers=api.headers(Role.REVIEWER),
        json={"expected_content_sha256": stored_hash(session, draft.id)},
    )
    assert wrong_status.status_code == 409
    assert wrong_status.json()["code"] == "invalid_transition"

    api.client.post(vurl(draft.id, "/submit"), headers=api.headers(Role.REVIEWER))
    stale = api.client.post(
        vurl(draft.id, "/approve"),
        headers=api.headers(Role.REVIEWER),
        json={"expected_content_sha256": NO_HASH},
    )
    assert stale.status_code == 409
    assert stale.json()["code"] == "stale_content"
    assert status_of(connection, draft.id) == "in_review"


def test_with_the_rule_on_the_other_decisions_are_not_restricted(
    strict_api: ApiHarness, session: Session, env: Env
) -> None:
    api = strict_api
    view = create(session, env, actor=api.actor(Role.REVIEWER))
    api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.REVIEWER))
    back = api.client.post(
        vurl(view.id, "/request-changes"),
        headers=api.headers(Role.REVIEWER),
        json={"reason": REASON},
    )
    assert back.status_code == 200


# --- who the last editor is ------------------------------------------------------------------
# The actor of the version's latest `created` entry, or `updated` entry that changed the content.
# Saving identical content again does not make the account the last editor.


@pytest.fixture(params=[False, True], ids=["rule-off", "rule-on"])
def duty_api(
    request: pytest.FixtureRequest, connection: Connection, session: Session
) -> Iterator[ApiHarness]:
    harness = make_harness(
        connection,
        session,
        settings=Settings(Environment.LOCAL, forbid_self_approval=request.param),
    )
    with harness.client:
        yield harness


def put_document(
    api: ApiHarness, role: Role, version_id: uuid.UUID, doc: dict[str, Any]
) -> Response:
    return api.client.put(vurl(version_id), headers=api.headers(role), json={"document": doc})


def approve_as(api: ApiHarness, session: Session, role: Role, version_id: uuid.UUID) -> Response:
    return api.client.post(
        vurl(version_id, "/approve"),
        headers=api.headers(role),
        json={"expected_content_sha256": stored_hash(session, version_id)},
    )


def assert_approved_by_last_editor(session: Session, version_id: uuid.UUID, expected: bool) -> None:
    assert approved_entry(session, version_id).data["approver_is_last_editor"] is expected


def test_resaving_identical_content_does_not_make_the_resaver_the_last_editor(
    duty_api: ApiHarness, session: Session, env: Env
) -> None:
    api = duty_api
    view = create(
        session, env, document(samples.plain_mcq_document()), actor=api.actor(Role.PLATFORM_ADMIN)
    )
    assert put_document(api, Role.REVIEWER, view.id, samples.mcq_document()).status_code == 200  # A
    assert (
        put_document(api, Role.CONTENT_ADMIN, view.id, samples.mcq_document()).status_code == 200
    )  # B, same
    assert (
        api.client.post(
            vurl(view.id, "/submit"), headers=api.headers(Role.CONTENT_ADMIN)
        ).status_code
        == 200
    )

    by_a = approve_as(api, session, Role.REVIEWER, view.id)  # A is still the last editor
    if api.settings.forbid_self_approval:
        assert by_a.status_code == 403
        assert by_a.json()["code"] == "self_approval_forbidden"
        assert status_of(session.connection(), view.id) == "in_review"
        # B only re-saved: B may approve.
        by_b = approve_as(api, session, Role.CONTENT_ADMIN, view.id)
        assert by_b.status_code == 200
        assert_approved_by_last_editor(session, view.id, False)
    else:
        assert by_a.status_code == 200
        assert_approved_by_last_editor(session, view.id, True)


def test_the_resaver_of_identical_content_is_not_the_last_editor_when_approving(
    duty_api: ApiHarness, session: Session, env: Env
) -> None:
    api = duty_api
    view = create(
        session, env, document(samples.plain_mcq_document()), actor=api.actor(Role.PLATFORM_ADMIN)
    )
    put_document(api, Role.REVIEWER, view.id, samples.mcq_document())
    put_document(api, Role.CONTENT_ADMIN, view.id, samples.mcq_document())
    api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.PLATFORM_ADMIN))
    response = approve_as(api, session, Role.CONTENT_ADMIN, view.id)
    assert response.status_code == 200
    assert_approved_by_last_editor(session, view.id, False)


def test_a_real_change_by_another_account_makes_that_account_the_last_editor(
    duty_api: ApiHarness, session: Session, env: Env
) -> None:
    api = duty_api
    view = create(
        session, env, document(samples.plain_mcq_document()), actor=api.actor(Role.PLATFORM_ADMIN)
    )
    assert put_document(api, Role.REVIEWER, view.id, samples.mcq_document()).status_code == 200  # A
    assert (
        put_document(
            api, Role.CONTENT_ADMIN, view.id, samples.two_column_mcq_document()
        ).status_code
        == 200
    )  # B changes the content
    api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.PLATFORM_ADMIN))

    by_a = approve_as(api, session, Role.REVIEWER, view.id)
    assert by_a.status_code == 200, by_a.text
    assert_approved_by_last_editor(session, view.id, False)


def test_the_last_editor_of_that_real_change_is_refused_with_the_rule_on(
    duty_api: ApiHarness, session: Session, env: Env
) -> None:
    api = duty_api
    view = create(
        session, env, document(samples.plain_mcq_document()), actor=api.actor(Role.PLATFORM_ADMIN)
    )
    put_document(api, Role.REVIEWER, view.id, samples.mcq_document())
    put_document(api, Role.CONTENT_ADMIN, view.id, samples.two_column_mcq_document())
    api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.PLATFORM_ADMIN))
    by_b = approve_as(api, session, Role.CONTENT_ADMIN, view.id)
    if api.settings.forbid_self_approval:
        assert by_b.status_code == 403
        assert by_b.json()["code"] == "self_approval_forbidden"
    else:
        assert by_b.status_code == 200
        assert_approved_by_last_editor(session, view.id, True)


def test_whoever_opened_an_unedited_revision_is_its_last_editor(
    duty_api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    api = duty_api
    published = seed(session, connection, env, "published", samples.plain_mcq_document())
    opened = api.client.post(
        f"/v1/admin/questions/{qid(published.question_id)}/revisions",
        headers=api.headers(Role.REVIEWER),
    )
    assert opened.status_code == 201
    v2 = ids.decode(ids.QUESTION_VERSION, opened.json()["id"])
    submitted = api.client.post(vurl(v2, "/submit"), headers=api.headers(Role.CONTENT_ADMIN))
    assert submitted.status_code == 200

    by_opener = approve_as(api, session, Role.REVIEWER, v2)
    if api.settings.forbid_self_approval:
        assert by_opener.status_code == 403
        assert by_opener.json()["code"] == "self_approval_forbidden"
        other = approve_as(api, session, Role.PLATFORM_ADMIN, v2)
        assert other.status_code == 200
        assert_approved_by_last_editor(session, v2, False)
    else:
        assert by_opener.status_code == 200
        assert_approved_by_last_editor(session, v2, True)


def test_another_account_can_approve_an_unedited_revision(
    duty_api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    api = duty_api
    published = seed(session, connection, env, "published", samples.plain_mcq_document())
    opened = api.client.post(
        f"/v1/admin/questions/{qid(published.question_id)}/revisions",
        headers=api.headers(Role.REVIEWER),
    )
    v2 = ids.decode(ids.QUESTION_VERSION, opened.json()["id"])
    api.client.post(vurl(v2, "/submit"), headers=api.headers(Role.REVIEWER))
    response = approve_as(api, session, Role.CONTENT_ADMIN, v2)
    assert response.status_code == 200
    assert_approved_by_last_editor(session, v2, False)


def test_without_any_created_or_updated_entry_the_service_refuses_with_the_rule_on(
    session: Session, connection: Connection, env: Env
) -> None:
    raw = raw_full_version(connection, env)
    raw_walk(connection, raw.version_id, "in_review")
    assert [
        e.action
        for e in audit_for(session, raw.version_id)
        if e.action.endswith(("created", "updated"))
    ] == []
    sha = stored_hash(session, raw.version_id)
    with pytest.raises(svc.SelfApprovalForbidden):
        svc.approve(
            session,
            actor="u_anyone",
            version_id=raw.version_id,
            expected_content_sha256=sha,
            forbid_self_approval=True,
        )
    assert status_of(connection, raw.version_id) == "in_review"


def test_without_any_created_or_updated_entry_the_rule_off_approves(
    session: Session, connection: Connection, env: Env
) -> None:
    raw = raw_full_version(connection, env)
    raw_walk(connection, raw.version_id, "in_review")
    state = svc.approve(
        session,
        actor="u_anyone",
        version_id=raw.version_id,
        expected_content_sha256=stored_hash(session, raw.version_id),
        forbid_self_approval=False,
    )
    assert state.status is svc.VersionStatus.APPROVED


# --- rights fail closed for staff too --------------------------------------------------------


def revoke(session: Session, rights_id: uuid.UUID) -> None:
    from qlab.rights import service as rights

    rights.revoke(session, rights_id, at=now())
    session.flush()


def test_after_revocation_staff_reads_are_404(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    rights_id = new_rights(session)
    view = seed(session, connection, env, "published", rights_record_id=rights_id)
    headers = api.headers(Role.PLATFORM_ADMIN)
    assert api.client.get(vurl(view.id), headers=headers).status_code == 200
    revoke(session, rights_id)
    for url in (
        f"/v1/admin/questions/{qid(view.question_id)}",
        vurl(view.id),
        vurl(view.id, "/history"),
    ):
        response = api.client.get(url, headers=headers)
        assert response.status_code == 404, url
        assert response.json()["code"] == "not_found"
    listed = api.client.get("/v1/admin/questions", headers=headers).json()
    assert listed["items"] == []


@pytest.mark.parametrize("op", ["edit", "submit", "approve", "revision"])
def test_after_revocation_staff_writes_are_404_and_change_nothing(
    api: ApiHarness, session: Session, connection: Connection, env: Env, op: str
) -> None:
    rights_id = new_rights(session)
    before_status = OPS[op][0]
    view = seed(session, connection, env, before_status, rights_record_id=rights_id)
    revoke(session, rights_id)
    snap = snapshot(session, connection, view.question_id)
    response = call(api, session, Role.PLATFORM_ADMIN, op, view)
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
    assert snapshot(session, connection, view.question_id) == snap


@pytest.mark.parametrize(
    ("op", "status"),
    [
        ("withdraw", "published"),
        ("reject", "in_review"),
        ("request-changes", "in_review"),
        ("request-changes", "approved"),
    ],
)
def test_after_revocation_withdraw_reject_and_request_changes_still_work(
    api: ApiHarness, session: Session, connection: Connection, env: Env, op: str, status: str
) -> None:
    rights_id = new_rights(session)
    view = seed(session, connection, env, status, rights_record_id=rights_id)
    revoke(session, rights_id)
    response = call(api, session, Role.PLATFORM_ADMIN, op, view)
    assert response.status_code == 200, response.text
    assert (
        response.json()["status"]
        == {
            "withdraw": "withdrawn",
            "reject": "rejected",
            "request-changes": "needs_fix",
        }[op]
    )
    assert status_of(connection, view.id) == response.json()["status"]


def test_after_revocation_republish_does_not_bring_the_question_back(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    rights_id = new_rights(session)
    view = seed(session, connection, env, "withdrawn", rights_record_id=rights_id)
    revoke(session, rights_id)
    response = call(api, session, Role.PLATFORM_ADMIN, "republish", view)
    assert response.status_code in (404, 409)
    assert status_of(connection, view.id) == "withdrawn"
