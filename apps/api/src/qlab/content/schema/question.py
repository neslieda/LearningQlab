"""Question document schema v1: the single source of truth for question content.

Specification: docs/DATA_ARCHITECTURE.md section 3.5. Vocabulary that belongs to a programme
(exam sections, command terms, syllabus node codes) is data validated elsewhere. The structural
limits hard-coded here (four options, part marks, the two-level split) are a known v1 limitation
recorded in docs/DECISIONS.md D-50.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from qlab.content.schema.blocks import (
    NUMBER_PATTERN,
    UNIT_PATTERN,
    Doc,
    Quantity,
    is_blank,
    iter_figure_refs,
    iter_latex,
    iter_quantities,
)

SCHEMA_VERSION: Literal["1.0"] = "1.0"
MAX_PART_MARKS = 3
OPTION_KEYS = ("A", "B", "C", "D")
_ROMAN = ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")

_IDENT = r"^[A-Za-z_][A-Za-z0-9_]*$"
_SLUG = r"^[a-z0-9][a-z0-9_.-]*$"

Slug = Annotated[str, StringConstraints(pattern=_SLUG)]
Ident = Annotated[str, StringConstraints(pattern=_IDENT)]
NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
OptionKey = Literal["A", "B", "C", "D"]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class QuestionClass(StrEnum):
    MCQ = "mcq"
    DATA_BASED = "data_based"
    SHORT_STRUCTURED = "short_structured"
    LONG_STRUCTURED = "long_structured"


class Level(StrEnum):
    """Papers the question may be used in. Declaration order is the canonical order."""

    SL = "sl"
    HL = "hl"


class LevelContent(StrEnum):
    SL_CORE = "sl_core"
    AHL = "ahl"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class OptionKind(StrEnum):
    NUMERIC_WITH_UNIT = "numeric_with_unit"
    RATIO = "ratio"
    ALGEBRAIC_EXPRESSION = "algebraic_expression"
    WORD_PHRASE = "word_phrase"
    STATEMENT = "statement"
    FIGURE_CHOICE = "figure_choice"


class OptionLayout(StrEnum):
    SINGLE_VALUE = "single_value"
    TWO_COLUMN_TABLE = "two_column_table"
    FIGURE_OPTIONS = "figure_options"
    ROMAN_STATEMENTS = "roman_statements"


class AnswerType(StrEnum):
    NUMERIC_WITH_UNIT = "numeric_with_unit"
    NUMERIC_UNITLESS = "numeric_unitless"
    VALUE_FROM_GRAPH = "value_from_graph"
    UNIT = "unit"
    ALGEBRAIC_EXPRESSION = "algebraic_expression"
    SYMBOLIC_EQUATION = "symbolic_equation"
    WORD_PHRASE = "word_phrase"
    EXPLANATION = "explanation"
    JUDGEMENT_JUSTIFIED = "judgement_justified"
    EXTENDED_EVALUATION = "extended_evaluation"
    DERIVATION_ALGEBRAIC = "derivation_algebraic"
    DERIVATION_NUMERIC = "derivation_numeric"
    DRAWING_ON_DIAGRAM = "drawing_on_diagram"
    GRAPH_SKETCH = "graph_sketch"


class StimulusKind(StrEnum):
    SCHEMATIC_DIAGRAM = "schematic_diagram"
    GRAPH = "graph"
    DATA_TABLE = "data_table"
    CIRCUIT_DIAGRAM = "circuit_diagram"
    FIELD_DIAGRAM = "field_diagram"
    RAY_WAVEFRONT_DIAGRAM = "ray_wavefront_diagram"
    ENERGY_LEVEL_DIAGRAM = "energy_level_diagram"
    SPACETIME_DIAGRAM = "spacetime_diagram"
    PICTURE = "picture"


class StimulusUse(StrEnum):
    READ_ONLY = "read_only"
    READ_VALUES = "read_values"
    STUDENT_ANNOTATES = "student_annotates"


class Stimulus(Model):
    """A figure, graph or similar. Without an asset it is a description and blocks publishing."""

    id: Slug
    kind: StimulusKind
    use: StimulusUse = StimulusUse.READ_ONLY
    description: NonBlank
    asset_id: Slug | None = None
    alt_text: NonBlank | None = None

    @model_validator(mode="after")
    def _asset_needs_alt_text(self) -> Self:
        if self.asset_id is not None and self.alt_text is None:
            raise ValueError("a stimulus with an asset must have alt text")
        return self


class McqOption(Model):
    key: OptionKey
    # One cell for ordinary options; one per column for a two-column table.
    cells: tuple[Doc, ...] = Field(min_length=1, max_length=2)
    # For a wrong option: the misconception or typical error it is built on.
    rationale: Doc | None = None


class Mcq(Model):
    option_kind: OptionKind
    option_layout: OptionLayout = OptionLayout.SINGLE_VALUE
    column_headers: tuple[Doc, ...] = ()
    statements: tuple[Doc, ...] = ()
    options: tuple[McqOption, ...]
    correct_key: OptionKey
    explanation: Doc | None = None
    assessment_objective: Literal[1, 2, 3] | None = None
    level_content: LevelContent = LevelContent.SL_CORE
    solution_step: Ident | None = None

    @model_validator(mode="after")
    def _options_consistent(self) -> Self:
        if tuple(o.key for o in self.options) != OPTION_KEYS:
            raise ValueError("options must be exactly A, B, C, D in that order")
        for option in self.options:
            wrong = option.key != self.correct_key
            if wrong and (option.rationale is None or is_blank(option.rationale)):
                raise ValueError(f"wrong option {option.key} needs a rationale")
        columns = 2 if self.option_layout is OptionLayout.TWO_COLUMN_TABLE else 1
        if any(len(o.cells) != columns for o in self.options):
            raise ValueError(f"every option needs {columns} cell(s) for this layout")
        if len(self.column_headers) != (2 if columns == 2 else 0):
            raise ValueError("column headers are required for, and only for, a two-column table")
        roman = self.option_layout is OptionLayout.ROMAN_STATEMENTS
        if roman != bool(self.statements) or (roman and len(self.statements) < 2):
            raise ValueError("roman-statement layout needs at least two statements, others none")
        if len({o.cells for o in self.options}) != len(self.options):
            raise ValueError("two options are identical")
        return self


class MarkPointKind(StrEnum):
    METHOD = "method"
    ANSWER = "answer"
    STATEMENT = "statement"


class AcceptRange(Model):
    minimum: str = Field(pattern=NUMBER_PATTERN)
    maximum: str = Field(pattern=NUMBER_PATTERN)
    unit: str = Field(default="", pattern=UNIT_PATTERN)

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        if float(self.minimum) > float(self.maximum):
            raise ValueError("accept range minimum is greater than maximum")
        return self


class MarkPoint(Model):
    """One mark.

    Points sharing an alternative_group are alternatives for a single mark. Points sharing a route
    form one complete way of earning the part's marks; routes are mutually exclusive.
    """

    id: Slug
    content: Doc
    kind: MarkPointKind = MarkPointKind.STATEMENT
    alternative_group: Slug | None = None
    route: Slug | None = None
    accept_range: AcceptRange | None = None
    solution_step: Ident | None = None


class NoteKind(StrEnum):
    GENERAL = "general"
    OWTTE = "owtte"
    ACCEPT = "accept"
    DO_NOT_ACCEPT = "do_not_accept"
    CAP = "cap"
    ECF = "ecf"


class Note(Model):
    """A mark-scheme note for a part, optionally tied to one of its mark points."""

    kind: NoteKind = NoteKind.GENERAL
    content: Doc
    mark_point_id: Slug | None = None


def _point_count(points: Sequence[MarkPoint]) -> int:
    groups = {p.alternative_group for p in points if p.alternative_group}
    return sum(1 for p in points if not p.alternative_group) + len(groups)


def _label_key(label: str) -> tuple[str, int]:
    letter, _, roman = label.partition(".")
    return letter, (_ROMAN.index(roman) + 1 if roman else 0)


class Part(Model):
    id: Slug
    label: str = Field(pattern=r"^[a-z](\.(i|ii|iii|iv|v|vi|vii|viii))?$")
    # Text shown before the part that belongs to its parent letter or sets new context.
    lead_in: Doc | None = None
    body: Doc
    marks: int = Field(ge=1, le=MAX_PART_MARKS)
    # True when the mark scheme offers more points than marks ("max").
    marks_capped: bool = False
    show_that: bool = False
    command_term: str | None = Field(default=None, pattern=r"^[a-z][a-z_]*$")
    answer_type: AnswerType
    assessment_objective: Literal[1, 2, 3] | None = None
    level_content: LevelContent = LevelContent.SL_CORE
    syllabus_node: NonBlank
    stimulus_refs: tuple[Slug, ...] = ()
    depends_on: tuple[Slug, ...] = ()
    ecf_from: tuple[Slug, ...] = ()
    mark_points: tuple[MarkPoint, ...] = Field(min_length=1)
    notes: tuple[Note, ...] = ()

    @property
    def awardable_marks(self) -> int:
        """Most marks obtainable from the mark points: shared points plus the best route."""
        shared = [p for p in self.mark_points if p.route is None]
        routes: dict[str, list[MarkPoint]] = {}
        for point in self.mark_points:
            if point.route is not None:
                routes.setdefault(point.route, []).append(point)
        best = max((_point_count(points) for points in routes.values()), default=0)
        return _point_count(shared) + best

    @model_validator(mode="after")
    def _mark_scheme_consistent(self) -> Self:
        if is_blank(self.body):
            raise ValueError(f"part {self.label}: empty body")
        ids = {p.id for p in self.mark_points}
        routes = {p.route for p in self.mark_points if p.route}
        if len(routes) == 1:
            raise ValueError(f"part {self.label}: a single route is not an alternative")
        if self.marks_capped:
            if self.awardable_marks <= self.marks:
                raise ValueError(f"part {self.label}: capped but no more points than marks")
        elif self.awardable_marks != self.marks:
            raise ValueError(
                f"part {self.label}: {self.awardable_marks} awardable mark points "
                f"for {self.marks} marks"
            )
        for note in self.notes:
            if note.mark_point_id is not None and note.mark_point_id not in ids:
                raise ValueError(f"part {self.label}: note refers to an unknown mark point")
        for refs in (self.depends_on, self.ecf_from, self.stimulus_refs):
            if len(refs) != len(set(refs)):
                raise ValueError(f"part {self.label}: duplicate reference")
        return self


class Parameter(Model):
    name: Ident
    value: str = Field(pattern=NUMBER_PATTERN)
    unit: str = Field(default="", pattern=UNIT_PATTERN)


class Constant(Model):
    name: Ident
    ref: NonBlank


class Step(Model):
    id: Ident
    name: Ident
    expr: NonBlank
    unit: str = Field(default="", pattern=UNIT_PATTERN)
    # A "show that" value given in the question, to be used downstream instead of the result.
    stated_value: str | None = Field(default=None, pattern=NUMBER_PATTERN)


class AnswerBinding(Model):
    part_id: Slug
    step: Ident


class SolutionModel(Model):
    """Declarative formula chain, stored as data. It is not evaluated here (no interpreter yet)."""

    parameters: tuple[Parameter, ...] = ()
    constants: tuple[Constant, ...] = ()
    steps: tuple[Step, ...] = ()
    answers: tuple[AnswerBinding, ...] = ()

    @model_validator(mode="after")
    def _names_unique_and_bound(self) -> Self:
        names = [p.name for p in self.parameters] + [c.name for c in self.constants]
        names += [s.name for s in self.steps]
        if len(names) != len(set(names)):
            raise ValueError("solution model: duplicate parameter, constant or step name")
        step_ids = [s.id for s in self.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("solution model: duplicate step id")
        bound_parts = [b.part_id for b in self.answers]
        if len(bound_parts) != len(set(bound_parts)):
            raise ValueError("solution model: a part has more than one answer binding")
        for binding in self.answers:
            if binding.step not in step_ids:
                raise ValueError(f"solution model: answer bound to unknown step {binding.step}")
        return self


class QuestionDocument(Model):
    schema_version: Literal["1.0"]
    question_class: QuestionClass
    exam_section: Slug
    levels: tuple[Level, ...] = Field(min_length=1)
    language: str = Field(default="en", pattern=r"^[a-z]{2}$")
    calculator: bool = True
    difficulty: Difficulty | None = None
    primary_syllabus_node: NonBlank
    secondary_syllabus_nodes: tuple[NonBlank, ...] = ()
    # The assessed outcome in the author's own words (not syllabus text).
    outcome: NonBlank | None = None
    stem: Doc
    stimuli: tuple[Stimulus, ...] = ()
    mcq: Mcq | None = None
    parts: tuple[Part, ...] = ()
    total_marks: int = Field(ge=1)
    solution_model: SolutionModel | None = None

    @property
    def visual_pending(self) -> bool:
        return any(s.asset_id is None for s in self.stimuli)

    def docs(self) -> Iterator[Doc]:
        """Every rich-text document in the question, in reading order."""
        yield self.stem
        if self.mcq is not None:
            yield from self.mcq.column_headers
            yield from self.mcq.statements
            for option in self.mcq.options:
                yield from option.cells
                if option.rationale is not None:
                    yield option.rationale
            if self.mcq.explanation is not None:
                yield self.mcq.explanation
        for part in self.parts:
            if part.lead_in is not None:
                yield part.lead_in
            yield part.body
            for point in part.mark_points:
                yield point.content
            for note in part.notes:
                yield note.content

    def latex_sources(self) -> Iterator[str]:
        for doc in self.docs():
            yield from iter_latex(doc)

    def quantities(self) -> Iterator[Quantity]:
        for doc in self.docs():
            yield from iter_quantities(doc)

    @model_validator(mode="after")
    def _header_consistent(self) -> Self:
        if is_blank(self.stem):
            raise ValueError("empty stem")
        if list(self.levels) != sorted(set(self.levels), key=list(Level).index):
            raise ValueError("levels must be unique and in canonical order (sl, hl)")
        nodes = (self.primary_syllabus_node, *self.secondary_syllabus_nodes)
        if len(nodes) != len(set(nodes)):
            raise ValueError("duplicate syllabus node")
        return self

    @model_validator(mode="after")
    def _class_shape(self) -> Self:
        if self.question_class is QuestionClass.MCQ:
            if self.mcq is None or self.parts:
                raise ValueError("a multiple-choice question has an mcq block and no parts")
            if self.total_marks != 1:
                raise ValueError("a multiple-choice question carries exactly 1 mark")
        else:
            if self.mcq is not None or not self.parts:
                raise ValueError("a structured question has parts and no mcq block")
            if sum(p.marks for p in self.parts) != self.total_marks:
                raise ValueError("part marks do not add up to total_marks")
        return self

    @model_validator(mode="after")
    def _parts_consistent(self) -> Self:
        ids = [p.id for p in self.parts]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate part id")
        keys = [_label_key(p.label) for p in self.parts]
        if keys != sorted(set(keys)):
            raise ValueError("part labels must be unique and in order")
        letters_bare = {letter for letter, index in keys if index == 0}
        letters_split = {letter for letter, index in keys if index > 0}
        if letters_bare & letters_split:
            raise ValueError("a part letter is used both with and without sub-parts")
        point_ids = [point.id for part in self.parts for point in part.mark_points]
        if len(point_ids) != len(set(point_ids)):
            raise ValueError("duplicate mark point id in the question")
        nodes = {self.primary_syllabus_node, *self.secondary_syllabus_nodes}
        seen: set[str] = set()
        for part in self.parts:
            if part.syllabus_node not in nodes:
                raise ValueError(f"part {part.label}: syllabus node is not listed on the question")
            for ref in (*part.depends_on, *part.ecf_from):
                if ref not in seen:
                    raise ValueError(f"part {part.label} refers to {ref}: not an earlier part")
            seen.add(part.id)
        return self

    @model_validator(mode="after")
    def _level_content_consistent(self) -> Self:
        contents = [p.level_content for p in self.parts]
        if self.mcq is not None:
            contents.append(self.mcq.level_content)
        if Level.SL in self.levels and LevelContent.AHL in contents:
            raise ValueError("a question usable at SL cannot contain additional-HL content")
        return self

    @model_validator(mode="after")
    def _stimuli_consistent(self) -> Self:
        ids = [s.id for s in self.stimuli]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate stimulus id")
        known = set(ids)
        refs = [ref for doc in self.docs() for ref in iter_figure_refs(doc)]
        refs += [ref for part in self.parts for ref in part.stimulus_refs]
        for ref in refs:
            if ref not in known:
                raise ValueError(f"reference to unknown stimulus {ref}")
        return self

    @model_validator(mode="after")
    def _solution_model_consistent(self) -> Self:
        # A missing model is an empty one: bindings that point at it are still errors.
        model = self.solution_model or SolutionModel()
        part_ids = {p.id for p in self.parts}
        step_ids = {s.id for s in model.steps}
        for binding in model.answers:
            if binding.part_id not in part_ids:
                raise ValueError(f"solution model: answer bound to unknown part {binding.part_id}")
        step_refs = [
            (f"mark point {point.id}", point.solution_step)
            for part in self.parts
            for point in part.mark_points
        ]
        if self.mcq is not None:
            step_refs.append(("mcq", self.mcq.solution_step))
        for owner, step in step_refs:
            if step is not None and step not in step_ids:
                raise ValueError(f"{owner}: unknown solution step {step}")
        parameters = {p.name: p for p in model.parameters}
        for quantity in self.quantities():
            name = quantity.attrs.param
            if name is None:
                continue
            parameter = parameters.get(name)
            if parameter is None:
                raise ValueError(f"quantity bound to unknown parameter {name}")
            if (parameter.value, parameter.unit) != (quantity.attrs.value, quantity.attrs.unit):
                raise ValueError(f"quantity and parameter {name} differ in value or unit")
        return self
