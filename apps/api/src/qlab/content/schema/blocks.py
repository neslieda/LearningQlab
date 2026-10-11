"""Rich-content nodes in ProseMirror JSON shape (type / attrs / content / text / marks).

Specification: docs/DATA_ARCHITECTURE.md section 3.5. `type` is always required so that stored
documents and generated client types can discriminate on it.
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

NUMBER_PATTERN = r"^-?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?$"
UNSIGNED_NUMBER_PATTERN = r"^[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?$"
# Unit expressions are checked for shape only; a unit grammar comes with the formula interpreter.
UNIT_PATTERN = r"^([A-Za-zµΩ°%]([A-Za-zµΩ°%0-9 /*^().-]*[A-Za-zµΩ°%0-9/*^().-])?)?$"


class Node(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class MarkType(StrEnum):
    BOLD = "bold"
    ITALIC = "italic"
    SUB = "sub"
    SUP = "sup"
    # Mark-scheme conventions: words not needed for the mark, and words essential for it.
    OPTIONAL = "optional"
    ESSENTIAL = "essential"


_EXCLUSIVE_MARKS = (
    {MarkType.SUB, MarkType.SUP},
    {MarkType.OPTIONAL, MarkType.ESSENTIAL},
)


class Mark(Node):
    type: MarkType


class MarkedNode(Node):
    marks: tuple[Mark, ...] = ()

    @model_validator(mode="after")
    def _marks_consistent(self) -> Self:
        types = [m.type for m in self.marks]
        if len(types) != len(set(types)):
            raise ValueError("duplicate mark on a node")
        for pair in _EXCLUSIVE_MARKS:
            if pair <= set(types):
                raise ValueError("mutually exclusive marks on a node")
        return self


class Text(MarkedNode):
    type: Literal["text"]
    text: str = Field(min_length=1)


class MathAttrs(Node):
    latex: str = Field(min_length=1)


class MathInline(MarkedNode):
    type: Literal["math_inline"]
    attrs: MathAttrs


class QuantityAttrs(Node):
    # Kept as text so that significant figures survive ("20" and "20.0" differ).
    value: str = Field(pattern=NUMBER_PATTERN)
    unit: str = Field(default="", pattern=UNIT_PATTERN)
    param: str | None = Field(default=None, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    uncertainty: str | None = Field(default=None, pattern=UNSIGNED_NUMBER_PATTERN)


class Quantity(MarkedNode):
    type: Literal["quantity"]
    attrs: QuantityAttrs


class HardBreak(Node):
    type: Literal["hard_break"]


Inline = Annotated[Text | MathInline | Quantity | HardBreak, Field(discriminator="type")]


class Paragraph(Node):
    type: Literal["paragraph"]
    content: tuple[Inline, ...] = ()


class MathBlock(Node):
    type: Literal["math_block"]
    attrs: MathAttrs


class CellAttrs(Node):
    colspan: int = Field(default=1, ge=1, le=12)
    rowspan: int = Field(default=1, ge=1, le=50)


class TableCell(Node):
    type: Literal["table_cell"]
    attrs: CellAttrs = CellAttrs()
    content: tuple[Paragraph, ...] = Field(min_length=1)


class TableHeader(Node):
    type: Literal["table_header"]
    attrs: CellAttrs = CellAttrs()
    content: tuple[Paragraph, ...] = Field(min_length=1)


Cell = Annotated[TableCell | TableHeader, Field(discriminator="type")]


class TableRow(Node):
    type: Literal["table_row"]
    content: tuple[Cell, ...] = Field(min_length=1)


class Table(Node):
    type: Literal["table"]
    content: tuple[TableRow, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _rectangular(self) -> Self:
        if any(c.attrs.rowspan > 1 for row in self.content for c in row.content):
            return self  # row spans make per-row widths differ legitimately
        widths = {sum(c.attrs.colspan for c in row.content) for row in self.content}
        if len(widths) > 1:
            raise ValueError("table rows have different widths")
        return self


class FigureAttrs(Node):
    stimulus_id: str = Field(min_length=1)


class Figure(Node):
    """Placement of a stimulus in the text; the stimulus lives in QuestionDocument.stimuli."""

    type: Literal["figure"]
    attrs: FigureAttrs


class ListItem(Node):
    type: Literal["list_item"]
    content: tuple[Paragraph, ...] = Field(min_length=1)


class BulletList(Node):
    type: Literal["bullet_list"]
    content: tuple[ListItem, ...] = Field(min_length=1)


class OrderedList(Node):
    type: Literal["ordered_list"]
    content: tuple[ListItem, ...] = Field(min_length=1)


Block = Annotated[
    Paragraph | MathBlock | Table | Figure | BulletList | OrderedList,
    Field(discriminator="type"),
]


class Doc(Node):
    type: Literal["doc"]
    content: tuple[Block, ...] = Field(min_length=1)


def _paragraphs(doc: Doc) -> Iterator[Paragraph]:
    for block in doc.content:
        if isinstance(block, Paragraph):
            yield block
        elif isinstance(block, Table):
            for row in block.content:
                for cell in row.content:
                    yield from cell.content
        elif isinstance(block, BulletList | OrderedList):
            for item in block.content:
                yield from item.content


def iter_inlines(doc: Doc) -> Iterator[Text | MathInline | Quantity | HardBreak]:
    for paragraph in _paragraphs(doc):
        yield from paragraph.content


def iter_latex(doc: Doc) -> Iterator[str]:
    """Every LaTeX source string in the document, for the save-time render check."""
    for block in doc.content:
        if isinstance(block, MathBlock):
            yield block.attrs.latex
    for inline in iter_inlines(doc):
        if isinstance(inline, MathInline):
            yield inline.attrs.latex


def iter_quantities(doc: Doc) -> Iterator[Quantity]:
    for inline in iter_inlines(doc):
        if isinstance(inline, Quantity):
            yield inline


def iter_figure_refs(doc: Doc) -> Iterator[str]:
    for block in doc.content:
        if isinstance(block, Figure):
            yield block.attrs.stimulus_id


def is_blank(doc: Doc) -> bool:
    """True when the document has no visible content (only empty or whitespace paragraphs)."""
    for block in doc.content:
        if not isinstance(block, Paragraph):
            return False
        for inline in block.content:
            if not isinstance(inline, Text | HardBreak) or (
                isinstance(inline, Text) and inline.text.strip()
            ):
                return False
    return True
