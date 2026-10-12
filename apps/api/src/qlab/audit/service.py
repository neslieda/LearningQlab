"""Audit service: the only way other modules write to or read from the audit log."""

from __future__ import annotations

import re
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from qlab.audit.models import AuditLog

_ACTION = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")


@dataclass(frozen=True)
class AuditEntry:
    id: uuid.UUID
    occurred_at: datetime
    actor: str
    action: str
    entity_type: str
    entity_id: str
    data: Mapping[str, Any]


def _entry(row: AuditLog) -> AuditEntry:
    return AuditEntry(
        id=row.id,
        occurred_at=row.occurred_at,
        actor=row.actor,
        action=row.action,
        entity_type=row.entity_type,
        entity_id=row.entity_id,
        data=row.data,
    )


def record(
    session: Session,
    *,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: str,
    data: Mapping[str, Any] | None = None,
) -> AuditEntry:
    """Append one entry inside the caller's transaction and return it.

    The entry commits or rolls back together with the change it describes. `action` is a dotted
    lower-case name such as "question_version.published". `actor`, `entity_type` and `entity_id`
    must be non-blank. Invalid arguments raise ValueError and write nothing.
    """
    for name, value in (("actor", actor), ("entity_type", entity_type), ("entity_id", entity_id)):
        if not value.strip():
            raise ValueError(f"audit: {name} is blank")
    if not _ACTION.fullmatch(action):
        raise ValueError(f"audit: action {action!r} is not a dotted lower-case name")
    row = AuditLog(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        data=dict(data or {}),
    )
    session.add(row)
    session.flush()
    session.refresh(row)
    return _entry(row)


def entries_for(session: Session, entity_type: str, entity_id: str) -> list[AuditEntry]:
    """Entries for one entity, oldest first.

    Entries written in one transaction share `occurred_at`; they come back in the order they
    were recorded (the identifier is time-ordered).
    """
    rows = session.scalars(
        select(AuditLog)
        .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        # now() is constant within a transaction; the time-ordered id breaks the tie.
        .order_by(AuditLog.occurred_at, AuditLog.id)
    )
    return [_entry(row) for row in rows]
