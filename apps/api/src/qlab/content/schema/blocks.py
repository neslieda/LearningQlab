"""Rich-content block nodes (ProseMirror-compatible shape: type / attrs / content / text / marks).

Specification: docs/DATA_ARCHITECTURE.md section 3.
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class Node(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class TextMark(StrEnum):
    BOLD = "bold"
    ITALIC = "italic"
    SUB = "sub"
    SUP = "sup"
    # Mark-scheme conventions: words not needed for the mark, and words essential for it.
    OPTIONAL = "optional"
    ESSENTIAL = "essential"


class Text(Node):
    type: Literal["text"] = "text"
    text: str = Field(min_length=1)
    marks: tuple[TextMark, ...] = ()


class MathAttrs(Node):
    latex: str = Field(min_length=1)


class MathInline(Node):
    type: Literal["math_inline"] = "math_inline"
    attrs: MathAttrs


class QuantityAttrs(Node):
    # Kept as text so that significant figures survive ("20" and "20.0" differ).
    value: str = Field(pattern=r"^-?\d+(\.\d+)?([eE]-?\d+)?$")
    unit: str = ""
    param: str | None = Field(default=None, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    sig_figs: int | None = Field(default=None, ge=1, le=6)
    uncertainty: str | None = Field(default=None, pattern=r"^\d+(\.\d+)?([eE]-?\d+)?$")


class Quantity(Node):
    type: Literal["quantity"] = "quantity"
    attrs: QuantityAttrs


Inline = Annotated[Text | MathInline | Quantity, Field(discriminator="type")]


class Paragraph(Node):
    type: Literal["paragraph"] = "paragraph"
    content: tuple[Inline, ...] = ()


class MathBlock(Node):
    type: Literal["math_block"] = "math_block"
    attrs: MathAttrs


class TableCellAttrs(Node):
    header: bool = False
    colspan: int = Field(default=1, ge=1)
    rowspan: int = Field(default=1, ge=1)


class TableCell(Node):
    type: Literal["table_cell"] = "table_cell"
    attrs: TableCellAttrs = TableCellAttrs()
    content: tuple[Inline, ...] = ()


class TableRow(Node):
    type: Literal["table_row"] = "table_row"
    content: tuple[TableCell, ...] = Field(min_length=1)


class Table(Node):
    type: Literal["table"] = "table"
    content: tuple[TableRow, ...] = Field(min_length=1)


class FigureAttrs(Node):
    stimulus_id: str = Field(min_length=1)


class Figure(Node):
    """Placement of a stimulus in the text; the stimulus lives in QuestionDocument.stimuli."""

    type: Literal["figure"] = "figure"
    attrs: FigureAttrs


class ListItem(Node):
    type: Literal["list_item"] = "list_item"
    content: tuple[Paragraph, ...] = Field(min_length=1)


class ListAttrs(Node):
    ordered: bool = False


class BulletList(Node):
    type: Literal["list"] = "list"
    attrs: ListAttrs = ListAttrs()
    content: tuple[ListItem, ...] = Field(min_length=1)


Block = Annotated[Paragraph | MathBlock | Table | Figure | BulletList, Field(discriminator="type")]


class Doc(Node):
    type: Literal["doc"] = "doc"
    content: tuple[Block, ...] = ()


def iter_inlines(doc: Doc) -> Iterator[Text | MathInline | Quantity]:
    for block in doc.content:
        if isinstance(block, Paragraph):
            yield from block.content
        elif isinstance(block, Table):
            for row in block.content:
                for cell in row.content:
                    yield from cell.content
        elif isinstance(block, BulletList):
            for item in block.content:
                for paragraph in item.content:
                    yield from paragraph.content


def iter_latex(doc: Doc) -> Iterator[str]:
    """Every LaTeX source string in the document, for the save-time render check."""
    for block in doc.content:
        if isinstance(block, MathBlock):
            yield block.attrs.latex
    for inline in iter_inlines(doc):
        if isinstance(inline, MathInline):
            yield inline.attrs.latex


def iter_figure_refs(doc: Doc) -> Iterator[str]:
    for block in doc.content:
        if isinstance(block, Figure):
            yield block.attrs.stimulus_id
