"""Pieces every router uses."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI

from qlab.api import errors, ids
from qlab.api.errors import Problem

# Documented error responses. 401 and 404 can come from any endpoint but /healthz.
_PROBLEM: dict[str, Any] = {"model": Problem, "content": {errors.PROBLEM_MEDIA_TYPE: {}}}
AUTH_ERRORS: dict[int | str, dict[str, Any]] = {
    401: {**_PROBLEM, "description": "No acceptable token (`unauthenticated`)."},
    404: {
        **_PROBLEM,
        "description": "No such resource, or the caller may not know of it (`not_found`).",
    },
    422: {**_PROBLEM, "description": "The request is not valid (`validation_failed`)."},
}
CONFLICT: dict[int | str, dict[str, Any]] = {
    409: {
        **_PROBLEM,
        "description": "`invalid_transition`, `stale_content`, `not_publishable` or "
        "`working_version_exists`.",
    },
}


def question_id(text: str) -> uuid.UUID:
    """The UUID of a `q_...` path parameter. A malformed identifier names nothing: 404."""
    try:
        return ids.decode(ids.QUESTION, text)
    except ValueError:
        raise errors.not_found() from None


def version_id(text: str) -> uuid.UUID:
    """The UUID of a `qv_...` path parameter. A malformed identifier names nothing: 404."""
    try:
        return ids.decode(ids.QUESTION_VERSION, text)
    except ValueError:
        raise errors.not_found() from None


class Routes:
    """The endpoints of one resource group. They are added to the application's own router
    (`register`), never through an included router, so that every one of them is a
    `qlab.api.policy.PolicyRoute` handled by that class and nothing else."""

    def __init__(
        self, *, tags: list[str], responses: dict[int | str, dict[str, Any]] | None = None
    ) -> None:
        self._tags = tags
        self._responses = responses or {}
        self._endpoints: list[tuple[str, str, Callable[..., Any], dict[str, Any]]] = []

    def _add[F: Callable[..., Any]](
        self, method: str, path: str, options: dict[str, Any]
    ) -> Callable[[F], F]:
        def decorator(endpoint: F) -> F:
            self._endpoints.append((method, path, endpoint, options))
            return endpoint

        return decorator

    def get[F: Callable[..., Any]](self, path: str, **options: Any) -> Callable[[F], F]:
        return self._add("GET", path, options)

    def post[F: Callable[..., Any]](self, path: str, **options: Any) -> Callable[[F], F]:
        return self._add("POST", path, options)

    def put[F: Callable[..., Any]](self, path: str, **options: Any) -> Callable[[F], F]:
        return self._add("PUT", path, options)

    def register(self, app: FastAPI) -> None:
        for method, path, endpoint, options in self._endpoints:
            responses = {**self._responses, **options.get("responses", {})}
            app.add_api_route(
                path,
                endpoint,
                methods=[method],
                **{**options, "tags": self._tags, "responses": responses},
            )
