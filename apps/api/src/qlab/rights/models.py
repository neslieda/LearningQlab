"""Rights records: who holds the rights to a piece of content and what may be done with it.

Flags follow docs/SECURITY.md section 4.2. A record is evidence that the platform recorded a
permission; it is not a legal determination.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Text, false
from sqlalchemy.orm import Mapped, mapped_column

from qlab.database import Base, created_at_column, new_id

DISPLAY_SCOPES = ("none", "organization", "all")


class RightsRecord(Base):
    __tablename__ = "rights_record"
    __table_args__ = (
        CheckConstraint("display_scope IN ('none', 'organization', 'all')", name="display_scope"),
        CheckConstraint(
            "(display_scope = 'organization') = (display_organization_id IS NOT NULL)",
            name="display_organization",
        ),
        CheckConstraint("valid_until IS NULL OR valid_until > valid_from", name="validity_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    holder: Mapped[str] = mapped_column(Text)
    license_ref: Mapped[str | None] = mapped_column(Text)
    display_scope: Mapped[str] = mapped_column(Text, server_default="none")
    # Organization allowed to see the content when display_scope is "organization". No foreign
    # key: rights does not depend on the organizations module.
    display_organization_id: Mapped[uuid.UUID | None]
    allows_ai_processing: Mapped[bool] = mapped_column(server_default=false())
    allows_commercial_use: Mapped[bool] = mapped_column(server_default=false())
    valid_from: Mapped[datetime]
    valid_until: Mapped[datetime | None]
    revoked_at: Mapped[datetime | None]
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()
