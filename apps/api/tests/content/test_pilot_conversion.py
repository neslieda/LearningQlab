"""Acceptance test for slice 4: the committed `content/pilot/*.json` say what `docs/pilot/*.md` say.

Written from docs/pilot/IMPORT_RULES.md, docs/pilot/AUTHORING_STANDARD.md, the 24 Markdown source
files, the frozen schema and the reference vocabulary only. It does not use, import or read the
converter: both sides are reduced to plain text and compared by code in this module.

How it works
------------
* `SourceQuestion` is this module's own reading of one `## Soru N` block of a Markdown file
  (IMPORT_RULES section 3 for the block layout). Inline markup is read by `scan`, a small state
  machine over `**`, `*`, `<sub>`, `<sup>`, `<br>`, the guillemets and the tick mark.
* The document side is read by `doc_items` / `nodes_of`, straight from the schema objects.
* `fidelity_errors` implements section 6 (visible text, whitespace removed, compared region by
  region and then as one string), plus the checks that section 6 cannot see: bold, optional,
  sub/sup marks and the variable-to-math mapping of section 4.2/4.3.
* `structure_errors`, `rule_filled_errors` and `validity_errors` implement section 3, section 5
  and the validity list of the slice. Every function returns a list of messages; the tests assert
  the list is empty, so a failure names the question and the place.
* The comparison logic itself is proved on an invented question (`SELF_CHECK_MARKDOWN`, built by
  hand into a document): the faithful document gives no error, and every corruption in
  `CORRUPTIONS` gives at least one. Those tests need no JSON files.

Normalisation: the only one used is "remove all whitespace" (IMPORT_RULES section 6). Where the
rules leave a choice open, section 8 of IMPORT_RULES records the reading and this module uses that
one only (a single `expected_*` function per rule).
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import unicodedata
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from functools import cache
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from qlab.content import math as qmath
from qlab.content.pilot.model import PilotFile, PilotQuestion, source_ref
from qlab.content.schema import (
    Doc,
    Figure,
    HardBreak,
    MathBlock,
    MathInline,
    Paragraph,
    Part,
    Quantity,
    QuestionDocument,
    Table,
    Text,
)
from tests.conftest import REPO_ROOT

node = pytest.mark.node

MD_DIR = REPO_ROOT / "docs" / "pilot"
JSON_DIR = REPO_ROOT / "content" / "pilot"
REFERENCE_FILE = REPO_ROOT / "content" / "reference" / "dp-physics-2025-syllabus.json"
REPORT_FILE = JSON_DIR / "CONVERSION_REPORT.md"

FILE_SUFFIX = "-pilot-questions.md"
EXPECTED_FILES = 24
EXPECTED_QUESTIONS = 130
EXPECTED_BY_SECTION = {"paper_1a": 101, "paper_2": 24, "paper_1b": 5}
# IMPORT_RULES 3.2: the text of a figure note is not imported; its stimulus carries this sentence.
FIGURE_NOTE_DESCRIPTION = "Veriden üretilecek grafik; ayrıntı kaynak dosyadaki Şekil notunda."

# --------------------------------------------------------------------------------------------
# Small text helpers
# --------------------------------------------------------------------------------------------


def squash(text: str) -> str:
    """IMPORT_RULES section 6: all whitespace removed, nothing else normalised."""
    return "".join(text.split())


def first_difference(source: str, document: str, context: int = 40) -> str:
    """'' when equal after `squash`; otherwise the first differing position with context."""
    a, b = squash(source), squash(document)
    if a == b:
        return ""
    at = next(
        (k for k, (x, y) in enumerate(zip(a, b, strict=False)) if x != y), min(len(a), len(b))
    )
    lo = max(0, at - context)
    return (
        f"first difference at position {at} of {len(a)}/{len(b)}: "
        f"source ...{a[lo : at + context]!r}... / document ...{b[lo : at + context]!r}..."
    )


# --------------------------------------------------------------------------------------------
# Greek letters and the inverse of IMPORT_RULES section 4.3
# --------------------------------------------------------------------------------------------

_LOWER_NAMES = (
    "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi pi rho sigma tau "
    "upsilon phi chi psi omega"
)
_UPPER_NAMES = "Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega"
_GREEK_NAMES: dict[str, str] = {
    **dict(zip("αβγδεζηθικλμνξπρστυφχψω", _LOWER_NAMES.split(), strict=True)),
    **dict(zip("ΓΔΘΛΞΠΣΥΦΨΩ", _UPPER_NAMES.split(), strict=True)),
}
# Section 8: where a letter has two commands, the one named after its Unicode letter name is used
# (epsilon, phi, theta); \varepsilon and friends are not accepted.
_COMMAND_TO_CHAR: dict[str, str] = {name: ch for ch, name in _GREEK_NAMES.items()}


def is_latin_or_greek_letter(ch: str) -> bool:
    if not ch.isalpha():
        return False
    name = unicodedata.name(ch, "")
    return name.startswith(("LATIN", "GREEK"))


def tex_of(text: str) -> str:
    """Section 4.3 forward: Latin as is, Greek as a command, a space between command and letter."""
    out: list[str] = []
    after_command = False
    for ch in text:
        name = _GREEK_NAMES.get(ch)
        if name is not None:
            out.append("\\" + name)
            after_command = True
        else:
            if after_command and ch.isalpha():
                out.append(" ")
            out.append(ch)
            after_command = False
    return "".join(out)


def latex_to_plain(latex: str) -> str:
    """Section 6, document side: command -> Greek letter; `_`, `^`, `{`, `}` dropped.

    A command that is not a Greek letter stays visible (as `\\name`) so that it cannot match.
    """
    replaced = re.sub(
        r"\\([A-Za-z]+)",
        lambda m: _COMMAND_TO_CHAR.get(m.group(1), m.group(0)),
        latex,
    )
    return re.sub(r"[_^{}]", "", replaced)


# --------------------------------------------------------------------------------------------
# Source side: inline markup
# --------------------------------------------------------------------------------------------


class SourceError(Exception):
    """The Markdown does not have the shape this test's reading of the rules expects."""


@dataclass(frozen=True)
class Seg:
    text: str
    bold: bool = False
    italic: bool = False
    italic_run: int = 0
    sub: bool = False
    sup: bool = False
    optional: bool = False


_TOKEN = re.compile(r"\*\*|\*|<sub>|</sub>|<sup>|</sup>|<br>|«|»|✓")


def scan(raw: str, *, keep_ticks: bool = False) -> list[Seg]:
    """Split inline Markdown into runs with their marks. `<br>` becomes a space.

    The tick mark vanishes, except in a markscheme note (`keep_ticks`; IMPORT_RULES section 8).
    """
    segs: list[Seg] = []
    bold = italic = sub = sup = optional = False
    run = 0
    pos = 0

    def emit(text: str) -> None:
        if text:
            segs.append(
                Seg(text, bold, italic, run if italic else 0, sub, sup, optional),
            )

    for m in _TOKEN.finditer(raw):
        emit(raw[pos : m.start()])
        pos = m.end()
        piece = m.group()
        if piece == "**":
            bold = not bold
        elif piece == "*":
            italic = not italic
            if italic:
                run += 1
        elif piece == "<sub>":
            sub = True
        elif piece == "</sub>":
            sub = False
        elif piece == "<sup>":
            sup = True
        elif piece == "</sup>":
            sup = False
        elif piece == "«":
            optional = True
        elif piece == "»":
            optional = False
        elif piece == "<br>":
            segs.append(Seg(" "))
        elif piece == "✓" and keep_ticks:
            emit("✓")
    emit(raw[pos:])
    if bold or italic or sub or sup or optional:
        raise SourceError(f"unbalanced inline markup in: {raw[:80]!r}")
    return segs


def plain_of(raw: str, *, keep_ticks: bool = False) -> str:
    return "".join(s.text for s in scan(raw, keep_ticks=keep_ticks))


# --------------------------------------------------------------------------------------------
# Source side: block layout
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Element:
    kind: str  # "para" | "table" | "quote" | "h3"
    lines: tuple[str, ...]


def elements_of(lines: Sequence[str]) -> list[Element]:
    out: list[Element] = []
    cur: list[str] = []
    kind = ""

    def flush() -> None:
        nonlocal cur, kind
        if cur:
            out.append(Element(kind, tuple(cur)))
        cur, kind = [], ""

    for line in lines:
        if not line.strip():
            flush()
            continue
        if line.startswith("### "):
            flush()
            out.append(Element("h3", (line,)))
            continue
        k = "table" if line.startswith("|") else "quote" if line.startswith(">") else "para"
        if kind and k != kind:
            flush()
        kind = k
        cur.append(line)
    flush()
    return out


@dataclass(frozen=True)
class SItem:
    """A block of a stem or lead-in: paragraph, table or figure block."""

    kind: str  # "paragraph" | "table" | "figure"
    raw: str = ""
    rows: tuple[tuple[str, ...], ...] = ()
    fig: int = 0  # 1-based figure number for kind == "figure"


@dataclass(frozen=True)
class SPoint:
    raw: str  # without the tick
    route: str | None


@dataclass
class SPart:
    id: str
    label: str
    marks: int
    body_raw: str
    lead_in: list[SItem]
    # the Answers cell as parsed lines: ("alt", "alt1") | ("point", raw) | ("loose", raw)
    answer_lines: list[tuple[str, str]] = field(default_factory=list)
    notes_raw: list[str] = field(default_factory=list)  # as written, one per <br> line
    total_col: int = 0
    total_says_max: bool = False

    @property
    def points(self) -> list[SPoint]:
        route: str | None = None
        out: list[SPoint] = []
        for kind, value in self.answer_lines:
            if kind == "alt":
                route = value
            elif kind == "point":
                out.append(SPoint(value, route))
        return out

    @property
    def has_loose_lines(self) -> bool:
        return any(kind == "loose" for kind, _ in self.answer_lines)

    @property
    def tick_lines(self) -> int:
        return len(self.points)

    @property
    def awardable(self) -> int:
        """Shared points plus the largest route (routes counted once)."""
        shared = sum(1 for p in self.points if p.route is None)
        routes = Counter(p.route for p in self.points if p.route is not None)
        return shared + max(routes.values(), default=0)


@dataclass
class SourceQuestion:
    stem: str  # file stem, e.g. "a1-kinematics"
    number: int
    paper: str  # "1A" | "1B" | "2"
    heading_hl: bool
    heading_marks: int | None
    stem_items: list[SItem] = field(default_factory=list)
    # multiple choice
    options: dict[str, str] = field(default_factory=dict)
    correct: str = ""
    explanation: list[str] = field(default_factory=list)
    rationales: dict[str, str] = field(default_factory=dict)
    # structured
    parts: list[SPart] = field(default_factory=list)
    has_formula_chain: bool = False
    figure_note: str | None = None
    free_paragraphs: list[str] = field(default_factory=list)
    # `> **Şekil:**` block texts in document order (stem, lead-ins); the figure note is apart
    figures: list[str] = field(default_factory=list)
    row: dict[str, str] = field(default_factory=dict)

    @property
    def ref(self) -> str:
        return source_ref(self.stem, self.number)

    @property
    def stimulus_count(self) -> int:
        """One per figure block and one for the figure note, in that order (section 3.3)."""
        return len(self.figures) + (self.figure_note is not None)

    @property
    def is_mcq(self) -> bool:
        return self.paper == "1A"

    @property
    def level_hl(self) -> bool:
        return self.heading_hl or self.row.get("Düzey") == "HL"

    @property
    def total_marks(self) -> int:
        return 1 if self.is_mcq else sum(p.marks for p in self.parts)

    @property
    def primary_node(self) -> str:
        head = self.stem.split("-")[0]
        return f"{head[0].upper()}.{head[1:]}"


_HEADING = re.compile(r"^## Soru (\d+) — Paper (1A|1B|2)(?: \(([^)]*)\))?\s*$")
_PART = re.compile(r"^\s*\*\*\(([a-z])\)\*\*\s*(.*)$")
_ROMAN_PART = re.compile(r"^\s*\(([ivx]+)\)\s+(.*)$")
_ROMAN_AFTER_LETTER = re.compile(r"^\(([ivx]+)\)\s*(.*)$")
_MARKS_AT_END = re.compile(r"\[(\d+)\]\s*$")
_ALT_LINE = re.compile(r"^\*\*ALTERNATIVE (\d+)\*\*$")


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_separator(cells: Sequence[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", c) for c in cells)


def _table_rows(el: Element) -> tuple[tuple[str, ...], ...]:
    rows = [split_row(line) for line in el.lines]
    return tuple(tuple(r) for r in rows if not _is_separator(r))


def _quote_text(el: Element) -> str:
    return " ".join(line.lstrip(">").strip() for line in el.lines)


_FIGURE_LABEL = "**Şekil:**"


def _item(el: Element, q: SourceQuestion, where: str) -> SItem:
    if el.kind == "para":
        return SItem("paragraph", raw=" ".join(line.strip() for line in el.lines))
    if el.kind == "table":
        return SItem("table", rows=_table_rows(el))
    if el.kind == "quote":
        text = _quote_text(el)
        if not text.startswith(_FIGURE_LABEL):
            raise SourceError(f"{q.ref}: quote block without the figure label in {where}")
        q.figures.append(text.removeprefix(_FIGURE_LABEL).strip())
        return SItem("figure", raw=q.figures[-1], fig=len(q.figures))
    raise SourceError(f"{q.ref}: unexpected {el.kind} element in {where}")


def _parse_mcq(q: SourceQuestion, els: list[Element]) -> None:
    it = iter(els)
    el = next(it, None)
    while el is not None and not (el.kind == "para" and re.match(r"^A\. ", el.lines[0])):
        q.stem_items.append(_item(el, q, "stem"))
        el = next(it, None)
    if el is None:
        raise SourceError(f"{q.ref}: no options")
    keys = []
    for line in el.lines:
        m = re.match(r"^([A-D])\. (.*)$", line)
        if m is None:
            raise SourceError(f"{q.ref}: option line does not match: {line[:60]!r}")
        keys.append(m.group(1))
        q.options[m.group(1)] = m.group(2).strip()
    if keys != ["A", "B", "C", "D"]:
        raise SourceError(f"{q.ref}: options are {keys}")
    el = next(it, None)
    m = re.fullmatch(r"\*\*Cevap: ([A-D])\*\*", el.lines[0].strip()) if el else None
    if el is None or m is None or len(el.lines) != 1:
        raise SourceError(f"{q.ref}: no answer line after the options")
    q.correct = m.group(1)
    el = next(it, None)
    while el is not None and el.kind == "para":
        text = " ".join(line.strip() for line in el.lines)
        if not q.explanation:
            if not text.startswith("**Çözüm.**"):
                raise SourceError(f"{q.ref}: explanation does not start with the label")
            text = text.removeprefix("**Çözüm.**").strip()
        q.explanation.append(text)
        el = next(it, None)
    if not q.explanation:
        raise SourceError(f"{q.ref}: no explanation")
    if el is None or el.kind != "table":
        raise SourceError(f"{q.ref}: no misconception table")
    rows = _table_rows(el)
    if rows[0] != ("Seçenek", "Dayandığı yanılgı"):
        raise SourceError(f"{q.ref}: misconception table header is {rows[0]}")
    for row in rows[1:]:
        if len(row) != 2:
            raise SourceError(f"{q.ref}: misconception row has {len(row)} cells")
        q.rationales[row[0]] = row[1]
    # Paragraphs after the table are free commentary (IMPORT_RULES is silent for multiple choice;
    # section 3.2 excludes them after a markscheme). They are kept apart and never compared.
    for rest in it:
        if rest.kind != "para":
            raise SourceError(f"{q.ref}: unexpected {rest.kind} element after the table")
        q.free_paragraphs.append(" ".join(line.strip() for line in rest.lines))


def _parse_structured(q: SourceQuestion, els: list[Element]) -> None:
    main: list[Element] = []
    sections: dict[str, list[Element]] = {}
    current: str | None = None
    for el in els:
        if el.kind == "h3":
            current = el.lines[0][4:].strip()
            if current in sections:
                raise SourceError(f"{q.ref}: section {current!r} twice")
            sections[current] = []
        elif current is None:
            main.append(el)
        else:
            sections[current].append(el)

    pending: list[SItem] = []
    previous_split_letter = False
    for el in main:
        first = el.lines[0] if el.kind == "para" else ""
        letter_match = _PART.match(first)
        roman_match = _ROMAN_PART.match(first)
        if letter_match is None and not (roman_match and previous_split_letter):
            pending.append(_item(el, q, "stem or lead-in"))
            continue
        text = " ".join(line.strip() for line in el.lines)
        if letter_match is not None:
            letter = letter_match.group(1)
            rest = re.sub(r"^\*\*\([a-z]\)\*\*\s*", "", text)
            sub = _ROMAN_AFTER_LETTER.match(rest)
            if sub is not None:
                label = f"{letter}.{sub.group(1)}"
                rest = sub.group(2)
                previous_split_letter = True
            else:
                label = letter
                previous_split_letter = False
        else:
            assert roman_match is not None
            letter = q.parts[-1].label.split(".")[0]
            label = f"{letter}.{roman_match.group(1)}"
            rest = re.sub(r"^\s*\([ivx]+\)\s+", "", text)
        marks_match = _MARKS_AT_END.search(rest)
        if marks_match is None:
            raise SourceError(f"{q.ref}: part {label} has no [n] mark at its end")
        body = rest[: marks_match.start()].strip()
        part = SPart(label, label, int(marks_match.group(1)), body, lead_in=pending)
        pending = []
        if not q.parts:
            q.stem_items = part.lead_in
            part.lead_in = []
        q.parts.append(part)
    if not q.parts:
        raise SourceError(f"{q.ref}: no parts")
    if pending:
        raise SourceError(f"{q.ref}: content between the last part and the first section")

    q.has_formula_chain = any(name.startswith("Formül zinciri") for name in sections)
    figure_note = [name for name in sections if name.startswith("Şekil notu")]
    if len(figure_note) > 1:
        raise SourceError(f"{q.ref}: several figure notes")
    markscheme = [name for name in sections if name == "Markscheme"]
    if len(markscheme) != 1:
        raise SourceError(f"{q.ref}: expected exactly one Markscheme section")
    tables = [el for el in sections["Markscheme"] if el.kind == "table"]
    if not tables:
        raise SourceError(f"{q.ref}: no markscheme table")
    rows = _table_rows(tables[0])
    if rows[0] != ("Question", "", "", "Answers", "Notes", "Total"):
        raise SourceError(f"{q.ref}: markscheme header is {rows[0]}")
    body_rows = rows[1:]
    if len(body_rows) != len(q.parts):
        raise SourceError(f"{q.ref}: {len(body_rows)} markscheme rows for {len(q.parts)} parts")
    for part, row in zip(q.parts, body_rows, strict=True):
        if len(row) != 6:
            raise SourceError(f"{q.ref}: markscheme row of {part.label} has {len(row)} cells")
        number, letter, roman, answers, notes, total = row
        row_label = f"{letter}.{roman}" if roman else letter
        if number != f"{q.number}." or row_label != part.label:
            raise SourceError(f"{q.ref}: markscheme row {number} {row_label} for part {part.label}")
        for line in (x.strip() for x in answers.split("<br>")):
            if not line:
                continue
            alt = _ALT_LINE.match(line)
            if alt:
                part.answer_lines.append(("alt", f"alt{alt.group(1)}"))
            elif line.endswith("✓"):
                part.answer_lines.append(("point", line.removesuffix("✓").rstrip()))
            else:
                part.answer_lines.append(("loose", line))
        part.notes_raw = [x.strip() for x in notes.split("<br>") if x.strip()]
        total_match = re.fullmatch(r"(\d+)( max)?", total)
        if total_match is None:
            raise SourceError(f"{q.ref}: Total column of {part.label} is {total!r}")
        part.total_col = int(total_match.group(1))
        part.total_says_max = total_match.group(2) is not None

    if figure_note:
        els_note = sections[figure_note[0]]
        text = " ".join(" ".join(x.strip() for x in el.lines) for el in els_note)
        q.figure_note = text


def _parse_kapsam(text: str, stem: str) -> dict[int, dict[str, str]]:
    lines = text.split("\n")
    try:
        start = lines.index("## Kapsam tablosu")
    except ValueError:
        raise SourceError(f"{stem}: no scope table") from None
    i = start + 1
    while not lines[i].startswith("|"):
        i += 1
    header = split_row(lines[i])
    rows: dict[int, dict[str, str]] = {}
    for line in lines[i + 2 :]:
        if not line.startswith("|"):
            break
        cells = split_row(line)
        if len(cells) != len(header):
            raise SourceError(f"{stem}: scope row has {len(cells)} cells")
        # the outcome column is headed "Kazanım (A.1)": keep the key without the node
        keys = [re.sub(r" \(.*\)$", "", h) for h in header]
        rows[int(cells[0])] = dict(zip(keys, cells, strict=True))
    return rows


@dataclass
class SourceFile:
    stem: str
    sha256: str
    numbers: list[int]  # every `## Soru N` heading, in order, found by a plain regex
    questions: list[SourceQuestion]


def parse_source_text(text: str, stem: str, digest: str = "") -> SourceFile:
    kapsam = _parse_kapsam(text, stem)
    numbers = [int(n) for n in re.findall(r"^## Soru (\d+)\b", text, flags=re.M)]
    blocks: list[tuple[re.Match[str], list[str]]] = []
    current: tuple[re.Match[str], list[str]] | None = None
    after_rule = False
    for line in text.split("\n"):
        if after_rule and line.strip() and not line.startswith("## "):
            raise SourceError(
                f"{stem}: text between a closing --- and the next heading: {line[:60]!r}"
            )
        if line.startswith("## "):
            after_rule = False
        if line.strip() == "---":
            after_rule = current is not None
        if line.startswith("## ") or line.strip() == "---":
            current = None
        m = _HEADING.match(line)
        if m is not None:
            current = (m, [])
            blocks.append(current)
            continue
        if line.startswith("## Soru"):
            raise SourceError(f"{stem}: heading not understood: {line!r}")
        if current is not None:
            current[1].append(line)
    questions: list[SourceQuestion] = []
    for m, body in blocks:
        extra = [t.strip() for t in (m.group(3) or "").split(",") if t.strip()]
        marks: int | None = None
        for token in extra:
            marks_token = re.fullmatch(r"(\d+) puan", token)
            if marks_token is not None:
                marks = int(marks_token.group(1))
        q = SourceQuestion(stem, int(m.group(1)), m.group(2), "HL" in extra, marks)
        q.row = kapsam.get(q.number, {})
        if not q.row:
            raise SourceError(f"{q.ref}: no row in the scope table")
        els = elements_of(body)
        if q.is_mcq:
            _parse_mcq(q, els)
        else:
            _parse_structured(q, els)
        questions.append(q)
    return SourceFile(stem, digest, numbers, questions)


@cache
def source_files() -> tuple[SourceFile, ...]:
    out: list[SourceFile] = []
    for path in sorted(MD_DIR.glob("*" + FILE_SUFFIX)):
        data = path.read_bytes()
        stem = path.name.removesuffix(FILE_SUFFIX)
        out.append(parse_source_text(data.decode("utf-8"), stem, hashlib.sha256(data).hexdigest()))
    return tuple(out)


def all_source_questions() -> list[SourceQuestion]:
    return [q for f in source_files() for q in f.questions]


# --------------------------------------------------------------------------------------------
# Document side
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class DNode:
    kind: str  # "text" | "math" | "break" | "quantity"
    text: str  # visible text; for math the section 6 inverse of the LaTeX
    marks: frozenset[str]
    latex: str = ""


@dataclass(frozen=True)
class DCell:
    kind: str  # "table_header" | "table_cell"
    paragraphs: int
    nodes: tuple[DNode, ...]


@dataclass(frozen=True)
class DItem:
    kind: str  # "paragraph" | "table" | "figure" | the schema type of anything else
    nodes: tuple[DNode, ...] = ()
    rows: tuple[tuple[DCell, ...], ...] = ()
    stimulus_id: str = ""


def nodes_of(paragraph: Paragraph) -> tuple[DNode, ...]:
    out: list[DNode] = []
    for inline in paragraph.content:
        if isinstance(inline, Text):
            out.append(DNode("text", inline.text, frozenset(m.type.value for m in inline.marks)))
        elif isinstance(inline, MathInline):
            latex = inline.attrs.latex
            out.append(
                DNode(
                    "math",
                    latex_to_plain(latex),
                    frozenset(m.type.value for m in inline.marks),
                    latex,
                )
            )
        elif isinstance(inline, HardBreak):
            out.append(DNode("break", " ", frozenset()))
        elif isinstance(inline, Quantity):
            out.append(
                DNode("quantity", inline.attrs.value, frozenset(m.type.value for m in inline.marks))
            )
    return tuple(out)


def doc_items(doc: Doc) -> list[DItem]:
    items: list[DItem] = []
    for block in doc.content:
        if isinstance(block, Paragraph):
            items.append(DItem("paragraph", nodes=nodes_of(block)))
        elif isinstance(block, Table):
            rows = tuple(
                tuple(
                    DCell(
                        cell.type,
                        len(cell.content),
                        tuple(n for p in cell.content for n in nodes_of(p)),
                    )
                    for cell in row.content
                )
                for row in block.content
            )
            items.append(DItem("table", rows=rows))
        elif isinstance(block, Figure):
            items.append(DItem("figure", stimulus_id=block.attrs.stimulus_id))
        else:
            items.append(DItem(block.type))
    return items


def item_text(item: DItem) -> str:
    if item.kind == "table":
        return "".join(n.text for row in item.rows for cell in row for n in cell.nodes)
    return "".join(n.text for n in item.nodes)


def doc_text(doc: Doc) -> str:
    return "".join(item_text(i) for i in doc_items(doc))


# --------------------------------------------------------------------------------------------
# Comparison of one inline region
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Run:
    text: str
    first: int  # index of the first seg of the run in the scan result
    scripts: tuple[int, ...]  # indices of the segs of an immediately following <sub>/<sup>
    script_kind: str  # "sub" | "sup" | ""
    script_text: str


def italic_runs(segs: Sequence[Seg]) -> list[Run]:
    runs: list[Run] = []
    index = 0
    while index < len(segs):
        seg = segs[index]
        if not seg.italic:
            index += 1
            continue
        end = index
        while end + 1 < len(segs) and segs[end + 1].italic_run == seg.italic_run:
            end += 1
        text = "".join(s.text for s in segs[index : end + 1])
        script_idx: list[int] = []
        kind = ""
        nxt = end + 1
        if nxt < len(segs) and (segs[nxt].sub or segs[nxt].sup):
            kind = "sub" if segs[nxt].sub else "sup"
            while nxt < len(segs) and getattr(segs[nxt], kind):
                script_idx.append(nxt)
                nxt += 1
        out_text = "".join(segs[i].text for i in script_idx)
        runs.append(Run(text, index, tuple(script_idx), kind, out_text))
        index = end + 1
    return runs


def classify_run(text: str) -> str:
    """Section 4.2 as far as it is decidable without the converter's two lists.

    "A": certainly a variable (rule 1, rule 2); "B": possibly a variable (rule 3, a closed list of
    lowercase sequences this test cannot see); "C": certainly italic text.
    """
    if not text or not all(is_latin_or_greek_letter(c) for c in text):
        return "C"
    if len(text) == 1:
        return "A"
    greek = any(c in _GREEK_NAMES for c in text)
    if len(text) <= 4 and (greek or any(c.isupper() for c in text)):
        return "A"
    if text.isascii() and text.islower():
        return "B"
    return "C"


def expected_latex(run: Run) -> str:
    out = tex_of(run.text)
    if run.script_kind == "sub":
        out += "_{" + tex_of(run.script_text) + "}"
    elif run.script_kind == "sup":
        out += "^{" + tex_of(run.script_text) + "}"
    return out


def _joined(nodes: Sequence[DNode], mark: str) -> str:
    return "".join(n.text for n in nodes if mark in n.marks)


def diff_inline(
    label: str,
    raw: str,
    nodes: Sequence[DNode],
    *,
    check_italic: bool = True,
    keep_ticks: bool = False,
    drop_italic: bool = False,
) -> list[str]:
    """Visible text (section 6) and the marks that carry meaning, for one paragraph-sized region.

    In a markscheme note (`keep_ticks`, `drop_italic`; section 8) italic words lose their mark and
    the tick stays; a variable is still a math node.
    """
    segs = scan(raw, keep_ticks=keep_ticks)
    problem = first_difference("".join(s.text for s in segs), "".join(n.text for n in nodes))
    if problem:
        return [f"{label}: text differs: {problem}"]
    errors: list[str] = []
    if any(n.kind == "quantity" for n in nodes):
        errors.append(f"{label}: a quantity node (numbers and units are not structured)")
    breaks = sum(1 for n in nodes if n.kind == "break")
    if breaks != raw.count("<br>"):
        errors.append(f"{label}: {breaks} hard_break nodes for {raw.count('<br>')} <br> in source")

    math_nodes = [n for n in nodes if n.kind == "math"]
    cursor = 0
    absorbed: set[int] = set()
    kept_italic: list[str] = []
    for run in italic_runs(segs):
        kind = classify_run(run.text)
        wanted = expected_latex(run)
        found = math_nodes[cursor].latex if cursor < len(math_nodes) else None
        if kind in ("A", "B") and found == wanted:
            cursor += 1
            absorbed.update(run.scripts)
            continue
        if kind == "A":
            errors.append(
                f"{label}: variable *{run.text}* must be a math_inline with LaTeX {wanted!r}; "
                f"the next math node is {found!r}"
            )
        kept_italic.append(run.text)
    if cursor != len(math_nodes):
        extra = [n.latex for n in math_nodes[cursor:]]
        errors.append(
            f"{label}: math nodes with no italic variable behind them in the source: {extra}"
        )

    def check(name: str, source: str, document: str) -> None:
        difference = first_difference(source, document)
        if difference:
            errors.append(f"{label}: {name} text differs: {difference}")

    check("bold", "".join(s.text for s in segs if s.bold), _joined(nodes, "bold"))
    check("optional («…»)", "".join(s.text for s in segs if s.optional), _joined(nodes, "optional"))
    check(
        "sub",
        "".join(s.text for i, s in enumerate(segs) if s.sub and i not in absorbed),
        _joined(nodes, "sub"),
    )
    check(
        "sup",
        "".join(s.text for i, s in enumerate(segs) if s.sup and i not in absorbed),
        _joined(nodes, "sup"),
    )
    if check_italic:
        check("italic", "" if drop_italic else "".join(kept_italic), _joined(nodes, "italic"))
    return errors


def diff_items(
    label: str, source: Sequence[SItem], document: Sequence[DItem], *, check_italic: bool = True
) -> list[str]:
    """A stem, a lead-in or another multi-block region: same block kinds in the same order."""
    kinds_s = [i.kind for i in source]
    kinds_d = [i.kind for i in document]
    if kinds_s != kinds_d:
        return [f"{label}: blocks are {kinds_d}, the source has {kinds_s}"]
    errors: list[str] = []
    for n, (s, d) in enumerate(zip(source, document, strict=True), start=1):
        where = f"{label} block {n}"
        if s.kind == "paragraph":
            errors += diff_inline(where, s.raw, d.nodes, check_italic=check_italic)
        elif s.kind == "figure":
            if d.stimulus_id != f"fig{s.fig}":
                errors.append(f"{where}: figure node refers to {d.stimulus_id!r}, want fig{s.fig}")
        else:
            if len(s.rows) != len(d.rows) or any(
                len(a) != len(b) for a, b in zip(s.rows, d.rows, strict=False)
            ):
                errors.append(f"{where}: table shape differs from the source")
                continue
            for r, (srow, drow) in enumerate(zip(s.rows, d.rows, strict=True)):
                for c, (sraw, dcell) in enumerate(zip(srow, drow, strict=True)):
                    want_kind = "table_header" if r == 0 else "table_cell"
                    cell = f"{where} row {r + 1} column {c + 1}"
                    if dcell.kind != want_kind:
                        errors.append(f"{cell}: is {dcell.kind}, want {want_kind}")
                    if dcell.paragraphs != 1:
                        errors.append(f"{cell}: {dcell.paragraphs} paragraphs, want 1")
                    errors += diff_inline(cell, sraw, dcell.nodes, check_italic=check_italic)
    return errors


def one_paragraph(
    label: str,
    raw: str,
    doc: Doc,
    *,
    check_italic: bool = True,
    keep_ticks: bool = False,
    drop_italic: bool = False,
) -> list[str]:
    if keep_ticks:
        nodes = doc_items_nodes(doc)
        if len(doc.content) != 1 or not isinstance(doc.content[0], Paragraph):
            return [f"{label}: blocks are not a single paragraph"]
        return diff_inline(
            label,
            raw,
            nodes,
            check_italic=check_italic,
            keep_ticks=True,
            drop_italic=drop_italic,
        )
    return diff_items(
        label, [SItem("paragraph", raw=raw)], doc_items(doc), check_italic=check_italic
    )


# --------------------------------------------------------------------------------------------
# Whole-question text (IMPORT_RULES section 6, in the order given there)
# --------------------------------------------------------------------------------------------


def _items_plain(items: Sequence[SItem]) -> str:
    out: list[str] = []
    for item in items:
        if item.kind == "paragraph":
            out.append(plain_of(item.raw))
        elif item.kind == "table":
            out.extend(plain_of(cell) for row in item.rows for cell in row)
    return " ".join(out)


def source_text(src: SourceQuestion) -> str:
    parts: list[str] = [_items_plain(src.stem_items)]
    if src.is_mcq:
        parts += [plain_of(src.options[k]) for k in "ABCD"]
        parts += [plain_of(p) for p in src.explanation]
        parts += [plain_of(src.rationales[k]) for k in "ABCD" if k in src.rationales]
    for part in src.parts:
        parts.append(_items_plain(part.lead_in))
        parts.append(plain_of(part.body_raw))
        parts += [plain_of(raw) for kind, raw in part.answer_lines if kind != "alt"]
        parts += [plain_of(n, keep_ticks=True) for n in part.notes_raw]
    parts += [plain_of(f) for f in src.figures]
    if src.figure_note is not None:
        parts.append(FIGURE_NOTE_DESCRIPTION)  # the note's own text is not imported
    return " ".join(parts)


def document_text(doc: QuestionDocument) -> str:
    parts: list[str] = [doc_text(doc.stem)]
    if doc.mcq is not None:
        parts += [doc_text(c) for o in doc.mcq.options for c in o.cells]
        if doc.mcq.explanation is not None:
            parts.append(doc_text(doc.mcq.explanation))
        parts += [doc_text(o.rationale) for o in doc.mcq.options if o.rationale is not None]
    for part in doc.parts:
        if part.lead_in is not None:
            parts.append(doc_text(part.lead_in))
        parts.append(doc_text(part.body))
        parts += [doc_text(p.content) for p in part.mark_points]
        parts += [doc_text(n.content) for n in part.notes]
    parts += [s.description for s in doc.stimuli]
    return " ".join(parts)


# --------------------------------------------------------------------------------------------
# Check 2: text fidelity, region by region and as a whole
# --------------------------------------------------------------------------------------------


def fidelity_errors(src: SourceQuestion, doc: QuestionDocument) -> list[str]:
    errors = diff_items("stem", src.stem_items, doc_items(doc.stem))
    if src.is_mcq:
        errors += _mcq_fidelity(src, doc)
    else:
        errors += _parts_fidelity(src, doc)
    if len(doc.stimuli) != src.stimulus_count:
        errors.append(f"{len(doc.stimuli)} stimuli, the source has {src.stimulus_count}")
    for n, (raw, stimulus) in enumerate(zip(src.figures, doc.stimuli, strict=False), start=1):
        problem = first_difference(plain_of(raw), stimulus.description)
        if problem:
            errors.append(f"stimulus fig{n} description: {problem}")
    if src.figure_note is not None and doc.stimuli:
        note = doc.stimuli[-1]
        if note.description != FIGURE_NOTE_DESCRIPTION:
            errors.append(
                f"stimulus {note.id} (figure note) description is {note.description!r}, "
                f"expected the fixed sentence {FIGURE_NOTE_DESCRIPTION!r}"
            )
    problem = first_difference(source_text(src), document_text(doc))
    if problem:
        errors.append(f"whole question (section 6 order): {problem}")
    return errors


def _mcq_fidelity(src: SourceQuestion, doc: QuestionDocument) -> list[str]:
    mcq = doc.mcq
    if mcq is None:
        return ["no mcq block"]
    errors: list[str] = []
    for key, option in zip("ABCD", mcq.options, strict=False):
        if len(option.cells) != 1:
            errors.append(f"option {key}: {len(option.cells)} cells")
            continue
        errors += one_paragraph(f"option {key}", src.options[key], option.cells[0])
        if key in src.rationales:
            if option.rationale is None:
                errors.append(f"option {key}: no rationale")
            else:
                errors += one_paragraph(f"rationale {key}", src.rationales[key], option.rationale)
    if mcq.explanation is None:
        errors.append("no explanation")
    else:
        errors += diff_items(
            "explanation",
            [SItem("paragraph", raw=p) for p in src.explanation],
            doc_items(mcq.explanation),
        )
    return errors


def _parts_fidelity(src: SourceQuestion, doc: QuestionDocument) -> list[str]:
    errors: list[str] = []
    if len(src.parts) != len(doc.parts):
        return [f"{len(doc.parts)} parts for {len(src.parts)} in the source"]
    for sp, dp in zip(src.parts, doc.parts, strict=True):
        where = f"part {sp.label}"
        if sp.lead_in:
            if dp.lead_in is None:
                errors.append(f"{where}: the source has a lead-in, the document none")
            else:
                errors += diff_items(f"{where} lead_in", sp.lead_in, doc_items(dp.lead_in))
        elif dp.lead_in is not None:
            errors.append(f"{where}: lead_in in the document, none in the source")
        errors += one_paragraph(f"{where} body", sp.body_raw, dp.body)
        lines = [raw for kind, raw in sp.answer_lines if kind != "alt"]
        if sp.has_loose_lines:
            # A line without a tick belongs to no mark point by the rules; compare the whole cell.
            combined = " ".join(lines)
            nodes = [n for p in dp.mark_points for n in doc_items_nodes(p.content)]
            errors += diff_inline(
                f"{where} mark points (cell with a line without a tick)", combined, nodes
            )
        elif len(dp.mark_points) == len(lines):
            for k, (raw, point) in enumerate(zip(lines, dp.mark_points, strict=True), start=1):
                errors += one_paragraph(f"{where} mark point {k}", raw, point.content)
        else:
            errors.append(f"{where}: {len(dp.mark_points)} mark points for {len(lines)} lines")
        if len(sp.notes_raw) != len(dp.notes):
            errors.append(f"{where}: {len(dp.notes)} notes for {len(sp.notes_raw)} note lines")
        else:
            for k, (raw, note) in enumerate(zip(sp.notes_raw, dp.notes, strict=True), start=1):
                errors += one_paragraph(
                    f"{where} note {k}", raw, note.content, keep_ticks=True, drop_italic=True
                )
    return errors


def doc_items_nodes(doc: Doc) -> list[DNode]:
    return [n for item in doc_items(doc) for n in item.nodes]


# --------------------------------------------------------------------------------------------
# Reference vocabulary
# --------------------------------------------------------------------------------------------


@cache
def reference() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    return data


def exam_sections() -> set[str]:
    return {s["code"] for s in reference()["exam_format"]["sections"]}


def command_terms() -> set[str]:
    return set(reference()["exam_format"]["command_terms"])


def leaf_nodes() -> set[str]:
    nodes = reference()["nodes"]
    parents = {n.get("parent") for n in nodes}
    return {n["code"] for n in nodes if n["code"] not in parents}


# --------------------------------------------------------------------------------------------
# Check 3: structure read independently from the Markdown
# --------------------------------------------------------------------------------------------

PAPER_SECTION = {"1A": "paper_1a", "1B": "paper_1b", "2": "paper_2"}
DIFFICULTY = {
    "Kolay": "easy",
    "Kolay–orta": "medium",
    "Orta": "medium",
    "Orta–zor": "hard",
    "Zor": "hard",
}
# IMPORT_RULES 3.3 (as amended): keyword -> kind. The earliest keyword in the description wins.
STIMULUS_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("devre", "circuit_diagram"),
    ("direnç", "circuit_diagram"),
    ("batarya", "circuit_diagram"),
    ("voltmetre", "circuit_diagram"),
    ("ampermetre", "circuit_diagram"),
    ("grafik", "graph"),
    ("eksen", "graph"),
    ("p–v", "graph"),
    ("alan çizgi", "field_diagram"),
    ("ışın", "ray_wavefront_diagram"),
    ("dalga cephe", "ray_wavefront_diagram"),
    ("enerji düzey", "energy_level_diagram"),
    ("uzay-zaman", "spacetime_diagram"),
    ("tablo", "data_table"),
)


def _eq(errors: list[str], what: str, actual: object, expected: object) -> None:
    if actual != expected:
        errors.append(f"{what}: {actual!r}, expected {expected!r}")


def expected_class(src: SourceQuestion) -> str:
    if src.is_mcq:
        return "mcq"
    if src.paper == "1B":
        return "data_based"
    return "long_structured" if src.total_marks == 20 else "short_structured"


def expected_outcome(src: SourceQuestion) -> str:
    """Section 3 and 8: the Kazanim cell as it stands, markup included."""
    return src.row["Kazanım"]


def structure_errors(src: SourceQuestion, doc: QuestionDocument) -> list[str]:
    errors: list[str] = []
    _eq(errors, "schema_version", doc.schema_version, "1.0")
    _eq(errors, "question_class", doc.question_class.value, expected_class(src))
    _eq(errors, "exam_section", doc.exam_section, PAPER_SECTION[src.paper])
    _eq(
        errors,
        "levels",
        [lv.value for lv in doc.levels],
        ["hl"] if src.level_hl else ["sl", "hl"],
    )
    _eq(errors, "language", doc.language, "en")
    _eq(errors, "calculator", doc.calculator, True)
    _eq(
        errors,
        "difficulty",
        doc.difficulty.value if doc.difficulty else None,
        DIFFICULTY[src.row["Zorluk"]],
    )
    _eq(errors, "primary_syllabus_node", doc.primary_syllabus_node, src.primary_node)
    _eq(errors, "secondary_syllabus_nodes", doc.secondary_syllabus_nodes, ())
    if doc.outcome is None or squash(doc.outcome) != squash(expected_outcome(src)):
        errors.append(f"outcome: {doc.outcome!r}, the scope-table cell is {src.row['Kazanım']!r}")
    _eq(errors, "total_marks", doc.total_marks, src.total_marks)
    errors += _stimulus_structure(src, doc)
    level_content = "ahl" if src.level_hl else "sl_core"
    if src.is_mcq:
        errors += _mcq_structure(src, doc, level_content)
    else:
        errors += _parts_structure(src, doc, level_content)
    return errors


def _stimulus_structure(src: SourceQuestion, doc: QuestionDocument) -> list[str]:
    errors: list[str] = []
    count = src.stimulus_count
    _eq(errors, "number of stimuli", len(doc.stimuli), count)
    _eq(
        errors,
        "stimulus ids",
        [s.id for s in doc.stimuli],
        [f"fig{k}" for k in range(1, count + 1)],
    )
    note_tokens = re.findall(r"\d+(?:\.\d+)?", src.figure_note or "")
    for k, stimulus in enumerate(doc.stimuli, start=1):
        if stimulus.asset_id is not None or stimulus.alt_text is not None:
            errors.append(f"fig{k}: has an asset or alt text (the source has none)")
        is_note = src.figure_note is not None and k == count
        _eq(errors, f"fig{k} use", stimulus.use.value, "read_values" if is_note else "read_only")
        own = plain_of(src.figures[k - 1]) if not is_note and k <= len(src.figures) else ""
        for token in note_tokens:
            if token in stimulus.description and token not in own:
                errors.append(f"fig{k}: description contains {token!r} from the figure note")
        if is_note:
            _eq(errors, f"fig{k} kind (figure note)", stimulus.kind.value, "graph")
            _eq(errors, f"fig{k} description", stimulus.description, FIGURE_NOTE_DESCRIPTION)
            if any(ch.isdigit() for ch in stimulus.description):
                errors.append(f"fig{k}: the figure note's description contains a digit")
        else:
            _eq(errors, f"fig{k} kind", stimulus.kind.value, stimulus_kind(stimulus.description))
    return errors


def turkish_lower(text: str) -> str:
    return text.replace("I", "ı").replace("İ", "i").lower()


def stimulus_kind(description: str) -> str:
    """IMPORT_RULES 3.3: the keyword that comes first in the text, matched case-insensitively
    (Turkish casing) at a word start; no keyword gives `schematic_diagram`."""
    lowered = turkish_lower(description)
    best: tuple[int, str] | None = None
    for word, kind in STIMULUS_KEYWORDS:
        for m in re.finditer(re.escape(word), lowered):
            if m.start() == 0 or not lowered[m.start() - 1].isalpha():
                if best is None or m.start() < best[0]:
                    best = (m.start(), kind)
                break
    return best[1] if best else "schematic_diagram"


def _mcq_structure(src: SourceQuestion, doc: QuestionDocument, level_content: str) -> list[str]:
    mcq = doc.mcq
    if mcq is None or doc.parts:
        return ["a multiple-choice question needs an mcq block and no parts"]
    errors: list[str] = []
    _eq(errors, "option keys", [o.key for o in mcq.options], ["A", "B", "C", "D"])
    _eq(errors, "correct_key", mcq.correct_key, src.correct)
    _eq(errors, "option_layout", mcq.option_layout.value, "single_value")
    _eq(errors, "column_headers", mcq.column_headers, ())
    _eq(errors, "statements", mcq.statements, ())
    _eq(errors, "level_content", mcq.level_content.value, level_content)
    hedef = re.fullmatch(r"AO([123])", src.row["Hedef"])
    _eq(
        errors,
        "assessment_objective",
        mcq.assessment_objective,
        int(hedef.group(1)) if hedef else None,
    )
    _eq(errors, "solution_step", mcq.solution_step, None)
    _eq(errors, "solution_model", doc.solution_model, None)
    for option in mcq.options:
        _eq(errors, f"option {option.key} cells", len(option.cells), 1)
        if option.key == src.correct and option.rationale is not None:
            errors.append(f"option {option.key} is the correct one and has a rationale")
        if option.key != src.correct and option.rationale is None:
            errors.append(f"option {option.key} has no rationale")
    return errors


def _parts_structure(src: SourceQuestion, doc: QuestionDocument, level_content: str) -> list[str]:
    errors: list[str] = []
    if doc.mcq is not None:
        errors.append("a structured question has no mcq block")
    if len(doc.parts) != len(src.parts):
        return [*errors, f"{len(doc.parts)} parts for {len(src.parts)} in the source"]
    _eq(errors, "labels", [p.label for p in doc.parts], [p.label for p in src.parts])
    _eq(errors, "part ids", [p.id for p in doc.parts], [p.id for p in src.parts])
    _eq(errors, "part marks", [p.marks for p in doc.parts], [p.marks for p in src.parts])
    for sp, dp in zip(src.parts, doc.parts, strict=True):
        where = f"part {sp.label}"
        _eq(errors, f"{where} syllabus_node", dp.syllabus_node, src.primary_node)
        _eq(errors, f"{where} level_content", dp.level_content.value, level_content)
        _eq(errors, f"{where} assessment_objective", dp.assessment_objective, None)
        _eq(errors, f"{where} depends_on", dp.depends_on, ())
        _eq(errors, f"{where} stimulus_refs", dp.stimulus_refs, ())
        _eq(errors, f"{where} number of mark points", len(dp.mark_points), sp.tick_lines)
        _eq(errors, f"{where} marks_capped", dp.marks_capped, sp.awardable > sp.marks)
        points = sp.points
        for k, (spt, dpt) in enumerate(zip(points, dp.mark_points, strict=False), start=1):
            at = f"{where} mark point {k}"
            _eq(errors, f"{at} id", dpt.id, f"{sp.id}-m{k}")
            _eq(errors, f"{at} route", dpt.route, spt.route)
            _eq(errors, f"{at} alternative_group", dpt.alternative_group, None)
            _eq(errors, f"{at} accept_range", dpt.accept_range, None)
            _eq(errors, f"{at} solution_step", dpt.solution_step, None)
            _eq(errors, f"{at} kind", dpt.kind.value, "statement")
        _eq(errors, f"{where} number of notes", len(dp.notes), len(sp.notes_raw))
        for n, note in enumerate(dp.notes, start=1):
            if len(note.content.content) != 1:
                errors.append(f"{where} note {n}: {len(note.content.content)} blocks, want 1")
        for point in dp.mark_points:
            if len(point.content.content) != 1:
                errors.append(f"{where} {point.id}: {len(point.content.content)} blocks, want 1")
        if len(dp.body.content) != 1:
            errors.append(f"{where} body: {len(dp.body.content)} blocks, want 1")
    if doc.solution_model is not None:
        errors += _solution_model_structure(src, doc)
    return errors


def _solution_model_structure(src: SourceQuestion, doc: QuestionDocument) -> list[str]:
    """Only what IMPORT_RULES 3.4 fixes without a full re-implementation of the conversion."""
    model = doc.solution_model
    errors: list[str] = []
    if model is None:
        return errors
    if not src.has_formula_chain:
        errors.append("solution_model present but the source has no formula chain")
    _eq(errors, "solution_model answers", model.answers, ())
    _eq(
        errors,
        "solution_model steps ids",
        [s.id for s in model.steps],
        [f"s{k}" for k in range(1, len(model.steps) + 1)],
    )
    for step in model.steps:
        if step.stated_value is not None:
            errors.append(f"step {step.id} has a stated_value")
    return errors


# --------------------------------------------------------------------------------------------
# Check 5: the fields filled by rule (IMPORT_RULES section 5)
# --------------------------------------------------------------------------------------------

ANSWER_TYPE = {
    "calculate": "numeric_with_unit",
    "determine": "numeric_with_unit",
    "estimate": "numeric_with_unit",
    "state": "word_phrase",
    "identify": "word_phrase",
    "show": "derivation_numeric",
    "explain": "explanation",
    "outline": "explanation",
    "describe": "explanation",
    "suggest": "explanation",
    "predict": "explanation",
    "deduce": "explanation",
    "discuss": "extended_evaluation",
    "analyse": "extended_evaluation",
    "draw": "drawing_on_diagram",
    "annotate": "drawing_on_diagram",
    "complete": "drawing_on_diagram",
    "sketch": "graph_sketch",
}

_ROMAN_SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_NUMBER = rf"[+−-]?\d+(?:\.\d+)?(?:\s*×\s*10[⁻⁺]?[{_ROMAN_SUP}]+)?"
_UNIT_TOKEN = re.compile(rf"[A-Za-zµΩ°%]+[⁻⁺]?[{_ROMAN_SUP}]*")


def _number_with_unit(text: str) -> bool:
    m = re.fullmatch(rf"({_NUMBER})\s*(.+)", text.strip())
    if m is None:
        return False
    return all(_UNIT_TOKEN.fullmatch(tok) for tok in m.group(2).split())


def _number_or_ratio(text: str) -> bool:
    return bool(
        re.fullmatch(_NUMBER, text.strip()) or re.fullmatch(r"\d+\s*[⁄/:]\s*\d+", text.strip())
    )


def _option_kind(texts: Sequence[str], has_math: Sequence[bool]) -> str:
    """Section 5 applied to the letter, in the order the rule lists (section 8)."""
    if not any(has_math) and all(_number_with_unit(t) for t in texts):
        return "numeric_with_unit"
    if not any(has_math) and all(_number_or_ratio(t) for t in texts):
        return "ratio"
    if any(has_math):
        return "algebraic_expression"
    if all(len(t.split()) <= 4 for t in texts):
        return "word_phrase"
    return "statement"


def expected_option_kind(doc: QuestionDocument) -> str:
    mcq = doc.mcq
    assert mcq is not None
    has_math: list[bool] = []
    plain: list[str] = []
    for option in mcq.options:
        nodes = doc_items_nodes(option.cells[0])
        plain.append("".join(n.text for n in nodes))
        has_math.append(any(n.kind == "math" for n in nodes))
    return _option_kind(plain, has_math)


def expected_command_term(body_text: str) -> str | None:
    """First word, punctuation dropped, lower case, in the dictionary (section 5 and 8)."""
    words = body_text.split()
    if not words:
        return None
    first = words[0].rstrip(",.;:").lower()
    return first if first in command_terms() else None


def expected_note_kind(text: str) -> str:
    t = text.strip()
    if t == "OWTTE":
        return "owtte"
    if t.startswith("Allow ECF"):
        return "ecf"
    if re.match(r"Accept\b", t):
        return "accept"
    if re.match(r"Do not accept\b", t):
        return "do_not_accept"
    if re.match(r"Award \[\d+\] max\b", t) or re.match(r"Award \[\d+ max\]", t):
        return "cap"
    return "general"


def ecf_refs(text: str) -> list[str]:
    refs: list[str] = []
    for m in re.finditer(r"\(([a-z])\)(?:\(([ivx]+)\))?", text):
        ref = m.group(1) + (f".{m.group(2)}" if m.group(2) else "")
        if ref not in refs:
            refs.append(ref)
    return refs


def rule_filled_errors(doc: QuestionDocument) -> list[str]:
    """Recompute section 5 (and the note kinds of 3.2) from the document's own content."""
    errors: list[str] = []
    if doc.mcq is not None:
        kind = expected_option_kind(doc)
        if doc.mcq.option_kind.value != kind:
            errors.append(f"option_kind {doc.mcq.option_kind.value!r}, the rule gives {kind!r}")
    earlier: list[str] = []
    for part in doc.parts:
        errors += _part_rule_errors(part, earlier)
        earlier.append(part.id)
    return errors


def _part_rule_errors(part: Part, earlier: list[str]) -> list[str]:
    errors: list[str] = []
    where = f"part {part.label}"
    body = " ".join("".join(n.text for n in item.nodes) for item in doc_items(part.body))
    term = expected_command_term(body)
    if part.command_term != term:
        errors.append(f"{where} command_term {part.command_term!r}, the rule gives {term!r}")
    show_that = re.match(r"show that\b", body.lower()) is not None
    if part.show_that != show_that:
        errors.append(f"{where} show_that {part.show_that}, expected {show_that}")
    wanted = ANSWER_TYPE[part.command_term] if part.command_term else "explanation"
    if part.answer_type.value != wanted:
        errors.append(f"{where} answer_type {part.answer_type.value!r}, expected {wanted!r}")
    ecf: list[str] = []
    for n, note in enumerate(part.notes, start=1):
        text = " ".join("".join(x.text for x in item.nodes) for item in doc_items(note.content))
        kind = expected_note_kind(text)
        if note.kind.value != kind:
            errors.append(
                f"{where} note {n} kind {note.kind.value!r}, the rule gives {kind!r}: {text[:50]!r}"
            )
        if kind == "ecf":
            for ref in ecf_refs(text):
                if ref not in earlier and any(e.startswith(ref + ".") for e in earlier):
                    errors.append(f"{where} note {n}: cites {ref!r}, a letter with sub-parts")
            ecf += [r for r in ecf_refs(text) if r in earlier and r not in ecf]
    if list(part.ecf_from) != ecf:
        errors.append(f"{where} ecf_from {list(part.ecf_from)}, expected {ecf}")
    return errors


# --------------------------------------------------------------------------------------------
# Check 4: validity
# --------------------------------------------------------------------------------------------

MARKUP_LEFTOVERS = ("*", "`", "<sub", "<sup", "<br", "«", "»", "✓")


def validity_errors(doc: QuestionDocument) -> list[str]:
    """Vocabulary, markup that should have been converted, math source form, text-node hygiene."""
    errors: list[str] = []
    if doc.exam_section not in exam_sections():
        errors.append(f"exam_section {doc.exam_section!r} is not in the reference vocabulary")
    leaves = leaf_nodes()
    nodes = {doc.primary_syllabus_node, *doc.secondary_syllabus_nodes}
    nodes |= {p.syllabus_node for p in doc.parts}
    for code in sorted(nodes):
        if code not in leaves:
            errors.append(f"syllabus node {code!r} is not a leaf of the reference syllabus")
    for part in doc.parts:
        if part.command_term is not None and part.command_term not in command_terms():
            errors.append(
                f"part {part.label}: command term {part.command_term!r} is not in the vocabulary"
            )
    for stimulus in doc.stimuli:
        for bad in MARKUP_LEFTOVERS:
            if bad in stimulus.description:
                errors.append(f"stimulus {stimulus.id}: description contains {bad!r}")
    note_docs = {id(n.content) for part in doc.parts for n in part.notes}
    for number, d in enumerate(doc.docs(), start=1):
        # Section 8: a tick inside a markscheme note stays in the text; nowhere else.
        errors += _doc_hygiene(f"doc {number}", d, allow_tick=id(d) in note_docs)
    return errors


def _doc_hygiene(where: str, d: Doc, *, allow_tick: bool = False) -> list[str]:
    errors: list[str] = []
    for block in d.content:
        if isinstance(block, MathBlock) or block.type in ("bullet_list", "ordered_list"):
            errors.append(f"{where}: unexpected block type {block.type!r}")
    paragraphs: list[Paragraph] = []
    for block in d.content:
        if isinstance(block, Paragraph):
            paragraphs.append(block)
        elif isinstance(block, Table):
            paragraphs += [p for row in block.content for cell in row.content for p in cell.content]
    for n, paragraph in enumerate(paragraphs, start=1):
        at = f"{where} paragraph {n}"
        inlines = paragraph.content
        for k, inline in enumerate(inlines):
            if isinstance(inline, Quantity):
                errors.append(f"{at}: a quantity node")
            elif isinstance(inline, MathInline):
                if not inline.attrs.latex.isascii():
                    errors.append(f"{at}: math is not ASCII: {inline.attrs.latex!r}")
            elif isinstance(inline, Text):
                if not inline.text:
                    errors.append(f"{at}: empty text node")
                for bad in MARKUP_LEFTOVERS:
                    if bad in inline.text and not (allow_tick and bad == "✓"):
                        errors.append(f"{at}: text node contains {bad!r}: {inline.text[:40]!r}")
                if re.search(r"\s{2,}|[\n\r\t]", inline.text):
                    errors.append(f"{at}: whitespace not collapsed: {inline.text[:40]!r}")
                nxt = inlines[k + 1] if k + 1 < len(inlines) else None
                if isinstance(nxt, Text) and {m.type for m in nxt.marks} == {
                    m.type for m in inline.marks
                }:
                    errors.append(f"{at}: two adjacent text nodes with the same marks")
        if inlines:
            first, last = inlines[0], inlines[-1]
            if isinstance(first, Text) and first.text != first.text.lstrip():
                errors.append(f"{at}: leading whitespace")
            if isinstance(last, Text) and last.text != last.text.rstrip():
                errors.append(f"{at}: trailing whitespace")
    return errors


def math_problems(doc: QuestionDocument) -> tuple[str, ...]:
    return qmath.check(doc)


def all_errors(src: SourceQuestion, doc: QuestionDocument) -> list[str]:
    return (
        fidelity_errors(src, doc)
        + structure_errors(src, doc)
        + rule_filled_errors(doc)
        + validity_errors(doc)
    )


# ============================================================================================
# Self-check of the comparison: an invented question pair, built by hand
# ============================================================================================

SELF_CHECK_MARKDOWN = """\
# Pilot soru seti: A.1 Self-check

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (A.1) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Net force on a body in circular motion | AO2 | — | 1 | Orta |
| 2 | Paper 2 | HL | Rolling without slipping on a ramp | AO1–AO3 | State, Show that | 7 | Orta–zor |

---

## Soru 1 — Paper 1A

A turntable rotates with angular speed *ω* about a vertical axis.<br>A coin of mass *m* rests on it at a distance *r* from the axis, and the coin does **not** slip.

> **Şekil:** A flat disc seen from above with a small coin near its rim. *Diagram not to scale.*

What is the magnitude of the net force on the coin?

A. *mω*<sup>2</sup>*r*
B. *mωr*
C. *m*<sub>c</sub>*g*
D. zero

**Cevap: A**

**Çözüm.** The net force is the centripetal force, *F* = *mω*<sup>2</sup>*r*. It is directed *towards the centre*, so **speed** alone is not what is asked.

| Seçenek | Dayandığı yanılgı |
|---|---|
| B | Linear speed *v* = *ωr* is used in place of the force |
| C | Weight *m*<sub>c</sub>*g* is chosen, as if the coin were in free fall |
| D | The coin is thought to be at rest, so the net force is zero |

---

## Soru 2 — Paper 2 (HL, 7 puan)

A small trolley of mass 0.40 kg rolls from rest down a smooth ramp. The speed *v* of the trolley is recorded after it has travelled a distance *s* along the ramp.

> **Şekil:** A ramp inclined at angle *θ* to the horizontal with a trolley at its upper end.
> *Diagram not to scale.*

| *s* / m | *v* / m s⁻¹ ± 0.1 m s⁻¹ |
|---|---|
| 1.0 | 2.1 |
| 2.0 | 3.0 |

**(a)** State the unit of the gradient of a graph of *v*² against *s*. [1]

**(b)** Show that the acceleration of the trolley is about 2.2 m s⁻². [2]

The trolley is replaced by a hoop that rolls without slipping.

> **Şekil:** The hoop at the top of the same ramp.

**(c)** (i) Explain why the linear acceleration of the hoop is smaller than that of the trolley. [2]

 (ii) The mass of the hoop is *m*<sub>h</sub> = 0.40 kg. Calculate the ratio of the two
 accelerations. [2]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 2. | a | | m s⁻² «or N kg⁻¹» ✓ | *OWTTE* | 1 |
| 2. | b | | *v*² = 2 × *a* × *s* **OR** *a* = *v*² / (2 × *s*) ✓<br>*a* = 3.0² / (2 × 2.0) = 2.25 «m s⁻²» ✓ | *Substitution or an answer to at least 3 s.f. must be seen.*<br>*Credit a correct numerical value ✓ if the method is clear.* | 2 |
| 2. | c | i | **ALTERNATIVE 1**<br>some of the energy goes into rotation of the hoop ✓<br>so less is available as translational kinetic energy ✓<br>**ALTERNATIVE 2**<br>the friction force acts up the ramp «at the rim» ✓<br>the net force down the ramp is smaller than *mg* sin *θ* ✓ | *OWTTE*<br>*Allow ECF from (b).*<br>*Award [1] max for a statement without a reason.* | 2 |
| 2. | c | ii | *a*<sub>h</sub> = ½ *g* sin *θ* ✓<br>ratio = 0.5 «= *a*<sub>h</sub> / *a*» ✓ | *Accept* 1 : 2.<br>*Do not accept "half" without a calculation.*<br>*Allow ECF from (b) and (c)(i).* | 2 |

This free paragraph uses *g* = 9.8 m s⁻² and is not part of the question text.

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | s = 2.0 m | |
| `a` | `v**2/(2*s)` | 2.25 m s⁻² |

### Şekil notu

A graph of *v*² against *s* is drawn with gradient 4.50 m s⁻² and intercept 0.12 m² s⁻².

---
"""  # noqa: E501  (Markdown lines are as long as in the real files)

Json = dict[str, Any]


def T(text: str, *marks: str) -> Json:
    node: Json = {"type": "text", "text": text}
    if marks:
        node["marks"] = [{"type": m} for m in marks]
    return node


def M(latex: str, *marks: str) -> Json:
    node: Json = {"type": "math_inline", "attrs": {"latex": latex}}
    if marks:
        node["marks"] = [{"type": m} for m in marks]
    return node


HB: Json = {"type": "hard_break"}


def P(*inlines: Json) -> Json:
    return {"type": "paragraph", "content": list(inlines)}


def FIG(stimulus_id: str) -> Json:
    return {"type": "figure", "attrs": {"stimulus_id": stimulus_id}}


def D(*blocks: Json) -> Json:
    return {"type": "doc", "content": list(blocks)}


def TABLE(header: list[Json], *rows: list[Json]) -> Json:
    def row(cells: list[Json], kind: str) -> Json:
        return {
            "type": "table_row",
            "content": [{"type": kind, "content": [c]} for c in cells],
        }

    return {
        "type": "table",
        "content": [row(header, "table_header"), *(row(r, "table_cell") for r in rows)],
    }


def self_check_mcq() -> Json:
    stem = D(
        P(
            T("A turntable rotates with angular speed "),
            M("\\omega"),
            T(" about a vertical axis."),
            HB,
            T("A coin of mass "),
            M("m"),
            T(" rests on it at a distance "),
            M("r"),
            T(" from the axis, and the coin does "),
            T("not", "bold"),
            T(" slip."),
        ),
        FIG("fig1"),
        P(T("What is the magnitude of the net force on the coin?")),
    )
    return {
        "schema_version": "1.0",
        "question_class": "mcq",
        "exam_section": "paper_1a",
        "levels": ["sl", "hl"],
        "language": "en",
        "calculator": True,
        "difficulty": "medium",
        "primary_syllabus_node": "A.1",
        "outcome": "Net force on a body in circular motion",
        "stem": stem,
        "stimuli": [
            {
                "id": "fig1",
                "kind": "schematic_diagram",
                "use": "read_only",
                "description": "A flat disc seen from above with a small coin near its rim. "
                "Diagram not to scale.",
            }
        ],
        "mcq": {
            "option_kind": "algebraic_expression",
            "option_layout": "single_value",
            "options": [
                {"key": "A", "cells": [D(P(M("m\\omega^{2}"), M("r")))]},
                {
                    "key": "B",
                    "cells": [D(P(M("m\\omega r")))],
                    "rationale": D(
                        P(
                            T("Linear speed "),
                            M("v"),
                            T(" = "),
                            M("\\omega r"),
                            T(" is used in place of the force"),
                        )
                    ),
                },
                {
                    "key": "C",
                    "cells": [D(P(M("m_{c}"), M("g")))],
                    "rationale": D(
                        P(
                            T("Weight "),
                            M("m_{c}"),
                            M("g"),
                            T(" is chosen, as if the coin were in free fall"),
                        )
                    ),
                },
                {
                    "key": "D",
                    "cells": [D(P(T("zero")))],
                    "rationale": D(
                        P(T("The coin is thought to be at rest, so the net force is zero"))
                    ),
                },
            ],
            "correct_key": "A",
            "explanation": D(
                P(
                    T("The net force is the centripetal force, "),
                    M("F"),
                    T(" = "),
                    M("m\\omega^{2}"),
                    M("r"),
                    T(". It is directed "),
                    T("towards the centre", "italic"),
                    T(", so "),
                    T("speed", "bold"),
                    T(" alone is not what is asked."),
                )
            ),
            "assessment_objective": 2,
            "level_content": "sl_core",
        },
        "total_marks": 1,
    }


def _part(
    label: str,
    body: Json,
    marks: int,
    points: list[Json],
    notes: list[Json],
    *,
    command_term: str | None,
    answer_type: str,
    lead_in: Json | None = None,
    show_that: bool = False,
    ecf_from: list[str] | None = None,
) -> Json:
    part: Json = {
        "id": label,
        "label": label,
        "body": body,
        "marks": marks,
        "answer_type": answer_type,
        "level_content": "ahl",
        "syllabus_node": "A.1",
        "mark_points": [
            {**p, "id": f"{label}-m{k}", "kind": "statement"} for k, p in enumerate(points, 1)
        ],
        "notes": notes,
        "show_that": show_that,
    }
    if command_term is not None:
        part["command_term"] = command_term
    if lead_in is not None:
        part["lead_in"] = lead_in
    if ecf_from:
        part["ecf_from"] = ecf_from
    return part


def _note(kind: str, text: str) -> Json:
    return {"kind": kind, "content": D(P(T(text)))}


def self_check_structured() -> Json:
    stem = D(
        P(
            T("A small trolley of mass 0.40 kg rolls from rest down a smooth ramp. The speed "),
            M("v"),
            T(" of the trolley is recorded after it has travelled a distance "),
            M("s"),
            T(" along the ramp."),
        ),
        FIG("fig1"),
        TABLE(
            [P(M("s"), T(" / m")), P(M("v"), T(" / m s⁻¹ ± 0.1 m s⁻¹"))],
            [P(T("1.0")), P(T("2.1"))],
            [P(T("2.0")), P(T("3.0"))],
        ),
    )
    part_a = _part(
        "a",
        D(
            P(
                T("State the unit of the gradient of a graph of "),
                M("v"),
                T("² against "),
                M("s"),
                T("."),
            )
        ),
        1,
        [{"content": D(P(T("m s⁻² "), T("or N kg⁻¹", "optional")))}],
        [_note("owtte", "OWTTE")],
        command_term="state",
        answer_type="word_phrase",
    )
    part_b = _part(
        "b",
        D(P(T("Show that the acceleration of the trolley is about 2.2 m s⁻²."))),
        2,
        [
            {
                "content": D(
                    P(
                        M("v"),
                        T("² = 2 × "),
                        M("a"),
                        T(" × "),
                        M("s"),
                        T(" "),
                        T("OR", "bold"),
                        T(" "),
                        M("a"),
                        T(" = "),
                        M("v"),
                        T("² / (2 × "),
                        M("s"),
                        T(")"),
                    )
                )
            },
            {"content": D(P(M("a"), T(" = 3.0² / (2 × 2.0) = 2.25 "), T("m s⁻²", "optional")))},
        ],
        [
            _note("general", "Substitution or an answer to at least 3 s.f. must be seen."),
            _note("general", "Credit a correct numerical value ✓ if the method is clear."),
        ],
        command_term="show",
        answer_type="derivation_numeric",
        show_that=True,
    )
    part_ci = _part(
        "c.i",
        D(
            P(
                T(
                    "Explain why the linear acceleration of the hoop is smaller than "
                    "that of the trolley."
                )
            )
        ),
        2,
        [
            {
                "content": D(P(T("some of the energy goes into rotation of the hoop"))),
                "route": "alt1",
            },
            {
                "content": D(P(T("so less is available as translational kinetic energy"))),
                "route": "alt1",
            },
            {
                "content": D(
                    P(T("the friction force acts up the ramp "), T("at the rim", "optional"))
                ),
                "route": "alt2",
            },
            {
                "content": D(
                    P(
                        T("the net force down the ramp is smaller than "),
                        M("mg"),
                        T(" sin "),
                        M("\\theta"),
                    )
                ),
                "route": "alt2",
            },
        ],
        [
            _note("owtte", "OWTTE"),
            _note("ecf", "Allow ECF from (b)."),
            _note("cap", "Award [1] max for a statement without a reason."),
        ],
        command_term="explain",
        answer_type="explanation",
        lead_in=D(
            P(T("The trolley is replaced by a hoop that rolls without slipping.")), FIG("fig2")
        ),
        ecf_from=["b"],
    )
    part_cii = _part(
        "c.ii",
        D(
            P(
                T("The mass of the hoop is "),
                M("m_{h}"),
                T(" = 0.40 kg. Calculate the ratio of the two accelerations."),
            )
        ),
        2,
        [
            {"content": D(P(M("a_{h}"), T(" = ½ "), M("g"), T(" sin "), M("\\theta")))},
            {
                "content": D(
                    P(
                        T("ratio = 0.5 "),
                        T("= ", "optional"),
                        M("a_{h}", "optional"),
                        T(" / ", "optional"),
                        M("a", "optional"),
                    )
                )
            },
        ],
        [
            _note("accept", "Accept 1 : 2."),
            _note("do_not_accept", 'Do not accept "half" without a calculation.'),
            _note("ecf", "Allow ECF from (b) and (c)(i)."),
        ],
        command_term=None,
        answer_type="explanation",
        ecf_from=["b", "c.i"],
    )
    return {
        "schema_version": "1.0",
        "question_class": "short_structured",
        "exam_section": "paper_2",
        "levels": ["hl"],
        "language": "en",
        "calculator": True,
        "difficulty": "hard",
        "primary_syllabus_node": "A.1",
        "outcome": "Rolling without slipping on a ramp",
        "stem": stem,
        "stimuli": [
            {
                "id": "fig1",
                "kind": "schematic_diagram",
                "use": "read_only",
                "description": "A ramp inclined at angle θ to the horizontal with a trolley at its "
                "upper end. Diagram not to scale.",
            },
            {
                "id": "fig2",
                "kind": "schematic_diagram",
                "use": "read_only",
                "description": "The hoop at the top of the same ramp.",
            },
            {
                "id": "fig3",
                "kind": "graph",
                "use": "read_values",
                "description": FIGURE_NOTE_DESCRIPTION,
            },
        ],
        "parts": [part_a, part_b, part_ci, part_cii],
        "total_marks": 7,
    }


@cache
def self_check_source() -> dict[int, SourceQuestion]:
    parsed = parse_source_text(SELF_CHECK_MARKDOWN, "a1-self-check")
    return {q.number: q for q in parsed.questions}


def build(data: Json) -> QuestionDocument:
    return QuestionDocument.model_validate(data)


def test_self_check_source_is_read_as_intended() -> None:
    mcq, structured = self_check_source()[1], self_check_source()[2]
    assert [mcq.is_mcq, structured.is_mcq] == [True, False]
    assert mcq.correct == "A" and sorted(mcq.rationales) == ["B", "C", "D"]
    assert len(mcq.figures) == 1 and len(structured.figures) == 2
    assert structured.figures[0].endswith("*Diagram not to scale.*")  # two quote lines joined
    assert [p.label for p in structured.parts] == ["a", "b", "c.i", "c.ii"]
    assert [p.marks for p in structured.parts] == [1, 2, 2, 2]
    assert structured.heading_hl and structured.heading_marks == 7 and structured.total_marks == 7
    assert [len(p.points) for p in structured.parts] == [1, 2, 4, 2]
    assert [pt.route for pt in structured.parts[2].points] == ["alt1", "alt1", "alt2", "alt2"]
    assert structured.parts[2].awardable == 2
    assert structured.parts[2].lead_in and structured.parts[2].lead_in[-1].kind == "figure"
    assert len(structured.parts[3].notes_raw) == 3
    assert structured.has_formula_chain and structured.figure_note is not None
    assert structured.stimulus_count == 3


def test_self_check_faithful_mcq_has_no_error() -> None:
    assert all_errors(self_check_source()[1], build(self_check_mcq())) == []


def test_self_check_faithful_structured_question_has_no_error() -> None:
    assert all_errors(self_check_source()[2], build(self_check_structured())) == []


def test_self_check_whole_text_is_the_section_6_order() -> None:
    q = self_check_source()[2]
    d = build(self_check_structured())
    assert squash(source_text(q)) == squash(document_text(d))
    assert squash(source_text(q)).startswith("Asmalltrolley")
    assert squash(source_text(q)).endswith(squash(FIGURE_NOTE_DESCRIPTION))
    assert "intercept" not in source_text(q)  # the note's own text is not imported


def test_self_check_line_without_a_tick_is_compared_with_its_cell() -> None:
    """A markscheme line without a tick (no rule covers it) must not drop out of the comparison."""
    original = "| 2. | b | | *v*² = 2 × *a* × *s* **OR** *a* = *v*² / (2 × *s*) ✓<br>*a* = 3.0²"
    changed = (
        "| 2. | b | | *v*² = 2 × *a* × *s* **OR** *a* = *v*² / (2 × *s*) ✓<br>**OR**<br>*a* = 3.0²"
    )
    assert original in SELF_CHECK_MARKDOWN
    parsed = parse_source_text(SELF_CHECK_MARKDOWN.replace(original, changed), "a1-self-check")
    src = parsed.questions[1]
    assert src.parts[1].has_loose_lines and src.parts[1].tick_lines == 2
    at_front = self_check_structured()
    point = at_front["parts"][1]["mark_points"][1]["content"]["content"][0]
    point["content"][:0] = [T("OR", "bold"), T(" ")]
    assert all_errors(src, build(at_front)) == []
    at_end = self_check_structured()
    point = at_end["parts"][1]["mark_points"][0]["content"]["content"][0]
    point["content"][-1]["text"] += " "
    point["content"].append(T("OR", "bold"))
    assert all_errors(src, build(at_end)) == []
    assert all_errors(src, build(self_check_structured())) != []  # the "OR" is gone: detected


def test_self_check_text_between_a_closing_rule_and_the_next_heading_is_an_error() -> None:
    broken = SELF_CHECK_MARKDOWN.replace(
        "---\n\n## Soru 2", "---\n\nstray words after the rule\n\n## Soru 2"
    )
    assert broken != SELF_CHECK_MARKDOWN
    with pytest.raises(SourceError, match="closing ---"):
        parse_source_text(broken, "a1-self-check")


# --- corruptions ------------------------------------------------------------------------------


def _inlines(block: Json) -> list[Json]:
    content: list[Json] = block["content"]
    return content


def _first(nodes: list[Json], **where: Any) -> int:
    for index, n in enumerate(nodes):
        if all(
            (n.get("attrs", {}).get("latex") if k == "latex" else n.get(k)) == v
            for k, v in where.items()
        ):
            return index
    raise AssertionError(f"no node with {where}")


def _part_of(d: Json, label: str) -> Json:
    part: Json = next(p for p in d["parts"] if p["label"] == label)
    return part


def _point_inlines(d: Json, label: str, k: int) -> list[Json]:
    return _inlines(_part_of(d, label)["mark_points"][k]["content"]["content"][0])


def c_drop_word(d: Json) -> None:
    _inlines(d["stem"]["content"][0])[2]["text"] = " about a vertical."


def c_digit(d: Json) -> None:
    body = _inlines(_part_of(d, "c.ii")["body"]["content"][0])
    body[2]["text"] = body[2]["text"].replace("0.40", "0.45")


def c_swap_options(d: Json) -> None:
    options = d["mcq"]["options"]
    options[0]["cells"], options[1]["cells"] = options[1]["cells"], options[0]["cells"]


def c_missing_point(d: Json) -> None:
    part = _part_of(d, "b")
    part["mark_points"].pop()
    part["marks"] = 1
    d["total_marks"] = 6


def c_variable_other_letter_mcq(d: Json) -> None:
    nodes = _inlines(d["stem"]["content"][0])
    nodes[_first(nodes, latex="m")] = T("w")


def c_variable_other_letter_structured(d: Json) -> None:
    nodes = _point_inlines(d, "b", 0)
    nodes[0] = T("w")


def c_variable_same_letter_as_text(d: Json) -> None:
    nodes = _inlines(d["stem"]["content"][0])
    nodes[_first(nodes, latex="r")] = T("r")


def c_math_node_invented(d: Json) -> None:
    nodes = _inlines(d["stem"]["content"][0])
    index = _first(nodes, type="text", text=" from the axis, and the coin does ")
    nodes[index : index + 1] = [T(" from the "), M("a"), T("xis, and the coin does ")]


def c_missing_note(d: Json) -> None:
    _part_of(d, "c.i")["notes"].pop()


def c_note_swapped(d: Json) -> None:
    notes = _part_of(d, "c.i")["notes"]
    notes[0], notes[1] = notes[1], notes[0]


def c_note_kind(d: Json) -> None:
    _part_of(d, "c.ii")["notes"][0]["kind"] = "general"


def c_ecf_from(d: Json) -> None:
    _part_of(d, "c.ii")["ecf_from"] = ["b"]


def c_ecf_from_missing(d: Json) -> None:
    _part_of(d, "c.i")["ecf_from"] = []


def c_routes_swapped(d: Json) -> None:
    for point in _part_of(d, "c.i")["mark_points"]:
        point["route"] = "alt2" if point["route"] == "alt1" else "alt1"


def c_route_dropped(d: Json) -> None:
    for point in _part_of(d, "c.i")["mark_points"]:
        del point["route"]
    _part_of(d, "c.i")["marks_capped"] = True


def c_optional_lost(d: Json) -> None:
    nodes = _point_inlines(d, "a", 0)
    nodes[1] = T("or N kg⁻¹")


def c_bold_lost_structured(d: Json) -> None:
    nodes = _point_inlines(d, "b", 0)
    nodes[_first(nodes, text="OR")] = T("OR")


def c_bold_lost_mcq(d: Json) -> None:
    nodes = _inlines(d["stem"]["content"][0])
    nodes[_first(nodes, text="not")] = T("not")


def c_italic_lost(d: Json) -> None:
    nodes = _inlines(d["mcq"]["explanation"]["content"][0])
    nodes[_first(nodes, text="towards the centre")] = T("towards the centre")


def c_table_cell(d: Json) -> None:
    d["stem"]["content"][2]["content"][1]["content"][1]["content"][0]["content"][0]["text"] = "2.2"


def c_table_header_kind(d: Json) -> None:
    d["stem"]["content"][2]["content"][0]["content"][0]["type"] = "table_cell"


def c_table_quantity(d: Json) -> None:
    cell = d["stem"]["content"][2]["content"][1]["content"][1]["content"][0]
    cell["content"] = [{"type": "quantity", "attrs": {"value": "2.1"}}]


def c_lead_in_dropped(d: Json) -> None:
    del _part_of(d, "c.i")["lead_in"]


def c_figure_node_removed(d: Json) -> None:
    del d["stem"]["content"][1]


def c_figure_description(d: Json) -> None:
    d["stimuli"][0]["description"] = d["stimuli"][0]["description"].replace("small", "large")


def c_figure_kind(d: Json) -> None:
    d["stimuli"][0]["kind"] = "graph"


def c_figure_use(d: Json) -> None:
    d["stimuli"][1]["use"] = "read_values"


def c_show_that(d: Json) -> None:
    _part_of(d, "b")["show_that"] = False


def c_command_term(d: Json) -> None:
    _part_of(d, "a")["command_term"] = "calculate"


def c_answer_type(d: Json) -> None:
    _part_of(d, "c.ii")["answer_type"] = "numeric_with_unit"


def c_command_term_in_context_sentence(d: Json) -> None:
    _part_of(d, "c.ii")["command_term"] = "calculate"
    _part_of(d, "c.ii")["answer_type"] = "numeric_with_unit"


def c_point_id(d: Json) -> None:
    _part_of(d, "b")["mark_points"][1]["id"] = "b-m3"


def c_sub_letter(d: Json) -> None:
    nodes = _point_inlines(d, "c.ii", 1)
    nodes[_first(nodes, latex="a_{h}")]["attrs"]["latex"] = "a_{k}"


def c_sub_lost(d: Json) -> None:
    nodes = _inlines(_part_of(d, "c.ii")["body"]["content"][0])
    index = _first(nodes, latex="m_{h}")
    nodes[index : index + 1] = [M("m"), T("h", "sub")]


def c_sup_as_sub(d: Json) -> None:
    d["mcq"]["options"][0]["cells"][0]["content"][0]["content"][0]["attrs"]["latex"] = (
        "m\\omega_{2}"
    )


def c_greek_letter(d: Json) -> None:
    nodes = _point_inlines(d, "c.ii", 0)
    nodes[_first(nodes, latex="\\theta")]["attrs"]["latex"] = "\\phi"


def c_greek_as_latin(d: Json) -> None:
    d["mcq"]["options"][1]["cells"][0]["content"][0]["content"][0]["attrs"]["latex"] = "m w r"


def c_rationale_word(d: Json) -> None:
    rationale = d["mcq"]["options"][3]["rationale"]["content"][0]["content"][0]
    rationale["text"] = rationale["text"].replace("is zero", "is nonzero")


def c_correct_key(d: Json) -> None:
    d["mcq"]["correct_key"] = "B"
    d["mcq"]["options"][0]["rationale"] = d["mcq"]["options"][1]["rationale"]
    d["mcq"]["options"][1].pop("rationale")


def c_option_kind(d: Json) -> None:
    d["mcq"]["option_kind"] = "ratio"


def c_hard_break_lost(d: Json) -> None:
    nodes = _inlines(d["stem"]["content"][0])
    index = _first(nodes, type="hard_break")
    del nodes[index]
    nodes[index]["text"] = " " + nodes[index]["text"]


def c_levels(d: Json) -> None:
    d["levels"] = ["hl"]


def c_difficulty(d: Json) -> None:
    d["difficulty"] = "hard"


def c_outcome(d: Json) -> None:
    d["outcome"] = "Net force on a body"


def c_extra_stem_text(d: Json) -> None:
    d["stem"]["content"].append(P(T("Take care.")))


def c_leftover_markup(d: Json) -> None:
    nodes = _inlines(d["stem"]["content"][2])
    nodes[0]["text"] = nodes[0]["text"].replace("net force", "*net* force")


def c_exam_section(d: Json) -> None:
    d["exam_section"] = "paper_2"


def c_part_marks_capped(d: Json) -> None:
    _part_of(d, "b")["mark_points"].append(
        {
            "id": "b-m3",
            "kind": "statement",
            "content": D(P(T("extra"))),
        }
    )
    _part_of(d, "b")["marks_capped"] = True


def c_whitespace(d: Json) -> None:
    nodes = _inlines(d["stem"]["content"][0])
    nodes[0]["text"] = nodes[0]["text"].replace("turntable rotates", "turntable  rotates")


def c_ascii(d: Json) -> None:
    d["mcq"]["options"][2]["cells"][0]["content"][0]["content"][1]["attrs"]["latex"] = "ǵ"


def c_stimulus_markup(d: Json) -> None:
    d["stimuli"][1]["description"] = "The *hoop* at the top of the same ramp."


def c_note_tick_removed(d: Json) -> None:
    note = _part_of(d, "b")["notes"][1]["content"]["content"][0]["content"][0]
    note["text"] = note["text"].replace(" ✓", "")


def c_tick_in_mark_point(d: Json) -> None:
    nodes = _point_inlines(d, "a", 0)
    nodes[0]["text"] = nodes[0]["text"] + "✓"


def c_italic_kept_in_note(d: Json) -> None:
    paragraph = _part_of(d, "c.ii")["notes"][0]["content"]["content"][0]
    paragraph["content"] = [T("Accept", "italic"), T(" 1 : 2.")]


def c_variable_in_note(d: Json) -> None:
    paragraph = _part_of(d, "b")["notes"][0]["content"]["content"][0]
    paragraph["content"] = [
        T("Substitution or an answer to at least 3 "),
        M("s"),
        T(".f. must be seen."),
    ]


def c_note_stimulus_leak(d: Json) -> None:
    d["stimuli"][2]["description"] = FIGURE_NOTE_DESCRIPTION + " Gradient 4.50."


def c_note_stimulus_own_text(d: Json) -> None:
    d["stimuli"][2]["description"] = "A graph of v² against s is drawn."


def c_note_stimulus_kind(d: Json) -> None:
    d["stimuli"][2]["kind"] = "data_table"


def c_note_stimulus_use(d: Json) -> None:
    d["stimuli"][2]["use"] = "read_only"


def c_note_stimulus_missing(d: Json) -> None:
    d["stimuli"].pop()


def c_note_figure_node(d: Json) -> None:
    d["stem"]["content"].insert(1, FIG("fig3"))


def c_greek_variant_command(d: Json) -> None:
    nodes = _point_inlines(d, "c.ii", 0)
    nodes[_first(nodes, latex="\\theta")]["attrs"]["latex"] = "\\vartheta"


@dataclass(frozen=True)
class Corruption:
    name: str
    target: str  # "mcq" | "structured"
    apply: Callable[[Json], None]
    # a fragment that must appear in at least one error message (the check that should catch it)
    expect: str


CORRUPTIONS: tuple[Corruption, ...] = (
    Corruption("a dropped word", "mcq", c_drop_word, "text differs"),
    Corruption("a changed digit", "structured", c_digit, "text differs"),
    Corruption("two options swapped", "mcq", c_swap_options, "text differs"),
    Corruption("a missing mark point", "structured", c_missing_point, "mark points"),
    Corruption(
        "a variable as another plain letter (mcq)",
        "mcq",
        c_variable_other_letter_mcq,
        "text differs",
    ),
    Corruption(
        "a variable as another plain letter",
        "structured",
        c_variable_other_letter_structured,
        "text differs",
    ),
    Corruption(
        "a variable left as plain text", "mcq", c_variable_same_letter_as_text, "variable *r*"
    ),
    Corruption(
        "a math node with no variable behind it", "mcq", c_math_node_invented, "math nodes with no"
    ),
    Corruption("a missing note", "structured", c_missing_note, "notes"),
    Corruption("two notes swapped", "structured", c_note_swapped, "text differs"),
    Corruption("a wrong note kind", "structured", c_note_kind, "kind"),
    Corruption("a wrong ecf_from", "structured", c_ecf_from, "ecf_from"),
    Corruption("a missing ecf_from", "structured", c_ecf_from_missing, "ecf_from"),
    Corruption("routes swapped", "structured", c_routes_swapped, "route"),
    Corruption("routes dropped", "structured", c_route_dropped, "route"),
    Corruption("optional text lost", "structured", c_optional_lost, "optional"),
    Corruption("bold lost (markscheme)", "structured", c_bold_lost_structured, "bold"),
    Corruption("bold lost (stem)", "mcq", c_bold_lost_mcq, "bold"),
    Corruption("italic lost", "mcq", c_italic_lost, "italic"),
    Corruption("a table cell changed", "structured", c_table_cell, "text differs"),
    Corruption(
        "a table header turned into a cell", "structured", c_table_header_kind, "table_header"
    ),
    Corruption("a quantity node", "structured", c_table_quantity, "quantity"),
    Corruption("a dropped lead-in", "structured", c_lead_in_dropped, "lead"),
    Corruption("a figure node removed", "mcq", c_figure_node_removed, "blocks are"),
    Corruption("a changed figure description", "mcq", c_figure_description, "description"),
    Corruption("a wrong stimulus kind", "structured", c_figure_kind, "kind"),
    Corruption("a wrong stimulus use", "structured", c_figure_use, "use"),
    Corruption("show_that cleared", "structured", c_show_that, "show_that"),
    Corruption("a wrong command term", "structured", c_command_term, "command_term"),
    Corruption("a wrong answer type", "structured", c_answer_type, "answer_type"),
    Corruption(
        "a command term taken from a context sentence",
        "structured",
        c_command_term_in_context_sentence,
        "command_term",
    ),
    Corruption("a wrong mark point id", "structured", c_point_id, "id"),
    Corruption("a changed subscript letter", "structured", c_sub_letter, "text differs"),
    Corruption("a subscript left as text", "structured", c_sub_lost, "variable"),
    Corruption("a superscript turned into a subscript", "mcq", c_sup_as_sub, "variable"),
    Corruption("a different Greek letter", "structured", c_greek_letter, "text differs"),
    Corruption("a Greek letter written as Latin", "mcq", c_greek_as_latin, "text differs"),
    Corruption("a changed rationale", "mcq", c_rationale_word, "text differs"),
    Corruption("a wrong correct key", "mcq", c_correct_key, "correct_key"),
    Corruption("a wrong option_kind", "mcq", c_option_kind, "option_kind"),
    Corruption("a lost hard_break", "mcq", c_hard_break_lost, "hard_break"),
    Corruption("wrong levels", "mcq", c_levels, "levels"),
    Corruption("a wrong difficulty", "mcq", c_difficulty, "difficulty"),
    Corruption("a wrong outcome", "mcq", c_outcome, "outcome"),
    Corruption("an added paragraph", "mcq", c_extra_stem_text, "blocks are"),
    Corruption("markup left in a text node", "mcq", c_leftover_markup, "text differs"),
    Corruption("a wrong exam section", "mcq", c_exam_section, "exam_section"),
    Corruption("marks_capped set without cause", "structured", c_part_marks_capped, "mark points"),
    Corruption("uncollapsed whitespace", "mcq", c_whitespace, "whitespace not collapsed"),
    Corruption("non-ASCII LaTeX", "mcq", c_ascii, "not ASCII"),
    Corruption("markup in a stimulus description", "structured", c_stimulus_markup, "description"),
    Corruption("a tick lost from a note", "structured", c_note_tick_removed, "text differs"),
    Corruption("a tick kept in a mark point", "structured", c_tick_in_mark_point, "'✓'"),
    Corruption("an italic mark kept in a note", "structured", c_italic_kept_in_note, "italic"),
    Corruption("a variable made math in a note", "structured", c_variable_in_note, "math nodes"),
    Corruption("text of the figure note leaked", "structured", c_note_stimulus_leak, "description"),
    Corruption(
        "the figure note's own text imported", "structured", c_note_stimulus_own_text, "description"
    ),
    Corruption(
        "a wrong kind for the figure note", "structured", c_note_stimulus_kind, "figure note"
    ),
    Corruption("a wrong use for the figure note", "structured", c_note_stimulus_use, "use"),
    Corruption(
        "the figure note's stimulus missing", "structured", c_note_stimulus_missing, "stimul"
    ),
    Corruption(
        "a figure node pointing at the figure note", "structured", c_note_figure_node, "blocks are"
    ),
    Corruption("a variant Greek command", "structured", c_greek_variant_command, "text differs"),
)


@pytest.mark.parametrize("corruption", CORRUPTIONS, ids=lambda c: c.name)
def test_self_check_every_corruption_is_detected(corruption: Corruption) -> None:
    if corruption.target == "mcq":
        data, src = self_check_mcq(), self_check_source()[1]
    else:
        data, src = self_check_structured(), self_check_source()[2]
    data = copy.deepcopy(data)
    corruption.apply(data)
    doc = build(data)  # the corrupted document is still valid under the schema
    errors = all_errors(src, doc)
    assert errors, f"{corruption.name}: the comparison found nothing wrong"
    assert any(corruption.expect in e for e in errors), (
        f"{corruption.name}: detected, but not by the intended check "
        f"({corruption.expect!r}); errors: {errors}"
    )


def test_self_check_corruptions_cover_both_targets_and_are_unique() -> None:
    names = [c.name for c in CORRUPTIONS]
    assert len(set(names)) == len(names)
    assert {c.target for c in CORRUPTIONS} == {"mcq", "structured"}
    assert len(CORRUPTIONS) >= 40


def test_self_check_error_message_shows_context_on_both_sides() -> None:
    data = self_check_mcq()
    c_drop_word(data)
    errors = fidelity_errors(self_check_source()[1], build(data))
    first = errors[0]
    assert first.startswith("stem block 1: text differs: first difference at position")
    assert "source ..." in first and "document ..." in first
    assert "axis" in first  # the source side still has the dropped word in the context


# --- the helpers on their own (Hypothesis where the input space is large) ---------------------

_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZαβγδεζηθικλμνξπρστυφχψωΓΔΘΛΞΠΣΥΦΨΩ"
_NO_MARKUP = st.text(
    alphabet=st.characters(
        blacklist_characters="*<>«»✓|`\\", blacklist_categories=("Cs", "Cc", "Zl", "Zp")
    ),
    max_size=60,
)


@given(st.text(alphabet=_LETTERS + "0123456789", min_size=1, max_size=12))
def test_greek_round_trip_through_section_4_3(text: str) -> None:
    assert squash(latex_to_plain(tex_of(text))) == squash(text)
    assert tex_of(text).isascii()


@given(
    st.text(alphabet=_LETTERS, min_size=1, max_size=8),
    st.text(alphabet=_LETTERS + "0123", max_size=5),
)
def test_subscript_forms_follow_the_rule(base: str, sub: str) -> None:
    run = Run(base, 0, (1,), "sub" if sub else "", sub)
    latex = expected_latex(run)
    assert latex.isascii()
    assert squash(latex_to_plain(latex)) == squash(base + sub)
    if sub:
        assert "_{" in latex and latex.endswith("}")


def test_command_followed_by_a_letter_gets_a_space() -> None:
    assert tex_of("Iω") == "I\\omega"
    assert tex_of("ωt") == "\\omega t"
    assert tex_of("ωω") == "\\omega\\omega"
    assert tex_of("ω2") == "\\omega2"
    assert tex_of("Δ") == "\\Delta"


@given(_NO_MARKUP)
def test_plain_text_without_markup_is_unchanged_by_the_scanner(text: str) -> None:
    assert plain_of(text) == text


@given(_NO_MARKUP, st.data())
def test_comparison_ignores_whitespace_and_nothing_else(text: str, data: st.DataObject) -> None:
    stripped = squash(text)
    if not stripped:
        return
    cut = data.draw(st.integers(min_value=0, max_value=len(stripped)))
    spaced = stripped[:cut] + data.draw(st.sampled_from([" ", "\n", "\t", "  "])) + stripped[cut:]
    assert first_difference(text, spaced) == ""
    index = data.draw(st.integers(min_value=0, max_value=len(stripped) - 1))
    changed = stripped[:index] + ("☃" if stripped[index] != "☃" else "x") + stripped[index + 1 :]
    message = first_difference(text, changed)
    assert message.startswith(f"first difference at position {index} ")


def test_scanner_reads_each_kind_of_markup() -> None:
    segs = scan("a **b** *c*<sub>d</sub> «e<br>f» <sup>g</sup> ✓")
    assert "".join(s.text for s in segs) == "a b cd e f g "
    by_text = {s.text: s for s in segs if s.text.strip()}
    assert by_text["b"].bold and by_text["c"].italic and by_text["d"].sub and by_text["g"].sup
    assert by_text["e"].optional and not by_text["a "].bold
    with pytest.raises(SourceError):
        scan("an *unclosed italic")
    with pytest.raises(SourceError):
        scan("an «unclosed guillemet")


def test_ticks_are_kept_only_when_asked() -> None:
    assert plain_of("**OR** x ✓", keep_ticks=True) == "OR x ✓"
    assert plain_of("x ✓") == "x "


def test_classification_of_italic_runs() -> None:
    assert [classify_run(t) for t in ("v", "ω", "Mv", "GMm", "Iω", "ωt", "mv", "hf", "not")] == [
        "A",
        "A",
        "A",
        "A",
        "A",
        "A",
        "B",
        "B",
        "B",
    ]
    assert [classify_run(t) for t in ("Accept", "two words", "x2", "", "1e6")] == ["C"] * 5
    assert classify_run("ABCDE") == "C"  # longer than four characters and not lowercase


def test_note_and_option_rules_on_small_inputs() -> None:
    assert expected_note_kind("OWTTE") == "owtte"
    assert expected_note_kind("Allow ECF from (b).") == "ecf"
    assert expected_note_kind("Allow ECF for the volume from (a).") == "ecf"
    assert expected_note_kind("Accept 3 s.f.") == "accept"
    assert expected_note_kind("Do not accept it.") == "do_not_accept"
    assert expected_note_kind("Award [2] max if x.") == "cap"
    assert expected_note_kind("Award [2 max] if x.") == "cap"
    assert expected_note_kind("Award the third mark only if x.") == "general"
    assert expected_note_kind("Award [0] for x.") == "general"
    assert expected_note_kind("Do not award it.") == "general"
    assert expected_command_term("Explain, with reference to x") == "explain"
    assert expected_command_term("Determine the x") == "determine"
    assert expected_command_term("The mass is 2 kg. Calculate x") is None
    assert expected_command_term("Comment on x") is None
    assert ecf_refs("Allow ECF from (b) and (c)(i).") == ["b", "c.i"]
    assert _option_kind(["5.0 m s⁻¹", "7 m"], [False, False]) == "numeric_with_unit"
    assert _option_kind(["1/3", "9", "2.5 × 10²"], [False] * 3) == "ratio"
    assert _option_kind(["3.0 V and 80 ms", "6 V"], [False, False]) == "statement"
    assert _option_kind(["white dwarf", "red giant"], [False, False]) == "word_phrase"
    assert _option_kind(["2", "3"], [True, False]) == "algebraic_expression"
    assert _option_kind(["a b c d e", "x"], [False, False]) == "statement"
    # section 8: read to the letter; a lone zero or a plain-text Greek letter spoils "number + unit"
    assert _option_kind(["−2.0 J K⁻¹", "0", "+0.5 J K⁻¹"], [False] * 3) == "word_phrase"
    assert _option_kind(["π/6 rad", "π/3 rad"], [False, False]) == "word_phrase"


@pytest.mark.parametrize(
    ("description", "kind"),
    [
        ("Bir devre ve bir grafik", "circuit_diagram"),
        ("Bir grafik ve bir devre", "graph"),  # the earliest keyword wins, not list order
        ("Nothing special", "schematic_diagram"),
        ("Kenarın dışında kalan bölge", "schematic_diagram"),  # "ışın" inside "dışında": no match
        ("Işın demeti levhaya gelir", "ray_wavefront_diagram"),  # capital Turkish dotless I
        ("IŞIN demeti", "ray_wavefront_diagram"),
        ("Devreye seri bağlı bir ampermetre", "circuit_diagram"),
        ("Bir ampermetre ve bir eksen", "circuit_diagram"),
        ("Bir gaz için P–V çevrimi", "graph"),
        ("Dalga cepheleri ve ışınlar", "ray_wavefront_diagram"),
        ("Enerji düzeyleri ve bir tablo", "energy_level_diagram"),
        ("Bir uzay-zaman çizimi", "spacetime_diagram"),
        ("Bir tablo", "data_table"),
        ("Alan çizgileri", "field_diagram"),
        ("Bir sistemi gösteren şema", "schematic_diagram"),
    ],
)
def test_stimulus_kind_rule(description: str, kind: str) -> None:
    assert stimulus_kind(description) == kind


# ============================================================================================
# The source files themselves (no JSON needed): the reading above must hold for all 24 files
# ============================================================================================

QUESTIONS = all_source_questions()
QUESTION_PARAMS = [pytest.param(q, id=q.ref) for q in QUESTIONS]
STEMS = [f.stem for f in source_files()]


def test_source_inventory_matches_the_contract() -> None:
    assert len(source_files()) == EXPECTED_FILES
    assert len(QUESTIONS) == EXPECTED_QUESTIONS
    by_paper = Counter(PAPER_SECTION[q.paper] for q in QUESTIONS)
    assert dict(by_paper) == EXPECTED_BY_SECTION


@pytest.mark.parametrize("sf", source_files(), ids=lambda f: f.stem)
def test_source_question_numbers_are_the_headings_in_order(sf: SourceFile) -> None:
    assert [q.number for q in sf.questions] == sf.numbers
    assert sf.numbers == sorted(set(sf.numbers))


@pytest.mark.parametrize("src", QUESTION_PARAMS)
def test_source_question_is_internally_consistent(src: SourceQuestion) -> None:
    """Section 3 conditions that make a question convertible at all, read from the Markdown."""
    assert src.row["Bölüm"] == f"Paper {src.paper}"
    assert src.row["Düzey"] in ("SL", "HL")
    assert src.row["Zorluk"] in DIFFICULTY
    assert int(src.row["Puan"]) == src.total_marks
    assert src.stem_items, "empty stem"
    if src.is_mcq:
        assert src.correct in "ABCD"
        assert sorted(src.rationales) == sorted(set("ABCD") - {src.correct})
        assert src.explanation
        return
    assert src.heading_marks == src.total_marks
    assert src.paper != "1B" or src.heading_marks is not None
    for part in src.parts:
        assert 1 <= part.marks <= 3
        assert part.total_col == part.marks
        assert part.points, f"part {part.label}: no mark point"
        assert part.awardable >= part.marks, f"part {part.label}: fewer points than marks"
        assert part.body_raw
    labels = [p.label for p in src.parts]
    assert labels == sorted(labels, key=lambda lab: (lab.partition(".")[0], len(lab), lab))


def test_source_figure_blocks_and_notes_are_28() -> None:
    quote_blocks = sum(len(q.figures) for q in QUESTIONS)
    notes = sum(q.figure_note is not None for q in QUESTIONS)
    assert (quote_blocks, notes) == (23, 5)


# ============================================================================================
# Check 1: inventory of the committed JSON
# ============================================================================================


@cache
def pilot_file(stem: str) -> PilotFile:
    path = JSON_DIR / f"{stem}.json"
    if not path.is_file():
        pytest.fail(f"content/pilot/{stem}.json does not exist: that file has not been converted")
    return PilotFile.model_validate_json(path.read_text(encoding="utf-8"))


def converted(src: SourceQuestion) -> PilotQuestion:
    matches = [q for q in pilot_file(src.stem).questions if q.number == src.number]
    if len(matches) != 1:
        pytest.fail(f"{src.ref}: {len(matches)} converted questions with number {src.number}")
    return matches[0]


def test_exactly_one_json_file_per_markdown_file() -> None:
    wanted = sorted(STEMS)
    present = sorted(p.stem for p in JSON_DIR.glob("*.json")) if JSON_DIR.is_dir() else []
    assert len(present) == EXPECTED_FILES, f"{len(present)} JSON files in content/pilot"
    assert present == wanted


@pytest.mark.parametrize("sf", source_files(), ids=lambda f: f.stem)
def test_json_file_is_tied_to_its_source_file(sf: SourceFile) -> None:
    data = pilot_file(sf.stem)
    assert data.source_file == f"docs/pilot/{sf.stem}{FILE_SUFFIX}"
    path = REPO_ROOT / data.source_file
    assert path.is_file(), f"{data.source_file} does not exist"
    assert data.source_sha256 == hashlib.sha256(path.read_bytes()).hexdigest(), (
        "the JSON file is stale: its source_sha256 is not the hash of the Markdown file"
    )
    assert data.source_sha256 == sf.sha256
    assert data.stem == sf.stem


@pytest.mark.parametrize("sf", source_files(), ids=lambda f: f.stem)
def test_json_question_numbers_are_the_headings_in_order(sf: SourceFile) -> None:
    data = pilot_file(sf.stem)
    assert [q.number for q in data.questions] == sf.numbers
    assert [q.source_ref for q in data.questions] == [source_ref(sf.stem, n) for n in sf.numbers]


def test_all_questions_are_converted_with_unique_source_refs() -> None:
    refs: list[str] = []
    for stem in STEMS:
        refs += [q.source_ref for q in pilot_file(stem).questions]
    assert len(refs) == EXPECTED_QUESTIONS
    assert len(set(refs)) == len(refs)
    assert sorted(refs) == sorted(q.ref for q in QUESTIONS)


def test_class_counts() -> None:
    sections: Counter[str] = Counter()
    classes: Counter[str] = Counter()
    for stem in STEMS:
        for q in pilot_file(stem).questions:
            sections[q.document.exam_section] += 1
            classes[q.document.question_class.value] += 1
    assert dict(sections) == EXPECTED_BY_SECTION
    assert classes["mcq"] == 101
    assert classes["data_based"] == 5
    assert classes["short_structured"] + classes["long_structured"] == 24


# ============================================================================================
# Checks 2 to 5, one test per question so that a failure names it
# ============================================================================================


def _assert_clean(src: SourceQuestion, errors: list[str]) -> None:
    assert not errors, f"{src.ref}:\n  " + "\n  ".join(errors)


@pytest.mark.parametrize("src", QUESTION_PARAMS)
def test_text_fidelity(src: SourceQuestion) -> None:
    _assert_clean(src, fidelity_errors(src, converted(src).document))


@pytest.mark.parametrize("src", QUESTION_PARAMS)
def test_structure(src: SourceQuestion) -> None:
    _assert_clean(src, structure_errors(src, converted(src).document))


@pytest.mark.parametrize("src", QUESTION_PARAMS)
def test_validity_of_vocabulary_markup_and_text_nodes(src: SourceQuestion) -> None:
    _assert_clean(src, validity_errors(converted(src).document))


@node
@pytest.mark.parametrize("src", QUESTION_PARAMS)
def test_every_math_node_renders(src: SourceQuestion) -> None:
    assert math_problems(converted(src).document) == ()


@pytest.mark.parametrize("src", QUESTION_PARAMS)
def test_rule_filled_fields(src: SourceQuestion) -> None:
    _assert_clean(src, rule_filled_errors(converted(src).document))


# ============================================================================================
# Check 6: the conversion report
# ============================================================================================


def test_conversion_report_counts_match_the_json() -> None:
    assert REPORT_FILE.is_file(), "content/pilot/CONVERSION_REPORT.md does not exist"
    lines = REPORT_FILE.read_text(encoding="utf-8").splitlines()
    problems: list[str] = []
    total = 0
    for sf in source_files():
        count = len(pilot_file(sf.stem).questions)
        total += count
        if count != len(sf.questions):
            problems.append(
                f"{sf.stem}: the JSON has {count} questions, the Markdown {len(sf.questions)}"
            )
        found = False
        for line in lines:
            if sf.stem not in line:
                continue
            if line.startswith("|"):
                cells = split_row(line)
                found |= any(
                    cell.strip("`") == sf.stem
                    and idx + 1 < len(cells)
                    and cells[idx + 1] == str(count)
                    for idx, cell in enumerate(cells)
                )
            else:
                found |= bool(re.search(rf"(?<![\d.]){count}(?![\d.])", line.replace(sf.stem, "")))
        if not found:
            problems.append(f"{sf.stem}: the report does not give {count} questions for this file")
    if not any(re.search(rf"(?<!\d){total}(?!\d)", line) for line in lines):
        problems.append(f"the report does not state the total of {total} questions")
    assert not problems, "\n".join(problems)


def _report_section(heading_word: str) -> list[str]:
    """The lines under the first heading (any level) that contains `heading_word`."""
    lines = REPORT_FILE.read_text(encoding="utf-8").splitlines()
    start = next(
        (i for i, line in enumerate(lines) if line.startswith("#") and heading_word in line), None
    )
    assert start is not None, f"the report has no heading containing {heading_word!r}"
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    out: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("#") and len(line) - len(line.lstrip("#")) <= level:
            break
        out.append(line)
    return out


def _table_first_cells(lines: Sequence[str]) -> list[str]:
    cells = [split_row(line) for line in lines if line.startswith("|")]
    return [row[0].strip("`") for row in cells[2:]]  # header and separator skipped


def test_report_lists_every_question_with_its_rule_filled_values() -> None:
    assert REPORT_FILE.is_file(), "content/pilot/CONVERSION_REPORT.md does not exist"
    section = _report_section("Soru soru")
    rows = {split_row(line)[0].strip("`"): line for line in section if line.startswith("| `")}
    assert sorted(rows) == sorted(q.ref for q in QUESTIONS), (
        "the per-question table does not list exactly the 130 questions"
    )
    problems: list[str] = []
    for src in QUESTIONS:
        doc = converted(src).document
        row = rows[src.ref]
        if doc.mcq is not None:
            if doc.mcq.option_kind.value not in row:
                problems.append(
                    f"{src.ref}: option_kind {doc.mcq.option_kind.value} not in its row"
                )
        else:
            for part in doc.parts:
                if part.answer_type.value not in row:
                    problems.append(f"{src.ref}: answer_type of part {part.label} not in its row")
    assert not problems, "\n".join(problems)


def test_report_stimulus_table_matches_the_stimuli_in_the_json() -> None:
    assert REPORT_FILE.is_file(), "content/pilot/CONVERSION_REPORT.md does not exist"
    section = _report_section("Uyaranlar")
    table = [split_row(line) for line in section if line.startswith("|")][2:]
    reported = {(row[0].strip("`"), row[1].strip("`")): row[2].strip("`") for row in table}
    assert len(table) == 28 == len(reported)
    actual = {
        (q.ref, stimulus.id): stimulus.kind.value
        for q in QUESTIONS
        for stimulus in converted(q).document.stimuli
    }
    assert reported == actual
