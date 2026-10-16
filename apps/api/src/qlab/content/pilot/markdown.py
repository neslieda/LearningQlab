r"""Rule-based conversion of a pilot question file (Markdown) to a `PilotFile`.

Specification: docs/pilot/IMPORT_RULES.md; source format: docs/pilot/AUTHORING_STANDARD.md.

The conversion is deterministic and never guesses: where a rule does not cover the input it
raises `ConversionError` with the file, the question number and the line. Everything here is a
pure function of the Markdown text, the file stem and the syllabus vocabulary; the counters that
feed content/pilot/CONVERSION_REPORT.md are collected in a `Tally` that the caller owns.

Inline markup (IMPORT_RULES section 4) is scanned left to right: `**` toggles bold, `*...*` pairs
with the next `*`, `«` and `»` toggle the optional mark. A `*` that cannot be paired, an italic
span that begins or ends with a space, a backtick outside a formula chain and an unknown italic
token are errors. Two closed lists (`VARIABLE_WORDS`, `ITALIC_WORDS`) decide the italic tokens
that rules 1 and 2 of section 4.2 do not settle; tokens that are not examples in the
specification are marked as additions and listed in the report.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Literal

from pydantic import ValidationError

from qlab.content.math import ALLOWED_COMMANDS, disallowed
from qlab.content.pilot.model import PilotFile, PilotQuestion, source_ref
from qlab.content.schema import (
    AnswerType,
    Cell,
    Difficulty,
    Doc,
    Figure,
    FigureAttrs,
    HardBreak,
    Inline,
    Level,
    LevelContent,
    Mark,
    MarkPoint,
    MarkPointKind,
    MarkType,
    MathAttrs,
    MathInline,
    Mcq,
    McqOption,
    Note,
    NoteKind,
    OptionKind,
    OptionLayout,
    Paragraph,
    Parameter,
    Part,
    QuestionClass,
    QuestionDocument,
    SolutionModel,
    Step,
    Stimulus,
    StimulusKind,
    StimulusUse,
    Table,
    TableCell,
    TableHeader,
    TableRow,
    Text,
)
from qlab.content.schema.blocks import NUMBER_PATTERN, UNIT_PATTERN, Block

SOURCE_SUFFIX = "-pilot-questions.md"

# --- Closed lists (IMPORT_RULES 4.2) -------------------------------------------------------
# Tokens named as examples in the specification; everything else below them is an addition and
# is reported as such ("Kural ekleri").
SPEC_VARIABLE_WORDS = frozenset({"mv", "mg", "ct", "hf", "gt", "vx", "vt", "mr"})
SPEC_ITALIC_WORDS = frozenset(
    {"not", "one", "two", "twice", "into", "on", "out of", "parallel", "one eighth"}
)
# Lower-case multi-letter symbols that are products of single-letter variables.
VARIABLE_WORDS = SPEC_VARIABLE_WORDS | frozenset({"gh", "gr", "hc", "kx", "mc", "mgv", "mx"})
# Words and short phrases set in italics for emphasis or as mark-scheme wording.
ITALIC_WORDS = SPEC_ITALIC_WORDS | frozenset({"Accept", "Allow", "and", "OWTTE"})

_SENTENCE_PUNCTUATION = frozenset(".,;:!?'\"()[]")

# --- Mappings (IMPORT_RULES 3 and 5) -------------------------------------------------------
_DIFFICULTY = {
    "Easy": Difficulty.EASY,
    "Easy–medium": Difficulty.MEDIUM,
    "Medium": Difficulty.MEDIUM,
    "Medium–hard": Difficulty.HARD,
    "Hard": Difficulty.HARD,
}
_SECTION_CODES = {"1A": "paper_1a", "1B": "paper_1b", "2": "paper_2"}
_ANSWER_TYPES: dict[str, AnswerType] = {
    **dict.fromkeys(("calculate", "determine", "estimate"), AnswerType.NUMERIC_WITH_UNIT),
    **dict.fromkeys(("state", "identify"), AnswerType.WORD_PHRASE),
    "show": AnswerType.DERIVATION_NUMERIC,
    **dict.fromkeys(
        ("explain", "outline", "describe", "suggest", "predict", "deduce"),
        AnswerType.EXPLANATION,
    ),
    **dict.fromkeys(("discuss", "analyse"), AnswerType.EXTENDED_EVALUATION),
    **dict.fromkeys(("draw", "annotate", "complete"), AnswerType.DRAWING_ON_DIAGRAM),
    "sketch": AnswerType.GRAPH_SKETCH,
}
# Staff-only figure descriptions: the keyword found earliest in the text decides the kind.
# Matching is case-insensitive and starts at a word start (`ray` is not found in `array`).
_STIMULUS_KEYWORDS: tuple[tuple[str, StimulusKind], ...] = (
    ("circuit", StimulusKind.CIRCUIT_DIAGRAM),
    ("resistor", StimulusKind.CIRCUIT_DIAGRAM),
    ("battery", StimulusKind.CIRCUIT_DIAGRAM),
    ("cell", StimulusKind.CIRCUIT_DIAGRAM),
    ("voltmeter", StimulusKind.CIRCUIT_DIAGRAM),
    ("ammeter", StimulusKind.CIRCUIT_DIAGRAM),
    ("graph", StimulusKind.GRAPH),
    ("axis", StimulusKind.GRAPH),
    ("axes", StimulusKind.GRAPH),
    ("p–v", StimulusKind.GRAPH),
    ("field line", StimulusKind.FIELD_DIAGRAM),
    ("ray", StimulusKind.RAY_WAVEFRONT_DIAGRAM),
    ("wavefront", StimulusKind.RAY_WAVEFRONT_DIAGRAM),
    ("energy level", StimulusKind.ENERGY_LEVEL_DIAGRAM),
    ("spacetime", StimulusKind.SPACETIME_DIAGRAM),
    ("space-time", StimulusKind.SPACETIME_DIAGRAM),
    ("table", StimulusKind.DATA_TABLE),
)
FIGURE_NOTE_DESCRIPTION = (
    "Graph to be generated from data; details in the Figure note of the source file."
)
MAX_FILE_BYTES = 1_048_576
MAX_LINE_CHARS = 20_000
MAX_DIGITS = 4
_MARK_ORDER = (
    MarkType.BOLD,
    MarkType.ITALIC,
    MarkType.SUB,
    MarkType.SUP,
    MarkType.OPTIONAL,
    MarkType.ESSENTIAL,
)
_SUPERSCRIPTS = str.maketrans("⁻⁺⁰¹²³⁴⁵⁶⁷⁸⁹", "-+0123456789")
_SUPERSCRIPT_CHARS = "⁻⁺⁰¹²³⁴⁵⁶⁷⁸⁹"
_KNOWN_SECTION_TITLES = (
    "Scope table",
    "Format conformance",
    "Independent check",
    "Observations from this trial",
)
_ROMAN = ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")

# Rule additions beyond the text of IMPORT_RULES.md, keyed by id; the report prints them with
# the places where they were needed.
ADDITIONS: dict[str, str] = {
    "note-italic": (
        "Notlarda tüm metin düğümlerinden `italic` işareti atılır (not satırının tamamı italik "
        "yazılır; satır `*Accept* Δ*U* = … *for the second mark.*` gibi bölünmüşse de)."
    ),
    "ecf-prefix": (
        "`Allow ECF` ile başlayan her not `ecf` olur (`Allow ECF from (b)…` kalıbının dışındaki "
        "`Allow ECF for the volume from (a).`, `Allow ECF from an incorrect T in (b).`); "
        "`ecf_from` notun içindeki `(x)` / `(x)(y)` başvurularından kurulur."
    ),
    "total-max": (
        "Markscheme `Total` hücresi `n` ya da `n max` olabilir (`2 max`); sayı parça puanına eşit "
        "olmalıdır."
    ),
    "mcq-trailing-note": (
        "Çoktan seçmelide yanılgı tablosundan sonra gelen serbest paragraflar (`Note: …`) "
        "aktarılmaz, raporda sayılır."
    ),
    "italic-word": "Kapalı italik sözcük listesine eklenen belirteçler (aşağıda).",
    "variable-word": "Kapalı değişken listesine eklenen belirteçler (aşağıda).",
}


class ConversionError(Exception):
    """A place the rules do not cover. Carries where it happened; the message says what."""

    def __init__(self, file: str, question: int | None, line: int | None, message: str) -> None:
        self.file = file
        self.question = question
        self.line = line
        self.message = message
        super().__init__(str(self))

    def __str__(self) -> str:
        where = self.file
        if self.question is not None:
            where += f", question {self.question}"
        if self.line is not None:
            where += f", line {self.line}"
        return f"{where}: {self.message}"


class ConversionFailed(ConversionError):
    """Raised by `convert_markdown` after all questions were tried; `errors` has every failure."""

    def __init__(self, errors: Sequence[ConversionError]) -> None:
        first = errors[0]
        self.errors = tuple(errors)
        super().__init__(first.file, first.question, first.line, first.message)

    def __str__(self) -> str:
        return "\n".join(str(error) for error in self.errors)


@dataclass
class ItalicUse:
    kind: Literal["variable", "italic"]
    rule: str
    count: int = 0
    first: str = ""


@dataclass
class Tally:
    """Everything the report counts. Owned by the caller, filled during the conversion."""

    italics: dict[str, ItalicUse] = field(default_factory=dict)
    counters: dict[str, Counter[str]] = field(default_factory=dict)
    models_imported: list[str] = field(default_factory=list)
    models_omitted: list[tuple[str, str, str]] = field(default_factory=list)
    free_paragraphs: list[tuple[str, int]] = field(default_factory=list)
    constants: list[tuple[str, str]] = field(default_factory=list)
    additions: dict[str, list[str]] = field(default_factory=dict)
    file_counts: dict[str, Counter[str]] = field(default_factory=dict)
    figure_notes_skipped: list[str] = field(default_factory=list)
    # (ref, stimulus id, kind, source) of every stimulus
    stimuli: list[tuple[str, str, str, str]] = field(default_factory=list)
    # (ref, class, option_kind or "", ((label, command term or "", answer type), ...))
    question_fields: list[tuple[str, str, str, tuple[tuple[str, str, str], ...]]] = field(
        default_factory=list
    )
    # (ref, steps without a unit, steps) of every imported solution model
    step_units: list[tuple[str, int, int]] = field(default_factory=list)

    def count(self, category: str, value: str) -> None:
        self.counters.setdefault(category, Counter())[value] += 1


@dataclass(frozen=True)
class Env:
    """Where we are, for error messages and the tally."""

    stem: str
    tally: Tally
    question: int | None = None
    line: int | None = None

    @property
    def file(self) -> str:
        return f"docs/pilot/{self.stem}{SOURCE_SUFFIX}"

    @property
    def ref(self) -> str:
        return source_ref(self.stem, self.question) if self.question else f"pilot/{self.stem}"

    def at(self, line: int | None) -> Env:
        return replace(self, line=line)

    def fail(self, message: str) -> ConversionError:
        return ConversionError(self.file, self.question, self.line, message)

    def add(self, key: str, detail: str | None = None) -> None:
        places = self.tally.additions.setdefault(key, [])
        entry = detail if detail is not None else self.ref
        if entry not in places:
            places.append(entry)


@dataclass(frozen=True)
class Vocabulary:
    nodes: frozenset[str]
    sections: frozenset[str]
    command_terms: frozenset[str]


def load_vocabulary(path: Path) -> Vocabulary:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Vocabulary(
        nodes=frozenset(node["code"] for node in data["nodes"]),
        sections=frozenset(section["code"] for section in data["exam_format"]["sections"]),
        command_terms=frozenset(data["exam_format"]["command_terms"]),
    )


# --- Inline text ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Span:
    """One inline piece. `plain` is the visible source text (variables as written)."""

    kind: Literal["text", "math", "break"]
    value: str
    plain: str
    marks: frozenset[MarkType] = frozenset()


@dataclass(frozen=True)
class Classification:
    kind: Literal["variable", "italic"]
    rule: str


def greek_command(char: str) -> str | None:
    """The LaTeX command name of a Greek letter, if the closed math list allows it."""
    if char == "µ":  # micro sign
        char = "μ"
    elif char == "Ω":  # ohm sign
        char = "Ω"
    found = re.fullmatch(r"GREEK (SMALL|CAPITAL) LETTER ([A-Z]+)", unicodedata.name(char, ""))
    if found is None:
        return None
    word = found.group(2).lower().replace("lamda", "lambda")
    name = word if found.group(1) == "SMALL" else word.capitalize()
    return name if name in ALLOWED_COMMANDS else None


_LATEX_SPECIALS = frozenset("\\{}%&#_^$~")


def to_latex(source: str, env: Env) -> str:
    r"""ASCII LaTeX for a run of variable or subscript text (IMPORT_RULES 4.3).

    Latin letters, digits and plain ASCII punctuation pass through; Greek letters become commands
    with a space before a following letter (`Iω` -> `I\omega`, `ωt` -> `\omega t`).
    """
    out: list[str] = []
    for index, char in enumerate(source):
        command = greek_command(char)
        if command is not None:
            out.append("\\" + command)
            following = source[index + 1 : index + 2]
            if following.isascii() and following.isalpha():
                out.append(" ")
        elif 32 <= ord(char) < 127 and char not in _LATEX_SPECIALS:
            out.append(char)
        else:
            raise env.fail(f"character {char!r} (U+{ord(char):04X}) cannot be written in math")
    return "".join(out)


def classify_italic(token: str, env: Env) -> Classification:
    """Section 4.2: variable or italic text; unknown tokens raise `ConversionError`."""
    if len(token) == 1 and token.isalpha():
        return Classification("variable", "1")
    letters = token.isalpha()
    if letters and len(token) <= 4 and any(c.isupper() or "Ͱ" <= c < "Ѐ" for c in token):
        return Classification("variable", "2")
    if token in VARIABLE_WORDS:
        return Classification("variable", "3")
    if token in ITALIC_WORDS:
        return Classification("italic", "4-word")
    if any(c.isspace() or c in _SENTENCE_PUNCTUATION for c in token):
        return Classification("italic", "4-phrase")
    raise env.fail(
        f"italic token {token!r} is not a variable (rules 1-3) nor on the closed word list "
        "nor a phrase (rule 4); add it to the right list or fix the Markdown"
    )


def _note_token(token: str, classification: Classification, env: Env) -> None:
    use = env.tally.italics.setdefault(token, ItalicUse(classification.kind, classification.rule))
    use.count += 1
    if not use.first:
        use.first = env.ref


@dataclass
class _State:
    bold: bool = False
    optional: bool = False


def _marks(state: _State, *extra: MarkType) -> frozenset[MarkType]:
    marks = set(extra)
    if state.bold:
        marks.add(MarkType.BOLD)
    if state.optional:
        marks.add(MarkType.OPTIONAL)
    return frozenset(marks)


def _math_span(latex: str, plain: str, marks: frozenset[MarkType], env: Env) -> Span:
    refused = disallowed(latex)
    if refused:
        raise env.fail(f"math `{latex}` is not allowed: {', '.join(refused)}")
    return Span("math", latex, plain, marks)


def _require_closed(state: _State, text: str, env: Env) -> None:
    if state.bold:
        raise env.fail(f"unclosed ** in {_quote(text)}")
    if state.optional:
        raise env.fail(f"unclosed « in {_quote(text)}")


def _fragment(content: str, env: Env) -> tuple[str, str]:
    """LaTeX and visible text of a sub/superscript that belongs to a variable."""
    state = _State()
    spans = _scan(content, state, env)
    _require_closed(state, content, env)
    parts: list[str] = []
    plain: list[str] = []
    for span in spans:
        if span.kind == "break" or span.marks:
            raise env.fail(f"<sub>/<sup> content {content!r} has markup that math cannot carry")
        parts.append(to_latex(span.value, env) if span.kind == "text" else span.value)
        plain.append(span.plain)
    latex = "".join(parts)
    if not latex.strip():
        raise env.fail("empty <sub>/<sup>")
    return latex, "".join(plain)


def _scan(text: str, state: _State, env: Env, *, italic: bool = False) -> list[Span]:
    spans: list[Span] = []
    buffer: list[str] = []
    attach_at = -1  # index just after the last variable's closing `*`
    marks_extra: tuple[MarkType, ...] = (MarkType.ITALIC,) if italic else ()

    def flush() -> None:
        if buffer:
            value = "".join(buffer)
            spans.append(Span("text", value, value, _marks(state, *marks_extra)))
            buffer.clear()

    i = 0
    while i < len(text):
        char = text[i]
        if text.startswith("**", i):
            if italic:
                raise env.fail("bold inside an italic span")
            flush()
            state.bold = not state.bold
            i += 2
        elif char == "*":
            if italic:
                raise env.fail("unpaired `*` inside an italic span")
            end = text.find("*", i + 1)
            if end < 0:
                raise env.fail(f"unpaired `*` at column {i + 1} of {_quote(text)}")
            if text.startswith("*", end + 1):
                raise env.fail(f"ambiguous `**` after italic span in {_quote(text)}")
            token = text[i + 1 : end]
            if not token or token[0].isspace() or token[-1].isspace():
                raise env.fail(f"italic span {token!r} starts or ends with a space (unpaired `*`?)")
            flush()
            classification = classify_italic(token, env)
            _note_token(token, classification, env)
            if classification.kind == "variable":
                spans.append(
                    _math_span(to_latex(token, env), token, _marks(state), env),
                )
                attach_at = end + 1
            else:
                spans.extend(_scan(token, state, env, italic=True))
            i = end + 1
        elif text.startswith("<br>", i):
            flush()
            spans.append(Span("break", "", " ", frozenset()))
            i += 4
        elif text.startswith(("<sub>", "<sup>"), i):
            tag = text[i + 1 : i + 4]
            close = text.find(f"</{tag}>", i)
            if close < 0:
                raise env.fail(f"<{tag}> without a closing tag")
            content = text[i + 5 : close]
            flush()
            if i == attach_at and spans and spans[-1].kind == "math":
                base = spans[-1]
                latex, plain = _fragment(content, env)
                operator = "_" if tag == "sub" else "^"
                if f"{operator}{{" in base.value:
                    raise env.fail(f"two <{tag}> on one variable ({base.plain!r})")
                spans[-1] = _math_span(
                    f"{base.value}{operator}{{{latex}}}", base.plain + plain, base.marks, env
                )
                attach_at = close + 6
            else:
                inner_state = _State()
                inner = _scan(content, inner_state, env)
                _require_closed(inner_state, content, env)
                mark = MarkType.SUB if tag == "sub" else MarkType.SUP
                for piece in inner:
                    if piece.kind != "text":
                        raise env.fail(f"<{tag}> content must be plain text: {content!r}")
                    spans.append(
                        Span("text", piece.value, piece.value, piece.marks | _marks(state, mark))
                    )
            i = close + 6
        elif char == "«":
            if state.optional:
                raise env.fail("nested « »")
            flush()
            state.optional = True
            i += 1
        elif char == "»":
            if not state.optional:
                raise env.fail("» without «")
            flush()
            state.optional = False
            i += 1
        elif char == "`":
            raise env.fail("backtick outside a formula chain")
        else:
            buffer.append(char)
            i += 1
    flush()
    return spans


def _quote(text: str, limit: int = 70) -> str:
    return repr(text if len(text) <= limit else text[: limit - 3] + "...")


def parse_inline(text: str, env: Env, *, ticks: bool = False) -> list[Span]:
    """Section 4.1: inline spans of one paragraph (or table cell, mark point, note).

    A `✓` is only expected in the mark-scheme columns; `ticks=True` lets it through (notes).
    """
    if "✓" in text and not ticks:
        raise env.fail(f"✓ outside a mark-scheme cell: {_quote(text)}")
    collapsed = re.sub(r"\s+", " ", text)
    state = _State()
    spans = _scan(collapsed, state, env)
    _require_closed(state, text, env)
    return _tidy(spans)


def _tidy(spans: list[Span]) -> list[Span]:
    """Merge neighbouring text spans with equal marks; trim spaces at the edges and at breaks."""
    merged: list[Span] = []
    for span in spans:
        last = merged[-1] if merged else None
        if (
            last is not None
            and span.kind == "text"
            and last.kind == "text"
            and last.marks == span.marks
        ):
            merged[-1] = Span("text", last.value + span.value, last.plain + span.plain, span.marks)
        else:
            merged.append(span)
    for index, span in enumerate(merged):
        if span.kind != "text":
            continue
        value = span.value
        before_edge = index == 0 or merged[index - 1].kind == "break"
        after_edge = index == len(merged) - 1 or merged[index + 1].kind == "break"
        if before_edge:
            value = value.lstrip()
        if after_edge:
            value = value.rstrip()
        merged[index] = Span("text", value, value, span.marks)
    return [s for s in merged if s.kind != "text" or s.value]


def plain_text(spans: Iterable[Span]) -> str:
    return "".join(span.plain for span in spans)


def _mark_nodes(marks: frozenset[MarkType]) -> tuple[Mark, ...]:
    return tuple(Mark(type=m) for m in _MARK_ORDER if m in marks)


def inline_nodes(spans: Iterable[Span]) -> tuple[Inline, ...]:
    nodes: list[Inline] = []
    for span in spans:
        if span.kind == "text":
            nodes.append(Text(type="text", text=span.value, marks=_mark_nodes(span.marks)))
        elif span.kind == "math":
            nodes.append(
                MathInline(
                    type="math_inline",
                    attrs=MathAttrs(latex=span.value),
                    marks=_mark_nodes(span.marks),
                )
            )
        else:
            nodes.append(HardBreak(type="hard_break"))
    return tuple(nodes)


def paragraph_of(spans: Iterable[Span]) -> Paragraph:
    return Paragraph(type="paragraph", content=inline_nodes(spans))


def doc_of(blocks: Sequence[Block], env: Env) -> Doc:
    if not blocks:
        raise env.fail("empty document")
    return Doc(type="doc", content=tuple(blocks))


def doc_from_text(text: str, env: Env) -> Doc:
    return doc_of([paragraph_of(parse_inline(text, env))], env)


# --- Block structure -----------------------------------------------------------------------


@dataclass(frozen=True)
class Line:
    no: int
    text: str


@dataclass(frozen=True)
class SourceBlock:
    kind: Literal["para", "quote", "table"]
    lines: tuple[Line, ...]

    @property
    def first(self) -> int:
        return self.lines[0].no


_PART_START = re.compile(r"^\*\*\(([a-z])\)\*\*")


def split_blocks(lines: Sequence[Line]) -> list[SourceBlock]:
    """Paragraphs, quotes and tables, separated by blank lines (a part line starts a block)."""
    blocks: list[SourceBlock] = []
    current: list[Line] = []
    kind: Literal["para", "quote", "table"] = "para"

    def flush() -> None:
        if current:
            blocks.append(SourceBlock(kind, tuple(current)))
            current.clear()

    for line in lines:
        stripped = line.text.strip()
        if not stripped:
            flush()
            continue
        if stripped.startswith(">"):
            line_kind: Literal["para", "quote", "table"] = "quote"
        elif stripped.startswith("|"):
            line_kind = "table"
        else:
            line_kind = "para"
        if line_kind != kind or (line_kind == "para" and _PART_START.match(stripped)):
            flush()
        kind = line_kind
        current.append(Line(line.no, stripped if line_kind != "para" else line.text))
    flush()
    return blocks


def split_row(line: Line, env: Env) -> list[str]:
    text = line.text.strip()
    if not (text.startswith("|") and text.endswith("|")):
        raise env.at(line.no).fail("table row must start and end with `|`")
    if "\\|" in text:
        raise env.at(line.no).fail("escaped pipe in a table row")
    return [cell.strip() for cell in text[1:-1].split("|")]


def _is_separator(cells: Sequence[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", c) for c in cells)


def table_rows(block: SourceBlock, env: Env) -> list[tuple[int, list[str]]]:
    """Rows of a Markdown table without the separator row."""
    rows: list[tuple[int, list[str]]] = []
    for line in block.lines:
        cells = split_row(line, env)
        if not _is_separator(cells):
            rows.append((line.no, cells))
    if not rows:
        raise env.at(block.first).fail("table without a header row")
    return rows


def table_node(block: SourceBlock, env: Env) -> Table:
    rows = table_rows(block, env)
    out: list[TableRow] = []
    width = len(rows[0][1])
    for index, (no, cells) in enumerate(rows):
        if len(cells) != width:
            raise env.at(no).fail(f"table row has {len(cells)} cells, expected {width}")
        nodes: list[Cell] = []
        for cell in cells:
            paragraph = paragraph_of(parse_inline(cell, env.at(no)))
            if index == 0:
                nodes.append(TableHeader(type="table_header", content=(paragraph,)))
            else:
                nodes.append(TableCell(type="table_cell", content=(paragraph,)))
        out.append(TableRow(type="table_row", content=tuple(nodes)))
    return Table(type="table", content=tuple(out))


def _joined(block: SourceBlock) -> str:
    return " ".join(line.text.strip() for line in block.lines)


# --- Stimuli -------------------------------------------------------------------------------


def stimulus_kind(description: str) -> StimulusKind:
    """Section 3.3: the kind from the keyword that occurs first, as a whole word (a plural `s` or
    `es` is allowed: "graphs", but not "graphite")."""
    lowered = description.casefold()
    best: tuple[int, StimulusKind] | None = None
    for keyword, kind in _STIMULUS_KEYWORDS:
        found = re.search(rf"(?<![^\W\d_]){re.escape(keyword)}(?:e?s)?(?![^\W\d_])", lowered)
        if found is not None and (best is None or found.start() < best[0]):
            best = (found.start(), kind)
    return best[1] if best is not None else StimulusKind.SCHEMATIC_DIAGRAM


_FIGURE_LABEL = re.compile(r"^>\s*\*\*Figure:\*\*\s*")


def figure_block(block: SourceBlock, stimuli: list[Stimulus], env: Env) -> Figure:
    """A `> **Figure:** …` quote: a stimulus (fig1, fig2, …) and its placement."""
    env = env.at(block.first)
    parts: list[str] = []
    for index, line in enumerate(block.lines):
        text = line.text.strip()
        if index == 0:
            if not _FIGURE_LABEL.match(text):
                raise env.fail("a quote block must start with `> **Figure:**`")
            text = _FIGURE_LABEL.sub("", text)
        elif text.startswith(">"):
            text = text[1:].strip()
        parts.append(text)
    description = plain_text(parse_inline(" ".join(parts), env))
    stimulus_id = f"fig{len(stimuli) + 1}"
    stimuli.append(
        Stimulus(
            id=stimulus_id,
            kind=stimulus_kind(description),
            use=StimulusUse.READ_ONLY,
            description=description,
        )
    )
    env.tally.stimuli.append((env.ref, stimulus_id, stimuli[-1].kind.value, "Figure block"))
    env.tally.count("stimulus_kind", stimuli[-1].kind.value)
    return Figure(type="figure", attrs=FigureAttrs(stimulus_id=stimulus_id))


def content_blocks(blocks: Sequence[SourceBlock], stimuli: list[Stimulus], env: Env) -> list[Block]:
    """Paragraphs, tables and figures of a stem, lead-in or explanation, in order."""
    out: list[Block] = []
    for block in blocks:
        local = env.at(block.first)
        if block.kind == "para":
            out.append(paragraph_of(parse_inline(_joined(block), local)))
        elif block.kind == "table":
            out.append(table_node(block, local))
        else:
            out.append(figure_block(block, stimuli, local))
    return out


# --- File structure ------------------------------------------------------------------------


@dataclass(frozen=True)
class ScopeRow:
    number: int
    section: str
    level: str
    outcome: str
    objective: str
    marks: int
    difficulty: str
    line: int


@dataclass(frozen=True)
class Heading:
    number: int
    section: str  # "1A", "1B", "2"
    marks: int | None
    hl: bool
    line: int


_HEADING = re.compile(
    r"^## Question ([0-9]{1,4}) — Paper (1A|1B|2)"
    r"(?: \((?:(HL), )?([0-9]{1,4}) marks\)| \((HL)\))?$"
)


def small_int(text: str) -> int | None:
    """An unsigned integer of at most MAX_DIGITS ASCII digits, else None."""
    if re.fullmatch(rf"[0-9]{{1,{MAX_DIGITS}}}", text) is None:
        return None
    return int(text)


_SCOPE_HEADER = (
    "#",
    "Section",
    "Level",
    "Outcome",
    "Objective",
    "Command terms",
    "Marks",
    "Difficulty",
)


def parse_heading(line: Line, env: Env) -> Heading:
    found = _HEADING.match(line.text)
    if found is None:
        raise env.at(line.no).fail(f"unrecognised question heading {line.text!r}")
    number, section, hl_marks, marks, hl_only = found.groups()
    if (section == "1A") != (marks is None):
        raise env.at(line.no).fail("heading marks: required for Paper 1B and 2, absent for 1A")
    return Heading(
        number=int(number),
        section=section,
        marks=int(marks) if marks is not None else None,
        hl=bool(hl_marks or hl_only),
        line=line.no,
    )


def parse_scope(lines: Sequence[Line], env: Env) -> dict[int, ScopeRow]:
    rows: dict[int, ScopeRow] = {}
    table = [line for line in lines if line.text.strip().startswith("|")]
    if not table:
        raise env.fail("no scope table (`## Scope table`)")
    header = split_row(table[0], env)
    if len(header) != 8 or tuple(cell.split(" (")[0] for cell in header) != _SCOPE_HEADER:
        raise env.at(table[0].no).fail(f"unexpected scope table header {header}")
    for line in table[1:]:
        cells = split_row(line, env)
        if _is_separator(cells):
            continue
        number, marks = (
            (small_int(cells[0]), small_int(cells[6])) if len(cells) == 8 else (None,) * 2
        )
        if number is None or marks is None:
            raise env.at(line.no).fail(f"unexpected scope table row {cells}")
        if number in rows:
            raise env.at(line.no).fail(f"question {number} appears twice in the scope table")
        rows[number] = ScopeRow(
            number, cells[1], cells[2], cells[3], cells[4], marks, cells[7], line.no
        )
    return rows


def _split_sections(lines: Sequence[Line], env: Env) -> tuple[list[Line], dict[str, list[Line]]]:
    """Lines before the first `###` heading, and the lines of each `###` section."""
    main: list[Line] = []
    sections: dict[str, list[Line]] = {}
    current = main
    for line in lines:
        if line.text.startswith("### "):
            title = line.text[4:].strip()
            if title in sections:
                raise env.at(line.no).fail(f"section {title!r} appears twice")
            sections[title] = []
            current = sections[title]
        else:
            current.append(line)
    return main, sections


# --- Multiple choice -----------------------------------------------------------------------

_NUMBER = r"[-−+]?\d+(?:\.\d+)?(?:\s*×\s*10[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)?"
_UNIT_WORD = r"[A-Za-zµμΩ°%][A-Za-zµμΩ°%/·⁻⁰¹²³⁴⁵⁶⁷⁸⁹]*"
_NUMERIC_WITH_UNIT = re.compile(rf"^{_NUMBER}\s*{_UNIT_WORD}(?: {_UNIT_WORD}){{0,3}}$")
_RATIO = re.compile(rf"^{_NUMBER}(?:\s*[:/⁄÷]\s*{_NUMBER})?$")


def option_kind(options: Sequence[Sequence[Span]]) -> OptionKind:
    """IMPORT_RULES section 5: the kind of the four options, from their visible text."""
    texts = [plain_text(spans).strip() for spans in options]
    has_math = [any(s.kind == "math" for s in spans) for spans in options]
    if not any(has_math):
        if all(_NUMERIC_WITH_UNIT.match(t) and not _RATIO.match(t) for t in texts):
            return OptionKind.NUMERIC_WITH_UNIT
        if all(_RATIO.match(t) for t in texts):
            return OptionKind.RATIO
    if any(has_math):
        return OptionKind.ALGEBRAIC_EXPRESSION
    if all(len(t.split()) <= 4 for t in texts):
        return OptionKind.WORD_PHRASE
    return OptionKind.STATEMENT


def convert_mcq(
    blocks: Sequence[SourceBlock],
    heading: Heading,
    scope: ScopeRow,
    node: str,
    hl: bool,
    env: Env,
    stimuli: list[Stimulus],
) -> tuple[Doc, Mcq]:
    index = next(
        (
            i
            for i, b in enumerate(blocks)
            if b.kind == "para" and re.match(r"A\. ", b.lines[0].text.strip())
        ),
        None,
    )
    if index is None:
        raise env.at(heading.line).fail("no option block (`A. …`)")
    if index == 0:
        raise env.at(blocks[0].first).fail("a multiple-choice question needs a stem before A.")
    stem = doc_of(content_blocks(blocks[:index], stimuli, env), env)

    option_block = blocks[index]
    option_spans: list[list[Span]] = []
    for offset, key in enumerate("ABCD"):
        if offset >= len(option_block.lines):
            raise env.at(option_block.first).fail(f"option {key} is missing")
        line = option_block.lines[offset]
        text = line.text.strip()
        if not text.startswith(f"{key}. "):
            raise env.at(line.no).fail(f"expected option {key}., found {text[:30]!r}")
        option_spans.append(parse_inline(text[3:], env.at(line.no)))
    if len(option_block.lines) != 4:
        raise env.at(option_block.lines[4].no).fail("more than four option lines")

    rest = blocks[index + 1 :]
    if not rest or rest[0].kind != "para":
        raise env.at(option_block.first).fail("`**Answer: X**` is missing after the options")
    answer = _joined(rest[0])
    found = re.fullmatch(r"\*\*Answer: ([A-D])\*\*", answer)
    if found is None:
        raise env.at(rest[0].first).fail(f"expected `**Answer: X**`, found {answer[:40]!r}")
    correct = found.group(1)

    table_at = next((i for i, b in enumerate(rest) if b.kind == "table"), None)
    if table_at is None or table_at < 2:
        raise env.at(rest[0].first).fail("missing `**Solution.**` text or the misconception table")
    explanation_blocks = rest[1:table_at]
    first_text = _joined(explanation_blocks[0])
    if not first_text.startswith("**Solution.**"):
        raise env.at(explanation_blocks[0].first).fail(
            "explanation must start with `**Solution.**`"
        )
    if any(b.kind != "para" for b in explanation_blocks):
        raise env.at(explanation_blocks[0].first).fail("explanation may only hold paragraphs")
    trailing = rest[table_at + 1 :]
    if any(b.kind != "para" for b in trailing):
        raise env.at(trailing[0].first).fail("unexpected quote or table after the table")
    if trailing:
        env.add("mcq-trailing-note")
        env.tally.free_paragraphs.append((env.ref, len(trailing)))
    explanation_paragraphs = [
        paragraph_of(parse_inline(_joined(b).removeprefix("**Solution.**"), env.at(b.first)))
        if i == 0
        else paragraph_of(parse_inline(_joined(b), env.at(b.first)))
        for i, b in enumerate(explanation_blocks)
    ]
    explanation = doc_of(explanation_paragraphs, env)

    rows = table_rows(rest[table_at], env)
    if [c for c in rows[0][1]] != ["Option", "Misconception"]:
        raise env.at(rows[0][0]).fail(f"unexpected misconception table header {rows[0][1]}")
    rationales: dict[str, Doc] = {}
    for no, cells in rows[1:]:
        if len(cells) != 2 or cells[0] not in "ABCD" or len(cells[0]) != 1:
            raise env.at(no).fail(f"unexpected misconception row {cells}")
        if cells[0] == correct:
            raise env.at(no).fail("misconception row for the correct option")
        if cells[0] in rationales:
            raise env.at(no).fail(f"duplicate misconception row for {cells[0]}")
        rationales[cells[0]] = doc_from_text(cells[1], env.at(no))
    missing = [k for k in "ABCD" if k != correct and k not in rationales]
    if missing:
        raise env.at(rest[table_at].first).fail(f"no misconception row for {', '.join(missing)}")

    kind = option_kind(option_spans)
    env.tally.count("option_kind", kind.value)
    env.tally.question_fields.append((env.ref, "mcq", kind.value, ()))
    objective = None
    match = re.fullmatch(r"AO([123])", scope.objective)
    if match is not None:
        objective = int(match.group(1))
    options = tuple(
        McqOption(
            key=key,  # type: ignore[arg-type]
            cells=(doc_of([paragraph_of(spans)], env),),
            rationale=rationales.get(key),
        )
        for key, spans in zip("ABCD", option_spans, strict=True)
    )
    mcq = Mcq(
        option_kind=kind,
        option_layout=OptionLayout.SINGLE_VALUE,
        options=options,
        correct_key=correct,  # type: ignore[arg-type]
        explanation=explanation,
        assessment_objective=objective,  # type: ignore[arg-type]
        level_content=LevelContent.AHL if hl else LevelContent.SL_CORE,
    )
    return stem, mcq


# --- Structured and data-based -------------------------------------------------------------

_PART_LINE = re.compile(r"^\*\*\(([a-z])\)\*\*\s*(?:\(([ivx]+)\)\s+)?(.+)$", re.DOTALL)
_SUBPART_LINE = re.compile(r"^\(([ivx]+)\)\s+(.+)$", re.DOTALL)
_MARKS_SUFFIX = re.compile(r"\[([0-9]{1,4})\]$")


@dataclass
class _PartDraft:
    label: str
    letter: str
    roman: str
    lead_in: list[Block]
    body_text: str
    marks: int
    line: int


def command_term_of(body_text: str, vocabulary: Vocabulary) -> tuple[str | None, bool]:
    """Section 5: the command term (lower-case first word, if in the vocabulary) and show_that."""
    words = re.findall(r"[A-Za-z]+", body_text[:40])
    if not words:
        return None, False
    first = words[0].lower()
    if first not in vocabulary.command_terms:
        return None, False
    return first, first == "show" and len(words) > 1 and words[1].lower() == "that"


def answer_type_of(command_term: str | None) -> AnswerType:
    if command_term is None:
        return AnswerType.EXPLANATION
    return _ANSWER_TYPES[command_term]


def parse_parts(
    blocks: Sequence[SourceBlock], stimuli: list[Stimulus], env: Env
) -> tuple[list[Block], list[_PartDraft]]:
    """Split the main section into the stem and the parts (with their lead-ins)."""
    stem_blocks: list[SourceBlock] = []
    drafts: list[_PartDraft] = []
    pending: list[SourceBlock] = []
    for block in blocks:
        text = _joined(block) if block.kind == "para" else ""
        local = env.at(block.first)
        part = _PART_LINE.match(text.strip()) if block.kind == "para" else None
        sub = _SUBPART_LINE.match(text.strip()) if block.kind == "para" and drafts else None
        if part is not None:
            letter, roman, body = part.groups()
            roman = roman or ""
            if not drafts:
                stem = pending
                pending = []
                stem_blocks.extend(stem)
            lead = content_blocks(pending, stimuli, local)
            pending = []
            drafts.append(_new_draft(letter, roman, body, lead, local))
        elif sub is not None and drafts[-1].roman:
            roman, body = sub.groups()
            if pending:
                raise local.fail("text between sub-parts of one letter")
            if drafts[-1].letter != drafts[-1].label.split(".")[0]:
                raise local.fail("internal: bad draft label")
            drafts.append(_new_draft(drafts[-1].letter, roman, body, [], local))
        else:
            pending.append(block)
    if not drafts:
        raise env.fail("no parts (`**(a)** … [n]`)")
    if pending:
        raise env.at(pending[0].first).fail("text after the last part and before the mark scheme")
    stem_doc_blocks = content_blocks(stem_blocks, stimuli, env)
    return stem_doc_blocks, drafts


def _new_draft(letter: str, roman: str, body: str, lead: list[Block], env: Env) -> _PartDraft:
    if roman and roman not in _ROMAN:
        raise env.fail(f"unsupported sub-part numeral ({roman})")
    body = body.rstrip()
    found = _MARKS_SUFFIX.search(body)
    if found is None:
        raise env.fail(f"part ({letter}){f' ({roman})' if roman else ''} has no `[n]` marks")
    label = f"{letter}.{roman}" if roman else letter
    return _PartDraft(
        label=label,
        letter=letter,
        roman=roman,
        lead_in=lead,
        body_text=body[: found.start()].strip(),
        marks=int(found.group(1)),
        line=env.line or 0,
    )


_ROUTE = re.compile(r"\*\*ALTERNATIVE ([0-9]{1,2})\*\*")
_ECF_REF = re.compile(r"\(([a-z])\)(?:\(([ivx]+)\))?")
_CAP = re.compile(r"^Award (?:\[\d+ max\]|\[\d+\] max)(?:\s|$)")


def note_kind(plain: str) -> NoteKind:
    """Section 3.2: the kind of a mark-scheme note, from its visible text."""
    if plain.strip().rstrip(".") == "OWTTE":
        return NoteKind.OWTTE
    if plain.startswith("Allow ECF"):
        return NoteKind.ECF
    if plain.startswith("Do not accept"):
        return NoteKind.DO_NOT_ACCEPT
    if plain.startswith("Accept"):
        return NoteKind.ACCEPT
    if _CAP.match(plain):
        return NoteKind.CAP
    return NoteKind.GENERAL


def convert_notes(
    cell: str, part_id: str, earlier: Sequence[str], env: Env
) -> tuple[tuple[Note, ...], tuple[str, ...]]:
    notes: list[Note] = []
    ecf: list[str] = []
    for text in (t.strip() for t in cell.split("<br>")):
        if not text:
            continue
        spans = parse_inline(text, env, ticks=True)
        if any(MarkType.ITALIC in s.marks for s in spans if s.kind == "text"):
            env.add("note-italic")
            spans = _tidy(
                [
                    replace(s, marks=s.marks - {MarkType.ITALIC}) if s.kind == "text" else s
                    for s in spans
                ]
            )
        plain = plain_text(spans).strip()
        if not plain:
            raise env.fail(f"empty note {text!r}")
        kind = note_kind(plain)
        if kind is NoteKind.ECF:
            if not plain.startswith("Allow ECF from ("):
                env.add("ecf-prefix")
            refs = [
                f"{letter}.{roman}" if roman else letter
                for letter, roman in _ECF_REF.findall(plain)
            ]
            if not refs:
                raise env.fail(f"ECF note names no part: {plain!r}")
            for ref in refs:
                if ref not in earlier:
                    raise env.fail(
                        f"ECF note in part {part_id} refers to {ref}: not an earlier part "
                        f"({', '.join(earlier) or 'none'})"
                    )
                if ref not in ecf:
                    ecf.append(ref)
        env.tally.count("note_kind", kind.value)
        notes.append(Note(kind=kind, content=doc_of([paragraph_of(spans)], env)))
    return tuple(notes), tuple(ecf)


def convert_answers(
    cell: str, label: str, marks: int, env: Env
) -> tuple[tuple[MarkPoint, ...], bool]:
    """Mark points of one Answers cell and whether the part is capped (more points than marks)."""
    points: list[MarkPoint] = []
    route: str | None = None
    for text in (t.strip() for t in cell.split("<br>")):
        if not text:
            continue
        found = _ROUTE.fullmatch(text)
        if found is not None:
            route = f"alt{found.group(1)}"
            continue
        if not text.endswith("✓"):
            raise env.fail(f"mark-scheme line without ✓ in part ({label}): {_quote(text)}")
        body = text[:-1].rstrip()
        if "✓" in body:
            raise env.fail(f"✓ inside a mark point in part ({label}): {_quote(text)}")
        spans = parse_inline(body, env)
        points.append(
            MarkPoint(
                id=f"{label}-m{len(points) + 1}",
                content=doc_of([paragraph_of(spans)], env),
                kind=MarkPointKind.STATEMENT,
                route=route,
            )
        )
        env.tally.count("mark_point_kind", MarkPointKind.STATEMENT.value)
    if not points:
        raise env.fail(f"no mark points in part ({label})")
    routes = {p.route for p in points if p.route}
    if len(routes) == 1:
        raise env.fail(f"part ({label}) has a single ALTERNATIVE route")
    shared = [p for p in points if p.route is None]
    best = max((sum(1 for p in points if p.route == r) for r in routes), default=0)
    awardable = len(shared) + best
    if awardable < marks:
        raise env.fail(f"part ({label}): {awardable} awardable mark points for {marks} marks")
    return tuple(points), awardable > marks


def convert_markscheme(
    lines: Sequence[Line],
    drafts: Sequence[_PartDraft],
    node: str,
    hl: bool,
    question: int,
    vocabulary: Vocabulary,
    stimuli: list[Stimulus],
    env: Env,
) -> list[Part]:
    blocks = split_blocks(lines)
    if not blocks or blocks[0].kind != "table":
        raise env.fail("the mark scheme must start with its table")
    free = 0
    for block in blocks[1:]:
        if block.kind != "para":
            raise env.at(block.first).fail("unexpected quote or table after the mark scheme")
        free += 1
    if free:
        env.tally.free_paragraphs.append((env.ref, free))
    rows = table_rows(blocks[0], env)
    if [c for c in rows[0][1]] != ["Question", "", "", "Answers", "Notes", "Total"]:
        raise env.at(rows[0][0]).fail(f"unexpected mark-scheme header {rows[0][1]}")
    by_part: dict[str, tuple[int, list[str]]] = {}
    for no, cells in rows[1:]:
        if len(cells) != 6:
            raise env.at(no).fail(f"mark-scheme row has {len(cells)} cells, expected 6")
        if cells[0] != f"{question}.":
            raise env.at(no).fail(f"mark-scheme row for question {cells[0]!r}")
        part_id = f"{cells[1]}.{cells[2]}" if cells[2] else cells[1]
        if part_id in by_part:
            raise env.at(no).fail(f"two mark-scheme rows for part ({part_id})")
        by_part[part_id] = (no, cells)
    draft_ids = [d.label for d in drafts]
    for part_id, (no, _) in by_part.items():
        if part_id not in draft_ids:
            raise env.at(no).fail(f"mark-scheme row for unknown part ({part_id})")
    parts: list[Part] = []
    fields: list[tuple[str, str, str]] = []
    for draft in drafts:
        if draft.label not in by_part:
            raise env.at(draft.line).fail(f"part ({draft.label}) has no mark-scheme row")
        no, cells = by_part[draft.label]
        local = env.at(no)
        total = cells[5]
        if total.endswith(" max"):
            env.add("total-max")
            total = total.removesuffix(" max")
        if small_int(total) != draft.marks:
            raise local.fail(f"Total {cells[5]!r} differs from the part's [{draft.marks}]")
        points, capped = convert_answers(cells[3], draft.label, draft.marks, local)
        earlier = [p.id for p in parts]
        notes, ecf = convert_notes(cells[4], draft.label, earlier, local)
        command_term, show_that = command_term_of(draft.body_text, vocabulary)
        answer_type = answer_type_of(command_term)
        env.tally.count("command_term", command_term or "(boş)")
        env.tally.count("answer_type", answer_type.value)
        fields.append((draft.label, command_term or "", answer_type.value))
        if capped:
            env.tally.count("marks_capped", "true")
        body_spans = parse_inline(draft.body_text, env.at(draft.line))
        parts.append(
            Part(
                id=draft.label,
                label=draft.label,
                lead_in=doc_of(draft.lead_in, env) if draft.lead_in else None,
                body=doc_of([paragraph_of(body_spans)], env),
                marks=draft.marks,
                marks_capped=capped,
                show_that=show_that,
                command_term=command_term,
                answer_type=answer_type,
                level_content=LevelContent.AHL if hl else LevelContent.SL_CORE,
                syllabus_node=node,
                ecf_from=ecf,
                mark_points=points,
                notes=notes,
            )
        )
    env.tally.question_fields.append((env.ref, "parts", "", tuple(fields)))
    return parts


# --- Solution model ------------------------------------------------------------------------


class _Omit(Exception):
    """The formula chain does not fully fit section 3.4. `code` groups the reasons in the report."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_BACKTICKED = re.compile(r"`([^`]*)`")
_RESULT = re.compile(rf"^({_NUMBER})\s*(.+)$")
_UNIT_TOKEN = re.compile(r"^[A-Za-zµΩ°%]+(?:\^-?\d+)?(?:/[A-Za-zµΩ°%]+(?:\^-?\d+)?)*$")


def ascii_unit(unit: str) -> str:
    """`m s⁻¹` -> `m s^-1`: every run of superscript characters becomes `^` and the run."""
    return re.sub(
        f"[{_SUPERSCRIPT_CHARS}]+", lambda m: "^" + m.group(0).translate(_SUPERSCRIPTS), unit
    )


def _parameters(cell: str, ref: str, tally: Tally) -> list[Parameter]:
    outside = _BACKTICKED.sub(" ", cell)
    leftover = re.sub(r"\b(constants|constant)\b|[,;]", " ", outside, flags=re.IGNORECASE)
    if leftover.strip():
        raise _Omit("ters tırnaksız parametre metni", repr(leftover.strip()))
    if "`" in cell and cell.count("`") % 2:
        raise _Omit("ters tırnaksız parametre metni", "unbalanced backtick")
    parameters: list[Parameter] = []
    after_constant_word = False
    position = 0
    for found in _BACKTICKED.finditer(cell):
        between = cell[position : found.start()]
        if re.search(r"\bconstants?\b", between, flags=re.IGNORECASE):
            after_constant_word = True
        position = found.end()
        item = re.fullmatch(
            r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\S+)(?:\s+(.+))?", found.group(1).strip()
        )
        if item is None:
            raise _Omit("parametre biçimi", f"{found.group(1)!r} is not `name = value unit`")
        name, value, unit = item.group(1), item.group(2), (item.group(3) or "")
        if not re.fullmatch(NUMBER_PATTERN, value):
            raise _Omit("sayı biçimi", f"{value!r}")
        if not re.fullmatch(UNIT_PATTERN, unit):
            raise _Omit("birim biçimi", f"{unit!r}")
        parameters.append(Parameter(name=name, value=value, unit=unit))
        if after_constant_word:
            tally.constants.append((ref, name))
    return parameters


def _step_unit(result: str) -> str:
    found = _RESULT.match(result.strip())
    if found is None:
        return ""
    unit = ascii_unit(found.group(2).strip())
    words = unit.split(" ")
    if all(_UNIT_TOKEN.match(w) for w in words) and re.fullmatch(UNIT_PATTERN, unit):
        return unit
    return ""


def solution_model(
    lines: Sequence[Line], env: Env
) -> tuple[SolutionModel | None, tuple[str, str] | None]:
    """Section 3.4: the model, or None with the reason it was left out."""
    blocks = split_blocks(lines)
    if not blocks or blocks[0].kind != "table":
        raise env.fail("the formula chain must start with its table")
    free = 0
    for block in blocks[1:]:
        if block.kind != "para":
            raise env.at(block.first).fail("unexpected quote or table after the formula chain")
        free += 1
    if free:
        env.tally.free_paragraphs.append((env.ref, free))
    rows = table_rows(blocks[0], env)
    if rows[0][1] != ["Step", "Expression", "Result"]:
        raise env.at(rows[0][0]).fail(f"unexpected formula chain header {rows[0][1]}")
    try:
        parameters: list[Parameter] = []
        steps: list[Step] = []
        seen_parameters = False
        for no, cells in rows[1:]:
            if len(cells) != 3:
                raise _Omit("sütun sayısı", f"line {no}: {len(cells)} instead of 3")
            name_cell, expr_cell, result = cells
            if name_cell == "Parameters":
                if seen_parameters:
                    raise _Omit("yinelenen parametre satırı", f"line {no}")
                seen_parameters = True
                parameters = _parameters(expr_cell, env.ref, env.tally)
                continue
            named = re.match(r"^`([^`]*)`([^`]*)$", name_cell)
            if named is None or not _IDENT.match(named.group(1)):
                raise _Omit("satır adı tanımlayıcı değil", f"line {no}: {name_cell!r}")
            expressions = _BACKTICKED.findall(expr_cell)
            if len(expressions) != 1 or _BACKTICKED.sub("", expr_cell).strip():
                raise _Omit("ifade sütunu tek ifade değil", f"line {no}")
            if not expressions[0].strip():
                raise _Omit("ifade sütunu boş", f"line {no}")
            steps.append(
                Step(
                    id=f"s{len(steps) + 1}",
                    name=named.group(1),
                    expr=expressions[0].strip(),
                    unit=_step_unit(result),
                )
            )
        names = [p.name for p in parameters] + [s.name for s in steps]
        if len(names) != len(set(names)):
            raise _Omit("yinelenen ad", "parameter or step name")
        model = SolutionModel(parameters=tuple(parameters), steps=tuple(steps))
        env.tally.step_units.append((env.ref, sum(1 for st in steps if not st.unit), len(steps)))
        return model, None
    except _Omit as omit:
        return None, (omit.code, omit.detail)
    except ValidationError as error:
        return None, ("şema", error.errors()[0]["msg"])


# --- Question and file ---------------------------------------------------------------------


def _node_of(stem: str, env: Env, vocabulary: Vocabulary) -> str:
    found = re.match(r"^([a-e])([1-9])-", stem)
    if found is None:
        raise env.fail(f"cannot read the syllabus node from the file name {stem!r}")
    node = f"{found.group(1).upper()}.{found.group(2)}"
    if node not in vocabulary.nodes:
        raise env.fail(f"syllabus node {node} is not in the vocabulary")
    return node


def convert_question(
    lines: Sequence[Line],
    heading: Heading,
    scope: ScopeRow,
    vocabulary: Vocabulary,
    env: Env,
) -> PilotQuestion:
    env = replace(env, question=heading.number, line=heading.line)
    node = _node_of(env.stem, env, vocabulary)
    section_code = _SECTION_CODES[heading.section]
    if section_code not in vocabulary.sections:
        raise env.fail(f"exam section {section_code} is not in the vocabulary")
    if scope.section != f"Paper {heading.section}":
        raise env.fail(f"scope table says {scope.section!r}, heading says Paper {heading.section}")
    if scope.level not in ("SL", "HL"):
        raise env.fail(f"scope table level {scope.level!r} is neither SL nor HL")
    if heading.hl and scope.level != "HL":
        raise env.fail("heading says HL but the scope table says SL")
    hl = scope.level == "HL"
    if scope.difficulty not in _DIFFICULTY:
        raise env.fail(f"unknown difficulty {scope.difficulty!r}")
    if not scope.outcome:
        raise env.fail("empty outcome in the scope table")

    main, sections = _split_sections(lines, env)
    unknown = [
        t
        for t in sections
        if t not in ("Markscheme", "Formula chain (solution model)", "Figure note")
    ]
    if unknown:
        raise env.fail(f"unknown section {unknown[0]!r}")
    stimuli: list[Stimulus] = []
    main_blocks = split_blocks(main)
    if not main_blocks:
        raise env.fail("empty question")

    levels = (Level.HL,) if hl else (Level.SL, Level.HL)
    common = {
        "schema_version": "1.0",
        "exam_section": section_code,
        "levels": levels,
        "language": "en",
        "calculator": True,
        "difficulty": _DIFFICULTY[scope.difficulty],
        "primary_syllabus_node": node,
        "outcome": scope.outcome,
    }
    try:
        if heading.section == "1A":
            if sections:
                raise env.fail("a Paper 1A question has no ### sections")
            if scope.marks != 1:
                raise env.fail(f"Paper 1A question with {scope.marks} marks in the scope table")
            stem, mcq = convert_mcq(main_blocks, heading, scope, node, hl, env, stimuli)
            document = QuestionDocument.model_validate(
                {
                    **common,
                    "question_class": QuestionClass.MCQ,
                    "stem": stem,
                    "stimuli": tuple(stimuli),
                    "mcq": mcq,
                    "total_marks": 1,
                }
            )
            env.tally.count("question_class", "mcq")
            return PilotQuestion(source_ref=env.ref, number=heading.number, document=document)

        stem_blocks, drafts = parse_parts(main_blocks, stimuli, env)
        total = sum(d.marks for d in drafts)
        if heading.marks != total:
            raise env.fail(f"heading says {heading.marks} marks, the parts add up to {total}")
        if scope.marks != total:
            raise env.fail(f"scope table says {scope.marks} marks, the parts add up to {total}")
        if "Markscheme" not in sections:
            raise env.fail("missing `### Markscheme`")
        parts = convert_markscheme(
            sections["Markscheme"], drafts, node, hl, heading.number, vocabulary, stimuli, env
        )
        model: SolutionModel | None = None
        chain = "Formula chain (solution model)"
        if chain in sections:
            model, reason = solution_model(sections[chain], env)
            if model is None:
                env.tally.models_omitted.append((env.ref, *(reason or ("?", ""))))
            else:
                env.tally.models_imported.append(env.ref)
        else:
            env.tally.models_omitted.append((env.ref, "bölüm yok", ""))
        if "Figure note" in sections:
            if not any(line.text.strip() for line in sections["Figure note"]):
                raise env.fail("`### Figure note` is empty")
            # The note is the author's working text and may hold the answer: it is not imported.
            env.tally.figure_notes_skipped.append(env.ref)
            stimuli.append(
                Stimulus(
                    id=f"fig{len(stimuli) + 1}",
                    kind=StimulusKind.GRAPH,
                    use=StimulusUse.READ_VALUES,
                    description=FIGURE_NOTE_DESCRIPTION,
                )
            )
            env.tally.stimuli.append((env.ref, stimuli[-1].id, "graph", "Figure note"))
            env.tally.count("stimulus_kind", StimulusKind.GRAPH.value)
        question_class = (
            QuestionClass.DATA_BASED
            if heading.section == "1B"
            else QuestionClass.LONG_STRUCTURED
            if total == 20
            else QuestionClass.SHORT_STRUCTURED
        )
        document = QuestionDocument.model_validate(
            {
                **common,
                "question_class": question_class,
                "stem": doc_of(stem_blocks, env),
                "stimuli": tuple(stimuli),
                "parts": tuple(parts),
                "total_marks": total,
                "solution_model": model,
            }
        )
        env.tally.count("question_class", question_class.value)
        return PilotQuestion(source_ref=env.ref, number=heading.number, document=document)
    except ValidationError as error:
        details = "; ".join(
            f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in error.errors()[:3]
        )
        raise env.fail(f"schema validation failed: {details}") from error


def convert_markdown(
    data: bytes,
    stem: str,
    vocabulary: Vocabulary,
    tally: Tally | None = None,
) -> PilotFile:
    """The whole file. Raises `ConversionFailed` (all question errors) if any question fails."""
    tally = tally if tally is not None else Tally()
    env = Env(stem=stem, tally=tally)
    if len(data) > MAX_FILE_BYTES:
        raise env.fail(f"file is larger than {MAX_FILE_BYTES} bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise env.fail("file is not UTF-8") from error
    if "\r" in text:
        raise env.fail("file has carriage returns")
    lines = [Line(no, raw) for no, raw in enumerate(text.split("\n"), start=1)]
    for line in lines:
        if len(line.text) > MAX_LINE_CHARS:
            raise env.at(line.no).fail(f"line is longer than {MAX_LINE_CHARS} characters")

    # Cut the file into `## ` sections. A `---` ends the section it follows; what comes after it
    # up to the next `## ` heading must be blank (section 3).
    sections: list[tuple[Line, list[Line], list[Line]]] = []
    current: list[Line] | None = None
    after: list[Line] | None = None
    for line in lines:
        if line.text.startswith("## "):
            current, after = [], []
            sections.append((line, current, after))
        elif line.text.strip() == "---":
            if after is not None and current is None:
                after.append(line)  # a second rule is text after the block end
            current = None
        elif current is not None:
            current.append(line)
        elif after is not None:
            after.append(line)

    scope_lines = next((body for head, body, _ in sections if head.text == "## Scope table"), None)
    if scope_lines is None:
        raise env.fail("no `## Scope table` section")
    scope = parse_scope(scope_lines, env)

    errors: list[ConversionError] = []
    questions: list[PilotQuestion] = []
    headings_seen: list[int] = []
    for head, body, trailing in sections:
        if not head.text.startswith("## Question"):
            if head.text[3:] not in _KNOWN_SECTION_TITLES:
                raise env.at(head.no).fail(f"unknown section heading {head.text!r}")
            continue
        heading = parse_heading(head, env)
        headings_seen.append(heading.number)
        row = scope.get(heading.number)
        if row is None:
            raise env.at(head.no).fail(f"question {heading.number} is not in the scope table")
        stray = next((ln for ln in trailing if ln.text.strip()), None)
        if stray is not None:
            errors.append(
                ConversionError(
                    env.file,
                    heading.number,
                    stray.no,
                    "text after the `---` that ends the question block "
                    f"(rules cannot use `---` inside a question): {_quote(stray.text.strip())}",
                )
            )
            continue
        try:
            questions.append(convert_question(body, heading, row, vocabulary, env))
        except ConversionError as error:
            errors.append(error)
    if sorted(headings_seen) != sorted(scope) or len(set(headings_seen)) != len(headings_seen):
        raise env.fail(
            f"questions {sorted(headings_seen)} do not match the scope table {sorted(scope)}"
        )
    if errors:
        raise ConversionFailed(errors)
    if not questions:
        raise env.fail("the file has no questions")
    tally.file_counts[stem] = Counter(q.document.question_class.value for q in questions)
    try:
        return PilotFile(
            source_file=f"docs/pilot/{stem}{SOURCE_SUFFIX}",
            source_sha256=hashlib.sha256(data).hexdigest(),
            questions=tuple(questions),
        )
    except ValidationError as error:
        raise env.fail(f"file model rejected: {error.errors()[0]['msg']}") from error
