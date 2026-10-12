"""Migration 0002 refuses to be undone while questions exist (content is never dropped)."""

from __future__ import annotations

import pytest
from alembic import command
from sqlalchemy import Engine, inspect, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from tests.conftest import alembic_config
from tests.content.support import (
    make_env,
    raw_check,
    raw_question,
    raw_version,
    raw_walk,
    status_of,
)

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


def test_downgrade_to_0002_restores_the_two_code_rule_and_head_needs_three(
    engine: Engine,
) -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(connection, join_transaction_mode="create_savepoint") as session:
            env = make_env(session)
            session.commit()  # releases the savepoint; the outer transaction is rolled back below
        question_id = raw_question(connection, env)
        version_id = raw_version(connection, question_id)
        for code in ("schema_valid", "vocabulary_valid"):  # the two codes of revision 0002
            raw_check(connection, version_id, code, "critical", "passed")
        raw_walk(connection, version_id, "auto_checking")
        move = text("UPDATE question_version SET status = 'in_review' WHERE id = :v")

        with (
            pytest.raises(DBAPIError, match="a required check has not passed"),
            connection.begin_nested(),
        ):
            connection.execute(move, {"v": version_id})
        assert connection.execute(text("SELECT content_required_checks()")).scalar_one() == [
            "schema_valid",
            "vocabulary_valid",
            "math_renders",
        ]

        command.downgrade(alembic_config(connection), "0002")

        exists = connection.execute(
            text("SELECT to_regproc('public.content_required_checks')")
        ).scalar_one()
        assert exists is None
        connection.execute(move, {"v": version_id})  # two codes were enough at 0002
        assert status_of(connection, version_id) == "in_review"
        transaction.rollback()
    with engine.connect() as connection:
        assert connection.execute(
            text("SELECT to_regproc('public.content_required_checks') IS NOT NULL")
        ).scalar_one()
