"""Invites: how an account comes to exist and get a role (M1-G slice 9, D-63).

Who may call which is decided by the policy table. `redeem` is a `SIGNED_IN` endpoint: a valid
token is enough, because the account is created there. The audit entries are written by
`qlab.api.invites_view`, in the same transaction.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Path, Request

from qlab.api import deps, invites_view
from qlab.api.deps import Caller, SignedInUser
from qlab.api.routers.common import AUTH_ERRORS, Routes
from qlab.api.routers.learner import Cursor, Limit
from qlab.api.schemas import (
    DEFAULT_PAGE_SIZE,
    CreateInviteRequest,
    InviteCreated,
    InviteId,
    InviteOut,
    InvitePage,
    RedeemInviteRequest,
    RedeemOut,
)

router = Routes(tags=["invites"], responses=AUTH_ERRORS)

_NOT_VALID = {
    404: {
        "model": AUTH_ERRORS[404]["model"],
        "description": "Unknown, expired, revoked or used-up invite (`invite_not_found`).",
    }
}


@router.post(
    "/v1/invites/redeem",
    response_model=RedeemOut,
    responses=_NOT_VALID,
    operation_id="redeemInvite",
)
def redeem(request: Request, caller: SignedInUser, body: RedeemInviteRequest) -> RedeemOut:
    """Use an invite: the caller's account is created if it does not exist and the invite's
    role is granted (an existing role is kept as it is). Using the same invite twice counts
    once. A disabled account: 401."""
    with deps.writing(request) as session:
        return invites_view.redeem(
            session, issuer=caller.issuer, subject=caller.subject, code=body.code
        )


@router.post(
    "/v1/admin/invites",
    status_code=201,
    response_model=InviteCreated,
    responses={
        403: {
            "model": AUTH_ERRORS[404]["model"],
            "description": "A teacher may invite students only (`invite_role_forbidden`).",
        }
    },
    operation_id="createInvite",
)
def create(request: Request, caller: Caller, body: CreateInviteRequest) -> InviteCreated:
    """A new invite link. The code is in this response only; only its SHA-256 is stored."""
    with deps.writing(request) as session:
        return invites_view.create(
            session,
            caller=caller,
            role=body.role,
            expires_in_days=body.expires_in_days,
            max_uses=body.max_uses,
        )


@router.get("/v1/admin/invites", response_model=InvitePage, operation_id="listInvites")
def list_invites(
    request: Request, caller: Caller, cursor: Cursor = None, limit: Limit = DEFAULT_PAGE_SIZE
) -> InvitePage:
    """Invites, newest first, without their codes. A teacher sees only their own."""
    with deps.reading(request) as session:
        return invites_view.list_page(session, caller=caller, cursor=cursor, limit=limit)


@router.post(
    "/v1/admin/invites/{invite_id}/revoke",
    response_model=InviteOut,
    operation_id="revokeInvite",
)
def revoke(request: Request, caller: Caller, invite_id: Annotated[InviteId, Path()]) -> InviteOut:
    """Stop an invite from being used. A teacher may revoke only their own (another's: 404).
    Revoking twice keeps the first revocation."""
    with deps.writing(request) as session:
        return invites_view.revoke(session, caller=caller, invite_id=invite_id)
