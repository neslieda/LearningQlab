"""Migration 0002 refuses to be undone while questions exist (content is never dropped)."""

from __future__ import annotations

import pytest
from alembic import command
from sqlalchemy import Engine, inspect
from sqlalchemy.orm import Session

from tests.conftest import alembic_config
from tests.content.support import make_env, raw_question

pytestmark = pytest.mark.db


def test_downgrade_to_the_foundation_refuses_while_a_question_exists(engine: Engine) -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(connection, join_transaction_mode="create_savepoint") as session:
            env = make_env(session)
            raw_question(connection, env)
            with pytest.raises(RuntimeError, match="question is not empty"):
                command.downgrade(alembic_config(connection), "0001")
        transaction.rollback()
    with engine.connect() as connection:
        tables = set(inspect(connection).get_table_names())
        assert {"question", "question_version", "question_version_check"} <= tables


def test_downgrade_to_the_foundation_removes_the_content_tables_when_none_exist(
    engine: Engine,
) -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        config = alembic_config(connection)
        command.downgrade(config, "0001")
        tables = set(inspect(connection).get_table_names())
        assert "question" not in tables and "question_version" not in tables
        assert {"audit_log", "rights_record", "syllabus_node"} <= tables
        leftovers = connection.exec_driver_sql(
            "SELECT proname FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
            "WHERE n.nspname = 'public' AND left(proname, 8) = 'question'"
        ).all()
        assert leftovers == []
        pinned = connection.exec_driver_sql(
            "SELECT proname FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
            "WHERE n.nspname = 'public' AND p.proconfig IS NOT NULL"
        ).all()
        assert pinned == []  # the foundation functions get their search_path back as it was
        transaction.rollback()
