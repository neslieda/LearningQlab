"""Question document schema v1: the single source of truth for question content.

Specification: docs/DATA_ARCHITECTURE.md sections 3-4. Programme-specific vocabulary (exam sections,
command terms, syllabus node codes) is data validated elsewhere, not part of this schema.
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from qlab.content.schema.blocks import (
    Doc,
    Inline,
    MathInline,
    Quantity,
    iter_figure_refs,
    iter_inlines,
    iter_latex,
)

SCHEMA_VERSION: Literal["1.0"] = "1.0"
MAX_PART_MARKS = 3
OPTION_KEYS = ("A", "B", "C", "D")

_IDENT = r"^[A-Za-z_][A-Za-z0-9_]*$"
_SLUG = r"^[a-z0-9][a-z0-9_.-]*$"


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class QuestionClass(StrEnum):
    MCQ = "mcq"
    DATA_BASED = "data_based"
    SHORT_STRUCTURED = "short_structured"
    LONG_STRUCTURED = "long_structured"


class Level(StrEnum):
    """Papers the question may be used in."""

    SL = "sl"
    HL = "hl"


class LevelContent(StrEnum):
    SL_CORE = "sl_core"
    AHL = "ahl"


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
    STATEMENT_COMBINATION = "statement_combination"


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

    id: str = Field(pattern=_SLUG)
    kind: StimulusKind
    use: StimulusUse = StimulusUse.READ_ONLY
    description: str = Field(min_length=1)
    asset_id: str | None = None
    alt_text: str | None = None

    @model_validator(mode="after")
    def _asset_needs_alt_text(self) -> Self:
        if self.asset_id is not None and not (self.alt_text and self.alt_text.strip()):
            raise ValueError("a stimulus with an asset must have alt text")
        return self


class McqOption(Model):
    key: Literal["A", "B", "C", "D"]
    content: tuple[Inline, ...] = Field(min_length=1)
    # For a wrong option: the misconception or typical error it is built on.
    rationale: str | None = None


class Mcq(Model):
    option_kind: OptionKind
    option_layout: OptionLayout = OptionLayout.SINGLE_VALUE
    options: tuple[McqOption, ...]
    correct_key: Literal["A", "B", "C", "D"]

    @model_validator(mode="after")
    def _four_options_one_key(self) -> Self:
        if tuple(o.key for o in self.options) != OPTION_KEYS:
            raise ValueError("options must be exactly A, B, C, D in that order")
        for option in self.options:
            if option.key != self.correct_key and not (option.rationale or "").strip():
                raise ValueError(f"wrong option {option.key} needs a rationale")
        return self


class MarkPointKind(StrEnum):
    METHOD = "method"
    ANSWER = "answer"
    STATEMENT = "statement"


class AcceptRange(Model):
    minimum: float
    maximum: float
    unit: str = ""

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        if self.minimum > self.maximum:
            raise ValueError("accept range minimum is greater than maximum")
        return self


class MarkPoint(Model):
    """One mark. Points sharing an alternative_group are alternatives: at most one scores."""

    id: str = Field(pattern=_SLUG)
    content: tuple[Inline, ...] = Field(min_length=1)
    kind: MarkPointKind = MarkPointKind.STATEMENT
    alternative_group: str | None = Field(default=None, pattern=_SLUG)
    accept_range: AcceptRange | None = None
    solution_step: str | None = Field(default=None, pattern=_IDENT)
    note: str | None = None


class Part(Model):
    id: str = Field(pattern=_SLUG)
    label: str = Field(pattern=r"^[a-h](\.(i|ii|iii|iv|v))?$")
    body: Doc
    marks: int = Field(ge=1, le=MAX_PART_MARKS)
    command_term: str | None = Field(default=None, pattern=r"^[a-z][a-z_]*$")
    answer_type: AnswerType
    assessment_objective: Literal[1, 2, 3] | None = None
    level_content: LevelContent = LevelContent.SL_CORE
    syllabus_node: str = Field(min_length=1)
    stimulus_refs: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    ecf_from: tuple[str, ...] = ()
    mark_points: tuple[MarkPoint, ...] = Field(min_length=1)

    @property
    def awardable_marks(self) -> int:
        """Marks available from the mark points, counting each group of alternatives once."""
        groups = {p.alternative_group for p in self.mark_points if p.alternative_group}
        ungrouped = sum(1 for p in self.mark_points if not p.alternative_group)
        return ungrouped + len(groups)

    @model_validator(mode="after")
    def _mark_points_cover_marks(self) -> Self:
        ids = [p.id for p in self.mark_points]
        if len(ids) != len(set(ids)):
            raise ValueError(f"part {self.label}: duplicate mark point ids")
        # More points than marks is allowed (a "max" part); fewer is not.
        if self.awardable_marks < self.marks:
            raise ValueError(
                f"part {self.label}: {self.awardable_marks} awardable mark points "
                f"for {self.marks} marks"
            )
        return self


class Parameter(Model):
    name: str = Field(pattern=_IDENT)
    value: str = Field(pattern=r"^-?\d+(\.\d+)?([eE]-?\d+)?$")
    unit: str = ""


class Constant(Model):
    name: str = Field(pattern=_IDENT)
    ref: str = Field(min_length=1)


class Step(Model):
    id: str = Field(pattern=_IDENT)
    name: str = Field(pattern=_IDENT)
    expr: str = Field(min_length=1)
    unit: str = ""


class AnswerBinding(Model):
    part_id: str
    step: str


class SolutionModel(Model):
    """Declarative formula chain, stored as data. It is not evaluated here (no interpreter yet)."""

    parameters: tuple[Parameter, ...] = ()
    constants: tuple[Constant, ...] = ()
    steps: tuple[Step, ...] = ()
    answers: tuple[AnswerBinding, ...] = ()
    verified: bool = False

    @model_validator(mode="after")
    def _names_unique_and_bound(self) -> Self:
        names = [p.name for p in self.parameters] + [c.name for c in self.constants]
        names += [s.name for s in self.steps]
        if len(names) != len(set(names)):
            raise ValueError("solution model: duplicate parameter, constant or step name")
        step_ids = [s.id for s in self.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("solution model: duplicate step id")
        for binding in self.answers:
            if binding.step not in step_ids:
                raise ValueError(f"solution model: answer bound to unknown step {binding.step}")
        return self


class QuestionDocument(Model):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    question_class: QuestionClass
    exam_section: str = Field(pattern=_SLUG)
    levels: frozenset[Level] = Field(min_length=1)
    language: str = Field(default="en", pattern=r"^[a-z]{2}$")
    calculator: bool = True
    primary_syllabus_node: str = Field(min_length=1)
    secondary_syllabus_nodes: tuple[str, ...] = ()
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
        yield self.stem
        for part in self.parts:
            yield part.body

    def inline_sequences(self) -> Iterator[tuple[Inline, ...]]:
        if self.mcq:
            for option in self.mcq.options:
                yield option.content
        for part in self.parts:
            for point in part.mark_points:
                yield point.content

    def latex_sources(self) -> Iterator[str]:
        for doc in self.docs():
            yield from iter_latex(doc)
        for sequence in self.inline_sequences():
            for inline in sequence:
                if isinstance(inline, MathInline):
                    yield inline.attrs.latex

    def quantities(self) -> Iterator[Quantity]:
        for doc in self.docs():
            for inline in iter_inlines(doc):
                if isinstance(inline, Quantity):
                    yield inline
        for sequence in self.inline_sequences():
            for inline in sequence:
                if isinstance(inline, Quantity):
                    yield inline

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
        labels = [p.label for p in self.parts]
        if len(ids) != len(set(ids)) or len(labels) != len(set(labels)):
            raise ValueError("duplicate part id or label")
        seen: set[str] = set()
        for part in self.parts:
            for ref in (*part.depends_on, *part.ecf_from):
                if ref not in seen:
                    raise ValueError(
                        f"part {part.label} refers to {ref}, which is not an earlier part"
                    )
            seen.add(part.id)
        if Level.SL in self.levels and any(p.level_content is LevelContent.AHL for p in self.parts):
            raise ValueError("a question usable at SL cannot contain an additional-HL part")
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
        model = self.solution_model
        if model is None:
            return self
        part_ids = {p.id for p in self.parts}
        step_ids = {s.id for s in model.steps}
        for binding in model.answers:
            if binding.part_id not in part_ids:
                raise ValueError(f"solution model: answer bound to unknown part {binding.part_id}")
        for part in self.parts:
            for point in part.mark_points:
                if point.solution_step is not None and point.solution_step not in step_ids:
                    raise ValueError(f"mark point {point.id}: unknown solution step")
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
