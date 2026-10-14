"""Role assignments: `grant`, `revoke`, `roles_of` and the database rules of the
`role_assignment` table (migration 0005), checked with raw SQL.

Default deny: an account has exactly the roles with an active assignment. Roles are revoked,
never deleted by the service; granting again after a revocation is a new row.
"""

from __future__ import annotations

import uuid

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from qlab.identity import service as identity
from qlab.organizations import service as organizations
from qlab.organizations.service import Role

pytestmark = pytest.mark.db

ISSUER = "https://issuer.example.invalid"
ACTOR = "system:test"
ACTOR_FORMS = ["system:dev-cli", "acc_01j9z3k4m5n6p7q8r9s0t1v2w3", "a", "A.b-c_d:e|f", "x" * 200]
BAD_ACTORS = [
    "",
    " ",
    "a b",
    " a",
    "a ",
    "a\n",
    "a/b",
    "a@b",
    "ünï",
    "a,b",
    "x" * 201,
    "a\tb",
    "a;b",
]
FIXTURE_SCOPE = settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=40
)


def make_account(session: Session) -> uuid.UUID:
    return identity.ensure_account(session, issuer=ISSUER, subject=f"u-{uuid.uuid4().hex}").id


def rows(
    connection: Connection, account_id: uuid.UUID, role: str | None = None
) -> list[tuple[object, ...]]:
    sql = (
        "SELECT role, granted_by, revoked_at, revoked_by FROM role_assignment WHERE account_id = :a"
    )
    params: dict[str, object] = {"a": account_id}
    if role:
        sql += " AND role = :r"
        params["r"] = role
    return [tuple(r) for r in connection.execute(text(sql + " ORDER BY created_at, id"), params)]


def rejected(connection: Connection, sql: str, **params: object) -> str:
    with pytest.raises(DBAPIError) as caught, connection.begin_nested():
        connection.execute(text(sql), params)
    return str(caught.value.orig)


INSERT = (
    "INSERT INTO role_assignment (id, account_id, role, granted_by, revoked_at, revoked_by) "
    "VALUES (gen_random_uuid(), :a, :role, :by, :at, :rby)"
)


def insert(connection: Connection, account_id: uuid.UUID, **overrides: object) -> None:
    params: dict[str, object] = {
        "a": account_id, "role": "student", "by": ACTOR, "at": None, "rby": None,
    }  # fmt: skip
    params.update(overrides)
    connection.execute(text(INSERT), params)


def insert_rejected(connection: Connection, account_id: uuid.UUID, **overrides: object) -> str:
    params: dict[str, object] = {
        "a": account_id, "role": "student", "by": ACTOR, "at": None, "rby": None,
    }  # fmt: skip
    params.update(overrides)
    return rejected(connection, INSERT, **params)


# --- the roles ----------------------------------------------------------------------------------


def test_the_role_names_are_the_six_of_the_domain_model() -> None:
    assert {r.value for r in Role} == {
        "student", "teacher", "org_admin", "reviewer", "content_admin", "platform_admin",
    }  # fmt: skip


# --- roles_of -----------------------------------------------------------------------------------


def test_a_new_account_has_no_roles(session: Session) -> None:
    assert organizations.roles_of(session, make_account(session)) == frozenset()


def test_an_unknown_account_has_no_roles(session: Session) -> None:
    assert organizations.roles_of(session, uuid.uuid4()) == frozenset()


def test_roles_of_returns_a_frozenset_of_roles(session: Session) -> None:
    account = make_account(session)
    organizations.grant(session, account_id=account, role=Role.REVIEWER, granted_by=ACTOR)
    roles = organizations.roles_of(session, account)
    assert isinstance(roles, frozenset)
    assert roles == {Role.REVIEWER}
    assert all(isinstance(r, Role) for r in roles)


# --- grant --------------------------------------------------------------------------------------


@pytest.mark.parametrize("role", list(Role))
def test_grant_gives_exactly_that_role(
    session: Session, connection: Connection, role: Role
) -> None:
    account = make_account(session)
    assert organizations.grant(session, account_id=account, role=role, granted_by=ACTOR) is True
    assert organizations.roles_of(session, account) == {role}
    assert rows(connection, account) == [(role.value, ACTOR, None, None)]


def test_a_grant_to_one_account_does_not_reach_another(session: Session) -> None:
    a, b = make_account(session), make_account(session)
    organizations.grant(session, account_id=a, role=Role.PLATFORM_ADMIN, granted_by=ACTOR)
    assert organizations.roles_of(session, b) == frozenset()


def test_granting_again_returns_false_and_writes_nothing(
    session: Session, connection: Connection
) -> None:
    account = make_account(session)
    assert organizations.grant(session, account_id=account, role=Role.REVIEWER, granted_by=ACTOR)
    assert not organizations.grant(
        session, account_id=account, role=Role.REVIEWER, granted_by="system:someone-else"
    )
    assert len(rows(connection, account)) == 1
    assert rows(connection, account)[0][1] == ACTOR  # the first grantor is kept


def test_several_roles_can_be_held_at_once(session: Session) -> None:
    account = make_account(session)
    for role in Role:
        assert organizations.grant(session, account_id=account, role=role, granted_by=ACTOR)
    assert organizations.roles_of(session, account) == set(Role)


@pytest.mark.parametrize("actor", ACTOR_FORMS)
def test_grant_accepts_audit_actor_forms(
    session: Session, connection: Connection, actor: str
) -> None:
    account = make_account(session)
    assert organizations.grant(session, account_id=account, role=Role.STUDENT, granted_by=actor)
    assert rows(connection, account)[0][1] == actor


@pytest.mark.parametrize("actor", BAD_ACTORS)
def test_grant_refuses_an_actor_that_is_not_an_opaque_identifier(
    session: Session, connection: Connection, actor: str
) -> None:
    account = make_account(session)
    with pytest.raises(ValueError):
        organizations.grant(session, account_id=account, role=Role.STUDENT, granted_by=actor)
    assert organizations.roles_of(session, account) == frozenset()
    assert rows(connection, account) == []


def test_grant_to_an_unknown_account_is_a_lookup_error(
    session: Session, connection: Connection
) -> None:
    ghost = uuid.uuid4()
    with pytest.raises(LookupError):
        organizations.grant(session, account_id=ghost, role=Role.STUDENT, granted_by=ACTOR)
    assert rows(connection, ghost) == []


def test_grant_of_an_unknown_role_is_refused(session: Session, connection: Connection) -> None:
    account = make_account(session)
    for bad in ("superuser", "admin", "Student", "", "platform-admin", "root"):
        with pytest.raises(ValueError):
            organizations.grant(session, account_id=account, role=bad, granted_by=ACTOR)  # type: ignore[arg-type]
    assert rows(connection, account) == []


def test_the_actor_is_checked_before_the_account_is_looked_up(session: Session) -> None:
    with pytest.raises(ValueError):
        organizations.grant(
            session, account_id=uuid.uuid4(), role=Role.STUDENT, granted_by="bad actor"
        )


# --- revoke -------------------------------------------------------------------------------------


def test_revoke_takes_the_role_away_and_keeps_the_row(
    session: Session, connection: Connection
) -> None:
    account = make_account(session)
    organizations.grant(session, account_id=account, role=Role.REVIEWER, granted_by=ACTOR)
    assert organizations.revoke(
        session, account_id=account, role=Role.REVIEWER, revoked_by="system:rev"
    )
    assert organizations.roles_of(session, account) == frozenset()
    [(role, granted_by, revoked_at, revoked_by)] = rows(connection, account)
    assert (role, granted_by, revoked_by) == ("reviewer", ACTOR, "system:rev")
    assert revoked_at is not None


def test_revoking_a_role_not_held_returns_false(session: Session, connection: Connection) -> None:
    account = make_account(session)
    assert not organizations.revoke(
        session, account_id=account, role=Role.REVIEWER, revoked_by=ACTOR
    )
    assert rows(connection, account) == []


def test_revoking_twice_returns_false_the_second_time(
    session: Session, connection: Connection
) -> None:
    account = make_account(session)
    organizations.grant(session, account_id=account, role=Role.TEACHER, granted_by=ACTOR)
    assert organizations.revoke(
        session, account_id=account, role=Role.TEACHER, revoked_by="system:first"
    )
    assert not organizations.revoke(
        session, account_id=account, role=Role.TEACHER, revoked_by="system:second"
    )
    assert rows(connection, account)[0][3] == "system:first"


def test_revoking_for_an_unknown_account_is_false(session: Session) -> None:
    assert not organizations.revoke(
        session, account_id=uuid.uuid4(), role=Role.STUDENT, revoked_by=ACTOR
    )


def test_revoking_one_role_leaves_the_others_and_other_accounts(session: Session) -> None:
    a, b = make_account(session), make_account(session)
    for account in (a, b):
        for role in (Role.STUDENT, Role.REVIEWER):
            organizations.grant(session, account_id=account, role=role, granted_by=ACTOR)
    organizations.revoke(session, account_id=a, role=Role.REVIEWER, revoked_by=ACTOR)
    assert organizations.roles_of(session, a) == {Role.STUDENT}
    assert organizations.roles_of(session, b) == {Role.STUDENT, Role.REVIEWER}


@pytest.mark.parametrize("actor", BAD_ACTORS)
def test_revoke_refuses_an_actor_that_is_not_an_opaque_identifier(
    session: Session, actor: str
) -> None:
    account = make_account(session)
    organizations.grant(session, account_id=account, role=Role.STUDENT, granted_by=ACTOR)
    with pytest.raises(ValueError):
        organizations.revoke(session, account_id=account, role=Role.STUDENT, revoked_by=actor)
    assert organizations.roles_of(session, account) == {Role.STUDENT}  # nothing was revoked


def test_revoke_of_an_unknown_role_is_refused(session: Session) -> None:
    account = make_account(session)
    organizations.grant(session, account_id=account, role=Role.STUDENT, granted_by=ACTOR)
    with pytest.raises(ValueError):
        organizations.revoke(session, account_id=account, role="superuser", revoked_by=ACTOR)  # type: ignore[arg-type]
    assert organizations.roles_of(session, account) == {Role.STUDENT}


# --- grant again after revoke -------------------------------------------------------------------


def test_regranting_after_a_revocation_is_a_new_row(
    session: Session, connection: Connection
) -> None:
    account = make_account(session)
    assert organizations.grant(
        session, account_id=account, role=Role.REVIEWER, granted_by="system:one"
    )
    assert organizations.revoke(
        session, account_id=account, role=Role.REVIEWER, revoked_by="system:two"
    )
    assert organizations.grant(
        session, account_id=account, role=Role.REVIEWER, granted_by="system:three"
    )
    assert organizations.roles_of(session, account) == {Role.REVIEWER}
    history = rows(connection, account, "reviewer")
    assert len(history) == 2
    assert [h[1] for h in history] == ["system:one", "system:three"]
    assert history[0][2] is not None and history[0][3] == "system:two"  # the old one stays revoked
    assert history[1][2] is None and history[1][3] is None
    assert not organizations.grant(
        session, account_id=account, role=Role.REVIEWER, granted_by=ACTOR
    )


def test_many_grant_revoke_cycles_leave_one_active_row(
    session: Session, connection: Connection
) -> None:
    account = make_account(session)
    for _ in range(5):
        assert organizations.grant(session, account_id=account, role=Role.STUDENT, granted_by=ACTOR)
        assert organizations.revoke(
            session, account_id=account, role=Role.STUDENT, revoked_by=ACTOR
        )
    assert organizations.grant(session, account_id=account, role=Role.STUDENT, granted_by=ACTOR)
    history = rows(connection, account)
    assert len(history) == 6
    assert sum(1 for h in history if h[2] is None) == 1
    assert organizations.roles_of(session, account) == {Role.STUDENT}


Operation = st.tuples(st.sampled_from(["grant", "revoke"]), st.sampled_from(list(Role)))


@FIXTURE_SCOPE
@given(st.lists(Operation, max_size=25))
def test_roles_follow_the_sequence_of_grants_and_revocations(
    session: Session, connection: Connection, operations: list[tuple[str, Role]]
) -> None:
    account = make_account(session)
    held: set[Role] = set()
    for action, role in operations:
        if action == "grant":
            assert organizations.grant(
                session, account_id=account, role=role, granted_by=ACTOR
            ) == (role not in held)
            held.add(role)
        else:
            assert organizations.revoke(
                session, account_id=account, role=role, revoked_by=ACTOR
            ) == (role in held)
            held.discard(role)
        assert organizations.roles_of(session, account) == held
    active = [r for r in rows(connection, account) if r[2] is None]
    assert sorted(str(r[0]) for r in active) == sorted(r.value for r in held)


# --- the table's own rules (migration 0005) ------------------------------------------------------


@pytest.mark.parametrize("role", [r.value for r in Role])
def test_the_database_accepts_each_role(
    session: Session, connection: Connection, role: str
) -> None:
    insert(connection, make_account(session), role=role)


@pytest.mark.parametrize(
    "role",
    [
        "",
        "admin",
        "Student",
        "STUDENT",
        "student ",
        " student",
        "superuser",
        "platform-admin",
        "root",
        "owner",
    ],
)
def test_the_database_refuses_an_unknown_role(
    session: Session, connection: Connection, role: str
) -> None:
    assert "ck_role_assignment_role" in insert_rejected(
        connection, make_account(session), role=role
    )


@pytest.mark.parametrize("actor", BAD_ACTORS)
def test_the_database_refuses_a_granted_by_that_is_not_an_actor(
    session: Session, connection: Connection, actor: str
) -> None:
    assert "ck_role_assignment_granted_by" in insert_rejected(
        connection, make_account(session), by=actor
    )


@pytest.mark.parametrize("actor", ACTOR_FORMS)
def test_the_database_accepts_actor_forms(
    session: Session, connection: Connection, actor: str
) -> None:
    insert(connection, make_account(session), by=actor)


def test_granted_by_is_required(session: Session, connection: Connection) -> None:
    rejected(
        connection, INSERT, a=make_account(session), role="student", by=None, at=None, rby=None
    )


def test_the_database_allows_one_active_assignment_per_account_and_role(
    session: Session, connection: Connection
) -> None:
    account = make_account(session)
    insert(connection, account)
    message = insert_rejected(connection, account)
    assert "uq_role_assignment_one_active" in message


def test_the_same_role_for_another_account_or_another_role_for_the_same_account_is_fine(
    session: Session, connection: Connection
) -> None:
    a, b = make_account(session), make_account(session)
    insert(connection, a, role="student")
    insert(connection, b, role="student")
    insert(connection, a, role="teacher")


def test_revoked_rows_do_not_count_against_the_unique_rule(
    session: Session, connection: Connection
) -> None:
    account = make_account(session)
    for _ in range(3):
        insert(connection, account, at="2030-01-01T00:00:00Z", rby=ACTOR)
    insert(connection, account)  # one active beside any number of revoked
    assert "uq_role_assignment_one_active" in insert_rejected(connection, account)


def test_revoking_the_active_row_frees_the_slot(session: Session, connection: Connection) -> None:
    account = make_account(session)
    insert(connection, account)
    connection.execute(
        text(
            "UPDATE role_assignment SET revoked_at = now(), revoked_by = :by "
            "WHERE account_id = :a AND revoked_at IS NULL"
        ),
        {"a": account, "by": ACTOR},
    )
    insert(connection, account)


def test_revoked_at_and_revoked_by_come_together(session: Session, connection: Connection) -> None:
    account = make_account(session)
    assert "ck_role_assignment_revoked" in insert_rejected(
        connection, account, at="2030-01-01T00:00:00Z", rby=None
    )
    assert "ck_role_assignment_revoked" in insert_rejected(connection, account, at=None, rby=ACTOR)
    insert(connection, account, at="2030-01-01T00:00:00Z", rby=ACTOR)  # both: fine
    insert(connection, account, role="teacher")  # neither: fine


@pytest.mark.parametrize("actor", BAD_ACTORS)
def test_revoked_by_must_be_an_actor_too(
    session: Session, connection: Connection, actor: str
) -> None:
    message = insert_rejected(
        connection, make_account(session), at="2030-01-01T00:00:00Z", rby=actor
    )
    assert "ck_role_assignment_revoked" in message


def test_an_assignment_needs_an_existing_account(connection: Connection) -> None:
    message = insert_rejected(connection, uuid.uuid4())
    assert "fk_role_assignment_account_id_account" in message


def test_a_role_cannot_be_left_empty(session: Session, connection: Connection) -> None:
    rejected(connection, INSERT, a=make_account(session), role=None, by=ACTOR, at=None, rby=None)
    rejected(connection, INSERT, a=None, role="student", by=ACTOR, at=None, rby=None)


def test_assignments_and_the_account_can_be_erased_on_request(
    session: Session, connection: Connection
) -> None:
    """Docs/SECURITY.md 5.4: no delete guard; the lasting record is the audit log."""
    account = make_account(session)
    insert(connection, account, role="student")
    insert(connection, account, role="reviewer", at="2030-01-01T00:00:00Z", rby=ACTOR)
    rejected(connection, "DELETE FROM account WHERE id = :a", a=account)  # rows still reference it
    connection.execute(text("DELETE FROM role_assignment WHERE account_id = :a"), {"a": account})
    connection.execute(text("DELETE FROM account WHERE id = :a"), {"a": account})
    assert rows(connection, account) == []
    assert identity.get_account(session, account) is None
    assert organizations.roles_of(session, account) == frozenset()


def test_the_service_never_deletes_assignment_rows(
    session: Session, connection: Connection
) -> None:
    account = make_account(session)
    organizations.grant(session, account_id=account, role=Role.STUDENT, granted_by=ACTOR)
    organizations.revoke(session, account_id=account, role=Role.STUDENT, revoked_by=ACTOR)
    assert len(rows(connection, account)) == 1


def test_a_disabled_account_keeps_its_assignments(session: Session) -> None:
    """Disabling is an authentication matter; the role table is not touched."""
    account = make_account(session)
    organizations.grant(session, account_id=account, role=Role.STUDENT, granted_by=ACTOR)
    identity.disable_account(session, account)
    assert organizations.roles_of(session, account) == {Role.STUDENT}
