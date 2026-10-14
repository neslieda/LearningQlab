"""Identity service: accounts. Token verification is in `qlab.identity.tokens`."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from qlab.identity.models import MAX_ISSUER_LENGTH, MAX_SUBJECT_LENGTH, Account


@dataclass(frozen=True)
class AccountView:
    id: uuid.UUID
    issuer: str
    subject: str
    created_at: datetime
    disabled_at: datetime | None

    @property
    def is_active(self) -> bool:
        return self.disabled_at is None


def _view(row: Account) -> AccountView:
    return AccountView(
        id=row.id,
        issuer=row.issuer,
        subject=row.subject,
        created_at=row.created_at,
        disabled_at=row.disabled_at,
    )


def _find(session: Session, issuer: str, subject: str) -> Account | None:
    return session.scalars(
        select(Account).where(Account.issuer == issuer, Account.subject == subject)
    ).one_or_none()


def find_account(session: Session, *, issuer: str, subject: str) -> AccountView | None:
    """The account for a token's `iss` and `sub`, or None. A disabled account is returned with
    `is_active` false; deciding what that means is the caller's job."""
    row = _find(session, issuer, subject)
    return None if row is None else _view(row)


def get_account(session: Session, account_id: uuid.UUID) -> AccountView | None:
    row = session.get(Account, account_id)
    return None if row is None else _view(row)


def ensure_account(session: Session, *, issuer: str, subject: str) -> AccountView:
    """The account for this issuer and subject, created if it does not exist. Runs inside the
    caller's transaction. Blank, padded, over-long or non-printable values raise ValueError."""
    for name, value, limit in (
        ("issuer", issuer, MAX_ISSUER_LENGTH),
        ("subject", subject, MAX_SUBJECT_LENGTH),
    ):
        if not value or value != value.strip() or len(value) > limit or not value.isprintable():
            raise ValueError(f"identity: {name} is blank, padded, too long or not printable")
    row = _find(session, issuer, subject)
    if row is None:
        row = Account(issuer=issuer, subject=subject)
        session.add(row)
        session.flush()
        session.refresh(row)
    return _view(row)


def disable_account(session: Session, account_id: uuid.UUID) -> bool:
    """Disable an account. Returns False when it was already disabled. Unknown id: LookupError.
    The caller writes the audit entry."""
    row = session.get(Account, account_id, with_for_update=True)
    if row is None:
        raise LookupError(f"account {account_id}")
    if row.disabled_at is not None:
        return False
    row.disabled_at = session.scalar(select(func.now()))
    session.flush()
    return True
