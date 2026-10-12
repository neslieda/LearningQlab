"""Rights service. Fail-closed: anything that is not positively permitted is denied.

CLAUDE.md rule 2 and docs/SECURITY.md section 4.2. The kill switch for source content is not
part of this slice; `source_original` content stays closed in the content module (D-47).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from sqlalchemy.orm import Session


class Purpose(StrEnum):
    DISPLAY = "display"
    AI_PROCESSING = "ai_processing"
    COMMERCIAL_USE = "commercial_use"


class DisplayScope(StrEnum):
    NONE = "none"
    ORGANIZATION = "organization"
    ALL = "all"


class RightsDenied(Exception):
    """Raised by `require` when a use is not permitted."""


@dataclass(frozen=True)
class RightsRecordView:
    id: uuid.UUID
    holder: str
    license_ref: str | None
    display_scope: DisplayScope
    display_organization_id: uuid.UUID | None
    allows_ai_processing: bool
    allows_commercial_use: bool
    valid_from: datetime
    valid_until: datetime | None
    revoked_at: datetime | None


def evaluate(
    record: RightsRecordView | None,
    purpose: Purpose,
    *,
    at: datetime,
    organization_id: uuid.UUID | None = None,
) -> bool:
    """Decide whether `purpose` is permitted at the instant `at`. Pure; no database access.

    Denied when: there is no record; `at` is before `valid_from`; `valid_until` is set and
    `at` is at or after it; the record has been revoked (any `revoked_at`, even a future one);
    or the flag for the purpose is off.

    DISPLAY: scope "all" permits everyone; scope "organization" permits only when
    `organization_id` equals the record's `display_organization_id`; scope "none" permits no one.
    `organization_id` is ignored for the other purposes.

    `at` must be timezone-aware; a naive datetime raises ValueError.
    """
    raise NotImplementedError


def create_record(
    session: Session,
    *,
    holder: str,
    valid_from: datetime,
    display_scope: DisplayScope = DisplayScope.NONE,
    display_organization_id: uuid.UUID | None = None,
    allows_ai_processing: bool = False,
    allows_commercial_use: bool = False,
    valid_until: datetime | None = None,
    license_ref: str | None = None,
    note: str | None = None,
) -> RightsRecordView:
    """Insert a record inside the caller's transaction. Every permission defaults to off.

    Raises ValueError (and writes nothing) when: `holder` is blank; a datetime is naive;
    `valid_until` is not after `valid_from`; or `display_organization_id` is given without
    scope "organization", or missing with it.
    """
    raise NotImplementedError


def get_record(session: Session, rights_record_id: uuid.UUID) -> RightsRecordView | None:
    raise NotImplementedError


def revoke(session: Session, rights_record_id: uuid.UUID, *, at: datetime) -> None:
    """Mark the record revoked; a second call keeps the first timestamp.

    Unknown id raises LookupError; a naive `at` raises ValueError.
    """
    raise NotImplementedError


def is_permitted(
    session: Session,
    rights_record_id: uuid.UUID | None,
    purpose: Purpose,
    *,
    at: datetime | None = None,
    organization_id: uuid.UUID | None = None,
) -> bool:
    """`evaluate` for the stored record; `at` defaults to now. None or unknown id is denied."""
    raise NotImplementedError


def require(
    session: Session,
    rights_record_id: uuid.UUID | None,
    purpose: Purpose,
    *,
    at: datetime | None = None,
    organization_id: uuid.UUID | None = None,
) -> None:
    """Raise RightsDenied unless `is_permitted` holds."""
    raise NotImplementedError
