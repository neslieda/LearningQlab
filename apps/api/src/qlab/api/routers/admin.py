"""Staff endpoints: review, editing in place and publishing (docs/API_DESIGN.md section 3.3).

Who may call which is decided by the policy table, not here. Every writing endpoint passes the
caller's opaque account identifier to the content service as the audit actor.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Query, Request

from qlab.api.deps import Caller, CurrentSettings
from qlab.api.routers.common import AUTH_ERRORS, CONFLICT, Routes
from qlab.api.routers.learner import Code, Cursor, Limit
from qlab.api.schemas import (
    DEFAULT_PAGE_SIZE,
    AdminQuestion,
    AdminQuestionPage,
    AdminVersion,
    DecisionRequest,
    History,
    ReasonRequest,
    RepublishRequest,
    UpdateDraftRequest,
    VersionStateOut,
)
from qlab.content.schema import Level, QuestionClass
from qlab.content.service import VersionStatus

router = Routes(tags=["admin"], responses=AUTH_ERRORS)

_QV = "/v1/admin/question-versions/{version_id}"


@router.get(
    "/v1/admin/questions", response_model=AdminQuestionPage, operation_id="adminListQuestions"
)
def list_questions(
    request: Request,
    caller: Caller,
    status: VersionStatus | None = None,
    exam_section: Code | None = None,
    level: Level | None = None,
    question_class: QuestionClass | None = None,
    syllabus_node: Annotated[
        Code | None, Query(description="Node code; matches primary and secondary nodes.")
    ] = None,
    has_unverified_visuals: bool | None = None,
    cursor: Cursor = None,
    limit: Limit = DEFAULT_PAGE_SIZE,
) -> AdminQuestionPage:
    """Questions in every status, oldest first. The filters apply to each question's latest
    version (highest number). Questions whose rights record does not permit display are not
    listed."""
    raise NotImplementedError


@router.get(
    "/v1/admin/questions/{question_id}",
    response_model=AdminQuestion,
    operation_id="adminGetQuestion",
)
def get_question(request: Request, caller: Caller, question_id: str) -> AdminQuestion:
    """A question and all its versions, without their content."""
    raise NotImplementedError


@router.post(
    "/v1/admin/questions/{question_id}/revisions",
    response_model=AdminVersion,
    status_code=201,
    responses=CONFLICT,
    operation_id="adminStartRevision",
)
def start_revision(request: Request, caller: Caller, question_id: str) -> AdminVersion:
    """Open a new draft version to correct a question; a published version is never edited
    (CLAUDE.md rule 7). 409 `working_version_exists` when one is already being worked on."""
    raise NotImplementedError


@router.get(_QV, response_model=AdminVersion, operation_id="adminGetVersion")
def get_version(request: Request, caller: Caller, version_id: str) -> AdminVersion:
    """A version in any status, with its whole document and its check results."""
    raise NotImplementedError


@router.get(f"{_QV}/history", response_model=History, operation_id="adminGetVersionHistory")
def get_history(request: Request, caller: Caller, version_id: str) -> History:
    """What happened to the version, oldest first."""
    raise NotImplementedError


@router.put(_QV, response_model=AdminVersion, responses=CONFLICT, operation_id="adminUpdateDraft")
def update_draft(
    request: Request, caller: Caller, version_id: str, body: UpdateDraftRequest
) -> AdminVersion:
    """Replace the content of a `draft` or `needs_fix` version; the result is `draft`.
    422 `invalid_document` when the document uses unknown labels or math that does not render;
    409 `invalid_transition` in any other status."""
    raise NotImplementedError


@router.post(
    f"{_QV}/submit", response_model=VersionStateOut, responses=CONFLICT, operation_id="adminSubmit"
)
def submit(request: Request, caller: Caller, version_id: str) -> VersionStateOut:
    """Run the automatic checks on a draft: the result is `in_review` or `needs_fix`."""
    raise NotImplementedError


@router.post(
    f"{_QV}/approve",
    response_model=VersionStateOut,
    responses={
        **CONFLICT,
        403: {
            "model": AUTH_ERRORS[404]["model"],
            "description": "The caller is the last editor and separation of duties is on "
            "(`self_approval_forbidden`).",
        },
    },
    operation_id="adminApprove",
)
def approve(
    request: Request,
    caller: Caller,
    settings: CurrentSettings,
    version_id: str,
    body: DecisionRequest,
) -> VersionStateOut:
    """`in_review` → `approved`, for exactly the content the caller looked at."""
    raise NotImplementedError


@router.post(
    f"{_QV}/request-changes",
    response_model=VersionStateOut,
    responses=CONFLICT,
    operation_id="adminRequestChanges",
)
def request_changes(
    request: Request, caller: Caller, version_id: str, body: ReasonRequest
) -> VersionStateOut:
    """Send an `in_review` or `approved` version back to `needs_fix`."""
    raise NotImplementedError


@router.post(
    f"{_QV}/reject", response_model=VersionStateOut, responses=CONFLICT, operation_id="adminReject"
)
def reject(
    request: Request, caller: Caller, version_id: str, body: ReasonRequest
) -> VersionStateOut:
    """`in_review` → `rejected` (final)."""
    raise NotImplementedError


@router.post(
    f"{_QV}/publish",
    response_model=VersionStateOut,
    responses=CONFLICT,
    operation_id="adminPublish",
)
def publish(
    request: Request, caller: Caller, version_id: str, body: DecisionRequest
) -> VersionStateOut:
    """`approved` → `published`. 409 `not_publishable` lists every reason: a failed or missing
    critical check, unverified visuals, rights (CLAUDE.md rule 8)."""
    raise NotImplementedError


@router.post(
    f"{_QV}/withdraw",
    response_model=VersionStateOut,
    responses=CONFLICT,
    operation_id="adminWithdraw",
)
def withdraw(
    request: Request, caller: Caller, version_id: str, body: ReasonRequest
) -> VersionStateOut:
    """`published` → `withdrawn`."""
    raise NotImplementedError


@router.post(
    f"{_QV}/republish",
    response_model=VersionStateOut,
    responses=CONFLICT,
    operation_id="adminRepublish",
)
def republish(
    request: Request, caller: Caller, version_id: str, body: RepublishRequest
) -> VersionStateOut:
    """`withdrawn` → `published`, under the same conditions as publishing."""
    raise NotImplementedError
