"""The JWKS-backed token verifier and the settings that build it (M1-G slice 9,
docs/slices/M1G-9-ACILIS.md 3.1 and 6.1). The identity provider is a fake `fetch` function: no
network is used."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from qlab.api.settings import Environment, Settings, StartupError, build_verifier
from qlab.identity.oidc import OidcTokenVerifier, OidcUnavailable, http_fetch
from qlab.identity.tokens import ORGANIZATION_CLAIM, InvalidToken

ISSUER = "https://idp.example.invalid"
AUDIENCE = "project-1"
CLIENT = "client-1"
STAFF_ORG = "org-staff"
DISCOVERY = f"{ISSUER}/.well-known/openid-configuration"
JWKS_URI = f"{ISSUER}/oauth/v2/keys"


def jwk(public_key: Any, kid: str, algorithm: str, **extra: Any) -> dict[str, Any]:
    cls: Any = {
        "RS256": jwt.algorithms.RSAAlgorithm,
        "ES256": jwt.algorithms.ECAlgorithm,
        "EdDSA": jwt.algorithms.OKPAlgorithm,
    }[algorithm]
    data: dict[str, Any] = json.loads(cls.to_jwk(public_key))
    return {**data, "kid": kid, "use": "sig", **extra}


class FakeProvider:
    def __init__(self) -> None:
        self.keys: list[dict[str, Any]] = []
        self.calls: list[str] = []
        self.down = False
        self.issuer = ISSUER
        self.jwks_uri = JWKS_URI

    def fetch(self, url: str) -> bytes:
        self.calls.append(url)
        if self.down:
            raise OidcUnavailable("down")
        if url == DISCOVERY:
            return json.dumps({"issuer": self.issuer, "jwks_uri": self.jwks_uri}).encode()
        if url == self.jwks_uri:
            return json.dumps({"keys": self.keys}).encode()
        raise OidcUnavailable("404")


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


RSA = rsa.generate_private_key(public_exponent=65537, key_size=2048)
EC = ec.generate_private_key(ec.SECP256R1())
ED = Ed25519PrivateKey.generate()


@pytest.fixture
def provider() -> FakeProvider:
    fake = FakeProvider()
    fake.keys = [
        jwk(RSA.public_key(), "rsa-1", "RS256"),
        jwk(EC.public_key(), "ec-1", "ES256"),
        jwk(ED.public_key(), "ed-1", "EdDSA"),
    ]
    return fake


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def verifier(provider: FakeProvider, clock: Clock) -> OidcTokenVerifier:
    return OidcTokenVerifier(
        issuer=ISSUER, audience=AUDIENCE, client_id=CLIENT, fetch=provider.fetch, clock=clock
    )


def claims(**changes: Any) -> dict[str, Any]:
    issued = int(datetime.now(tz=UTC).timestamp())
    base: dict[str, Any] = {
        "iss": ISSUER,
        "aud": [AUDIENCE, "other"],
        "azp": CLIENT,
        "sub": "user-1",
        "iat": issued,
        "exp": issued + 300,
        ORGANIZATION_CLAIM: STAFF_ORG,
    }
    base.update(changes)
    return {k: v for k, v in base.items() if v is not None}


def make(
    payload: dict[str, Any] | None = None,
    *,
    key: Any = RSA,
    algorithm: str = "RS256",
    kid: str | None = "rsa-1",
) -> str:
    headers = {"kid": kid} if kid else {}
    return jwt.encode(payload or claims(), key, algorithm=algorithm, headers=headers)


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def refused(verifier: OidcTokenVerifier, token: str) -> None:
    with pytest.raises(InvalidToken):
        verifier.verify(token)


@pytest.mark.parametrize(
    ("key", "algorithm", "kid"),
    [(RSA, "RS256", "rsa-1"), (EC, "ES256", "ec-1"), (ED, "EdDSA", "ed-1")],
)
def test_a_valid_token(verifier: OidcTokenVerifier, key: Any, algorithm: str, kid: str) -> None:
    result = verifier.verify(make(key=key, algorithm=algorithm, kid=kid))
    assert (result.issuer, result.subject, result.organization) == (ISSUER, "user-1", STAFF_ORG)


def test_the_organization_is_none_when_the_token_has_none(verifier: OidcTokenVerifier) -> None:
    assert verifier.verify(make(claims(**{ORGANIZATION_CLAIM: None}))).organization is None
    assert verifier.verify(make(claims(**{ORGANIZATION_CLAIM: 7}))).organization is None


def test_audience_may_be_a_string(verifier: OidcTokenVerifier) -> None:
    assert verifier.verify(make(claims(aud=AUDIENCE))).subject == "user-1"


@pytest.mark.parametrize(
    "changes",
    [
        {"iss": "https://other.example.invalid"},
        {"iss": ISSUER + "/"},
        {"aud": "another-project"},
        {"aud": ["a", "b"]},
        {"aud": None},
        {"azp": "another-client"},
        {"azp": None},
        {"exp": 1},
        {"iat": 4_000_000_000, "exp": 4_000_000_300},
        {"sub": None},
        {"sub": "  padded "},
    ],
)
def test_refused_claims(verifier: OidcTokenVerifier, changes: dict[str, Any]) -> None:
    refused(verifier, make(claims(**changes)))


def test_a_lifetime_over_24_hours_is_refused(verifier: OidcTokenVerifier) -> None:
    issued = int(datetime.now(tz=UTC).timestamp())
    refused(verifier, make(claims(iat=issued, exp=issued + 24 * 3600 + 1)))
    assert verifier.verify(make(claims(iat=issued, exp=issued + 24 * 3600)))


def test_alg_none_and_hmac_are_refused(verifier: OidcTokenVerifier) -> None:
    head = b64(json.dumps({"alg": "none", "kid": "rsa-1"}).encode())
    refused(verifier, f"{head}.{b64(json.dumps(claims()).encode())}.")
    # HS256 signed with the public key bytes as the secret (the classic confusion attack).
    secret = b"public key bytes"
    head = b64(json.dumps({"alg": "HS256", "kid": "rsa-1"}).encode())
    body = b64(json.dumps(claims()).encode())
    mac = hmac.new(secret, f"{head}.{body}".encode(), hashlib.sha256).digest()
    refused(verifier, f"{head}.{body}.{b64(mac)}")


def test_a_signature_from_another_key_is_refused(verifier: OidcTokenVerifier) -> None:
    refused(verifier, make(key=rsa.generate_private_key(public_exponent=65537, key_size=2048)))


def test_the_algorithm_must_fit_the_key(verifier: OidcTokenVerifier) -> None:
    refused(verifier, make(key=ED, algorithm="EdDSA", kid="rsa-1"))


def test_a_key_that_declares_another_algorithm_is_refused(
    provider: FakeProvider, clock: Clock
) -> None:
    provider.keys = [jwk(RSA.public_key(), "rsa-1", "RS256", alg="RS384")]
    verifier = OidcTokenVerifier(
        issuer=ISSUER, audience=AUDIENCE, client_id=CLIENT, fetch=provider.fetch, clock=clock
    )
    refused(verifier, make())


def test_no_kid_is_refused(verifier: OidcTokenVerifier) -> None:
    refused(verifier, make(kid=None))


def test_garbage_is_refused(verifier: OidcTokenVerifier) -> None:
    for token in ("", "x", "a.b.c", "x" * 5000):
        refused(verifier, token)


def test_unknown_kid_refetches_once_a_minute(
    verifier: OidcTokenVerifier, provider: FakeProvider, clock: Clock
) -> None:
    new_key = Ed25519PrivateKey.generate()
    token = make(key=new_key, algorithm="EdDSA", kid="ed-2")
    start = len(provider.calls)
    clock.now += 30
    refused(verifier, token)  # too soon since the first fetch: no fetch
    assert len(provider.calls) == start
    provider.keys.append(jwk(new_key.public_key(), "ed-2", "EdDSA"))
    clock.now += 31
    assert verifier.verify(token).subject == "user-1"  # fetched and found
    assert len(provider.calls) == start + 1
    refused(verifier, make(key=new_key, algorithm="EdDSA", kid="ed-3"))
    refused(verifier, make(key=new_key, algorithm="EdDSA", kid="ed-4"))
    assert len(provider.calls) == start + 1  # the minute has not passed again
    clock.now += 61
    refused(verifier, make(key=new_key, algorithm="EdDSA", kid="ed-5"))
    assert len(provider.calls) == start + 2


def test_key_rotation(verifier: OidcTokenVerifier, provider: FakeProvider, clock: Clock) -> None:
    old = make()
    replacement = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    provider.keys = [jwk(replacement.public_key(), "rsa-2", "RS256")]
    clock.now += 61
    assert verifier.verify(make(key=replacement, kid="rsa-2")).subject == "user-1"
    refused(verifier, old)  # the provider no longer lists the old key


def test_a_failing_refetch_keeps_the_known_keys(
    verifier: OidcTokenVerifier, provider: FakeProvider, clock: Clock
) -> None:
    provider.down = True
    clock.now += 61
    refused(verifier, make(kid="nope"))
    assert verifier.verify(make()).subject == "user-1"


def test_start_fails_when_the_provider_is_unreachable(provider: FakeProvider) -> None:
    provider.down = True
    with pytest.raises(OidcUnavailable):
        OidcTokenVerifier(issuer=ISSUER, audience=AUDIENCE, client_id=CLIENT, fetch=provider.fetch)


def test_start_fails_for_another_issuer_in_the_discovery_document(provider: FakeProvider) -> None:
    provider.issuer = "https://other.example.invalid"
    with pytest.raises(OidcUnavailable):
        OidcTokenVerifier(issuer=ISSUER, audience=AUDIENCE, client_id=CLIENT, fetch=provider.fetch)


def test_start_fails_without_usable_keys(provider: FakeProvider) -> None:
    provider.keys = [{"kty": "oct", "kid": "x", "k": "AAAA"}]
    with pytest.raises(OidcUnavailable):
        OidcTokenVerifier(issuer=ISSUER, audience=AUDIENCE, client_id=CLIENT, fetch=provider.fetch)


def test_a_little_clock_difference_on_iat_is_tolerated_but_exp_is_strict(
    verifier: OidcTokenVerifier,
) -> None:
    now = int(datetime.now(tz=UTC).timestamp())
    assert verifier.verify(make(claims(iat=now + 5, exp=now + 300))).subject == "user-1"
    refused(verifier, make(claims(iat=now + 60, exp=now + 300)))
    refused(verifier, make(claims(iat=now - 100, exp=now - 3)))  # expired 3 seconds ago


def test_keys_are_fetched_again_when_an_hour_old(
    verifier: OidcTokenVerifier, provider: FakeProvider, clock: Clock
) -> None:
    start = len(provider.calls)
    clock.now += 3599
    verifier.verify(make())
    assert len(provider.calls) == start  # a known key, not yet an hour: no fetch
    replacement = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    provider.keys = [jwk(replacement.public_key(), "rsa-2", "RS256")]
    clock.now += 2
    refused(verifier, make())  # the key was withdrawn: the hourly refresh dropped it
    assert len(provider.calls) == start + 1
    assert verifier.verify(make(key=replacement, kid="rsa-2")).subject == "user-1"
    assert len(provider.calls) == start + 1


def test_an_hourly_refresh_that_fails_keeps_the_known_keys(
    verifier: OidcTokenVerifier, provider: FakeProvider, clock: Clock
) -> None:
    provider.down = True
    clock.now += 7200
    assert verifier.verify(make()).subject == "user-1"
    start = len(provider.calls)
    assert verifier.verify(make()).subject == "user-1"
    assert len(provider.calls) == start  # not retried on every request


def test_start_fails_when_the_key_set_is_on_another_host(provider: FakeProvider) -> None:
    provider.jwks_uri = "https://keys.elsewhere.invalid/keys"
    with pytest.raises(OidcUnavailable, match="host"):
        OidcTokenVerifier(issuer=ISSUER, audience=AUDIENCE, client_id=CLIENT, fetch=provider.fetch)


# --- settings ------------------------------------------------------------------------------------

OIDC_ENV = {
    "QLAB_OIDC_ISSUER": ISSUER,
    "QLAB_OIDC_AUDIENCE": AUDIENCE,
    "QLAB_OIDC_CLIENT_ID": CLIENT,
    "QLAB_OIDC_STAFF_ORG_ID": STAFF_ORG,
}


@pytest.mark.parametrize("env", ["staging", "production"])
def test_settings_read_the_provider_outside_local(env: str) -> None:
    settings = Settings.from_env({"QLAB_ENV": env, **OIDC_ENV})
    assert settings.oidc_issuer == ISSUER
    assert settings.oidc_audience == AUDIENCE
    assert settings.oidc_client_id == CLIENT
    assert settings.staff_organization == STAFF_ORG
    assert settings.forbid_self_approval is True


@pytest.mark.parametrize("env", ["staging", "production"])
@pytest.mark.parametrize("missing", sorted(OIDC_ENV))
def test_a_missing_provider_setting_outside_local_stops_start_up(env: str, missing: str) -> None:
    environ = {"QLAB_ENV": env, **OIDC_ENV}
    del environ[missing]
    with pytest.raises(StartupError, match=missing):
        Settings.from_env(environ)
    environ[missing] = "  "
    with pytest.raises(StartupError, match=missing):
        Settings.from_env(environ)


@pytest.mark.parametrize("env", ["staging", "production"])
def test_an_http_issuer_is_refused_outside_local(env: str) -> None:
    environ = {"QLAB_ENV": env, **OIDC_ENV, "QLAB_OIDC_ISSUER": "http://idp.example.invalid"}
    with pytest.raises(StartupError, match="https"):
        Settings.from_env(environ)
    settings = Settings(
        Environment.PRODUCTION,
        True,
        staff_organization=STAFF_ORG,
        oidc_issuer="http://idp.example.invalid",
        oidc_audience=AUDIENCE,
        oidc_client_id=CLIENT,
    )
    with pytest.raises(StartupError, match="https"):
        build_verifier(settings)


def test_local_needs_no_provider_and_has_no_staff_organization() -> None:
    settings = Settings.from_env({"QLAB_ENV": "local"})
    assert settings.staff_organization is None
    assert settings.oidc_issuer is None


def test_the_self_approval_rule_still_applies_outside_local() -> None:
    with pytest.raises(StartupError):
        Settings.from_env(
            {"QLAB_ENV": "production", "QLAB_FORBID_SELF_APPROVAL": "false", **OIDC_ENV}
        )


def test_build_verifier_with_an_unreachable_provider_is_a_start_up_error() -> None:
    # A name under `.invalid` never resolves, so this fails at once without leaving the machine.
    settings = Settings(
        Environment.PRODUCTION,
        True,
        staff_organization=STAFF_ORG,
        oidc_issuer=ISSUER,
        oidc_audience=AUDIENCE,
        oidc_client_id=CLIENT,
    )
    with pytest.raises(StartupError):
        build_verifier(settings)


@pytest.mark.parametrize(
    "url", ["http://idp.example.com/x", "ftp://localhost/x", "file:///etc/passwd"]
)
def test_the_default_fetch_refuses_insecure_addresses(url: str) -> None:
    with pytest.raises(OidcUnavailable):
        http_fetch(url)
