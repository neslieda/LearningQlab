"""The application's database role (infra/sql/app-role.sql, M1-G slice 9) and the start-up check
that refuses an over-privileged one outside the local environment.

The script is written for psql (`\\set`, `:'variable'`, `\\gexec`). There is no psql in the test
environment, so `run_psql_script` below carries out the same few constructs with the driver.
The role names are fixed in the script and roles belong to the whole server, so the names are
replaced with ones made for this test: the roles a developer already has are never touched.
"""

from __future__ import annotations

import re
import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker

from qlab.api.settings import StartupError, check_database_role
from tests.conftest import REPO_ROOT

pytestmark = pytest.mark.db

SCRIPT = REPO_ROOT / "infra" / "sql" / "app-role.sql"
APP_PASSWORD = "app-test-password"  # noqa: S105
BACKUP_PASSWORD = "backup-test-password"  # noqa: S105


def run_psql_script(engine: Engine, source: str, variables: dict[str, str]) -> None:
    """Run the script's constructs: comment lines, `\\set`, statements ending in `;`, and
    queries ending in `\\gexec` (each value of the first column is run as a statement)."""
    buffer: list[str] = []
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        for line in source.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(("--", "\\set")):
                continue
            for name, value in variables.items():
                line = line.replace(f":'{name}'", "'" + value.replace("'", "''") + "'")
            buffer.append(line)
            joined = "\n".join(buffer)
            if stripped.endswith("\\gexec"):
                query = joined.rsplit("\\gexec", 1)[0]
                for (statement,) in connection.exec_driver_sql(query.replace("%", "%%")).all():
                    connection.exec_driver_sql(statement.replace("%", "%%"))
                buffer = []
            elif stripped.endswith(";"):
                connection.exec_driver_sql(joined.replace("%", "%%"))
                buffer = []
    assert buffer == [], f"the script ends in the middle of a statement: {buffer}"


@dataclass
class Roles:
    owner: Engine
    app: Engine
    backup: Engine
    app_name: str
    backup_name: str


@pytest.fixture
def roles(throwaway_url: URL) -> Iterator[Roles]:
    tag = uuid.uuid4().hex[:8]
    app_name, backup_name = f"qlab_app_{tag}", f"qlab_backup_{tag}"
    source = SCRIPT.read_text()
    source = re.sub(r"\bqlab_app\b", app_name, source)
    source = re.sub(r"\bqlab_backup\b", backup_name, source)
    owner = create_engine(throwaway_url)
    run_psql_script(
        owner, source, {"app_password": APP_PASSWORD, "backup_password": BACKUP_PASSWORD}
    )
    app = create_engine(throwaway_url.set(username=app_name, password=APP_PASSWORD))
    backup = create_engine(throwaway_url.set(username=backup_name, password=BACKUP_PASSWORD))
    try:
        yield Roles(owner, app, backup, app_name, backup_name)
    finally:
        for engine in (app, backup):
            engine.dispose()
        owner.dispose()
        # The database is dropped by the fixture that made it; roles outlive it, so drop them
        # from the server's maintenance database once nothing is connected.
        # Runs before the database is dropped: take the roles' privileges there first.
        cleaner = create_engine(throwaway_url, isolation_level="AUTOCOMMIT")
        with cleaner.connect() as connection:
            for name in (app_name, backup_name):
                connection.execute(text(f'DROP OWNED BY "{name}"'))
        cleaner.dispose()
        root = create_engine(throwaway_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
        with root.connect() as connection:
            for name in (app_name, backup_name):
                connection.execute(text(f'DROP ROLE IF EXISTS "{name}"'))
        root.dispose()


def refused(engine: Engine, sql: str, *, because: str = "permission denied|must be owner") -> None:
    with pytest.raises(DBAPIError, match=because), engine.begin() as connection:
        connection.execute(text(sql))


def test_the_application_role_changes_data_but_not_structure(roles: Roles) -> None:
    with roles.app.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO account (id, issuer, subject) "
                "VALUES (gen_random_uuid(), 'https://i.invalid', 'someone')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO invite (id, code_sha256, role, created_by, expires_at, max_uses) "
                "VALUES (gen_random_uuid(), repeat('a', 64), 'student', 'cli:owner', "
                "now() + interval '1 day', 1)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO invite_redemption (invite_id, account_id) "
                "SELECT i.id, a.id FROM invite i, account a"
            )
        )
        connection.execute(text("UPDATE invite SET uses = 1"))
        assert connection.execute(text("SELECT count(*) FROM invite_redemption")).scalar_one() == 1
        # question: the rights and syllabus rows it needs are not worth building here, so the
        # statements match no row; privileges are checked all the same.
        connection.execute(text("INSERT INTO question SELECT * FROM question WHERE false"))
        connection.execute(text("UPDATE question SET source_ref = 'x' WHERE false"))
        connection.execute(text("DELETE FROM question WHERE false"))
        assert connection.execute(text("SELECT count(*) FROM question")).scalar_one() == 0
        connection.execute(text("DELETE FROM invite_redemption"))
        connection.execute(text("DELETE FROM invite"))
        connection.execute(text("DELETE FROM account"))
    refused(roles.app, "CREATE TABLE made_by_the_app (x int)")
    refused(roles.app, "ALTER TABLE audit_log DISABLE TRIGGER USER")
    refused(roles.app, "ALTER TABLE invite ADD COLUMN extra int")
    refused(roles.app, "DROP TABLE invite")
    refused(roles.app, "TRUNCATE audit_log")
    refused(roles.app, "SELECT * FROM alembic_version")


def test_the_application_role_appends_to_the_audit_log_but_cannot_change_it(roles: Roles) -> None:
    with roles.app.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO audit_log (id, actor, action, entity_type, entity_id, data) "
                "VALUES (gen_random_uuid(), 'system:test', 'x.y', 'x', 'z', '{}')"
            )
        )
        assert connection.execute(text("SELECT count(*) FROM audit_log")).scalar_one() == 1
    # The privilege is there; the guard trigger of the audit log is what refuses.
    refused(roles.app, "UPDATE audit_log SET actor = 'system:other'", because="audit_log")
    refused(roles.app, "DELETE FROM audit_log", because="audit_log")


def test_tables_the_owner_makes_later_are_covered(roles: Roles) -> None:
    with roles.owner.begin() as connection:
        connection.execute(text("CREATE TABLE made_later (id serial PRIMARY KEY, note text)"))
    with roles.app.begin() as connection:
        connection.execute(text("INSERT INTO made_later (note) VALUES ('a')"))  # and its sequence
        connection.execute(text("UPDATE made_later SET note = 'b'"))
        assert connection.execute(text("SELECT note FROM made_later")).scalar_one() == "b"
        connection.execute(text("DELETE FROM made_later"))
    with roles.backup.begin() as connection:
        assert connection.execute(text("SELECT count(*) FROM made_later")).scalar_one() == 0
    refused(roles.backup, "INSERT INTO made_later (note) VALUES ('a')")
    refused(roles.backup, "CREATE TABLE made_by_the_backup (x int)")


def test_the_start_up_check_accepts_the_application_role(roles: Roles) -> None:
    check_database_role(sessionmaker(roles.app))


def test_the_start_up_check_refuses_the_owner_role(roles: Roles) -> None:
    with pytest.raises(StartupError, match="owns audit_log"):
        check_database_role(sessionmaker(roles.owner))


def test_the_start_up_check_refuses_a_role_that_may_create_in_public(roles: Roles) -> None:
    with roles.owner.begin() as connection:
        connection.execute(text(f'GRANT CREATE ON SCHEMA public TO "{roles.app_name}"'))
    with pytest.raises(StartupError, match="create objects"):
        check_database_role(sessionmaker(roles.app))


def test_the_start_up_check_refuses_a_member_of_the_owner_role(roles: Roles) -> None:
    with roles.owner.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        owner_name = connection.execute(text("SELECT current_user")).scalar_one()
        # A role that inherits the owner's rights owns audit_log in effect.
        connection.execute(text(f'GRANT "{owner_name}" TO "{roles.app_name}"'))
    with pytest.raises(StartupError, match="owns audit_log"):
        check_database_role(sessionmaker(roles.app))


def test_an_unusable_connection_is_a_start_up_error() -> None:
    bad = create_engine(
        "postgresql+psycopg://nobody:x@127.0.0.1:1/none", connect_args={"connect_timeout": 2}
    )
    with pytest.raises(StartupError, match="cannot be checked"):
        check_database_role(sessionmaker(bad))
