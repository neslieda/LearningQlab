"""Invites, SIGNED_IN access and the staff two-step check (M1-G slice 9).

Specification: docs/slices/M1G-9-ACILIS.md sections 3.2, 3.3 and 6 items 2 to 4; decision D-63;
the frozen contract (openapi.json, ENDPOINT_POLICY and `authorize`, migration 0006). Written
without reading the handlers.
"""

# ruff: noqa: S608 - the f-string SQL only interpolates a fixed sub-select

from __future__ import annotations

import hashlib
import json
import threading
import uuid
from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy import Connection, Engine, text
from sqlalchemy.orm import Session, sessionmaker

from qlab.api import ids
from qlab.api.app import create_app
from qlab.api.settings import Environment, Settings
from qlab.identity import service as identity
from qlab.identity.tokens import DEV_AUDIENCE, DEV_ISSUER, Claims, TokenVerifier
from qlab.organizations import service as organizations
from qlab.organizations.service import Role
from tests.api.support import ApiHarness

pytestmark = pytest.mark.db

INVITES = "/v1/admin/invites"
REDEEM = "/v1/invites/redeem"
INVITE_ID = r"^inv_[0-7][0123456789abcdefghjkmnpqrstvwxyz]{25}$"
UNKNOWN_CODE = "A" * 43
INVITE_KEYS = {
    "id",
    "role",
    "created_by",
    "created_at",
    "expires_at",
    "max_uses",
    "uses",
    "revoked_at",
}


# --- helpers ---------------------------------------------------------------------------------


def create_invite(
    api: ApiHarness, caller: tuple[Role, ...], role: str = "student", **body: Any
) -> Response:
    return api.client.post(INVITES, headers=api.headers(*caller), json={"role": role, **body})


def made(
    api: ApiHarness, caller: tuple[Role, ...] = (Role.TEACHER,), role: str = "student", **body: Any
) -> dict[str, Any]:
    response = create_invite(api, caller, role, **body)
    assert response.status_code == 201, response.text
    return dict(response.json())


def person(api: ApiHarness, name: str) -> dict[str, str]:
    """Headers of a signed-in person who has no account (the dev verifier accepts any subject)."""
    return {"Authorization": f"Bearer {api.token('person-' + name)}"}


def redeem(api: ApiHarness, headers: dict[str, str], code: str) -> Response:
    return api.client.post(REDEEM, headers=headers, json={"code": code})


def invite_rows(api: ApiHarness) -> list[Any]:
    api.session.expire_all()
    return list(api.session.execute(text("SELECT * FROM invite")).mappings())


def invite_row(api: ApiHarness, invite_id: str) -> Any:
    api.session.expire_all()
    return (
        api.session.execute(
            text("SELECT * FROM invite WHERE id = :id"),
            {"id": ids.decode(ids.INVITE, invite_id)},
        )
        .mappings()
        .one()
    )


def audit_rows(api: ApiHarness, action: str) -> dict[uuid.UUID, Any]:
    api.session.expire_all()
    rows = api.session.execute(
        text("SELECT id, actor, entity_type, entity_id, data FROM audit_log WHERE action = :a"),
        {"a": action},
    ).mappings()
    return {row["id"]: row for row in rows}


def row_text(row: Any) -> str:
    return " ".join([row["actor"], row["entity_type"], row["entity_id"], json.dumps(row["data"])])


def names(value: uuid.UUID) -> tuple[str, str]:
    """Both plausible spellings of an identifier in an audit entry."""
    return str(value), ids.encode(ids.INVITE, value)


# --- create ----------------------------------------------------------------------------------


def test_teacher_creates_student_invite_with_43_char_code(api: ApiHarness) -> None:
    response = create_invite(api, (Role.TEACHER,))
    assert response.status_code == 201
    body = response.json()
    assert set(body) >= INVITE_KEYS | {"code"}
    assert len(body["code"]) == 43
    assert body["role"] == "student"
    assert body["uses"] == 0
    assert body["max_uses"] == 1
    assert body["revoked_at"] is None
    assert body["created_by"] == api.actor(Role.TEACHER)
    expires = datetime.fromisoformat(body["expires_at"])
    created = datetime.fromisoformat(body["created_at"])
    assert timedelta(days=6, hours=23) < expires - created <= timedelta(days=7, minutes=5)


def test_codes_are_distinct(api: ApiHarness) -> None:
    codes = {made(api)["code"] for _ in range(5)}
    assert len(codes) == 5


@pytest.mark.parametrize(
    "role", ["student", "teacher", "reviewer", "content_admin", "platform_admin"]
)
def test_platform_admin_may_invite_any_invitable_role(api: ApiHarness, role: str) -> None:
    body = made(api, (Role.PLATFORM_ADMIN,), role)
    assert body["role"] == role


@pytest.mark.parametrize("role", ["teacher", "reviewer", "content_admin", "platform_admin"])
def test_teacher_may_not_invite_other_roles(api: ApiHarness, role: str) -> None:
    response = create_invite(api, (Role.TEACHER,), role)
    assert response.status_code == 403
    assert response.json()["code"] == "invite_role_forbidden"
    assert invite_rows(api) == []


@pytest.mark.parametrize("caller", [Role.STUDENT, Role.REVIEWER, Role.CONTENT_ADMIN])
def test_other_roles_cannot_create_invites(api: ApiHarness, caller: Role) -> None:
    response = create_invite(api, (caller,))
    assert response.status_code == 404
    assert invite_rows(api) == []


def test_create_needs_a_token_and_an_account(api: ApiHarness) -> None:
    assert api.client.post(INVITES, json={"role": "student"}).status_code == 401
    unknown = api.client.post(INVITES, headers=person(api, "x"), json={"role": "student"})
    assert unknown.status_code == 401


@pytest.mark.parametrize(
    "body",
    [
        {"role": "student", "expires_in_days": 0},
        {"role": "student", "expires_in_days": 31},
        {"role": "student", "max_uses": 0},
        {"role": "student", "max_uses": 201},
        {"role": "student", "max_uses": "many"},
        {"role": "org_admin"},
        {"role": "emperor"},
        {},
        {"role": "student", "surplus": 1},
    ],
)
def test_create_rejects_invalid_bodies(api: ApiHarness, body: dict[str, Any]) -> None:
    response = api.client.post(INVITES, headers=api.headers(Role.PLATFORM_ADMIN), json=body)
    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"
    assert invite_rows(api) == []


@pytest.mark.parametrize(("days", "uses"), [(1, 1), (30, 200)])
def test_create_accepts_the_bounds(api: ApiHarness, days: int, uses: int) -> None:
    body = made(api, expires_in_days=days, max_uses=uses)
    assert body["max_uses"] == uses
    expires = datetime.fromisoformat(body["expires_at"])
    created = datetime.fromisoformat(body["created_at"])
    assert timedelta(days=days - 1, hours=23) < expires - created <= timedelta(days=days, minutes=5)


def test_code_is_never_stored_only_its_sha256(api: ApiHarness) -> None:
    body = made(api)
    row = invite_row(api, body["id"])
    assert row["code_sha256"] == hashlib.sha256(body["code"].encode()).hexdigest()
    api.session.expire_all()
    everything = api.session.execute(text("SELECT t::text FROM invite t")).scalars().all()
    assert all(body["code"] not in line for line in everything)
    assert row["role"] == "student"
    assert row["created_by"] == api.actor(Role.TEACHER)


# --- list ------------------------------------------------------------------------------------


def test_list_is_newest_first_and_has_no_code(api: ApiHarness) -> None:
    created = [made(api)["id"] for _ in range(3)]
    response = api.client.get(INVITES, headers=api.headers(Role.TEACHER))
    assert response.status_code == 200
    page = response.json()
    assert [item["id"] for item in page["items"]] == created[::-1]
    assert page["next_cursor"] is None
    for item in page["items"]:
        assert set(item) == INVITE_KEYS
        assert "code" not in item


def test_list_pages_with_cursor(api: ApiHarness) -> None:
    created = [made(api)["id"] for _ in range(3)]
    first = api.client.get(INVITES, headers=api.headers(Role.TEACHER), params={"limit": 2}).json()
    assert [i["id"] for i in first["items"]] == created[::-1][:2]
    assert first["next_cursor"]
    second = api.client.get(
        INVITES,
        headers=api.headers(Role.TEACHER),
        params={"limit": 2, "cursor": first["next_cursor"]},
    ).json()
    assert [i["id"] for i in second["items"]] == created[::-1][2:]
    assert second["next_cursor"] is None


@pytest.mark.parametrize("limit", [0, 101])
def test_list_limit_bounds(api: ApiHarness, limit: int) -> None:
    response = api.client.get(INVITES, headers=api.headers(Role.TEACHER), params={"limit": limit})
    assert response.status_code == 422


def test_teacher_sees_only_own_invites_platform_admin_sees_all(api: ApiHarness) -> None:
    other = (Role.TEACHER, Role.STUDENT)  # a second teacher account
    mine = made(api)["id"]
    theirs = made(api, other)["id"]
    admin_own = made(api, (Role.PLATFORM_ADMIN,))["id"]
    seen = api.client.get(INVITES, headers=api.headers(Role.TEACHER)).json()["items"]
    assert [i["id"] for i in seen] == [mine]
    seen_other = api.client.get(INVITES, headers=api.headers(*other)).json()["items"]
    assert [i["id"] for i in seen_other] == [theirs]
    everything = api.client.get(INVITES, headers=api.headers(Role.PLATFORM_ADMIN)).json()["items"]
    assert [i["id"] for i in everything] == [admin_own, theirs, mine]


@pytest.mark.parametrize("caller", [Role.STUDENT, Role.REVIEWER, Role.CONTENT_ADMIN])
def test_other_roles_cannot_list(api: ApiHarness, caller: Role) -> None:
    assert api.client.get(INVITES, headers=api.headers(caller)).status_code == 404


# --- revoke ----------------------------------------------------------------------------------


def revoke(api: ApiHarness, invite_id: str, *caller: Role) -> Response:
    return api.client.post(f"{INVITES}/{invite_id}/revoke", headers=api.headers(*caller))


def test_owner_revokes_own_invite(api: ApiHarness) -> None:
    body = made(api)
    response = revoke(api, body["id"], Role.TEACHER)
    assert response.status_code == 200
    out = response.json()
    assert out["id"] == body["id"]
    assert out["revoked_at"] is not None
    assert "code" not in out
    row = invite_row(api, body["id"])
    assert row["revoked_at"] is not None
    assert row["revoked_by"] == api.actor(Role.TEACHER)


def test_teacher_cannot_revoke_anothers_invite_and_it_looks_like_unknown(api: ApiHarness) -> None:
    other = (Role.TEACHER, Role.STUDENT)
    theirs = made(api, other)
    refused = revoke(api, theirs["id"], Role.TEACHER)
    unknown = revoke(api, ids.encode(ids.INVITE, uuid.uuid4()), Role.TEACHER)
    assert refused.status_code == unknown.status_code == 404
    assert refused.content == unknown.content
    assert invite_row(api, theirs["id"])["revoked_at"] is None


def test_platform_admin_revokes_anyones_invite(api: ApiHarness) -> None:
    body = made(api)
    assert revoke(api, body["id"], Role.PLATFORM_ADMIN).status_code == 200
    assert invite_row(api, body["id"])["revoked_by"] == api.actor(Role.PLATFORM_ADMIN)


def test_revoking_twice_keeps_the_first_revocation(api: ApiHarness) -> None:
    body = made(api)
    first = revoke(api, body["id"], Role.TEACHER)
    assert first.status_code == 200
    before = invite_row(api, body["id"])
    second = revoke(api, body["id"], Role.TEACHER)
    assert second.status_code == 200
    after = invite_row(api, body["id"])
    assert after["revoked_at"] == before["revoked_at"]
    assert after["revoked_by"] == before["revoked_by"]
    assert second.json()["revoked_at"] == first.json()["revoked_at"]


def test_revoke_by_another_party_does_not_replace_first_revoker(api: ApiHarness) -> None:
    body = made(api)
    revoke(api, body["id"], Role.TEACHER)
    revoke(api, body["id"], Role.PLATFORM_ADMIN)
    assert invite_row(api, body["id"])["revoked_by"] == api.actor(Role.TEACHER)


def test_revoke_malformed_id_and_wrong_roles(api: ApiHarness) -> None:
    body = made(api)
    assert revoke(api, "not-an-id", Role.TEACHER).status_code == 422
    for caller in (Role.STUDENT, Role.REVIEWER, Role.CONTENT_ADMIN):
        assert revoke(api, body["id"], caller).status_code == 404
    assert api.client.post(f"{INVITES}/{body['id']}/revoke").status_code == 401
    assert invite_row(api, body["id"])["revoked_at"] is None


# --- redeem ----------------------------------------------------------------------------------


def test_redeem_creates_the_account_with_the_role(api: ApiHarness) -> None:
    body = made(api, (Role.PLATFORM_ADMIN,), "teacher")
    headers = person(api, "alice")
    assert api.client.get("/v1/me", headers=headers).status_code == 401  # no account yet
    response = redeem(api, headers, body["code"])
    assert response.status_code == 200, response.text
    out = response.json()
    assert out["roles"] == ["teacher"]
    assert out["account_id"].startswith("acc_")
    me = api.client.get("/v1/me", headers=headers)
    assert me.status_code == 200
    assert me.json() == {"account_id": out["account_id"], "roles": ["teacher"]}
    assert invite_row(api, body["id"])["uses"] == 1


def test_redeemed_teacher_role_works_on_teacher_endpoints(api: ApiHarness) -> None:
    body = made(api, (Role.PLATFORM_ADMIN,), "teacher")
    headers = person(api, "bob")
    redeem(api, headers, body["code"])
    assert api.client.get(INVITES, headers=headers).status_code == 200


def test_same_person_twice_counts_once(api: ApiHarness) -> None:
    body = made(api, max_uses=3)
    headers = person(api, "carol")
    first = redeem(api, headers, body["code"])
    second = redeem(api, headers, body["code"])
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert invite_row(api, body["id"])["uses"] == 1
    count = api.session.execute(text("SELECT count(*) FROM invite_redemption")).scalar_one()
    assert count == 1
    # The remaining uses are still available to other people.
    assert redeem(api, person(api, "dave"), body["code"]).status_code == 200
    assert invite_row(api, body["id"])["uses"] == 2


@pytest.mark.parametrize("state", ["used_up", "expired", "revoked"])
def test_same_person_repeat_redeem_still_succeeds_on_an_unusable_invite(
    api: ApiHarness, state: str
) -> None:
    body = made(api)
    headers = person(api, "repeat-" + state)
    first = redeem(api, headers, body["code"])
    assert first.status_code == 200, first.text
    before = len(audit_rows(api, "invite.redeemed"))
    if state == "used_up":
        assert redeem(api, person(api, "other-" + state), body["code"]).status_code == 404
    elif state == "expired":
        api.session.execute(
            text(
                "UPDATE invite SET created_at = now() - interval '3 days', "
                "expires_at = now() - interval '1 second' WHERE id = :id"
            ),
            {"id": ids.decode(ids.INVITE, body["id"])},
        )
    else:
        assert revoke(api, body["id"], Role.TEACHER).status_code in (200, 204)
    again = redeem(api, headers, body["code"])
    assert again.status_code == 200, again.text
    assert again.json() == first.json()
    assert invite_row(api, body["id"])["uses"] == 1
    count = api.session.execute(text("SELECT count(*) FROM invite_redemption")).scalar_one()
    assert count == 1
    assert len(audit_rows(api, "invite.redeemed")) == before


def test_repeat_redeem_returns_the_current_roles(api: ApiHarness) -> None:
    body = made(api, max_uses=2)
    headers = person(api, "grown")
    first = redeem(api, headers, body["code"])
    assert first.json()["roles"] == ["student"]
    account = ids.decode(ids.ACCOUNT, first.json()["account_id"])
    api.session.execute(
        text(
            "INSERT INTO role_assignment (id, account_id, role, granted_by) "
            "VALUES (gen_random_uuid(), :a, 'teacher', 'system:test')"
        ),
        {"a": account},
    )
    again = redeem(api, headers, body["code"])
    assert again.status_code == 200, again.text
    assert sorted(again.json()["roles"]) == ["student", "teacher"]


def test_second_person_on_single_use_invite_gets_404(api: ApiHarness) -> None:
    body = made(api)
    assert redeem(api, person(api, "erin"), body["code"]).status_code == 200
    refused = redeem(api, person(api, "frank"), body["code"])
    assert refused.status_code == 404
    assert refused.json()["code"] == "invite_not_found"
    assert invite_row(api, body["id"])["uses"] == 1
    # And no account came to exist for the refused person.
    assert api.client.get("/v1/me", headers=person(api, "frank")).status_code == 401


def test_max_uses_is_honoured(api: ApiHarness) -> None:
    body = made(api, max_uses=2)
    statuses = [redeem(api, person(api, f"p{n}"), body["code"]).status_code for n in range(4)]
    assert statuses == [200, 200, 404, 404]


def test_expired_invite_is_404(api: ApiHarness) -> None:
    body = made(api)
    api.session.execute(
        text(
            "UPDATE invite SET created_at = now() - interval '3 days', "
            "expires_at = now() - interval '1 second' WHERE id = :id"
        ),
        {"id": ids.decode(ids.INVITE, body["id"])},
    )
    response = redeem(api, person(api, "gina"), body["code"])
    assert response.status_code == 404
    assert response.json()["code"] == "invite_not_found"
    assert invite_row(api, body["id"])["uses"] == 0


def test_revoked_invite_is_404(api: ApiHarness) -> None:
    body = made(api)
    revoke(api, body["id"], Role.TEACHER)
    response = redeem(api, person(api, "hank"), body["code"])
    assert response.status_code == 404
    assert response.json()["code"] == "invite_not_found"


def test_unknown_code_is_404(api: ApiHarness) -> None:
    response = redeem(api, person(api, "ivy"), UNKNOWN_CODE)
    assert response.status_code == 404
    assert response.json()["code"] == "invite_not_found"


def test_all_refusals_are_byte_identical(api: ApiHarness) -> None:
    expired = made(api)
    api.session.execute(
        text(
            "UPDATE invite SET created_at = now() - interval '3 days', "
            "expires_at = now() - interval '1 second' WHERE id = :id"
        ),
        {"id": ids.decode(ids.INVITE, expired["id"])},
    )
    revoked = made(api)
    revoke(api, revoked["id"], Role.TEACHER)
    used_up = made(api)
    redeem(api, person(api, "first"), used_up["code"])
    headers = person(api, "judge")
    bodies = {
        "unknown": redeem(api, headers, UNKNOWN_CODE),
        "expired": redeem(api, headers, expired["code"]),
        "revoked": redeem(api, headers, revoked["code"]),
        "used up": redeem(api, headers, used_up["code"]),
    }
    assert {r.status_code for r in bodies.values()} == {404}
    assert len({r.content for r in bodies.values()}) == 1
    assert len({r.headers["content-type"] for r in bodies.values()}) == 1


def test_redeem_validates_the_code_shape(api: ApiHarness) -> None:
    headers = person(api, "kim")
    for code in ("", "short", "A" * 42, "A" * 44, "!" * 43):
        assert redeem(api, headers, code).status_code == 422
    assert api.client.post(REDEEM, headers=headers, json={}).status_code == 422


def test_redeem_needs_a_valid_token(api: ApiHarness) -> None:
    assert api.client.post(REDEEM, json={"code": UNKNOWN_CODE}).status_code == 401
    bad = {"Authorization": "Bearer not-a-token"}
    assert redeem(api, bad, UNKNOWN_CODE).status_code == 401
    other_key = Ed25519PrivateKey.generate()
    forged = {"Authorization": f"Bearer {api.token('x', key=other_key)}"}
    assert redeem(api, forged, UNKNOWN_CODE).status_code == 401


def test_an_existing_role_is_kept_not_duplicated(api: ApiHarness) -> None:
    body = made(api)
    headers = api.headers(Role.STUDENT)
    out = redeem(api, headers, body["code"])
    assert out.status_code == 200
    assert out.json()["roles"] == ["student"]
    assert api.client.get("/v1/me", headers=headers).json()["roles"] == ["student"]


def test_redeeming_adds_the_role_to_an_existing_account(api: ApiHarness) -> None:
    body = made(api, (Role.PLATFORM_ADMIN,), "teacher")
    headers = api.headers(Role.STUDENT)
    out = redeem(api, headers, body["code"])
    assert out.status_code == 200
    assert "teacher" in out.json()["roles"]
    assert "student" in out.json()["roles"]


def test_an_account_without_roles_can_redeem(api: ApiHarness) -> None:
    body = made(api)
    headers = api.headers()  # an account with no role at all
    assert redeem(api, headers, body["code"]).status_code == 200
    assert api.client.get("/v1/me", headers=headers).json()["roles"] == ["student"]


def test_signed_in_without_account_reaches_only_redeem(api: ApiHarness) -> None:
    headers = person(api, "nobody")
    assert api.client.get("/v1/me", headers=headers).status_code == 401
    assert api.client.get("/v1/questions", headers=headers).status_code == 401
    assert api.client.get(INVITES, headers=headers).status_code == 401
    assert api.client.get("/v1/admin/questions", headers=headers).status_code == 401
    # Redeem answers (404 for a bad code, never 401): the token alone is enough.
    assert redeem(api, headers, UNKNOWN_CODE).status_code == 404


def test_an_account_without_roles_reaches_only_redeem(api: ApiHarness) -> None:
    headers = api.headers()
    assert api.client.get("/v1/me", headers=headers).status_code == 404
    assert api.client.get("/v1/questions", headers=headers).status_code == 404
    assert api.client.get(INVITES, headers=headers).status_code == 404
    assert redeem(api, headers, UNKNOWN_CODE).status_code == 404


def test_disabled_account_gets_401_on_redeem(api: ApiHarness) -> None:
    body = made(api)
    account = api.account(Role.STUDENT)
    headers = api.headers(Role.STUDENT)
    assert identity.disable_account(api.session, account)
    api.session.flush()
    assert redeem(api, headers, body["code"]).status_code == 401
    assert redeem(api, headers, UNKNOWN_CODE).status_code == 401
    assert invite_row(api, body["id"])["uses"] == 0


# --- audit -----------------------------------------------------------------------------------


def new_entries(api: ApiHarness, action: str, before: dict[uuid.UUID, Any]) -> list[Any]:
    return [row for key, row in audit_rows(api, action).items() if key not in before]


def test_create_revoke_redeem_are_audited_without_the_code(api: ApiHarness) -> None:
    before = {
        a: audit_rows(api, a) for a in ("invite.created", "invite.revoked", "invite.redeemed")
    }

    body = made(api, (Role.PLATFORM_ADMIN,), "teacher", max_uses=2)
    invite_uuid = ids.decode(ids.INVITE, body["id"])
    created = new_entries(api, "invite.created", before["invite.created"])
    assert len(created) == 1
    assert created[0]["actor"] == api.actor(Role.PLATFORM_ADMIN)
    assert any(n in row_text(created[0]) for n in names(invite_uuid))
    assert "teacher" in row_text(created[0])

    headers = person(api, "lena")
    out = redeem(api, headers, body["code"]).json()
    redeemed = new_entries(api, "invite.redeemed", before["invite.redeemed"])
    assert len(redeemed) == 1
    text_ = row_text(redeemed[0])
    assert any(n in text_ for n in names(invite_uuid))
    assert "teacher" in text_
    account_uuid = ids.decode(ids.ACCOUNT, out["account_id"])
    assert str(account_uuid) in text_ or out["account_id"] in text_

    # A repeat by the same person is not a second redemption.
    redeem(api, headers, body["code"])
    assert len(new_entries(api, "invite.redeemed", before["invite.redeemed"])) == 1

    revoke(api, body["id"], Role.PLATFORM_ADMIN)
    revoked = new_entries(api, "invite.revoked", before["invite.revoked"])
    assert len(revoked) == 1
    assert revoked[0]["actor"] == api.actor(Role.PLATFORM_ADMIN)
    assert any(n in row_text(revoked[0]) for n in names(invite_uuid))

    for row in created + redeemed + revoked:
        assert body["code"] not in row_text(row)
        assert hashlib.sha256(body["code"].encode()).hexdigest() not in row_text(row)


def test_refused_requests_write_no_audit_entry(api: ApiHarness) -> None:
    before = {a: audit_rows(api, a) for a in ("invite.created", "invite.redeemed")}
    create_invite(api, (Role.TEACHER,), "reviewer")
    redeem(api, person(api, "mia"), UNKNOWN_CODE)
    assert audit_rows(api, "invite.created") == before["invite.created"]
    assert audit_rows(api, "invite.redeemed") == before["invite.redeemed"]


# --- concurrency -----------------------------------------------------------------------------


@pytest.fixture
def committed(throwaway_engine: Engine) -> Iterator[tuple[Engine, TestClient, list[str]]]:
    """The application on real, committed connections (the harness shares one transaction, which
    cannot show a race), on a database made for this test and dropped after it, so nothing it
    commits (audit entries are append-only) reaches other tests."""
    engine = throwaway_engine
    key = Ed25519PrivateKey.generate()
    settings = Settings(environment=Environment.LOCAL, forbid_self_approval=False)
    factory = sessionmaker(bind=engine)
    app = create_app(
        settings,
        verifier=TokenVerifier(
            public_keys=[key.public_key()], issuer=DEV_ISSUER, audience=DEV_AUDIENCE
        ),
        session_factory=factory,
        check_renderer=False,
    )
    from qlab.identity.tokens import sign

    def token(subject: str) -> str:
        return sign(
            key,
            issuer=DEV_ISSUER,
            audience=DEV_AUDIENCE,
            subject=subject,
            lifetime=timedelta(minutes=5),
            now=datetime.now(tz=UTC),
        )

    tag = uuid.uuid4().hex[:12]
    with factory() as session:
        admin = identity.ensure_account(session, issuer=DEV_ISSUER, subject=f"conc-{tag}-admin")
        organizations.grant(
            session, account_id=admin.id, role=Role.PLATFORM_ADMIN, granted_by="system:test"
        )
        session.commit()
    client = TestClient(app, raise_server_exceptions=False)
    client.token = token  # type: ignore[attr-defined]
    client.tag = tag  # type: ignore[attr-defined]
    yield engine, client, [tag]


def run_race(client: TestClient, code: str, tag: str, contenders: int) -> list[int]:
    barrier = threading.Barrier(contenders)
    statuses: list[int] = [0] * contenders

    def go(index: int) -> None:
        headers = {"Authorization": f"Bearer {client.token(f'conc-{tag}-p{index}')}"}  # type: ignore[attr-defined]
        barrier.wait(timeout=30)
        statuses[index] = client.post(REDEEM, headers=headers, json={"code": code}).status_code

    threads = [threading.Thread(target=go, args=(i,)) for i in range(contenders)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    return statuses


@pytest.mark.parametrize(("max_uses", "contenders"), [(1, 2), (1, 8), (3, 8)])
def test_parallel_redemptions_never_exceed_max_uses(
    committed: tuple[Engine, TestClient, list[str]], max_uses: int, contenders: int
) -> None:
    engine, client, (tag,) = committed
    admin_headers = {"Authorization": f"Bearer {client.token(f'conc-{tag}-admin')}"}  # type: ignore[attr-defined]
    created = client.post(
        INVITES, headers=admin_headers, json={"role": "student", "max_uses": max_uses}
    )
    assert created.status_code == 201, created.text
    body = created.json()
    statuses = run_race(client, body["code"], tag, contenders)
    assert sorted(statuses) == sorted([200] * max_uses + [404] * (contenders - max_uses))
    with engine.connect() as connection:
        uses = connection.execute(
            text("SELECT uses FROM invite WHERE id = :id"),
            {"id": ids.decode(ids.INVITE, body["id"])},
        ).scalar_one()
        redemptions = connection.execute(
            text("SELECT count(*) FROM invite_redemption WHERE invite_id = :id"),
            {"id": ids.decode(ids.INVITE, body["id"])},
        ).scalar_one()
    assert uses == redemptions == max_uses


# --- staff two-step check --------------------------------------------------------------------

STAFF_ORG = "org-staff-123"
STAFF_ENDPOINT = "/v1/admin/questions"
EVERYONE_ENDPOINT = "/v1/me"


class OrgVerifier(TokenVerifier):
    """The development verifier plus an organisation claim chosen by the test, per subject."""

    def __init__(self, inner: TokenVerifier) -> None:
        super().__init__(
            public_keys=list(inner._keys),  # noqa: SLF001
            issuer=inner.issuer,
            audience=inner.audience,
        )
        self.organizations: dict[str, str | None] = {}

    def verify(self, token: str) -> Claims:
        claims = super().verify(token)
        return replace(claims, organization=self.organizations.get(claims.subject))


@pytest.fixture
def mfa(connection: Connection, session: Session) -> Iterator[tuple[ApiHarness, OrgVerifier]]:
    key = Ed25519PrivateKey.generate()
    settings = Settings(
        environment=Environment.LOCAL, forbid_self_approval=False, staff_organization=STAFF_ORG
    )
    verifier = OrgVerifier(
        TokenVerifier(public_keys=[key.public_key()], issuer=DEV_ISSUER, audience=DEV_AUDIENCE)
    )
    app = create_app(
        settings,
        verifier=verifier,
        session_factory=sessionmaker(bind=connection, join_transaction_mode="create_savepoint"),
        check_renderer=False,
    )
    client = TestClient(app, raise_server_exceptions=False)
    harness = ApiHarness(client=client, session=session, key=key, settings=settings)
    with client:
        yield harness, verifier


def sign_in(
    harness: ApiHarness, verifier: OrgVerifier, *roles: Role, org: str | None
) -> dict[str, str]:
    subject = harness.subject(*roles)
    verifier.organizations[subject] = org
    return {"Authorization": f"Bearer {harness.token(subject)}"}


@pytest.mark.parametrize("staff_role", [Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN])
@pytest.mark.parametrize("org", [None, "org-learners-999", STAFF_ORG + " ", STAFF_ORG.upper()])
def test_staff_without_staff_organisation_gets_mfa_required(
    mfa: tuple[ApiHarness, OrgVerifier], staff_role: Role, org: str | None
) -> None:
    harness, verifier = mfa
    headers = sign_in(harness, verifier, staff_role, org=org)
    response = harness.client.get(STAFF_ENDPOINT, headers=headers)
    assert response.status_code == 403
    assert response.json()["code"] == "mfa_required"


@pytest.mark.parametrize("staff_role", [Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN])
def test_staff_with_staff_organisation_is_allowed(
    mfa: tuple[ApiHarness, OrgVerifier], staff_role: Role
) -> None:
    harness, verifier = mfa
    headers = sign_in(harness, verifier, staff_role, org=STAFF_ORG)
    assert harness.client.get(STAFF_ENDPOINT, headers=headers).status_code == 200


def test_staff_who_also_hold_a_learner_role_are_fine_on_an_everyone_endpoint(
    mfa: tuple[ApiHarness, OrgVerifier],
) -> None:
    harness, verifier = mfa
    headers = sign_in(harness, verifier, Role.PLATFORM_ADMIN, Role.STUDENT, org="org-learners-999")
    assert harness.client.get(EVERYONE_ENDPOINT, headers=headers).status_code == 200
    assert harness.client.get(STAFF_ENDPOINT, headers=headers).status_code == 403


def test_staff_only_caller_outside_staff_org_is_refused_on_every_endpoint(
    mfa: tuple[ApiHarness, OrgVerifier],
) -> None:
    harness, verifier = mfa
    headers = sign_in(harness, verifier, Role.PLATFORM_ADMIN, org="org-learners-999")
    for path in ("/v1/me", "/v1/questions", STAFF_ENDPOINT, INVITES):
        response = harness.client.get(path, headers=headers)
        assert response.status_code == 403, path
        assert response.json()["code"] == "mfa_required", path


def test_mfa_required_is_not_a_not_found(mfa: tuple[ApiHarness, OrgVerifier]) -> None:
    """Without a staff role, the answer stays 404 (nothing is revealed); 403 is only for those
    whose staff roles were the reason."""
    harness, verifier = mfa
    for roles in ((Role.STUDENT,), (Role.TEACHER,), ()):
        headers = sign_in(harness, verifier, *roles, org="org-learners-999")
        assert harness.client.get(STAFF_ENDPOINT, headers=headers).status_code == 404


def test_teacher_is_unaffected(mfa: tuple[ApiHarness, OrgVerifier]) -> None:
    harness, verifier = mfa
    for org in (None, "org-learners-999", STAFF_ORG):
        headers = sign_in(harness, verifier, Role.TEACHER, org=org)
        assert harness.client.get(INVITES, headers=headers).status_code == 200
        created = harness.client.post(INVITES, headers=headers, json={"role": "student"})
        assert created.status_code == 201


def test_staff_endpoint_with_a_teacher_in_the_wrong_organisation_is_404(
    mfa: tuple[ApiHarness, OrgVerifier],
) -> None:
    harness, verifier = mfa
    headers = sign_in(harness, verifier, Role.TEACHER, org="org-learners-999")
    assert harness.client.get(STAFF_ENDPOINT, headers=headers).status_code == 404


def test_staff_role_is_ignored_for_the_request_when_not_in_staff_organisation(
    mfa: tuple[ApiHarness, OrgVerifier],
) -> None:
    """A teacher who also holds platform_admin, signed in outside the staff organisation, acts
    as a teacher only: teacher endpoints work, platform_admin powers do not."""
    harness, verifier = mfa
    both = (Role.TEACHER, Role.PLATFORM_ADMIN)
    headers = sign_in(harness, verifier, *both, org="org-learners-999")
    assert harness.client.get(INVITES, headers=headers).status_code == 200
    assert harness.client.get(STAFF_ENDPOINT, headers=headers).status_code == 403
    forbidden = harness.client.post(INVITES, headers=headers, json={"role": "reviewer"})
    assert forbidden.status_code == 403
    assert forbidden.json()["code"] == "invite_role_forbidden"
    # In the staff organisation the same account may invite a reviewer.
    staff_headers = sign_in(harness, verifier, *both, org=STAFF_ORG)
    allowed = harness.client.post(INVITES, headers=staff_headers, json={"role": "reviewer"})
    assert allowed.status_code == 201


def test_platform_admin_outside_staff_organisation_cannot_use_invite_admin(
    mfa: tuple[ApiHarness, OrgVerifier],
) -> None:
    """Platform admin is the only allowing role here and it is a staff role: mfa_required."""
    harness, verifier = mfa
    headers = sign_in(harness, verifier, Role.PLATFORM_ADMIN, org=None)
    response = harness.client.get(INVITES, headers=headers)
    assert response.status_code == 403
    assert response.json()["code"] == "mfa_required"


def test_redeem_works_without_any_organisation(mfa: tuple[ApiHarness, OrgVerifier]) -> None:
    harness, verifier = mfa
    admin = sign_in(harness, verifier, Role.PLATFORM_ADMIN, org=STAFF_ORG)
    code = harness.client.post(INVITES, headers=admin, json={"role": "student"}).json()["code"]
    newcomer = {"Authorization": f"Bearer {harness.token('person-orgless')}"}
    response = harness.client.post(REDEEM, headers=newcomer, json={"code": code})
    assert response.status_code == 200


def test_staff_invite_redeemed_outside_staff_org_works_but_stays_gated(
    mfa: tuple[ApiHarness, OrgVerifier],
) -> None:
    harness, verifier = mfa
    admin = sign_in(harness, verifier, Role.PLATFORM_ADMIN, org=STAFF_ORG)
    code = harness.client.post(INVITES, headers=admin, json={"role": "reviewer"}).json()["code"]
    verifier.organizations["person-newrev"] = "org-learners-999"
    headers = {"Authorization": f"Bearer {harness.token('person-newrev')}"}
    response = harness.client.post(REDEEM, headers=headers, json={"code": code})
    assert response.status_code == 200, response.text
    assert response.json()["roles"] == ["reviewer"]
    for path in (STAFF_ENDPOINT, EVERYONE_ENDPOINT):
        refused = harness.client.get(path, headers=headers)
        assert refused.status_code == 403, path
        assert refused.json()["code"] == "mfa_required", path
    verifier.organizations["person-newrev"] = STAFF_ORG
    for path in (STAFF_ENDPOINT, EVERYONE_ENDPOINT):
        assert harness.client.get(path, headers=headers).status_code == 200, path
