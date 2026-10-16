"""The owner command `python -m qlab.api.admin invite` (M1-G slice 9, docs/slices/M1G-9-ACILIS.md
3.3 and 6.5). The command commits, so each test gets a database of its own, dropped afterwards."""

from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Iterator
from typing import Any

import pytest
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url

from qlab.api import admin
from tests.conftest import DEFAULT_TEST_URL, LOCAL_HOSTS, alembic_config

pytestmark = pytest.mark.db

LINK = re.compile(r"^(?P<base>\S+)/invite#(?P<code>[A-Za-z0-9_-]{43})$")


@pytest.fixture
def database(monkeypatch: pytest.MonkeyPatch) -> Iterator[URL]:
    base = make_url(os.environ.get("QLAB_TEST_DATABASE_URL", DEFAULT_TEST_URL))
    assert base.database is not None and base.host in LOCAL_HOSTS
    name = base.database.removesuffix("_test") + "_admincli_test"
    assert re.fullmatch(r"[a-z0-9_]+_test", name)
    root = create_engine(base.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with root.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    url = base.set(database=name)
    engine = create_engine(url)
    with engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
    engine.dispose()
    monkeypatch.setenv("QLAB_DATABASE_URL", url.render_as_string(hide_password=False))
    try:
        yield url
    finally:
        with root.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        root.dispose()


def rows(url: URL, sql: str) -> list[Any]:
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            return list(connection.execute(text(sql)).all())
    finally:
        engine.dispose()


def test_it_writes_an_invite_and_an_audit_entry(
    database: URL, capsys: pytest.CaptureFixture[str]
) -> None:
    code = admin.main(
        ["invite", "--role", "platform_admin", "--base-url", "https://qlab.example.invalid/"]
    )
    out = capsys.readouterr().out
    assert code == 0
    match = LINK.match(out.splitlines()[0])
    assert match is not None and match["base"] == "https://qlab.example.invalid"
    [(digest, role, created_by, max_uses)] = rows(
        database, "SELECT code_sha256, role, created_by, max_uses FROM invite"
    )
    assert digest == hashlib.sha256(match["code"].encode()).hexdigest()
    assert (role, created_by, max_uses) == ("platform_admin", "cli:owner", 1)
    [(actor, action, data)] = rows(database, "SELECT actor, action, data::text FROM audit_log")
    assert (actor, action) == ("cli:owner", "invite.created")
    assert match["code"] not in data
    assert "expires" in out
    [(days,)] = rows(
        database, "SELECT round(extract(epoch FROM expires_at - created_at) / 86400) FROM invite"
    )
    assert int(days) == 1  # the default is one day


def test_options(database: URL, capsys: pytest.CaptureFixture[str]) -> None:
    args = ["--role", "teacher", "--base-url", "http://localhost:3000"]
    assert admin.main(["invite", *args, "--expires-in-days", "2", "--max-uses", "5"]) == 0
    [(max_uses, days)] = rows(
        database,
        "SELECT max_uses, round(extract(epoch FROM expires_at - created_at) / 86400) FROM invite",
    )
    assert (max_uses, int(days)) == (5, 2)


@pytest.mark.parametrize(
    "base_url",
    [
        "http://qlab.example.com",
        "ftp://localhost",
        "localhost",
        "https://",
        "http://localhost.evil.com",
    ],
)
def test_an_insecure_base_url_is_refused(database: URL, base_url: str) -> None:
    with pytest.raises(SystemExit) as exit_:
        admin.main(["invite", "--role", "student", "--base-url", base_url])
    assert exit_.value.code == 2
    assert rows(database, "SELECT 1 FROM invite") == []


@pytest.mark.parametrize("role", ["org_admin", "nobody"])
def test_a_role_that_cannot_be_invited_is_refused(database: URL, role: str) -> None:
    with pytest.raises(SystemExit):
        admin.main(["invite", "--role", role, "--base-url", "https://qlab.example.invalid"])
    assert rows(database, "SELECT 1 FROM invite") == []


@pytest.mark.parametrize(
    "option", [["--expires-in-days", "0"], ["--expires-in-days", "31"], ["--max-uses", "201"]]
)
def test_out_of_range_options_are_refused(database: URL, option: list[str]) -> None:
    with pytest.raises(SystemExit):
        admin.main(
            ["invite", "--role", "student", "--base-url", "https://qlab.example.invalid", *option]
        )


def test_without_a_database_it_refuses(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("QLAB_DATABASE_URL", raising=False)
    code = admin.main(["invite", "--role", "student", "--base-url", "https://qlab.example.invalid"])
    assert code == 2
    assert "refused" in capsys.readouterr().err


@pytest.mark.parametrize("role", ["reviewer", "content_admin", "platform_admin"])
def test_a_staff_invite_for_many_people_is_refused(
    database: URL, capsys: pytest.CaptureFixture[str], role: str
) -> None:
    base = ["invite", "--role", role, "--base-url", "https://qlab.example.invalid"]
    assert admin.main([*base, "--max-uses", "6"]) == 2
    assert "refused" in capsys.readouterr().err
    assert rows(database, "SELECT 1 FROM invite") == []
    assert admin.main([*base, "--max-uses", "5"]) == 0


def test_a_student_invite_may_have_many_uses(database: URL) -> None:
    args = ["invite", "--role", "student", "--base-url", "https://qlab.example.invalid"]
    assert admin.main([*args, "--max-uses", "200"]) == 0
