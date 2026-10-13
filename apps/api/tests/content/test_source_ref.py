"""The stable external key of an imported question (`question.source_ref`).

Written from the docstrings of `qlab.content.service` (`create_question`,
`find_question_by_source_ref`, `QuestionView`), migration 0004 and docs/pilot/IMPORT_RULES.md
section 2. No implementation was read.

Two layers: the service (which checks the form, refuses a second use of a key and audits the key)
and the database (unique, CHECK on the form, immutable because the question guard of migration 0002
only allows `syllabus_status` to change). The database tests use raw SQL and never call the content
service.
"""

from __future__ import annotations

import re
import threading
import uuid
from collections.abc import Callable, Iterator

import pytest
from alembic import command
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from qlab.content import service as svc
from qlab.content.schema import QuestionDocument
from qlab.rights import service as rights
from tests.conftest import LOCAL_HOSTS, alembic_config
from tests.content import samples
from tests.content.support import (
    AUTHOR,
    Env,
    approve,
    audit_actions,
    audit_for,
    create,
    data_text,
    document,
    make_env,
    new_rights,
    now,
    other_document,
    publish,
    raw_question,
    snapshot,
    table_counts,
    usable,
)

pytestmark = [pytest.mark.db, pytest.mark.node]

KEY = "pilot/demo-set#1"
OTHER_KEY = "pilot/demo-set#2"
FORM = re.compile(r"[a-z0-9][a-z0-9/_#.-]{0,199}")

INVALID_KEYS = [
    pytest.param("", id="empty"),
    pytest.param("Pilot/demo#1", id="upper_case"),
    pytest.param("pilot/demo set#1", id="space"),
    pytest.param(" pilot/demo#1", id="leading_space"),
    pytest.param("pilot/demo#1 ", id="trailing_space"),
    pytest.param("/pilot/demo#1", id="leading_slash"),
    pytest.param("-pilot", id="leading_hyphen"),
    pytest.param("_pilot", id="leading_underscore"),
    pytest.param("#1", id="leading_hash"),
    pytest.param(".hidden", id="leading_dot"),
    pytest.param("a" * 201, id="201_characters"),
    pytest.param("pilot/dem\u00f6#1", id="non_ascii_letter"),
    pytest.param("pilot/\u0430#1", id="cyrillic_look_alike"),
    pytest.param("pilot/demo#1\n", id="trailing_newline"),
    pytest.param("pilot/de\tmo", id="tab"),
    pytest.param("pilot/de:mo", id="colon"),
    pytest.param("pilot/de\\mo", id="backslash"),
    pytest.param("pilot/de*mo", id="asterisk"),
]
VALID_KEYS = [
    pytest.param("a", id="one_letter"),
    pytest.param("0", id="one_digit"),
    pytest.param("pilot/a1-kinematics#12", id="pilot_form"),
    pytest.param("a/_#.-", id="every_allowed_punctuation"),
    pytest.param("a" * 200, id="200_characters"),
]


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


def make(
    session: Session,
    env: Env,
    key: str | None,
    *,
    doc: QuestionDocument | None = None,
    origin: svc.Origin = svc.Origin.AUTHORED,
) -> svc.QuestionVersionView:
    return svc.create_question(
        session,
        actor=AUTHOR,
        document=doc if doc is not None else document(),
        rights_record_id=env.rights_record_id,
        syllabus_version_id=env.syllabus_version_id,
        origin=origin,
        source_ref=key,
    )


# =============================================================================================
# Service
# =============================================================================================


def test_a_key_is_stored_and_found_again(session: Session, env: Env) -> None:
    version = make(session, env, KEY)

    assert svc.get_question(session, version.question_id).source_ref == KEY
    found = svc.find_question_by_source_ref(session, KEY)
    assert found is not None
    assert found.id == version.question_id
    assert found.source_ref == KEY
    assert found.origin is svc.Origin.AUTHORED
    assert found.rights_record_id == env.rights_record_id
    assert found.syllabus_version_id == env.syllabus_version_id
    assert found.created_by == AUTHOR


def test_without_a_key_the_view_has_none_and_the_question_is_not_findable(
    session: Session, env: Env
) -> None:
    default = create(session, env)
    explicit = make(session, env, None)

    for version in (default, explicit):
        assert svc.get_question(session, version.question_id).source_ref is None
    assert svc.find_question_by_source_ref(session, "None") is None
    assert svc.find_question_by_source_ref(session, "") is None


def test_several_questions_may_have_no_key(session: Session, env: Env) -> None:
    first = make(session, env, None)
    second = make(session, env, None)

    assert first.question_id != second.question_id


def test_an_unknown_key_finds_nothing(session: Session, env: Env) -> None:
    make(session, env, KEY)

    assert svc.find_question_by_source_ref(session, OTHER_KEY) is None
    assert svc.find_question_by_source_ref(session, KEY.upper()) is None
    assert svc.find_question_by_source_ref(session, KEY + " ") is None


def test_each_key_finds_its_own_question(session: Session, env: Env) -> None:
    first = make(session, env, KEY)
    second = make(session, env, OTHER_KEY, doc=other_document())

    found_first = svc.find_question_by_source_ref(session, KEY)
    found_second = svc.find_question_by_source_ref(session, OTHER_KEY)
    assert found_first is not None and found_second is not None
    assert found_first.id == first.question_id
    assert found_second.id == second.question_id


def test_a_second_question_with_the_same_key_is_refused_and_writes_nothing(
    session: Session, connection: Connection, env: Env
) -> None:
    first = make(session, env, KEY)
    before = snapshot(session, connection, first.question_id)
    counts = table_counts(connection)
    audit_before = audit_actions(session, first.id)

    with pytest.raises(svc.DuplicateSourceRef):
        make(session, env, KEY, doc=other_document())

    assert snapshot(session, connection, first.question_id) == before
    assert table_counts(connection) == counts
    assert audit_actions(session, first.id) == audit_before
    found = svc.find_question_by_source_ref(session, KEY)
    assert found is not None and found.id == first.question_id
    usable(session)
    # the session carries on: another key can still be used
    assert make(session, env, OTHER_KEY).version_no == 1


def test_the_same_key_with_the_same_document_is_also_refused(session: Session, env: Env) -> None:
    make(session, env, KEY)

    with pytest.raises(svc.DuplicateSourceRef):
        make(session, env, KEY)


def test_a_key_stays_taken_after_its_rights_were_revoked(session: Session, env: Env) -> None:
    make(session, env, KEY)
    rights.revoke(session, env.rights_record_id, at=now())

    other_rights = new_rights(session)
    with pytest.raises(svc.DuplicateSourceRef):
        svc.create_question(
            session,
            actor=AUTHOR,
            document=document(),
            rights_record_id=other_rights,
            syllabus_version_id=env.syllabus_version_id,
            source_ref=KEY,
        )
    usable(session)


@pytest.mark.parametrize("key", INVALID_KEYS)
def test_an_invalid_key_raises_value_error_and_writes_nothing(
    session: Session, connection: Connection, env: Env, key: str
) -> None:
    counts = table_counts(connection)

    with pytest.raises(ValueError):  # noqa: PT011  # the contract names the type only
        make(session, env, key)

    assert table_counts(connection) == counts
    assert svc.find_question_by_source_ref(session, key) is None
    usable(session)


@pytest.mark.parametrize("key", VALID_KEYS)
def test_a_valid_key_is_accepted_and_found(session: Session, env: Env, key: str) -> None:
    version = make(session, env, key)

    assert svc.get_question(session, version.question_id).source_ref == key
    found = svc.find_question_by_source_ref(session, key)
    assert found is not None and found.id == version.question_id


def test_200_characters_are_accepted_and_201_are_not(session: Session, env: Env) -> None:
    make(session, env, "k" * 200)
    with pytest.raises(ValueError):  # noqa: PT011
        make(session, env, "k" * 201)


@settings(max_examples=60, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    key=st.text(
        alphabet=st.sampled_from(list("abcxyz019/_#.-AZ \n\t:\u00e4\u0430")), min_size=0, max_size=8
    ).filter(lambda value: FORM.fullmatch(value) is None)
)
def test_any_key_outside_the_documented_form_is_refused(
    session: Session, connection: Connection, env: Env, key: str
) -> None:
    counts = table_counts(connection)

    with pytest.raises(ValueError):  # noqa: PT011
        make(session, env, key)

    assert table_counts(connection) == counts


def test_the_creation_audit_entry_carries_the_key(session: Session, env: Env) -> None:
    version = make(session, env, KEY)

    entries = audit_for(session, version.id)
    assert [e.action for e in entries] == ["question_version.created"]
    assert entries[0].actor == AUTHOR
    assert KEY in data_text(entries[0])


def test_a_revoked_rights_record_hides_the_question_from_the_lookup(
    session: Session, env: Env
) -> None:
    version = make(session, env, KEY)
    assert svc.find_question_by_source_ref(session, KEY) is not None

    rights.revoke(session, env.rights_record_id, at=now())

    assert svc.find_question_by_source_ref(session, KEY) is None
    with pytest.raises(svc.NotFound):
        svc.get_question(session, version.question_id)


def test_a_question_whose_rights_do_not_permit_everyone_is_not_found_either(
    session: Session, env: Env
) -> None:
    closed = new_rights(session, scope=rights.DisplayScope.NONE)
    # such a record cannot be used to create a question, so build the row without the service
    question_id = uuid.uuid4()
    session.execute(
        text(
            "INSERT INTO question (id, origin, rights_record_id, syllabus_version_id, "
            "created_by, source_ref) VALUES (:id, 'authored', :r, :s, :by, :key)"
        ),
        {
            "id": question_id,
            "r": closed,
            "s": env.syllabus_version_id,
            "by": AUTHOR,
            "key": KEY,
        },
    )

    assert svc.find_question_by_source_ref(session, KEY) is None


def test_a_revision_keeps_the_key(session: Session, connection: Connection, env: Env) -> None:
    first = make(session, env, KEY)
    svc.submit(session, actor=AUTHOR, version_id=first.id)
    approve(session, first.id)
    publish(session, first.id)

    second = svc.start_revision(session, actor=AUTHOR, question_id=first.question_id)

    assert second.question_id == first.question_id
    assert second.version_no == 2
    assert svc.get_question(session, first.question_id).source_ref == KEY
    found = svc.find_question_by_source_ref(session, KEY)
    assert found is not None and found.id == first.question_id
    stored = connection.execute(
        text("SELECT source_ref FROM question WHERE id = :q"), {"q": first.question_id}
    ).scalar_one()
    assert stored == KEY


def test_updating_a_draft_keeps_the_key(session: Session, env: Env) -> None:
    first = make(session, env, KEY)

    svc.update_draft(session, actor=AUTHOR, version_id=first.id, document=other_document())

    assert svc.get_question(session, first.question_id).source_ref == KEY


# --- check order: the closed origin comes first -------------------------------------------------


@pytest.mark.parametrize("origin", [svc.Origin.GENERATED, svc.Origin.SOURCE_ORIGINAL])
def test_a_closed_origin_wins_over_a_bad_key(
    session: Session, connection: Connection, env: Env, origin: svc.Origin
) -> None:
    counts = table_counts(connection)

    with pytest.raises(svc.OriginClosed):
        make(session, env, "Not A Valid Key", origin=origin)

    assert table_counts(connection) == counts


def test_a_closed_origin_wins_over_a_taken_key(session: Session, env: Env) -> None:
    make(session, env, KEY)

    with pytest.raises(svc.OriginClosed):
        make(session, env, KEY, origin=svc.Origin.GENERATED)


def test_a_closed_origin_wins_over_everything_else_at_once(
    session: Session, connection: Connection, env: Env
) -> None:
    make(session, env, KEY)
    revoked = new_rights(session, revoked=True)
    broken = samples.data_based_document()
    broken["parts"][0]["command_term"] = "no_such_term"
    counts = table_counts(connection)

    with pytest.raises(svc.OriginClosed):
        svc.create_question(
            session,
            actor=AUTHOR,
            document=document(broken),
            rights_record_id=revoked,
            syllabus_version_id=uuid.uuid4(),
            origin=svc.Origin.GENERATED,
            source_ref=KEY,
        )

    assert table_counts(connection) == counts


# =============================================================================================
# Database (raw SQL)
# =============================================================================================

INSERT = text(
    "INSERT INTO question (id, origin, rights_record_id, syllabus_version_id, created_by, "
    "source_ref) VALUES (:id, 'authored', :r, :s, 'u_author', :key)"
)


def raw_keyed(connection: Connection, env: Env, key: str | None) -> uuid.UUID:
    question_id = uuid.uuid4()
    connection.execute(
        INSERT,
        {
            "id": question_id,
            "r": env.rights_record_id,
            "s": env.syllabus_version_id,
            "key": key,
        },
    )
    return question_id


def stored_key(connection: Connection, question_id: uuid.UUID) -> str | None:
    value = connection.execute(
        text("SELECT source_ref FROM question WHERE id = :q"), {"q": question_id}
    ).scalar_one()
    return None if value is None else str(value)


def test_the_column_defaults_to_null(connection: Connection, env: Env) -> None:
    question_id = raw_question(connection, env)

    assert stored_key(connection, question_id) is None


def test_a_second_row_with_the_same_key_violates_the_unique_constraint(
    connection: Connection, env: Env
) -> None:
    raw_keyed(connection, env, KEY)

    with pytest.raises(IntegrityError, match="uq_question_source_ref"), connection.begin_nested():
        raw_keyed(connection, env, KEY)

    count = connection.execute(
        text("SELECT count(*) FROM question WHERE source_ref = :k"), {"k": KEY}
    ).scalar_one()
    assert count == 1


def test_an_upper_case_twin_of_a_key_is_refused_by_the_form_check(
    connection: Connection, env: Env
) -> None:
    raw_keyed(connection, env, KEY)

    # an upper-case twin is refused by the form check, not accepted as a different key
    with pytest.raises(IntegrityError, match="ck_question_source_ref"), connection.begin_nested():
        raw_keyed(connection, env, KEY.upper())


def test_many_rows_may_have_a_null_key(connection: Connection, env: Env) -> None:
    ids = [raw_keyed(connection, env, None) for _ in range(3)]
    ids.append(raw_question(connection, env))

    assert all(stored_key(connection, i) is None for i in ids)


@pytest.mark.parametrize("key", INVALID_KEYS)
def test_the_check_constraint_rejects_the_invalid_forms(
    connection: Connection, env: Env, key: str
) -> None:
    with pytest.raises(IntegrityError, match="ck_question_source_ref"), connection.begin_nested():
        raw_keyed(connection, env, key)

    assert connection.execute(text("SELECT count(*) FROM question")).scalar_one() == 0


@pytest.mark.parametrize("key", VALID_KEYS)
def test_the_check_constraint_accepts_the_valid_forms(
    connection: Connection, env: Env, key: str
) -> None:
    question_id = raw_keyed(connection, env, key)

    assert stored_key(connection, question_id) == key


@pytest.mark.parametrize(
    ("start", "new"),
    [
        pytest.param(None, KEY, id="null_to_value"),
        pytest.param(KEY, OTHER_KEY, id="value_to_other_value"),
        pytest.param(KEY, None, id="value_to_null"),
    ],
)
def test_the_key_cannot_be_changed_after_creation(
    connection: Connection, env: Env, start: str | None, new: str | None
) -> None:
    question_id = raw_keyed(connection, env, start)

    with pytest.raises(DBAPIError) as caught, connection.begin_nested():
        connection.execute(
            text("UPDATE question SET source_ref = :k WHERE id = :q"),
            {"k": new, "q": question_id},
        )

    assert "only syllabus_status may change" in str(caught.value.orig)
    assert stored_key(connection, question_id) == start


def test_the_key_cannot_be_changed_together_with_syllabus_status(
    connection: Connection, env: Env
) -> None:
    question_id = raw_keyed(connection, env, KEY)

    with pytest.raises(DBAPIError) as caught, connection.begin_nested():
        connection.execute(
            text(
                "UPDATE question SET source_ref = :k, syllabus_status = 'out_of_syllabus' "
                "WHERE id = :q"
            ),
            {"k": OTHER_KEY, "q": question_id},
        )

    assert "only syllabus_status may change" in str(caught.value.orig)
    status = connection.execute(
        text("SELECT syllabus_status FROM question WHERE id = :q"), {"q": question_id}
    ).scalar_one()
    assert status != "out_of_syllabus"
    assert stored_key(connection, question_id) == KEY


def test_syllabus_status_still_updates_on_a_keyed_question(
    connection: Connection, env: Env
) -> None:
    question_id = raw_keyed(connection, env, KEY)

    connection.execute(
        text("UPDATE question SET syllabus_status = 'out_of_syllabus' WHERE id = :q"),
        {"q": question_id},
    )

    status = connection.execute(
        text("SELECT syllabus_status FROM question WHERE id = :q"), {"q": question_id}
    ).scalar_one()
    assert status == "out_of_syllabus"
    assert stored_key(connection, question_id) == KEY


# --- migration -------------------------------------------------------------------------------


def column_present(connection: Connection) -> bool:
    return bool(
        connection.execute(
            text(
                "SELECT count(*) FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = 'question' "
                "AND column_name = 'source_ref'"
            )
        ).scalar_one()
        == 1
    )


def constraint_names(connection: Connection) -> set[str]:
    rows = connection.execute(
        text("SELECT conname FROM pg_constraint WHERE conrelid = 'public.question'::regclass")
    ).all()
    return {str(name) for (name,) in rows}


def test_downgrade_to_0003_removes_the_column_and_both_constraints_and_upgrade_restores_them(
    engine: Engine,
) -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        config = alembic_config(connection)
        assert column_present(connection)
        assert {"uq_question_source_ref", "ck_question_source_ref"} <= constraint_names(connection)

        command.downgrade(config, "0003")

        assert not column_present(connection)
        assert not {"uq_question_source_ref", "ck_question_source_ref"} & constraint_names(
            connection
        )

        command.upgrade(config, "head")

        assert column_present(connection)
        assert {"uq_question_source_ref", "ck_question_source_ref"} <= constraint_names(connection)
        transaction.rollback()
    with engine.connect() as connection:
        assert column_present(connection)  # the rollback left the schema at head
        assert {"uq_question_source_ref", "ck_question_source_ref"} <= constraint_names(connection)


def test_the_restored_constraints_work_after_a_downgrade_and_upgrade(
    engine: Engine,
) -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        config = alembic_config(connection)
        command.downgrade(config, "0003")
        command.upgrade(config, "head")
        with Session(connection, join_transaction_mode="create_savepoint") as session:
            env = make_env(session)
            session.commit()
        raw_keyed(connection, env, KEY)
        with (
            pytest.raises(IntegrityError, match="uq_question_source_ref"),
            connection.begin_nested(),
        ):
            raw_keyed(connection, env, KEY)
        with (
            pytest.raises(IntegrityError, match="ck_question_source_ref"),
            connection.begin_nested(),
        ):
            raw_keyed(connection, env, "Bad Key")
        transaction.rollback()


def test_downgrade_to_0003_refuses_while_a_keyed_question_exists(engine: Engine) -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(connection, join_transaction_mode="create_savepoint") as session:
            env = make_env(session)
            session.commit()
        raw_keyed(connection, env, KEY)
        raw_keyed(connection, env, None)

        with pytest.raises(RuntimeError, match="source_ref"):
            command.downgrade(alembic_config(connection), "0003")

        assert column_present(connection)
        assert {"uq_question_source_ref", "ck_question_source_ref"} <= constraint_names(connection)
        assert stored_key(connection, raw_keyed_id(connection, KEY)) == KEY
        transaction.rollback()
    with engine.connect() as connection:
        assert column_present(connection)


def raw_keyed_id(connection: Connection, key: str) -> uuid.UUID:
    value = connection.execute(
        text("SELECT id FROM question WHERE source_ref = :k"), {"k": key}
    ).scalar_one()
    assert isinstance(value, uuid.UUID)
    return value


def test_downgrade_to_0003_still_removes_the_column_when_no_question_has_a_key(
    engine: Engine,
) -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(connection, join_transaction_mode="create_savepoint") as session:
            env = make_env(session)
            session.commit()
        unkeyed = raw_question(connection, env)
        raw_keyed(connection, env, None)

        command.downgrade(alembic_config(connection), "0003")

        assert not column_present(connection)
        assert not {"uq_question_source_ref", "ck_question_source_ref"} & constraint_names(
            connection
        )
        still_there = connection.execute(
            text("SELECT count(*) FROM question WHERE id = :q"), {"q": unkeyed}
        ).scalar_one()
        assert still_there == 1
        transaction.rollback()


# =============================================================================================
# Two writers with the same key (the key is serialised before it is checked)
# =============================================================================================

WAIT_BLOCKED = 1.5
WAIT_DONE = 20.0


@pytest.fixture(scope="module")
def aux_engine(engine: Engine) -> Iterator[Engine]:
    """A database of its own with a committed environment: these tests commit."""
    url = engine.url
    base = url.database
    if base is None or not re.fullmatch(r"[a-z0-9_]+_test", base) or url.host not in LOCAL_HOSTS:
        raise RuntimeError("refusing to create a second database next to a non-test database")
    name = f"{base}_key"
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


@pytest.fixture(scope="module")
def committed_env(aux_engine: Engine) -> Env:
    with Session(aux_engine) as setup:
        env = make_env(setup)
        setup.commit()
    return env


class Background:
    """Runs one call on its own session in a thread and keeps what it returned or raised."""

    def __init__(self, aux: Engine, call: Callable[[Session], object]) -> None:
        self.session = Session(aux)
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


def create_keyed(env: Env, key: str) -> Callable[[Session], object]:
    def call(session: Session) -> object:
        return svc.create_question(
            session,
            actor="u_second",
            document=other_document(),
            rights_record_id=env.rights_record_id,
            syllabus_version_id=env.syllabus_version_id,
            source_ref=key,
        )

    return call


def test_a_second_creator_of_the_same_key_waits_and_then_gets_duplicate_source_ref(
    aux_engine: Engine, committed_env: Env
) -> None:
    key = f"lock/{uuid.uuid4().hex}"
    first = Session(aux_engine)
    waiting: Background | None = None
    try:
        svc.create_question(
            first,
            actor=AUTHOR,
            document=document(),
            rights_record_id=committed_env.rights_record_id,
            syllabus_version_id=committed_env.syllabus_version_id,
            source_ref=key,
        )
        waiting = Background(aux_engine, create_keyed(committed_env, key))
        waiting.start()
        assert waiting.still_waiting(), "the second creator did not wait for the first one"
        first.commit()
        waiting.finish()
    finally:
        first.rollback()
        first.close()
        if waiting is not None:
            waiting.finish()

    assert isinstance(waiting.error, svc.DuplicateSourceRef), repr(waiting.error)
    assert not isinstance(waiting.error, IntegrityError)
    with Session(aux_engine) as check:
        found = svc.find_question_by_source_ref(check, key)
        assert found is not None and found.created_by == AUTHOR
        count_for_key = check.execute(
            text("SELECT count(*) FROM question WHERE source_ref = :k"), {"k": key}
        ).scalar_one()
        assert count_for_key == 1


def test_a_second_creator_succeeds_when_the_first_one_rolls_back(
    aux_engine: Engine, committed_env: Env
) -> None:
    key = f"lock/{uuid.uuid4().hex}"
    first = Session(aux_engine)
    waiting: Background | None = None
    try:
        svc.create_question(
            first,
            actor=AUTHOR,
            document=document(),
            rights_record_id=committed_env.rights_record_id,
            syllabus_version_id=committed_env.syllabus_version_id,
            source_ref=key,
        )
        waiting = Background(aux_engine, create_keyed(committed_env, key))
        waiting.start()
        assert waiting.still_waiting(), "the second creator did not wait for the first one"
        first.rollback()
        waiting.finish()
    finally:
        first.rollback()
        first.close()
        if waiting is not None:
            waiting.finish()

    assert waiting.error is None, repr(waiting.error)
    with Session(aux_engine) as check:
        found = svc.find_question_by_source_ref(check, key)
        assert found is not None and found.created_by == "u_second"


def test_creators_of_different_keys_do_not_wait_for_each_other(
    aux_engine: Engine, committed_env: Env
) -> None:
    first = Session(aux_engine)
    other: Background | None = None
    try:
        svc.create_question(
            first,
            actor=AUTHOR,
            document=document(),
            rights_record_id=committed_env.rights_record_id,
            syllabus_version_id=committed_env.syllabus_version_id,
            source_ref=f"lock/{uuid.uuid4().hex}",
        )
        other = Background(aux_engine, create_keyed(committed_env, f"lock/{uuid.uuid4().hex}"))
        other.start()
        other.finish()  # a creator that had to wait would hit the 20 s limit and fail below
    finally:
        first.rollback()
        first.close()
        if other is not None:
            other.finish()

    assert other.error is None, repr(other.error)
