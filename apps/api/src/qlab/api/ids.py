"""Prefixed identifiers. They exist only at the API edge (D-54); the database holds UUIDv7.

`q_01j9z3k4m5n6p7q8r9s0t1v2w3`: a prefix, an underscore and the 128 bits in lower-case
Crockford base32 (26 characters). The text form sorts like the UUID, so like creation time.
"""

from __future__ import annotations

import uuid

QUESTION = "q"
QUESTION_VERSION = "qv"
ACCOUNT = "acc"

_ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"
_VALUES = {character: value for value, character in enumerate(_ALPHABET)}
_LENGTH = 26

QUESTION_ID_PATTERN = rf"^{QUESTION}_[{_ALPHABET}]{{{_LENGTH}}}$"
QUESTION_VERSION_ID_PATTERN = rf"^{QUESTION_VERSION}_[{_ALPHABET}]{{{_LENGTH}}}$"
ACCOUNT_ID_PATTERN = rf"^{ACCOUNT}_[{_ALPHABET}]{{{_LENGTH}}}$"


def encode(prefix: str, value: uuid.UUID) -> str:
    number = value.int
    characters = []
    for _ in range(_LENGTH):
        characters.append(_ALPHABET[number & 31])
        number >>= 5
    return f"{prefix}_{''.join(reversed(characters))}"


def decode(prefix: str, text: str) -> uuid.UUID:
    """The UUID behind a prefixed identifier. ValueError for another prefix, another length, a
    character outside the alphabet, or a value that does not fit in 128 bits. Exactly one text
    form decodes to each UUID."""
    head, separator, body = text.partition("_")
    if head != prefix or not separator or len(body) != _LENGTH:
        raise ValueError("not an identifier of this kind")
    number = 0
    for character in body:
        value = _VALUES.get(character)
        if value is None:
            raise ValueError("not an identifier of this kind")
        number = (number << 5) | value
    if number >> 128:
        raise ValueError("not an identifier of this kind")
    return uuid.UUID(int=number)


def actor(account_id: uuid.UUID) -> str:
    """The opaque form of an account that is written to the audit log."""
    return encode(ACCOUNT, account_id)
