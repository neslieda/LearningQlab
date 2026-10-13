"""Audit service: the only way other modules write to or read from the audit log."""

from __future__ import annotations

import json
import re
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from qlab.audit.models import (
    ACTION_PATTERN,
    ACTOR_PATTERN,
    ENTITY_TYPE_PATTERN,
    MAX_DATA_BYTES,
    MAX_ENTITY_ID_LENGTH,
    AuditLog,
)

_ACTOR = re.compile(ACTOR_PATTERN)
_ACTION = re.compile(ACTION_PATTERN)
_ENTITY_TYPE = re.compile(ENTITY_TYPE_PATTERN)


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


def is_valid_actor(actor: str) -> bool:
    """Whether `actor` has the form the audit log accepts: an opaque account identifier or
    "system:<process>" (letters, digits and `_ . : | -`; no spaces, no e-mail address)."""
    return _ACTOR.fullmatch(actor) is not None


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

    The entry commits or rolls back together with the change it describes. Its time is set by
    the database. Invalid arguments raise ValueError and write nothing:

    - `actor`: an opaque account identifier or "system:<process>": letters, digits and
      `_ . : | -` only, so never a name with spaces or an e-mail address.
    - `action`: a dotted lower-case name such as "question_version.published".
    - `entity_type`: a lower-case identifier; `entity_id`: non-blank, no surrounding whitespace.
    - `data`: a JSON object (identifiers and codes, not personal data) of limited size.
    """
    if not _ACTOR.fullmatch(actor):
        raise ValueError("audit: actor must be an opaque identifier or system:<process>")
    if not _ACTION.fullmatch(action):
        raise ValueError(f"audit: action {action!r} is not a dotted lower-case name")
    if not _ENTITY_TYPE.fullmatch(entity_type):
        raise ValueError(f"audit: entity_type {entity_type!r} is not a lower-case identifier")
    if not entity_id or entity_id != entity_id.strip() or len(entity_id) > MAX_ENTITY_ID_LENGTH:
        raise ValueError("audit: entity_id is blank, padded or too long")
    try:
        encoded = json.dumps(dict(data or {}), allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError(f"audit: data is not JSON: {error}") from None
    # Generous margin under the table's limit, which counts PostgreSQL's own rendering.
    if len(encoded.encode()) > MAX_DATA_BYTES // 2:
        raise ValueError("audit: data is too large")
    row = AuditLog(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        data=json.loads(encoded),
    )
    session.add(row)
    session.flush()
    session.refresh(row)
    return _entry(row)


def entries_for(session: Session, entity_type: str, entity_id: str) -> list[AuditEntry]:
    """Entries for one entity in the order they were recorded, oldest first."""
    rows = session.scalars(
        select(AuditLog)
        .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(AuditLog.occurred_at, AuditLog.id)
    )
    return [_entry(row) for row in rows]
