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
    raise NotImplementedError


def entries_for(session: Session, entity_type: str, entity_id: str) -> list[AuditEntry]:
    """Entries for one entity, oldest first."""
    raise NotImplementedError


__all__ = ["AuditEntry", "entries_for", "record"]
_ = (select, AuditLog)
