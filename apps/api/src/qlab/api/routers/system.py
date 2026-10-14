"""Health check and the caller's own account."""

from __future__ import annotations

from qlab.api import ids
from qlab.api.deps import Caller
from qlab.api.routers.common import AUTH_ERRORS, Routes
from qlab.api.schemas import Health, Me

router = Routes(tags=["system"])


@router.get("/healthz", response_model=Health, operation_id="health")
def health() -> Health:
    """Liveness. Needs no token and returns no content."""
    return Health(status="ok")


@router.get("/v1/me", response_model=Me, responses=AUTH_ERRORS, operation_id="getMe")
def me(caller: Caller) -> Me:
    """The caller's account identifier and roles."""
    return Me(
        account_id=ids.encode(ids.ACCOUNT, caller.account_id),
        roles=tuple(sorted(caller.roles)),
    )
