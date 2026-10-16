"""Role assignments (D-12: roles live in the application, not in the token).

M1-G has no organisations yet: every assignment is platform-wide. The organisation scope of
`student`, `teacher` and `org_admin` (docs/DOMAIN_MODEL.md section 3) arrives with the
organisation table in M2.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from qlab.database import Base, created_at_column, new_id

ROLES = ("student", "teacher", "org_admin", "reviewer", "content_admin", "platform_admin")
# Same form as the audit log's actor (qlab.audit.models.ACTOR_PATTERN).
_ACTOR_CHECK = r"~ '^[A-Za-z0-9_.:|-]{1,200}$'"


class RoleAssignment(Base):
    """One role held by one account. A role that is taken away is revoked, and granting it
    again is a new row. The lasting record is the audit log: rows here go when the account is
    erased (docs/SECURITY.md section 5.4)."""

    __tablename__ = "role_assignment"
    __table_args__ = (
        CheckConstraint(f"role IN ({', '.join(repr(r) for r in ROLES)})", name="role"),
        CheckConstraint(f"granted_by {_ACTOR_CHECK}", name="granted_by"),
        CheckConstraint(
            f"(revoked_at IS NULL) = (revoked_by IS NULL) "
            f"AND (revoked_by IS NULL OR revoked_by {_ACTOR_CHECK})",
            name="revoked",
        ),
        Index(
            "uq_role_assignment_one_active",
            "account_id",
            "role",
            unique=True,
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("account.id"))
    role: Mapped[str] = mapped_column(Text)
    # Opaque account identifier or "system:<process>" of whoever granted or revoked it.
    granted_by: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()
    revoked_at: Mapped[datetime | None]
    revoked_by: Mapped[str | None] = mapped_column(Text)


class Invite(Base):
    """A link that gives its user an account and one role (D-63). Only the code's SHA-256 is
    stored; the code is shown once to whoever created the invite."""

    __tablename__ = "invite"
    __table_args__ = (
        UniqueConstraint("code_sha256"),
        CheckConstraint("code_sha256 ~ '^[0-9a-f]{64}$'", name="code_sha256"),
        CheckConstraint(f"role IN ({', '.join(repr(r) for r in ROLES)})", name="role"),
        CheckConstraint(f"created_by {_ACTOR_CHECK}", name="created_by"),
        CheckConstraint("expires_at > created_at", name="expires_at"),
        CheckConstraint("max_uses BETWEEN 1 AND 200", name="max_uses"),
        CheckConstraint("uses BETWEEN 0 AND max_uses", name="uses"),
        CheckConstraint(
            f"(revoked_at IS NULL) = (revoked_by IS NULL) "
            f"AND (revoked_by IS NULL OR revoked_by {_ACTOR_CHECK})",
            name="revoked",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    code_sha256: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()
    expires_at: Mapped[datetime]
    max_uses: Mapped[int] = mapped_column(Integer)
    uses: Mapped[int] = mapped_column(Integer, server_default="0")
    revoked_at: Mapped[datetime | None]
    revoked_by: Mapped[str | None] = mapped_column(Text)


class InviteRedemption(Base):
    """Who used an invite. The same person using it twice counts once."""

    __tablename__ = "invite_redemption"

    invite_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invite.id"), primary_key=True)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("account.id"), primary_key=True)
    redeemed_at: Mapped[datetime] = created_at_column()
