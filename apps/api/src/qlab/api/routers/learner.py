"""What any signed-in account may read: the syllabus and published questions in the learner
view (docs/slices/M1G-5-YETKILER.md sections 3 and 4). Nothing here writes."""

from __future__ import annotations

from typing import Annotated

from fastapi import Path, Query, Request

from qlab.api import deps, errors, ids, learner_view, responses_view
from qlab.api.deps import Caller
from qlab.api.routers.common import AUTH_ERRORS, Routes
from qlab.api.routers.common import question_id as decode_question_id
from qlab.api.schemas import (
    CODE_PATTERN,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    AnswerRequest,
    AnswerResult,
    CatalogOut,
    CatalogSubjectOut,
    CatalogVersionOut,
    ExamSectionOut,
    LearnerQuestion,
    LearnerQuestionPage,
    SyllabusNodeOut,
    SyllabusOut,
)
from qlab.content import service as content
from qlab.content.schema import Level, QuestionClass
from qlab.syllabus import service as syllabus

router = Routes(tags=["questions"], responses=AUTH_ERRORS)

Cursor = Annotated[str | None, Query(max_length=200, description="`next_cursor` of the last page.")]
Limit = Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)]
# Codes of exam sections, syllabus nodes and versions: nothing else reaches a query.
Code = Annotated[str, Query(max_length=120, pattern=CODE_PATTERN)]
PathCode = Annotated[str, Path(max_length=120, pattern=CODE_PATTERN)]


@router.get("/v1/programs", response_model=CatalogOut, operation_id="listPrograms")
def list_programs(request: Request, caller: Caller) -> CatalogOut:
    """Programmes, subjects and syllabus versions that questions can be written against."""
    with deps.reading(request) as session:
        entries = syllabus.list_catalog(session)
    return CatalogOut(
        items=tuple(
            CatalogSubjectOut(
                program=e.program,
                program_name=e.program_name,
                subject=e.subject,
                subject_name=e.subject_name,
                versions=tuple(CatalogVersionOut(code=c, title=t) for c, t in e.versions),
            )
            for e in entries
        )
    )


@router.get(
    "/v1/programs/{program}/subjects/{subject}/syllabus",
    response_model=SyllabusOut,
    operation_id="getSyllabus",
)
def get_syllabus(
    request: Request,
    caller: Caller,
    program: PathCode,
    subject: PathCode,
    version: Annotated[
        Code | None, Query(description="Syllabus version code. Default: the newest version.")
    ] = None,
) -> SyllabusOut:
    """The syllabus tree and exam format vocabulary of a subject. Unknown programme, subject
    or version: 404."""
    with deps.reading(request) as session:
        tree = syllabus.get_tree(session, program=program, subject=subject, version=version)
    if tree is None:
        raise errors.not_found()
    return SyllabusOut(
        program=tree.program,
        subject=tree.subject,
        version=tree.version,
        title=tree.title,
        nodes=tuple(
            SyllabusNodeOut(
                code=n.code,
                title=n.title,
                parent=n.parent,
                is_leaf=n.is_leaf,
                attributes=n.attributes,
            )
            for n in tree.nodes
        ),
        exam_sections=tuple(ExamSectionOut(code=c, title=t) for c, t in tree.exam_sections),
        command_terms=tree.command_terms,
    )


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
    after = None
    if cursor is not None:
        try:
            after = ids.decode(ids.QUESTION, cursor)
        except ValueError:
            raise errors.ApiError(422, "invalid_cursor", "The cursor is not valid") from None
    selection = content.ListFilter(
        exam_section=exam_section,
        level=level,
        question_class=question_class,
        syllabus_node=syllabus_node,
    )
    with deps.reading(request) as session:
        found = content.list_published(session, filter=selection, after=after, limit=limit + 1)
    page = found[:limit]
    return LearnerQuestionPage(
        items=tuple(learner_view.to_learner_summary(v) for v in page),
        next_cursor=ids.encode(ids.QUESTION, page[-1].question_id) if len(found) > limit else None,
    )


@router.get(
    "/v1/questions/{question_id}",
    response_model=LearnerQuestion,
    operation_id="getQuestion",
)
def get_question(request: Request, caller: Caller, question_id: str) -> LearnerQuestion:
    """The published version of a question in the learner view: no answer, no mark scheme.
    404 when the question does not exist, has no published version, or may not be displayed."""
    with deps.reading(request) as session:
        view = content.get_published_version(session, decode_question_id(question_id))
    return learner_view.to_learner_question(view)


@router.post(
    "/v1/questions/{question_id}/answers",
    status_code=201,
    response_model=AnswerResult,
    responses={
        422: {
            "model": AUTH_ERRORS[404]["model"],
            "description": "The answer does not fit the question (`answer_does_not_fit`).",
        },
        429: {
            "model": AUTH_ERRORS[404]["model"],
            "description": "200 answers to this question are stored already "
            "(`too_many_answers`), or 5000 answers in all (`answer_limit_reached`).",
        },
    },
    operation_id="submitAnswer",
)
def submit_answer(
    request: Request, caller: Caller, question_id: str, answer: AnswerRequest
) -> AnswerResult:
    """Send an answer. It is stored for the caller (D-66) and the correct answer comes back.

    - `mcq`: whether the selected option is correct, the correct option, the explanation and
      the reason each wrong option is wrong.
    - `written`: the mark points and notes of that part, and a language warning when the
      answer does not look English. The answer is not marked.

    An `mcq` answer to a structured question, a `written` answer to a multiple-choice
    question or an unknown `part_id`: 422 `answer_does_not_fit`.
    """
    with deps.writing(request) as session:
        return responses_view.submit(
            session, caller=caller, question_id=decode_question_id(question_id), answer=answer
        )
