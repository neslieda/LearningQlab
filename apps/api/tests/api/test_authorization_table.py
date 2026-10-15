"""The endpoint x role table (docs/slices/M1G-5-YETKILER.md section 1) rewritten here as data
and compared cell by cell with `policy.ENDPOINT_POLICY`, then exercised over HTTP: every
endpoint x {six roles, an account without a role, no token} (CLAUDE.md rule 9).

The table below is typed from the specification on purpose; it is not imported from the code.
For an allowed cell this file asserts only what the policy layer guarantees (not 401, not the
policy's 404 for roles it does not know): handler bodies are tested elsewhere and a nonexistent
id legitimately gives 404 from a handler.
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any, Final

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, text
from sqlalchemy.orm import Session

from qlab.api import ids, policy
from qlab.content import service as svc
from qlab.organizations.service import Role
from qlab.rights import service as rights
from tests.api.support import ApiHarness
from tests.content import samples
from tests.content.support import Env, bring_to, document, make_env, now, stored_hash

R = Role
USER_ROLES: Final = frozenset({R.STUDENT, R.TEACHER, R.ORG_ADMIN})  # one column in M1-G
STAFF: Final = frozenset({R.REVIEWER, R.CONTENT_ADMIN, R.PLATFORM_ADMIN})
PUBLISHERS: Final = frozenset({R.CONTENT_ADMIN, R.PLATFORM_ADMIN})
EVERYONE: Final = frozenset(Role)

QV = "/v1/admin/question-versions/{version_id}"

# (number in the specification, method, route template, roles that may call it; None = public)
TABLE: Final[list[tuple[int, str, str, frozenset[Role] | None]]] = [
    (1, "GET", "/healthz", None),
    (2, "GET", "/v1/me", EVERYONE),
    (3, "GET", "/v1/programs/{program}/subjects/{subject}/syllabus", EVERYONE),
    (4, "GET", "/v1/questions", EVERYONE),
    (5, "GET", "/v1/questions/{question_id}", EVERYONE),
    (6, "POST", "/v1/questions/{question_id}/check", EVERYONE),
    (7, "GET", "/v1/admin/questions", STAFF),
    (8, "GET", "/v1/admin/questions/{question_id}", STAFF),
    (9, "GET", QV, STAFF),
    (10, "GET", QV + "/history", STAFF),
    (11, "PUT", QV, STAFF),
    (12, "POST", QV + "/submit", STAFF),
    (13, "POST", QV + "/approve", STAFF),
    (14, "POST", QV + "/request-changes", STAFF),
    (15, "POST", QV + "/reject", STAFF),
    (16, "POST", "/v1/admin/questions/{question_id}/revisions", STAFF),
    (17, "POST", QV + "/publish", PUBLISHERS),
    (18, "POST", QV + "/withdraw", PUBLISHERS),
    (19, "POST", QV + "/republish", PUBLISHERS),
    (20, "POST", "/v1/admin/questions", STAFF),
]
NON_PUBLIC = [row for row in TABLE if row[3] is not None]


def allowed(roles: frozenset[Role] | None, role: Role) -> bool:
    return roles is None or role in roles


def concrete(template: str) -> str:
    """A syntactically valid path whose ids name nothing."""
    return template.format(
        question_id=ids.encode(ids.QUESTION, uuid.uuid7()),
        version_id=ids.encode(ids.QUESTION_VERSION, uuid.uuid7()),
        program="synthetic-program",
        subject="synthetic-subject",
    )


def call(client: TestClient, method: str, template: str, headers: dict[str, str] | None = None):  # type: ignore[no-untyped-def]
    return client.request(method, concrete(template), headers=headers or {}, json={})


# --- the table in the code is the table in the specification ----------------------------------


def test_the_specification_table_has_twenty_distinct_endpoints() -> None:
    assert [row[0] for row in TABLE] == list(range(1, 21))
    assert len({(m, t) for _, m, t, _ in TABLE}) == 20


def test_the_policy_has_exactly_the_endpoints_of_the_specification() -> None:
    assert set(policy.ENDPOINT_POLICY) == {(m, t) for _, m, t, _ in TABLE}


@pytest.mark.parametrize(("number", "method", "template", "roles"), TABLE)
@pytest.mark.parametrize("role", list(Role))
def test_policy_cell(
    number: int, method: str, template: str, roles: frozenset[Role] | None, role: Role
) -> None:
    access = policy.ENDPOINT_POLICY[(method, template)]
    if roles is None:
        assert isinstance(access, policy.Public)
        return
    assert not isinstance(access, policy.Public)
    assert (role in access) == allowed(roles, role), f"#{number} {method} {template} {role}"


@pytest.mark.parametrize(("number", "method", "template", "roles"), TABLE)
def test_policy_row_is_exactly_the_specified_set(
    number: int, method: str, template: str, roles: frozenset[Role] | None
) -> None:
    access = policy.ENDPOINT_POLICY[(method, template)]
    if roles is None:
        assert isinstance(access, policy.Public)
    else:
        assert access == roles


def test_student_teacher_and_org_admin_share_a_column() -> None:
    for (_method, _template), access in policy.ENDPOINT_POLICY.items():
        if isinstance(access, policy.Public):
            continue
        assert len({role in access for role in USER_ROLES}) == 1


def test_no_endpoint_but_the_health_check_is_public() -> None:
    public = [
        key for key, access in policy.ENDPOINT_POLICY.items() if isinstance(access, policy.Public)
    ]
    assert public == [("GET", "/healthz")]


def test_every_non_public_endpoint_allows_platform_admin() -> None:
    for access in policy.ENDPOINT_POLICY.values():
        if not isinstance(access, policy.Public):
            assert Role.PLATFORM_ADMIN in access


def test_the_policy_table_cannot_be_modified() -> None:
    with pytest.raises(TypeError):
        policy.ENDPOINT_POLICY[("GET", "/x")] = policy.PUBLIC  # type: ignore[index]


@pytest.mark.db
def test_the_running_application_serves_exactly_the_table(api: ApiHarness) -> None:
    served = set()
    for route in api.client.app.routes:  # type: ignore[attr-defined]
        assert isinstance(route, policy.PolicyRoute)
        for method in route.methods or ():
            served.add((method, route.path_format))
    assert served == {(m, t) for _, m, t, _ in TABLE}


# --- over HTTP, cell by cell -------------------------------------------------------------------


@pytest.mark.db
@pytest.mark.parametrize(("number", "method", "template", "roles"), TABLE)
@pytest.mark.parametrize("role", list(Role))
def test_cell(
    api: ApiHarness,
    number: int,
    method: str,
    template: str,
    roles: frozenset[Role] | None,
    role: Role,
) -> None:
    response = call(api.client, method, template, api.headers(role))
    if allowed(roles, role):
        assert response.status_code not in (401, 405), f"#{number} {role}: {response.status_code}"
        # The policy's own refusal is a plain `not_found`; an allowed role never gets a 403.
        assert response.status_code != 403 or template.endswith("/approve")
    else:
        unknown = api.client.request(method, "/v1/no-such-endpoint", headers=api.headers(role))
        assert response.status_code == 404, f"#{number} {role}"
        assert unknown.status_code == 404
        assert response.content == unknown.content
        assert response.headers["content-type"] == unknown.headers["content-type"]
        assert response.json()["code"] == "not_found"
        assert "www-authenticate" not in response.headers


@pytest.mark.db
@pytest.mark.parametrize(("number", "method", "template", "roles"), TABLE)
def test_cell_account_without_a_role(
    api: ApiHarness, number: int, method: str, template: str, roles: frozenset[Role] | None
) -> None:
    response = call(api.client, method, template, api.headers())
    if roles is None:
        assert response.status_code == 200
        return
    unknown = api.client.request(method, "/v1/no-such-endpoint", headers=api.headers())
    assert response.status_code == 404, f"#{number}"
    assert response.content == unknown.content
    assert response.json()["code"] == "not_found"


@pytest.mark.db
@pytest.mark.parametrize(("number", "method", "template", "roles"), TABLE)
def test_cell_no_token(
    api: ApiHarness, number: int, method: str, template: str, roles: frozenset[Role] | None
) -> None:
    response = call(api.client, method, template)
    if roles is None:
        assert response.status_code == 200
        return
    assert response.status_code == 401, f"#{number}"
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "unauthenticated"


@pytest.mark.db
def test_the_health_check_answers_every_caller_the_same(api: ApiHarness) -> None:
    anonymous = api.client.get("/healthz")
    assert anonymous.status_code == 200
    assert anonymous.json() == {"status": "ok"}
    for headers in (
        api.headers(),
        api.headers(Role.STUDENT),
        api.headers(Role.PLATFORM_ADMIN),
        {"Authorization": "Bearer garbage"},
    ):
        response = api.client.get("/healthz", headers=headers)
        assert response.status_code == 200
        assert response.content == anonymous.content


@pytest.mark.db
def test_me_returns_the_roles_of_each_caller(api: ApiHarness) -> None:
    for role in Role:
        response = api.client.get("/v1/me", headers=api.headers(role))
        assert response.status_code == 200
        assert response.json() == {"account_id": api.actor(role), "roles": [role.value]}
        assert response.json()["account_id"].startswith("acc_")


# --- paths outside the table -------------------------------------------------------------------


@pytest.mark.db
@pytest.mark.parametrize(
    "path", ["/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect", "/v1", "/", "/v1/admin"]
)
def test_paths_that_are_not_endpoints_are_404_for_everyone(api: ApiHarness, path: str) -> None:
    anonymous = api.client.get(path)
    assert anonymous.status_code == 404  # an unknown path is 404 before authentication
    for headers in (api.headers(), api.headers(Role.STUDENT), api.headers(Role.PLATFORM_ADMIN)):
        response = api.client.get(path, headers=headers)
        assert response.status_code == 404
        assert response.content == anonymous.content


@pytest.mark.db
def test_an_unknown_path_is_404_with_or_without_a_token(api: ApiHarness) -> None:
    a = api.client.get("/v1/admin/nothing")
    b = api.client.get("/v1/admin/nothing", headers={"Authorization": "Bearer junk"})
    assert a.status_code == b.status_code == 404
    assert a.content == b.content


@pytest.mark.db
@pytest.mark.parametrize("method", ["DELETE", "PATCH"])
@pytest.mark.parametrize("role", [None, Role.STUDENT, Role.PLATFORM_ADMIN])
def test_methods_outside_the_table_are_404_like_an_unknown_path(
    api: ApiHarness, method: str, role: Role | None
) -> None:
    """A method the table does not list is an unknown endpoint: 404, byte-identical to an
    unknown path, for every caller (also without a token; step 1 of the order)."""
    for _, _, template, _ in TABLE:
        headers = api.headers(role) if role is not None else {}
        response = api.client.request(method, concrete(template), headers=headers)
        unknown = api.client.request(method, "/v1/no-such-endpoint", headers=headers)
        assert response.status_code == 404, (method, template)
        assert response.content == unknown.content, (method, template)
        assert response.headers["content-type"] == unknown.headers["content-type"]
        assert "allow" not in response.headers


# --- with real data: every allowed cell succeeds, every denied cell is a 404 -------------------

# Per endpoint number: the status the version (or question) is brought to before the call, and
# the status code of success. An operation that cannot be applied twice is built fresh for each
# role, so the expected answer is the success code, never a 409.
POSITIVE: Final[dict[int, tuple[str, int]]] = {
    1: ("published", 200),
    2: ("published", 200),
    3: ("published", 200),
    4: ("published", 200),
    5: ("published", 200),
    6: ("published", 200),
    7: ("published", 200),
    8: ("published", 200),
    9: ("draft", 200),
    10: ("draft", 200),
    11: ("draft", 200),
    12: ("draft", 200),
    13: ("in_review", 200),
    14: ("in_review", 200),
    15: ("in_review", 200),
    16: ("published", 201),
    17: ("approved", 200),
    18: ("published", 200),
    19: ("withdrawn", 200),
    20: ("draft", 201),
}


def real_request(
    api: ApiHarness, session: Session, connection: Connection, env: Env, number: int
) -> tuple[str, str, dict[str, Any] | None]:
    """Method, path and JSON body of endpoint `number`, aimed at real data in the state that
    fits its operation."""
    _, method, template, _ = TABLE[number - 1]
    status, _ = POSITIVE[number]
    view = bring_to(session, connection, env, status, document(samples.plain_mcq_document()))
    path = template.format(
        question_id=ids.encode(ids.QUESTION, view.question_id),
        version_id=ids.encode(ids.QUESTION_VERSION, view.id),
        program="ib_dp",
        subject="physics",
    )
    sha = stored_hash(session, view.id)
    body: dict[str, Any] | None = None
    if number == 6:
        body = {"kind": "mcq", "selected_key": "A"}
    elif number == 11:
        body = {"document": samples.mcq_document(), "expected_content_sha256": sha}
    elif number in (13, 17):
        body = {"expected_content_sha256": sha}
    elif number in (14, 15, 18):
        body = {"reason": "synthetic reason for the decision"}
    elif number == 19:
        body = {"expected_content_sha256": sha, "reason": "synthetic reason for the decision"}
    elif number == 20:
        # The platform's own-content record the creation needs, then a valid new document.
        rights.create_record(
            session,
            holder="Synthetic holder",
            valid_from=now() - timedelta(days=1),
            display_scope=rights.DisplayScope.ALL,
            allows_ai_processing=True,
            allows_commercial_use=True,
            license_ref=svc.OWN_CONTENT_LICENSE_REF,
        )
        body = {
            "program": "ib_dp",
            "subject": "physics",
            "document": samples.data_based_document(),
        }
    return method, path, body


@pytest.mark.db
@pytest.mark.node
@pytest.mark.parametrize(("number", "method", "template", "roles"), TABLE)
@pytest.mark.parametrize("role", [*Role, None], ids=[*(r.value for r in Role), "no-role"])
def test_cell_with_real_data(
    api: ApiHarness,
    session: Session,
    connection: Connection,
    number: int,
    method: str,
    template: str,
    roles: frozenset[Role] | None,
    role: Role | None,
) -> None:
    env = make_env(session)
    verb, path, body = real_request(api, session, connection, env, number)
    assert verb == method
    headers = api.headers(role) if role is not None else api.headers()
    response = api.client.request(method, path, headers=headers, json=body)
    if (roles is None) or (role is not None and allowed(roles, role)):
        _, success = POSITIVE[number]
        assert response.status_code == success, f"#{number} {role}: {response.text}"
    else:
        unknown = api.client.request(method, "/v1/no-such-endpoint", headers=headers)
        assert response.status_code == 404, f"#{number} {role}: {response.text}"
        assert response.content == unknown.content
        assert response.json()["code"] == "not_found"


@pytest.mark.db
@pytest.mark.node
@pytest.mark.parametrize(
    "number", [n for n, _, _, roles in TABLE if roles is not None and roles != EVERYONE]
)
def test_a_denied_role_changes_nothing_on_real_data(
    api: ApiHarness, session: Session, connection: Connection, number: int
) -> None:
    """The 404 for a role the table does not allow is more than an answer: the operation did
    not run, so the version is in the same state afterwards."""
    env = make_env(session)
    _, method, _, roles = TABLE[number - 1]
    assert roles is not None
    status_before, _ = POSITIVE[number]
    verb, path, body = real_request(api, session, connection, env, number)
    for role in Role:
        if role not in roles:
            response = api.client.request(verb, path, headers=api.headers(role), json=body)
            assert response.status_code == 404, f"#{number} {role}"
    session.expire_all()
    rows = connection.execute(
        text("SELECT status FROM question_version ORDER BY created_at DESC, id DESC")
    ).all()
    assert [r[0] for r in rows] == [status_before]
