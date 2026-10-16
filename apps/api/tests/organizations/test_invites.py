"""The invite service (M1-G slice 9, D-63): codes, roles, redemption rules. The HTTP side is in
tests/api/test_invites_spec.py."""

from __future__ import annotations

import hashlib
import uuid
from datetime import timedelta

import pytest
from sqlalchemy import Connection, text
from sqlalchemy.orm import Session

from qlab.identity import service as identity
from qlab.organizations import service as organizations
from qlab.organizations.service import Role

pytestmark = pytest.mark.db

ISSUER = "https://issuer.example.invalid"
TEACHER = "acc_teacher"
ADMIN = "cli:owner"


def new_invite(
    session: Session,
    *,
    roles: frozenset[Role] = frozenset({Role.PLATFORM_ADMIN}),
    role: Role = Role.STUDENT,
    max_uses: int = 1,
    created_by: str = ADMIN,
) -> tuple[organizations.InviteView, str]:
    return organizations.create_invite(
        session,
        created_by=created_by,
        creator_roles=roles,
        role=role,
        expires_in_days=7,
        max_uses=max_uses,
    )


def person() -> str:
    return f"u-{uuid.uuid4().hex}"


def test_only_the_hash_of_the_code_is_stored(session: Session, connection: Connection) -> None:
    view, code = new_invite(session)
    assert len(code) == 43
    stored = connection.execute(
        text("SELECT code_sha256 FROM invite WHERE id = :i"), {"i": view.id}
    ).scalar_one()
    assert stored == hashlib.sha256(code.encode()).hexdigest()
    assert code not in str(connection.execute(text("SELECT invite::text FROM invite")).all())


def test_role_rules(session: Session) -> None:
    teacher = frozenset({Role.TEACHER})
    new_invite(session, roles=teacher, role=Role.STUDENT, created_by=TEACHER)
    for role in (Role.TEACHER, Role.REVIEWER, Role.PLATFORM_ADMIN, Role.ORG_ADMIN):
        with pytest.raises(organizations.InviteRoleForbidden):
            new_invite(session, roles=teacher, role=role, created_by=TEACHER)
    for role in (Role.STUDENT, Role.TEACHER, Role.REVIEWER, Role.CONTENT_ADMIN):
        new_invite(session, role=role)
    with pytest.raises(organizations.InviteRoleForbidden):
        new_invite(session, role=Role.ORG_ADMIN)  # not before organisations exist
    with pytest.raises(organizations.InviteRoleForbidden):
        new_invite(session, roles=frozenset({Role.STUDENT, Role.REVIEWER}))


def test_redeem_opens_the_account_and_grants_the_role(session: Session) -> None:
    _, code = new_invite(session, role=Role.TEACHER)
    subject = person()
    result = organizations.redeem_invite(session, issuer=ISSUER, subject=subject, code=code)
    assert result.counted and result.granted
    assert result.roles == {Role.TEACHER}
    account = identity.find_account(session, issuer=ISSUER, subject=subject)
    assert account is not None and account.id == result.account_id


def test_the_same_person_counts_once_and_keeps_a_revoked_role_revoked(session: Session) -> None:
    _, code = new_invite(session, max_uses=5)
    subject = person()
    first = organizations.redeem_invite(session, issuer=ISSUER, subject=subject, code=code)
    organizations.revoke(
        session, account_id=first.account_id, role=Role.STUDENT, revoked_by="system:test"
    )
    again = organizations.redeem_invite(session, issuer=ISSUER, subject=subject, code=code)
    assert not again.counted and not again.granted
    assert again.roles == frozenset()
    assert session.execute(text("SELECT uses FROM invite")).scalar_one() == 1


def test_every_refusal_is_the_same_error_and_writes_nothing(
    session: Session, connection: Connection
) -> None:
    expired, expired_code = new_invite(session)
    revoked, revoked_code = new_invite(session)
    _, used_code = new_invite(session)
    connection.execute(
        text(
            "UPDATE invite SET created_at = now() - interval '2 days', "
            "expires_at = now() - interval '1 day' WHERE id = :i"
        ),
        {"i": expired.id},
    )
    organizations.revoke_invite(
        session, invite_id=revoked.id, actor=ADMIN, roles=frozenset({Role.PLATFORM_ADMIN})
    )
    organizations.redeem_invite(session, issuer=ISSUER, subject=person(), code=used_code)
    accounts = connection.execute(text("SELECT count(*) FROM account")).scalar_one()
    for code in (expired_code, revoked_code, used_code, "A" * 43, ""):
        with pytest.raises(organizations.InviteNotFound):
            organizations.redeem_invite(session, issuer=ISSUER, subject=person(), code=code)
    assert connection.execute(text("SELECT count(*) FROM account")).scalar_one() == accounts


def test_a_disabled_account_cannot_redeem(session: Session) -> None:
    _, code = new_invite(session)
    account = identity.ensure_account(session, issuer=ISSUER, subject=person())
    identity.disable_account(session, account.id)
    with pytest.raises(organizations.AccountDisabled):
        organizations.redeem_invite(session, issuer=ISSUER, subject=account.subject, code=code)
    assert session.execute(text("SELECT uses FROM invite")).scalar_one() == 0


def test_revoke_is_idempotent_and_teachers_revoke_only_their_own(session: Session) -> None:
    teacher = frozenset({Role.TEACHER})
    own, _ = new_invite(session, roles=teacher, created_by=TEACHER)
    with pytest.raises(organizations.InviteNotFound):
        organizations.revoke_invite(session, invite_id=own.id, actor="acc_other", roles=teacher)
    first, changed = organizations.revoke_invite(
        session, invite_id=own.id, actor=TEACHER, roles=teacher
    )
    assert changed and first.revoked_at is not None
    admin = frozenset({Role.PLATFORM_ADMIN})
    second, changed = organizations.revoke_invite(
        session, invite_id=own.id, actor=ADMIN, roles=admin
    )
    assert not changed and second.revoked_at == first.revoked_at
    revoked_by = session.execute(text("SELECT revoked_by FROM invite")).scalar_one()
    assert revoked_by == TEACHER
    with pytest.raises(organizations.InviteNotFound):
        organizations.revoke_invite(session, invite_id=uuid.uuid7(), actor=ADMIN, roles=admin)


def test_listing_is_newest_first_and_scoped(session: Session) -> None:
    teacher = frozenset({Role.TEACHER})
    mine = [new_invite(session, roles=teacher, created_by=TEACHER)[0] for _ in range(3)]
    other = new_invite(session)[0]
    listed = organizations.list_invites(session, actor=TEACHER, roles=teacher, after=None, limit=10)
    assert [v.id for v in listed] == [v.id for v in reversed(mine)]
    everything = organizations.list_invites(
        session, actor=ADMIN, roles=frozenset({Role.PLATFORM_ADMIN}), after=None, limit=10
    )
    assert everything[0].id == other.id and len(everything) == 4
    page = organizations.list_invites(
        session, actor=TEACHER, roles=teacher, after=mine[2].id, limit=10
    )
    assert [v.id for v in page] == [mine[1].id, mine[0].id]
    assert all(v.expires_at - v.created_at >= timedelta(days=6) for v in everything)


@pytest.mark.parametrize("role", [Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN])
def test_a_staff_invite_has_at_most_five_uses(session: Session, role: Role) -> None:
    assert organizations.MAX_STAFF_INVITE_USES == 5
    new_invite(session, role=role, max_uses=5)
    with pytest.raises(organizations.InviteTooManyUses):
        new_invite(session, role=role, max_uses=6)
    with pytest.raises(organizations.InviteTooManyUses):
        new_invite(session, role=role, max_uses=200)
    assert session.execute(text("SELECT count(*) FROM invite")).scalar_one() == 1


def test_the_use_limit_is_checked_after_the_role_permission(session: Session) -> None:
    teacher = frozenset({Role.TEACHER})
    with pytest.raises(organizations.InviteRoleForbidden):
        new_invite(session, roles=teacher, role=Role.REVIEWER, max_uses=200, created_by=TEACHER)


def test_student_and_teacher_invites_may_have_many_uses(session: Session) -> None:
    new_invite(session, role=Role.STUDENT, max_uses=200)
    new_invite(session, role=Role.TEACHER, max_uses=200)
    new_invite(session, roles=frozenset({Role.TEACHER}), max_uses=200, created_by=TEACHER)
