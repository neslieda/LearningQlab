"""Content service: the only way other modules create, change, publish or read questions.

Lifecycle and rules: docs/DOMAIN_MODEL.md section 4, docs/DATA_ARCHITECTURE.md section 2.2.
Functions run inside the caller's transaction (they flush, never commit) and write one audit
entry per change. `actor` is the opaque account identifier written to the audit log; which
roles may call what is decided by the authorization layer, not here.

Rights are fail-closed (CLAUDE.md rule 2): every function except `withdraw`, `reject` and
`request_changes`, which only ever restrict, needs the question's rights record to permit
display to everyone right now. A write that lacks it raises `qlab.rights.service.RightsDenied`;
a read behaves as if the question did not exist.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy.orm import Session

from qlab.content.schema import QuestionDocument

MAX_REASON_LENGTH = 500


class Origin(StrEnum):
    AUTHORED = "authored"
    GENERATED = "generated"
    SOURCE_ORIGINAL = "source_original"


class VersionStatus(StrEnum):
    DRAFT = "draft"
    AUTO_CHECKING = "auto_checking"
    NEEDS_FIX = "needs_fix"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    WITHDRAWN = "withdrawn"
    REJECTED = "rejected"


class Severity(StrEnum):
    CRITICAL = "critical"
    WARNING = "warning"


class Outcome(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"


class ContentError(Exception):
    """Base class for the errors below."""


class NotFound(ContentError):
    """No such question or version, or the caller may not know that it exists."""


class OriginClosed(ContentError):
    """The origin is not accepted yet: only `authored` content is (D-52)."""


class InvalidDocument(ContentError):
    """The document uses labels the syllabus version does not define. `errors` lists them."""

    def __init__(self, errors: tuple[str, ...]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class InvalidTransition(ContentError):
    """The version is not in a state from which this operation is allowed."""


class WorkingVersionExists(ContentError):
    """The question already has a version that is being worked on."""


class NotPublishable(ContentError):
    """Publishing was refused. `reasons` holds one or more of: `critical_checks_failed`,
    `unverified_visuals`, `rights_denied`."""

    def __init__(self, reasons: tuple[str, ...]) -> None:
        super().__init__(", ".join(reasons))
        self.reasons = reasons


@dataclass(frozen=True)
class QuestionView:
    id: uuid.UUID
    origin: Origin
    rights_record_id: uuid.UUID
    syllabus_version_id: uuid.UUID
    created_by: str
    created_at: datetime


@dataclass(frozen=True)
class CheckResult:
    code: str
    severity: Severity
    outcome: Outcome
    detail: dict[str, Any]


@dataclass(frozen=True)
class QuestionVersionView:
    id: uuid.UUID
    question_id: uuid.UUID
    version_no: int
    status: VersionStatus
    document: QuestionDocument
    content_sha256: str
    has_unverified_visuals: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


def content_sha256(document: QuestionDocument) -> str:
    """SHA-256 (hex) of the document's canonical JSON, `document.model_dump_json()`."""
    return hashlib.sha256(document.model_dump_json().encode()).hexdigest()


# --- internals ----------------------------------------------------------------------------


# --- writing ------------------------------------------------------------------------------


def create_question(
    session: Session,
    *,
    actor: str,
    document: QuestionDocument,
    rights_record_id: uuid.UUID,
    syllabus_version_id: uuid.UUID,
    origin: Origin = Origin.AUTHORED,
) -> QuestionVersionView:
    """Create a question and its first version (version 1, `draft`).

    - `origin` other than `authored` raises OriginClosed (D-52), before anything else.
    - The rights record must permit display to everyone now, else RightsDenied.
    - Unknown `syllabus_version_id` raises LookupError.
    - The document's exam section, command terms and syllabus nodes (leaf nodes only) must
      belong to the syllabus version, else InvalidDocument listing every problem.

    Nothing is written when an error is raised. On success the derived rows exist (one `part`
    per part, or a single one with key "mcq" for a multiple-choice question; one `mark_point`
    per mark point; one `question_version_syllabus` per node with the primary flagged) and the
    audit log has `question_version.created` for the new version.
    """
    raise NotImplementedError


def update_draft(
    session: Session, *, actor: str, version_id: uuid.UUID, document: QuestionDocument
) -> QuestionVersionView:
    """Replace the content of a `draft` or `needs_fix` version; the result is `draft`.

    Any other status raises InvalidTransition (a published version is corrected with
    `start_revision`). Same rights and vocabulary rules as `create_question`. The derived rows
    are rebuilt and earlier check results are discarded. Audit: `question_version.updated`
    with the new content hash and `previous_content_sha256`. Unknown id: NotFound.
    """
    raise NotImplementedError


def record_check(
    session: Session, *, actor: str, version_id: uuid.UUID, result: CheckResult
) -> None:
    """Store the result of an external check, replacing an earlier result with the same code.

    Allowed while the version is `draft`, `needs_fix` or `auto_checking`; otherwise
    InvalidTransition. Results are discarded when the content changes. A failed critical
    result sends the next `submit` to `needs_fix` and blocks publishing. Audit:
    `question_version.check_recorded`. Unknown id: NotFound.
    """
    raise NotImplementedError


def submit(session: Session, *, actor: str, version_id: uuid.UUID) -> QuestionVersionView:
    """Run the automatic checks on a `draft` version and move it on.

    `draft` → `auto_checking` → `in_review` when no critical check has failed, else
    `needs_fix`. The service's own checks (`schema_valid`, `vocabulary_valid`) are run and
    stored; results recorded earlier with `record_check` count too. Unverified visuals do not
    stop a review; they stop publishing. Audit: `question_version.submitted`, then
    `question_version.checks_passed` or `question_version.checks_failed` (with the failed
    codes). Other status: InvalidTransition. Rights as in `create_question`.
    """
    raise NotImplementedError


def request_changes(
    session: Session, *, actor: str, version_id: uuid.UUID, reason: str
) -> QuestionVersionView:
    """Send an `in_review` or `approved` version back: → `needs_fix`, where it can be edited.

    `reason` is required (1 to 500 characters after trimming, else ValueError) and is written
    to the audit entry `question_version.changes_requested`. Other status: InvalidTransition.
    """
    raise NotImplementedError


def approve(session: Session, *, actor: str, version_id: uuid.UUID) -> QuestionVersionView:
    """`in_review` → `approved`. One approval is enough in M1-G (D-53); the approver is the
    audit entry's actor (`question_version.approved`). Other status: InvalidTransition. Rights
    as in `create_question`."""
    raise NotImplementedError


def reject(
    session: Session, *, actor: str, version_id: uuid.UUID, reason: str
) -> QuestionVersionView:
    """`in_review` → `rejected` (final). `reason` as in `request_changes`. Audit:
    `question_version.rejected`. Other status: InvalidTransition."""
    raise NotImplementedError


def publish(session: Session, *, actor: str, version_id: uuid.UUID) -> QuestionVersionView:
    """`approved` → `published`. The backend refuses, whatever the caller is (rule 8):

    - a status other than `approved` raises InvalidTransition;
    - otherwise NotPublishable with every reason that applies: `critical_checks_failed`,
      `unverified_visuals` (the document has stimuli; no asset can be verified yet, D-49),
      `rights_denied`.

    If the question already has a published version, that one becomes `withdrawn` in the same
    transaction (audit `question_version.superseded`). Audit: `question_version.published`.
    """
    raise NotImplementedError


def withdraw(
    session: Session, *, actor: str, version_id: uuid.UUID, reason: str
) -> QuestionVersionView:
    """`published` → `withdrawn`. Always possible, also when rights have been revoked.
    `reason` as in `request_changes`. Audit: `question_version.withdrawn`."""
    raise NotImplementedError


def republish(session: Session, *, actor: str, version_id: uuid.UUID) -> QuestionVersionView:
    """`withdrawn` → `published`, under the same conditions as `publish`.

    Refused with InvalidTransition when the question has a published version or a newer
    version than this one. Audit: `question_version.republished`.
    """
    raise NotImplementedError


def start_revision(session: Session, *, actor: str, question_id: uuid.UUID) -> QuestionVersionView:
    """Open a new `draft` version to correct a question (CLAUDE.md rule 7).

    The new version copies the document of the published version, or, if none is published,
    of the latest version; its number is the highest existing number plus one. The source
    version is not changed. If the question already has a working version (`draft`,
    `auto_checking`, `needs_fix`, `in_review` or `approved`) WorkingVersionExists is raised.
    Rights as in `create_question`. Audit: `question_version.created` with `based_on`.
    Unknown id: NotFound.
    """
    raise NotImplementedError


# --- reading ------------------------------------------------------------------------------


def get_question(session: Session, question_id: uuid.UUID) -> QuestionView:
    """The question. NotFound when it does not exist or its rights do not permit display."""
    raise NotImplementedError


def get_version(session: Session, version_id: uuid.UUID) -> QuestionVersionView:
    """Any version, in any status: the staff view. NotFound when it does not exist or the
    question's rights do not permit display."""
    raise NotImplementedError


def list_versions(session: Session, question_id: uuid.UUID) -> list[QuestionVersionView]:
    """All versions of a question, oldest first. NotFound as in `get_question`."""
    raise NotImplementedError


def get_published_version(session: Session, question_id: uuid.UUID) -> QuestionVersionView:
    """The published version of a question: the only view a learner may be given.

    NotFound when the question does not exist, has no published version (a draft, approved or
    withdrawn version is never returned), or its rights do not permit display.
    """
    raise NotImplementedError


def get_checks(session: Session, version_id: uuid.UUID) -> list[CheckResult]:
    """Check results stored for the version's current content, by code. NotFound as in
    `get_version`."""
    raise NotImplementedError
