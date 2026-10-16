"""Token verification against an OpenID Connect identity provider (M1-G slice 9, D-62).

The verification keys come from the provider's JWKS, found through
`<issuer>/.well-known/openid-configuration`. They are kept in memory; a token with an unknown
`kid` makes the verifier fetch the key set again, at most once a minute. Allowed algorithms:
RS256, ES256, EdDSA. Never `none`, never an HMAC algorithm. Checked: signature, `iss` (exact),
`aud` (contains the configured audience; it may be a list), `azp` (the client id), `exp`, `iat`,
a lifetime of at most 24 hours, and the same `sub` / `iss` rules as for development tokens.

No network access happens at import time. The network is reached through a `Fetch` function
(the default one has a 5 second timeout, a size limit and follows no redirects), so tests give
it a fake.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

import jwt

from qlab.identity.tokens import (
    _REQUIRED_CLAIMS,
    MAX_TOKEN_LENGTH,
    Claims,
    InvalidToken,
    TokenVerifier,
)

ALGORITHMS = ("RS256", "ES256", "EdDSA")
FETCH_TIMEOUT_SECONDS = 5.0
MAX_RESPONSE_BYTES = 1024 * 1024
REFETCH_INTERVAL_SECONDS = 60.0
_KEY_TYPES = ("RSA", "EC", "OKP")  # never "oct": no shared secrets
_LOCAL_HOSTS = ("localhost", "127.0.0.1")

Fetch = Callable[[str], bytes]


class OidcUnavailable(Exception):
    """The identity provider's discovery document or key set could not be used."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _checked_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme == "https" and parsed.hostname:
        return
    if parsed.scheme == "http" and parsed.hostname in _LOCAL_HOSTS:
        return
    raise OidcUnavailable("identity provider addresses must be https")


def http_fetch(url: str) -> bytes:
    """GET `url`: https only (http for localhost), 5 second timeout, at most 1 MiB, no
    redirects. OidcUnavailable on any failure."""
    _checked_url(url)
    opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(url, headers={"Accept": "application/json"})  # noqa: S310
    try:
        with opener.open(request, timeout=FETCH_TIMEOUT_SECONDS) as response:  # noqa: S310
            if response.status != 200:
                raise OidcUnavailable(f"status {response.status}")
            body: bytes = response.read(MAX_RESPONSE_BYTES + 1)
    except (OSError, urllib.error.URLError, ValueError) as error:
        raise OidcUnavailable(type(error).__name__) from None
    if len(body) > MAX_RESPONSE_BYTES:
        raise OidcUnavailable("response too large")
    return body


def _json_object(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except ValueError:
        raise OidcUnavailable("not JSON") from None
    if not isinstance(value, dict):
        raise OidcUnavailable("not a JSON object")
    return value


class OidcTokenVerifier(TokenVerifier):
    """Verifies tokens of one identity provider for one audience and one client."""

    def __init__(  # noqa: PLR0913 - three coordinates and two seams for tests
        self,
        *,
        issuer: str,
        audience: str,
        client_id: str,
        fetch: Fetch = http_fetch,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        # The parent's fixed key list does not apply: keys come from the key set.
        if not issuer or not audience or not client_id:
            raise ValueError("an OIDC verifier needs an issuer, an audience and a client id")
        self.issuer = issuer
        self.audience = audience
        self.client_id = client_id
        self._fetch = fetch
        self._clock = clock
        self._lock = threading.Lock()
        self._jwks: dict[str, jwt.PyJWK] = {}
        self._declared: dict[str, str] = {}  # the `alg` a key says it is for, when it says
        self._last_fetch = float("-inf")
        discovery = _json_object(fetch(f"{issuer.rstrip('/')}/.well-known/openid-configuration"))
        if discovery.get("issuer") != issuer:
            raise OidcUnavailable("the discovery document names another issuer")
        jwks_uri = discovery.get("jwks_uri")
        if not isinstance(jwks_uri, str):
            raise OidcUnavailable("the discovery document has no jwks_uri")
        _checked_url(jwks_uri)
        self._jwks_uri = jwks_uri
        self._refresh()
        if not self._jwks:
            raise OidcUnavailable("the key set has no usable key")

    def _refresh(self) -> None:
        """Fetch the key set. A failure keeps the keys already known."""
        self._last_fetch = self._clock()
        document = _json_object(self._fetch(self._jwks_uri))
        entries = document.get("keys")
        if not isinstance(entries, list):
            raise OidcUnavailable("the key set has no keys")
        keys: dict[str, jwt.PyJWK] = {}
        declared: dict[str, str] = {}
        for entry in entries:
            if (
                not isinstance(entry, dict)
                or entry.get("use") == "enc"
                or entry.get("kty") not in _KEY_TYPES
            ):
                continue
            kid = entry.get("kid")
            if not isinstance(kid, str) or not kid:
                continue
            try:
                keys[kid] = jwt.PyJWK(entry)
                if isinstance(entry.get("alg"), str):
                    declared[kid] = entry["alg"]
            except jwt.PyJWTError, ValueError, KeyError:
                continue  # a key this library cannot use is no key
        self._jwks = keys
        self._declared = declared

    def _key_for(self, kid: str) -> jwt.PyJWK:
        key = self._jwks.get(kid)
        if key is not None:
            return key
        with self._lock:
            key = self._jwks.get(kid)
            if key is None and self._clock() - self._last_fetch >= REFETCH_INTERVAL_SECONDS:
                try:
                    self._refresh()
                except OidcUnavailable as error:
                    raise InvalidToken(f"key set unavailable: {error}") from None
                key = self._jwks.get(kid)
        if key is None:
            raise InvalidToken("unknown key id")
        return key

    def verify(self, token: str) -> Claims:
        if not token or len(token) > MAX_TOKEN_LENGTH:
            raise InvalidToken("token is empty or too long")
        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError:
            raise InvalidToken("unreadable header") from None
        algorithm, kid = header.get("alg"), header.get("kid")
        if not isinstance(algorithm, str) or algorithm not in ALGORITHMS:
            raise InvalidToken("algorithm not allowed")
        if not isinstance(kid, str) or not kid:
            raise InvalidToken("no key id")
        key = self._key_for(kid)
        declared = self._declared.get(kid)
        if declared is not None and declared != algorithm:
            raise InvalidToken("key does not fit the algorithm")
        try:
            payload = jwt.decode(
                token,
                key.key,
                algorithms=[algorithm],
                audience=self.audience,
                issuer=self.issuer,
                leeway=0,
                options={"require": list(_REQUIRED_CLAIMS), "verify_iat": True},
            )
        except jwt.PyJWTError as caught:
            raise InvalidToken(type(caught).__name__) from None
        if payload.get("azp") != self.client_id:
            raise InvalidToken("wrong authorised party")
        return self._claims(payload)
