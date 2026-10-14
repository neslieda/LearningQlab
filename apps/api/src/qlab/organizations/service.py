"""Roles of an account. Default deny: an account has exactly the roles with an active
assignment, and none otherwise.

This module may depend on `identity` only (docs/API_DESIGN.md section 2), so the audit entry
for a grant or a revocation is written by the caller, in the same transaction.
"""

from __future__ import annotations

import re
import uuid
from enum import StrEnum

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from qlab.identity import service as identity
from qlab.organizations.models import RoleAssignment

_ACTOR = re.compile(r"[A-Za-z0-9_.:|-]{1,200}")


class Role(StrEnum):
    """docs/DOMAIN_MODEL.md section 3."""

    STUDENT = "student"
    TEACHER = "teacher"
    ORG_ADMIN = "org_admin"
    REVIEWER = "reviewer"
    CONTENT_ADMIN = "content_admin"
    PLATFORM_ADMIN = "platform_admin"


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
