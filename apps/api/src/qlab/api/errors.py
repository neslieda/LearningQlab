"""Error responses: `application/problem+json` with a stable `code` (docs/API_DESIGN.md
section 4). `code` is the only field a client branches on.

A request that is not allowed and a resource that does not exist get the same response, byte
for byte: `not_found()` below is the only place that builds it.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from starlette.exceptions import HTTPException as StarletteHTTPException

from qlab.content import math
from qlab.content import service as content
from qlab.rights import service as rights

PROBLEM_MEDIA_TYPE = "application/problem+json"
_TYPE_BASE = "https://errors.qlab.invalid/"
_log = logging.getLogger("qlab.api")


class ProblemItem(BaseModel):
    """One thing that is wrong. `location` names the field or part it is about, if any."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    message: str
    location: str | None = None


class Problem(BaseModel):
    """RFC 9457 problem details."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    type: str
    title: str
    status: int
    code: str
    detail: str | None = None
    errors: tuple[ProblemItem, ...] = ()


class ApiError(Exception):
    def __init__(
        self,
        status: int,
        code: str,
        title: str,
        *,
        detail: str | None = None,
        errors: Sequence[ProblemItem] = (),
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(code)
        self.problem = Problem(
            type=_TYPE_BASE + code.replace("_", "-"),
            title=title,
            status=status,
            code=code,
            detail=detail,
            errors=tuple(errors),
        )
        self.headers = headers


def not_found() -> ApiError:
    """No such resource, or the caller may not know that it exists."""
    return ApiError(404, "not_found", "Not found")


def unauthenticated() -> ApiError:
    """No token, or a token that is not acceptable. Never says why."""
    return ApiError(
        401, "unauthenticated", "Authentication required", headers={"WWW-Authenticate": "Bearer"}
    )


def _response(error: ApiError) -> JSONResponse:
    return JSONResponse(
        error.problem.model_dump(mode="json"),
        status_code=error.problem.status,
        media_type=PROBLEM_MEDIA_TYPE,
        headers=error.headers,
    )


def from_service_error(error: Exception) -> ApiError | None:
    """The response for an error raised by a module's service, or None when it is not one the
    API knows how to explain (it then becomes a 500)."""
    if isinstance(error, content.NotFound | rights.RightsDenied):
        # A write that the rights record does not permit looks like a missing resource, as a
        # read already does (fail-closed, CLAUDE.md rule 2).
        return not_found()
    if isinstance(error, content.InvalidDocument):
        return ApiError(
            422,
            "invalid_document",
            "The document was not accepted",
            errors=[
                ProblemItem(
                    code="invalid_document",
                    message=p.message,
                    location=None if p.location is None else f"document.{p.location}",
                )
                for p in error.errors
            ],
        )
    if isinstance(error, content.OwnContentRightsUnavailable):
        return ApiError(
            409,
            "own_content_rights_unavailable",
            "New questions cannot be created",
            detail="The platform's own-content rights record is missing or does not permit "
            "display. Nothing was created.",
        )
    if isinstance(error, content.StaleContent):
        return ApiError(
            409,
            "stale_content",
            "The content has changed since it was read",
            detail="Read the version again and repeat the decision on the current content.",
        )
    if isinstance(error, content.NotPublishable):
        return ApiError(
            409,
            "not_publishable",
            "Question version cannot be published",
            errors=[ProblemItem(code=reason, message=reason) for reason in error.reasons],
        )
    if isinstance(error, content.SelfApprovalForbidden):
        return ApiError(
            403,
            "self_approval_forbidden",
            "The last editor of a version cannot approve it",
        )
    if isinstance(error, content.WorkingVersionExists):
        return ApiError(
            409, "working_version_exists", "The question already has a version being worked on"
        )
    if isinstance(error, content.InvalidTransition):
        return ApiError(
            409,
            "invalid_transition",
            "The version is not in a state that allows this",
            detail=str(error),
        )
    if isinstance(error, math.RendererUnavailable):
        return ApiError(503, "renderer_unavailable", "The math renderer is not available")
    return None


def install(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(request: Request, error: ApiError) -> JSONResponse:
        return _response(error)

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, error: RequestValidationError) -> JSONResponse:
        # Location and message only: the rejected input is never echoed back. Two kinds of
        # error would carry it anyway (a key the caller invented, a discriminator value).
        items = []
        for item in error.errors():
            kind = str(item.get("type", "invalid"))
            location = [str(part) for part in item.get("loc", ())]
            message = str(item.get("msg", "invalid"))
            if kind == "extra_forbidden":
                location = location[:-1]
            elif kind == "union_tag_invalid":
                message = "Unknown kind"
            items.append(
                ProblemItem(code=kind, message=message, location=".".join(location) or None)
            )
        return _response(
            ApiError(422, "validation_failed", "The request is not valid", errors=items)
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, error: StarletteHTTPException) -> JSONResponse:
        # A method the policy table does not list for a path is not an endpoint: default deny,
        # the same answer as for a path that does not exist.
        if error.status_code in (404, 405):
            return _response(not_found())
        return _response(ApiError(error.status_code, "http_error", "Request failed"))

    async def _service(request: Request, error: Exception) -> JSONResponse:
        known = from_service_error(error)
        if known is None:  # a new service error nobody mapped: fail closed, say nothing
            _log.error("unmapped service error: %s", type(error).__name__)
            known = ApiError(500, "internal_error", "Internal error")
        return _response(known)

    for service_error in (content.ContentError, rights.RightsDenied, math.RendererUnavailable):
        app.add_exception_handler(service_error, _service)

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, error: Exception) -> JSONResponse:
        _log.exception("unhandled error", exc_info=error)
        return _response(ApiError(500, "internal_error", "Internal error"))
