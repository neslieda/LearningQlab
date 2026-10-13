"""Shape of a converted pilot file (content/pilot/<stem>.json); see docs/pilot/IMPORT_RULES.md."""

from __future__ import annotations

from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from qlab.content.schema import QuestionDocument

SourceRef = Annotated[str, StringConstraints(pattern=r"^pilot/[a-z0-9][a-z0-9-]*#[1-9][0-9]*$")]


def source_ref(stem: str, number: int) -> str:
    """The stable key of a pilot question: `pilot/<file stem>#<question number>`."""
    return f"pilot/{stem}#{number}"


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class PilotQuestion(Model):
    source_ref: SourceRef
    number: int = Field(ge=1)
    document: QuestionDocument


class PilotFile(Model):
    # Repository-relative path of the Markdown file and the SHA-256 of its bytes.
    source_file: str = Field(pattern=r"^docs/pilot/[a-z0-9-]+-pilot-questions\.md$")
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    questions: tuple[PilotQuestion, ...] = Field(min_length=1)

    @property
    def stem(self) -> str:
        return self.source_file.removeprefix("docs/pilot/").removesuffix("-pilot-questions.md")

    @model_validator(mode="after")
    def _refs_consistent(self) -> Self:
        expected = [source_ref(self.stem, q.number) for q in self.questions]
        if [q.source_ref for q in self.questions] != expected:
            raise ValueError("source_ref does not match the file stem and question number")
        if len(set(expected)) != len(expected):
            raise ValueError("duplicate question number")
        return self

    def to_json(self) -> str:
        """The exact text written to disk: stable, readable, newline-terminated."""
        return self.model_dump_json(indent=1) + "\n"
