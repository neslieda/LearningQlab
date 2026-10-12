"""Rights service. Fail-closed: anything that is not positively permitted is denied.

CLAUDE.md rule 2 and docs/SECURITY.md section 4.2. The kill switch for source content is not
part of this slice; `source_original` content stays closed in the content module (D-47).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy.orm import Session

from qlab.rights.models import RightsRecord


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


def _require_aware(name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"rights: {name} must be timezone-aware")


def _view(row: RightsRecord) -> RightsRecordView:
    return RightsRecordView(
        id=row.id,
        holder=row.holder,
        license_ref=row.license_ref,
        display_scope=DisplayScope(row.display_scope),
        display_organization_id=row.display_organization_id,
        allows_ai_processing=row.allows_ai_processing,
        allows_commercial_use=row.allows_commercial_use,
        valid_from=row.valid_from,
        valid_until=row.valid_until,
        revoked_at=row.revoked_at,
    )


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
    Display does not depend on the two `allows_*` flags. `organization_id` is ignored for the
    other purposes.

    `at` must be timezone-aware; a naive datetime raises ValueError.
    """
    _require_aware("at", at)
    if record is None or record.revoked_at is not None:
        return False
    if at < record.valid_from:
        return False
    if record.valid_until is not None and at >= record.valid_until:
        return False
    if purpose is Purpose.AI_PROCESSING:
        return record.allows_ai_processing
    if purpose is Purpose.COMMERCIAL_USE:
        return record.allows_commercial_use
    if purpose is Purpose.DISPLAY:
        if record.display_scope is DisplayScope.ALL:
            return True
        if record.display_scope is DisplayScope.ORGANIZATION:
            return organization_id is not None and organization_id == record.display_organization_id
    return False


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
    if not holder.strip():
        raise ValueError("rights: holder is blank")
    _require_aware("valid_from", valid_from)
    if valid_until is not None:
        _require_aware("valid_until", valid_until)
        if valid_until <= valid_from:
            raise ValueError("rights: valid_until must be after valid_from")
    scope = DisplayScope(display_scope)
    if (scope is DisplayScope.ORGANIZATION) != (display_organization_id is not None):
        raise ValueError(
            "rights: display_organization_id is required for, and only for, scope 'organization'"
        )
    row = RightsRecord(
        holder=holder,
        license_ref=license_ref,
        display_scope=scope.value,
        display_organization_id=display_organization_id,
        allows_ai_processing=allows_ai_processing,
        allows_commercial_use=allows_commercial_use,
        valid_from=valid_from,
        valid_until=valid_until,
        note=note,
    )
    session.add(row)
    session.flush()
    return _view(row)


def get_record(session: Session, rights_record_id: uuid.UUID) -> RightsRecordView | None:
    row = session.get(RightsRecord, rights_record_id)
    return None if row is None else _view(row)


def revoke(session: Session, rights_record_id: uuid.UUID, *, at: datetime) -> None:
    """Mark the record revoked; a second call keeps the first timestamp.

    Unknown id raises LookupError; a naive `at` raises ValueError.
    """
    _require_aware("at", at)
    row = session.get(RightsRecord, rights_record_id, with_for_update=True)
    if row is None:
        raise LookupError(f"rights record {rights_record_id} does not exist")
    if row.revoked_at is None:
        row.revoked_at = at
        session.flush()


def is_permitted(
    session: Session,
    rights_record_id: uuid.UUID | None,
    purpose: Purpose,
    *,
    at: datetime | None = None,
    organization_id: uuid.UUID | None = None,
) -> bool:
    """`evaluate` for the stored record; `at` defaults to now. None or unknown id is denied.

    A naive `at` raises ValueError whenever a record id is given.
    """
    if rights_record_id is None:
        return False
    return evaluate(
        get_record(session, rights_record_id),
        purpose,
        at=at if at is not None else datetime.now(UTC),
        organization_id=organization_id,
    )


def require(
    session: Session,
    rights_record_id: uuid.UUID | None,
    purpose: Purpose,
    *,
    at: datetime | None = None,
    organization_id: uuid.UUID | None = None,
) -> None:
    """Raise RightsDenied unless `is_permitted` holds."""
    if not is_permitted(session, rights_record_id, purpose, at=at, organization_id=organization_id):
        raise RightsDenied(f"{purpose.value} is not permitted for rights record {rights_record_id}")
