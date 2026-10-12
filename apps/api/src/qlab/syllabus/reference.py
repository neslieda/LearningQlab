"""Shape of a syllabus reference file (content/reference/*-syllabus.json).

One file describes one syllabus version of one subject: its node tree and its exam format.
Unknown fields are rejected at every level.
"""

from __future__ import annotations

from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Code = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9_]*$")]
NodeCode = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9]+(\.[A-Za-z0-9]+)*$")]
# Reference text is short labels only; the bound keeps anything longer (such as question
# content, CLAUDE.md rule 14) out by construction.
NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]
Label = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Named(Model):
    code: Code
    name: Label


class VersionRef(Model):
    code: Code
    title: Label


class NodeEntry(Model):
    code: NodeCode
    title: Label
    # Code of the parent node; None for a top-level node. A parent is listed before its children.
    parent: NodeCode | None = None
    attributes: dict[Code, Code] = Field(default={}, max_length=8)


class Section(Model):
    code: Code
    title: Label


class ExamFormatDefinition(Model):
    sections: tuple[Section, ...] = Field(min_length=1)
    command_terms: tuple[Code, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique(self) -> Self:
        sections = [s.code for s in self.sections]
        if len(sections) != len(set(sections)):
            raise ValueError("duplicate exam section code")
        if len(self.command_terms) != len(set(self.command_terms)):
            raise ValueError("duplicate command term")
        return self


class ExamFormatEntry(ExamFormatDefinition):
    code: Code


class SyllabusReference(Model):
    status: NonBlank
    program: Named
    subject: Named
    syllabus_version: VersionRef
    nodes: tuple[NodeEntry, ...] = Field(min_length=1)
    exam_format: ExamFormatEntry

    @model_validator(mode="after")
    def _tree_consistent(self) -> Self:
        seen: set[str] = set()
        for node in self.nodes:
            if node.code in seen:
                raise ValueError(f"duplicate node code {node.code}")
            if node.parent is not None and node.parent not in seen:
                raise ValueError(f"node {node.code}: parent {node.parent} is not listed before it")
            seen.add(node.code)
        return self
