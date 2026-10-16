"""Invite operations at the API edge: identifiers, the audit entries and the response shapes
(M1-G slice 9, docs/slices/M1G-9-ACILIS.md section 3.3). The code of an invite is never written
to the audit log; it is returned once, by `create`."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from qlab.api import errors, ids
from qlab.api.policy import Principal
from qlab.api.schemas import InviteCreated, InviteOut, InvitePage, RedeemOut
from qlab.audit import service as audit
from qlab.organizations import service as organizations
from qlab.organizations.service import InviteView, Role

CLI_ACTOR = "cli:owner"
_ENTITY = "invite"


def encode_invite(value: uuid.UUID) -> str:
    return ids.encode(ids.INVITE, value)


def out(view: InviteView) -> InviteOut:
    return InviteOut(
        id=encode_invite(view.id),
        role=view.role.value,  # type: ignore[arg-type]  # an invitable role, checked on create
        created_by=view.created_by,
        created_at=view.created_at,
        expires_at=view.expires_at,
        max_uses=view.max_uses,
        uses=view.uses,
        revoked_at=view.revoked_at,
    )


def create_as(
    session: Session,
    *,
    actor: str,
    roles: frozenset[Role],
    role: str,
    expires_in_days: int,
    max_uses: int,
) -> InviteCreated:
    """Create an invite for `actor` (an account or `cli:owner`) and audit it. Shared by the
    endpoint and the command line."""
    view, code = organizations.create_invite(
        session,
        created_by=actor,
        creator_roles=roles,
        role=Role(role),
        expires_in_days=expires_in_days,
        max_uses=max_uses,
    )
    audit.record(
        session,
        actor=actor,
        action="invite.created",
        entity_type=_ENTITY,
        entity_id=encode_invite(view.id),
        data={
            "role": view.role.value,
            "expires_at": view.expires_at.isoformat(),
            "max_uses": view.max_uses,
        },
    )
    return InviteCreated(**out(view).model_dump(), code=code)


def create(
    session: Session, *, caller: Principal, role: str, expires_in_days: int, max_uses: int
) -> InviteCreated:
    return create_as(
        session,
        actor=caller.actor,
        roles=caller.roles,
        role=role,
        expires_in_days=expires_in_days,
        max_uses=max_uses,
    )


def redeem(session: Session, *, issuer: str, subject: str, code: str) -> RedeemOut:
    try:
        result = organizations.redeem_invite(session, issuer=issuer, subject=subject, code=code)
    except organizations.AccountDisabled:
        raise errors.unauthenticated() from None
    if result.counted:
        audit.record(
            session,
            actor=ids.actor(result.account_id),
            action="invite.redeemed",
            entity_type=_ENTITY,
            entity_id=encode_invite(result.invite_id),
            data={
                "role": result.role.value,
                "account_id": ids.actor(result.account_id),
                "role_granted": result.granted,
            },
        )
    return RedeemOut(
        account_id=ids.actor(result.account_id),
        roles=tuple(role for role in Role if role in result.roles),
    )


def list_page(session: Session, *, caller: Principal, cursor: str | None, limit: int) -> InvitePage:
    try:
        after = None if cursor is None else ids.decode(ids.INVITE, cursor)
    except ValueError:
        raise errors.ApiError(422, "invalid_cursor", "The cursor is not valid") from None
    found = organizations.list_invites(
        session, actor=caller.actor, roles=caller.roles, after=after, limit=limit + 1
    )
    page = found[:limit]
    return InvitePage(
        items=tuple(out(view) for view in page),
        next_cursor=encode_invite(page[-1].id) if len(found) > limit else None,
    )


def revoke(session: Session, *, caller: Principal, invite_id: str) -> InviteOut:
    try:
        identifier = ids.decode(ids.INVITE, invite_id)
    except ValueError:
        raise errors.not_found() from None
    view, changed = organizations.revoke_invite(
        session, invite_id=identifier, actor=caller.actor, roles=caller.roles
    )
    if changed:  # a second revocation changes nothing and writes nothing
        audit.record(
            session,
            actor=caller.actor,
            action="invite.revoked",
            entity_type=_ENTITY,
            entity_id=encode_invite(identifier),
            data={"role": view.role.value},
        )
    return out(view)
