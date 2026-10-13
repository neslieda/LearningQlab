"""`qlab.audit.service.is_valid_actor`: the form the audit log accepts for an actor.

Written from its docstring only: an opaque account identifier or "system:<process>", made of
letters, digits and `_ . : | -`; no spaces and no e-mail address. No database is needed.
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from qlab.audit.service import is_valid_actor

ALLOWED = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.:|-"


@pytest.mark.parametrize(
    "actor",
    [
        "u_author",
        "u_editor",
        "system:pilot_import",
        "system:test",
        "acct-123",
        "A",
        "0",
        "a.b|c:d-e_f",
        "U_0f3a9c2e",
        "x" * 200,
    ],
)
def test_account_identifiers_and_system_processes_are_valid(actor: str) -> None:
    assert is_valid_actor(actor) is True


@pytest.mark.parametrize(
    "actor",
    [
        "",
        " ",
        "Jane Doe",
        "a@b.c",
        "jane@example.org",
        " u_author",
        "u_author ",
        "u author",
        "u_author\n",
        "\nu_author",
        "u\tauthor",
        "u/author",
        "u,author",
        "u;author",
        "u(author)",
        "ünal",
        "u_аuthor",  # a Cyrillic letter
        "u_author​",  # a zero-width space
        "\U0001f600",
        "x" * 201,
    ],
)
def test_names_addresses_and_odd_characters_are_not_valid(actor: str) -> None:
    assert is_valid_actor(actor) is False


@given(actor=st.text(alphabet=ALLOWED, min_size=1, max_size=200))
def test_any_string_of_allowed_characters_is_valid(actor: str) -> None:
    assert is_valid_actor(actor) is True


@given(
    prefix=st.text(alphabet=ALLOWED, max_size=20),
    odd=st.characters(blacklist_characters=ALLOWED),
    suffix=st.text(alphabet=ALLOWED, max_size=20),
)
def test_one_character_outside_the_allowed_set_makes_it_invalid(
    prefix: str, odd: str, suffix: str
) -> None:
    assert is_valid_actor(prefix + odd + suffix) is False


@given(actor=st.text(alphabet=ALLOWED, min_size=201, max_size=260))
def test_more_than_200_characters_are_invalid(actor: str) -> None:
    assert is_valid_actor(actor) is False
