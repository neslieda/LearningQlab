"""Owner command: `python -m qlab.api.admin <command>` (M1-G slice 9, M1G-9-ACILIS.md 3.3).

`invite --role <role> --base-url <url> [--expires-in-days N] [--max-uses N]` creates an invite
and prints its link and expiry.

This is how the first `platform_admin` comes to exist. It runs from the owner's computer with
`QLAB_DATABASE_URL`; the audit actor is `cli:owner`. The link contains the code, which is shown
only here: keep it private. `--base-url` must be https (http only for localhost).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from qlab.api import invites_view
from qlab.organizations.service import INVITABLE_ROLES, InviteRoleForbidden, Role

_LOCAL_HOSTS = ("localhost", "127.0.0.1")


def _base_url(text: str) -> str:
    parsed = urlparse(text)
    secure = parsed.scheme == "https" and bool(parsed.hostname)
    local = parsed.scheme == "http" and parsed.hostname in _LOCAL_HOSTS
    if not (secure or local) or parsed.query or parsed.fragment or parsed.username:
        raise argparse.ArgumentTypeError("must be an https address (http only for localhost)")
    return text.rstrip("/")


def _bounded(low: int, high: int) -> Callable[[str], int]:
    def parse(text: str) -> int:
        try:
            value = int(text)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{text!r} is not a number") from None
        if not low <= value <= high:
            raise argparse.ArgumentTypeError(f"must be between {low} and {high}")
        return value

    return parse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m qlab.api.admin", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    invite = commands.add_parser("invite", help="create an invite link")
    invite.add_argument("--role", required=True, choices=sorted(r.value for r in INVITABLE_ROLES))
    invite.add_argument("--base-url", required=True, type=_base_url)
    invite.add_argument("--expires-in-days", type=_bounded(1, 30), default=7)
    invite.add_argument("--max-uses", type=_bounded(1, 200), default=1)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    from qlab.database import make_engine

    try:
        engine = make_engine()
    except RuntimeError as error:
        print(f"refused: {error}", file=sys.stderr)
        return 2
    try:
        with Session(engine) as session, session.begin():
            created = invites_view.create_as(
                session,
                actor=invites_view.CLI_ACTOR,
                roles=frozenset({Role.PLATFORM_ADMIN}),
                role=args.role,
                expires_in_days=args.expires_in_days,
                max_uses=args.max_uses,
            )
    except (InviteRoleForbidden, ValueError) as error:
        print(f"refused: {error}", file=sys.stderr)
        return 2
    finally:
        engine.dispose()
    print(f"{args.base_url}/invite/{created.code}")
    print(
        f"role: {created.role}; uses: {created.max_uses}; expires: {created.expires_at.isoformat()}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
