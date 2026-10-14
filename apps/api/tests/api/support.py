"""Harness for API tests: the application on the test's own transaction, and accounts with
tokens. Nothing a test does through the API outlives the test.

    def test_something(api: ApiHarness) -> None:
        response = api.client.get("/v1/me", headers=api.headers(Role.STUDENT))

The application's sessions and the test's `session` fixture share one connection, so each sees
what the other wrote (call `session.expire_all()` before re-reading rows the API changed).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from sqlalchemy import Connection
from sqlalchemy.orm import Session, sessionmaker

from qlab.api import ids
from qlab.api.app import create_app
from qlab.api.settings import Environment, Settings
from qlab.identity import service as identity
from qlab.identity.tokens import DEV_AUDIENCE, DEV_ISSUER, TokenVerifier, sign
from qlab.organizations import service as organizations
from qlab.organizations.service import Role

ALL_ROLES: tuple[Role, ...] = tuple(Role)
GRANTED_BY = "system:test"


@dataclass
class ApiHarness:
    client: TestClient
    session: Session
    key: Ed25519PrivateKey
    settings: Settings
    _accounts: dict[frozenset[Role], uuid.UUID] = field(default_factory=dict)

    def account(self, *roles: Role) -> uuid.UUID:
        """An account holding exactly these roles (none: an account without any role). The
        same roles give the same account within a test."""
        wanted = frozenset(roles)
        if wanted not in self._accounts:
            subject = "test-" + ("-".join(sorted(wanted)) or "no-role")
            account = identity.ensure_account(self.session, issuer=DEV_ISSUER, subject=subject)
            for role in wanted:
                organizations.grant(
                    self.session, account_id=account.id, role=role, granted_by=GRANTED_BY
                )
            self.session.flush()
            self._accounts[wanted] = account.id
        return self._accounts[wanted]

    def actor(self, *roles: Role) -> str:
        """The audit actor of `account(*roles)`."""
        return ids.actor(self.account(*roles))

    def token(
        self,
        subject: str,
        *,
        issuer: str = DEV_ISSUER,
        audience: str = DEV_AUDIENCE,
        lifetime: timedelta = timedelta(minutes=5),
        now: datetime | None = None,
        key: Ed25519PrivateKey | None = None,
    ) -> str:
        return sign(
            key or self.key,
            issuer=issuer,
            audience=audience,
            subject=subject,
            lifetime=lifetime,
            now=now or datetime.now(tz=UTC),
        )

    def subject(self, *roles: Role) -> str:
        account = identity.get_account(self.session, self.account(*roles))
        assert account is not None
        return account.subject

    def headers(self, *roles: Role) -> dict[str, str]:
        """Authorization header of `account(*roles)`."""
        return {"Authorization": f"Bearer {self.token(self.subject(*roles))}"}


def make_harness(
    connection: Connection,
    session: Session,
    *,
    settings: Settings | None = None,
    check_renderer: bool = False,
) -> ApiHarness:
    key = Ed25519PrivateKey.generate()
    settings = settings or Settings(environment=Environment.LOCAL, forbid_self_approval=False)
    app = create_app(
        settings,
        verifier=TokenVerifier(
            public_keys=[key.public_key()], issuer=DEV_ISSUER, audience=DEV_AUDIENCE
        ),
        session_factory=sessionmaker(bind=connection, join_transaction_mode="create_savepoint"),
        check_renderer=check_renderer,
    )
    # Server errors come back as 500 responses instead of being raised into the test.
    client = TestClient(app, raise_server_exceptions=False)
    return ApiHarness(client=client, session=session, key=key, settings=settings)
