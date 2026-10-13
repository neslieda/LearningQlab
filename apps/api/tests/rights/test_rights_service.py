"""Rights service: fail-closed evaluation, record creation, revocation, and the database checks.

Written from the docstrings of qlab.rights.service and migration 0001 only. `evaluate` is pure
and tested without a database; everything else is marked `db`.
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from qlab.rights.service import (
    DisplayScope,
    Purpose,
    RightsDenied,
    RightsRecordView,
    create_record,
    evaluate,
    find_by_license_ref,
    get_record,
    is_permitted,
    require,
    revoke,
)

PURPOSES = list(Purpose)
T0 = datetime(2030, 3, 1, 12, 0, 0, tzinfo=UTC)
UNTIL = datetime(2031, 3, 1, 12, 0, 0, tzinfo=UTC)
ORG_A = uuid.UUID("aaaaaaaa-0000-4000-8000-00000000000a")
ORG_B = uuid.UUID("bbbbbbbb-0000-4000-8000-00000000000b")
MICRO = timedelta(microseconds=1)

# Permits every purpose for everybody inside [T0, infinity) unless a test changes something.
OPEN_RECORD = RightsRecordView(
    id=uuid.UUID("11111111-0000-4000-8000-000000000001"),
    holder="Synthetic Holder",
    license_ref=None,
    display_scope=DisplayScope.ALL,
    display_organization_id=None,
    allows_ai_processing=True,
    allows_commercial_use=True,
    valid_from=T0,
    valid_until=None,
    revoked_at=None,
)


def view(**changes: Any) -> RightsRecordView:
    return dataclasses.replace(OPEN_RECORD, **changes)


# =============================================================================================
# evaluate: pure
# =============================================================================================


def test_baseline_open_record_permits_every_purpose() -> None:
    for purpose in PURPOSES:
        assert evaluate(OPEN_RECORD, purpose, at=T0 + timedelta(days=1)) is True


@pytest.mark.parametrize("purpose", PURPOSES)
@pytest.mark.parametrize("organization_id", [None, ORG_A])
def test_no_record_is_denied(purpose: Purpose, organization_id: uuid.UUID | None) -> None:
    assert evaluate(None, purpose, at=T0, organization_id=organization_id) is False


@pytest.mark.parametrize("purpose", PURPOSES)
@pytest.mark.parametrize(
    ("at", "expected"),
    [
        (T0 - timedelta(days=3650), False),
        (T0 - timedelta(seconds=1), False),
        (T0 - MICRO, False),
        (T0, True),  # exactly at valid_from: permitted
        (T0 + MICRO, True),
        (T0 + timedelta(days=1), True),
        (UNTIL - timedelta(seconds=1), True),
        (UNTIL - MICRO, True),  # just before valid_until: permitted
        (UNTIL, False),  # exactly at valid_until: denied
        (UNTIL + MICRO, False),
        (UNTIL + timedelta(days=3650), False),
    ],
)
def test_validity_window_boundaries(purpose: Purpose, at: datetime, expected: bool) -> None:
    assert evaluate(view(valid_until=UNTIL), purpose, at=at) is expected


@pytest.mark.parametrize("purpose", PURPOSES)
@pytest.mark.parametrize("at", [T0, T0 + timedelta(days=36500)])
def test_open_ended_record_never_expires(purpose: Purpose, at: datetime) -> None:
    assert evaluate(view(valid_until=None), purpose, at=at) is True


@pytest.mark.parametrize("purpose", PURPOSES)
def test_boundaries_compare_instants_not_wall_clock_fields(purpose: Purpose) -> None:
    plus_14 = timezone(timedelta(hours=14))
    minus_12 = timezone(timedelta(hours=-12))
    record = view(valid_from=T0.astimezone(plus_14), valid_until=UNTIL.astimezone(minus_12))

    assert evaluate(record, purpose, at=T0.astimezone(minus_12)) is True
    assert evaluate(record, purpose, at=(T0 - MICRO).astimezone(plus_14)) is False
    assert evaluate(record, purpose, at=(UNTIL - MICRO).astimezone(plus_14)) is True
    assert evaluate(record, purpose, at=UNTIL.astimezone(plus_14)) is False


@pytest.mark.parametrize("purpose", PURPOSES)
@pytest.mark.parametrize(
    "revoked_at",
    [
        T0 - timedelta(days=1),  # before validity even began
        T0,
        T0 + timedelta(days=1),  # in the past relative to `at`
        T0 + timedelta(days=2),  # exactly at `at`
        T0 + timedelta(days=2) + MICRO,  # a future revocation still denies
        T0 + timedelta(days=30),
        UNTIL + timedelta(days=30),  # after the record would have expired anyway
        datetime(9000, 1, 1, tzinfo=UTC),
    ],
)
def test_any_revocation_denies_even_a_future_one(purpose: Purpose, revoked_at: datetime) -> None:
    record = view(revoked_at=revoked_at)
    at = T0 + timedelta(days=2)

    assert evaluate(record, purpose, at=at) is False


@pytest.mark.parametrize("purpose", PURPOSES)
def test_unrevoked_record_is_unaffected(purpose: Purpose) -> None:
    assert evaluate(view(revoked_at=None), purpose, at=T0 + timedelta(days=2)) is True


def test_ai_flag_off_denies_ai_processing_only() -> None:
    record = view(allows_ai_processing=False)
    at = T0 + timedelta(days=1)

    assert evaluate(record, Purpose.AI_PROCESSING, at=at) is False
    assert evaluate(record, Purpose.DISPLAY, at=at) is True
    assert evaluate(record, Purpose.COMMERCIAL_USE, at=at) is True


def test_commercial_flag_off_denies_commercial_use_only() -> None:
    record = view(allows_commercial_use=False)
    at = T0 + timedelta(days=1)

    assert evaluate(record, Purpose.COMMERCIAL_USE, at=at) is False
    assert evaluate(record, Purpose.DISPLAY, at=at) is True
    assert evaluate(record, Purpose.AI_PROCESSING, at=at) is True


def test_flags_on_permit_their_purposes_even_when_display_scope_is_none() -> None:
    record = view(display_scope=DisplayScope.NONE, display_organization_id=None)
    at = T0 + timedelta(days=1)

    assert evaluate(record, Purpose.AI_PROCESSING, at=at) is True
    assert evaluate(record, Purpose.COMMERCIAL_USE, at=at) is True
    assert evaluate(record, Purpose.DISPLAY, at=at) is False


def test_display_does_not_depend_on_the_two_flags() -> None:
    record = view(allows_ai_processing=False, allows_commercial_use=False)

    assert evaluate(record, Purpose.DISPLAY, at=T0 + timedelta(days=1)) is True


@pytest.mark.parametrize(
    ("scope", "record_org", "caller_org", "expected"),
    [
        (DisplayScope.ALL, None, None, True),
        (DisplayScope.ALL, None, ORG_A, True),
        (DisplayScope.ALL, None, ORG_B, True),
        (DisplayScope.ORGANIZATION, ORG_A, ORG_A, True),
        (DisplayScope.ORGANIZATION, ORG_A, ORG_B, False),
        (DisplayScope.ORGANIZATION, ORG_A, None, False),
        (DisplayScope.ORGANIZATION, ORG_B, ORG_A, False),
        (DisplayScope.NONE, None, None, False),
        (DisplayScope.NONE, None, ORG_A, False),
        (DisplayScope.NONE, None, ORG_B, False),
    ],
)
def test_display_scope_matrix(
    scope: DisplayScope,
    record_org: uuid.UUID | None,
    caller_org: uuid.UUID | None,
    expected: bool,
) -> None:
    record = view(display_scope=scope, display_organization_id=record_org)

    result = evaluate(
        record, Purpose.DISPLAY, at=T0 + timedelta(days=1), organization_id=caller_org
    )

    assert result is expected


@pytest.mark.parametrize("scope", [DisplayScope.ORGANIZATION, DisplayScope.ALL, DisplayScope.NONE])
def test_display_obeys_the_validity_window_under_every_scope(
    scope: DisplayScope,
) -> None:
    org = ORG_A if scope is DisplayScope.ORGANIZATION else None
    record = view(display_scope=scope, display_organization_id=org, valid_until=UNTIL)
    expected_inside = scope is not DisplayScope.NONE

    assert evaluate(record, Purpose.DISPLAY, at=T0 - MICRO, organization_id=ORG_A) is False
    assert evaluate(record, Purpose.DISPLAY, at=T0, organization_id=ORG_A) is expected_inside
    assert evaluate(record, Purpose.DISPLAY, at=UNTIL, organization_id=ORG_A) is False


@pytest.mark.parametrize("purpose", [Purpose.AI_PROCESSING, Purpose.COMMERCIAL_USE])
@pytest.mark.parametrize(
    ("scope", "record_org"),
    [
        (DisplayScope.NONE, None),
        (DisplayScope.ORGANIZATION, ORG_A),
        (DisplayScope.ALL, None),
    ],
)
@pytest.mark.parametrize("caller_org", [None, ORG_A, ORG_B])
def test_organization_is_ignored_for_non_display_purposes(
    purpose: Purpose,
    scope: DisplayScope,
    record_org: uuid.UUID | None,
    caller_org: uuid.UUID | None,
) -> None:
    record = view(display_scope=scope, display_organization_id=record_org)

    assert evaluate(record, purpose, at=T0, organization_id=caller_org) is True


@pytest.mark.parametrize("purpose", PURPOSES)
def test_naive_at_raises_value_error(purpose: Purpose) -> None:
    naive = datetime(2030, 6, 1, 12, 0, 0)

    with pytest.raises(ValueError):
        evaluate(OPEN_RECORD, purpose, at=naive)


@pytest.mark.parametrize("purpose", PURPOSES)
def test_naive_at_raises_value_error_even_without_a_record(purpose: Purpose) -> None:
    """Literal reading: "a naive datetime raises ValueError" is unconditional."""
    naive = datetime(2030, 6, 1, 12, 0, 0)

    with pytest.raises(ValueError):
        evaluate(None, purpose, at=naive)


def test_evaluate_returns_a_plain_bool() -> None:
    assert evaluate(OPEN_RECORD, Purpose.DISPLAY, at=T0) is True
    assert evaluate(None, Purpose.DISPLAY, at=T0) is False


# --- Hypothesis -----------------------------------------------------------------------------

_offsets = st.integers(min_value=-14 * 60, max_value=14 * 60).map(
    lambda minutes: timezone(timedelta(minutes=minutes))
)
aware_datetimes = st.datetimes(
    min_value=datetime(1971, 1, 1),
    max_value=datetime(2200, 1, 1),
    timezones=_offsets,
)
optional_datetimes = st.none() | aware_datetimes
optional_orgs = st.none() | st.sampled_from([ORG_A, ORG_B]) | st.uuids()


@given(
    purpose=st.sampled_from(PURPOSES),
    at=aware_datetimes,
    valid_from=aware_datetimes,
    valid_until=optional_datetimes,
    revoked_at=optional_datetimes,
    caller_org=optional_orgs,
)
def test_a_record_with_every_permission_off_is_denied_everywhere(
    purpose: Purpose,
    at: datetime,
    valid_from: datetime,
    valid_until: datetime | None,
    revoked_at: datetime | None,
    caller_org: uuid.UUID | None,
) -> None:
    record = view(
        display_scope=DisplayScope.NONE,
        display_organization_id=None,
        allows_ai_processing=False,
        allows_commercial_use=False,
        valid_from=valid_from,
        valid_until=valid_until,
        revoked_at=revoked_at,
    )

    assert evaluate(record, purpose, at=at, organization_id=caller_org) is False


@given(
    purpose=st.sampled_from(PURPOSES),
    at=aware_datetimes,
    valid_from=aware_datetimes,
    valid_until=optional_datetimes,
    revoked_at=optional_datetimes,
    caller_org=optional_orgs,
)
def test_a_fully_permissive_record_is_permitted_exactly_inside_its_window(
    purpose: Purpose,
    at: datetime,
    valid_from: datetime,
    valid_until: datetime | None,
    revoked_at: datetime | None,
    caller_org: uuid.UUID | None,
) -> None:
    record = view(
        valid_from=valid_from, valid_until=valid_until, revoked_at=revoked_at
    )  # scope ALL, both flags on
    expected = valid_from <= at and (valid_until is None or at < valid_until) and revoked_at is None

    assert evaluate(record, purpose, at=at, organization_id=caller_org) is expected


@given(at=aware_datetimes, caller_org=optional_orgs, purpose=st.sampled_from(PURPOSES))
def test_no_record_is_denied_at_every_instant(
    at: datetime, caller_org: uuid.UUID | None, purpose: Purpose
) -> None:
    assert evaluate(None, purpose, at=at, organization_id=caller_org) is False


# =============================================================================================
# Database: create_record / get_record
# =============================================================================================

HOUR = timedelta(hours=1)
DAY = timedelta(days=1)


def _rights_count(connection: Connection) -> int:
    return int(connection.execute(text("SELECT count(*) FROM rights_record")).scalar_one())


@pytest.mark.db
def test_create_record_defaults_everything_to_off(session: Session) -> None:
    created = create_record(session, holder="Synthetic Holder", valid_from=T0)

    assert isinstance(created.id, uuid.UUID)
    assert created.holder == "Synthetic Holder"
    assert created.display_scope == DisplayScope.NONE
    assert created.display_organization_id is None
    assert created.allows_ai_processing is False
    assert created.allows_commercial_use is False
    assert created.valid_from == T0
    assert created.valid_until is None
    assert created.revoked_at is None
    assert created.license_ref is None


@pytest.mark.db
def test_default_record_permits_nothing(session: Session) -> None:
    created = create_record(session, holder="Synthetic Holder", valid_from=T0)

    for purpose in PURPOSES:
        assert evaluate(created, purpose, at=T0 + DAY, organization_id=ORG_A) is False


@pytest.mark.db
def test_create_record_stores_every_given_value(session: Session) -> None:
    created = create_record(
        session,
        holder="Synthetic Holder",
        valid_from=T0,
        display_scope=DisplayScope.ORGANIZATION,
        display_organization_id=ORG_A,
        allows_ai_processing=True,
        allows_commercial_use=True,
        valid_until=UNTIL,
        license_ref="LIC-0001 (synthetic)",
        note="synthetic note",
    )

    assert created.holder == "Synthetic Holder"
    assert created.license_ref == "LIC-0001 (synthetic)"
    assert created.display_scope == DisplayScope.ORGANIZATION
    assert created.display_organization_id == ORG_A
    assert created.allows_ai_processing is True
    assert created.allows_commercial_use is True
    assert created.valid_from == T0
    assert created.valid_until == UNTIL
    assert created.revoked_at is None


@pytest.mark.db
def test_returned_view_matches_get_record(session: Session) -> None:
    created = create_record(
        session,
        holder="Synthetic Holder",
        valid_from=T0,
        valid_until=UNTIL,
        display_scope=DisplayScope.ALL,
        allows_ai_processing=True,
        license_ref="LIC-2",
    )

    session.expire_all()
    fetched = get_record(session, created.id)

    assert fetched == created


@pytest.mark.db
def test_note_is_stored(session: Session, connection: Connection) -> None:
    created = create_record(session, holder="Synthetic Holder", valid_from=T0, note="kept")

    stored = connection.execute(
        text("SELECT note FROM rights_record WHERE id = :id"), {"id": created.id}
    ).scalar_one()
    assert stored == "kept"


@pytest.mark.db
def test_each_call_creates_a_distinct_record(session: Session, connection: Connection) -> None:
    first = create_record(session, holder="Synthetic Holder", valid_from=T0)
    second = create_record(session, holder="Synthetic Holder", valid_from=T0)

    assert first.id != second.id
    assert _rights_count(connection) == 2


@pytest.mark.db
def test_valid_from_given_in_another_timezone_is_the_same_instant(session: Session) -> None:
    offset = timezone(timedelta(hours=-7))

    created = create_record(session, holder="Synthetic Holder", valid_from=T0.astimezone(offset))

    fetched = get_record(session, created.id)
    assert fetched is not None
    assert fetched.valid_from == T0
    assert fetched.valid_from.tzinfo is not None


@pytest.mark.db
def test_get_record_unknown_id_is_none(session: Session) -> None:
    assert get_record(session, uuid.uuid4()) is None


@pytest.mark.db
def test_get_record_does_not_confuse_records(session: Session) -> None:
    a = create_record(session, holder="Holder A", valid_from=T0)
    b = create_record(session, holder="Holder B", valid_from=T0 + DAY)

    fetched_a = get_record(session, a.id)
    fetched_b = get_record(session, b.id)

    assert fetched_a is not None
    assert fetched_b is not None
    assert (fetched_a.holder, fetched_b.holder) == ("Holder A", "Holder B")


@pytest.mark.db
def test_created_record_rolls_back_with_the_callers_transaction(
    session: Session, connection: Connection
) -> None:
    savepoint = session.begin_nested()
    created = create_record(session, holder="Synthetic Holder", valid_from=T0)
    assert get_record(session, created.id) is not None
    savepoint.rollback()

    assert get_record(session, created.id) is None
    assert _rights_count(connection) == 0


NAIVE = datetime(2030, 3, 1, 12, 0, 0)

INVALID_CREATE_ARGUMENTS: dict[str, dict[str, Any]] = {
    "empty_holder": {"holder": ""},
    "space_holder": {"holder": "   "},
    "whitespace_holder": {"holder": " \t\n "},
    "naive_valid_from": {"valid_from": NAIVE},
    "naive_valid_until": {"valid_until": datetime(2031, 3, 1)},
    "valid_until_equals_valid_from": {"valid_until": T0},
    "valid_until_before_valid_from": {"valid_until": T0 - MICRO},
    "valid_until_long_before": {"valid_until": T0 - timedelta(days=400)},
    "organization_id_with_scope_none": {
        "display_scope": DisplayScope.NONE,
        "display_organization_id": ORG_A,
    },
    "organization_id_with_scope_all": {
        "display_scope": DisplayScope.ALL,
        "display_organization_id": ORG_A,
    },
    "organization_id_with_default_scope": {"display_organization_id": ORG_A},
    "scope_organization_without_id": {"display_scope": DisplayScope.ORGANIZATION},
    "scope_organization_with_explicit_none_id": {
        "display_scope": DisplayScope.ORGANIZATION,
        "display_organization_id": None,
    },
}


@pytest.mark.db
@pytest.mark.parametrize(
    "overrides", INVALID_CREATE_ARGUMENTS.values(), ids=INVALID_CREATE_ARGUMENTS.keys()
)
def test_invalid_create_arguments_raise_value_error_and_write_nothing(
    session: Session, connection: Connection, overrides: dict[str, Any]
) -> None:
    arguments: dict[str, Any] = {"holder": "Synthetic Holder", "valid_from": T0}
    arguments.update(overrides)
    before = _rights_count(connection)

    with pytest.raises(ValueError):
        create_record(session, **arguments)

    assert _rights_count(connection) == before


@pytest.mark.db
def test_valid_until_one_microsecond_after_valid_from_is_accepted(session: Session) -> None:
    created = create_record(
        session, holder="Synthetic Holder", valid_from=T0, valid_until=T0 + MICRO
    )

    assert created.valid_until == T0 + MICRO


@pytest.mark.db
def test_organization_scope_with_an_organization_is_accepted(session: Session) -> None:
    created = create_record(
        session,
        holder="Synthetic Holder",
        valid_from=T0,
        display_scope=DisplayScope.ORGANIZATION,
        display_organization_id=ORG_B,
    )

    # Display needs only the scope and the organization, not the two flags.
    assert evaluate(created, Purpose.DISPLAY, at=T0, organization_id=ORG_B) is True
    assert is_permitted(session, created.id, Purpose.DISPLAY, at=T0, organization_id=ORG_B)


# =============================================================================================
# Database: revoke
# =============================================================================================


@pytest.mark.db
def test_revoke_sets_revoked_at(session: Session) -> None:
    created = create_record(session, holder="Synthetic Holder", valid_from=T0)

    revoke(session, created.id, at=T0 + DAY)

    fetched = get_record(session, created.id)
    assert fetched is not None
    assert fetched.revoked_at == T0 + DAY


@pytest.mark.db
def test_revoke_touches_nothing_but_revoked_at(session: Session) -> None:
    created = create_record(
        session,
        holder="Synthetic Holder",
        valid_from=T0,
        valid_until=UNTIL,
        display_scope=DisplayScope.ALL,
        allows_ai_processing=True,
        license_ref="LIC-3",
    )

    revoke(session, created.id, at=T0 + DAY)

    fetched = get_record(session, created.id)
    assert fetched == dataclasses.replace(created, revoked_at=T0 + DAY)


@pytest.mark.db
@pytest.mark.parametrize("second_offset", [timedelta(days=1), timedelta(days=-1), timedelta(0)])
def test_second_revoke_keeps_the_first_timestamp(
    session: Session, second_offset: timedelta
) -> None:
    created = create_record(session, holder="Synthetic Holder", valid_from=T0)
    first = T0 + DAY

    revoke(session, created.id, at=first)
    revoke(session, created.id, at=first + second_offset)

    fetched = get_record(session, created.id)
    assert fetched is not None
    assert fetched.revoked_at == first


@pytest.mark.db
def test_revoke_unknown_id_raises_lookup_error(session: Session) -> None:
    with pytest.raises(LookupError):
        revoke(session, uuid.uuid4(), at=T0)


@pytest.mark.db
def test_revoke_with_naive_at_raises_value_error_and_changes_nothing(session: Session) -> None:
    created = create_record(session, holder="Synthetic Holder", valid_from=T0)

    with pytest.raises(ValueError):
        revoke(session, created.id, at=NAIVE)

    fetched = get_record(session, created.id)
    assert fetched is not None
    assert fetched.revoked_at is None


@pytest.mark.db
def test_revoke_only_affects_the_given_record(session: Session) -> None:
    a = create_record(session, holder="Holder A", valid_from=T0)
    b = create_record(session, holder="Holder B", valid_from=T0)

    revoke(session, a.id, at=T0 + DAY)

    other = get_record(session, b.id)
    assert other is not None
    assert other.revoked_at is None


@pytest.mark.db
def test_revoked_record_is_denied_for_every_purpose_even_before_the_revocation_instant(
    session: Session,
) -> None:
    created = create_record(
        session,
        holder="Synthetic Holder",
        valid_from=T0,
        display_scope=DisplayScope.ALL,
        allows_ai_processing=True,
        allows_commercial_use=True,
    )
    assert all(is_permitted(session, created.id, p, at=T0 + HOUR) for p in PURPOSES)

    revoke(session, created.id, at=T0 + 10 * DAY)

    for purpose in PURPOSES:
        assert is_permitted(session, created.id, purpose, at=T0 + HOUR) is False
        assert is_permitted(session, created.id, purpose, at=T0 + 20 * DAY) is False


@pytest.mark.db
def test_revoke_rolls_back_with_the_callers_transaction(session: Session) -> None:
    created = create_record(session, holder="Synthetic Holder", valid_from=T0)

    savepoint = session.begin_nested()
    revoke(session, created.id, at=T0 + DAY)
    savepoint.rollback()

    fetched = get_record(session, created.id)
    assert fetched is not None
    assert fetched.revoked_at is None


# =============================================================================================
# Database: is_permitted / require
# =============================================================================================


def _permissive(session: Session, **overrides: Any) -> RightsRecordView:
    arguments: dict[str, Any] = {
        "holder": "Synthetic Holder",
        "valid_from": T0,
        "display_scope": DisplayScope.ALL,
        "allows_ai_processing": True,
        "allows_commercial_use": True,
    }
    arguments.update(overrides)
    return create_record(session, **arguments)


@pytest.mark.db
@pytest.mark.parametrize("purpose", PURPOSES)
def test_none_id_is_denied(session: Session, purpose: Purpose) -> None:
    assert is_permitted(session, None, purpose, at=T0) is False
    assert is_permitted(session, None, purpose) is False
    assert is_permitted(session, None, purpose, at=T0, organization_id=ORG_A) is False


@pytest.mark.db
@pytest.mark.parametrize("purpose", PURPOSES)
def test_unknown_id_is_denied(session: Session, purpose: Purpose) -> None:
    assert is_permitted(session, uuid.uuid4(), purpose, at=T0) is False
    assert is_permitted(session, uuid.uuid4(), purpose) is False


@pytest.mark.db
@pytest.mark.parametrize("purpose", PURPOSES)
def test_stored_permissive_record_is_permitted(session: Session, purpose: Purpose) -> None:
    created = _permissive(session)

    assert is_permitted(session, created.id, purpose, at=T0 + DAY) is True


@pytest.mark.db
def test_stored_record_decisions_agree_with_evaluate(session: Session) -> None:
    created = _permissive(
        session,
        valid_until=UNTIL,
        allows_commercial_use=False,
        display_scope=DisplayScope.ORGANIZATION,
        display_organization_id=ORG_A,
    )
    instants = [T0 - MICRO, T0, T0 + DAY, UNTIL - MICRO, UNTIL, UNTIL + DAY]

    for purpose in PURPOSES:
        for org in (None, ORG_A, ORG_B):
            for at in instants:
                expected = evaluate(created, purpose, at=at, organization_id=org)
                assert is_permitted(session, created.id, purpose, at=at, organization_id=org) is (
                    expected
                )


@pytest.mark.db
def test_stored_record_denies_when_the_flag_is_off(session: Session) -> None:
    created = _permissive(session, allows_ai_processing=False)

    assert is_permitted(session, created.id, Purpose.AI_PROCESSING, at=T0 + DAY) is False
    assert is_permitted(session, created.id, Purpose.COMMERCIAL_USE, at=T0 + DAY) is True


@pytest.mark.db
def test_stored_record_boundaries(session: Session) -> None:
    created = _permissive(session, valid_until=UNTIL)

    assert is_permitted(session, created.id, Purpose.AI_PROCESSING, at=T0 - MICRO) is False
    assert is_permitted(session, created.id, Purpose.AI_PROCESSING, at=T0) is True
    assert is_permitted(session, created.id, Purpose.AI_PROCESSING, at=UNTIL - MICRO) is True
    assert is_permitted(session, created.id, Purpose.AI_PROCESSING, at=UNTIL) is False


@pytest.mark.db
def test_organization_scope_is_enforced_for_stored_records(session: Session) -> None:
    created = _permissive(
        session, display_scope=DisplayScope.ORGANIZATION, display_organization_id=ORG_A
    )
    at = T0 + DAY

    assert is_permitted(session, created.id, Purpose.DISPLAY, at=at, organization_id=ORG_A)
    assert not is_permitted(session, created.id, Purpose.DISPLAY, at=at, organization_id=ORG_B)
    assert not is_permitted(session, created.id, Purpose.DISPLAY, at=at)
    assert is_permitted(session, created.id, Purpose.AI_PROCESSING, at=at, organization_id=ORG_B)


@pytest.mark.db
def test_at_defaults_to_now_for_a_record_valid_now(session: Session) -> None:
    now = datetime.now(UTC)
    created = _permissive(session, valid_from=now - DAY, valid_until=now + DAY)

    for purpose in PURPOSES:
        assert is_permitted(session, created.id, purpose) is True
        assert is_permitted(session, created.id, purpose, at=now - 2 * DAY) is False
        assert is_permitted(session, created.id, purpose, at=now + 2 * DAY) is False


@pytest.mark.db
def test_at_defaults_to_now_for_a_record_not_yet_valid(session: Session) -> None:
    now = datetime.now(UTC)
    created = _permissive(session, valid_from=now + DAY)

    assert is_permitted(session, created.id, Purpose.AI_PROCESSING) is False
    assert is_permitted(session, created.id, Purpose.AI_PROCESSING, at=now + 2 * DAY) is True


@pytest.mark.db
def test_at_defaults_to_now_for_an_expired_record(session: Session) -> None:
    now = datetime.now(UTC)
    created = _permissive(session, valid_from=now - 2 * DAY, valid_until=now - DAY)

    assert is_permitted(session, created.id, Purpose.AI_PROCESSING) is False
    assert is_permitted(session, created.id, Purpose.AI_PROCESSING, at=now - 36 * HOUR) is True


@pytest.mark.db
def test_future_revocation_denies_with_default_at(session: Session) -> None:
    now = datetime.now(UTC)
    created = _permissive(session, valid_from=now - DAY)
    assert is_permitted(session, created.id, Purpose.COMMERCIAL_USE) is True

    revoke(session, created.id, at=now + DAY)

    assert is_permitted(session, created.id, Purpose.COMMERCIAL_USE) is False


@pytest.mark.db
def test_is_permitted_with_naive_at_raises_value_error(session: Session) -> None:
    created = _permissive(session)

    with pytest.raises(ValueError):
        is_permitted(session, created.id, Purpose.AI_PROCESSING, at=NAIVE)


@pytest.mark.db
@pytest.mark.parametrize("purpose", PURPOSES)
def test_require_returns_none_when_permitted(session: Session, purpose: Purpose) -> None:
    created = _permissive(session)

    require(session, created.id, purpose, at=T0 + DAY)  # does not raise


@pytest.mark.db
@pytest.mark.parametrize("purpose", PURPOSES)
def test_require_raises_for_none_id(session: Session, purpose: Purpose) -> None:
    with pytest.raises(RightsDenied):
        require(session, None, purpose, at=T0)
    with pytest.raises(RightsDenied):
        require(session, None, purpose)


@pytest.mark.db
@pytest.mark.parametrize("purpose", PURPOSES)
def test_require_raises_for_unknown_id(session: Session, purpose: Purpose) -> None:
    with pytest.raises(RightsDenied):
        require(session, uuid.uuid4(), purpose, at=T0)


@pytest.mark.db
def test_require_raises_for_denied_records(session: Session) -> None:
    flag_off = _permissive(session, allows_ai_processing=False)
    expired = _permissive(session, valid_until=UNTIL)
    not_yet = _permissive(session, valid_from=T0)
    revoked = _permissive(session)
    revoke(session, revoked.id, at=T0 + HOUR)
    org_only = _permissive(
        session, display_scope=DisplayScope.ORGANIZATION, display_organization_id=ORG_A
    )

    with pytest.raises(RightsDenied):
        require(session, flag_off.id, Purpose.AI_PROCESSING, at=T0 + DAY)
    with pytest.raises(RightsDenied):
        require(session, expired.id, Purpose.DISPLAY, at=UNTIL)
    with pytest.raises(RightsDenied):
        require(session, not_yet.id, Purpose.DISPLAY, at=T0 - MICRO)
    with pytest.raises(RightsDenied):
        require(session, revoked.id, Purpose.DISPLAY, at=T0 + DAY)
    with pytest.raises(RightsDenied):
        require(session, org_only.id, Purpose.DISPLAY, at=T0 + DAY, organization_id=ORG_B)
    require(session, org_only.id, Purpose.DISPLAY, at=T0 + DAY, organization_id=ORG_A)


@pytest.mark.db
def test_require_at_defaults_to_now(session: Session) -> None:
    now = datetime.now(UTC)
    valid = _permissive(session, valid_from=now - DAY, valid_until=now + DAY)
    expired = _permissive(session, valid_from=now - 2 * DAY, valid_until=now - DAY)

    require(session, valid.id, Purpose.AI_PROCESSING)
    with pytest.raises(RightsDenied):
        require(session, expired.id, Purpose.AI_PROCESSING)


# =============================================================================================
# Database: CHECK constraints (raw SQL, because the spec is about the table itself)
# =============================================================================================

RAW_INSERT = text(
    "INSERT INTO rights_record "
    "(id, holder, display_scope, display_organization_id, valid_from, valid_until) "
    "VALUES (:id, 'raw holder', :scope, :org, :valid_from, :valid_until)"
)


def _raw_insert(connection: Connection, **overrides: Any) -> None:
    parameters: dict[str, Any] = {
        "id": uuid.uuid4(),
        "scope": "none",
        "org": None,
        "valid_from": T0,
        "valid_until": None,
    }
    parameters.update(overrides)
    connection.execute(RAW_INSERT, parameters)


@pytest.mark.db
@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"scope": "all"},
        {"scope": "organization", "org": ORG_A},
        {"valid_until": T0 + MICRO},
    ],
    ids=["none", "all", "organization", "minimal_window"],
)
def test_raw_insert_of_a_valid_row_succeeds(
    connection: Connection, overrides: dict[str, Any]
) -> None:
    _raw_insert(connection, **overrides)

    assert _rights_count(connection) == 1


@pytest.mark.db
def test_defaults_of_the_table_are_all_off(connection: Connection) -> None:
    _raw_insert(connection)

    row = connection.execute(
        text(
            "SELECT display_scope, allows_ai_processing, allows_commercial_use, revoked_at "
            "FROM rights_record"
        )
    ).one()
    assert tuple(row) == ("none", False, False, None)


@pytest.mark.db
@pytest.mark.parametrize(
    ("overrides", "constraint"),
    [
        ({"scope": "bogus"}, "ck_rights_record_display_scope"),
        ({"scope": ""}, "ck_rights_record_display_scope"),
        ({"scope": "ALL"}, "ck_rights_record_display_scope"),
        ({"scope": "organization", "org": None}, "ck_rights_record_display_organization"),
        ({"scope": "none", "org": ORG_A}, "ck_rights_record_display_organization"),
        ({"scope": "all", "org": ORG_A}, "ck_rights_record_display_organization"),
        ({"valid_until": T0}, "ck_rights_record_validity_order"),
        ({"valid_until": T0 - MICRO}, "ck_rights_record_validity_order"),
        ({"valid_until": T0 - timedelta(days=100)}, "ck_rights_record_validity_order"),
    ],
    ids=[
        "scope_unknown",
        "scope_empty",
        "scope_wrong_case",
        "organization_without_id",
        "none_with_id",
        "all_with_id",
        "until_equals_from",
        "until_just_before_from",
        "until_long_before_from",
    ],
)
def test_check_constraints_reject_bad_rows(
    connection: Connection, overrides: dict[str, Any], constraint: str
) -> None:
    with pytest.raises(IntegrityError, match=constraint), connection.begin_nested():
        _raw_insert(connection, **overrides)

    assert _rights_count(connection) == 0


@pytest.mark.db
def test_holder_and_valid_from_are_required(connection: Connection) -> None:
    with pytest.raises(DBAPIError), connection.begin_nested():
        connection.execute(
            text("INSERT INTO rights_record (id, valid_from) VALUES (:id, :vf)"),
            {"id": uuid.uuid4(), "vf": T0},
        )
    with pytest.raises(DBAPIError), connection.begin_nested():
        connection.execute(
            text("INSERT INTO rights_record (id, holder) VALUES (:id, 'h')"),
            {"id": uuid.uuid4()},
        )

    assert _rights_count(connection) == 0


# =============================================================================================
# find_by_license_ref
# =============================================================================================

REF = "synthetic:licence-a"


def _with_ref(session: Session, ref: str | None, **kwargs: Any) -> RightsRecordView:
    kwargs.setdefault("valid_from", T0)
    return create_record(session, holder="Synthetic Holder", license_ref=ref, **kwargs)


@pytest.mark.db
def test_find_by_license_ref_returns_every_record_with_the_reference_oldest_first(
    session: Session,
) -> None:
    first = _with_ref(session, REF, valid_from=T0)
    second = _with_ref(session, REF, valid_from=T0 + timedelta(days=1))
    third = _with_ref(session, REF, valid_from=T0 + timedelta(days=2))

    found = find_by_license_ref(session, REF)

    assert [record.id for record in found] == [first.id, second.id, third.id]
    assert all(record.license_ref == REF for record in found)


@pytest.mark.db
def test_find_by_license_ref_returns_the_record_as_get_record_does(session: Session) -> None:
    created = _with_ref(
        session,
        REF,
        display_scope=DisplayScope.ALL,
        allows_ai_processing=True,
        allows_commercial_use=True,
        valid_until=UNTIL,
    )

    assert find_by_license_ref(session, REF) == [get_record(session, created.id)]


@pytest.mark.db
def test_find_by_license_ref_with_no_match_is_an_empty_list(session: Session) -> None:
    assert find_by_license_ref(session, REF) == []

    _with_ref(session, "synthetic:other")
    _with_ref(session, None)

    assert find_by_license_ref(session, REF) == []


@pytest.mark.db
def test_find_by_license_ref_ignores_records_with_another_or_no_reference(
    session: Session,
) -> None:
    wanted = _with_ref(session, REF)
    _with_ref(session, "synthetic:other")
    _with_ref(session, None)
    _with_ref(session, REF + "-2")
    _with_ref(session, REF.upper())

    assert [record.id for record in find_by_license_ref(session, REF)] == [wanted.id]


@pytest.mark.db
def test_find_by_license_ref_includes_revoked_and_expired_records(session: Session) -> None:
    revoked = _with_ref(session, REF, valid_from=T0)
    expired = _with_ref(
        session,
        REF,
        valid_from=T0 + timedelta(days=1),
        valid_until=T0 + timedelta(days=2),
    )
    live = _with_ref(session, REF, valid_from=T0 + timedelta(days=3))
    revoke(session, revoked.id, at=T0 + timedelta(hours=1))

    found = {record.id: record for record in find_by_license_ref(session, REF)}

    assert set(found) == {revoked.id, expired.id, live.id}
    assert found[revoked.id].revoked_at == T0 + timedelta(hours=1)
    assert found[expired.id].valid_until == T0 + timedelta(days=2)
    assert found[live.id].revoked_at is None


@pytest.mark.db
def test_find_by_license_ref_sees_a_revocation_made_by_raw_sql_after_an_earlier_call(
    session: Session,
) -> None:
    created = _with_ref(session, REF)
    before = find_by_license_ref(session, REF)
    assert [record.revoked_at for record in before] == [None]

    session.execute(
        text("UPDATE rights_record SET revoked_at = :at WHERE id = :id"),
        {"at": T0 + timedelta(minutes=5), "id": created.id},
    )

    after = find_by_license_ref(session, REF)
    assert [record.id for record in after] == [created.id]
    assert after[0].revoked_at == T0 + timedelta(minutes=5)


@pytest.mark.db
def test_find_by_license_ref_matches_the_reference_exactly(session: Session) -> None:
    _with_ref(session, REF)

    assert find_by_license_ref(session, "") == []
    assert find_by_license_ref(session, REF + " ") == []
    assert find_by_license_ref(session, REF[:-1]) == []
    assert find_by_license_ref(session, "%") == []
    assert find_by_license_ref(session, REF.replace("a", "_")) == []
