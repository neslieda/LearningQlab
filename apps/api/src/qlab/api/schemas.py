"""Request and response types of the API. This file is the contract the OpenAPI document and
the generated client are made from; it is frozen per slice (docs/API_DESIGN.md section 6).

Two families that must never be mixed:

- `Learner*`: what any signed-in account may see of a published question. Built on the server
  from the stored document by an allow-list (docs/slices/M1G-5-YETKILER.md section 4). These
  types have no field for an answer, an explanation, a rationale, an outcome, a stimulus
  description, a staff identifier or rule-filled metadata, and they reject unknown fields, so
  a projection that tries to carry one fails instead of leaking it.
- `Admin*`: the staff view, with the whole document.

Identifiers are prefixed strings (`q_...`, `qv_...`, `acc_...`); see `qlab.api.ids`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from qlab.api import ids
from qlab.content.schema import (
    AcceptRange,
    Doc,
    Level,
    MarkPointKind,
    NoteKind,
    OptionLayout,
    QuestionClass,
    QuestionDocument,
    StimulusKind,
)
from qlab.content.service import MAX_REASON_LENGTH, Origin, Outcome, Severity, VersionStatus
from qlab.organizations.service import Role

MAX_ANSWER_LENGTH = 5000
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

QuestionId = Annotated[str, StringConstraints(pattern=ids.QUESTION_ID_PATTERN)]
QuestionVersionId = Annotated[str, StringConstraints(pattern=ids.QUESTION_VERSION_ID_PATTERN)]
AccountId = Annotated[str, StringConstraints(pattern=ids.ACCOUNT_ID_PATTERN)]
ContentHash = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
Reason = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_REASON_LENGTH)
]
OptionKey = Literal["A", "B", "C", "D"]
PartKey = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9_.-]{0,63}$")]


class Api(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


# --- system -------------------------------------------------------------------------------


class Health(Api):
    status: Literal["ok"]


class Me(Api):
    """The caller. M1-G has no profile, entitlement or quota yet."""

    account_id: AccountId
    roles: tuple[Role, ...] = Field(description="Sorted by name.")


# --- syllabus -----------------------------------------------------------------------------


class SyllabusNodeOut(Api):
    code: str
    title: str
    parent: str | None = Field(description="Code of the parent node; null for a top-level node.")
    is_leaf: bool = Field(description="Questions are tagged with leaf nodes only.")
    attributes: dict[str, str]


class ExamSectionOut(Api):
    code: str
    title: str


class SyllabusOut(Api):
    """One syllabus version: its node tree (parents before children, in syllabus order) and its
    exam format vocabulary."""

    program: str
    subject: str
    version: str
    title: str
    status: str = Field(description="Review status of the reference data, as declared by it.")
    nodes: tuple[SyllabusNodeOut, ...]
    exam_sections: tuple[ExamSectionOut, ...]
    command_terms: tuple[str, ...]


# --- learner view -------------------------------------------------------------------------


class LearnerStimulus(Api):
    """Placeholder for a figure. Its description is staff-only and is not here."""

    id: str
    kind: StimulusKind


class LearnerOption(Api):
    key: OptionKey
    cells: tuple[Doc, ...]


class LearnerMcq(Api):
    option_layout: OptionLayout
    column_headers: tuple[Doc, ...]
    statements: tuple[Doc, ...]
    options: tuple[LearnerOption, ...]


class LearnerPart(Api):
    id: PartKey
    label: str
    lead_in: Doc | None
    body: Doc
    marks: int
    command_term: str | None
    stimulus_refs: tuple[str, ...]


class LearnerQuestionSummary(Api):
    id: QuestionId
    version_id: QuestionVersionId
    question_class: QuestionClass
    exam_section: str
    levels: tuple[Level, ...]
    total_marks: int


class LearnerQuestion(LearnerQuestionSummary):
    """The published version of a question as a learner sees it before answering."""

    stem: Doc
    stimuli: tuple[LearnerStimulus, ...]
    mcq: LearnerMcq | None
    parts: tuple[LearnerPart, ...]


class LearnerQuestionPage(Api):
    items: tuple[LearnerQuestionSummary, ...]
    next_cursor: str | None


class McqAnswer(Api):
    kind: Literal["mcq"]
    selected_key: OptionKey


class WrittenAnswer(Api):
    kind: Literal["written"]
    part_id: PartKey
    text: str = Field(min_length=1, max_length=MAX_ANSWER_LENGTH)

    @field_validator("text")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("an empty answer is not accepted")
        return value


CheckRequest = Annotated[McqAnswer | WrittenAnswer, Field(discriminator="kind")]


class McqCheckResult(Api):
    kind: Literal["mcq"]
    version_id: QuestionVersionId
    correct: bool
    correct_key: OptionKey


class MarkPointOut(Api):
    id: str
    content: Doc
    kind: MarkPointKind
    alternative_group: str | None
    route: str | None
    accept_range: AcceptRange | None


class NoteOut(Api):
    kind: NoteKind
    content: Doc
    mark_point_id: str | None


class LanguageWarning(Api):
    """Help, not a refusal: the mark scheme is returned all the same."""

    code: Literal["answer_not_english"]
    message: str


class WrittenCheckResult(Api):
    """The mark scheme of one part. The answer is not marked (AI marking is M4)."""

    kind: Literal["written"]
    version_id: QuestionVersionId
    part_id: PartKey
    marks: int
    marks_capped: bool
    mark_points: tuple[MarkPointOut, ...]
    notes: tuple[NoteOut, ...]
    language_warning: LanguageWarning | None


CheckResult = Annotated[McqCheckResult | WrittenCheckResult, Field(discriminator="kind")]


# --- staff view ---------------------------------------------------------------------------


class AdminVersionSummary(Api):
    id: QuestionVersionId
    question_id: QuestionId
    version_no: int
    status: VersionStatus
    content_sha256: ContentHash
    question_class: QuestionClass
    exam_section: str
    levels: tuple[Level, ...]
    total_marks: int
    has_unverified_visuals: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


class AdminQuestionSummary(Api):
    id: QuestionId
    origin: Origin
    source_ref: str | None
    created_at: datetime
    latest_version: AdminVersionSummary
    published_version_id: QuestionVersionId | None
    working_version_id: QuestionVersionId | None


class AdminQuestionPage(Api):
    items: tuple[AdminQuestionSummary, ...]
    next_cursor: str | None


class AdminQuestion(Api):
    id: QuestionId
    origin: Origin
    source_ref: str | None
    created_by: str
    created_at: datetime
    versions: tuple[AdminVersionSummary, ...] = Field(description="Oldest first.")


class CheckOut(Api):
    code: str
    severity: Severity
    outcome: Outcome
    detail: dict[str, Any]


class AdminVersion(AdminVersionSummary):
    document: QuestionDocument
    checks: tuple[CheckOut, ...] = Field(
        description="Results stored for the current content, by code."
    )


class HistoryEntry(Api):
    """One audit entry about a version. Fields an action does not carry are null."""

    occurred_at: datetime
    actor: str
    action: str = Field(description="Without the `question_version.` prefix, e.g. `approved`.")
    status: VersionStatus
    previous_status: VersionStatus | None
    content_sha256: ContentHash
    previous_content_sha256: ContentHash | None
    reason: str | None
    failed_checks: tuple[str, ...] | None
    check: str | None
    severity: Severity | None
    outcome: Outcome | None
    based_on: QuestionVersionId | None
    superseded_by: QuestionVersionId | None
    source_ref: str | None
    approver_is_last_editor: bool | None


class History(Api):
    items: tuple[HistoryEntry, ...] = Field(description="Oldest first.")


class VersionStateOut(Api):
    """Where a version stands after a decision. Never carries content (D-56)."""

    id: QuestionVersionId
    question_id: QuestionId
    version_no: int
    status: VersionStatus
    content_sha256: ContentHash


class UpdateDraftRequest(Api):
    document: QuestionDocument


class DecisionRequest(Api):
    """Approve or publish exactly the content the caller looked at (D-56)."""

    expected_content_sha256: ContentHash


class ReasonRequest(Api):
    reason: Reason = Field(description="About the content, never about a person.")


class RepublishRequest(Api):
    expected_content_sha256: ContentHash
    reason: Reason
