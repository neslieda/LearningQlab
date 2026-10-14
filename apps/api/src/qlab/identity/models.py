"""Accounts. An account is an identity provider subject; it holds no name, e-mail or password.

Roles live in `qlab.organizations`. Personal fields (age band, country) arrive with the real
identity provider (M1-G slice 9, M2).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from qlab.database import Base, created_at_column, new_id

MAX_ISSUER_LENGTH = 200
MAX_SUBJECT_LENGTH = 200


class Account(Base):
    __tablename__ = "account"
    __table_args__ = (
        UniqueConstraint("issuer", "subject"),
        CheckConstraint(
            f"issuer <> '' AND issuer = btrim(issuer) AND length(issuer) <= {MAX_ISSUER_LENGTH}",
            name="issuer",
        ),
        CheckConstraint(
            f"subject <> '' AND subject = btrim(subject) "
            f"AND length(subject) <= {MAX_SUBJECT_LENGTH}",
            name="subject",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    # The token's `iss` and `sub` claims. Together they name one person at one provider.
    issuer: Mapped[str] = mapped_column(Text)
    subject: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()
    # A disabled account authenticates as nobody.
    disabled_at: Mapped[datetime | None]
