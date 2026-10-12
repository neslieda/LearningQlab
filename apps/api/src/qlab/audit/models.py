"""Append-only audit log. The database rejects UPDATE, DELETE and TRUNCATE (migration 0001)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from qlab.database import Base, created_at_column, new_id

# The same rules are enforced by the service (clear errors) and by the table (no bypass).
ACTOR_PATTERN = r"^[A-Za-z0-9_.:|-]{1,200}$"
ACTION_PATTERN = r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$"
ENTITY_TYPE_PATTERN = r"^[a-z][a-z0-9_]*$"
MAX_ENTITY_ID_LENGTH = 200
MAX_DATA_BYTES = 16384


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        Index(None, "entity_type", "entity_id", "occurred_at"),
        CheckConstraint(rf"actor ~ '{ACTOR_PATTERN}'", name="actor"),
        CheckConstraint(rf"action ~ '{ACTION_PATTERN}'", name="action"),
        CheckConstraint(f"entity_type ~ '{ENTITY_TYPE_PATTERN}'", name="entity_type"),
        CheckConstraint(
            f"entity_id <> '' AND entity_id = btrim(entity_id) "
            f"AND length(entity_id) <= {MAX_ENTITY_ID_LENGTH}",
            name="entity_id",
        ),
        CheckConstraint(
            f"jsonb_typeof(data) = 'object' AND octet_length(data::text) <= {MAX_DATA_BYTES}",
            name="data",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    # Set by a database trigger to the wall-clock time of the insert; a supplied value is ignored.
    occurred_at: Mapped[datetime] = created_at_column()
    # Opaque account identifier or "system:<process>"; never a name or an e-mail address.
    actor: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    entity_type: Mapped[str] = mapped_column(Text)
    entity_id: Mapped[str] = mapped_column(Text)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default="{}")
