"""A learner's stored answers (M1-G slice 8, D-66).

The only personal data here is the opaque account id and what the learner typed or chose. No
name, e-mail, address or device data. A row belongs to the account: it goes when the account is
erased, and the learner can delete their own rows at any time (docs/SECURITY.md section 5.4), so
this table has no delete guard.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from qlab.database import Base, created_at_column, new_id

MAX_ANSWERS_PER_QUESTION = 200
MAX_PAYLOAD_BYTES = 66_000


class Response(Base):
    __tablename__ = "response"
    __table_args__ = (
        CheckConstraint("kind IN ('mcq', 'written')", name="kind"),
        # Multiple choice: no part, a marked result. Written: a part, no mark yet (M4).
        CheckConstraint(
            "(kind = 'mcq' AND part_id IS NULL AND correct IS NOT NULL) "
            "OR (kind = 'written' AND part_id IS NOT NULL AND correct IS NULL)",
            name="shape",
        ),
        CheckConstraint(
            "part_id IS NULL OR (part_id <> '' AND length(part_id) <= 64)", name="part_id"
        ),
        CheckConstraint(f"pg_column_size(payload) <= {MAX_PAYLOAD_BYTES}", name="payload_size"),
        Index("ix_response_account_created", "account_id", "created_at", "id"),
        Index("ix_response_account_version", "account_id", "question_version_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("account.id", ondelete="CASCADE"))
    question_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question_version.id"))
    part_id: Mapped[str | None] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(Text)
    # `{"selected_key": "B"}` or `{"text": "..."}`.
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    correct: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[datetime] = created_at_column()
