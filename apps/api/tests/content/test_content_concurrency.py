"""Two real connections: writers on the same version or question must queue, not interleave.

These tests commit. Rows cannot be deleted from the question tables, so they run in a database of
their own that is created and dropped here, and no other test sees what they leave behind.
A blocked call is detected by waiting a short time and finding its thread still running; the
wait only makes the tests slower when the code is right, never flaky in the other direction
(a call that does not block finishes within milliseconds and fails the assertion).
"""

from __future__ import annotations

import re
import threading
from collections.abc import Callable, Iterator

import pytest
from alembic import command
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from qlab.content import service as svc
from tests.conftest import LOCAL_HOSTS, alembic_config
from tests.content.support import (
    Env,
    bring_to,
    make_env,
    other_document,
    stored_hash,
)

pytestmark = pytest.mark.db

WAIT_BLOCKED = 1.5
WAIT_DONE = 20.0
EDITOR = "u_editor"
SECOND = "u_second"


@pytest.fixture(scope="module")
def aux_engine(engine: Engine) -> Iterator[Engine]:
    url = engine.url
    base = url.database
    if base is None or not re.fullmatch(r"[a-z0-9_]+_test", base) or url.host not in LOCAL_HOSTS:
        raise RuntimeError("refusing to create a second database next to a non-test database")
    name = f"{base}_two"
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    aux = create_engine(url.set(database=name))
    with aux.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
    try:
        yield aux
    finally:
        aux.dispose()
        with admin.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        admin.dispose()


def committed(aux_engine: Engine, status: str) -> tuple[Env, svc.QuestionVersionView]:
    with Session(aux_engine) as setup:
        env = make_env(setup)
        version = bring_to(setup, setup.connection(), env, status)
        setup.commit()
    return env, version


class Background:
    """Runs one call on its own session in a thread and keeps what it returned or raised."""

    def __init__(self, aux_engine: Engine, call: Callable[[Session], object]) -> None:
        self.session = Session(aux_engine)
        self.result: object = None
        self.error: BaseException | None = None
        self._call = call
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        try:
            self.session.execute(text("SET lock_timeout = '20s'"))
            self.result = self._call(self.session)
            self.session.commit()
        except BaseException as error:  # noqa: BLE001  # whatever the call raises is the result
            self.error = error
            self.session.rollback()

    def start(self) -> None:
        self.thread.start()

    def still_waiting(self) -> bool:
        self.thread.join(timeout=WAIT_BLOCKED)
        return self.thread.is_alive()

    def finish(self) -> None:
        self.thread.join(timeout=WAIT_DONE)
        assert not self.thread.is_alive(), "the call never finished"
        self.session.close()


def test_a_second_writer_waits_for_an_uncommitted_edit_and_then_sees_it(aux_engine: Engine) -> None:
    _, version = committed(aux_engine, "needs_fix")
    editor = Session(aux_engine)
    waiting: Background | None = None
    try:
        svc.update_draft(editor, actor=EDITOR, version_id=version.id, document=other_document())
        waiting = Background(
            aux_engine, lambda s: svc.submit(s, actor=SECOND, version_id=version.id)
        )
        waiting.start()
        assert waiting.still_waiting(), "submit did not wait for the open edit of the same version"
        editor.commit()
        waiting.finish()
    finally:
        editor.rollback()
        editor.close()
        if waiting is not None:
            waiting.finish()

    assert waiting.error is None, waiting.error
    state = waiting.result
    assert isinstance(state, svc.VersionState)
    assert state.status is svc.VersionStatus.IN_REVIEW
    assert state.content_sha256 == svc.content_sha256(other_document())
    assert state.content_sha256 != version.content_sha256


def test_an_approval_waits_for_a_request_for_changes_and_is_then_refused(
    aux_engine: Engine,
) -> None:
    _, version = committed(aux_engine, "in_review")
    reviewer = Session(aux_engine)
    waiting: Background | None = None
    try:
        svc.request_changes(reviewer, actor=EDITOR, version_id=version.id, reason="fix the stem")
        waiting = Background(
            aux_engine,
            lambda s: svc.approve(
                s,
                actor=SECOND,
                version_id=version.id,
                expected_content_sha256=version.content_sha256,
            ),
        )
        waiting.start()
        assert waiting.still_waiting(), "approve did not wait for the open change on the version"
        reviewer.commit()
        waiting.finish()
    finally:
        reviewer.rollback()
        reviewer.close()
        if waiting is not None:
            waiting.finish()

    assert isinstance(waiting.error, svc.InvalidTransition), waiting.error
    with Session(aux_engine) as check:
        assert (
            check.execute(
                text("SELECT status FROM question_version WHERE id = :v"), {"v": version.id}
            ).scalar_one()
            == "needs_fix"
        )
        assert stored_hash(check, version.id) == version.content_sha256


def test_two_revisions_of_one_question_one_wins_and_the_other_is_told_so(
    aux_engine: Engine,
) -> None:
    _, version = committed(aux_engine, "published")
    first = Session(aux_engine)
    waiting: Background | None = None
    try:
        opened = svc.start_revision(first, actor=EDITOR, question_id=version.question_id)
        waiting = Background(
            aux_engine,
            lambda s: svc.start_revision(s, actor=SECOND, question_id=version.question_id),
        )
        waiting.start()
        assert waiting.still_waiting(), "the second start_revision did not wait for the first"
        first.commit()
        waiting.finish()
    finally:
        first.rollback()
        first.close()
        if waiting is not None:
            waiting.finish()

    assert opened.version_no == 2
    assert isinstance(waiting.error, svc.WorkingVersionExists), repr(waiting.error)
    with Session(aux_engine) as check:
        numbers = (
            check.execute(
                text(
                    "SELECT version_no FROM question_version WHERE question_id = :q "
                    "ORDER BY version_no"
                ),
                {"q": version.question_id},
            )
            .scalars()
            .all()
        )
        assert numbers == [1, 2]
