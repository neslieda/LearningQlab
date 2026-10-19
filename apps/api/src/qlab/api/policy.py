"""The authorization policy: one layer, default deny (CLAUDE.md rule 9, docs/SECURITY.md
section 3).

`ENDPOINT_POLICY` is the endpoint x role table. It is the only place that says who may call
what, and it is also the data the authorization tests are generated from. An endpoint that is
not in the table cannot be served: the application refuses to start (`check_routes`), and a
request that reached such a route anyway would be refused.

Every route of the application is a `PolicyRoute`. It decides before anything else happens:
before the body is read, before parameters are validated, before the handler runs. So a caller
who is not allowed learns nothing from the shape of the answer:

- no token, or a token that is not acceptable, or an unknown or disabled account: 401;
- an account without a role the endpoint allows: 404, the same response as for a resource that
  does not exist;
- outside the local environment, staff roles count only when the token comes from the staff
  organisation of the identity provider, where two-step verification is enforced (M1-G slice
  9, docs/SECURITY.md section 2): a caller whose only allowing roles are staff roles gets 403
  `mfa_required`.

`SIGNED_IN` endpoints need a valid token but no account: they are how an account comes to
exist (an invite is redeemed, D-63). Their handlers receive a `SignedInCaller`.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable, Coroutine, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final

from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session, sessionmaker
from starlette.concurrency import run_in_threadpool
from starlette.responses import Response
from starlette.routing import BaseRoute

from qlab.api import errors, ids
from qlab.identity import service as identity
from qlab.identity.tokens import InvalidToken, TokenVerifier
from qlab.organizations import service as organizations
from qlab.organizations.service import Role

_log = logging.getLogger("qlab.api.policy")


class Public:
    """Marker for an endpoint that needs no token. It must return no content."""


class SignedIn:
    """Marker for an endpoint that needs a valid token and nothing else (no account, no role)."""


PUBLIC: Final = Public()
SIGNED_IN: Final = SignedIn()
Access = Public | SignedIn | frozenset[Role]

EVERYONE: Final = frozenset(Role)
STAFF: Final = frozenset({Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN})
PUBLISHERS: Final = frozenset({Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN})
INVITERS: Final = frozenset({Role.TEACHER, Role.PLATFORM_ADMIN})
# Roles that need two-step verification (docs/SECURITY.md section 2).
MFA_ROLES: Final = STAFF

_QV = "/v1/admin/question-versions/{version_id}"

# docs/SECURITY.md section 3 (M1-G slice 5, D-59). Key: HTTP method and route template.
ENDPOINT_POLICY: Final[Mapping[tuple[str, str], Access]] = MappingProxyType(
    {
        ("GET", "/healthz"): PUBLIC,
        ("GET", "/v1/me"): EVERYONE,
        ("POST", "/v1/invites/redeem"): SIGNED_IN,
        ("POST", "/v1/admin/invites"): INVITERS,
        ("GET", "/v1/admin/invites"): INVITERS,
        ("POST", "/v1/admin/invites/{invite_id}/revoke"): INVITERS,
        ("GET", "/v1/programs"): EVERYONE,
        ("GET", "/v1/programs/{program}/subjects/{subject}/syllabus"): EVERYONE,
        ("GET", "/v1/questions"): EVERYONE,
        ("GET", "/v1/questions/{question_id}"): EVERYONE,
        ("POST", "/v1/questions/{question_id}/answers"): EVERYONE,
        ("GET", "/v1/me/responses"): EVERYONE,
        ("DELETE", "/v1/me/responses"): EVERYONE,
        ("GET", "/v1/admin/questions"): STAFF,
        ("POST", "/v1/admin/questions"): STAFF,
        ("GET", "/v1/admin/questions/{question_id}"): STAFF,
        ("GET", _QV): STAFF,
        ("GET", f"{_QV}/history"): STAFF,
        ("PUT", _QV): STAFF,
        ("POST", f"{_QV}/submit"): STAFF,
        ("POST", f"{_QV}/approve"): STAFF,
        ("POST", f"{_QV}/request-changes"): STAFF,
        ("POST", f"{_QV}/reject"): STAFF,
        ("POST", "/v1/admin/questions/{question_id}/revisions"): STAFF,
        ("POST", f"{_QV}/publish"): PUBLISHERS,
        ("POST", f"{_QV}/withdraw"): PUBLISHERS,
        ("POST", f"{_QV}/republish"): PUBLISHERS,
    }
)


class PolicyError(RuntimeError):
    """The routes and the policy table do not agree; the application must not start."""


@dataclass(frozen=True)
class SignedInCaller:
    """A caller with a valid token, who may not have an account yet."""

    issuer: str
    subject: str


@dataclass(frozen=True)
class Principal:
    """Who is calling. `actor` is the opaque form written to the audit log."""

    account_id: uuid.UUID
    roles: frozenset[Role]

    @property
    def actor(self) -> str:
        return ids.actor(self.account_id)


def _bearer_token(request: Request) -> str:
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise errors.unauthenticated()
    return token.strip()


def _load_principal(
    session_factory: sessionmaker[Session], issuer: str, subject: str
) -> Principal | None:
    with session_factory() as session:
        try:
            account = identity.find_account(session, issuer=issuer, subject=subject)
            if account is None or not account.is_active:
                return None
            return Principal(account.id, organizations.roles_of(session, account.id))
        finally:
            session.rollback()


async def authorize(request: Request, access: Access | None) -> Principal | SignedInCaller | None:
    """Decide whether the request may reach its handler. Returns the caller, or None for a
    public endpoint; otherwise raises the 401, 403 or 404 response."""
    if access is None:
        # Not reachable when the application was built by `create_app`; refuse all the same.
        raise errors.not_found()
    if isinstance(access, Public):
        return None
    verifier: TokenVerifier = request.app.state.verifier
    try:
        # In a worker thread: verifying may fetch the provider's keys (network, up to seconds),
        # which must not block the event loop for every other request.
        claims = await run_in_threadpool(verifier.verify, _bearer_token(request))
    except InvalidToken as error:
        _log.info("token refused: %s", error)
        raise errors.unauthenticated() from None
    if isinstance(access, SignedIn):
        return SignedInCaller(issuer=claims.issuer, subject=claims.subject)
    principal = await run_in_threadpool(
        _load_principal, request.app.state.session_factory, claims.issuer, claims.subject
    )
    if principal is None:
        raise errors.unauthenticated()
    if not principal.roles & access:
        raise errors.not_found()
    staff_organization = request.app.state.staff_organization
    if staff_organization is not None and claims.organization != staff_organization:
        # Staff roles need the staff sign-in, where two-step verification is enforced.
        principal = Principal(principal.account_id, principal.roles - MFA_ROLES)
        if not principal.roles & access:
            raise errors.ApiError(
                403,
                "mfa_required",
                "Staff access needs a staff sign-in with two-step verification",
            )
    return principal


MAX_BODY_BYTES: Final = 1024 * 1024
# Tighter limits for endpoints whose body is small by nature.
BODY_LIMITS: Final[Mapping[tuple[str, str], int]] = MappingProxyType(
    {("POST", "/v1/questions/{question_id}/answers"): 64 * 1024}
)


def check_body_size(request: Request, limit: int) -> None:
    """Refuse a body that is too large before any of it is read. A body must announce its
    length: 411 without `Content-Length` when one is being sent, 413 above the limit."""
    declared = request.headers.get("content-length")
    if declared is None:
        if "transfer-encoding" in request.headers:
            raise errors.ApiError(411, "length_required", "Content-Length is required")
        return
    if not declared.isascii() or not declared.isdigit() or int(declared) > limit:
        raise errors.ApiError(413, "payload_too_large", "The request body is too large")


class PolicyRoute(APIRoute):
    """A route that is authorized before its handler, its parameters or its body are touched."""

    def access(self, method: str) -> Access | None:
        return ENDPOINT_POLICY.get((method, self.path_format))

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def authorized(request: Request) -> Response:
            request.state.principal = await authorize(request, self.access(request.method))
            # Only after the caller is known to be allowed, and still before the body is read.
            check_body_size(
                request, BODY_LIMITS.get((request.method, self.path_format), MAX_BODY_BYTES)
            )
            return await handler(request)

        return authorized


def principal(request: Request) -> Principal:
    """The authenticated caller of a non-public endpoint (FastAPI dependency)."""
    caller = getattr(request.state, "principal", None)
    if not isinstance(caller, Principal):
        raise errors.not_found()
    return caller


def signed_in(request: Request) -> SignedInCaller:
    """The caller of a `SIGNED_IN` endpoint (FastAPI dependency)."""
    caller = getattr(request.state, "principal", None)
    if not isinstance(caller, SignedInCaller):
        raise errors.not_found()
    return caller


def _declared(routes: list[BaseRoute]) -> set[tuple[str, str]]:
    declared: set[tuple[str, str]] = set()
    for route in routes:
        if not isinstance(route, PolicyRoute):
            raise PolicyError(
                f"route {getattr(route, 'path', route)!r} is not a PolicyRoute: every route "
                f"goes through the policy layer"
            )
        for method in route.methods or ():
            declared.add((method, route.path_format))
    return declared


def check_routes(app: FastAPI) -> None:
    """PolicyError unless the application's routes are exactly the endpoints of the table."""
    declared = _declared(app.routes)
    missing = sorted(declared - ENDPOINT_POLICY.keys())
    if missing:
        raise PolicyError(f"endpoints without an entry in the policy table: {missing}")
    unused = sorted(ENDPOINT_POLICY.keys() - declared)
    if unused:
        raise PolicyError(f"policy table entries without a route: {unused}")
    for (method, path), access in ENDPOINT_POLICY.items():
        if not isinstance(access, Public) and not access:
            raise PolicyError(f"{method} {path} allows no role")
