"""Bearer token verification (docs/SECURITY.md section 2; docs/slices/M1G-5-SOZLESME.md 3.1):
`TokenVerifier` on its own (no database), then the HTTP layer (marked `db`).

Tokens are EdDSA JWTs with `iss`, `sub`, `aud`, `exp`, `iat`; no clock leeway; lifetime at most
24 hours; at most 4096 characters. Anything else is `InvalidToken`, and over HTTP always 401.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from hypothesis import given, settings
from hypothesis import strategies as st

from qlab.identity.tokens import (
    ALGORITHM,
    DEV_AUDIENCE,
    DEV_ISSUER,
    MAX_LIFETIME,
    MAX_NAME_LENGTH,
    MAX_TOKEN_LENGTH,
    Claims,
    InvalidToken,
    TokenVerifier,
    sign,
)
from qlab.organizations.service import Role
from tests.api.support import ApiHarness

ISSUER = "https://issuer.example.invalid"
AUDIENCE = "synthetic-audience"
KEY = Ed25519PrivateKey.generate()
OTHER_KEY = Ed25519PrivateKey.generate()
VERIFIER = TokenVerifier(public_keys=[KEY.public_key()], issuer=ISSUER, audience=AUDIENCE)


def now() -> datetime:
    return datetime.now(tz=UTC).replace(microsecond=0)


def payload(**changes: Any) -> dict[str, Any]:
    issued = int(now().timestamp())
    base: dict[str, Any] = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "user-1",
        "iat": issued,
        "exp": issued + 300,
    }
    base.update(changes)
    return {k: v for k, v in base.items() if v is not None}


def make(claims: dict[str, Any] | None = None, key: Ed25519PrivateKey = KEY) -> str:
    return jwt.encode(payload() if claims is None else claims, key, algorithm=ALGORITHM)


def refused(token: str, verifier: TokenVerifier = VERIFIER) -> None:
    with pytest.raises(InvalidToken):
        verifier.verify(token)


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def forged(header: dict[str, Any], claims: dict[str, Any], signature: bytes = b"") -> str:
    return ".".join(
        [b64(json.dumps(header).encode()), b64(json.dumps(claims).encode()), b64(signature)]
    )


# --- the verifier -------------------------------------------------------------------------------


def test_a_valid_token_yields_its_claims() -> None:
    claims = VERIFIER.verify(make(payload(sub="abc", exp=int(now().timestamp()) + 600)))
    assert isinstance(claims, Claims)
    assert (claims.issuer, claims.subject) == (ISSUER, "abc")
    assert claims.expires_at > datetime.now(tz=UTC)


def test_sign_and_verify_round_trip() -> None:
    token = sign(KEY, issuer=ISSUER, audience=AUDIENCE, subject="s", lifetime=timedelta(hours=1))
    assert VERIFIER.verify(token).subject == "s"


def test_the_application_does_not_depend_on_the_defaults_of_this_file() -> None:
    assert (ALGORITHM, DEV_ISSUER, DEV_AUDIENCE) == ("EdDSA", "qlab-local-dev", "qlab-api-local")
    assert MAX_TOKEN_LENGTH == 4096
    assert timedelta(hours=24) == MAX_LIFETIME


@pytest.mark.parametrize("seconds", [-1, -60, -3600, -86400])
def test_an_expired_token_is_refused(seconds: int) -> None:
    issued = int(now().timestamp()) - 7200
    refused(make(payload(iat=issued, exp=int(now().timestamp()) + seconds)))


def test_a_token_that_expires_exactly_now_is_refused() -> None:
    """No leeway: invalid from the second it expires."""
    current = int(datetime.now(tz=UTC).timestamp())
    token = make(payload(iat=current - 10, exp=current))
    refused(token)


def test_a_token_about_to_expire_is_still_valid() -> None:
    issued = int(now().timestamp())
    assert VERIFIER.verify(make(payload(iat=issued - 60, exp=issued + 30))).subject == "user-1"


@pytest.mark.parametrize("seconds", [5, 60, 3600])
def test_a_token_issued_in_the_future_is_refused(seconds: int) -> None:
    issued = int(now().timestamp()) + seconds
    refused(make(payload(iat=issued, exp=issued + 300)))


def test_wrong_audience_is_refused() -> None:
    refused(make(payload(aud="another-audience")))
    refused(make(payload(aud=AUDIENCE + "x")))
    refused(make(payload(aud=AUDIENCE.upper())))
    refused(make(payload(aud=[])))


def test_an_audience_list_is_accepted_only_if_it_names_ours() -> None:
    assert VERIFIER.verify(make(payload(aud=[AUDIENCE, "other"]))).subject == "user-1"
    refused(make(payload(aud=["other", "another"])))


def test_wrong_issuer_is_refused() -> None:
    refused(make(payload(iss="https://elsewhere.invalid")))
    refused(make(payload(iss=ISSUER + "/")))
    refused(make(payload(iss=ISSUER.upper())))
    refused(make(payload(iss="")))


def test_wrong_key_is_refused() -> None:
    refused(make(key=OTHER_KEY))


def test_tampered_payload_is_refused() -> None:
    header, claims, signature = make().split(".")
    evil = b64(json.dumps(payload(sub="admin")).encode())
    refused(f"{header}.{evil}.{signature}")


def test_tampered_header_is_refused() -> None:
    header, claims, signature = make().split(".")
    other = b64(json.dumps({"alg": "EdDSA", "typ": "JWT", "x": 1}).encode())
    refused(f"{other}.{claims}.{signature}")


def test_a_tampered_signature_is_refused() -> None:
    header, claims, signature = make().split(".")
    middle = len(signature) // 2
    flipped = (
        signature[:middle] + ("A" if signature[middle] != "A" else "B") + signature[middle + 1 :]
    )
    refused(f"{header}.{claims}.{flipped}")
    refused(f"{header}.{claims}.")
    refused(f"{header}.{claims}.{signature[:-10]}")
    refused(f"{header}.{claims}.{signature}{signature}")


def test_a_token_signed_for_one_payload_does_not_verify_another() -> None:
    first, second = make(payload(sub="a")), make(payload(sub="b"))
    h1, p1, s1 = first.split(".")
    h2, p2, s2 = second.split(".")
    refused(f"{h1}.{p2}.{s1}")


def test_alg_none_is_refused() -> None:
    claims = payload()
    refused(forged({"alg": "none", "typ": "JWT"}, claims))
    refused(forged({"alg": "None", "typ": "JWT"}, claims))
    refused(forged({"alg": "NONE", "typ": "JWT"}, claims))
    refused(forged({"alg": "none"}, claims, signature=b"x" * 64))
    refused(forged({"alg": "EdDSA"}, claims))  # right algorithm, no signature


def test_algorithm_confusion_hs256_with_the_public_key_is_refused() -> None:
    public = KEY.public_key()
    raw = public.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    pem = public.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    for secret in (raw, pem, b64(raw).encode(), raw.hex().encode()):
        for alg, digest in (
            ("HS256", hashlib.sha256),
            ("HS384", hashlib.sha384),
            ("HS512", hashlib.sha512),
        ):
            header = json.dumps({"alg": alg, "typ": "JWT"}).encode()
            body = json.dumps(payload()).encode()
            signing_input = f"{b64(header)}.{b64(body)}".encode()
            signature = hmac.new(secret, signing_input, digest).digest()
            refused(f"{signing_input.decode()}.{b64(signature)}")


@pytest.mark.parametrize("alg", ["RS256", "ES256", "PS256", "HS256", "EdDSA2", "", "ed25519"])
def test_other_declared_algorithms_are_refused(alg: str) -> None:
    refused(forged({"alg": alg, "typ": "JWT"}, payload(), signature=b"\x00" * 64))


def test_a_token_whose_header_claims_a_different_key_still_needs_our_signature() -> None:
    token = jwt.encode(
        payload(),
        OTHER_KEY,
        algorithm=ALGORITHM,
        headers={"kid": "ours", "jku": "http://evil.invalid"},
    )
    refused(token)


@pytest.mark.parametrize("missing", ["iss", "sub", "aud", "exp", "iat"])
def test_each_required_claim_is_required(missing: str) -> None:
    refused(make(payload(**{missing: None})))


@pytest.mark.parametrize("claim", ["exp", "iat"])
@pytest.mark.parametrize("bad", ["soon", "1700000000", None, [], {}, True])
def test_time_claims_must_be_numbers(claim: str, bad: Any) -> None:
    claims = payload()
    claims[claim] = bad
    refused(make(claims))


def test_lifetime_over_24_hours_is_refused() -> None:
    issued = int(now().timestamp())
    refused(make(payload(iat=issued, exp=issued + 86401)))
    refused(make(payload(iat=issued, exp=issued + 7 * 86400)))
    refused(make(payload(iat=issued - 10, exp=issued + 86400)))  # 24 h + 10 s


def test_lifetime_of_exactly_24_hours_is_accepted() -> None:
    issued = int(now().timestamp())
    assert VERIFIER.verify(make(payload(iat=issued, exp=issued + 86400))).subject == "user-1"
    assert VERIFIER.verify(make(payload(iat=issued, exp=issued + 86399))).subject == "user-1"


def test_sign_with_a_long_lifetime_is_refused_by_the_verifier() -> None:
    token = sign(KEY, issuer=ISSUER, audience=AUDIENCE, subject="s", lifetime=timedelta(hours=25))
    refused(token)


@pytest.mark.parametrize("subject", ["", " ", " a", "a ", "\t", "a\n", " ", "  \t "])
def test_a_blank_or_padded_subject_is_refused(subject: str) -> None:
    refused(make(payload(sub=subject)))


@pytest.mark.parametrize("subject", [123, 1.5, True, ["a"], {"a": 1}, None])
def test_a_subject_that_is_not_text_is_refused(subject: Any) -> None:
    claims = payload()
    claims["sub"] = subject
    refused(make(claims))


def test_a_subject_with_inner_spaces_or_unicode_is_kept_verbatim() -> None:
    for subject in ("a b", "user|1", "ünïcode", "x" * 50):
        assert VERIFIER.verify(make(payload(sub=subject))).subject == subject


def _token_with_subject_length(length: int) -> str:
    """A token padded to size with an extra claim (subjects are limited to 200 characters)."""
    return make(payload(pad="a" * length))


def test_token_length_limit_is_4096_characters() -> None:
    low, high = 0, 6000  # largest subject whose token still fits
    while low < high:
        middle = (low + high + 1) // 2
        if len(_token_with_subject_length(middle)) <= MAX_TOKEN_LENGTH:
            low = middle
        else:
            high = middle - 1
    fits = _token_with_subject_length(low)
    assert len(fits) <= MAX_TOKEN_LENGTH
    assert VERIFIER.verify(fits).subject == "user-1"
    for extra in range(1, 6):
        over = _token_with_subject_length(low + 3 * extra)
        assert len(over) > MAX_TOKEN_LENGTH
        refused(over)
    refused(_token_with_subject_length(10_000))


def test_a_valid_token_followed_by_padding_is_not_a_longer_valid_token() -> None:
    token = make()
    refused(token + "A" * MAX_TOKEN_LENGTH)
    refused(token + ".extra")
    refused(token + " ")
    refused(" " + token)


@pytest.mark.parametrize(
    "token", ["", " ", "a", "a.b", "a.b.c", "..", "...", "a.b.c.d", "\x00", "ey", "null"]
)
def test_structurally_invalid_tokens_are_refused(token: str) -> None:
    refused(token)


def test_a_jwe_or_nested_token_is_refused() -> None:
    inner = make()
    refused(".".join([b64(b'{"alg":"dir","enc":"A128GCM"}'), "", "", b64(inner.encode()), ""]))
    refused(forged({"alg": "EdDSA", "cty": "JWT"}, payload(), b"\x00" * 64))


def test_unicode_in_the_token_is_refused() -> None:
    refused(make().replace("e", "е", 1))
    refused(make() + "☃")


def test_a_verifier_needs_a_key_an_issuer_and_an_audience() -> None:
    with pytest.raises(ValueError):
        TokenVerifier(public_keys=[], issuer=ISSUER, audience=AUDIENCE)
    with pytest.raises(ValueError):
        TokenVerifier(public_keys=[KEY.public_key()], issuer="", audience=AUDIENCE)
    with pytest.raises(ValueError):
        TokenVerifier(public_keys=[KEY.public_key()], issuer=ISSUER, audience="")


def test_the_verifier_exposes_its_issuer_and_audience() -> None:
    assert (VERIFIER.issuer, VERIFIER.audience) == (ISSUER, AUDIENCE)


def test_key_rotation_accepts_tokens_of_either_key_and_no_others() -> None:
    third = Ed25519PrivateKey.generate()
    rotating = TokenVerifier(
        public_keys=[KEY.public_key(), OTHER_KEY.public_key()], issuer=ISSUER, audience=AUDIENCE
    )
    assert rotating.verify(make(key=KEY)).subject == "user-1"
    assert rotating.verify(make(key=OTHER_KEY)).subject == "user-1"
    refused(make(key=third), rotating)
    only_new = TokenVerifier(public_keys=[OTHER_KEY.public_key()], issuer=ISSUER, audience=AUDIENCE)
    refused(make(key=KEY), only_new)  # the old key was retired


def test_a_rotation_key_does_not_relax_the_other_checks() -> None:
    rotating = TokenVerifier(
        public_keys=[KEY.public_key(), OTHER_KEY.public_key()], issuer=ISSUER, audience=AUDIENCE
    )
    issued = int(now().timestamp())
    for key in (KEY, OTHER_KEY):
        refused(make(payload(aud="other"), key=key), rotating)
        refused(make(payload(iss="other"), key=key), rotating)
        refused(make(payload(exp=issued - 5), key=key), rotating)
        refused(make(payload(iat=issued, exp=issued + 90000), key=key), rotating)
        refused(make(payload(sub=" "), key=key), rotating)


def test_a_verifier_for_one_issuer_refuses_the_other_verifiers_tokens() -> None:
    other = TokenVerifier(public_keys=[KEY.public_key()], issuer="elsewhere", audience=AUDIENCE)
    refused(make(), other)


# --- Hypothesis ---------------------------------------------------------------------------------

segment = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_", max_size=120
)


@settings(max_examples=300)
@given(st.text(max_size=300))
def test_random_text_never_verifies_and_only_raises_invalid_token(text: str) -> None:
    with pytest.raises(InvalidToken):
        VERIFIER.verify(text)


@settings(max_examples=300)
@given(segment, segment, segment)
def test_random_three_part_strings_never_verify(a: str, b: str, c: str) -> None:
    with pytest.raises(InvalidToken):
        VERIFIER.verify(f"{a}.{b}.{c}")


@settings(max_examples=200)
@given(st.binary(max_size=200))
def test_random_signatures_never_verify(signature: bytes) -> None:
    header, claims, _ = make().split(".")
    with pytest.raises(InvalidToken):
        VERIFIER.verify(f"{header}.{claims}.{b64(signature)}")


@settings(max_examples=300)
@given(st.data())
def test_changing_any_character_but_the_last_breaks_the_token(data: st.DataObject) -> None:
    token = make()
    index = data.draw(st.integers(min_value=0, max_value=len(token) - 2))
    replacement = data.draw(
        st.sampled_from("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.")
    )
    if replacement == token[index]:
        return
    mutated = token[:index] + replacement + token[index + 1 :]
    with pytest.raises(InvalidToken):
        VERIFIER.verify(mutated)


PRINTABLE = st.text(min_size=1, max_size=200).filter(lambda s: s.isprintable() and s == s.strip())


@settings(max_examples=100)
@given(PRINTABLE)
def test_any_clean_subject_round_trips(subject: str) -> None:
    try:
        token = make(payload(sub=subject))
    except UnicodeEncodeError, ValueError:
        return
    assert VERIFIER.verify(token).subject == subject


@pytest.mark.parametrize("claim", ["sub", "iss"])
@pytest.mark.parametrize(
    "value",
    ["\x00", "a\x00b", "\x1b[31m", "a\x07", "a\nb", "a\rb", "a\tb", "a\u2028b", "a\u2029b",
     "a\x7f", "a\u200eb", "a\x85b"],
)  # fmt: skip
def test_non_printable_names_are_refused(claim: str, value: str) -> None:
    assert not value.isprintable()
    refused(make(payload(**{claim: value})), _verifier_for(value) if claim == "iss" else VERIFIER)


def _verifier_for(issuer: str) -> TokenVerifier:
    return TokenVerifier(public_keys=[KEY.public_key()], issuer=issuer, audience=AUDIENCE)


@pytest.mark.parametrize("claim", ["sub", "iss"])
def test_names_longer_than_200_characters_are_refused(claim: str) -> None:
    assert MAX_NAME_LENGTH == 200
    verifier = _verifier_for("i" * 200)
    ok = payload(**{"iss": "i" * 200, "sub": "s" * 200})
    assert verifier.verify(make(ok)).subject == "s" * 200
    too_long = payload(**{"iss": "i" * 200, "sub": "s" * 200, claim: "x" * 201})
    refused(make(too_long), _verifier_for(too_long["iss"]))


@pytest.mark.parametrize("claim", ["sub", "iss"])
@pytest.mark.parametrize("value", ["", " ", " a", "a ", 5, None, ["a"], True])
def test_names_that_are_not_clean_text_are_refused(claim: str, value: Any) -> None:
    claims = payload()
    claims[claim] = value
    header = {"alg": ALGORITHM, "typ": "JWT"}
    signing_input = f"{b64(json.dumps(header).encode())}.{b64(json.dumps(claims).encode())}"
    token = f"{signing_input}.{b64(KEY.sign(signing_input.encode()))}"
    refused(token)


@settings(max_examples=100)
@given(st.integers(min_value=-200000, max_value=200000))
def test_lifetime_boundary_is_exactly_24_hours(delta: int) -> None:
    issued = int(now().timestamp())
    token = make(payload(iat=issued, exp=issued + 86400 + delta))
    if delta > 0:
        with pytest.raises(InvalidToken):
            VERIFIER.verify(token)
    elif delta > -86390:  # far enough from "expires now" to be independent of the clock
        assert VERIFIER.verify(token).subject == "user-1"


# --- over HTTP --------------------------------------------------------------------------------


@pytest.mark.db
class TestHttp:
    @staticmethod
    def get(api: ApiHarness, authorization: str | None, path: str = "/v1/me") -> Any:
        headers = {} if authorization is None else {"Authorization": authorization}
        return api.client.get(path, headers=headers)

    def bearer(self, api: ApiHarness, **kwargs: Any) -> str:
        return "Bearer " + api.token(api.subject(Role.STUDENT), **kwargs)

    def test_the_good_token_works(self, api: ApiHarness) -> None:
        assert self.get(api, self.bearer(api)).status_code == 200

    @pytest.mark.parametrize(
        "case",
        [
            "expired",
            "future",
            "audience",
            "issuer",
            "key",
            "too-long-lifetime",
            "tampered-payload",
            "tampered-signature",
            "alg-none",
            "no-signature",
            "garbage",
            "too-long",
            "blank-subject",
        ],
    )
    def test_every_bad_token_is_401(self, api: ApiHarness, case: str) -> None:
        subject = api.subject(Role.STUDENT)
        make_token: dict[str, Callable[[], str]] = {
            "expired": lambda: api.token(
                subject,
                now=datetime.now(tz=UTC) - timedelta(hours=1),
                lifetime=timedelta(minutes=5),
            ),
            "future": lambda: api.token(subject, now=datetime.now(tz=UTC) + timedelta(hours=1)),
            "audience": lambda: api.token(subject, audience="someone-else"),
            "issuer": lambda: api.token(subject, issuer="someone-else"),
            "key": lambda: api.token(subject, key=Ed25519PrivateKey.generate()),
            "too-long-lifetime": lambda: api.token(subject, lifetime=timedelta(hours=25)),
            "tampered-payload": lambda: self._tamper_payload(api, subject),
            "tampered-signature": lambda: self._tamper_signature(api, subject),
            "alg-none": lambda: forged(
                {"alg": "none", "typ": "JWT"},
                payload(iss=DEV_ISSUER, aud=DEV_AUDIENCE, sub=subject),
            ),
            "no-signature": lambda: api.token(subject).rsplit(".", 1)[0] + ".",
            "garbage": lambda: "not.a.token",
            "too-long": lambda: api.token("a" * 5000),
            "blank-subject": lambda: api.token(" "),
        }
        response = self.get(api, "Bearer " + make_token[case]())
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"
        assert response.json()["code"] == "unauthenticated"

    @staticmethod
    def _tamper_payload(api: ApiHarness, subject: str) -> str:
        header, _, signature = api.token(subject).split(".")
        admin = api.subject(Role.PLATFORM_ADMIN)
        evil = b64(json.dumps(payload(iss=DEV_ISSUER, aud=DEV_AUDIENCE, sub=admin)).encode())
        return f"{header}.{evil}.{signature}"

    @staticmethod
    def _tamper_signature(api: ApiHarness, subject: str) -> str:
        header, claims, signature = api.token(subject).split(".")
        middle = len(signature) // 2
        flipped = (
            signature[:middle]
            + ("A" if signature[middle] != "A" else "B")
            + signature[middle + 1 :]
        )
        return f"{header}.{claims}.{flipped}"

    def test_hs256_signed_with_the_public_key_is_401(self, api: ApiHarness) -> None:
        public = api.key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        claims = payload(iss=DEV_ISSUER, aud=DEV_AUDIENCE, sub=api.subject(Role.PLATFORM_ADMIN))
        header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        signing_input = f"{header}.{b64(json.dumps(claims).encode())}"
        mac = hmac.new(public, signing_input.encode(), hashlib.sha256).digest()
        token = f"{signing_input}.{b64(mac)}"
        assert self.get(api, f"Bearer {token}").status_code == 401

    @pytest.mark.parametrize(
        "header",
        [
            None,
            "",
            " ",
            "Bearer",
            "Bearer ",
            "Bearer  ",
            "Basic dXNlcjpwYXNz",
            "Token abc",
            "Digest abc",
            "Negotiate abc",
            "Bearer-x abc",
            "Bearerabc",
            "abc",
        ],
    )
    def test_missing_or_malformed_authorization_header_is_401(
        self, api: ApiHarness, header: str | None
    ) -> None:
        response = self.get(api, header)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"

    def test_a_good_token_under_the_wrong_scheme_is_401(self, api: ApiHarness) -> None:
        token = api.token(api.subject(Role.STUDENT))
        for scheme in ("Basic", "Token", "JWT", "Bearer2", "Mac"):
            assert self.get(api, f"{scheme} {token}").status_code == 401
        assert self.get(api, token).status_code == 401  # no scheme at all

    def test_a_good_token_with_trailing_garbage_is_401(self, api: ApiHarness) -> None:
        token = api.token(api.subject(Role.STUDENT))
        assert self.get(api, f"Bearer {token} extra").status_code == 401
        assert self.get(api, f"Bearer {token}.").status_code == 401
        assert self.get(api, f"Bearer {token},{token}").status_code == 401

    def test_the_token_is_taken_from_the_header_only(self, api: ApiHarness) -> None:
        token = api.token(api.subject(Role.STUDENT))
        assert api.client.get(f"/v1/me?access_token={token}").status_code == 401
        assert api.client.get(f"/v1/me?token={token}").status_code == 401
        assert (
            api.client.get(
                "/v1/me", headers={"Cookie": f"token={token}; session={token}"}
            ).status_code
            == 401
        )
        assert api.client.get("/v1/me", headers={"X-Access-Token": token}).status_code == 401
        assert api.client.get("/v1/me", headers={"X-Forwarded-User": "admin"}).status_code == 401

    def test_a_token_at_the_length_limit_still_reaches_the_account_check(
        self, api: ApiHarness
    ) -> None:
        """A long, valid subject is a valid token that names no account: 401, not a 5xx."""
        response = self.get(api, "Bearer " + api.token("a" * 2000))
        assert response.status_code == 401

    def test_a_subject_over_the_account_limit_is_just_unknown(self, api: ApiHarness) -> None:
        for subject in ("a" * 201, "é" * 150):
            assert self.get(api, "Bearer " + api.token(subject)).status_code == 401

    def test_a_nul_or_control_character_in_the_subject_is_401(self, api: ApiHarness) -> None:
        for subject in ("a\x00b", "\x00", "a\x1bb", "a\nb", "a\u2028b"):
            assert self.get(api, "Bearer " + api.token(subject)).status_code == 401

    def test_a_subject_that_looks_like_sql_is_just_unknown(self, api: ApiHarness) -> None:
        for subject in ("' OR '1'='1", "x'; DROP TABLE account;--", "%", "_"):
            assert self.get(api, "Bearer " + api.token(subject)).status_code == 401
        assert self.get(api, self.bearer(api)).status_code == 200  # the tables are still there

    def test_a_good_token_is_401_before_the_endpoint_is_judged(self, api: ApiHarness) -> None:
        """Bad token on an admin endpoint: 401, not 404."""
        bad = "Bearer " + api.token(api.subject(Role.PLATFORM_ADMIN), audience="x")
        assert self.get(api, bad, "/v1/admin/questions").status_code == 401

    def test_the_failure_reason_is_not_in_the_response(self, api: ApiHarness) -> None:
        subject = api.subject(Role.STUDENT)
        reasons = [
            api.token(subject, now=datetime.now(tz=UTC) - timedelta(hours=1)),
            api.token(subject, audience="x"),
            api.token(subject, issuer="x"),
            api.token(subject, key=Ed25519PrivateKey.generate()),
            api.token("unknown-person"),
        ]
        bodies = {self.get(api, "Bearer " + t).content for t in reasons}
        assert len(bodies) == 1
