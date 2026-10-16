"""A learner's stored answers (M1-G slice 8, D-66). Every function is about one account: there is
no way to ask for somebody else's rows. The account id is opaque; no name or e-mail is kept."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from qlab.attempts.models import MAX_ANSWERS_PER_QUESTION, Response
from qlab.content.models import QuestionVersion


class TooManyAnswers(Exception):
    """The account already has MAX_ANSWERS_PER_QUESTION answers to this question."""


@dataclass(frozen=True)
class ResponseView:
    id: uuid.UUID
    question_id: uuid.UUID
    question_version_id: uuid.UUID
    kind: str
    part_id: str | None
    payload: dict[str, Any]
    correct: bool | None
    created_at: datetime


def _view(row: Response, question_id: uuid.UUID) -> ResponseView:
    return ResponseView(
        id=row.id,
        question_id=question_id,
        question_version_id=row.question_version_id,
        kind=row.kind,
        part_id=row.part_id,
        payload=dict(row.payload),
        correct=row.correct,
        created_at=row.created_at,
    )


def add_response(
    session: Session,
    *,
    account_id: uuid.UUID,
    question_version_id: uuid.UUID,
    kind: str,
    part_id: str | None,
    payload: dict[str, Any],
    correct: bool | None,
) -> ResponseView:
    """Store one answer. The count is per account and per question (all versions of it) and is
    taken under a transaction-scoped advisory lock on that pair, so concurrent submissions
    cannot pass the limit together. Raises TooManyAnswers at MAX_ANSWERS_PER_QUESTION."""
    question_id = session.scalar(
        select(QuestionVersion.question_id).where(QuestionVersion.id == question_version_id)
    )
    if question_id is None:
        raise LookupError("unknown question version")
    session.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
        {"key": f"response:{account_id}:{question_id}"},
    )
    stored = session.scalar(
        select(func.count())
        .select_from(Response)
        .join(QuestionVersion, QuestionVersion.id == Response.question_version_id)
        .where(Response.account_id == account_id, QuestionVersion.question_id == question_id)
    )
    if (stored or 0) >= MAX_ANSWERS_PER_QUESTION:
        raise TooManyAnswers(str(question_id))
    row = Response(
        account_id=account_id,
        question_version_id=question_version_id,
        kind=kind,
        part_id=part_id,
        payload=payload,
        correct=correct,
    )
    session.add(row)
    session.flush()
    session.refresh(row)
    return _view(row, question_id)


def list_responses(
    session: Session,
    *,
    account_id: uuid.UUID,
    question_id: uuid.UUID | None,
    after: uuid.UUID | None,
    limit: int,
) -> list[ResponseView]:
    """The account's answers, newest first (identifiers are time-ordered), after the given
    one. At most `limit` rows."""
    query = (
        select(Response, QuestionVersion.question_id)
        .join(QuestionVersion, QuestionVersion.id == Response.question_version_id)
        .where(Response.account_id == account_id)
        .order_by(Response.id.desc())
        .limit(limit)
    )
    if question_id is not None:
        query = query.where(QuestionVersion.question_id == question_id)
    if after is not None:
        query = query.where(Response.id < after)
    return [_view(row, qid) for row, qid in session.execute(query)]


def delete_responses(session: Session, *, account_id: uuid.UUID) -> int:
    """Delete every answer of the account; the number deleted."""
    result = session.execute(
        delete(Response).where(Response.account_id == account_id).returning(Response.id)
    )
    return len(result.all())
