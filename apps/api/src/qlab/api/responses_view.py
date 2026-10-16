"""Stored learner answers at the API edge (M1-G slice 8, D-66; docs/slices/M1G-8-OGRENCI.md).

The result of a submission is built here from the published version, which holds the answers,
the explanation and the mark scheme. Only what section 3 of the slice lists goes out: no
objective, no stimulus description, no solution model."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from qlab.api import errors, ids
from qlab.api.language import looks_non_english
from qlab.api.policy import Principal
from qlab.api.schemas import (
    AnswerRequest,
    AnswerResult,
    DeletedOut,
    LanguageWarning,
    MarkPointOut,
    McqAnswer,
    McqRationale,
    McqResult,
    NoteOut,
    ResponseOut,
    ResponsePage,
    WrittenResult,
)
from qlab.attempts import service as attempts
from qlab.audit import service as audit
from qlab.content import service as content

_NOT_ENGLISH = LanguageWarning(
    code="answer_not_english", message="Please write your answer in English."
)
_ENTITY = "response"


def _does_not_fit() -> errors.ApiError:
    return errors.ApiError(422, "answer_does_not_fit", "The answer does not fit this question")


def _store(
    session: Session,
    caller: Principal,
    version_id: uuid.UUID,
    kind: str,
    part_id: str | None,
    payload: dict[str, Any],
    correct: bool | None,
) -> str:
    stored = attempts.add_response(
        session,
        account_id=caller.account_id,
        question_version_id=version_id,
        kind=kind,
        part_id=part_id,
        payload=payload,
        correct=correct,
    )
    return ids.encode(ids.RESPONSE, stored.id)


def submit(
    session: Session, *, caller: Principal, question_id: uuid.UUID, answer: AnswerRequest
) -> AnswerResult:
    view = content.get_published_version(session, question_id)
    document = view.document
    version_id = ids.encode(ids.QUESTION_VERSION, view.id)
    if isinstance(answer, McqAnswer):
        mcq = document.mcq
        if mcq is None:
            raise _does_not_fit()
        correct = answer.selected_key == mcq.correct_key
        response_id = _store(
            session, caller, view.id, "mcq", None, {"selected_key": answer.selected_key}, correct
        )
        return McqResult(
            kind="mcq",
            response_id=response_id,
            version_id=version_id,
            correct=correct,
            correct_key=mcq.correct_key,
            explanation=mcq.explanation,
            rationales=tuple(
                McqRationale(key=o.key, content=o.rationale)
                for o in mcq.options
                if o.key != mcq.correct_key and o.rationale is not None
            ),
        )
    if document.mcq is not None:
        raise _does_not_fit()
    part = next((p for p in document.parts if p.id == answer.part_id), None)
    if part is None:
        raise _does_not_fit()
    response_id = _store(session, caller, view.id, "written", part.id, {"text": answer.text}, None)
    return WrittenResult(
        kind="written",
        response_id=response_id,
        version_id=version_id,
        part_id=part.id,
        marks=part.marks,
        marks_capped=part.marks_capped,
        mark_points=tuple(
            MarkPointOut(
                id=p.id,
                content=p.content,
                kind=p.kind,
                alternative_group=p.alternative_group,
                route=p.route,
                accept_range=p.accept_range,
            )
            for p in part.mark_points
        ),
        notes=tuple(
            NoteOut(kind=n.kind, content=n.content, mark_point_id=n.mark_point_id)
            for n in part.notes
        ),
        language_warning=_NOT_ENGLISH if looks_non_english(answer.text) else None,
    )


def _out(view: attempts.ResponseView) -> ResponseOut:
    return ResponseOut(
        id=ids.encode(ids.RESPONSE, view.id),
        question_id=ids.encode(ids.QUESTION, view.question_id),
        version_id=ids.encode(ids.QUESTION_VERSION, view.question_version_id),
        kind=view.kind,  # type: ignore[arg-type]  # the table allows exactly these two
        part_id=view.part_id,
        selected_key=view.payload.get("selected_key"),
        text=view.payload.get("text"),
        correct=view.correct,
        created_at=view.created_at,
    )


def list_page(
    session: Session,
    *,
    caller: Principal,
    question_id: uuid.UUID | None,
    cursor: str | None,
    limit: int,
) -> ResponsePage:
    try:
        after = None if cursor is None else ids.decode(ids.RESPONSE, cursor)
    except ValueError:
        raise errors.ApiError(422, "invalid_cursor", "The cursor is not valid") from None
    found = attempts.list_responses(
        session, account_id=caller.account_id, question_id=question_id, after=after, limit=limit + 1
    )
    page = found[:limit]
    return ResponsePage(
        items=tuple(_out(v) for v in page),
        next_cursor=ids.encode(ids.RESPONSE, page[-1].id) if len(found) > limit else None,
    )


def delete_all(session: Session, *, caller: Principal) -> DeletedOut:
    deleted = attempts.delete_responses(session, account_id=caller.account_id)
    audit.record(
        session,
        actor=caller.actor,
        action="learner.responses_deleted",
        entity_type="account",
        entity_id=caller.actor,
        data={"deleted": deleted},
    )
    return DeletedOut(deleted=deleted)
