"""What any signed-in account may read: the syllabus and published questions in the learner
view (docs/slices/M1G-5-YETKILER.md sections 3 and 4). Nothing here writes."""

from __future__ import annotations

from typing import Annotated

from fastapi import Query, Request

from qlab.api.deps import Caller
from qlab.api.routers.common import AUTH_ERRORS, Routes
from qlab.api.schemas import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    CheckRequest,
    CheckResult,
    LearnerQuestion,
    LearnerQuestionPage,
    SyllabusOut,
)
from qlab.content.schema import Level, QuestionClass

router = Routes(tags=["questions"], responses=AUTH_ERRORS)

Cursor = Annotated[str | None, Query(max_length=200, description="`next_cursor` of the last page.")]
Limit = Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)]
Code = Annotated[str, Query(max_length=120)]


@router.get(
    "/v1/programs/{program}/subjects/{subject}/syllabus",
    response_model=SyllabusOut,
    operation_id="getSyllabus",
)
def get_syllabus(
    request: Request,
    caller: Caller,
    program: str,
    subject: str,
    version: Annotated[
        Code | None, Query(description="Syllabus version code. Default: the newest version.")
    ] = None,
) -> SyllabusOut:
    """The syllabus tree and exam format vocabulary of a subject. Unknown programme, subject
    or version: 404."""
    raise NotImplementedError


@router.get(
    "/v1/questions",
    response_model=LearnerQuestionPage,
    operation_id="listQuestions",
)
def list_questions(
    request: Request,
    caller: Caller,
    exam_section: Code | None = None,
    level: Level | None = None,
    question_class: QuestionClass | None = None,
    syllabus_node: Annotated[
        Code | None, Query(description="Node code; matches primary and secondary nodes.")
    ] = None,
    cursor: Cursor = None,
    limit: Limit = DEFAULT_PAGE_SIZE,
) -> LearnerQuestionPage:
    """Published questions, oldest question first. Only questions with a published version
    whose rights record permits display are listed. A cursor that was not issued by this
    endpoint: 422."""
    raise NotImplementedError


@router.get(
    "/v1/questions/{question_id}",
    response_model=LearnerQuestion,
    operation_id="getQuestion",
)
def get_question(request: Request, caller: Caller, question_id: str) -> LearnerQuestion:
    """The published version of a question in the learner view: no answer, no mark scheme.
    404 when the question does not exist, has no published version, or may not be displayed."""
    raise NotImplementedError


@router.post(
    "/v1/questions/{question_id}/check",
    response_model=CheckResult,
    operation_id="checkAnswer",
)
def check_answer(
    request: Request, caller: Caller, question_id: str, answer: CheckRequest
) -> CheckResult:
    """Send an answer and see the correct one. The answer is not stored and not marked.

    - `mcq`: whether the selected option is correct, and the correct option.
    - `written`: the mark points and notes of that part, and a language warning when the
      answer does not look English.

    An `mcq` answer to a structured question, a `written` answer to a multiple-choice
    question or an unknown `part_id`: 422 `answer_does_not_fit`.
    """
    raise NotImplementedError
