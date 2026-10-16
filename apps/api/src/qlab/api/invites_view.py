"""Invite operations at the API edge: identifiers, the audit entries and the response shapes.
Implemented in M1-G slice 9 (docs/slices/M1G-9-ACILIS.md section 3.3)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from qlab.api.policy import Principal
from qlab.api.schemas import InviteCreated, InviteOut, InvitePage, RedeemOut


def redeem(session: Session, *, issuer: str, subject: str, code: str) -> RedeemOut:
    raise NotImplementedError


def create(
    session: Session, *, caller: Principal, role: str, expires_in_days: int, max_uses: int
) -> InviteCreated:
    raise NotImplementedError


def list_page(session: Session, *, caller: Principal, cursor: str | None, limit: int) -> InvitePage:
    raise NotImplementedError


def revoke(session: Session, *, caller: Principal, invite_id: str) -> InviteOut:
    raise NotImplementedError
