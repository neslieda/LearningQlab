"""Append-only audit log. The database rejects UPDATE, DELETE and TRUNCATE (migration 0001)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from qlab.database import Base, created_at_column, new_id


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (Index(None, "entity_type", "entity_id", "occurred_at"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    occurred_at: Mapped[datetime] = created_at_column()
    # Opaque account identifier or "system:<process>"; never a name or an e-mail address.
    actor: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    entity_type: Mapped[str] = mapped_column(Text)
    entity_id: Mapped[str] = mapped_column(Text)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default="{}")
