from __future__ import annotations

import os
import re
import uuid
from collections.abc import Iterator

import pytest
from alembic import command
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session

from tests.api.support import ApiHarness, make_harness
from tests.conftest import DEFAULT_TEST_URL, LOCAL_HOSTS, alembic_config


@pytest.fixture
def api(connection: Connection, session: Session) -> Iterator[ApiHarness]:
    """The application on this test's transaction (separation of duties off)."""
    harness = make_harness(connection, session)
    with harness.client:
        yield harness


@pytest.fixture
def throwaway_url() -> Iterator[URL]:
    """A migrated database made for one test and dropped after it, for tests that must commit
    (races, roles). Anything they leave behind, audit entries included, goes with it."""
    base = make_url(os.environ.get("QLAB_TEST_DATABASE_URL", DEFAULT_TEST_URL))
    assert base.database is not None and base.host in LOCAL_HOSTS
    name = f"{base.database.removesuffix('_test')}_tw{uuid.uuid4().hex[:8]}_test"
    assert re.fullmatch(r"[a-z0-9_]+_test", name)
    root = create_engine(base.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with root.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    url = base.set(database=name)
    try:
        engine = create_engine(url)
        with engine.begin() as connection:
            command.upgrade(alembic_config(connection), "head")
        engine.dispose()
        yield url
    finally:
        with root.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        root.dispose()


@pytest.fixture
def throwaway_engine(throwaway_url: URL) -> Iterator[Engine]:
    engine = create_engine(throwaway_url)
    yield engine
    engine.dispose()
