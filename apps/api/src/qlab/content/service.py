"""Content service: the only way other modules create, change, publish or read questions.

Lifecycle and rules: docs/DOMAIN_MODEL.md section 4, docs/DATA_ARCHITECTURE.md section 2.2.
Functions run inside the caller's transaction (they flush, never commit) and write one audit
entry per change. `actor` is the opaque account identifier written to the audit log; which
roles may call what is decided by the authorization layer, not here.

Rights are fail-closed (CLAUDE.md rule 2): every function except `withdraw`, `reject` and
`request_changes`, which only ever restrict and return no content, needs the question's rights
record to permit display to everyone right now. A write that lacks it raises
`qlab.rights.service.RightsDenied`, before the version's status is looked at; a read behaves as
if the question did not exist.

Every writing function is atomic: when it raises, for whatever reason, neither the change nor
any audit entry remains, and the session stays usable.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from functools import wraps
from typing import Any

from pydantic import ValidationError
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, aliased

from qlab.audit import service as audit
from qlab.content import math
from qlab.content.models import (
    WORKING_STATUSES,
    MarkPoint,
    Part,
    Question,
    QuestionVersion,
    QuestionVersionCheck,
    QuestionVersionSyllabus,
)
from qlab.content.schema import (
    Level,
    QuestionClass,
    QuestionDocument,
    non_english_message,
    non_english_paths,
)
from qlab.content.schema.language import dotted
from qlab.rights import service as rights
from qlab.syllabus import service as syllabus
from qlab.syllabus.models import SyllabusNode

MAX_REASON_LENGTH = 500
MAX_DOCUMENT_BYTES = 512 * 1024
MAX_CHECK_DETAIL_BYTES = 8 * 1024
_CHECK_CODE = re.compile(r"[a-z][a-z0-9_]{0,63}")
_SOURCE_REF = re.compile(r"[a-z0-9][a-z0-9/_#.-]{0,199}")
# First key of the two-key advisory lock taken per source_ref; keeps this use apart from any
# other advisory locks in the database.
_SOURCE_REF_LOCK_SPACE = 0x514C4142
# Critical checks that must have passed on the current content before review and publishing.
# Mirrored by the database function content_required_checks() (migration 0003); extend both
# together.
REQUIRED_CHECKS = ("schema_valid", "vocabulary_valid", "math_renders")


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


@dataclass(frozen=True)
class DocumentProblem:
    """One reason a document was refused. `location` is the dotted path inside the document
    (list indices as numbers, e.g. `parts.0.mark_points.1.content.content.0.content.2.attrs.latex`),
    or None when the problem is about the document as a whole (size, NUL character)."""

    message: str
    location: str | None = None


MAX_PROBLEMS = 50
MAX_LOCATION_CHARS = 500


class OwnContentRightsUnavailable(ContentError):
    """The platform's own-content rights record is missing, ambiguous or does not permit display:
    a new question cannot be created (fail-closed, D-58)."""


# Licence reference of the platform's own-content rights record (owner decision D-58).
OWN_CONTENT_LICENSE_REF = "platform:own-content"


def own_content_rights_id(session: Session, *, holder: str | None = None) -> uuid.UUID | None:
    """Id of the platform's own-content rights record, or None when no record with the licence
    reference `OWN_CONTENT_LICENSE_REF` exists at all.

    Raises OwnContentRightsUnavailable when records with that reference exist but must not be
    used: any of them is revoked, expired or not yet valid (a revocation is a takedown decision
    and is not worked around with a new record); there is more than one; or the one record is
    not exactly what is expected: display to everyone, AI processing and commercial use
    permitted, no end of validity, and the given `holder` when one is given.
    """
    records = rights.find_by_license_ref(session, OWN_CONTENT_LICENSE_REF)
    if not records:
        return None
    now = datetime.now(UTC)
    if any(r.revoked_at is not None or not (r.valid_from <= now) for r in records) or any(
        r.valid_until is not None for r in records
    ):
        raise OwnContentRightsUnavailable(
            f"a {OWN_CONTENT_LICENSE_REF} rights record is revoked, expired or limited in time; "
            "the import does not replace it"
        )
    if len(records) > 1:
        raise OwnContentRightsUnavailable(f"more than one {OWN_CONTENT_LICENSE_REF} rights record")
    record = records[0]
    expected = (
        (holder is None or record.holder == holder)
        and record.display_scope is rights.DisplayScope.ALL
        and record.allows_ai_processing is True
        and record.allows_commercial_use is True
    )
    if not expected:
        raise OwnContentRightsUnavailable(
            f"the {OWN_CONTENT_LICENSE_REF} rights record does not have the expected holder "
            "and permissions"
        )
    return record.id


class InvalidDocument(ContentError):
    """The document was refused (vocabulary, math, language, size). `errors` lists every problem
    with where it is."""

    def __init__(self, errors: tuple[DocumentProblem, ...]) -> None:
        # Bounded however hostile the document: at most MAX_PROBLEMS items, short locations.
        if len(errors) > MAX_PROBLEMS:
            more = len(errors) - (MAX_PROBLEMS - 1)
            errors = (
                *errors[: MAX_PROBLEMS - 1],
                DocumentProblem(f"... and {more} more problems", None),
            )
        errors = tuple(
            DocumentProblem(e.message, e.location[:MAX_LOCATION_CHARS])
            if e.location is not None and len(e.location) > MAX_LOCATION_CHARS
            else e
            for e in errors
        )
        super().__init__("; ".join(e.message for e in errors))
        self.errors = errors


class InvalidTransition(ContentError):
    """The version is not in a state from which this operation is allowed."""


class DuplicateSourceRef(ContentError):
    """A question with this source reference already exists."""


class WorkingVersionExists(ContentError):
    """The question already has a version that is being worked on."""


class StaleContent(ContentError):
    """The version's content is not the content the caller says it looked at."""


class SelfApprovalForbidden(ContentError):
    """The approver is the account that last edited the version, and that is not allowed."""


class NotPublishable(ContentError):
    """Publishing was refused. `reasons` holds one or more of: `critical_checks_failed` (a
    critical check failed or a required one has not passed), `unverified_visuals`,
    `rights_denied`."""

    def __init__(self, reasons: tuple[str, ...]) -> None:
        super().__init__(", ".join(reasons))
        self.reasons = reasons


@dataclass(frozen=True)
class QuestionView:
    id: uuid.UUID
    origin: Origin
    rights_record_id: uuid.UUID
    syllabus_version_id: uuid.UUID
    source_ref: str | None
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


@dataclass(frozen=True)
class VersionState:
    """Where a version stands, without its content."""

    id: uuid.UUID
    question_id: uuid.UUID
    version_no: int
    status: VersionStatus
    content_sha256: str


@dataclass(frozen=True)
class VersionSummary:
    """A version without its content: what lists show."""

    id: uuid.UUID
    question_id: uuid.UUID
    version_no: int
    status: VersionStatus
    content_sha256: str
    question_class: QuestionClass
    exam_section: str
    levels: tuple[Level, ...]
    total_marks: int
    has_unverified_visuals: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class QuestionListItem:
    question: QuestionView
    # The version with the highest number.
    latest: VersionSummary
    published_version_id: uuid.UUID | None
    working_version_id: uuid.UUID | None


@dataclass(frozen=True)
class ListFilter:
    """Conditions on the version a list is about; None means "any"."""

    status: VersionStatus | None = None
    exam_section: str | None = None
    level: Level | None = None
    question_class: QuestionClass | None = None
    # A syllabus node code; matches the primary node and the secondary ones.
    syllabus_node: str | None = None
    has_unverified_visuals: bool | None = None


# One more than the largest API page: a caller asks for a page plus one to learn whether more exist.
MAX_LIST_LIMIT = 101


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
        source_ref=row.source_ref,
        created_by=row.created_by,
        created_at=row.created_at,
    )


def _displayable(session: Session, question: Question) -> bool:
    return rights.is_permitted(session, question.rights_record_id, rights.Purpose.DISPLAY)


def _state(row: QuestionVersion) -> VersionState:
    return VersionState(
        id=row.id,
        question_id=row.question_id,
        version_no=row.version_no,
        status=VersionStatus(row.status),
        content_sha256=row.content_sha256,
    )


def _atomic[**P, R](function: Callable[P, R]) -> Callable[P, R]:
    """Run a writing function in a savepoint: on any error nothing it wrote remains."""

    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        session = args[0]
        assert isinstance(session, Session)  # noqa: S101 - every writer takes the session first
        with session.begin_nested():
            return function(*args, **kwargs)

    return wrapper


def _lock_question(session: Session, question_id: uuid.UUID) -> Question:
    question = session.get(Question, question_id, with_for_update=True, populate_existing=True)
    if question is None:
        raise NotFound(f"question {question_id}")
    return question


def _locked(session: Session, version_id: uuid.UUID) -> tuple[QuestionVersion, Question]:
    """The version and its question, both locked. The question is always locked first, so
    operations on the versions of one question run one after another."""
    question_id = session.scalar(
        select(QuestionVersion.question_id).where(QuestionVersion.id == version_id)
    )
    if question_id is None:
        raise NotFound(f"question version {version_id}")
    question = _lock_question(session, question_id)
    version = session.get(QuestionVersion, version_id, with_for_update=True, populate_existing=True)
    if version is None:  # versions are never deleted
        raise NotFound(f"question version {version_id}")
    return version, question


def _require_rights(session: Session, question: Question) -> None:
    rights.require(session, question.rights_record_id, rights.Purpose.DISPLAY)


def _expect_content(version: QuestionVersion, expected_content_sha256: str) -> None:
    if version.content_sha256 != expected_content_sha256:
        raise StaleContent("the version's content has changed since it was read")


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
) -> tuple[DocumentProblem, ...]:
    errors: list[DocumentProblem] = []
    if document.exam_section not in vocabulary.exam_sections:
        errors.append(
            DocumentProblem(f"unknown exam section {document.exam_section!r}", "exam_section")
        )
    nodes = (
        ("primary_syllabus_node", document.primary_syllabus_node),
        *(
            (f"secondary_syllabus_nodes.{i}", node)
            for i, node in enumerate(document.secondary_syllabus_nodes)
        ),
    )
    for location, node in nodes:
        if node not in vocabulary.leaf_node_codes:
            errors.append(DocumentProblem(f"unknown or non-leaf syllabus node {node!r}", location))
    for index, part in enumerate(document.parts):
        if part.command_term is not None and part.command_term not in vocabulary.command_terms:
            errors.append(
                DocumentProblem(
                    f"part {part.label}: unknown command term {part.command_term!r}",
                    f"parts.{index}.command_term",
                )
            )
    return tuple(errors)


def _write_content(
    session: Session,
    version: QuestionVersion,
    question: Question,
    document: QuestionDocument,
    *,
    check_math: bool = True,
) -> None:
    """Store the document on the version and rebuild every row derived from it."""
    encoded = document.model_dump_json()
    if len(encoded.encode()) > MAX_DOCUMENT_BYTES:
        raise InvalidDocument(
            (DocumentProblem(f"document is larger than {MAX_DOCUMENT_BYTES} bytes"),)
        )
    if "\\u0000" in encoded:
        raise InvalidDocument((DocumentProblem("document contains a NUL character"),))
    foreign = non_english_paths(document)
    if foreign:
        message = non_english_message(foreign)
        raise InvalidDocument(tuple(DocumentProblem(message, dotted(path)) for path in foreign))
    vocabulary = syllabus.get_vocabulary(session, question.syllabus_version_id)
    errors = _vocabulary_errors(document, vocabulary)
    if errors:
        raise InvalidDocument(errors)
    # Every math node must render now, or the document is not stored (CLAUDE.md rule 6).
    math_problems = math.check_located(document) if check_math else ()
    if math_problems:
        raise InvalidDocument(tuple(DocumentProblem(p.message, p.location) for p in math_problems))
    nodes = (document.primary_syllabus_node, *document.secondary_syllabus_nodes)
    node_ids = syllabus.node_ids(session, question.syllabus_version_id, frozenset(nodes))

    new_hash = content_sha256(document)
    unchanged = version.content_sha256 == new_hash
    version.schema_version = document.schema_version
    version.document = document.model_dump(mode="json")
    version.content_sha256 = new_hash
    version.question_class = document.question_class.value
    version.exam_section = document.exam_section
    version.levels = [level.value for level in document.levels]
    version.total_marks = document.total_marks
    session.add(version)
    session.flush()

    # Check results describe the content they ran on; they survive only an identical save.
    if not unchanged:
        session.execute(
            delete(QuestionVersionCheck).where(
                QuestionVersionCheck.question_version_id == version.id
            )
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


def _blocking_checks(session: Session, version_id: uuid.UUID) -> list[str]:
    """Codes that stop review and publishing: critical checks that failed, and required
    checks that have not passed on the current content."""
    rows = session.execute(
        select(QuestionVersionCheck.check_code, QuestionVersionCheck.outcome).where(
            QuestionVersionCheck.question_version_id == version_id,
            QuestionVersionCheck.severity == Severity.CRITICAL.value,
        )
    ).all()
    outcomes = {code: outcome for code, outcome in rows}
    failed = {code for code, outcome in outcomes.items() if outcome == Outcome.FAILED.value}
    missing = {c for c in REQUIRED_CHECKS if outcomes.get(c) != Outcome.PASSED.value}
    return sorted(failed | missing)


def _check_schema(session: Session, version: QuestionVersion, question: Question) -> CheckResult:
    try:
        QuestionDocument.model_validate(version.document)
    except ValidationError as error:
        # Counts only: validation messages quote the content.
        return CheckResult(
            "schema_valid", Severity.CRITICAL, Outcome.FAILED, {"errors": error.error_count()}
        )
    return CheckResult("schema_valid", Severity.CRITICAL, Outcome.PASSED, {})


def _check_vocabulary(
    session: Session, version: QuestionVersion, question: Question
) -> CheckResult:
    try:
        document = QuestionDocument.model_validate(version.document)
    except ValidationError:
        return CheckResult("vocabulary_valid", Severity.CRITICAL, Outcome.NOT_APPLICABLE, {})
    errors = _vocabulary_errors(
        document, syllabus.get_vocabulary(session, question.syllabus_version_id)
    )
    outcome = Outcome.FAILED if errors else Outcome.PASSED
    return CheckResult(
        "vocabulary_valid", Severity.CRITICAL, outcome, {"errors": [e.message for e in errors]}
    )


def _check_math(session: Session, version: QuestionVersion, question: Question) -> CheckResult:
    try:
        document = QuestionDocument.model_validate(version.document)
    except ValidationError:
        return CheckResult("math_renders", Severity.CRITICAL, Outcome.NOT_APPLICABLE, {})
    errors = math.check(document)
    outcome = Outcome.FAILED if errors else Outcome.PASSED
    return CheckResult(
        "math_renders",
        Severity.CRITICAL,
        outcome,
        {
            "errors": len(errors),
            "nodes": sum(1 for _ in math.math_nodes(document)),
            "katex": math.KATEX_VERSION,
        },
    )


# The checks `submit` runs itself. External results (the verification pipeline) arrive through
# `record_check`.
_OWN_CHECKS: list[Callable[[Session, QuestionVersion, Question], CheckResult]] = [
    _check_schema,
    _check_vocabulary,
    _check_math,
]


# --- writing ------------------------------------------------------------------------------


@_atomic
def create_question(
    session: Session,
    *,
    actor: str,
    document: QuestionDocument,
    rights_record_id: uuid.UUID,
    syllabus_version_id: uuid.UUID,
    origin: Origin = Origin.AUTHORED,
    source_ref: str | None = None,
) -> QuestionVersionView:
    """Create a question and its first version (version 1, `draft`).

    `source_ref` is the stable key of an imported question (lower-case letters, digits and
    `/ _ # . -`, at most 200 characters; else ValueError). It cannot be changed later. A second
    question with the same key raises DuplicateSourceRef.

    - `origin` other than `authored` raises OriginClosed (D-52), before anything else.
    - The rights record must permit display to everyone now, else RightsDenied.
    - Unknown `syllabus_version_id` raises LookupError.
    - The document's exam section, command terms and syllabus nodes (leaf nodes only) must
      belong to the syllabus version, else InvalidDocument listing every problem. A document
      over 512 kB or containing a NUL character is also InvalidDocument, and so is one with a
      Turkish-only letter (`ğ Ğ ı İ ş Ş`) in any string: content is written in English.
    - Every math node must use only allowed LaTeX commands and render in the pinned KaTeX
      (`qlab.content.math`), else InvalidDocument naming each node. If the renderer cannot be
      run, `qlab.content.math.RendererUnavailable` is raised and nothing is saved.

    Nothing is written when an error is raised. On success the derived rows exist (one `part`
    per part, or a single one with key "mcq" for a multiple-choice question; one `mark_point`
    per mark point, none for multiple choice; positions count from 0; one
    `question_version_syllabus` per node with the primary flagged) and the
    audit log has `question_version.created` for the new version.
    """
    if Origin(origin) is not Origin.AUTHORED:
        raise OriginClosed(f"origin {Origin(origin).value} is not accepted yet")
    if source_ref is not None and not _SOURCE_REF.fullmatch(source_ref):
        raise ValueError("source_ref is not a valid key")
    rights.require(session, rights_record_id, rights.Purpose.DISPLAY)
    syllabus.get_vocabulary(session, syllabus_version_id)
    if source_ref is not None:
        # Serialises concurrent imports of the same key; the unique constraint is the backstop.
        session.execute(
            select(func.pg_advisory_xact_lock(_SOURCE_REF_LOCK_SPACE, func.hashtext(source_ref)))
        )
        taken = session.scalar(select(Question.id).where(Question.source_ref == source_ref))
        if taken is not None:
            raise DuplicateSourceRef(source_ref)
    question = Question(
        origin=Origin.AUTHORED.value,
        rights_record_id=rights_record_id,
        syllabus_version_id=syllabus_version_id,
        source_ref=source_ref,
        created_by=actor,
    )
    session.add(question)
    session.flush()
    version = QuestionVersion(question_id=question.id, version_no=1, created_by=actor)
    _write_content(session, version, question, document)
    if source_ref is None:
        _audit(session, actor, "created", version)
    else:
        _audit(session, actor, "created", version, source_ref=source_ref)
    return _view(version)


@_atomic
def update_draft(
    session: Session,
    *,
    actor: str,
    version_id: uuid.UUID,
    document: QuestionDocument,
    expected_content_sha256: str | None = None,
) -> QuestionVersionView:
    """Replace the content of a `draft` or `needs_fix` version; the result is `draft`.

    When `expected_content_sha256` is given it must be the hash of the stored content (the
    content the editor started from), else StaleContent: two editors never overwrite each
    other silently. The API always passes it; internal callers such as the pilot import may not.

    Any other status raises InvalidTransition (a published version is corrected with
    `start_revision`). Same rights and document rules as `create_question`. The derived rows
    are rebuilt. Earlier check results are discarded, unless the new document is identical to
    the stored one (same hash): saving the same content again does not clear a failed check.
    Audit: `question_version.updated` with the new content hash and
    `previous_content_sha256`. Unknown id: NotFound.
    """
    version, question = _locked(session, version_id)
    _require_rights(session, question)
    _expect(version, VersionStatus.DRAFT, VersionStatus.NEEDS_FIX)
    if expected_content_sha256 is not None:
        _expect_content(version, expected_content_sha256)
    previous_status, previous_hash = version.status, version.content_sha256
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


@_atomic
def record_check(
    session: Session, *, actor: str, version_id: uuid.UUID, result: CheckResult
) -> None:
    """Store the result of an external check, replacing an earlier result with the same code.

    Allowed while the version is `draft`, `needs_fix` or `auto_checking`; otherwise
    InvalidTransition. Rights as in `create_question` (running a check is processing). A
    failed critical result sends the next `submit` to `needs_fix` and blocks publishing; it
    is discarded only when the content actually changes. Audit:
    `question_version.check_recorded`. Unknown id: NotFound. ValueError when the code is not a
    lower-case identifier of at most 64 characters, is one of the service's own required
    checks, or `detail` is not JSON of at most 8 kB.
    """
    if result.code in REQUIRED_CHECKS:
        raise ValueError(f"check {result.code} is run by submit and cannot be recorded")
    if not _CHECK_CODE.fullmatch(result.code):
        raise ValueError(f"check code {result.code[:80]!r} is not a short lower-case identifier")
    try:
        detail_size = len(json.dumps(result.detail, allow_nan=False).encode())
    except (TypeError, ValueError) as error:
        raise ValueError(f"check detail is not JSON: {error}") from None
    if detail_size > MAX_CHECK_DETAIL_BYTES:
        raise ValueError("check detail is too large")
    version, question = _locked(session, version_id)
    _require_rights(session, question)
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


@_atomic
def submit(session: Session, *, actor: str, version_id: uuid.UUID) -> VersionState:
    """Run the automatic checks on a `draft` version and move it on.

    `draft` → `auto_checking` → `in_review`, or `needs_fix` when a critical check has failed
    or a required check (`schema_valid`, `vocabulary_valid`, `math_renders`) has not
    passed. The service's own
    checks are run and stored; results recorded earlier with `record_check` count too.
    Unverified visuals do not stop a review; they stop publishing. If the math renderer
    cannot be run, `qlab.content.math.RendererUnavailable` is raised and the version stays
    `draft`. Audit:
    `question_version.submitted`, then `question_version.checks_passed` or
    `question_version.checks_failed` (with the blocking codes). Other status:
    InvalidTransition. Rights as in `create_question`.
    """
    version, question = _locked(session, version_id)
    _require_rights(session, question)
    _expect(version, VersionStatus.DRAFT)
    _move(session, actor, version, VersionStatus.AUTO_CHECKING, "submitted")
    for check in _OWN_CHECKS:
        _store_check(session, version.id, check(session, version, question))
    blocking = _blocking_checks(session, version.id)
    if blocking:
        _move(session, actor, version, VersionStatus.NEEDS_FIX, "checks_failed", failed=blocking)
    else:
        _move(session, actor, version, VersionStatus.IN_REVIEW, "checks_passed")
    return _state(version)


@_atomic
def request_changes(
    session: Session, *, actor: str, version_id: uuid.UUID, reason: str
) -> VersionState:
    """Send an `in_review` or `approved` version back: → `needs_fix`, where it can be edited.

    `reason` is required (1 to 500 characters after trimming, else ValueError) and is written
    to the audit entry `question_version.changes_requested`; it must describe the content, not
    a person. Other status: InvalidTransition. Needs no rights.
    """
    reason = _reason(reason)
    version, _ = _locked(session, version_id)
    _expect(version, VersionStatus.IN_REVIEW, VersionStatus.APPROVED)
    _move(session, actor, version, VersionStatus.NEEDS_FIX, "changes_requested", reason=reason)
    return _state(version)


def _last_editor(session: Session, version_id: uuid.UUID) -> str | None:
    """Actor of the latest entry that wrote the version's content: `created`, or an `updated`
    that changed it. Saving the same content again does not make someone the editor."""
    for entry in reversed(audit.entries_for(session, "question_version", str(version_id))):
        if entry.action == "question_version.created":
            return entry.actor
        if entry.action == "question_version.updated" and entry.data.get(
            "previous_content_sha256"
        ) != entry.data.get("content_sha256"):
            return entry.actor
    return None


@_atomic
def approve(
    session: Session,
    *,
    actor: str,
    version_id: uuid.UUID,
    expected_content_sha256: str,
    forbid_self_approval: bool = False,
) -> VersionState:
    """`in_review` → `approved`. One approval is enough in M1-G (D-53); the approver is the
    audit entry's actor (`question_version.approved`).

    `expected_content_sha256` is the hash of the content the approver looked at; if the
    version's content is different now, StaleContent is raised. Other status:
    InvalidTransition. Rights as in `create_question`.

    Separation of duties (D-59): the audit entry carries `approver_is_last_editor`, true when
    `actor` is the actor of the version's latest `created` entry or `updated` entry that
    changed the content (re-saving identical content does not count). With
    `forbid_self_approval` such an approval raises SelfApprovalForbidden instead, after the
    status and content checks; an approval whose last editor cannot be determined is refused
    too.
    """
    version, question = _locked(session, version_id)
    _require_rights(session, question)
    _expect(version, VersionStatus.IN_REVIEW)
    _expect_content(version, expected_content_sha256)
    last_editor = _last_editor(session, version.id)
    if forbid_self_approval and (last_editor is None or last_editor == actor):
        raise SelfApprovalForbidden("the last editor of a version cannot approve it")
    _move(
        session,
        actor,
        version,
        VersionStatus.APPROVED,
        "approved",
        approver_is_last_editor=last_editor == actor,
    )
    return _state(version)


@_atomic
def reject(session: Session, *, actor: str, version_id: uuid.UUID, reason: str) -> VersionState:
    """`in_review` → `rejected` (final). `reason` as in `request_changes`. Audit:
    `question_version.rejected`. Other status: InvalidTransition. Needs no rights."""
    reason = _reason(reason)
    version, _ = _locked(session, version_id)
    _expect(version, VersionStatus.IN_REVIEW)
    _move(session, actor, version, VersionStatus.REJECTED, "rejected", reason=reason)
    return _state(version)


def _publish(
    session: Session,
    actor: str,
    version: QuestionVersion,
    question: Question,
    action: str,
    **data: object,
) -> None:
    reasons: list[str] = []
    if _blocking_checks(session, version.id):
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
        .execution_options(populate_existing=True)
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
    _move(session, actor, version, VersionStatus.PUBLISHED, action, **data)


@_atomic
def publish(
    session: Session, *, actor: str, version_id: uuid.UUID, expected_content_sha256: str
) -> VersionState:
    """`approved` → `published`. The backend refuses, whatever the caller is (rule 8):

    - a status other than `approved` raises InvalidTransition;
    - content other than `expected_content_sha256` raises StaleContent;
    - otherwise NotPublishable with every reason that applies: `critical_checks_failed` (a
      critical check failed or a required check has not passed), `unverified_visuals` (the
      document has stimuli; no asset can be verified yet, D-49), `rights_denied`.

    If the question already has a published version, that one becomes `withdrawn` in the same
    transaction (audit `question_version.superseded`). Audit: `question_version.published`.
    """
    version, question = _locked(session, version_id)
    _expect(version, VersionStatus.APPROVED)
    _expect_content(version, expected_content_sha256)
    _publish(session, actor, version, question, "published")
    return _state(version)


@_atomic
def withdraw(session: Session, *, actor: str, version_id: uuid.UUID, reason: str) -> VersionState:
    """`published` → `withdrawn`. Always possible, also when rights have been revoked.
    `reason` as in `request_changes`. Audit: `question_version.withdrawn`."""
    reason = _reason(reason)
    version, _ = _locked(session, version_id)
    _expect(version, VersionStatus.PUBLISHED)
    _move(session, actor, version, VersionStatus.WITHDRAWN, "withdrawn", reason=reason)
    return _state(version)


@_atomic
def republish(
    session: Session,
    *,
    actor: str,
    version_id: uuid.UUID,
    expected_content_sha256: str,
    reason: str,
) -> VersionState:
    """`withdrawn` → `published`, under the same conditions as `publish`.

    `reason` (as in `request_changes`) says why the withdrawal no longer applies. Refused
    with InvalidTransition when the question has a published version or any newer version
    than this one. Audit: `question_version.republished`.
    """
    reason = _reason(reason)
    version, question = _locked(session, version_id)
    _expect(version, VersionStatus.WITHDRAWN)
    _expect_content(version, expected_content_sha256)
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
    _publish(session, actor, version, question, "republished", reason=reason)
    return _state(version)


@_atomic
def start_revision(session: Session, *, actor: str, question_id: uuid.UUID) -> QuestionVersionView:
    """Open a new `draft` version to correct a question (CLAUDE.md rule 7).

    The new version copies the document of the published version; if none is published, of
    the latest version that was not rejected; if all were rejected, of the latest. Its number
    is the highest existing number plus one. The source version is not changed. If the
    question already has a working version (`draft`, `auto_checking`, `needs_fix`, `in_review`
    or `approved`) WorkingVersionExists is raised. The copy is not checked against the math
    rules (it may predate them); `submit` checks it. Rights as in `create_question`. Audit:
    `question_version.created` with `based_on` (the source version's id). Unknown id: NotFound.
    """
    question = _lock_question(session, question_id)
    _require_rights(session, question)
    versions = list(
        session.scalars(
            select(QuestionVersion)
            .where(QuestionVersion.question_id == question_id)
            .order_by(QuestionVersion.version_no)
            .execution_options(populate_existing=True)
        )
    )
    if not versions:
        raise NotFound(f"question {question_id} has no versions")
    if any(v.status in WORKING_STATUSES for v in versions):
        raise WorkingVersionExists(f"question {question_id} already has a working version")
    published = [v for v in versions if v.status == VersionStatus.PUBLISHED.value]
    not_rejected = [v for v in versions if v.status != VersionStatus.REJECTED.value]
    source = (published or not_rejected or versions)[-1]
    version = QuestionVersion(
        question_id=question_id, version_no=versions[-1].version_no + 1, created_by=actor
    )
    # A copy is not new content: math that the current rules refuse (after the allowed list or
    # the KaTeX version changed) is carried into the draft so that it can be corrected, and the
    # math_renders check stops it at submit.
    _write_content(
        session,
        version,
        question,
        QuestionDocument.model_validate(source.document),
        check_math=False,
    )
    _audit(session, actor, "created", version, based_on=str(source.id))
    return _view(version)


# --- reading ------------------------------------------------------------------------------


def get_question(session: Session, question_id: uuid.UUID) -> QuestionView:
    """The question. NotFound when it does not exist or its rights do not permit display."""
    question = session.get(Question, question_id)
    if question is None or not _displayable(session, question):
        raise NotFound(f"question {question_id}")
    return _question_view(question)


def find_question_by_source_ref(session: Session, source_ref: str) -> QuestionView | None:
    """The question imported under this key, or None when there is none or its rights do not
    permit display."""
    question = session.scalars(
        select(Question).where(Question.source_ref == source_ref)
    ).one_or_none()
    if question is None or not _displayable(session, question):
        return None
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
    """The published version of a question, with its whole document.

    This is the only version a learner may ever be shown, but the view is not a learner
    projection: it contains the answers and the mark scheme. The API layer builds what a
    learner sees from it. NotFound when the question does not exist, has no published version
    (a draft, approved or withdrawn version is never returned), or its rights do not permit
    display.
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


def get_syllabus_version_id(session: Session, version_id: uuid.UUID) -> uuid.UUID:
    """Id of the syllabus version the version's question belongs to. NotFound as in
    `get_version`."""
    get_version(session, version_id)
    found = session.scalar(
        select(Question.syllabus_version_id)
        .join(QuestionVersion, QuestionVersion.question_id == Question.id)
        .where(QuestionVersion.id == version_id)
    )
    if found is None:
        raise NotFound(f"question version {version_id}")
    return found


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


def summarize(view: QuestionVersionView) -> VersionSummary:
    """The summary of a version that was read with its content."""
    return VersionSummary(
        id=view.id,
        question_id=view.question_id,
        version_no=view.version_no,
        status=view.status,
        content_sha256=view.content_sha256,
        question_class=view.document.question_class,
        exam_section=view.document.exam_section,
        levels=view.document.levels,
        total_marks=view.document.total_marks,
        has_unverified_visuals=view.has_unverified_visuals,
        created_by=view.created_by,
        created_at=view.created_at,
        updated_at=view.updated_at,
    )


def _summary(row: QuestionVersion) -> VersionSummary:
    return VersionSummary(
        id=row.id,
        question_id=row.question_id,
        version_no=row.version_no,
        status=VersionStatus(row.status),
        content_sha256=row.content_sha256,
        question_class=QuestionClass(row.question_class),
        exam_section=row.exam_section,
        levels=tuple(Level(level) for level in row.levels),
        total_marks=row.total_marks,
        has_unverified_visuals=row.has_unverified_visuals,
        created_by=row.created_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _check_limit(limit: int) -> None:
    if not 1 <= limit <= MAX_LIST_LIMIT:
        raise ValueError(f"limit must be 1 to {MAX_LIST_LIMIT}")


def _listing(
    session: Session,
    filter: ListFilter | None,
    after: uuid.UUID | None,
    limit: int,
    *,
    published_only: bool,
) -> list[tuple[Question, QuestionVersion]]:
    """Questions with the version a list is about (the latest one, or the published one),
    in question id order. Rights are decided per distinct record and applied in the query,
    before the limit."""
    _check_limit(limit)
    filter = filter or ListFilter()
    record_ids = session.scalars(select(Question.rights_record_id).distinct()).all()
    permitted = [
        record_id
        for record_id in record_ids
        if rights.is_permitted(session, record_id, rights.Purpose.DISPLAY)
    ]
    if not permitted:
        return []
    statement = (
        select(Question, QuestionVersion)
        .join(QuestionVersion, QuestionVersion.question_id == Question.id)
        .where(Question.rights_record_id.in_(permitted))
        .order_by(Question.id)
        .limit(limit)
        .execution_options(populate_existing=True)
    )
    if published_only:
        statement = statement.where(QuestionVersion.status == VersionStatus.PUBLISHED.value)
    else:
        other = aliased(QuestionVersion)
        latest = (
            select(func.max(other.version_no))
            .where(other.question_id == Question.id)
            .scalar_subquery()
        )
        statement = statement.where(QuestionVersion.version_no == latest)
    if after is not None:
        statement = statement.where(Question.id > after)
    if filter.status is not None:
        statement = statement.where(QuestionVersion.status == filter.status.value)
    if filter.exam_section is not None:
        statement = statement.where(QuestionVersion.exam_section == filter.exam_section)
    if filter.level is not None:
        statement = statement.where(QuestionVersion.levels.contains([filter.level.value]))
    if filter.question_class is not None:
        statement = statement.where(QuestionVersion.question_class == filter.question_class.value)
    if filter.has_unverified_visuals is not None:
        statement = statement.where(
            QuestionVersion.has_unverified_visuals == filter.has_unverified_visuals
        )
    if filter.syllabus_node is not None:
        # Codes are unique inside one syllabus version only: resolve them per version.
        node_ids: list[uuid.UUID] = []
        for syllabus_version_id in session.scalars(
            select(Question.syllabus_version_id).distinct()
        ).all():
            try:
                found = syllabus.node_ids(
                    session, syllabus_version_id, frozenset({filter.syllabus_node})
                )
            except LookupError:
                continue
            node_ids.extend(found.values())
        if not node_ids:
            return []
        statement = statement.where(
            select(QuestionVersionSyllabus.question_version_id)
            .where(
                QuestionVersionSyllabus.question_version_id == QuestionVersion.id,
                QuestionVersionSyllabus.syllabus_node_id.in_(node_ids),
            )
            .exists()
        )
    return [(question, version) for question, version in session.execute(statement).all()]


def list_questions(
    session: Session,
    *,
    filter: ListFilter | None = None,
    after: uuid.UUID | None = None,
    limit: int,
) -> list[QuestionListItem]:
    """Questions in any status, for staff: ordered by question id ascending (creation order),
    only those with an id greater than `after`, at most `limit` (1 to MAX_LIST_LIMIT, else
    ValueError).

    `filter` applies to each question's latest version (highest `version_no`); a question
    whose latest version does not match is left out. `published_version_id` and
    `working_version_id` are filled regardless of the filter.

    Rights are fail-closed (CLAUDE.md rule 2): a question is listed only when its rights
    record permits display to everyone right now, decided by `qlab.rights.service.is_permitted`
    (once per distinct rights record, not once per question). Filtering by rights happens
    before the limit is applied, so a page is short only at the end of the list.
    """
    items = _listing(session, filter, after, limit, published_only=False)
    if not items:
        return []
    ids = [question.id for question, _ in items]
    published: dict[uuid.UUID, uuid.UUID] = {}
    working: dict[uuid.UUID, uuid.UUID] = {}
    rows = session.execute(
        select(QuestionVersion.question_id, QuestionVersion.id, QuestionVersion.status).where(
            QuestionVersion.question_id.in_(ids),
            QuestionVersion.status.in_(
                (VersionStatus.PUBLISHED.value, *(s for s in WORKING_STATUSES))
            ),
        )
    )
    for question_id, version_id, status in rows:
        if status == VersionStatus.PUBLISHED.value:
            published[question_id] = version_id
        else:
            working[question_id] = version_id
    return [
        QuestionListItem(
            question=_question_view(question),
            latest=_summary(version),
            published_version_id=published.get(question.id),
            working_version_id=working.get(question.id),
        )
        for question, version in items
    ]


def list_published(
    session: Session,
    *,
    filter: ListFilter | None = None,
    after: uuid.UUID | None = None,
    limit: int,
) -> list[VersionSummary]:
    """The published version of every question that has one: ordered by question id
    ascending, only questions with an id greater than `after`, at most `limit` (1 to
    MAX_LIST_LIMIT, else ValueError).

    `filter` applies to the published version; `filter.status` must be None (ValueError). No
    version in another status is ever returned. Rights as in `list_questions`.
    """
    if filter is not None and filter.status is not None:
        raise ValueError("list_published takes no status filter")
    return [
        _summary(version)
        for _, version in _listing(session, filter, after, limit, published_only=True)
    ]


def primary_topics(
    session: Session, version_ids: frozenset[uuid.UUID]
) -> dict[uuid.UUID, tuple[str, str]]:
    """Code and title of the primary syllabus node of each version, in one query. For labels
    in lists; it checks no rights, so callers pass versions they already may show."""
    if not version_ids:
        return {}
    rows = session.execute(
        select(QuestionVersionSyllabus.question_version_id, SyllabusNode.code, SyllabusNode.title)
        .join(SyllabusNode, SyllabusNode.id == QuestionVersionSyllabus.syllabus_node_id)
        .where(
            QuestionVersionSyllabus.question_version_id.in_(version_ids),
            QuestionVersionSyllabus.is_primary,
        )
    )
    return {version_id: (code, title) for version_id, code, title in rows}


def get_history(session: Session, version_id: uuid.UUID) -> list[audit.AuditEntry]:
    """The audit entries about one version (entity type `question_version`), oldest first.
    NotFound as in `get_version`."""
    version = session.get(QuestionVersion, version_id)
    question = None if version is None else session.get(Question, version.question_id)
    if version is None or question is None or not _displayable(session, question):
        raise NotFound(f"question version {version_id}")
    return audit.entries_for(session, "question_version", str(version_id))
