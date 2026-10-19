"""The caller's own stored answers (M1-G slice 8, D-66). Everything here is about the caller and
nobody else: there is no way to name another account."""

from __future__ import annotations

from fastapi import Request

from qlab.api import deps, responses_view
from qlab.api.deps import Caller
from qlab.api.routers.common import AUTH_ERRORS, Routes
from qlab.api.routers.common import question_id as decode_question_id
from qlab.api.routers.learner import Cursor, Limit
from qlab.api.schemas import DeletedOut, ResponsePage

router = Routes(tags=["responses"], responses=AUTH_ERRORS)


@router.get("/v1/me/responses", response_model=ResponsePage, operation_id="listMyResponses")
def list_my_responses(
    request: Request,
    caller: Caller,
    question_id: str | None = None,
    cursor: Cursor = None,
    limit: Limit = 20,
) -> ResponsePage:
    """The caller's stored answers, newest first. `question_id` narrows them to one question."""
    with deps.reading(request) as session:
        return responses_view.list_page(
            session,
            caller=caller,
            question_id=None if question_id is None else decode_question_id(question_id),
            cursor=cursor,
            limit=limit,
        )


@router.delete("/v1/me/responses", response_model=DeletedOut, operation_id="deleteMyResponses")
def delete_my_responses(request: Request, caller: Caller) -> DeletedOut:
    """Delete every answer the caller has stored (docs/SECURITY.md 5.4). Cannot be undone. The
    audit log records the count and the account, never the answers."""
    with deps.writing(request) as session:
        return responses_view.delete_all(session, caller=caller)
