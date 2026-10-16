"""The English-only content rule (docs/slices/M1G-EN-INGILIZCE.md section 4).

A pure walk over a question document. It is applied when content is written, never when it is
read, so rows stored before the rule keep loading.
"""

from __future__ import annotations

from typing import Any

from qlab.content.schema.question import QuestionDocument

# Letters that occur in Turkish and not in English text. `ç ö ü` are left out on purpose: they
# appear in English physics text in proper names (Schrödinger).
NON_ENGLISH_LETTERS = frozenset("ğĞıİşŞ")


def _walk(value: Any, path: str, found: list[str]) -> None:
    if isinstance(value, str):
        if any(character in NON_ENGLISH_LETTERS for character in value):
            found.append(path)
    elif isinstance(value, dict):
        for key, item in value.items():
            _walk(item, f"{path}.{key}" if path else str(key), found)
    elif isinstance(value, list | tuple):
        for index, item in enumerate(value):
            _walk(item, f"{path}[{index}]", found)


def non_english_paths(document: QuestionDocument) -> list[str]:
    """Paths (like `mcq.options[1].rationale`) of every string holding a Turkish-only letter."""
    found: list[str] = []
    _walk(document.model_dump(mode="json"), "", found)
    return found


def non_english_message(paths: list[str]) -> str:
    shown = ", ".join(paths[:3]) + (", ..." if len(paths) > 3 else "")
    return f"Content must be written in English; found non-English letters at {shown}"
