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
import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from qlab.audit import service as audit
from qlab.content.models import (
    WORKING_STATUSES,
    MarkPoint,
    Part,
    Question,
    QuestionVersion,
    QuestionVersionCheck,
    QuestionVersionSyllabus,
)
from qlab.content.schema import QuestionDocument
from qlab.rights import service as rights
from qlab.syllabus import service as syllabus

MAX_REASON_LENGTH = 500
_CHECK_CODE = re.compile(r"[a-z][a-z0-9_]*")


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


def _view(row: QuestionVersion) -> QuestionVersionView:
    return QuestionVersionView(
        id=row.id,
        question_id=row.question_id,
        version_no=row.version_no,
        status=VersionStatus(row.status),
        document=QuestionDocument.model_validate(row.document),
        content_sha256=row.content_sha256,
        has_unverified_visuals=row.has_unverified_visuals,
        created_by=row.created_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _question_view(row: Question) -> QuestionView:
    return QuestionView(
        id=row.id,
        origin=Origin(row.origin),
        rights_record_id=row.rights_record_id,
        syllabus_version_id=row.syllabus_version_id,
        created_by=row.created_by,
        created_at=row.created_at,
    )


def _displayable(session: Session, question: Question) -> bool:
    return rights.is_permitted(session, question.rights_record_id, rights.Purpose.DISPLAY)


def _locked(session: Session, version_id: uuid.UUID) -> tuple[QuestionVersion, Question]:
    """The version, locked for update, and its question."""
    version = session.get(QuestionVersion, version_id, with_for_update=True, populate_existing=True)
    if version is None:
        raise NotFound(f"question version {version_id}")
    question = session.get(Question, version.question_id)
    if question is None:  # the foreign key makes this unreachable
        raise NotFound(f"question {version.question_id}")
    return version, question


def _expect(version: QuestionVersion, *allowed: VersionStatus) -> None:
    if version.status not in allowed:
        expected = " or ".join(allowed)
        raise InvalidTransition(f"version is {version.status}; expected {expected}")


def _reason(reason: str) -> str:
    reason = reason.strip()
    if not reason or len(reason) > MAX_REASON_LENGTH:
        raise ValueError(f"a reason of 1 to {MAX_REASON_LENGTH} characters is required")
    return reason


def _audit(
    session: Session, actor: str, action: str, version: QuestionVersion, **data: object
) -> None:
    audit.record(
        session,
        actor=actor,
        action=f"question_version.{action}",
        entity_type="question_version",
        entity_id=str(version.id),
        data={
            "question_id": str(version.question_id),
            "version_no": version.version_no,
            "status": version.status,
            "content_sha256": version.content_sha256,
            **data,
        },
    )


def _move(
    session: Session,
    actor: str,
    version: QuestionVersion,
    to: VersionStatus,
    action: str,
    **data: object,
) -> None:
    previous = version.status
    version.status = to.value
    session.flush()
    _audit(session, actor, action, version, previous_status=previous, **data)


def _vocabulary_errors(
    document: QuestionDocument, vocabulary: syllabus.Vocabulary
) -> tuple[str, ...]:
    errors: list[str] = []
    if document.exam_section not in vocabulary.exam_sections:
        errors.append(f"unknown exam section {document.exam_section!r}")
    nodes = (document.primary_syllabus_node, *document.secondary_syllabus_nodes)
    for node in nodes:
        if node not in vocabulary.leaf_node_codes:
            errors.append(f"unknown or non-leaf syllabus node {node!r}")
    for part in document.parts:
        if part.command_term is not None and part.command_term not in vocabulary.command_terms:
            errors.append(f"part {part.label}: unknown command term {part.command_term!r}")
    return tuple(errors)


def _write_content(
    session: Session, version: QuestionVersion, question: Question, document: QuestionDocument
) -> None:
    """Store the document on the version and rebuild every row derived from it."""
    vocabulary = syllabus.get_vocabulary(session, question.syllabus_version_id)
    errors = _vocabulary_errors(document, vocabulary)
    if errors:
        raise InvalidDocument(errors)
    nodes = (document.primary_syllabus_node, *document.secondary_syllabus_nodes)
    node_ids = syllabus.node_ids(session, question.syllabus_version_id, frozenset(nodes))

    version.schema_version = document.schema_version
    version.document = document.model_dump(mode="json")
    version.content_sha256 = content_sha256(document)
    version.question_class = document.question_class.value
    version.exam_section = document.exam_section
    version.levels = [level.value for level in document.levels]
    version.total_marks = document.total_marks
    session.add(version)
    session.flush()

    # Results of checks describe the previous content.
    session.execute(
        delete(QuestionVersionCheck).where(QuestionVersionCheck.question_version_id == version.id)
    )
    part_ids = select(Part.id).where(Part.question_version_id == version.id)
    session.execute(delete(MarkPoint).where(MarkPoint.part_id.in_(part_ids)))
    session.execute(delete(Part).where(Part.question_version_id == version.id))
    session.execute(
        delete(QuestionVersionSyllabus).where(
            QuestionVersionSyllabus.question_version_id == version.id
        )
    )
    for code in nodes:
        session.add(
            QuestionVersionSyllabus(
                question_version_id=version.id,
                syllabus_node_id=node_ids[code],
                is_primary=code == document.primary_syllabus_node,
            )
        )
    if document.mcq is not None:
        session.add(
            Part(
                question_version_id=version.id,
                position=0,
                part_key="mcq",
                label=None,
                marks=document.total_marks,
                answer_type="mcq",
            )
        )
    for position, part in enumerate(document.parts):
        row = Part(
            question_version_id=version.id,
            position=position,
            part_key=part.id,
            label=part.label,
            marks=part.marks,
            answer_type=part.answer_type.value,
        )
        session.add(row)
        session.flush()
        for point_position, point in enumerate(part.mark_points):
            session.add(
                MarkPoint(
                    part_id=row.id,
                    position=point_position,
                    point_key=point.id,
                    kind=point.kind.value,
                    alternative_group=point.alternative_group,
                    route=point.route,
                )
            )
    session.flush()
    session.refresh(version)


def _store_check(session: Session, version_id: uuid.UUID, result: CheckResult) -> None:
    session.execute(
        delete(QuestionVersionCheck).where(
            QuestionVersionCheck.question_version_id == version_id,
            QuestionVersionCheck.check_code == result.code,
        )
    )
    session.add(
        QuestionVersionCheck(
            question_version_id=version_id,
            check_code=result.code,
            severity=result.severity.value,
            outcome=result.outcome.value,
            detail=result.detail,
        )
    )
    session.flush()


def _failed_critical(session: Session, version_id: uuid.UUID) -> list[str]:
    return list(
        session.scalars(
            select(QuestionVersionCheck.check_code)
            .where(
                QuestionVersionCheck.question_version_id == version_id,
                QuestionVersionCheck.severity == Severity.CRITICAL.value,
                QuestionVersionCheck.outcome == Outcome.FAILED.value,
            )
            .order_by(QuestionVersionCheck.check_code)
        )
    )


def _check_schema(session: Session, version: QuestionVersion, question: Question) -> CheckResult:
    try:
        QuestionDocument.model_validate(version.document)
    except ValueError as error:
        return CheckResult(
            "schema_valid", Severity.CRITICAL, Outcome.FAILED, {"error": str(error)[:500]}
        )
    return CheckResult("schema_valid", Severity.CRITICAL, Outcome.PASSED, {})


def _check_vocabulary(
    session: Session, version: QuestionVersion, question: Question
) -> CheckResult:
    try:
        document = QuestionDocument.model_validate(version.document)
    except ValueError:
        return CheckResult("vocabulary_valid", Severity.CRITICAL, Outcome.NOT_APPLICABLE, {})
    errors = _vocabulary_errors(
        document, syllabus.get_vocabulary(session, question.syllabus_version_id)
    )
    outcome = Outcome.FAILED if errors else Outcome.PASSED
    return CheckResult("vocabulary_valid", Severity.CRITICAL, outcome, {"errors": list(errors)})


# The checks `submit` runs itself. Later slices append to this list (KaTeX rendering) or record
# results from outside with `record_check` (the verification pipeline).
_OWN_CHECKS: list[Callable[[Session, QuestionVersion, Question], CheckResult]] = [
    _check_schema,
    _check_vocabulary,
]


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
    per mark point, none for multiple choice; positions count from 0; one
    `question_version_syllabus` per node with the primary flagged) and the
    audit log has `question_version.created` for the new version.
    """
    if Origin(origin) is not Origin.AUTHORED:
        raise OriginClosed(f"origin {Origin(origin).value} is not accepted yet")
    rights.require(session, rights_record_id, rights.Purpose.DISPLAY)
    syllabus.get_vocabulary(session, syllabus_version_id)
    with session.begin_nested():
        question = Question(
            origin=Origin.AUTHORED.value,
            rights_record_id=rights_record_id,
            syllabus_version_id=syllabus_version_id,
            created_by=actor,
        )
        session.add(question)
        session.flush()
        version = QuestionVersion(question_id=question.id, version_no=1, created_by=actor)
        _write_content(session, version, question, document)
        _audit(session, actor, "created", version)
    return _view(version)


def update_draft(
    session: Session, *, actor: str, version_id: uuid.UUID, document: QuestionDocument
) -> QuestionVersionView:
    """Replace the content of a `draft` or `needs_fix` version; the result is `draft`.

    Any other status raises InvalidTransition (a published version is corrected with
    `start_revision`). Same rights and vocabulary rules as `create_question`. The derived rows
    are rebuilt and earlier check results are discarded. Audit: `question_version.updated`
    with the new content hash and `previous_content_sha256`. Unknown id: NotFound.
    """
    version, question = _locked(session, version_id)
    _expect(version, VersionStatus.DRAFT, VersionStatus.NEEDS_FIX)
    rights.require(session, question.rights_record_id, rights.Purpose.DISPLAY)
    previous_status, previous_hash = version.status, version.content_sha256
    with session.begin_nested():
        version.status = VersionStatus.DRAFT.value
        _write_content(session, version, question, document)
        _audit(
            session,
            actor,
            "updated",
            version,
            previous_status=previous_status,
            previous_content_sha256=previous_hash,
        )
    return _view(version)


def record_check(
    session: Session, *, actor: str, version_id: uuid.UUID, result: CheckResult
) -> None:
    """Store the result of an external check, replacing an earlier result with the same code.

    Allowed while the version is `draft`, `needs_fix` or `auto_checking`; otherwise
    InvalidTransition. Results are discarded when the content changes. A failed critical
    result sends the next `submit` to `needs_fix` and blocks publishing. Audit:
    `question_version.check_recorded`. Unknown id: NotFound. A code that is not a lower-case
    identifier raises ValueError.
    """
    if not _CHECK_CODE.fullmatch(result.code):
        raise ValueError(f"check code {result.code!r} is not a lower-case identifier")
    version, _ = _locked(session, version_id)
    _expect(version, VersionStatus.DRAFT, VersionStatus.NEEDS_FIX, VersionStatus.AUTO_CHECKING)
    _store_check(session, version.id, result)
    _audit(
        session,
        actor,
        "check_recorded",
        version,
        check=result.code,
        severity=result.severity.value,
        outcome=result.outcome.value,
    )


def submit(session: Session, *, actor: str, version_id: uuid.UUID) -> QuestionVersionView:
    """Run the automatic checks on a `draft` version and move it on.

    `draft` → `auto_checking` → `in_review` when no critical check has failed, else
    `needs_fix`. The service's own checks (`schema_valid`, `vocabulary_valid`) are run and
    stored; results recorded earlier with `record_check` count too. Unverified visuals do not
    stop a review; they stop publishing. Audit: `question_version.submitted`, then
    `question_version.checks_passed` or `question_version.checks_failed` (with the failed
    codes). Other status: InvalidTransition. Rights as in `create_question`.
    """
    version, question = _locked(session, version_id)
    _expect(version, VersionStatus.DRAFT)
    rights.require(session, question.rights_record_id, rights.Purpose.DISPLAY)
    _move(session, actor, version, VersionStatus.AUTO_CHECKING, "submitted")
    for check in _OWN_CHECKS:
        _store_check(session, version.id, check(session, version, question))
    failed = _failed_critical(session, version.id)
    if failed:
        _move(session, actor, version, VersionStatus.NEEDS_FIX, "checks_failed", failed=failed)
    else:
        _move(session, actor, version, VersionStatus.IN_REVIEW, "checks_passed")
    return _view(version)


def request_changes(
    session: Session, *, actor: str, version_id: uuid.UUID, reason: str
) -> QuestionVersionView:
    """Send an `in_review` or `approved` version back: → `needs_fix`, where it can be edited.

    `reason` is required (1 to 500 characters after trimming, else ValueError) and is written
    to the audit entry `question_version.changes_requested`. Other status: InvalidTransition.
    """
    reason = _reason(reason)
    version, _ = _locked(session, version_id)
    _expect(version, VersionStatus.IN_REVIEW, VersionStatus.APPROVED)
    _move(session, actor, version, VersionStatus.NEEDS_FIX, "changes_requested", reason=reason)
    return _view(version)


def approve(session: Session, *, actor: str, version_id: uuid.UUID) -> QuestionVersionView:
    """`in_review` → `approved`. One approval is enough in M1-G (D-53); the approver is the
    audit entry's actor (`question_version.approved`). Other status: InvalidTransition. Rights
    as in `create_question`."""
    version, question = _locked(session, version_id)
    _expect(version, VersionStatus.IN_REVIEW)
    rights.require(session, question.rights_record_id, rights.Purpose.DISPLAY)
    _move(session, actor, version, VersionStatus.APPROVED, "approved")
    return _view(version)


def reject(
    session: Session, *, actor: str, version_id: uuid.UUID, reason: str
) -> QuestionVersionView:
    """`in_review` → `rejected` (final). `reason` as in `request_changes`. Audit:
    `question_version.rejected`. Other status: InvalidTransition."""
    reason = _reason(reason)
    version, _ = _locked(session, version_id)
    _expect(version, VersionStatus.IN_REVIEW)
    _move(session, actor, version, VersionStatus.REJECTED, "rejected", reason=reason)
    return _view(version)


def _publish(
    session: Session, actor: str, version: QuestionVersion, question: Question, action: str
) -> None:
    reasons: list[str] = []
    if _failed_critical(session, version.id):
        reasons.append("critical_checks_failed")
    if version.has_unverified_visuals:
        reasons.append("unverified_visuals")
    if not _displayable(session, question):
        reasons.append("rights_denied")
    if reasons:
        raise NotPublishable(tuple(reasons))
    current = session.scalars(
        select(QuestionVersion)
        .where(
            QuestionVersion.question_id == version.question_id,
            QuestionVersion.status == VersionStatus.PUBLISHED.value,
        )
        .with_for_update()
    ).one_or_none()
    if current is not None:
        _move(
            session,
            actor,
            current,
            VersionStatus.WITHDRAWN,
            "superseded",
            superseded_by=str(version.id),
        )
    _move(session, actor, version, VersionStatus.PUBLISHED, action)


def publish(session: Session, *, actor: str, version_id: uuid.UUID) -> QuestionVersionView:
    """`approved` → `published`. The backend refuses, whatever the caller is (rule 8):

    - a status other than `approved` raises InvalidTransition;
    - otherwise NotPublishable with every reason that applies: `critical_checks_failed`,
      `unverified_visuals` (the document has stimuli; no asset can be verified yet, D-49),
      `rights_denied`.

    If the question already has a published version, that one becomes `withdrawn` in the same
    transaction (audit `question_version.superseded`). Audit: `question_version.published`.
    """
    version, question = _locked(session, version_id)
    _expect(version, VersionStatus.APPROVED)
    _publish(session, actor, version, question, "published")
    return _view(version)


def withdraw(
    session: Session, *, actor: str, version_id: uuid.UUID, reason: str
) -> QuestionVersionView:
    """`published` → `withdrawn`. Always possible, also when rights have been revoked.
    `reason` as in `request_changes`. Audit: `question_version.withdrawn`."""
    reason = _reason(reason)
    version, _ = _locked(session, version_id)
    _expect(version, VersionStatus.PUBLISHED)
    _move(session, actor, version, VersionStatus.WITHDRAWN, "withdrawn", reason=reason)
    return _view(version)


def republish(session: Session, *, actor: str, version_id: uuid.UUID) -> QuestionVersionView:
    """`withdrawn` → `published`, under the same conditions as `publish`.

    Refused with InvalidTransition when the question has a published version or a newer
    version than this one. Audit: `question_version.republished`.
    """
    version, question = _locked(session, version_id)
    _expect(version, VersionStatus.WITHDRAWN)
    blocking = session.scalar(
        select(func.count())
        .select_from(QuestionVersion)
        .where(
            QuestionVersion.question_id == version.question_id,
            (QuestionVersion.status == VersionStatus.PUBLISHED.value)
            | (QuestionVersion.version_no > version.version_no),
        )
    )
    if blocking:
        raise InvalidTransition("a published or newer version of this question exists")
    _publish(session, actor, version, question, "republished")
    return _view(version)


def start_revision(session: Session, *, actor: str, question_id: uuid.UUID) -> QuestionVersionView:
    """Open a new `draft` version to correct a question (CLAUDE.md rule 7).

    The new version copies the document of the published version, or, if none is published,
    of the latest version; its number is the highest existing number plus one. The source
    version is not changed. If the question already has a working version (`draft`,
    `auto_checking`, `needs_fix`, `in_review` or `approved`) WorkingVersionExists is raised.
    Rights as in `create_question`. Audit: `question_version.created` with `based_on`.
    Unknown id: NotFound.
    """
    question = session.get(Question, question_id, with_for_update=True)
    if question is None:
        raise NotFound(f"question {question_id}")
    rights.require(session, question.rights_record_id, rights.Purpose.DISPLAY)
    versions = list(
        session.scalars(
            select(QuestionVersion)
            .where(QuestionVersion.question_id == question_id)
            .order_by(QuestionVersion.version_no)
        )
    )
    if any(v.status in WORKING_STATUSES for v in versions):
        raise WorkingVersionExists(f"question {question_id} already has a working version")
    published = [v for v in versions if v.status == VersionStatus.PUBLISHED.value]
    source = published[0] if published else versions[-1]
    with session.begin_nested():
        version = QuestionVersion(
            question_id=question_id, version_no=versions[-1].version_no + 1, created_by=actor
        )
        _write_content(session, version, question, QuestionDocument.model_validate(source.document))
        _audit(session, actor, "created", version, based_on=str(source.id))
    return _view(version)


# --- reading ------------------------------------------------------------------------------


def get_question(session: Session, question_id: uuid.UUID) -> QuestionView:
    """The question. NotFound when it does not exist or its rights do not permit display."""
    question = session.get(Question, question_id)
    if question is None or not _displayable(session, question):
        raise NotFound(f"question {question_id}")
    return _question_view(question)


def get_version(session: Session, version_id: uuid.UUID) -> QuestionVersionView:
    """Any version, in any status: the staff view. NotFound when it does not exist or the
    question's rights do not permit display."""
    version = session.get(QuestionVersion, version_id, populate_existing=True)
    question = None if version is None else session.get(Question, version.question_id)
    if version is None or question is None or not _displayable(session, question):
        raise NotFound(f"question version {version_id}")
    return _view(version)


def list_versions(session: Session, question_id: uuid.UUID) -> list[QuestionVersionView]:
    """All versions of a question, oldest first. NotFound as in `get_question`."""
    get_question(session, question_id)
    rows = session.scalars(
        select(QuestionVersion)
        .where(QuestionVersion.question_id == question_id)
        .order_by(QuestionVersion.version_no)
        .execution_options(populate_existing=True)
    )
    return [_view(row) for row in rows]


def get_published_version(session: Session, question_id: uuid.UUID) -> QuestionVersionView:
    """The published version of a question: the only view a learner may be given.

    NotFound when the question does not exist, has no published version (a draft, approved or
    withdrawn version is never returned), or its rights do not permit display.
    """
    get_question(session, question_id)
    row = session.scalars(
        select(QuestionVersion)
        .where(
            QuestionVersion.question_id == question_id,
            QuestionVersion.status == VersionStatus.PUBLISHED.value,
        )
        .execution_options(populate_existing=True)
    ).one_or_none()
    if row is None:
        raise NotFound(f"question {question_id} has no published version")
    return _view(row)


def get_checks(session: Session, version_id: uuid.UUID) -> list[CheckResult]:
    """Check results stored for the version's current content, by code. NotFound as in
    `get_version`."""
    get_version(session, version_id)
    rows = session.scalars(
        select(QuestionVersionCheck)
        .where(QuestionVersionCheck.question_version_id == version_id)
        .order_by(QuestionVersionCheck.check_code)
    )
    return [
        CheckResult(row.check_code, Severity(row.severity), Outcome(row.outcome), row.detail)
        for row in rows
    ]
