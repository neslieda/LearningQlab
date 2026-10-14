"""Start-up checks (docs/slices/M1G-5-SOZLESME.md section 3.1): `Settings.from_env`,
`create_app`, `policy.check_routes` and the development signing key. None of this needs the
database: an application is built with an unbound session factory and never called, or called
only on routes that are refused before any database access.
"""

from __future__ import annotations

import os
import stat
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy.orm import sessionmaker
from starlette.routing import Mount, Route, WebSocketRoute

from qlab.api import errors, policy
from qlab.api.app import create_app
from qlab.api.settings import (
    Environment,
    Settings,
    StartupError,
    build_verifier,
    check_verifier,
)
from qlab.content import math
from qlab.identity import devkey
from qlab.identity.tokens import DEV_AUDIENCE, DEV_ISSUER, InvalidToken, TokenVerifier, sign
from qlab.organizations.service import Role

NON_LOCAL = [Environment.STAGING, Environment.PRODUCTION]
FACTORY: sessionmaker[Any] = sessionmaker()  # unbound: any use would fail loudly


def verifier(
    issuer: str = "https://idp.example.invalid", key: Ed25519PrivateKey | None = None
) -> TokenVerifier:
    key = key or Ed25519PrivateKey.generate()
    return TokenVerifier(public_keys=[key.public_key()], issuer=issuer, audience="aud")


def build(settings: Settings, **kwargs: Any) -> FastAPI:
    return create_app(settings, session_factory=FACTORY, check_renderer=False, **kwargs)


# --- Settings.from_env ---------------------------------------------------------------------------


@pytest.mark.parametrize("env", Environment)
def test_each_environment_name_parses(env: Environment) -> None:
    environ = {"QLAB_ENV": env.value}
    if env is not Environment.LOCAL:
        environ["QLAB_FORBID_SELF_APPROVAL"] = "true"
    assert Settings.from_env(environ).environment is env


@pytest.mark.parametrize(
    "value",
    [None, "", " ", "prod", "dev", "development", "test", "LOCAL", "Local", "Production", " local",
     "local ", "local\n", "locals", "staging2", "0", "none"],
)  # fmt: skip
def test_missing_or_unknown_environment_is_refused(value: str | None) -> None:
    environ = {} if value is None else {"QLAB_ENV": value}
    with pytest.raises(StartupError, match="QLAB_ENV"):
        Settings.from_env(environ)


def test_an_environment_missing_from_the_mapping_is_not_read_from_the_process(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QLAB_ENV", "local")
    with pytest.raises(StartupError):
        Settings.from_env({})


def test_from_env_reads_the_process_environment_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QLAB_ENV", "local")
    monkeypatch.delenv("QLAB_FORBID_SELF_APPROVAL", raising=False)
    assert Settings.from_env().environment is Environment.LOCAL
    monkeypatch.delenv("QLAB_ENV")
    with pytest.raises(StartupError):
        Settings.from_env()


def test_self_approval_defaults_to_off_locally_and_on_elsewhere() -> None:
    assert Settings.from_env({"QLAB_ENV": "local"}).forbid_self_approval is False
    assert Settings.from_env({"QLAB_ENV": "staging"}).forbid_self_approval is True
    assert Settings.from_env({"QLAB_ENV": "production"}).forbid_self_approval is True


@pytest.mark.parametrize(("flag", "expected"), [("true", True), ("false", False)])
def test_the_flag_is_honoured_locally(flag: str, expected: bool) -> None:
    settings = Settings.from_env({"QLAB_ENV": "local", "QLAB_FORBID_SELF_APPROVAL": flag})
    assert settings.forbid_self_approval is expected


@pytest.mark.parametrize("env", NON_LOCAL)
def test_outside_local_the_flag_must_be_true(env: Environment) -> None:
    ok = Settings.from_env({"QLAB_ENV": env.value, "QLAB_FORBID_SELF_APPROVAL": "true"})
    assert ok.forbid_self_approval is True
    with pytest.raises(StartupError, match="QLAB_FORBID_SELF_APPROVAL"):
        Settings.from_env({"QLAB_ENV": env.value, "QLAB_FORBID_SELF_APPROVAL": "false"})


@pytest.mark.parametrize(
    "flag",
    ["", " ", "1", "0", "yes", "no", "on", "off", "True", "TRUE", "False", "FALSE", " true",
     "true ", "t", "y", "enabled", "null"],
)  # fmt: skip
@pytest.mark.parametrize("env", list(Environment))
def test_any_other_flag_value_is_refused_everywhere(env: Environment, flag: str) -> None:
    """Parsing is strict: a value that is not exactly true or false is never guessed at."""
    with pytest.raises(StartupError, match="true or false"):
        Settings.from_env({"QLAB_ENV": env.value, "QLAB_FORBID_SELF_APPROVAL": flag})


@pytest.mark.parametrize("env", NON_LOCAL)
def test_a_dev_key_file_outside_local_is_refused(env: Environment, tmp_path: Path) -> None:
    for path in (str(tmp_path / "key.pem"), "/dev/null", "relative.pem", "x"):
        with pytest.raises(StartupError, match="QLAB_DEV_KEY_FILE"):
            Settings.from_env(
                {
                    "QLAB_ENV": env.value,
                    "QLAB_FORBID_SELF_APPROVAL": "true",
                    "QLAB_DEV_KEY_FILE": path,
                }
            )


def test_the_dev_key_file_is_taken_from_the_mapping_locally(tmp_path: Path) -> None:
    path = tmp_path / "k.pem"
    settings = Settings.from_env({"QLAB_ENV": "local", "QLAB_DEV_KEY_FILE": str(path)})
    assert settings.dev_key_file == path


def test_the_dev_key_file_defaults_to_the_home_directory_locally(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("QLAB_DEV_KEY_FILE", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    settings = Settings.from_env({"QLAB_ENV": "local"})
    assert settings.dev_key_file == tmp_path / ".qlab" / "dev-signing-key.pem"


@pytest.mark.parametrize("env", NON_LOCAL)
def test_outside_local_there_is_no_dev_key_file(env: Environment) -> None:
    settings = Settings.from_env({"QLAB_ENV": env.value, "QLAB_FORBID_SELF_APPROVAL": "true"})
    assert settings.dev_key_file is None


@pytest.mark.parametrize("env", NON_LOCAL)
def test_validate_refuses_unsafe_combinations_built_by_hand(env: Environment) -> None:
    Settings(env, True).validate()
    with pytest.raises(StartupError):
        Settings(env, False).validate()
    with pytest.raises(StartupError):
        Settings(env, True, dev_key_file=Path("/nonexistent/key.pem")).validate()
    with pytest.raises(StartupError):
        Settings(env, False, dev_key_file=Path("/nonexistent/key.pem")).validate()


def test_validate_accepts_local_in_both_modes() -> None:
    Settings(Environment.LOCAL, False).validate()
    Settings(Environment.LOCAL, True).validate()


def test_settings_are_immutable() -> None:
    settings = Settings(Environment.LOCAL, False)
    with pytest.raises(AttributeError):
        settings.environment = Environment.PRODUCTION  # type: ignore[misc]
    with pytest.raises(AttributeError):
        settings.forbid_self_approval = False  # type: ignore[misc]


@given(st.text(max_size=20))
def test_no_environment_text_but_the_three_names_is_accepted(text: str) -> None:
    if text in {"local", "staging", "production"}:
        return
    with pytest.raises(StartupError):
        Settings.from_env({"QLAB_ENV": text})


# --- create_app -----------------------------------------------------------------------------------


def test_local_with_a_verifier_starts() -> None:
    app = build(Settings(Environment.LOCAL, False), verifier=verifier(DEV_ISSUER))
    assert isinstance(app, FastAPI)


@pytest.mark.parametrize("env", NON_LOCAL)
def test_a_verifier_with_the_dev_issuer_is_refused_outside_local(env: Environment) -> None:
    for audience in (DEV_AUDIENCE, "anything"):
        dev = TokenVerifier(
            public_keys=[Ed25519PrivateKey.generate().public_key()],
            issuer=DEV_ISSUER,
            audience=audience,
        )
        with pytest.raises(StartupError, match="development issuer"):
            build(Settings(env, True), verifier=dev)
        with pytest.raises(StartupError):
            check_verifier(Settings(env, True), dev)


def test_check_verifier_allows_the_dev_issuer_locally_and_other_issuers_everywhere() -> None:
    check_verifier(Settings(Environment.LOCAL, False), verifier(DEV_ISSUER))
    check_verifier(Settings(Environment.LOCAL, False), verifier("https://idp.example.invalid"))
    for env in NON_LOCAL:
        check_verifier(Settings(env, True), verifier("https://idp.example.invalid"))


@pytest.mark.parametrize("env", NON_LOCAL)
def test_no_verifier_is_refused_outside_local(env: Environment) -> None:
    with pytest.raises(StartupError, match="identity provider"):
        build(Settings(env, True))
    with pytest.raises(StartupError):
        build_verifier(Settings(env, True))


@pytest.mark.parametrize("env", NON_LOCAL)
def test_outside_local_a_real_verifier_starts_only_with_separation_of_duties(
    env: Environment,
) -> None:
    assert isinstance(build(Settings(env, True), verifier=verifier()), FastAPI)
    with pytest.raises(StartupError):
        build(Settings(env, False), verifier=verifier())


@pytest.mark.parametrize("env", NON_LOCAL)
def test_outside_local_a_dev_key_in_the_settings_is_refused_even_with_a_verifier(
    env: Environment, tmp_path: Path
) -> None:
    with pytest.raises(StartupError):
        build(Settings(env, True, dev_key_file=tmp_path / "k.pem"), verifier=verifier())


def test_local_without_a_key_file_refuses_and_says_how_to_create_one(tmp_path: Path) -> None:
    with pytest.raises(StartupError, match="qlab.api.dev init"):
        build(Settings(Environment.LOCAL, False, dev_key_file=tmp_path / "missing.pem"))


def test_local_with_an_unsafe_key_file_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "k.pem"
    devkey.generate(path)
    path.chmod(0o644)
    with pytest.raises(StartupError):
        build(Settings(Environment.LOCAL, False, dev_key_file=path))


def test_local_without_settings_key_file_has_none_to_load() -> None:
    with pytest.raises(StartupError):
        build(Settings(Environment.LOCAL, False, dev_key_file=None))


def test_local_with_a_good_key_file_builds_a_verifier_for_the_dev_issuer(tmp_path: Path) -> None:
    path = tmp_path / "k.pem"
    key = devkey.generate(path)
    app = build(Settings(Environment.LOCAL, False, dev_key_file=path))
    built: TokenVerifier = app.state.verifier
    assert (built.issuer, built.audience) == (DEV_ISSUER, DEV_AUDIENCE)
    token = sign(
        key, issuer=DEV_ISSUER, audience=DEV_AUDIENCE, subject="s", lifetime=timedelta(minutes=5)
    )
    assert built.verify(token).subject == "s"
    stranger = sign(
        Ed25519PrivateKey.generate(), issuer=DEV_ISSUER, audience=DEV_AUDIENCE, subject="s",
        lifetime=timedelta(minutes=5),
    )  # fmt: skip
    with pytest.raises(InvalidToken):
        built.verify(stranger)


def test_a_missing_renderer_stops_the_start_up(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken() -> None:
        raise math.RendererUnavailable("no node")

    monkeypatch.setattr(math, "ensure_renderer", broken)
    settings = Settings(Environment.LOCAL, False)
    with pytest.raises(math.RendererUnavailable):
        create_app(settings, verifier=verifier(DEV_ISSUER), session_factory=FACTORY)
    # and a test may skip the check explicitly
    assert isinstance(build(settings, verifier=verifier(DEV_ISSUER)), FastAPI)


def test_the_renderer_is_checked_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []
    monkeypatch.setattr(math, "ensure_renderer", lambda: calls.append(1))
    create_app(
        Settings(Environment.LOCAL, False), verifier=verifier(DEV_ISSUER), session_factory=FACTORY
    )
    assert calls == [1]
    create_app(
        Settings(Environment.LOCAL, False), verifier=verifier(DEV_ISSUER), session_factory=FACTORY,
        check_renderer=False,
    )  # fmt: skip
    assert calls == [1]


def test_an_unsafe_setting_stops_the_start_up_before_anything_else(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[int] = []
    monkeypatch.setattr(math, "ensure_renderer", lambda: called.append(1))
    with pytest.raises(StartupError):
        create_app(
            Settings(Environment.PRODUCTION, False), verifier=verifier(), session_factory=FACTORY
        )
    assert called == []


def test_the_interactive_documentation_is_off() -> None:
    app = build(Settings(Environment.LOCAL, False), verifier=verifier(DEV_ISSUER))
    client = TestClient(app, raise_server_exceptions=False)
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 404


def test_the_application_keeps_its_settings_and_verifier() -> None:
    settings = Settings(Environment.LOCAL, True)
    v = verifier(DEV_ISSUER)
    app = build(settings, verifier=v)
    assert app.state.settings is settings
    assert app.state.verifier is v


# --- policy.check_routes ----------------------------------------------------------------------


def a_valid_app() -> FastAPI:
    return build(Settings(Environment.LOCAL, False), verifier=verifier(DEV_ISSUER))


async def static_app(scope: Any, receive: Any, send: Any) -> None:
    return None


def noop() -> dict[str, str]:
    return {}


def test_the_real_application_passes_the_check() -> None:
    policy.check_routes(a_valid_app())


def test_a_route_missing_from_the_table_is_refused() -> None:
    app = a_valid_app()
    app.add_api_route("/v1/extra", noop, methods=["GET"])
    with pytest.raises(policy.PolicyError, match="without an entry"):
        policy.check_routes(app)


def test_a_new_method_on_a_known_path_is_refused() -> None:
    for method in ("DELETE", "PATCH", "POST"):
        app = a_valid_app()
        app.add_api_route("/v1/me", noop, methods=[method])
        with pytest.raises(policy.PolicyError):
            policy.check_routes(app)


def test_a_path_that_differs_only_in_parameter_name_is_refused() -> None:
    app = a_valid_app()
    app.add_api_route("/v1/questions/{id}", noop, methods=["GET"])
    with pytest.raises(policy.PolicyError):
        policy.check_routes(app)


def test_a_table_entry_without_a_route_is_refused() -> None:
    app = a_valid_app()
    victim = next(r for r in app.routes if getattr(r, "path", "") == "/v1/me")
    app.router.routes.remove(victim)
    with pytest.raises(policy.PolicyError, match="without a route"):
        policy.check_routes(app)


def test_an_application_without_routes_is_refused() -> None:
    with pytest.raises(policy.PolicyError):
        policy.check_routes(FastAPI(docs_url=None, redoc_url=None, openapi_url=None))


@pytest.mark.parametrize(
    "plain",
    [
        APIRoute("/healthz", noop, methods=["GET"]),  # the right path, the wrong class
        APIRoute("/v1/extra", noop, methods=["GET"]),
        Route("/plain", lambda request: None),
        Mount("/static", app=static_app),
        WebSocketRoute("/ws", lambda websocket: None),
    ],
    ids=["APIRoute-known-path", "APIRoute-new-path", "Route", "Mount", "WebSocketRoute"],
)
def test_a_route_that_is_not_a_policy_route_is_refused(plain: Any) -> None:
    app = a_valid_app()
    app.router.routes.append(plain)
    with pytest.raises(policy.PolicyError, match="PolicyRoute"):
        policy.check_routes(app)


def test_a_plain_route_that_shadows_a_table_entry_is_refused() -> None:
    """Putting an unguarded route in front of the real one must not pass the check."""
    app = a_valid_app()
    app.router.routes.insert(0, APIRoute("/v1/admin/questions", noop, methods=["GET"]))
    with pytest.raises(policy.PolicyError):
        policy.check_routes(app)


def test_an_entry_that_allows_no_role_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.router.route_class = policy.PolicyRoute
    app.add_api_route("/a", noop, methods=["GET"])
    table = {("GET", "/a"): frozenset[Role]()}
    monkeypatch.setattr(policy, "ENDPOINT_POLICY", table)
    with pytest.raises(policy.PolicyError, match="no role"):
        policy.check_routes(app)
    monkeypatch.setattr(policy, "ENDPOINT_POLICY", {("GET", "/a"): frozenset({Role.REVIEWER})})
    policy.check_routes(app)
    monkeypatch.setattr(policy, "ENDPOINT_POLICY", {("GET", "/a"): policy.PUBLIC})
    policy.check_routes(app)


def test_create_app_runs_the_route_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """If the table loses an entry the application cannot start."""
    smaller = {k: v for k, v in policy.ENDPOINT_POLICY.items() if k != ("GET", "/v1/me")}
    monkeypatch.setattr(policy, "ENDPOINT_POLICY", smaller)
    with pytest.raises(policy.PolicyError):
        build(Settings(Environment.LOCAL, False), verifier=verifier(DEV_ISSUER))


def test_a_route_outside_the_table_that_reached_the_handler_anyway_is_refused() -> None:
    """Default deny: a PolicyRoute without an entry never runs its handler."""
    ran: list[int] = []

    def handler() -> dict[str, str]:
        ran.append(1)
        return {"secret": "x"}

    app = FastAPI()
    app.router.route_class = policy.PolicyRoute
    errors.install(app)
    app.add_api_route("/not-in-the-table", handler, methods=["GET"])
    response = TestClient(app, raise_server_exceptions=False).get("/not-in-the-table")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
    assert ran == []


# --- the development key -----------------------------------------------------------------------


def mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def test_generate_creates_a_private_file(tmp_path: Path) -> None:
    path = tmp_path / "dir" / "dev.pem"
    key = devkey.generate(path)
    assert isinstance(key, Ed25519PrivateKey)
    assert mode(path) == 0o600
    assert mode(path.parent) == 0o700
    assert b"PRIVATE KEY" in path.read_bytes()


def test_generate_is_private_whatever_the_umask(tmp_path: Path) -> None:
    previous = os.umask(0)
    try:
        path = tmp_path / "open-umask" / "dev.pem"
        devkey.generate(path)
    finally:
        os.umask(previous)
    assert mode(path) == 0o600


def test_generated_keys_differ(tmp_path: Path) -> None:
    a = devkey.generate(tmp_path / "a.pem")
    b = devkey.generate(tmp_path / "b.pem")
    raw = (serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    assert a.public_key().public_bytes(*raw) != b.public_key().public_bytes(*raw)


def test_load_returns_the_generated_key(tmp_path: Path) -> None:
    path = tmp_path / "dev.pem"
    key = devkey.generate(path)
    loaded = devkey.load(path)
    raw = (serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    assert loaded.public_key().public_bytes(*raw) == key.public_key().public_bytes(*raw)
    token = sign(loaded, issuer="i", audience="a", subject="s", lifetime=timedelta(minutes=1))
    TokenVerifier(public_keys=[key.public_key()], issuer="i", audience="a").verify(token)


def test_generate_never_overwrites(tmp_path: Path) -> None:
    path = tmp_path / "dev.pem"
    devkey.generate(path)
    before = path.read_bytes()
    with pytest.raises(devkey.DevKeyError, match="not overwritten"):
        devkey.generate(path)
    assert path.read_bytes() == before


def test_generate_does_not_overwrite_an_unrelated_file(tmp_path: Path) -> None:
    path = tmp_path / "precious.txt"
    path.write_text("keep me")
    with pytest.raises(devkey.DevKeyError):
        devkey.generate(path)
    assert path.read_text() == "keep me"


def test_load_of_a_missing_file_is_a_dev_key_error(tmp_path: Path) -> None:
    with pytest.raises(devkey.DevKeyError, match="does not exist"):
        devkey.load(tmp_path / "nope.pem")


@pytest.mark.parametrize(
    "bits", [0o640, 0o604, 0o660, 0o606, 0o644, 0o666, 0o620, 0o602, 0o610, 0o601, 0o700 | 0o070]
)
def test_load_refuses_a_file_others_can_access(tmp_path: Path, bits: int) -> None:
    path = tmp_path / "dev.pem"
    devkey.generate(path)
    path.chmod(bits)
    with pytest.raises(devkey.DevKeyError, match="other users"):
        devkey.load(path)


@pytest.mark.parametrize("bits", [0o600, 0o400, 0o500, 0o700])
def test_load_accepts_owner_only_files(tmp_path: Path, bits: int) -> None:
    path = tmp_path / "dev.pem"
    devkey.generate(path)
    path.chmod(bits)
    assert isinstance(devkey.load(path), Ed25519PrivateKey)


def private_file(tmp_path: Path, content: bytes) -> Path:
    path = tmp_path / "not-a-key.pem"
    path.write_bytes(content)
    path.chmod(0o600)
    return path


def test_load_refuses_files_that_are_not_ed25519_private_keys(tmp_path: Path) -> None:
    rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    rsa_pem = rsa_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    ed = Ed25519PrivateKey.generate()
    public_pem = ed.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    encrypted = ed.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(b"pw"),
    )
    raw = ed.private_bytes(
        serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()
    )
    pem_garbage = b"-----BEGIN PRIVATE KEY-----\nnot base64\n-----END PRIVATE KEY-----\n"
    contents = [b"", b"hello", pem_garbage, rsa_pem, public_pem, encrypted, raw, b"\x00" * 64]
    for content in contents:
        with pytest.raises(devkey.DevKeyError):
            devkey.load(private_file(tmp_path, content))


def test_errors_do_not_print_key_material(tmp_path: Path) -> None:
    path = tmp_path / "dev.pem"
    devkey.generate(path)
    body = path.read_text().splitlines()[1]
    path.chmod(0o644)
    with pytest.raises(devkey.DevKeyError) as caught:
        devkey.load(path)
    assert body not in str(caught.value)
    with pytest.raises(devkey.DevKeyError) as caught2:
        devkey.generate(path)
    assert body not in str(caught2.value)


def test_default_path_follows_the_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QLAB_DEV_KEY_FILE", str(tmp_path / "custom.pem"))
    assert devkey.default_path() == tmp_path / "custom.pem"
    monkeypatch.delenv("QLAB_DEV_KEY_FILE")
    monkeypatch.setenv("HOME", str(tmp_path))
    assert devkey.default_path() == tmp_path / ".qlab" / "dev-signing-key.pem"


def test_the_default_key_location_is_outside_any_repository(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("QLAB_DEV_KEY_FILE", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert devkey.default_path().is_relative_to(tmp_path)
    assert not devkey.default_path().is_relative_to(Path(__file__).resolve().parents[3])


def test_build_verifier_refuses_an_unsafe_key_with_a_startup_error(tmp_path: Path) -> None:
    path = tmp_path / "dev.pem"
    devkey.generate(path)
    path.chmod(0o666)
    with pytest.raises(StartupError, match="other users"):
        build_verifier(Settings(Environment.LOCAL, False, dev_key_file=path))
    path.chmod(0o600)
    path.write_bytes(b"garbage")
    with pytest.raises(StartupError):
        build_verifier(Settings(Environment.LOCAL, False, dev_key_file=path))
