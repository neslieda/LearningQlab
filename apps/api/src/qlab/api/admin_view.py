"""Staff view: service views to the `Admin*` response types (docs/slices/M1G-5-SOZLESME.md
section 3.5). Pure functions; identifiers get their prefixes here."""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from qlab.api import errors, ids
from qlab.api.schemas import (
    AdminQuestion,
    AdminQuestionSummary,
    AdminVersion,
    AdminVersionSummary,
    CheckOut,
    HistoryEntry,
    SyllabusRef,
    VersionStateOut,
)
from qlab.audit.service import AuditEntry
from qlab.content import service as content
from qlab.content.schema import QuestionDocument
from qlab.syllabus import service as syllabus

_ACTION_PREFIX = "question_version."


def question_id(value: uuid.UUID) -> str:
    return ids.encode(ids.QUESTION, value)


def version_id(value: uuid.UUID) -> str:
    return ids.encode(ids.QUESTION_VERSION, value)


def version_summary(summary: content.VersionSummary) -> AdminVersionSummary:
    return AdminVersionSummary(
        id=version_id(summary.id),
        question_id=question_id(summary.question_id),
        version_no=summary.version_no,
        status=summary.status,
        content_sha256=summary.content_sha256,
        question_class=summary.question_class,
        exam_section=summary.exam_section,
        levels=summary.levels,
        total_marks=summary.total_marks,
        has_unverified_visuals=summary.has_unverified_visuals,
        created_by=summary.created_by,
        created_at=summary.created_at,
        updated_at=summary.updated_at,
    )


def question_summary(item: content.QuestionListItem) -> AdminQuestionSummary:
    return AdminQuestionSummary(
        id=question_id(item.question.id),
        origin=item.question.origin,
        source_ref=item.question.source_ref,
        created_at=item.question.created_at,
        latest_version=version_summary(item.latest),
        published_version_id=_optional_version(item.published_version_id),
        working_version_id=_optional_version(item.working_version_id),
    )


def _optional_version(value: uuid.UUID | None) -> str | None:
    return None if value is None else version_id(value)


def question(
    view: content.QuestionView, versions: list[content.QuestionVersionView]
) -> AdminQuestion:
    return AdminQuestion(
        id=question_id(view.id),
        origin=view.origin,
        source_ref=view.source_ref,
        created_by=view.created_by,
        created_at=view.created_at,
        versions=tuple(version_summary(content.summarize(v)) for v in versions),
    )


def check(result: content.CheckResult) -> CheckOut:
    return CheckOut(
        code=result.code, severity=result.severity, outcome=result.outcome, detail=result.detail
    )


def version(
    session: Session, view: content.QuestionVersionView, checks: list[content.CheckResult]
) -> AdminVersion:
    codes = syllabus.get_codes(session, content.get_syllabus_version_id(session, view.id))
    return AdminVersion(
        **version_summary(content.summarize(view)).model_dump(),
        syllabus=SyllabusRef(program=codes.program, subject=codes.subject, version=codes.version),
        document=view.document,
        checks=tuple(check(c) for c in checks),
    )


_version = version


def create_question(
    session: Session,
    *,
    actor: str,
    program: str,
    subject: str,
    version: str | None,
    document: QuestionDocument,
) -> AdminVersion:
    """A new authored question under the platform's own-content rights record. Unknown
    programme, subject or version: NotFound (the API's 404). No usable own-content record:
    content.OwnContentRightsUnavailable (409). Nothing is written in either case."""
    syllabus_version_id = syllabus.resolve_version(
        session, program=program, subject=subject, version=version
    )
    if syllabus_version_id is None:
        raise errors.not_found()
    rights_record_id = content.own_content_rights_id(session)
    if rights_record_id is None:
        raise content.OwnContentRightsUnavailable("no own-content rights record exists")
    try:
        syllabus.get_vocabulary(session, syllabus_version_id)
    except LookupError:  # a version without an exam format has no vocabulary
        raise errors.not_found() from None
    created = content.create_question(
        session,
        actor=actor,
        document=document,
        rights_record_id=rights_record_id,
        syllabus_version_id=syllabus_version_id,
        origin=content.Origin.AUTHORED,
        source_ref=None,
    )
    return _version(session, created, content.get_checks(session, created.id))


def state(value: content.VersionState) -> VersionStateOut:
    return VersionStateOut(
        id=version_id(value.id),
        question_id=question_id(value.question_id),
        version_no=value.version_no,
        status=value.status,
        content_sha256=value.content_sha256,
    )


def _text(data: Mapping[str, Any], key: str) -> str | None:
    value = data.get(key)
    return None if value is None else str(value)


def _version_ref(data: Mapping[str, Any], key: str) -> str | None:
    value = data.get(key)
    return None if value is None else version_id(uuid.UUID(str(value)))


def history_entry(entry: AuditEntry) -> HistoryEntry:
    data = entry.data
    failed = data.get("failed")
    approver_is_last_editor = data.get("approver_is_last_editor")
    return HistoryEntry.model_validate(
        {
            "occurred_at": entry.occurred_at,
            "actor": entry.actor,
            "action": entry.action.removeprefix(_ACTION_PREFIX),
            "status": data["status"],
            "previous_status": data.get("previous_status"),
            "content_sha256": data["content_sha256"],
            "previous_content_sha256": data.get("previous_content_sha256"),
            "reason": _text(data, "reason"),
            "failed_checks": None if failed is None else tuple(str(f) for f in failed),
            "check": _text(data, "check"),
            "severity": data.get("severity"),
            "outcome": data.get("outcome"),
            "based_on": _version_ref(data, "based_on"),
            "superseded_by": _version_ref(data, "superseded_by"),
            "source_ref": _text(data, "source_ref"),
            "approver_is_last_editor": (
                None if approver_is_last_editor is None else bool(approver_is_last_editor)
            ),
        }
    )
