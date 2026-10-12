"""Audit service: append inside the caller's transaction, read back per entity, never rewrite.

Written from the docstrings of qlab.audit.service and migration 0001 only.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from types import MappingProxyType
from typing import Any

import pytest
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from qlab.audit.service import AuditEntry, entries_for, record

pytestmark = pytest.mark.db

ENTITY_TYPE = "question_version"
ENTITY_ID = "0b6c1a7e-0000-4000-8000-000000000001"


class _Boom(Exception):  # not RuntimeError: NotImplementedError is one
    pass


def _count(connection: Connection) -> int:
    return int(connection.execute(text("SELECT count(*) FROM audit_log")).scalar_one())


def _record(session: Session, **overrides: Any) -> AuditEntry:
    arguments: dict[str, Any] = {
        "actor": "system:test",
        "action": "question_version.published",
        "entity_type": ENTITY_TYPE,
        "entity_id": ENTITY_ID,
    }
    arguments.update(overrides)
    return record(session, **arguments)


# --- record / entries_for -------------------------------------------------------------------


def test_record_returns_the_entry_it_was_given(session: Session) -> None:
    entry = _record(session, actor="account-17", action="rights.revoked", entity_id="e-1")

    assert isinstance(entry, AuditEntry)
    assert entry.actor == "account-17"
    assert entry.action == "rights.revoked"
    assert entry.entity_type == ENTITY_TYPE
    assert entry.entity_id == "e-1"


def test_recorded_entry_is_readable_through_entries_for(session: Session) -> None:
    entry = _record(session)

    session.expire_all()
    found = entries_for(session, ENTITY_TYPE, ENTITY_ID)

    assert len(found) == 1
    assert found[0].id == entry.id
    assert found[0].actor == entry.actor
    assert found[0].action == entry.action
    assert found[0].entity_type == entry.entity_type
    assert found[0].entity_id == entry.entity_id
    assert found[0].occurred_at == entry.occurred_at
    assert dict(found[0].data) == dict(entry.data)


def test_occurred_at_is_timezone_aware_and_recent(session: Session) -> None:
    entry = _record(session)

    assert entry.occurred_at.tzinfo is not None
    assert abs(datetime.now(UTC) - entry.occurred_at) < timedelta(minutes=10)


def test_every_entry_gets_its_own_id(session: Session) -> None:
    first = _record(session)
    second = _record(session)

    assert first.id != second.id


def test_entries_for_returns_oldest_first(session: Session) -> None:
    actions = [f"step.number_{n}" for n in range(6)]
    for action in actions:
        _record(session, action=action)

    found = entries_for(session, ENTITY_TYPE, ENTITY_ID)

    assert [entry.action for entry in found] == actions


def test_entries_for_returns_only_that_entity(session: Session) -> None:
    mine = _record(session, action="a.mine")
    _record(session, entity_id="other-id", action="a.other_id")
    _record(session, entity_type="exam", action="a.other_type")
    _record(session, entity_type="exam", entity_id="other-id", action="a.other_both")
    last = _record(session, action="a.mine_again")

    found = entries_for(session, ENTITY_TYPE, ENTITY_ID)

    assert [entry.id for entry in found] == [mine.id, last.id]


def test_entries_for_unknown_entity_is_empty(session: Session) -> None:
    _record(session)

    assert entries_for(session, ENTITY_TYPE, "no-such-id") == []
    assert entries_for(session, "no_such_type", ENTITY_ID) == []


def test_entries_for_empty_log_is_empty(session: Session) -> None:
    assert entries_for(session, ENTITY_TYPE, ENTITY_ID) == []


def test_entity_id_is_matched_exactly(session: Session) -> None:
    _record(session, entity_id="Abc", action="a.upper")
    _record(session, entity_id="abc", action="a.lower")

    assert [e.action for e in entries_for(session, ENTITY_TYPE, "abc")] == ["a.lower"]


# --- data -----------------------------------------------------------------------------------


def test_data_defaults_to_an_empty_mapping(session: Session) -> None:
    entry = _record(session)

    assert dict(entry.data) == {}
    assert dict(entries_for(session, ENTITY_TYPE, ENTITY_ID)[0].data) == {}


def test_explicit_none_data_is_the_same_as_no_data(session: Session) -> None:
    entry = _record(session, data=None)

    assert dict(entry.data) == {}


def test_nested_json_data_round_trips(session: Session) -> None:
    payload: dict[str, Any] = {
        "from": "draft",
        "to": "published",
        "counts": [1, 2, 3],
        "mixed": [1, 2.5, "x", None, True, False, {"deep": {"deeper": []}}],
        "nested": {"a": {"b": {"c": "d"}}, "empty": {}},
        "text": "ğüşiöç ☃ \"quoted\" 'single'",
        "null": None,
    }
    entry = _record(session, data=payload)

    assert dict(entry.data) == payload
    session.expire_all()
    assert dict(entries_for(session, ENTITY_TYPE, ENTITY_ID)[0].data) == payload


def test_any_mapping_is_accepted_as_data(session: Session) -> None:
    mapping: Mapping[str, Any] = MappingProxyType({"k": ["v"]})

    entry = _record(session, data=mapping)

    assert dict(entry.data) == {"k": ["v"]}
    assert dict(entries_for(session, ENTITY_TYPE, ENTITY_ID)[0].data) == {"k": ["v"]}


@pytest.mark.parametrize(
    "action",
    [
        "question_version.published",
        "a.b",
        "a.b.c",
        "a1.b2_c",
        "rights.revoked",
        "x_y.z_9.w",
    ],
)
def test_valid_dotted_lowercase_actions_are_accepted(session: Session, action: str) -> None:
    assert _record(session, action=action).action == action


# --- invalid arguments ----------------------------------------------------------------------

BLANKS = ["", " ", "   ", "\t", "\n", " \t\n "]


@pytest.mark.parametrize("field", ["actor", "entity_type", "entity_id"])
@pytest.mark.parametrize("blank", BLANKS)
def test_blank_text_arguments_raise_value_error_and_write_nothing(
    session: Session, connection: Connection, field: str, blank: str
) -> None:
    before = _count(connection)

    with pytest.raises(ValueError):
        _record(session, **{field: blank})

    assert _count(connection) == before


@pytest.mark.parametrize(
    "action",
    [
        "",
        " ",
        "published",
        "Question.published",
        "question.Published",
        "QUESTION.PUBLISHED",
        "question..published",
        ".published",
        "question.",
        "question.published.",
        "1question.published",
        "question.1published",
        "question._published",
        "_question.published",
        "question.pub-lished",
        "question published",
        "question.publ ished",
        " question.published",
        "question.published ",
        "question:published",
        "question/published",
        "questıon.published",
    ],
)
def test_malformed_action_raises_value_error_and_writes_nothing(
    session: Session, connection: Connection, action: str
) -> None:
    before = _count(connection)

    with pytest.raises(ValueError):
        _record(session, action=action)

    assert _count(connection) == before
    assert entries_for(session, ENTITY_TYPE, ENTITY_ID) == []


def test_action_with_trailing_newline_is_rejected(session: Session, connection: Connection) -> None:
    """Literal reading of "dotted lower-case name": a newline is not part of a name."""
    before = _count(connection)

    with pytest.raises(ValueError):
        _record(session, action="question.published\n")

    assert _count(connection) == before


def test_invalid_call_does_not_disturb_earlier_entries(
    session: Session, connection: Connection
) -> None:
    kept = _record(session)

    with pytest.raises(ValueError):
        _record(session, actor=" ")

    assert [e.id for e in entries_for(session, ENTITY_TYPE, ENTITY_ID)] == [kept.id]
    assert _count(connection) == 1


# --- transaction behaviour ------------------------------------------------------------------


def test_entry_is_visible_inside_the_callers_transaction_before_commit(
    session: Session, connection: Connection
) -> None:
    entry = _record(session)

    # Same connection, so the flushed row is visible without any commit.
    stored = (
        connection.execute(
            text("SELECT id FROM audit_log WHERE entity_id = :entity_id"), {"entity_id": ENTITY_ID}
        )
        .scalars()
        .all()
    )
    assert stored == [entry.id]


def test_entry_rolls_back_with_the_callers_transaction(
    session: Session, connection: Connection
) -> None:
    outer_count = _count(connection)

    savepoint = session.begin_nested()
    _record(session)
    assert len(entries_for(session, ENTITY_TYPE, ENTITY_ID)) == 1
    savepoint.rollback()

    assert entries_for(session, ENTITY_TYPE, ENTITY_ID) == []
    assert _count(connection) == outer_count


def test_entry_rolls_back_when_the_block_raises(session: Session, connection: Connection) -> None:
    before = _count(connection)

    with pytest.raises(_Boom), session.begin_nested():
        _record(session)
        raise _Boom

    assert _count(connection) == before
    assert entries_for(session, ENTITY_TYPE, ENTITY_ID) == []


def test_entry_survives_when_the_savepoint_is_released(session: Session) -> None:
    with session.begin_nested():
        entry = _record(session)

    assert [e.id for e in entries_for(session, ENTITY_TYPE, ENTITY_ID)] == [entry.id]


def test_only_the_rolled_back_savepoint_loses_its_entries(session: Session) -> None:
    kept = _record(session, action="a.kept")

    savepoint = session.begin_nested()
    _record(session, action="a.lost")
    savepoint.rollback()

    assert [e.id for e in entries_for(session, ENTITY_TYPE, ENTITY_ID)] == [kept.id]


# --- append-only at the database level ------------------------------------------------------

REWRITING_STATEMENTS = {
    "update_one_row": "UPDATE audit_log SET actor = 'tampered' "
    "WHERE entity_id = 'append-only-check'",
    "update_every_row": "UPDATE audit_log SET action = 'tampered.action'",
    "update_data": "UPDATE audit_log SET data = '{\"x\": 1}'::jsonb "
    "WHERE entity_id = 'append-only-check'",
    "update_timestamp": "UPDATE audit_log SET occurred_at = now() - interval '1 day' "
    "WHERE entity_id = 'append-only-check'",
    "update_entity_id": "UPDATE audit_log SET entity_id = 'moved' "
    "WHERE entity_id = 'append-only-check'",
    "delete_one_row": "DELETE FROM audit_log WHERE entity_id = 'append-only-check'",
    "delete_every_row": "DELETE FROM audit_log",
    "truncate": "TRUNCATE audit_log",
    "truncate_restart_identity": "TRUNCATE TABLE audit_log RESTART IDENTITY",
    "truncate_cascade": "TRUNCATE audit_log CASCADE",
}


@pytest.mark.parametrize(
    "statement", REWRITING_STATEMENTS.values(), ids=REWRITING_STATEMENTS.keys()
)
def test_database_rejects_rewriting_the_log(
    session: Session, connection: Connection, statement: str
) -> None:
    entry = _record(
        session,
        entity_id="append-only-check",
        data={"original": True},
    )
    before = _count(connection)

    with pytest.raises(DBAPIError, match="append-only"), connection.begin_nested():
        connection.execute(text(statement))

    after = entries_for(session, ENTITY_TYPE, "append-only-check")
    assert [e.id for e in after] == [entry.id]
    assert after[0].actor == entry.actor
    assert after[0].action == entry.action
    assert after[0].occurred_at == entry.occurred_at
    assert dict(after[0].data) == {"original": True}
    assert _count(connection) == before


def test_appending_still_works_after_a_rejected_rewrite(
    session: Session, connection: Connection
) -> None:
    _record(session, entity_id="append-only-check", action="a.first")
    with pytest.raises(DBAPIError, match="append-only"), connection.begin_nested():
        connection.execute(text("DELETE FROM audit_log"))

    _record(session, entity_id="append-only-check", action="a.second")

    found = entries_for(session, ENTITY_TYPE, "append-only-check")
    assert [e.action for e in found] == ["a.first", "a.second"]
