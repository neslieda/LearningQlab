"""The local development command, `python -m qlab.api.dev` (docs/slices/M1G-5-SOZLESME.md 3.7,
M1G-5-YETKILER.md section 2 item 4, decision D-59).

The command opens its own engine from QLAB_DATABASE_URL and commits, so these tests give it a
database of its own: a template is migrated once per module, and each test works on a fresh
copy that is dropped afterwards. Nothing the command writes outlives its test, and the shared
test database is never touched. The function names inside `qlab.api.dev` are not part of the
specification, so everything goes through `main(argv)`.
"""

from __future__ import annotations

import base64
import os
import re
import stat
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import sessionmaker

from qlab.api import dev, ids
from qlab.api.app import create_app
from qlab.api.settings import Environment, Settings, build_verifier
from qlab.identity import devkey
from qlab.identity.tokens import DEV_AUDIENCE, DEV_ISSUER, TokenVerifier
from qlab.organizations.service import Role
from tests.conftest import DEFAULT_TEST_URL, LOCAL_HOSTS, alembic_config

pytestmark = pytest.mark.db

ROLES = tuple(role.value for role in Role)
CLI_ACTOR = "system:dev-cli"
JWT = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")


# --- a database of its own -------------------------------------------------------------------


def _base_url() -> URL:
    url = make_url(os.environ.get("QLAB_TEST_DATABASE_URL", DEFAULT_TEST_URL))
    assert url.database is not None
    assert url.database.endswith("_test")
    assert url.host in LOCAL_HOSTS
    return url


def _recreate(url: URL, name: str, template: str | None = None) -> None:
    assert re.fullmatch(r"[a-z0-9_]+_test", name)
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        suffix = f' TEMPLATE "{template}"' if template else ""
        connection.execute(text(f'CREATE DATABASE "{name}"{suffix}'))  # noqa: S608
    admin.dispose()


def _drop(url: URL, name: str) -> None:
    assert re.fullmatch(r"[a-z0-9_]+_test", name)
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
    admin.dispose()


@pytest.fixture(scope="module")
def template_name() -> Iterator[str]:
    """A migrated, empty database that each test copies."""
    from alembic import command

    base = _base_url()
    assert base.database is not None
    name = base.database.removesuffix("_test") + "_clitpl_test"
    _recreate(base, name)
    engine = create_engine(base.set(database=name))
    with engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
    engine.dispose()
    yield name
    _drop(base, name)


@dataclass
class Cli:
    url: str
    engine: Engine
    key_file: Path
    home: Path

    def rows(self, sql: str, **parameters: Any) -> list[Any]:
        with self.engine.connect() as connection:
            return list(connection.execute(text(sql), parameters).all())

    def count(self, table: str) -> int:
        assert table in {"account", "role_assignment", "audit_log"}
        return int(self.rows(f"SELECT count(*) FROM {table}")[0][0])  # noqa: S608

    def audit(self) -> list[dict[str, Any]]:
        return [
            {"actor": a, "action": b, "entity_type": c, "entity_id": d, "data": e}
            for a, b, c, d, e in self.rows(
                "SELECT actor, action, entity_type, entity_id, data FROM audit_log "
                "ORDER BY occurred_at, id"
            )
        ]

    def account_id(self, role: str) -> uuid.UUID:
        [(value,)] = self.rows(
            "SELECT id FROM account WHERE issuer = :i AND subject = :s",
            i=DEV_ISSUER,
            s=f"dev-{role}",
        )
        assert isinstance(value, uuid.UUID)
        return value

    def active_roles(self, subject: str) -> set[str]:
        return {
            role
            for (role,) in self.rows(
                "SELECT r.role FROM role_assignment r JOIN account a ON a.id = r.account_id "
                "WHERE a.subject = :s AND r.revoked_at IS NULL",
                s=subject,
            )
        }


@pytest.fixture
def cli(template_name: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Cli]:
    base = _base_url()
    assert base.database is not None
    name = base.database.removesuffix("_test") + "_cli_test"
    _recreate(base, name, template=template_name)
    url = base.set(database=name)
    rendered = url.render_as_string(hide_password=False)
    key_file = tmp_path / "keys" / "dev-signing-key.pem"
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))  # the default key path must never be reached
    monkeypatch.setenv("QLAB_ENV", "local")
    monkeypatch.setenv("QLAB_DEV_KEY_FILE", str(key_file))
    monkeypatch.setenv("QLAB_DATABASE_URL", rendered)
    monkeypatch.delenv("QLAB_FORBID_SELF_APPROVAL", raising=False)
    engine = create_engine(url)
    try:
        yield Cli(rendered, engine, key_file, home)
    finally:
        engine.dispose()
        _drop(base, name)


@dataclass
class Result:
    code: int
    out: str
    err: str
    raised: BaseException | None = None

    @property
    def failed(self) -> bool:
        return self.code != 0 or self.raised is not None


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> Result:
    capsys.readouterr()
    code, raised = 0, None
    try:
        returned = dev.main(list(argv))
        code = returned if isinstance(returned, int) else 0
    except SystemExit as exit_:
        code = exit_.code if isinstance(exit_.code, int) else (0 if exit_.code is None else 1)
    except Exception as error:
        code, raised = 1, error
    captured = capsys.readouterr()
    return Result(code, captured.out, captured.err, raised)


def secrets_of(key_file: Path) -> list[str]:
    """Every text form in which the private key could leak."""
    key = devkey.load(key_file)
    seed = key.private_bytes(
        serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()
    )
    der = key.private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    pem = key_file.read_text()
    body = [line for line in pem.splitlines() if line and not line.startswith("-----")]
    return [
        seed.hex(),
        base64.b64encode(seed).decode().rstrip("="),
        base64.urlsafe_b64encode(seed).decode().rstrip("="),
        base64.b64encode(der).decode().rstrip("="),
        base64.urlsafe_b64encode(der).decode().rstrip("="),
        *body,
        "PRIVATE KEY",
    ]


# --- outside the local environment -----------------------------------------------------------

COMMANDS: list[list[str]] = [
    ["init"],
    ["token", "reviewer"],
    ["accounts"],
    ["grant", "dev-student", "reviewer"],
    ["revoke", "dev-student", "student"],
]


@pytest.mark.parametrize("argv", COMMANDS, ids=lambda a: a[0])
@pytest.mark.parametrize("environment", ["staging", "production", "", "prod", "LOCAL"])
def test_outside_the_local_environment_nothing_happens(
    cli: Cli,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    argv: list[str],
    environment: str,
) -> None:
    monkeypatch.setenv("QLAB_ENV", environment)
    monkeypatch.delenv("QLAB_DEV_KEY_FILE")  # a key file is refused outside local anyway
    if environment in ("staging", "production"):
        monkeypatch.setenv("QLAB_FORBID_SELF_APPROVAL", "true")
    result = run(capsys, *argv)
    assert result.failed
    assert not result.out.strip() or not JWT.search(result.out)
    assert not cli.key_file.exists()
    assert not cli.key_file.parent.exists()
    assert not (cli.home / ".qlab").exists()
    assert cli.count("account") == 0
    assert cli.count("role_assignment") == 0
    assert cli.count("audit_log") == 0


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_a_key_file_setting_outside_local_is_refused_without_creating_it(
    cli: Cli, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, environment: str
) -> None:
    monkeypatch.setenv("QLAB_ENV", environment)
    monkeypatch.setenv("QLAB_FORBID_SELF_APPROVAL", "true")  # QLAB_DEV_KEY_FILE stays set
    result = run(capsys, "init")
    assert result.failed
    assert not cli.key_file.exists()
    assert cli.count("account") == 0
    assert cli.count("audit_log") == 0


def test_an_unknown_command_or_no_command_fails_and_changes_nothing(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    for argv in ([], ["frobnicate"], ["token"], ["grant", "dev-student"]):
        assert run(capsys, *argv).failed
    assert not cli.key_file.exists()
    assert cli.count("account") == 0


# --- init ------------------------------------------------------------------------------------


def test_init_creates_the_key_the_six_accounts_their_roles_and_prints_the_table(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    result = run(capsys, "init")
    assert not result.failed, result.err or result.raised
    mode = stat.S_IMODE(cli.key_file.stat().st_mode)
    assert mode == 0o600
    devkey.load(cli.key_file)  # a valid Ed25519 key that load() accepts

    assert cli.count("account") == 6
    accounts = cli.rows("SELECT issuer, subject FROM account ORDER BY subject")
    assert [(i, s) for i, s in accounts] == [(DEV_ISSUER, f"dev-{r}") for r in sorted(ROLES)]
    for role in ROLES:
        assert cli.active_roles(f"dev-{role}") == {role}, role
        assert role in result.out
        assert ids.actor(cli.account_id(role)) in result.out
    assert cli.count("role_assignment") == 6


def test_init_writes_one_granted_entry_per_role(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    run(capsys, "init")
    entries = cli.audit()
    assert len(entries) == 6
    assert {e["data"]["role"] for e in entries} == set(ROLES)
    for entry in entries:
        role = entry["data"]["role"]
        assert entry["actor"] == CLI_ACTOR
        assert entry["action"] == "role_assignment.granted"
        assert entry["entity_type"] == "account"
        assert entry["entity_id"] == ids.actor(cli.account_id(role))
        assert entry["data"] == {"role": role}


def test_init_can_be_run_again_and_changes_nothing(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    first = run(capsys, "init")
    key_bytes = cli.key_file.read_bytes()
    accounts = cli.rows("SELECT id, subject FROM account ORDER BY subject")
    audit = cli.audit()
    second = run(capsys, "init")
    assert not second.failed, second.err or second.raised
    assert cli.key_file.read_bytes() == key_bytes
    assert cli.rows("SELECT id, subject FROM account ORDER BY subject") == accounts
    assert cli.count("account") == 6
    assert cli.count("role_assignment") == 6
    assert cli.audit() == audit  # a grant that already exists writes nothing
    for role in ROLES:  # it still prints the table
        assert ids.actor(cli.account_id(role)) in second.out
    assert first.out.count("acc_") == second.out.count("acc_")


def test_init_never_overwrites_an_existing_key(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    existing = devkey.generate(cli.key_file)
    before = cli.key_file.read_bytes()
    result = run(capsys, "init")
    assert not result.failed, result.err or result.raised
    assert cli.key_file.read_bytes() == before
    # and the accounts' tokens are signed by that key
    token = run(capsys, "token", "reviewer").out.strip()
    claims = TokenVerifier(
        public_keys=[existing.public_key()], issuer=DEV_ISSUER, audience=DEV_AUDIENCE
    ).verify(token)
    assert claims.subject == "dev-reviewer"


# --- token -----------------------------------------------------------------------------------


@pytest.mark.parametrize("role", ROLES)
def test_token_prints_only_a_token_the_verifier_built_from_the_key_accepts(
    cli: Cli, capsys: pytest.CaptureFixture[str], role: str
) -> None:
    run(capsys, "init")
    result = run(capsys, "token", role)
    assert not result.failed, result.err or result.raised
    token = result.out.strip()
    assert result.out == token + "\n"
    assert "\n" not in token
    assert JWT.fullmatch(token)
    verifier = TokenVerifier(
        public_keys=[devkey.load(cli.key_file).public_key()],
        issuer=DEV_ISSUER,
        audience=DEV_AUDIENCE,
    )
    claims = verifier.verify(token)
    assert claims.issuer == DEV_ISSUER
    assert claims.subject == f"dev-{role}"
    lifetime = claims.expires_at - datetime.now(tz=UTC)
    assert timedelta(hours=7, minutes=55) < lifetime <= timedelta(hours=8, minutes=1)


@pytest.mark.parametrize("hours", [1, 8, 24])
def test_token_accepts_hours_up_to_24(
    cli: Cli, capsys: pytest.CaptureFixture[str], hours: int
) -> None:
    run(capsys, "init")
    result = run(capsys, "token", "student", "--hours", str(hours))
    assert not result.failed, result.err or result.raised
    verifier = TokenVerifier(
        public_keys=[devkey.load(cli.key_file).public_key()],
        issuer=DEV_ISSUER,
        audience=DEV_AUDIENCE,
    )
    claims = verifier.verify(result.out.strip())
    lifetime = claims.expires_at - datetime.now(tz=UTC)
    assert (
        timedelta(hours=hours) - timedelta(minutes=2)
        < lifetime
        <= timedelta(hours=hours, seconds=5)
    )


@pytest.mark.parametrize("hours", ["25", "100", "24.5"])
def test_token_refuses_more_than_24_hours_and_prints_no_token(
    cli: Cli, capsys: pytest.CaptureFixture[str], hours: str
) -> None:
    run(capsys, "init")
    result = run(capsys, "token", "student", "--hours", hours)
    assert result.failed
    assert not JWT.search(result.out)


def test_token_for_an_unknown_role_fails_and_prints_no_token(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    run(capsys, "init")
    for role in ("superuser", "Reviewer", ""):
        result = run(capsys, "token", role)
        assert result.failed, role
        assert not JWT.search(result.out)


@pytest.mark.parametrize("role", ROLES)
def test_a_token_from_the_command_logs_in_to_the_application_with_that_role(
    cli: Cli, capsys: pytest.CaptureFixture[str], role: str
) -> None:
    run(capsys, "init")
    token = run(capsys, "token", role).out.strip()
    settings = Settings(Environment.LOCAL, forbid_self_approval=False, dev_key_file=cli.key_file)
    app = create_app(
        settings,
        verifier=build_verifier(settings),
        session_factory=sessionmaker(bind=cli.engine),
        check_renderer=False,
    )
    with TestClient(app) as client:
        response = client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    assert response.json() == {"account_id": ids.actor(cli.account_id(role)), "roles": [role]}


# --- accounts --------------------------------------------------------------------------------


def test_accounts_lists_the_development_accounts_and_their_roles(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    run(capsys, "init")
    result = run(capsys, "accounts")
    assert not result.failed, result.err or result.raised
    for role in ROLES:
        assert f"dev-{role}" in result.out or role in result.out
        assert ids.actor(cli.account_id(role)) in result.out
    before = result.out.count("reviewer")
    run(capsys, "grant", "dev-student", "reviewer")
    assert run(capsys, "accounts").out.count("reviewer") > before


def test_accounts_writes_nothing(cli: Cli, capsys: pytest.CaptureFixture[str]) -> None:
    run(capsys, "init")
    audit, key = cli.audit(), cli.key_file.read_bytes()
    run(capsys, "accounts")
    assert cli.audit() == audit
    assert cli.key_file.read_bytes() == key
    assert cli.count("role_assignment") == 6


# --- grant and revoke ------------------------------------------------------------------------


def test_a_grant_writes_exactly_one_audit_entry_with_the_specified_fields(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    run(capsys, "init")
    before = cli.audit()
    result = run(capsys, "grant", "dev-student", "reviewer")
    assert not result.failed, result.err or result.raised
    assert cli.active_roles("dev-student") == {"student", "reviewer"}
    new = cli.audit()[len(before) :]
    assert new == [
        {
            "actor": CLI_ACTOR,
            "action": "role_assignment.granted",
            "entity_type": "account",
            "entity_id": ids.actor(cli.account_id("student")),
            "data": {"role": "reviewer"},
        }
    ]


def test_a_repeated_grant_writes_nothing(cli: Cli, capsys: pytest.CaptureFixture[str]) -> None:
    run(capsys, "init")
    run(capsys, "grant", "dev-student", "reviewer")
    audit, assignments = cli.audit(), cli.count("role_assignment")
    run(capsys, "grant", "dev-student", "reviewer")
    run(capsys, "grant", "dev-student", "student")  # held since init
    assert cli.audit() == audit
    assert cli.count("role_assignment") == assignments


def test_a_revoke_writes_one_audit_entry_and_keeps_the_row(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    run(capsys, "init")
    before = cli.audit()
    result = run(capsys, "revoke", "dev-reviewer", "reviewer")
    assert not result.failed, result.err or result.raised
    assert cli.active_roles("dev-reviewer") == set()
    rows = cli.rows(
        "SELECT r.revoked_at, r.revoked_by FROM role_assignment r JOIN account a "
        "ON a.id = r.account_id WHERE a.subject = 'dev-reviewer'"
    )
    assert len(rows) == 1  # revoked, not deleted
    assert rows[0][0] is not None
    assert rows[0][1]
    new = cli.audit()[len(before) :]
    assert new == [
        {
            "actor": CLI_ACTOR,
            "action": "role_assignment.revoked",
            "entity_type": "account",
            "entity_id": ids.actor(cli.account_id("reviewer")),
            "data": {"role": "reviewer"},
        }
    ]


def test_a_repeated_revoke_and_a_revoke_of_a_role_never_held_write_nothing(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    run(capsys, "init")
    run(capsys, "revoke", "dev-reviewer", "reviewer")
    audit = cli.audit()
    run(capsys, "revoke", "dev-reviewer", "reviewer")
    run(capsys, "revoke", "dev-student", "platform_admin")
    assert cli.audit() == audit


def test_granting_again_after_a_revoke_is_a_new_assignment_with_its_own_entry(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    run(capsys, "init")
    run(capsys, "revoke", "dev-reviewer", "reviewer")
    before = len(cli.audit())
    run(capsys, "grant", "dev-reviewer", "reviewer")
    assert cli.active_roles("dev-reviewer") == {"reviewer"}
    new = cli.audit()[before:]
    assert [e["action"] for e in new] == ["role_assignment.granted"]


def test_a_role_change_takes_effect_for_the_next_request(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    run(capsys, "init")
    token = run(capsys, "token", "student").out.strip()
    settings = Settings(Environment.LOCAL, forbid_self_approval=False, dev_key_file=cli.key_file)
    app = create_app(
        settings,
        verifier=build_verifier(settings),
        session_factory=sessionmaker(bind=cli.engine),
        check_renderer=False,
    )
    headers = {"Authorization": f"Bearer {token}"}
    with TestClient(app) as client:
        assert client.get("/v1/admin/questions", headers=headers).status_code == 404
        run(capsys, "grant", "dev-student", "reviewer")
        assert client.get("/v1/admin/questions", headers=headers).status_code == 200
        run(capsys, "revoke", "dev-student", "reviewer")
        assert client.get("/v1/admin/questions", headers=headers).status_code == 404


@pytest.mark.parametrize(
    "argv",
    [
        ["grant", "dev-student", "superuser"],
        ["grant", "dev-student", "Reviewer"],
        ["revoke", "dev-student", "superuser"],
    ],
)
def test_an_unknown_role_is_refused_and_writes_nothing(
    cli: Cli, capsys: pytest.CaptureFixture[str], argv: list[str]
) -> None:
    run(capsys, "init")
    before, assignments = cli.audit(), cli.count("role_assignment")
    assert run(capsys, *argv).failed
    assert cli.audit() == before
    assert cli.count("role_assignment") == assignments


# --- key material ----------------------------------------------------------------------------


def test_key_material_never_appears_in_any_output(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    results = [run(capsys, "init")]
    secrets = secrets_of(cli.key_file)
    results += [
        run(capsys, "init"),
        run(capsys, "accounts"),
        run(capsys, "token", "reviewer"),
        run(capsys, "token", "platform_admin", "--hours", "24"),
        run(capsys, "token", "student", "--hours", "25"),
        run(capsys, "token", "nobody"),
        run(capsys, "grant", "dev-student", "reviewer"),
        run(capsys, "grant", "dev-student", "reviewer"),
        run(capsys, "revoke", "dev-student", "reviewer"),
        run(capsys, "revoke", "dev-student", "superuser"),
        run(capsys, "frobnicate"),
        run(capsys),
    ]
    for result in results:
        for secret in secrets:
            assert secret not in result.out
            assert secret not in result.err
            assert secret not in str(result.raised or "")


def test_an_existing_key_is_not_echoed_when_init_finds_it(
    cli: Cli, capsys: pytest.CaptureFixture[str]
) -> None:
    devkey.generate(cli.key_file)
    secrets = secrets_of(cli.key_file)
    result = run(capsys, "init")
    for secret in secrets:
        assert secret not in result.out
        assert secret not in result.err
