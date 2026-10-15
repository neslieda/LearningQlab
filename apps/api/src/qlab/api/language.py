"""A cheap guess whether an answer is not written in English (docs/slices/M1G-5-SOZLESME.md
section 3.4). Pure and deterministic: no network, no model. It only decides whether to show a
hint; it never refuses an answer."""

from __future__ import annotations

import re

_WORD = re.compile(r"[^\W\d_]+")
_STRONG_TURKISH_LETTERS = frozenset("ğışİĞŞ")
_MIN_WORDS = 3
_MIN_TURKISH_HITS = 2

TURKISH_WORDS = frozenset(
    {
        "ve", "bir", "bu", "için", "ile", "gibi", "çok", "daha", "olarak", "olan",
        "değil", "var", "yok", "ama", "veya", "çünkü", "kadar", "sonra", "önce",
        "her", "ise", "de", "da", "ne", "nasıl", "neden", "hızı", "kuvvet", "enerji",
        "olur", "olduğu", "yani", "göre", "bunun", "şu", "ben", "biz",
    }
)  # fmt: skip
ENGLISH_WORDS = frozenset(
    {
        "the", "and", "of", "to", "in", "is", "are", "was", "were", "that", "this",
        "it", "for", "with", "as", "on", "by", "at", "from", "because", "which",
        "since", "so", "therefore", "has", "have", "an", "not", "be", "or", "when",
        "than", "then", "its", "their", "there", "force", "energy",
    }
)  # fmt: skip


def looks_non_english(text: str) -> bool:
    found = [w for w in _WORD.findall(text) if len(w) > 1]
    if len(found) < _MIN_WORDS:
        return False
    # Strong letters are tested on the original word: "İ".lower() is not one character.
    if any(not _STRONG_TURKISH_LETTERS.isdisjoint(w) for w in found):
        return True
    words = {w.lower() for w in found}
    turkish = len(words & TURKISH_WORDS)
    english = len(words & ENGLISH_WORDS)
    return turkish >= _MIN_TURKISH_HITS and turkish > english
