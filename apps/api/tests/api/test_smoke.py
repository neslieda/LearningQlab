"""The harness works end to end: token, account, role, policy, handler."""

from __future__ import annotations

import pytest

from qlab.organizations.service import Role
from tests.api.support import ApiHarness

pytestmark = pytest.mark.db


def test_health_needs_no_token(api: ApiHarness) -> None:
    response = api.client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_me_returns_the_caller(api: ApiHarness) -> None:
    response = api.client.get("/v1/me", headers=api.headers(Role.REVIEWER))
    assert response.status_code == 200
    assert response.json() == {"account_id": api.actor(Role.REVIEWER), "roles": ["reviewer"]}


def test_no_token_is_401_and_a_missing_role_is_404(api: ApiHarness) -> None:
    assert api.client.get("/v1/me").status_code == 401
    denied = api.client.get("/v1/admin/questions", headers=api.headers(Role.STUDENT))
    unknown = api.client.get("/v1/nothing-here", headers=api.headers(Role.STUDENT))
    assert denied.status_code == unknown.status_code == 404
    assert denied.content == unknown.content
    assert denied.headers["content-type"] == "application/problem+json"
