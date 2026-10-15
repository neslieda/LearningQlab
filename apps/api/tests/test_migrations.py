"""The hand-written migrations and the models must describe the same database."""

from __future__ import annotations

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Connection, Engine, inspect

import qlab.audit.models
import qlab.content.models
import qlab.identity.models
import qlab.organizations.models
import qlab.rights.models
import qlab.syllabus.models  # noqa: F401
from qlab.database import Base
from tests.conftest import alembic_config

pytestmark = pytest.mark.db


def test_migrated_schema_matches_models(connection: Connection) -> None:
    context = MigrationContext.configure(connection, opts={"compare_server_default": True})
    assert compare_metadata(context, Base.metadata) == []


def test_downgrade_removes_everything_and_upgrade_restores_it(engine: Engine) -> None:
    with engine.begin() as connection:
        config = alembic_config(connection)
        command.downgrade(config, "base")
        assert inspect(connection).get_table_names() == ["alembic_version"]
        leftover = connection.exec_driver_sql(
            "SELECT proname FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
            "WHERE n.nspname = 'public'"
        ).all()
        assert leftover == []
        command.upgrade(config, "head")
        assert "audit_log" in inspect(connection).get_table_names()


def test_downgrade_refuses_to_drop_recorded_history(engine: Engine) -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        connection.exec_driver_sql(
            "INSERT INTO audit_log (id, actor, action, entity_type, entity_id) "
            "VALUES (gen_random_uuid(), 'system:test', 'thing.done', 'thing', '1')"
        )
        with pytest.raises(RuntimeError, match="audit_log is not empty"):
            command.downgrade(alembic_config(connection), "base")
        transaction.rollback()
    with engine.connect() as connection:
        assert "audit_log" in inspect(connection).get_table_names()
