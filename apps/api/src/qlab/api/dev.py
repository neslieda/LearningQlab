"""Local development command: `python -m qlab.api.dev <command>` (M1G-5-SOZLESME 3.7).

| Command | Effect |
|---|---|
| `init` | Create the key if missing; open `dev-<role>` accounts. Repeatable. Prints ids. |
| `token <role> [--hours N]` | Print only a token for that role. Default 8 hours, at most 24. |
| `accounts` | List the development accounts and their roles. |
| `grant <subject> <role>` / `revoke ...` | Give or take a role on a development-issuer account. |

Runs only when `QLAB_ENV=local`; in any other environment nothing is touched. The key file's
contents are never printed. Every change of a role writes an audit entry in the same transaction.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from collections.abc import Sequence
from datetime import timedelta

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from sqlalchemy.orm import Session

from qlab.api import ids
from qlab.api.settings import Environment, Settings, StartupError
from qlab.audit import service as audit
from qlab.identity import devkey
from qlab.identity import service as identity
from qlab.identity.tokens import DEV_AUDIENCE, DEV_ISSUER, sign
from qlab.organizations import service as organizations
from qlab.organizations.service import Role

ACTOR = "system:dev-cli"
DEFAULT_HOURS = 8.0
MAX_HOURS = 24.0


class DevCommandRefused(Exception):
    """An expected refusal: the message is shown on stderr and the exit status is 2."""


def subject_for(role: Role) -> str:
    return f"dev-{role.value}"


def _record(session: Session, action: str, account_id: uuid.UUID, role: Role) -> None:
    audit.record(
        session,
        actor=ACTOR,
        action=action,
        entity_type="account",
        entity_id=ids.actor(account_id),
        data={"role": role.value},
    )


def grant_role(session: Session, *, subject: str, role: Role) -> tuple[uuid.UUID, bool]:
    """Give `role` to the account (DEV_ISSUER, subject), creating the account if needed.
    Returns the account id and whether anything changed; only a change writes an audit entry."""
    account = identity.ensure_account(session, issuer=DEV_ISSUER, subject=subject)
    changed = organizations.grant(session, account_id=account.id, role=role, granted_by=ACTOR)
    if changed:
        _record(session, "role_assignment.granted", account.id, role)
    return account.id, changed


def revoke_role(session: Session, *, subject: str, role: Role) -> tuple[uuid.UUID, bool]:
    """Take `role` from the account (DEV_ISSUER, subject). DevCommandRefused when there is no
    such account. Returns the account id and whether anything changed."""
    if not subject or subject != subject.strip() or not subject.isprintable():
        raise DevCommandRefused(f"no account {subject!r} of issuer {DEV_ISSUER}")
    account = identity.find_account(session, issuer=DEV_ISSUER, subject=subject)
    if account is None:
        raise DevCommandRefused(f"no account {subject!r} of issuer {DEV_ISSUER}")
    changed = organizations.revoke(session, account_id=account.id, role=role, revoked_by=ACTOR)
    if changed:
        _record(session, "role_assignment.revoked", account.id, role)
    return account.id, changed


def init_accounts(session: Session) -> dict[Role, uuid.UUID]:
    """Make sure `dev-<role>` exists for every role and holds that role."""
    result: dict[Role, uuid.UUID] = {}
    for role in Role:
        account_id, _ = grant_role(session, subject=subject_for(role), role=role)
        result[role] = account_id
    return result


def ensure_key(settings: Settings) -> Ed25519PrivateKey:
    """The development key; generated only when the file does not exist, never overwritten.
    DevKeyError when an existing file is unsafe or not a key."""
    path = settings.dev_key_file
    if path is None:
        raise DevCommandRefused("no development key file is configured")
    if path.exists():
        return devkey.load(path)
    return devkey.generate(path)


def make_token(
    session: Session, key: Ed25519PrivateKey, *, role: Role, hours: float = DEFAULT_HOURS
) -> str:
    """A token for the role's development account. DevCommandRefused (run `init`) when the
    account is missing or does not hold the role."""
    if not 0 < hours <= MAX_HOURS:
        raise DevCommandRefused(f"--hours must be above 0 and at most {MAX_HOURS:g}")
    subject = subject_for(role)
    account = identity.find_account(session, issuer=DEV_ISSUER, subject=subject)
    if account is None or role not in organizations.roles_of(session, account.id):
        raise DevCommandRefused(
            f"account {subject!r} does not exist or lacks the role; "
            "run `python -m qlab.api.dev init`"
        )
    return sign(
        key,
        issuer=DEV_ISSUER,
        audience=DEV_AUDIENCE,
        subject=subject,
        lifetime=timedelta(hours=hours),
    )


def list_accounts(session: Session) -> list[tuple[str, uuid.UUID, list[Role]]]:
    """(subject, id, roles) of the `dev-<role>` accounts that exist, in role order. Accounts
    created with `grant` under other subjects are not found by this listing: the identity
    service has no way to list accounts."""
    rows: list[tuple[str, uuid.UUID, list[Role]]] = []
    for role in Role:
        subject = subject_for(role)
        account = identity.find_account(session, issuer=DEV_ISSUER, subject=subject)
        if account is None:
            continue
        held = organizations.roles_of(session, account.id)
        rows.append((subject, account.id, [r for r in Role if r in held]))
    return rows


def _hours(text: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a number") from None
    if not 0 < value <= MAX_HOURS:
        raise argparse.ArgumentTypeError(f"must be above 0 and at most {MAX_HOURS:g}")
    return value


def build_parser() -> argparse.ArgumentParser:
    roles = [r.value for r in Role]
    parser = argparse.ArgumentParser(prog="python -m qlab.api.dev", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="create the key and the development accounts")
    token = commands.add_parser("token", help="print a token for a role's account")
    token.add_argument("role", choices=roles)
    token.add_argument("--hours", type=_hours, default=DEFAULT_HOURS)
    commands.add_parser("accounts", help="list the development accounts")
    for name in ("grant", "revoke"):
        sub = commands.add_parser(name, help=f"{name} a role on a development account")
        sub.add_argument("subject")
        sub.add_argument("role", choices=roles)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        settings = Settings.from_env()
    except StartupError as error:
        print(f"refused: {error}", file=sys.stderr)
        return 2
    if settings.environment is not Environment.LOCAL:
        print("refused: this command runs only with QLAB_ENV=local", file=sys.stderr)
        return 2

    from qlab.database import make_engine

    try:
        engine = make_engine()
    except RuntimeError as error:
        print(f"refused: {error}", file=sys.stderr)
        return 2
    if engine.url.host not in ("localhost", "127.0.0.1", "::1"):
        # Development accounts hold every role; they are never created in a shared database.
        print("refused: the database is not on this machine", file=sys.stderr)
        engine.dispose()
        return 2
    try:
        with Session(engine) as session, session.begin():
            return _run(args, session, settings)
    except (DevCommandRefused, devkey.DevKeyError, ValueError) as error:
        # Expected refusals: the transaction was rolled back. Other errors keep their traceback.
        print(f"refused: {error}", file=sys.stderr)
        return 2
    finally:
        engine.dispose()


def _run(args: argparse.Namespace, session: Session, settings: Settings) -> int:
    command: str = args.command
    if command == "init":
        key = ensure_key(settings)
        del key  # only needed to create or check the file
        created = init_accounts(session)
        print(f"{'role':<16}account")
        for role, account_id in created.items():
            print(f"{role.value:<16}{ids.actor(account_id)}")
    elif command == "token":
        path = settings.dev_key_file
        if path is None:
            raise DevCommandRefused("no development key file is configured")
        print(make_token(session, devkey.load(path), role=Role(args.role), hours=args.hours))
    elif command == "accounts":
        for subject, account_id, held in list_accounts(session):
            print(f"{subject:<28}{ids.actor(account_id)}  {', '.join(r.value for r in held)}")
    else:
        role = Role(args.role)
        if command == "grant":
            account_id, changed = grant_role(session, subject=args.subject, role=role)
            verb = "granted" if changed else "already held"
        else:
            account_id, changed = revoke_role(session, subject=args.subject, role=role)
            verb = "revoked" if changed else "was not held"
        print(f"{role.value} {verb}: {args.subject} ({ids.actor(account_id)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
