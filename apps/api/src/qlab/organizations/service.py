"""Roles of an account. Default deny: an account has exactly the roles with an active
assignment, and none otherwise.

This module may depend on `identity` only (docs/API_DESIGN.md section 2), so the audit entry
for a grant or a revocation is written by the caller, in the same transaction.
"""

from __future__ import annotations

import base64
import hashlib
import re
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from qlab.identity import service as identity
from qlab.organizations.models import Invite, InviteRedemption, RoleAssignment

_ACTOR = re.compile(r"[A-Za-z0-9_.:|-]{1,200}")


class InviteNotFound(Exception):
    """The invite code is unknown, expired, revoked or used up; or the invite is not the
    caller's to see. Deliberately one error for all of these (D-63)."""


class InviteRoleForbidden(Exception):
    """The caller's roles do not allow inviting someone to this role."""


MAX_STAFF_INVITE_USES = 5


class InviteTooManyUses(Exception):
    """A staff invite may be used by at most `MAX_STAFF_INVITE_USES` people: a leaked link must
    not hand a staff role to many."""


class AccountDisabled(Exception):
    """The account that wanted to use an invite is disabled."""


class Role(StrEnum):
    """docs/DOMAIN_MODEL.md section 3."""

    STUDENT = "student"
    TEACHER = "teacher"
    ORG_ADMIN = "org_admin"
    REVIEWER = "reviewer"
    CONTENT_ADMIN = "content_admin"
    PLATFORM_ADMIN = "platform_admin"


_STAFF_ROLES = frozenset({Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN})


def roles_of(session: Session, account_id: uuid.UUID) -> frozenset[Role]:
    """The roles the account holds right now. Read from the database on every call. An unknown
    account has none."""
    rows = session.scalars(
        select(RoleAssignment.role).where(
            RoleAssignment.account_id == account_id, RoleAssignment.revoked_at.is_(None)
        )
    )
    return frozenset(Role(role) for role in rows)


def _active(session: Session, account_id: uuid.UUID, role: Role) -> RoleAssignment | None:
    return session.scalars(
        select(RoleAssignment)
        .where(
            RoleAssignment.account_id == account_id,
            RoleAssignment.role == role.value,
            RoleAssignment.revoked_at.is_(None),
        )
        .with_for_update()
    ).one_or_none()


def _require_actor(actor: str) -> None:
    if not _ACTOR.fullmatch(actor):
        raise ValueError("organizations: actor must be an opaque identifier or system:<process>")


def grant(session: Session, *, account_id: uuid.UUID, role: Role, granted_by: str) -> bool:
    """Give the account a role. Returns False when it already holds it (nothing is written).

    Unknown account: LookupError. `granted_by` has the form of an audit actor, else
    ValueError. Runs inside the caller's transaction; the caller writes the audit entry.
    """
    role = Role(role)
    _require_actor(granted_by)
    if identity.get_account(session, account_id) is None:
        raise LookupError(f"account {account_id}")
    if _active(session, account_id, role) is not None:
        return False
    session.add(RoleAssignment(account_id=account_id, role=role.value, granted_by=granted_by))
    session.flush()
    return True


def revoke(session: Session, *, account_id: uuid.UUID, role: Role, revoked_by: str) -> bool:
    """Take a role away. Returns False when the account does not hold it. The row stays, marked
    revoked. The caller writes the audit entry."""
    role = Role(role)
    _require_actor(revoked_by)
    row = _active(session, account_id, role)
    if row is None:
        return False
    row.revoked_at = session.scalar(select(func.now()))
    row.revoked_by = revoked_by
    session.flush()
    return True


# --- Invites (M1-G slice 9, D-63) ----------------------------------------------------------------

CODE_BYTES = 32
# Roles an invite can give. `org_admin` waits for organisations (M2).
INVITABLE_ROLES = frozenset(
    {Role.STUDENT, Role.TEACHER, Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN}
)
_TEACHER_MAY_INVITE = frozenset({Role.STUDENT})


@dataclass(frozen=True)
class InviteView:
    id: uuid.UUID
    role: Role
    created_by: str
    created_at: datetime
    expires_at: datetime
    max_uses: int
    uses: int
    revoked_at: datetime | None


@dataclass(frozen=True)
class RedeemResult:
    account_id: uuid.UUID
    roles: frozenset[Role]
    invite_id: uuid.UUID
    role: Role
    counted: bool  # this call used the invite (a repeat by the same account does not)
    granted: bool  # this call gave the role (it was not held)


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _invite_view(row: Invite) -> InviteView:
    return InviteView(
        id=row.id,
        role=Role(row.role),
        created_by=row.created_by,
        created_at=row.created_at,
        expires_at=row.expires_at,
        max_uses=row.max_uses,
        uses=row.uses,
        revoked_at=row.revoked_at,
    )


def _now(session: Session) -> datetime:
    value = session.scalar(select(func.now()))
    assert isinstance(value, datetime)  # noqa: S101 - the database always answers
    return value


def create_invite(
    session: Session,
    *,
    created_by: str,
    creator_roles: frozenset[Role],
    role: Role,
    expires_in_days: int,
    max_uses: int,
) -> tuple[InviteView, str]:
    """A new invite and its code, which exists nowhere else (only its SHA-256 is stored).

    `platform_admin` may invite to any invitable role; `teacher` to `student` only; anyone
    else, and any other role: InviteRoleForbidden. The caller writes the audit entry.
    """
    role = Role(role)
    _require_actor(created_by)
    if role not in INVITABLE_ROLES:
        raise InviteRoleForbidden(role.value)
    if Role.PLATFORM_ADMIN not in creator_roles and not (
        Role.TEACHER in creator_roles and role in _TEACHER_MAY_INVITE
    ):
        raise InviteRoleForbidden(role.value)
    if not 1 <= expires_in_days <= 30 or not 1 <= max_uses <= 200:
        raise ValueError("organizations: expiry or number of uses out of range")
    if role in _STAFF_ROLES and max_uses > MAX_STAFF_INVITE_USES:
        raise InviteTooManyUses(role.value)
    code = base64.urlsafe_b64encode(secrets.token_bytes(CODE_BYTES)).rstrip(b"=").decode()
    row = Invite(
        code_sha256=hash_code(code),
        role=role.value,
        created_by=created_by,
        expires_at=_now(session) + timedelta(days=expires_in_days),
        max_uses=max_uses,
    )
    session.add(row)
    session.flush()
    session.refresh(row)
    return _invite_view(row), code


def list_invites(
    session: Session,
    *,
    actor: str,
    roles: frozenset[Role],
    after: uuid.UUID | None,
    limit: int,
) -> list[InviteView]:
    """Invites, newest first (identifiers are time-ordered), after the given one. A caller
    without `platform_admin` sees only their own. At most `limit` rows."""
    query = select(Invite).order_by(Invite.id.desc()).limit(limit)
    if Role.PLATFORM_ADMIN not in roles:
        query = query.where(Invite.created_by == actor)
    if after is not None:
        query = query.where(Invite.id < after)
    return [_invite_view(row) for row in session.scalars(query)]


def revoke_invite(
    session: Session, *, invite_id: uuid.UUID, actor: str, roles: frozenset[Role]
) -> tuple[InviteView, bool]:
    """Stop an invite from being used. Without `platform_admin` only the caller's own invite
    can be revoked; another's is InviteNotFound. Revoking twice keeps the first revocation; the
    flag says whether this call revoked it."""
    _require_actor(actor)
    row = session.get(Invite, invite_id, with_for_update=True)
    if row is None or (Role.PLATFORM_ADMIN not in roles and row.created_by != actor):
        raise InviteNotFound(str(invite_id))
    changed = row.revoked_at is None
    if changed:
        row.revoked_at = _now(session)
        row.revoked_by = actor
        session.flush()
    return _invite_view(row), changed


def redeem_invite(session: Session, *, issuer: str, subject: str, code: str) -> RedeemResult:
    """Use an invite for the person (issuer, subject): open their account if needed, give the
    role unless held, count the use. Unknown, expired, revoked or used-up code: InviteNotFound
    (nothing is written). A disabled account: AccountDisabled, whatever the code. The same
    account using the invite again changes nothing, even if the invite has since expired, been
    revoked or used up. The invite row is locked, so concurrent uses
    cannot exceed `max_uses`. The caller writes the audit entry.
    """
    account = identity.find_account(session, issuer=issuer, subject=subject)
    if account is not None and not account.is_active:
        raise AccountDisabled(str(account.id))
    row = session.scalars(
        select(Invite).where(Invite.code_sha256 == hash_code(code)).with_for_update()
    ).one_or_none()
    if row is None:
        raise InviteNotFound("invite")
    if account is not None and session.get(InviteRedemption, (row.id, account.id)) is not None:
        # Already used by this person: current roles, whatever became of the invite since.
        return RedeemResult(
            account.id, roles_of(session, account.id), row.id, Role(row.role), False, False
        )
    if row.revoked_at is not None or row.expires_at <= _now(session):
        raise InviteNotFound("invite")
    if row.uses >= row.max_uses:
        raise InviteNotFound("invite")
    account = identity.ensure_account(session, issuer=issuer, subject=subject)
    # Two first-time requests of the same new person can both pass the check above before
    # either has an account; the one that waited for the row lock re-checks here.
    if session.get(InviteRedemption, (row.id, account.id)) is not None:
        return RedeemResult(
            account.id, roles_of(session, account.id), row.id, Role(row.role), False, False
        )
    if not account.is_active:
        raise AccountDisabled(str(account.id))
    session.add(InviteRedemption(invite_id=row.id, account_id=account.id))
    row.uses += 1
    role = Role(row.role)
    granted = grant(session, account_id=account.id, role=role, granted_by=f"invite:{row.id}")
    return RedeemResult(account.id, roles_of(session, account.id), row.id, role, True, granted)
