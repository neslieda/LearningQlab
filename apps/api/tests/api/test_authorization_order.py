"""Authorization comes before validation (docs/slices/M1G-5-SOZLESME.md section 3.1): a caller
who may not call an endpoint gets 404 (or 401) whatever the request looks like, never 422, so
the shape of the answer says nothing about the resource. Roles are read on every request.

Oracle for "the request reached validation": the admin endpoints that take a body answer an
invalid body with 422 `validation_failed` when the caller is allowed, whether or not their
handler exists yet.
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from httpx2 import Response

from qlab.api import ids
from qlab.identity import service as identity
from qlab.identity.tokens import DEV_ISSUER
from qlab.organizations import service as organizations
from qlab.organizations.service import Role
from tests.api.support import ApiHarness

pytestmark = pytest.mark.db

VID = ids.encode(ids.QUESTION_VERSION, uuid.uuid7())
QID = ids.encode(ids.QUESTION, uuid.uuid7())
QV = "/v1/admin/question-versions"

# (method, path, roles that may call it): the admin endpoints that require a JSON body.
BODY_ENDPOINTS: list[tuple[str, str, frozenset[Role]]] = [
    ("PUT", f"{QV}/{VID}", frozenset({Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN})),
    (
        "POST",
        f"{QV}/{VID}/approve",
        frozenset({Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN}),
    ),
    (
        "POST",
        f"{QV}/{VID}/request-changes",
        frozenset({Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN}),
    ),
    (
        "POST",
        f"{QV}/{VID}/reject",
        frozenset({Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN}),
    ),
    ("POST", f"{QV}/{VID}/publish", frozenset({Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN})),
    ("POST", f"{QV}/{VID}/withdraw", frozenset({Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN})),
    ("POST", f"{QV}/{VID}/republish", frozenset({Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN})),
]
# Request bodies that are bad in different ways: (content, content type).
BAD_BODIES: list[tuple[bytes | None, str | None]] = [
    (None, None),
    (b"", "application/json"),
    (b'{"broken', "application/json"),
    (b"not json at all", "application/json"),
    (b"[]", "application/json"),
    (b'"a string"', "application/json"),
    (b"null", "application/json"),
    (b"123", "application/json"),
    (b"{}", "application/json"),
    (b'{"expected_content_sha256": 5, "reason": [], "document": "x"}', "application/json"),
    (b'{"document": {"unknown": true}}', "application/json"),
    (b"\xff\xfe\x00\x01", "application/json"),
    (b"a=b&c=d", "application/x-www-form-urlencoded"),
    (b"plain text", "text/plain"),
    (b"[" * 5000, "application/json"),
    (b'{"reason": "' + b"x" * 300_000 + b'"}', "application/json"),
]


def send(
    api: ApiHarness,
    method: str,
    path: str,
    headers: dict[str, str],
    body: tuple[bytes | None, str | None] = (None, None),
) -> Response:
    content, content_type = body
    merged = dict(headers)
    if content_type:
        merged["Content-Type"] = content_type
    return api.client.request(method, path, headers=merged, content=content)


def problem_key(response: Response) -> tuple[int, bytes, str | None, str | None]:
    return (
        response.status_code,
        response.content,
        response.headers.get("content-type"),
        response.headers.get("www-authenticate"),
    )


# --- no validation before authorization -------------------------------------------------------


@pytest.mark.parametrize(("method", "path", "roles"), BODY_ENDPOINTS)
@pytest.mark.parametrize("body", BAD_BODIES)
def test_denied_callers_never_get_422_for_a_bad_body(
    api: ApiHarness,
    method: str,
    path: str,
    roles: frozenset[Role],
    body: tuple[bytes | None, str | None],
) -> None:
    unknown = api.client.request(method, "/v1/no-such-endpoint")
    for caller in (Role.STUDENT, Role.TEACHER, Role.ORG_ADMIN):
        response = send(api, method, path, api.headers(caller), body)
        assert response.status_code == 404
        assert response.content == unknown.content
    no_role = send(api, method, path, api.headers(), body)
    assert no_role.status_code == 404
    assert no_role.content == unknown.content
    anonymous = send(api, method, path, {}, body)
    assert anonymous.status_code == 401
    assert anonymous.json()["code"] == "unauthenticated"
    assert anonymous.headers["www-authenticate"] == "Bearer"
    for role in Role:
        if role in roles:
            continue
        assert send(api, method, path, api.headers(role), body).status_code == 404


@pytest.mark.parametrize(("method", "path", "roles"), BODY_ENDPOINTS)
def test_allowed_callers_do_reach_validation(
    api: ApiHarness, method: str, path: str, roles: frozenset[Role]
) -> None:
    """The oracle: with an invalid body, an allowed role gets 422 where a denied one got 404."""
    for role in roles:
        response = send(api, method, path, api.headers(role), (b'{"broken', "application/json"))
        assert response.status_code == 422, role
        assert response.json()["code"] == "validation_failed"
        response = send(api, method, path, api.headers(role), (b"{}", "application/json"))
        assert response.status_code == 422, role


@pytest.mark.parametrize(
    "path_id",
    [
        "not-an-id",
        "q_",
        "qv_",
        "qv_" + "z" * 26,
        "qv_" + "0" * 25,
        "qv_" + "0" * 27,
        "QV_" + "0" * 26,
        "q_" + "0" * 26,  # the wrong kind of identifier
        "acc_" + "0" * 26,
        "00000000-0000-0000-0000-000000000000",
        "%00",
        "%2e%2e",
        "a" * 5000,
        "%27%20OR%201%3D1--",
        "%E2%82%AC",
        "1;DROP",
    ],
)
@pytest.mark.parametrize(
    ("method", "template"),
    [
        ("GET", "/v1/admin/question-versions/{}"),
        ("GET", "/v1/admin/question-versions/{}/history"),
        ("PUT", "/v1/admin/question-versions/{}"),
        ("POST", "/v1/admin/question-versions/{}/submit"),
        ("POST", "/v1/admin/question-versions/{}/approve"),
        ("POST", "/v1/admin/question-versions/{}/publish"),
        ("GET", "/v1/admin/questions/{}"),
        ("POST", "/v1/admin/questions/{}/revisions"),
    ],
)
def test_malformed_path_ids_on_admin_endpoints_are_404_or_401(
    api: ApiHarness, method: str, template: str, path_id: str
) -> None:
    path = template.format(path_id)
    well_formed = template.format(VID if "versions" in template else QID)
    reference = api.client.request(method, well_formed, headers=api.headers(Role.STUDENT))
    for headers in (api.headers(Role.STUDENT), api.headers()):
        response = api.client.request(method, path, headers=headers, json={"x": 1})
        assert response.status_code == 404
        assert response.content == reference.content
    anonymous = api.client.request(method, path, json={"x": 1})
    assert anonymous.status_code == 401
    assert anonymous.json()["code"] == "unauthenticated"


@pytest.mark.parametrize(
    "query",
    [
        "limit=abc",
        "limit=-1",
        "limit=999999999",
        "limit=0",
        "status=bogus",
        "level=zz&exam_section=%00",
        "has_unverified_visuals=maybe",
        "cursor=%00%00",
        "cursor=" + "x" * 5000,
        "limit=1&limit=2",
    ],
)
@pytest.mark.parametrize("path", ["/v1/admin/questions", "/v1/questions"])
def test_bad_query_parameters_do_not_reveal_endpoints_to_the_unauthorized(
    api: ApiHarness, path: str, query: str
) -> None:
    anonymous = api.client.get(f"{path}?{query}")
    assert anonymous.status_code == 401
    assert anonymous.json()["code"] == "unauthenticated"
    no_role = api.client.get(f"{path}?{query}", headers=api.headers())
    assert no_role.status_code == 404
    if path.startswith("/v1/admin"):
        student = api.client.get(f"{path}?{query}", headers=api.headers(Role.STUDENT))
        assert student.status_code == 404
        assert student.content == no_role.content


def test_a_bad_query_reaches_validation_for_allowed_callers(api: ApiHarness) -> None:
    response = api.client.get("/v1/admin/questions?limit=abc", headers=api.headers(Role.REVIEWER))
    assert response.status_code == 422
    response = api.client.get("/v1/questions?limit=abc", headers=api.headers(Role.STUDENT))
    assert response.status_code == 422


def test_check_endpoint_bad_body_is_401_or_404_for_unauthorized(api: ApiHarness) -> None:
    path = f"/v1/questions/{QID}/check"
    for body in BAD_BODIES:
        assert send(api, "POST", path, {}, body).status_code == 401
        assert send(api, "POST", path, api.headers(), body).status_code == 404


# --- roles are read from the database on every request ---------------------------------------


def probe(api: ApiHarness, headers: dict[str, str], *, publisher: bool = False) -> int:
    """Status for an invalid body: 422 = the endpoint is open to the caller, 404 = not."""
    path = f"{QV}/{VID}/{'publish' if publisher else 'approve'}"
    return api.client.post(path, headers=headers, json={}).status_code


def test_multi_role_account_gets_the_union(api: ApiHarness) -> None:
    student_reviewer = api.headers(Role.STUDENT, Role.REVIEWER)
    assert probe(api, student_reviewer) == 422  # reviewer part
    assert probe(api, student_reviewer, publisher=True) == 404  # reviewer may not publish
    assert api.client.get("/v1/questions", headers=student_reviewer).status_code != 404
    both = api.headers(Role.REVIEWER, Role.CONTENT_ADMIN)
    assert probe(api, both) == 422
    assert probe(api, both, publisher=True) == 422
    assert api.client.get("/v1/me", headers=both).json()["roles"] == ["content_admin", "reviewer"]
    everything = api.headers(*Role)
    assert probe(api, everything, publisher=True) == 422
    me = api.client.get("/v1/me", headers=everything).json()
    assert me["roles"] == sorted(r.value for r in Role)


def test_student_plus_teacher_gets_no_staff_access(api: ApiHarness) -> None:
    headers = api.headers(Role.STUDENT, Role.TEACHER, Role.ORG_ADMIN)
    assert probe(api, headers) == 404
    assert probe(api, headers, publisher=True) == 404
    assert api.client.get("/v1/admin/questions", headers=headers).status_code == 404


def test_revoking_a_role_takes_effect_on_the_next_request(api: ApiHarness) -> None:
    headers = api.headers(Role.REVIEWER, Role.STUDENT)
    account = api.account(Role.REVIEWER, Role.STUDENT)
    assert probe(api, headers) == 422
    assert organizations.revoke(
        api.session, account_id=account, role=Role.REVIEWER, revoked_by="system:test"
    )
    api.session.flush()
    assert probe(api, headers) == 404  # same token, no new login
    assert api.client.get("/v1/me", headers=headers).json()["roles"] == ["student"]
    # Granting it again is a new assignment and works at once.
    assert organizations.grant(
        api.session, account_id=account, role=Role.REVIEWER, granted_by="system:test"
    )
    api.session.flush()
    assert probe(api, headers) == 422


def test_revoking_every_role_leaves_a_valid_token_with_nothing(api: ApiHarness) -> None:
    headers = api.headers(Role.STUDENT)
    account = api.account(Role.STUDENT)
    assert api.client.get("/v1/me", headers=headers).status_code == 200
    organizations.revoke(
        api.session, account_id=account, role=Role.STUDENT, revoked_by="system:test"
    )
    api.session.flush()
    gone = api.client.get("/v1/me", headers=headers)
    assert gone.status_code == 404  # authenticated, but a role-less account sees nothing
    assert api.client.get("/healthz", headers=headers).status_code == 200


def test_granting_a_role_takes_effect_on_the_next_request(api: ApiHarness) -> None:
    headers = api.headers()
    assert probe(api, headers) == 404
    organizations.grant(
        api.session, account_id=api.account(), role=Role.REVIEWER, granted_by="system:test"
    )
    api.session.flush()
    assert probe(api, headers) == 422


def test_a_token_carries_no_role(api: ApiHarness) -> None:
    """A token that claims a role is not believed: roles come from the database."""
    from datetime import UTC, datetime

    import jwt

    now = int(datetime.now(tz=UTC).timestamp())
    subject = api.subject()  # an account without roles
    claims: dict[str, Any] = {
        "iss": DEV_ISSUER,
        "aud": "qlab-api-local",
        "sub": subject,
        "iat": now,
        "exp": now + 300,
        "roles": ["platform_admin"],
        "role": "platform_admin",
        "scope": "admin",
        "groups": ["platform_admin"],
    }
    token = jwt.encode(claims, api.key, algorithm="EdDSA")
    headers = {"Authorization": f"Bearer {token}"}
    assert probe(api, headers) == 404
    assert api.client.get("/v1/me", headers=headers).status_code == 404


# --- authentication failures ---------------------------------------------------------------------


def test_a_disabled_account_gets_401_on_its_old_token(api: ApiHarness) -> None:
    headers = api.headers(Role.PLATFORM_ADMIN)
    assert probe(api, headers, publisher=True) == 422
    assert identity.disable_account(api.session, api.account(Role.PLATFORM_ADMIN))
    api.session.flush()
    for path in ("/v1/me", "/v1/admin/questions", "/v1/questions"):
        response = api.client.get(path, headers=headers)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"
        assert response.json()["code"] == "unauthenticated"
    assert api.client.get("/healthz", headers=headers).status_code == 200


def test_a_disabled_account_with_roles_is_not_a_404(api: ApiHarness) -> None:
    """Disabled is an authentication failure (401), not an authorization one (404)."""
    headers = api.headers(Role.STUDENT)
    identity.disable_account(api.session, api.account(Role.STUDENT))
    api.session.flush()
    assert api.client.get("/v1/admin/questions", headers=headers).status_code == 401


def test_an_unknown_account_with_a_valid_token_gets_401(api: ApiHarness) -> None:
    token = api.token("nobody-has-this-subject")
    response = api.client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["code"] == "unauthenticated"
    assert (
        api.client.get(
            "/v1/admin/questions", headers={"Authorization": f"Bearer {token}"}
        ).status_code
        == 401
    )


def test_the_account_is_not_created_by_a_request(api: ApiHarness) -> None:
    token = api.token("never-registered")
    api.client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    api.session.expire_all()
    assert identity.find_account(api.session, issuer=DEV_ISSUER, subject="never-registered") is None


def test_the_same_subject_under_another_issuer_is_another_account(api: ApiHarness) -> None:
    """Accounts are keyed by issuer and subject together."""
    subject = api.subject(Role.PLATFORM_ADMIN)
    other = identity.ensure_account(api.session, issuer="https://other.invalid", subject=subject)
    api.session.flush()
    assert other.id != api.account(Role.PLATFORM_ADMIN)
    assert organizations.roles_of(api.session, other.id) == frozenset()


def test_an_account_of_another_issuer_is_unknown_to_this_verifier(api: ApiHarness) -> None:
    identity.ensure_account(api.session, issuer="https://other.invalid", subject="foreign-user")
    api.session.flush()
    token = api.token("foreign-user")  # signed for the dev issuer; no account under that issuer
    assert api.client.get("/v1/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_the_subject_is_matched_exactly(api: ApiHarness) -> None:
    subject = api.subject(Role.PLATFORM_ADMIN)
    for variant in (subject.upper(), subject + "x", subject[:-1], subject + "​"):
        token = api.token(variant)
        response = api.client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401, variant


def test_the_401_never_differs_between_failure_reasons(api: ApiHarness) -> None:
    api.account(Role.STUDENT)
    disabled_subject = api.subject(Role.REVIEWER)
    identity.disable_account(api.session, api.account(Role.REVIEWER))
    api.session.flush()
    other_key = Ed25519PrivateKey.generate()
    student = api.subject(Role.STUDENT)
    bad_headers: dict[str, dict[str, str]] = {
        "none": {},
        "empty": {"Authorization": ""},
        "scheme only": {"Authorization": "Bearer"},
        "basic": {"Authorization": "Basic dXNlcjpwYXNz"},
        "garbage": {"Authorization": "Bearer garbage"},
        "expired": {
            "Authorization": "Bearer " + api.token(student, lifetime=timedelta(seconds=-60))
        },
        "wrong audience": {"Authorization": "Bearer " + api.token(student, audience="other")},
        "wrong issuer": {"Authorization": "Bearer " + api.token(student, issuer="other")},
        "wrong key": {"Authorization": "Bearer " + api.token(student, key=other_key)},
        "unknown account": {"Authorization": "Bearer " + api.token("who-is-this")},
        "disabled account": {"Authorization": "Bearer " + api.token(disabled_subject)},
        "too long": {"Authorization": "Bearer " + "a" * 5000},
    }
    seen: dict[str, tuple[int, bytes, str | None, str | None]] = {}
    for name, headers in bad_headers.items():
        for path in ("/v1/me", "/v1/admin/questions", f"{QV}/{VID}/publish", "/v1/questions"):
            method = "POST" if path.endswith("publish") else "GET"
            response = api.client.request(method, path, headers=headers)
            assert response.status_code == 401, (name, path)
            seen[f"{name} {path}"] = problem_key(response)
    assert len(set(seen.values())) == 1, {k: v for k, v in seen.items()}
    status, body, content_type, challenge = next(iter(seen.values()))
    assert content_type == "application/problem+json"
    assert challenge == "Bearer"
    text = body.decode().lower()
    for word in ("expire", "signature", "audience", "issuer", "disabled", "unknown", "account"):
        assert word not in text, word
