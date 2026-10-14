"""Role assignments (D-12: roles live in the application, not in the token).

M1-G has no organisations yet: every assignment is platform-wide. The organisation scope of
`student`, `teacher` and `org_admin` (docs/DOMAIN_MODEL.md section 3) arrives with the
organisation table in M2.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from qlab.database import Base, created_at_column, new_id

ROLES = ("student", "teacher", "org_admin", "reviewer", "content_admin", "platform_admin")
# Same form as the audit log's actor (qlab.audit.models.ACTOR_PATTERN).
_ACTOR_CHECK = r"~ '^[A-Za-z0-9_.:|-]{1,200}$'"


class RoleAssignment(Base):
    """One role held by one account. Never deleted: a role that is taken away is revoked, and
    granting it again is a new row."""

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
