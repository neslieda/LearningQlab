"""`POST /v1/admin/questions` and the syllabus / problem locations on staff responses
(docs/slices/M1G-7C-YAZIM.md sections 1 and 3, items 1 to 3)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from httpx2 import Response
from sqlalchemy import Connection, text
from sqlalchemy.orm import Session

from qlab.api import ids
from qlab.content import service as svc
from qlab.organizations.service import Role
from qlab.rights import service as rights
from tests.api.support import ApiHarness
from tests.content import samples
from tests.content.support import (
    Env,
    audit_actions,
    bring_to,
    make_env,
    new_rights,
    now,
    stored_hash,
    table_counts,
)

pytestmark = pytest.mark.db

URL = "/v1/admin/questions"
STAFF = (Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN)
CODES = {"program": "ib_dp", "subject": "physics", "version": "2025"}


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


def own_content(session: Session, **changes: Any) -> Any:
    fields: dict[str, Any] = {
        "holder": "Synthetic holder",
        "valid_from": now() - timedelta(days=1),
        "display_scope": rights.DisplayScope.ALL,
        "allows_ai_processing": True,
        "allows_commercial_use": True,
        "license_ref": svc.OWN_CONTENT_LICENSE_REF,
    }
    fields.update(changes)
    return rights.create_record(session, **fields)


def body(document: dict[str, Any] | None = None, **extra: Any) -> dict[str, Any]:
    return {
        "program": "ib_dp",
        "subject": "physics",
        "document": document if document is not None else samples.data_based_document(),
        **extra,
    }


def post(api: ApiHarness, payload: dict[str, Any], role: Role = Role.REVIEWER) -> Response:
    return api.client.post(URL, headers=api.headers(role), json=payload)


def locations(response: Response) -> list[str | None]:
    return [item.get("location") for item in response.json()["errors"]]


# --- the syllabus on every response that returns a version -----------------------------------


def test_get_put_and_revision_carry_the_syllabus_codes(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = bring_to(session, connection, env, "draft")
    url = f"/v1/admin/question-versions/{ids.encode(ids.QUESTION_VERSION, view.id)}"
    headers = api.headers(Role.REVIEWER)

    got = api.client.get(url, headers=headers)
    assert got.status_code == 200
    assert got.json()["syllabus"] == CODES

    put = api.client.put(
        url,
        headers=headers,
        json={
            "document": samples.show_that_document(),
            "expected_content_sha256": stored_hash(session, view.id),
        },
    )
    assert put.status_code == 200
    assert put.json()["syllabus"] == CODES


def test_a_revision_carries_the_syllabus_codes(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = bring_to(session, connection, env, "published")
    response = api.client.post(
        f"/v1/admin/questions/{ids.encode(ids.QUESTION, view.question_id)}/revisions",
        headers=api.headers(Role.CONTENT_ADMIN),
    )
    assert response.status_code == 201
    assert response.json()["syllabus"] == CODES


# --- POST /v1/admin/questions ----------------------------------------------------------------


@pytest.mark.parametrize("role", STAFF)
def test_staff_create_a_draft_authored_question(
    api: ApiHarness, session: Session, env: Env, role: Role
) -> None:
    record = own_content(session)
    response = post(api, body(), role)

    assert response.status_code == 201, response.text
    created = response.json()
    assert created["status"] == "draft"
    assert created["version_no"] == 1
    assert created["syllabus"] == CODES
    assert created["created_by"] == api.actor(role)
    assert created["checks"] == []
    assert created["document"]["question_class"] == "data_based"

    session.expire_all()
    row = session.execute(
        text("SELECT origin, source_ref, rights_record_id, syllabus_version_id FROM question")
    ).one()
    assert row.origin == "authored"
    assert row.source_ref is None
    assert row.rights_record_id == record.id
    assert row.syllabus_version_id == env.syllabus_version_id


def test_the_creation_is_audited_and_visible_to_staff(
    api: ApiHarness, session: Session, env: Env
) -> None:
    own_content(session)
    created = post(api, body()).json()
    version_id = ids.decode(ids.QUESTION_VERSION, created["id"])

    assert audit_actions(session, version_id) == ["question_version.created"]
    again = api.client.get(
        f"/v1/admin/question-versions/{created['id']}", headers=api.headers(Role.REVIEWER)
    )
    assert again.status_code == 200
    assert again.json()["document"] == created["document"]


def test_without_a_version_the_newest_is_used_and_an_explicit_one_works(
    api: ApiHarness, session: Session, env: Env
) -> None:
    own_content(session)
    assert post(api, body()).json()["syllabus"] == CODES
    assert post(api, body(version="2025")).json()["syllabus"] == CODES


@pytest.mark.parametrize("role", [Role.STUDENT, Role.TEACHER, Role.ORG_ADMIN])
def test_learners_and_teachers_are_refused_like_an_unknown_path(
    api: ApiHarness, connection: Connection, session: Session, env: Env, role: Role
) -> None:
    own_content(session)
    before = table_counts(connection)
    response = post(api, body(), role)
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
    assert table_counts(connection) == before


def test_without_a_token_it_is_401(api: ApiHarness) -> None:
    assert api.client.post(URL, json=body()).status_code == 401


def own_content_cases(session: Session) -> dict[str, Any]:
    past = now() - timedelta(days=2)
    return {
        "missing": lambda: None,
        "revoked": lambda: rights.revoke(session, own_content(session).id, at=now()),
        "expired": lambda: own_content(
            session, valid_from=past, valid_until=now() - timedelta(days=1)
        ),
        "not_yet_valid": lambda: own_content(session, valid_from=now() + timedelta(days=1)),
        "limited_in_time": lambda: own_content(session, valid_until=now() + timedelta(days=30)),
        "display_to_an_organization": lambda: own_content(
            session,
            display_scope=rights.DisplayScope.ORGANIZATION,
            display_organization_id=__import__("uuid").uuid4(),
        ),
        "display_to_nobody": lambda: own_content(session, display_scope=rights.DisplayScope.NONE),
        "two_records": lambda: (own_content(session), own_content(session)),
    }


@pytest.mark.parametrize(
    "case",
    [
        "missing",
        "revoked",
        "expired",
        "not_yet_valid",
        "limited_in_time",
        "display_to_an_organization",
        "display_to_nobody",
        "two_records",
    ],
)
def test_an_unusable_own_content_record_is_409_and_nothing_is_written(
    api: ApiHarness, connection: Connection, session: Session, env: Env, case: str
) -> None:
    own_content_cases(session)[case]()
    before = table_counts(connection)
    rights_rows = connection.execute(text("SELECT count(*) FROM rights_record")).scalar_one()

    response = post(api, body())

    assert response.status_code == 409, response.text
    assert response.json()["code"] == "own_content_rights_unavailable"
    assert table_counts(connection) == before
    assert connection.execute(text("SELECT count(*) FROM rights_record")).scalar_one() == (
        rights_rows
    )


def test_a_record_that_is_not_own_content_is_not_used(
    api: ApiHarness, connection: Connection, session: Session, env: Env
) -> None:
    new_rights(session)  # a display-to-everyone record without the own-content reference
    before = table_counts(connection)
    response = post(api, body())
    assert response.status_code == 409
    assert table_counts(connection) == before


@pytest.mark.parametrize(
    "change",
    [{"program": "no_such"}, {"subject": "no_such"}, {"version": "1999"}],
)
def test_an_unknown_programme_subject_or_version_is_404(
    api: ApiHarness, connection: Connection, session: Session, env: Env, change: dict[str, str]
) -> None:
    own_content(session)
    before = table_counts(connection)
    response = post(api, {**body(), **change})
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
    assert table_counts(connection) == before


def test_unknown_syllabus_comes_before_the_rights_check(
    api: ApiHarness, session: Session, env: Env
) -> None:
    # No own-content record exists either; the unknown programme is what is reported.
    assert post(api, {**body(), "program": "no_such"}).status_code == 404


def test_an_invalid_document_is_422_with_locations_and_nothing_is_written(
    api: ApiHarness, connection: Connection, session: Session, env: Env
) -> None:
    own_content(session)
    document = samples.data_based_document()
    document["exam_section"] = "paper_9"
    document["parts"][0]["command_term"] = "juggle"
    before = table_counts(connection)

    response = post(api, body(document))

    assert response.status_code == 422
    assert response.json()["code"] == "invalid_document"
    assert locations(response) == ["document.exam_section", "document.parts.0.command_term"]
    assert table_counts(connection) == before


def test_a_problem_about_the_whole_document_has_no_location(
    api: ApiHarness, session: Session, env: Env
) -> None:
    own_content(session)
    document = samples.data_based_document()
    document["outcome"] = "a\u0000b"
    response = post(api, body(document))
    assert response.status_code == 422
    assert locations(response) == [None]


@pytest.mark.node
def test_math_location_reaches_the_client(api: ApiHarness, session: Session, env: Env) -> None:
    own_content(session)
    document = samples.question(samples.part("p1", "a", 2))
    document["parts"][0]["mark_points"][1]["content"] = samples.line(
        samples.text("one "), samples.math("x"), samples.math(r"\def\q{1}")
    )
    response = post(api, body(document))
    assert response.status_code == 422
    assert locations(response) == [
        "document.parts.0.mark_points.1.content.content.0.content.2.attrs.latex",
    ]


def test_an_update_reports_locations_too(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = bring_to(session, connection, env, "draft")
    document = samples.data_based_document()
    document["exam_section"] = "paper_9"
    response = api.client.put(
        f"/v1/admin/question-versions/{ids.encode(ids.QUESTION_VERSION, view.id)}",
        headers=api.headers(Role.REVIEWER),
        json={"document": document, "expected_content_sha256": stored_hash(session, view.id)},
    )
    assert response.status_code == 422
    assert locations(response) == ["document.exam_section"]


@pytest.mark.parametrize(
    "extra",
    [
        {"origin": "generated"},
        {"origin": "authored"},
        {"source_ref": "a1-1"},
        {"rights_record_id": "00000000-0000-0000-0000-000000000000"},
        {"status": "published"},
    ],
)
def test_the_client_cannot_set_origin_source_ref_or_rights(
    api: ApiHarness, connection: Connection, session: Session, env: Env, extra: dict[str, Any]
) -> None:
    own_content(session)
    before = table_counts(connection)
    response = post(api, body(**extra))
    assert response.status_code == 422
    assert table_counts(connection) == before


def test_turkish_locations_reach_the_client(api: ApiHarness, session: Session, env: Env) -> None:
    own_content(session)
    document = samples.data_based_document()
    document["outcome"] = "hız"
    document["parts"][1]["mark_points"][0]["content"] = samples.line(samples.text("şu"))
    response = post(api, body(document))
    assert response.status_code == 422
    assert locations(response) == [
        "document.outcome",
        "document.parts.1.mark_points.0.content.content.0.content.0.text",
    ]
