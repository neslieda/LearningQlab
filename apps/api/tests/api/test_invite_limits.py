"""Staff invites are limited to a few uses (M1-G slice 9, D-65), over HTTP."""

from __future__ import annotations

import pytest
from sqlalchemy import text

from qlab.organizations.service import Role
from tests.api.support import ApiHarness

pytestmark = pytest.mark.db

INVITES = "/v1/admin/invites"


def create(api: ApiHarness, caller: Role, role: str, uses: int):  # type: ignore[no-untyped-def]
    return api.client.post(
        INVITES, headers=api.headers(caller), json={"role": role, "max_uses": uses}
    )


def count(api: ApiHarness) -> int:
    return int(api.session.execute(text("SELECT count(*) FROM invite")).scalar_one())


@pytest.mark.parametrize("role", ["reviewer", "content_admin", "platform_admin"])
def test_a_staff_invite_for_six_people_is_422(api: ApiHarness, role: str) -> None:
    response = create(api, Role.PLATFORM_ADMIN, role, 6)
    assert response.status_code == 422
    assert response.json()["code"] == "invite_uses_too_many"
    assert count(api) == 0
    assert create(api, Role.PLATFORM_ADMIN, role, 5).status_code == 201


def test_a_teacher_invite_for_a_student_may_have_200_uses(api: ApiHarness) -> None:
    response = create(api, Role.TEACHER, "student", 200)
    assert response.status_code == 201
    assert response.json()["max_uses"] == 200


def test_the_role_permission_is_checked_first(api: ApiHarness) -> None:
    response = create(api, Role.TEACHER, "reviewer", 200)
    assert response.status_code == 403
    assert response.json()["code"] == "invite_role_forbidden"
