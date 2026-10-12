"""Shared fixtures. Tests marked `db` run against a real PostgreSQL (docs/TESTING_STRATEGY.md).

The server comes from infra/local/compose.yaml locally and from a service container in CI.
Override the address with QLAB_TEST_DATABASE_URL. An unreachable database is a failure, not a
skip: integration tests that silently do not run prove nothing.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = API_ROOT.parents[1]
DEFAULT_TEST_URL = "postgresql+psycopg://qlab:qlab-local-only@127.0.0.1:54340/qlab_test"


def alembic_config(connection: Connection) -> Config:
    config = Config(str(API_ROOT / "alembic.ini"))
    config.attributes["connection"] = connection
    return config


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    """An engine on a freshly migrated, otherwise empty test database."""
    url = make_url(os.environ.get("QLAB_TEST_DATABASE_URL", DEFAULT_TEST_URL))
    name = url.database
    if name is None or not name.endswith("_test"):
        raise RuntimeError("the test database name must end in _test; it is dropped and recreated")
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    admin.dispose()
    engine = create_engine(url)
    with engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
    yield engine
    engine.dispose()


@pytest.fixture
def connection(engine: Engine) -> Iterator[Connection]:
    """A connection whose outer transaction is rolled back after the test."""
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            yield connection
        finally:
            transaction.rollback()


@pytest.fixture
def session(connection: Connection) -> Iterator[Session]:
    """A session inside the test's transaction. `session.commit()` only releases a savepoint,
    so nothing a test writes outlives it. After a statement fails, call `session.rollback()`."""
    with Session(connection, join_transaction_mode="create_savepoint") as session:
        yield session
