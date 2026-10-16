"""Bearer token verification (docs/SECURITY.md section 2, D-59).

The API verifies a signed token on every request: signature, expiry, audience and issuer. The
token names an account (`iss` + `sub`) and nothing else; roles are read from the database.

Locally the tokens are signed with a development key generated on this machine
(`qlab.identity.devkey`). Its issuer is `DEV_ISSUER`, and the application refuses to start
with that issuer anywhere but in the local environment (`qlab.api.settings`). With a real
identity provider only the source of the verification keys changes (M1-G slice 9).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

ALGORITHM = "EdDSA"
DEV_ISSUER = "qlab-local-dev"
DEV_AUDIENCE = "qlab-api-local"
MAX_TOKEN_LENGTH = 4096
MAX_LIFETIME = timedelta(hours=24)
MAX_NAME_LENGTH = 200
_REQUIRED_CLAIMS = ("iss", "sub", "aud", "exp", "iat")


class InvalidToken(Exception):
    """The token is not acceptable. The message is for logs, never for the response."""


@dataclass(frozen=True)
class Claims:
    issuer: str
    subject: str
    expires_at: datetime
    # The identity provider organisation the person signed in through, when the token says so
    # (M1-G slice 9: staff roles count only for the staff organisation, where two-step
    # verification is enforced). None for development tokens.
    organization: str | None = None


class TokenVerifier:
    """Verifies EdDSA-signed tokens for one issuer and one audience.

    Several keys may be given (key rotation); a token is accepted when any of them verifies it.
    No clock leeway: a token is invalid from the second it expires.
    """

    def __init__(
        self, *, public_keys: Sequence[Ed25519PublicKey], issuer: str, audience: str
    ) -> None:
        if not public_keys:
            raise ValueError("a token verifier needs at least one key")
        if not issuer or not audience:
            raise ValueError("a token verifier needs an issuer and an audience")
        self._keys = tuple(public_keys)
        self.issuer = issuer
        self.audience = audience

    def verify(self, token: str) -> Claims:
        """Claims of a valid token; otherwise InvalidToken.

        Refused: anything not signed with EdDSA by one of the keys (including unsigned tokens);
        a missing `iss`, `sub`, `aud`, `exp` or `iat`; another issuer or audience; an expired
        token; one issued in the future; a lifetime over 24 hours; a subject or issuer that
        is blank, padded, longer than 200 characters or contains a non-printable character; a
        token longer than 4096 characters.
        """
        if not token or len(token) > MAX_TOKEN_LENGTH:
            raise InvalidToken("token is empty or too long")
        error: Exception | None = None
        for key in self._keys:
            try:
                payload = jwt.decode(
                    token,
                    key,
                    algorithms=[ALGORITHM],
                    audience=self.audience,
                    issuer=self.issuer,
                    leeway=0,
                    options={"require": list(_REQUIRED_CLAIMS), "verify_iat": True},
                )
            except jwt.InvalidSignatureError as caught:
                error = caught
                continue
            except jwt.PyJWTError as caught:
                raise InvalidToken(type(caught).__name__) from None
            return self._claims(payload)
        raise InvalidToken(type(error).__name__ if error else "no key")

    @staticmethod
    def _claims(payload: dict[str, object]) -> Claims:
        subject, issuer = payload.get("sub"), payload.get("iss")
        expires, issued = payload.get("exp"), payload.get("iat")
        for name, value in (("subject", subject), ("issuer", issuer)):
            # Printable, unpadded, bounded: what the account table can hold and look up.
            if (
                not isinstance(value, str)
                or not value
                or value != value.strip()
                or len(value) > MAX_NAME_LENGTH
                or not value.isprintable()
            ):
                raise InvalidToken(f"unusable {name}")
        assert isinstance(subject, str) and isinstance(issuer, str)  # noqa: S101 - checked above
        if isinstance(expires, bool) or not isinstance(expires, int | float):
            raise InvalidToken("exp is not a number")
        if isinstance(issued, bool) or not isinstance(issued, int | float):
            raise InvalidToken("iat is not a number")
        if expires - issued > MAX_LIFETIME.total_seconds():
            raise InvalidToken("lifetime too long")
        return Claims(
            issuer=issuer, subject=subject, expires_at=datetime.fromtimestamp(expires, tz=UTC)
        )


def sign(
    private_key: Ed25519PrivateKey,
    *,
    issuer: str,
    audience: str,
    subject: str,
    lifetime: timedelta,
    now: datetime | None = None,
) -> str:
    """A signed token. Used by the local development command and by tests; the application
    itself never signs tokens."""
    issued = now or datetime.now(tz=UTC)
    payload = {
        "iss": issuer,
        "aud": audience,
        "sub": subject,
        "iat": int(issued.timestamp()),
        "exp": int((issued + lifetime).timestamp()),
    }
    return jwt.encode(payload, private_key, algorithm=ALGORITHM)
