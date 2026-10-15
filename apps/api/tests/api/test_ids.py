"""The prefixed identifier codec (docs/slices/M1G-5-SOZLESME.md section 3.2): a prefix, an
underscore and 26 characters of lower-case Crockford base32. Exactly one text form per UUID."""

from __future__ import annotations

import uuid

import pytest
from hypothesis import given
from hypothesis import strategies as st

import qlab.api.ids as ids

ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"
PREFIXES = [ids.QUESTION, ids.QUESTION_VERSION, ids.ACCOUNT]
SAMPLE = uuid.UUID("01926f3e-8a4b-7c1d-9e2f-3a4b5c6d7e8f")


@given(st.uuids(), st.sampled_from(PREFIXES))
def test_round_trip(value: uuid.UUID, prefix: str) -> None:
    assert ids.decode(prefix, ids.encode(prefix, value)) == value


@given(st.uuids(), st.sampled_from(PREFIXES))
def test_encoded_form_has_the_documented_shape(value: uuid.UUID, prefix: str) -> None:
    text = ids.encode(prefix, value)
    head, separator, body = text.partition("_")
    assert (head, separator) == (prefix, "_")
    assert len(body) == 26
    assert set(body) <= set(ALPHABET)
    assert text == text.lower()


def test_known_values() -> None:
    assert ids.encode("q", uuid.UUID(int=0)) == "q_" + "0" * 26
    assert ids.encode("q", uuid.UUID(int=1)) == "q_" + "0" * 25 + "1"
    # The largest UUID needs the 128 bits: the first character carries only 3 of them.
    assert ids.encode("q", uuid.UUID(int=2**128 - 1)) == "q_7" + "z" * 25


@given(st.uuids(), st.uuids())
def test_text_order_is_uuid_order(a: uuid.UUID, b: uuid.UUID) -> None:
    ta, tb = ids.encode("q", a), ids.encode("q", b)
    assert (a < b) == (ta < tb)
    assert (a == b) == (ta == tb)


def test_time_ordered_uuids_sort_in_creation_order() -> None:
    generated = [uuid.uuid7() for _ in range(50)]
    texts = [ids.encode(ids.QUESTION, value) for value in generated]
    assert texts == sorted(texts)


@given(st.uuids())
def test_prefixes_are_not_interchangeable(value: uuid.UUID) -> None:
    q = ids.encode(ids.QUESTION, value)
    qv = ids.encode(ids.QUESTION_VERSION, value)
    acc = ids.encode(ids.ACCOUNT, value)
    with pytest.raises(ValueError):
        ids.decode(ids.QUESTION_VERSION, q)
    with pytest.raises(ValueError):
        ids.decode(ids.QUESTION, qv)
    with pytest.raises(ValueError):
        ids.decode(ids.QUESTION, acc)
    with pytest.raises(ValueError):
        ids.decode(ids.ACCOUNT, qv)


GOOD_BODY = ids.encode("q", SAMPLE)[2:]


@pytest.mark.parametrize(
    "text",
    [
        "",
        "q",
        "q_",
        "_",
        "_" + GOOD_BODY,
        GOOD_BODY,
        "q" + GOOD_BODY,  # no separator
        "q-" + GOOD_BODY,
        "q__" + GOOD_BODY[:-1],
        "Q_" + GOOD_BODY,  # upper-case prefix
        "q_" + GOOD_BODY[:-1],  # 25 characters
        "q_" + GOOD_BODY + "0",  # 27 characters
        "q_" + GOOD_BODY + " ",
        " q_" + GOOD_BODY,
        "q_" + GOOD_BODY + "\n",
        "q_" + "0" * 52,
        "q_" + GOOD_BODY.upper(),  # one text form only
        "q_" + GOOD_BODY[:-1] + "I",
        "q_" + GOOD_BODY[:-1] + "i",  # not in the alphabet
        "q_" + GOOD_BODY[:-1] + "l",
        "q_" + GOOD_BODY[:-1] + "o",
        "q_" + GOOD_BODY[:-1] + "u",
        "q_" + GOOD_BODY[:-1] + "-",
        "q_" + GOOD_BODY[:-1] + "_",
        "q_" + GOOD_BODY[:-1] + "١",  # an Arabic-indic digit
        "q_" + GOOD_BODY[:-1] + "é",
        "q_" + GOOD_BODY[:-1] + "\x00",
        "q_8" + "0" * 25,  # needs 129 bits
        "q_z" + "z" * 25,
        "q_" + "w" + "0" * 25,
    ],
)
def test_malformed_identifiers_are_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        ids.decode("q", text)


def test_the_first_character_beyond_seven_overflows() -> None:
    for first in "89abcdefghjkmnpqrstvwxyz":
        with pytest.raises(ValueError):
            ids.decode("q", f"q_{first}{'0' * 25}")
    for first in "01234567":
        assert ids.decode("q", f"q_{first}{'0' * 25}").int == int(first) << 125


@given(st.text(max_size=60))
def test_arbitrary_text_is_a_value_error_or_canonical(text: str) -> None:
    try:
        value = ids.decode("q", text)
    except ValueError:
        return
    assert ids.encode("q", value) == text  # exactly one text form decodes to each UUID


@given(st.text(alphabet=ALPHABET + ALPHABET.upper() + "_", min_size=26, max_size=29))
def test_any_accepted_text_is_lower_case_and_canonical(body: str) -> None:
    text = "q_" + body
    try:
        value = ids.decode("q", text)
    except ValueError:
        return
    assert text == ids.encode("q", value)
    assert body == body.lower()


@given(st.uuids())
def test_actor_is_the_account_form(value: uuid.UUID) -> None:
    assert ids.actor(value) == ids.encode(ids.ACCOUNT, value)
    assert ids.actor(value).startswith("acc_")


@pytest.mark.parametrize(
    ("pattern", "prefix"),
    [
        (ids.QUESTION_ID_PATTERN, "q"),
        (ids.QUESTION_VERSION_ID_PATTERN, "qv"),
        (ids.ACCOUNT_ID_PATTERN, "acc"),
    ],
)
@given(value=st.uuids())
def test_schema_patterns_accept_encoded_ids_and_only_those(
    pattern: str, prefix: str, value: uuid.UUID
) -> None:
    import re

    assert re.fullmatch(pattern, ids.encode(prefix, value))
    assert not re.fullmatch(pattern, ids.encode(prefix, value).upper())
    other = next(p for p in PREFIXES if p != prefix)
    assert not re.fullmatch(pattern, ids.encode(other, value))


PATTERNS = [
    (ids.QUESTION_ID_PATTERN, "q"),
    (ids.QUESTION_VERSION_ID_PATTERN, "qv"),
    (ids.ACCOUNT_ID_PATTERN, "acc"),
]


@pytest.mark.parametrize(("pattern", "prefix"), PATTERNS)
@given(body=st.text(alphabet=ALPHABET + "89ABIiLlOoUu-_ \n", min_size=24, max_size=28))
def test_patterns_and_decode_agree(pattern: str, prefix: str, body: str) -> None:
    import re

    text = f"{prefix}_{body}"
    try:
        ids.decode(prefix, text)
        decodes = True
    except ValueError:
        decodes = False
    assert bool(re.fullmatch(pattern, text)) == decodes


@pytest.mark.parametrize(("pattern", "prefix"), PATTERNS)
def test_patterns_reject_a_first_character_above_seven(pattern: str, prefix: str) -> None:
    import re

    for first in "89abcdefghjkmnpqrstvwxyz":
        assert not re.fullmatch(pattern, f"{prefix}_{first}{'0' * 25}")
    for first in "01234567":
        assert re.fullmatch(pattern, f"{prefix}_{first}{'0' * 25}")
