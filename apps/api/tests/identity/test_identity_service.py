"""Accounts: `ensure_account`, `find_account`, `get_account`, `disable_account`, and the
database rules of the `account` table (migration 0005), checked with raw SQL.

An account is an identity provider subject and nothing else: no name, e-mail or password.
"""

from __future__ import annotations

import uuid

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from qlab.identity import service as identity
from qlab.identity.service import AccountView

pytestmark = pytest.mark.db

ISSUER = "https://issuer.example.invalid"
FIXTURE_SCOPE = settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=40
)


def unique(prefix: str = "user") -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def rejected(connection: Connection, sql: str, **params: object) -> str:
    """Run a statement that must fail; return the database's message."""
    with pytest.raises(DBAPIError) as caught, connection.begin_nested():
        connection.execute(text(sql), params)
    return str(caught.value.orig)


def insert_account(connection: Connection, issuer: str, subject: str) -> None:
    connection.execute(
        text("INSERT INTO account (id, issuer, subject) VALUES (:id, :issuer, :subject)"),
        {"id": uuid.uuid4(), "issuer": issuer, "subject": subject},
    )


def count(connection: Connection, issuer: str, subject: str) -> int:
    row = connection.execute(
        text("SELECT count(*) FROM account WHERE issuer = :i AND subject = :s"),
        {"i": issuer, "s": subject},
    ).scalar_one()
    return int(row)


# --- ensure_account --------------------------------------------------------------------------


def test_ensure_creates_an_active_account(session: Session) -> None:
    subject = unique()
    account = identity.ensure_account(session, issuer=ISSUER, subject=subject)
    assert isinstance(account, AccountView)
    assert (account.issuer, account.subject) == (ISSUER, subject)
    assert isinstance(account.id, uuid.UUID)
    assert account.disabled_at is None
    assert account.is_active
    assert account.created_at is not None


def test_ensure_is_idempotent(session: Session, connection: Connection) -> None:
    subject = unique()
    first = identity.ensure_account(session, issuer=ISSUER, subject=subject)
    second = identity.ensure_account(session, issuer=ISSUER, subject=subject)
    assert first == second
    assert count(connection, ISSUER, subject) == 1


def test_the_same_subject_at_two_issuers_is_two_accounts(session: Session) -> None:
    subject = unique()
    a = identity.ensure_account(session, issuer=ISSUER, subject=subject)
    b = identity.ensure_account(session, issuer=ISSUER + "/other", subject=subject)
    assert a.id != b.id


def test_two_subjects_are_two_accounts(session: Session) -> None:
    a = identity.ensure_account(session, issuer=ISSUER, subject=unique())
    b = identity.ensure_account(session, issuer=ISSUER, subject=unique())
    assert a.id != b.id


def test_ensure_does_not_enable_a_disabled_account(session: Session) -> None:
    """Registering again must not bring a disabled account back."""
    account = identity.ensure_account(session, issuer=ISSUER, subject=unique())
    identity.disable_account(session, account.id)
    again = identity.ensure_account(session, issuer=ISSUER, subject=account.subject)
    assert again.id == account.id
    assert not again.is_active


@pytest.mark.parametrize("value", ["", " ", "  ", " x", "x ", " x ", "\tx", "x\n", "\n", " x"])
def test_blank_or_padded_values_are_refused(session: Session, value: str) -> None:
    with pytest.raises(ValueError):
        identity.ensure_account(session, issuer=ISSUER, subject=value)
    with pytest.raises(ValueError):
        identity.ensure_account(session, issuer=value, subject=unique())


@pytest.mark.parametrize(
    "value",
    ["\x00", "a\x00b", "a\x1bb", "a\nb", "a\tb", "a\u2028b", "a\u2029b", "a\x7f", "a\u200bb"],
)
def test_non_printable_values_are_refused(
    session: Session, connection: Connection, value: str
) -> None:
    assert not value.isprintable()
    with pytest.raises(ValueError):
        identity.ensure_account(session, issuer=ISSUER, subject=value)
    with pytest.raises(ValueError):
        identity.ensure_account(session, issuer=value, subject=unique())
    assert count(connection, ISSUER, "a-clean-value") == 0
    assert (
        connection.execute(
            text("SELECT count(*) FROM account WHERE issuer = :i"), {"i": ISSUER}
        ).scalar_one()
        == 0
    )


def test_the_length_limit_is_200_characters(session: Session) -> None:
    ok = identity.ensure_account(session, issuer="i" * 200, subject="s" * 200)
    assert len(ok.issuer) == len(ok.subject) == 200
    with pytest.raises(ValueError):
        identity.ensure_account(session, issuer=ISSUER, subject="s" * 201)
    with pytest.raises(ValueError):
        identity.ensure_account(session, issuer="i" * 201, subject=unique())


def test_the_limit_counts_characters_not_bytes(session: Session) -> None:
    identity.ensure_account(session, issuer=ISSUER, subject="é" * 200)
    with pytest.raises(ValueError):
        identity.ensure_account(session, issuer=ISSUER, subject="é" * 201)


def test_refused_values_leave_nothing_behind(session: Session, connection: Connection) -> None:
    with pytest.raises(ValueError):
        identity.ensure_account(session, issuer=ISSUER, subject=" padded ")
    assert count(connection, ISSUER, " padded ") == 0


def test_inner_spaces_and_unicode_are_kept_verbatim(session: Session) -> None:
    for subject in ("a b", "user|42", "ünï-çödé", "日本語", "a\u00b7b"):
        account = identity.ensure_account(session, issuer=ISSUER, subject=subject)
        assert account.subject == subject


@FIXTURE_SCOPE
@given(
    st.text(
        alphabet=st.characters(
            blacklist_characters="\x00",
            blacklist_categories=["Cs", "Cc", "Cf", "Zl", "Zp", "Co", "Cn"],
        ),
        min_size=1,
        max_size=200,
    )
)
def test_any_clean_text_is_stored_and_found_verbatim(session: Session, value: str) -> None:
    if value != value.strip() or not value.isprintable():
        with pytest.raises(ValueError):
            identity.ensure_account(session, issuer=ISSUER, subject=value)
        return
    subject = value
    created = identity.ensure_account(session, issuer=ISSUER, subject=subject)
    found = identity.find_account(session, issuer=ISSUER, subject=subject)
    assert found == created
    assert found is not None and found.subject == subject


# --- find / get -------------------------------------------------------------------------------


def test_find_returns_none_for_an_unknown_account(session: Session) -> None:
    assert identity.find_account(session, issuer=ISSUER, subject=unique()) is None


def test_find_matches_issuer_and_subject_exactly(session: Session) -> None:
    subject = unique("MixedCase")
    account = identity.ensure_account(session, issuer=ISSUER, subject=subject)
    assert identity.find_account(session, issuer=ISSUER, subject=subject) == account
    assert identity.find_account(session, issuer=ISSUER, subject=subject.lower()) is None
    assert identity.find_account(session, issuer=ISSUER, subject=subject.upper()) is None
    assert identity.find_account(session, issuer=ISSUER.upper(), subject=subject) is None
    assert identity.find_account(session, issuer=ISSUER, subject=subject + " ") is None
    assert identity.find_account(session, issuer=ISSUER + "x", subject=subject) is None
    assert identity.find_account(session, issuer=subject, subject=ISSUER) is None


def test_find_treats_wildcards_literally(session: Session) -> None:
    identity.ensure_account(session, issuer=ISSUER, subject=unique())
    for pattern in ("%", "_", "%%", "user-%", "' OR '1'='1"):
        assert identity.find_account(session, issuer=ISSUER, subject=pattern) is None


def test_find_returns_a_disabled_account_marked_inactive(session: Session) -> None:
    account = identity.ensure_account(session, issuer=ISSUER, subject=unique())
    identity.disable_account(session, account.id)
    found = identity.find_account(session, issuer=ISSUER, subject=account.subject)
    assert found is not None
    assert found.id == account.id
    assert found.disabled_at is not None
    assert not found.is_active


def test_get_account_by_id(session: Session) -> None:
    account = identity.ensure_account(session, issuer=ISSUER, subject=unique())
    assert identity.get_account(session, account.id) == account
    assert identity.get_account(session, uuid.uuid4()) is None


def test_account_views_are_immutable(session: Session) -> None:
    account = identity.ensure_account(session, issuer=ISSUER, subject=unique())
    with pytest.raises(AttributeError):
        account.subject = "x"  # type: ignore[misc]


# --- disable ----------------------------------------------------------------------------------


def test_disable_marks_the_account(session: Session) -> None:
    account = identity.ensure_account(session, issuer=ISSUER, subject=unique())
    assert identity.disable_account(session, account.id) is True
    after = identity.get_account(session, account.id)
    assert after is not None
    assert after.disabled_at is not None
    assert after.disabled_at >= account.created_at
    assert not after.is_active
    assert (after.issuer, after.subject, after.id) == (account.issuer, account.subject, account.id)


def test_disabling_twice_returns_false_and_keeps_the_first_time(session: Session) -> None:
    account = identity.ensure_account(session, issuer=ISSUER, subject=unique())
    assert identity.disable_account(session, account.id) is True
    first = identity.get_account(session, account.id)
    assert identity.disable_account(session, account.id) is False
    second = identity.get_account(session, account.id)
    assert first is not None and second is not None
    assert first.disabled_at == second.disabled_at


def test_disabling_an_unknown_account_is_a_lookup_error(session: Session) -> None:
    with pytest.raises(LookupError):
        identity.disable_account(session, uuid.uuid4())


def test_disabling_one_account_leaves_the_others(session: Session) -> None:
    a = identity.ensure_account(session, issuer=ISSUER, subject=unique())
    b = identity.ensure_account(session, issuer=ISSUER, subject=unique())
    identity.disable_account(session, a.id)
    other = identity.get_account(session, b.id)
    assert other is not None and other.is_active


# --- the table's own rules (migration 0005) ----------------------------------------------------


def test_the_database_refuses_a_second_account_for_one_issuer_and_subject(
    connection: Connection,
) -> None:
    subject = unique()
    insert_account(connection, ISSUER, subject)
    message = rejected(
        connection,
        "INSERT INTO account (id, issuer, subject) VALUES (:id, :i, :s)",
        id=uuid.uuid4(),
        i=ISSUER,
        s=subject,
    )
    assert "uq_account_issuer_subject" in message


def test_the_database_allows_the_same_subject_under_another_issuer(connection: Connection) -> None:
    subject = unique()
    insert_account(connection, ISSUER, subject)
    insert_account(connection, ISSUER + "2", subject)


@pytest.mark.parametrize("column", ["issuer", "subject"])
@pytest.mark.parametrize("value", ["", " ", " x", "x ", "  x  ", "x" * 201])
def test_the_database_refuses_blank_padded_or_long_values(
    connection: Connection, column: str, value: str
) -> None:
    params = {"issuer": ISSUER, "subject": unique()}
    params[column] = value
    message = rejected(
        connection,
        "INSERT INTO account (id, issuer, subject) VALUES (:id, :issuer, :subject)",
        id=uuid.uuid4(),
        **params,
    )
    assert f"ck_account_{column}" in message


@pytest.mark.parametrize("column", ["issuer", "subject"])
def test_the_database_accepts_values_at_the_limit(connection: Connection, column: str) -> None:
    params = {"issuer": ISSUER, "subject": unique()}
    params[column] = "x" * 200
    connection.execute(
        text("INSERT INTO account (id, issuer, subject) VALUES (:id, :issuer, :subject)"),
        {"id": uuid.uuid4(), **params},
    )


@pytest.mark.parametrize("column", ["id", "issuer", "subject", "created_at"])
def test_the_required_columns_are_not_null(connection: Connection, column: str) -> None:
    params: dict[str, object] = {"id": uuid.uuid4(), "issuer": ISSUER, "subject": unique()}
    if column == "created_at":
        sql = (
            "INSERT INTO account (id, issuer, subject, created_at) "
            "VALUES (:id, :issuer, :subject, NULL)"
        )
    else:
        sql = "INSERT INTO account (id, issuer, subject) VALUES (:id, :issuer, :subject)"
        params[column] = None
    rejected(connection, sql, **params)


def test_an_account_row_can_be_erased(connection: Connection) -> None:
    """Account erasure on request (docs/SECURITY.md 5.4) needs the row to be deletable."""
    subject = unique()
    insert_account(connection, ISSUER, subject)
    connection.execute(text("DELETE FROM account WHERE subject = :s"), {"s": subject})
    assert count(connection, ISSUER, subject) == 0


def test_the_account_table_holds_no_personal_columns(connection: Connection) -> None:
    columns = {
        row[0]
        for row in connection.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'account'")
        )
    }
    assert columns == {"id", "issuer", "subject", "created_at", "disabled_at"}
