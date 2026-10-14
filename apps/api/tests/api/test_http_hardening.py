"""Cross-cutting HTTP behaviour of the API that no single endpoint owns
(docs/slices/M1G-5-SOZLESME.md section 3.1 and the review round of the slice):

- request body size: decided in the policy layer after authorization and before the body is read;
- a trailing slash is not an endpoint (no redirect);
- `Cache-Control: no-store` on every response;
- the code parameters (path and query) accept one narrow alphabet and nothing else;
- a validation error never repeats what the caller sent.

Everything goes through HTTP. Content is seeded through the content service.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator
from typing import Any
from urllib.parse import quote

import pytest
from httpx2 import Response
from sqlalchemy import Connection
from sqlalchemy.orm import Session

from qlab.api import ids
from qlab.api.settings import Environment, Settings
from qlab.organizations.service import Role
from tests.api.support import ApiHarness, make_harness
from tests.api.test_learner_view import PUBLISHABLE, Published, publish_document
from tests.content.support import Env, create, document, make_env, stored_hash

pytestmark = [pytest.mark.db, pytest.mark.node]

Json = dict[str, Any]

QID = ids.encode(ids.QUESTION, uuid.uuid7())
VID = ids.encode(ids.QUESTION_VERSION, uuid.uuid7())
QV = "/v1/admin/question-versions"
CHECK_LIMIT = 64 * 1024
OTHER_LIMIT = 1024 * 1024
STAFF = (Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN)
JSON_TYPE = {"Content-Type": "application/json"}

# Every endpoint that can take a body, with a caller who is allowed to call it, and its limit.
# (method, path, role, limit)
BODY_ENDPOINTS: list[tuple[str, str, Role, int]] = [
    ("POST", f"/v1/questions/{QID}/check", Role.STUDENT, CHECK_LIMIT),
    ("PUT", f"{QV}/{VID}", Role.REVIEWER, OTHER_LIMIT),
    ("POST", f"{QV}/{VID}/submit", Role.REVIEWER, OTHER_LIMIT),
    ("POST", f"{QV}/{VID}/approve", Role.REVIEWER, OTHER_LIMIT),
    ("POST", f"{QV}/{VID}/request-changes", Role.REVIEWER, OTHER_LIMIT),
    ("POST", f"{QV}/{VID}/reject", Role.REVIEWER, OTHER_LIMIT),
    ("POST", f"/v1/admin/questions/{QID}/revisions", Role.REVIEWER, OTHER_LIMIT),
    ("POST", f"{QV}/{VID}/publish", Role.CONTENT_ADMIN, OTHER_LIMIT),
    ("POST", f"{QV}/{VID}/withdraw", Role.CONTENT_ADMIN, OTHER_LIMIT),
    ("POST", f"{QV}/{VID}/republish", Role.CONTENT_ADMIN, OTHER_LIMIT),
]
ENDPOINT_IDS = [f"{m} {p.split('/')[-1] if '/' in p else p}" for m, p, _, _ in BODY_ENDPOINTS]


def padded(size: int, value: Any = None) -> bytes:
    """A JSON document of exactly `size` bytes (trailing white space)."""
    raw = json.dumps({} if value is None else value).encode()
    assert len(raw) <= size
    return raw + b" " * (size - len(raw))


def send(
    api: ApiHarness,
    method: str,
    path: str,
    role: Role | None,
    *,
    content: Any = None,
    extra: dict[str, str] | None = None,
) -> Response:
    headers = api.headers(role) if role is not None else {}
    headers = {**headers, **JSON_TYPE, **(extra or {})}
    return api.client.request(method, path, content=content, headers=headers)


def problem(response: Response, status: int, code: str) -> None:
    assert response.status_code == status, response.text
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == code


def chunks() -> Iterator[bytes]:
    yield b'{"kind": '
    yield b'"mcq", "selected_key": "A"}'


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


@pytest.fixture
def mcq(api: ApiHarness, env: Env) -> Published:
    return publish_document(api.session, env, PUBLISHABLE["plain_mcq"](), tag="zzhx")


# =============================================================================================
# Body size
# =============================================================================================


@pytest.mark.parametrize(("method", "path", "role", "limit"), BODY_ENDPOINTS, ids=ENDPOINT_IDS)
def test_a_body_above_the_limit_is_413(
    api: ApiHarness, method: str, path: str, role: Role, limit: int
) -> None:
    response = send(api, method, path, role, content=padded(limit + 1))
    problem(response, 413, "payload_too_large")


@pytest.mark.parametrize(("method", "path", "role", "limit"), BODY_ENDPOINTS, ids=ENDPOINT_IDS)
def test_a_declared_length_above_the_limit_is_413_whatever_is_sent(
    api: ApiHarness, method: str, path: str, role: Role, limit: int
) -> None:
    """The decision is made on the announced length, before any of the body is read."""
    response = send(
        api, method, path, role, content=b"{}", extra={"Content-Length": str(limit + 1)}
    )
    problem(response, 413, "payload_too_large")
    huge = send(api, method, path, role, content=b"{}", extra={"Content-Length": "9" * 30})
    problem(huge, 413, "payload_too_large")


@pytest.mark.parametrize(("method", "path", "role", "limit"), BODY_ENDPOINTS, ids=ENDPOINT_IDS)
def test_a_body_of_exactly_the_limit_is_not_refused_for_its_size(
    api: ApiHarness, method: str, path: str, role: Role, limit: int
) -> None:
    response = send(api, method, path, role, content=padded(limit))
    assert response.status_code not in (411, 413), response.text
    assert response.json()["code"] != "payload_too_large"


def test_a_body_of_exactly_the_limit_gets_normal_validation(
    api: ApiHarness, mcq: Published
) -> None:
    # An invalid body of exactly the limit: validation, not size.
    for method, path, role, limit in (
        ("PUT", f"{QV}/{VID}", Role.REVIEWER, OTHER_LIMIT),
        ("POST", f"/v1/questions/{mcq.id}/check", Role.STUDENT, CHECK_LIMIT),
    ):
        response = send(api, method, path, role, content=padded(limit))
        problem(response, 422, "validation_failed")


def test_a_valid_check_of_exactly_the_limit_is_answered(api: ApiHarness, mcq: Published) -> None:
    body = padded(CHECK_LIMIT, {"kind": "mcq", "selected_key": "A"})
    assert len(body) == CHECK_LIMIT
    response = send(api, "POST", f"/v1/questions/{mcq.id}/check", Role.STUDENT, content=body)
    assert response.status_code == 200, response.text
    assert response.json()["kind"] == "mcq"
    over = padded(CHECK_LIMIT + 1, {"kind": "mcq", "selected_key": "A"})
    response = send(api, "POST", f"/v1/questions/{mcq.id}/check", Role.STUDENT, content=over)
    problem(response, 413, "payload_too_large")


def test_the_limit_of_the_check_endpoint_is_not_the_limit_of_the_others(
    api: ApiHarness,
) -> None:
    between = padded(CHECK_LIMIT + 1)  # too large for a check, fine for an edit
    edit = send(api, "PUT", f"{QV}/{VID}", Role.REVIEWER, content=between)
    problem(edit, 422, "validation_failed")
    check = send(api, "POST", f"/v1/questions/{QID}/check", Role.STUDENT, content=between)
    problem(check, 413, "payload_too_large")


@pytest.mark.parametrize(("method", "path", "role", "limit"), BODY_ENDPOINTS, ids=ENDPOINT_IDS)
def test_a_body_without_a_length_is_411(
    api: ApiHarness, method: str, path: str, role: Role, limit: int
) -> None:
    response = send(api, method, path, role, content=chunks())
    problem(response, 411, "length_required")


@pytest.mark.parametrize("declared", ["abc", "-1", "1.5", "0x10", "1e3", "12abc", "NaN", " "])
@pytest.mark.parametrize(
    ("method", "path", "role", "limit"), BODY_ENDPOINTS[:3], ids=ENDPOINT_IDS[:3]
)
def test_a_length_that_is_not_a_number_is_413(
    api: ApiHarness, method: str, path: str, role: Role, limit: int, declared: str
) -> None:
    response = send(api, method, path, role, content=b"{}", extra={"Content-Length": declared})
    problem(response, 413, "payload_too_large")


def test_a_get_with_an_announced_oversized_body_is_413_too(api: ApiHarness) -> None:
    response = send(
        api, "GET", "/v1/me", Role.STUDENT, extra={"Content-Length": str(OTHER_LIMIT + 1)}
    )
    problem(response, 413, "payload_too_large")


def test_a_request_without_a_body_is_not_a_length_problem(api: ApiHarness) -> None:
    response = api.client.get("/v1/me", headers=api.headers(Role.STUDENT))
    assert response.status_code == 200
    response = api.client.post(
        f"{QV}/{VID}/submit", headers=api.headers(Role.REVIEWER)
    )  # nothing to submit, but not a size problem
    assert response.status_code not in (411, 413)


@pytest.mark.parametrize(
    "shape", ["too_large", "no_length", "not_a_number"], ids=["413", "411", "413-nan"]
)
@pytest.mark.parametrize(("method", "path", "role", "limit"), BODY_ENDPOINTS, ids=ENDPOINT_IDS)
def test_authorization_comes_before_the_size_decision(
    api: ApiHarness, method: str, path: str, role: Role, limit: int, shape: str
) -> None:
    """No token: 401. A token without the role: 404. Never 411 or 413."""

    def request(caller: Role | None, *, with_token: bool = True) -> Response:
        kwargs: dict[str, Any]
        if shape == "too_large":
            kwargs = {"content": padded(limit + 1)}
        elif shape == "no_length":
            kwargs = {"content": chunks()}
        else:
            kwargs = {"content": b"{}", "extra": {"Content-Length": "abc"}}
        return send(api, method, path, caller if with_token else None, **kwargs)

    anonymous = request(None, with_token=False)
    problem(anonymous, 401, "unauthenticated")

    no_role = api.client.request(
        method,
        path,
        content=padded(limit + 1) if shape == "too_large" else None,
        headers={**api.headers(), **JSON_TYPE},
    )
    assert no_role.status_code == 404

    outsiders = [Role.STUDENT] if role is not Role.STUDENT else []
    if role is Role.CONTENT_ADMIN:
        outsiders.append(Role.REVIEWER)
    for outsider in outsiders:
        response = request(outsider)
        problem(response, 404, "not_found")
        unknown = api.client.get("/v1/nothing-here", headers=api.headers(outsider))
        assert response.content == unknown.content


def test_a_bad_token_with_an_oversized_body_is_401(api: ApiHarness) -> None:
    response = api.client.post(
        f"/v1/questions/{QID}/check",
        content=padded(CHECK_LIMIT + 1),
        headers={"Authorization": "Bearer garbage", **JSON_TYPE},
    )
    problem(response, 401, "unauthenticated")


def test_an_unknown_path_with_an_oversized_body_is_404(api: ApiHarness) -> None:
    response = send(
        api, "POST", "/v1/nothing-here", Role.PLATFORM_ADMIN, content=padded(OTHER_LIMIT + 1)
    )
    problem(response, 404, "not_found")


# =============================================================================================
# A trailing slash is not an endpoint
# =============================================================================================

SLASHED: list[tuple[str, str]] = [
    ("GET", "/healthz/"),
    ("GET", "/v1/me/"),
    ("GET", "/v1/questions/"),
    ("GET", "/v1/admin/questions/"),
    ("GET", "/v1/programs/ib_dp/subjects/physics/syllabus/"),
    ("GET", f"/v1/questions/{QID}/"),
    ("POST", f"/v1/questions/{QID}/check/"),
    ("GET", f"/v1/admin/questions/{QID}/"),
    ("POST", f"/v1/admin/questions/{QID}/revisions/"),
    ("GET", f"{QV}/{VID}/"),
    ("PUT", f"{QV}/{VID}/"),
    ("GET", f"{QV}/{VID}/history/"),
    ("POST", f"{QV}/{VID}/submit/"),
    ("POST", f"{QV}/{VID}/approve/"),
    ("POST", f"{QV}/{VID}/publish/"),
]


@pytest.mark.parametrize(("method", "path"), SLASHED, ids=[f"{m} {p}" for m, p in SLASHED])
@pytest.mark.parametrize("caller", [None, Role.STUDENT, Role.REVIEWER, Role.PLATFORM_ADMIN])
def test_a_trailing_slash_is_the_same_404_as_an_unknown_path(
    api: ApiHarness, method: str, path: str, caller: Role | None
) -> None:
    headers = api.headers(caller) if caller is not None else {}
    response = api.client.request(method, path, headers=headers, json={}, follow_redirects=False)
    unknown = api.client.request(
        method, "/v1/nothing-here", headers=headers, json={}, follow_redirects=False
    )
    assert response.status_code == 404
    assert response.history == []
    assert "location" not in response.headers
    assert response.content == unknown.content
    assert response.headers["content-type"] == unknown.headers["content-type"]


def test_the_real_path_still_works_next_to_its_slashed_twin(api: ApiHarness) -> None:
    headers = api.headers(Role.STUDENT)
    assert api.client.get("/v1/me", headers=headers).status_code == 200
    assert api.client.get("/v1/me/", headers=headers, follow_redirects=False).status_code == 404
    assert api.client.get("/healthz").status_code == 200
    assert api.client.get("/healthz/", follow_redirects=False).status_code == 404


# =============================================================================================
# Cache-Control: no-store on every response
# =============================================================================================


def test_every_kind_of_response_carries_no_store(api: ApiHarness, env: Env, mcq: Published) -> None:
    draft = create(api.session, env, document(PUBLISHABLE["plain_mcq"]()))
    student, reviewer, admin = (
        api.headers(r) for r in (Role.STUDENT, Role.REVIEWER, Role.CONTENT_ADMIN)
    )
    sha = stored_hash(api.session, draft.id)
    dvid = ids.encode(ids.QUESTION_VERSION, draft.id)
    responses: dict[str, Response] = {
        "200 health": api.client.get("/healthz"),
        "200 me": api.client.get("/v1/me", headers=student),
        "200 list": api.client.get("/v1/questions", headers=student),
        "200 read": api.client.get(f"/v1/questions/{mcq.id}", headers=student),
        "200 check": api.client.post(
            f"/v1/questions/{mcq.id}/check",
            headers=student,
            json={"kind": "mcq", "selected_key": "A"},
        ),
        "200 admin list": api.client.get("/v1/admin/questions", headers=reviewer),
        "200 submit": api.client.post(f"{QV}/{dvid}/submit", headers=reviewer),
        "201 revision": api.client.post(
            f"/v1/admin/questions/{ids.encode(ids.QUESTION, mcq.view.question_id)}/revisions",
            headers=reviewer,
        ),
        "401 no token": api.client.get("/v1/me"),
        "401 bad token": api.client.get("/v1/me", headers={"Authorization": "Bearer x"}),
        "404 unknown path": api.client.get("/v1/nothing-here"),
        "404 no role": api.client.get("/v1/me", headers=api.headers()),
        "404 not allowed": api.client.get("/v1/admin/questions", headers=student),
        "404 hidden": api.client.get(f"/v1/questions/{QID}", headers=student),
        "404 trailing slash": api.client.get("/v1/me/", headers=student),
        "404 method": api.client.delete("/v1/me", headers=student),
        "422 body": api.client.post(f"/v1/questions/{mcq.id}/check", headers=student, json={}),
        "422 query": api.client.get("/v1/questions", params={"limit": "0"}, headers=student),
        "422 code": api.client.get(
            "/v1/questions", params={"exam_section": "a b"}, headers=student
        ),
        "409 publish": api.client.post(
            f"{QV}/{dvid}/publish", headers=admin, json={"expected_content_sha256": sha}
        ),
        "413": send(
            api, "POST", f"/v1/questions/{QID}/check", Role.STUDENT, content=padded(CHECK_LIMIT + 1)
        ),
        "411": send(api, "POST", f"/v1/questions/{QID}/check", Role.STUDENT, content=chunks()),
    }
    expected = {
        "200 health": 200, "200 me": 200, "200 list": 200, "200 read": 200, "200 check": 200,
        "200 admin list": 200, "200 submit": 200, "201 revision": 201, "401 no token": 401,
        "401 bad token": 401, "404 unknown path": 404, "404 no role": 404, "404 not allowed": 404,
        "404 hidden": 404, "404 trailing slash": 404, "404 method": 404, "422 body": 422,
        "422 query": 422, "422 code": 422, "409 publish": 409, "413": 413,
        "411": 411,
    }  # fmt: skip
    for name, response in responses.items():
        assert response.status_code == expected[name], (name, response.status_code, response.text)
        assert response.headers.get("cache-control") == "no-store", name


def test_a_403_carries_no_store_too(connection: Connection, session: Session, env: Env) -> None:
    strict = make_harness(connection, session, settings=Settings(Environment.LOCAL, True))
    with strict.client:
        view = create(session, env, actor=strict.actor(Role.REVIEWER))
        version = ids.encode(ids.QUESTION_VERSION, view.id)
        strict.client.post(f"{QV}/{version}/submit", headers=strict.headers(Role.CONTENT_ADMIN))
        response = strict.client.post(
            f"{QV}/{version}/approve",
            headers=strict.headers(Role.REVIEWER),
            json={"expected_content_sha256": stored_hash(session, view.id)},
        )
        assert response.status_code == 403
        assert response.headers.get("cache-control") == "no-store"


# =============================================================================================
# Codes: path and query parameters
# =============================================================================================

BAD_CODES = [
    "",
    "-a",
    ".a",
    "_a",
    "a b",
    "a-b",
    "a;b",
    "<x>",
    "a'b",
    "a\nb",
    "a\n",
    "a\x00b",
    "\x00",
    "é",
    "ş1",
    "a" * 121,
]
GOOD_CODES = ["a", "A1", "0", "a.b_c", "1.2.3", "paper_2", "a" * 120]


def path_code(value: str) -> str:
    return quote(value, safe="")


@pytest.mark.parametrize("value", [v for v in BAD_CODES if v])
@pytest.mark.parametrize("slot", ["program", "subject"])
def test_a_bad_code_in_the_path_is_422_for_an_authorized_caller(
    api: ApiHarness, slot: str, value: str
) -> None:
    program, subject = ("ib_dp", "physics")
    if slot == "program":
        program = path_code(value)
    else:
        subject = path_code(value)
    response = api.client.get(
        f"/v1/programs/{program}/subjects/{subject}/syllabus", headers=api.headers(Role.STUDENT)
    )
    problem(response, 422, "validation_failed")
    assert value.strip() == "" or value not in response.text


@pytest.mark.parametrize("value", GOOD_CODES)
def test_a_good_code_in_the_path_is_not_a_validation_error(api: ApiHarness, value: str) -> None:
    response = api.client.get(
        f"/v1/programs/{value}/subjects/{value}/syllabus", headers=api.headers(Role.STUDENT)
    )
    problem(response, 404, "not_found")


@pytest.mark.parametrize("value", BAD_CODES)
def test_a_bad_syllabus_version_is_422(api: ApiHarness, value: str) -> None:
    response = api.client.get(
        "/v1/programs/ib_dp/subjects/physics/syllabus",
        params={"version": value},
        headers=api.headers(Role.STUDENT),
    )
    problem(response, 422, "validation_failed")


@pytest.mark.parametrize("value", GOOD_CODES)
def test_a_good_syllabus_version_is_not_a_validation_error(api: ApiHarness, value: str) -> None:
    response = api.client.get(
        "/v1/programs/ib_dp/subjects/physics/syllabus",
        params={"version": value},
        headers=api.headers(Role.STUDENT),
    )
    assert response.status_code == 404


LIST_URLS = [("/v1/questions", Role.STUDENT), ("/v1/admin/questions", Role.REVIEWER)]


@pytest.mark.parametrize(("url", "role"), LIST_URLS)
@pytest.mark.parametrize("name", ["exam_section", "syllabus_node"])
@pytest.mark.parametrize("value", BAD_CODES)
def test_a_bad_code_in_a_list_filter_is_422_never_500(
    api: ApiHarness, url: str, role: Role, name: str, value: str
) -> None:
    response = api.client.get(url, params={name: value}, headers=api.headers(role))
    problem(response, 422, "validation_failed")


@pytest.mark.parametrize(("url", "role"), LIST_URLS)
@pytest.mark.parametrize("name", ["exam_section", "syllabus_node"])
@pytest.mark.parametrize("value", GOOD_CODES)
def test_a_good_code_in_a_list_filter_is_an_ordinary_query(
    api: ApiHarness, url: str, role: Role, name: str, value: str
) -> None:
    response = api.client.get(url, params={name: value}, headers=api.headers(role))
    assert response.status_code == 200, response.text
    assert response.json()["items"] == []


@pytest.mark.parametrize(("url", "role"), LIST_URLS)
def test_a_raw_nul_byte_in_the_query_string_is_422(api: ApiHarness, url: str, role: Role) -> None:
    for name in ("exam_section", "syllabus_node"):
        response = api.client.get(f"{url}?{name}=abc%00def", headers=api.headers(role))
        problem(response, 422, "validation_failed")


def test_a_bad_code_does_not_reveal_endpoints_to_the_unauthorized(api: ApiHarness) -> None:
    for value in ("a\x00b", "a b", "a" * 121):
        none = api.client.get("/v1/admin/questions", params={"syllabus_node": value})
        assert none.status_code == 401
        student = api.client.get(
            "/v1/admin/questions",
            params={"syllabus_node": value},
            headers=api.headers(Role.STUDENT),
        )
        assert student.status_code == 404


# =============================================================================================
# Validation errors never repeat the caller's input
# =============================================================================================

NEEDLE = "zzreflectedneedle"


def test_an_unknown_kind_is_not_repeated(api: ApiHarness, mcq: Published) -> None:
    for kind in ("<script>x</script>", NEEDLE, "essay"):
        response = api.client.post(
            f"/v1/questions/{mcq.id}/check",
            headers=api.headers(Role.STUDENT),
            json={"kind": kind, "text": NEEDLE + "-answer"},
        )
        problem(response, 422, "validation_failed")
        assert "<script>" not in response.text
        assert NEEDLE not in response.text
        if kind != "essay":  # a word of the vocabulary may be named; invented text may not
            assert kind not in response.text


def test_an_unknown_kind_is_not_repeated_in_any_encoding(api: ApiHarness, mcq: Published) -> None:
    response = api.client.post(
        f"/v1/questions/{mcq.id}/check",
        headers=api.headers(Role.STUDENT),
        json={"kind": "<script>x</script>"},
    )
    for form in ("<script>", "\\u003cscript", "script>x", "&lt;script"):
        assert form not in response.text


@pytest.mark.parametrize(
    "body",
    [
        {"kind": "mcq", "selected_key": "A", f"{NEEDLE}key": 1},
        {"kind": "written", "part_id": "p-a", "text": "3.0 s", f"{NEEDLE}key": 1},
        {"kind": "mcq", "selected_key": "A", f"{NEEDLE}key": {"nested": NEEDLE}},
    ],
)
def test_an_invented_key_name_is_not_repeated_and_the_location_is_the_parents(
    api: ApiHarness, mcq: Published, body: Json
) -> None:
    response = api.client.post(
        f"/v1/questions/{mcq.id}/check", headers=api.headers(Role.STUDENT), json=body
    )
    problem(response, 422, "validation_failed")
    assert NEEDLE not in response.text
    items = response.json()["errors"]
    assert items
    for item in items:
        location = item.get("location")
        assert location is None or not location.endswith("key")
        assert NEEDLE not in json.dumps(item)


def test_the_location_of_an_unknown_key_is_that_of_the_object_that_holds_it(
    api: ApiHarness, mcq: Published
) -> None:
    clean = api.client.post(
        f"/v1/questions/{mcq.id}/check", headers=api.headers(Role.STUDENT), json={"kind": "mcq"}
    )
    unknown = api.client.post(
        f"/v1/questions/{mcq.id}/check",
        headers=api.headers(Role.STUDENT),
        json={"kind": "mcq", "selected_key": "A", "zzinvented": 1},
    )
    problem(clean, 422, "validation_failed")
    problem(unknown, 422, "validation_failed")
    # A missing field is located inside the object; an unknown key at the object itself.
    missing_location = clean.json()["errors"][0]["location"]
    unknown_location = unknown.json()["errors"][0]["location"]
    assert missing_location is not None
    assert missing_location.startswith(unknown_location or "")
    assert "zzinvented" not in (unknown_location or "")


def test_the_answer_text_is_never_in_a_validation_error(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, PUBLISHABLE["structured"](), tag="zzrefx")
    url = f"/v1/questions/{item.id}/check"
    headers = api.headers(Role.STUDENT)
    bodies = [
        {"kind": "written", "part_id": "p-a", "text": NEEDLE + "x" * 6000},  # too long
        {"kind": "written", "part_id": "", "text": NEEDLE},  # empty part id
        {"kind": "written", "part_id": "x" * 201, "text": NEEDLE},
        {"kind": "written", "part_id": "p-a", "text": NEEDLE, "other": NEEDLE},
        {"kind": "mcq", "selected_key": NEEDLE},
        {"kind": "mcq", "selected_key": NEEDLE, "text": NEEDLE},
        {"kind": "written", "part_id": NEEDLE, "text": NEEDLE},  # names no part
    ]
    for body in bodies:
        response = api.client.post(url, headers=headers, json=body)
        assert response.status_code == 422, (body, response.text)
        assert NEEDLE not in response.text, body


def test_an_unparsable_body_is_not_repeated(api: ApiHarness, mcq: Published) -> None:
    response = api.client.post(
        f"/v1/questions/{mcq.id}/check",
        content=('{"kind": "' + NEEDLE).encode(),
        headers={**api.headers(Role.STUDENT), **JSON_TYPE},
    )
    problem(response, 422, "validation_failed")
    assert NEEDLE not in response.text


@pytest.mark.parametrize(
    ("url", "role"), [("/v1/questions", Role.STUDENT), ("/v1/admin/questions", Role.REVIEWER)]
)
@pytest.mark.parametrize(
    "name", ["level", "question_class", "limit", "cursor", "status", "exam_section"]
)
def test_a_bad_query_value_is_not_repeated(
    api: ApiHarness, url: str, role: Role, name: str
) -> None:
    if name == "status" and role is Role.STUDENT:
        pytest.skip("the learner list has no status filter")
    value = NEEDLE if name != "exam_section" else NEEDLE + " "
    if name == "limit":
        value = NEEDLE + "7"
    response = api.client.get(url, params={name: value}, headers=api.headers(role))
    assert response.status_code == 422, (name, response.text)
    assert NEEDLE not in response.text


def test_a_bad_staff_body_is_not_repeated(api: ApiHarness) -> None:
    headers = api.headers(Role.REVIEWER)
    for path, body in (
        (f"{QV}/{VID}/reject", {"reason": 5, NEEDLE: NEEDLE}),
        (f"{QV}/{VID}/approve", {"expected_content_sha256": NEEDLE}),
        (f"{QV}/{VID}/request-changes", {"reason": [NEEDLE]}),
    ):
        response = api.client.post(path, headers=headers, json=body)
        assert response.status_code == 422, response.text
        assert NEEDLE not in response.text
    put = api.client.put(f"{QV}/{VID}", headers=headers, json={"document": {NEEDLE: NEEDLE}})
    assert put.status_code == 422
    assert NEEDLE not in put.text
