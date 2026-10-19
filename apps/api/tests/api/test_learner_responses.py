"""Stored learner answers (M1-G slice 8, D-66; docs/slices/M1G-8-OGRENCI.md sections 2, 3 and 5):
the row, the version binding, the cap of 200, `GET /v1/me/responses` and
`DELETE /v1/me/responses`. The answers endpoint itself is tested in test_learner_answers.py.
"""

from __future__ import annotations

import threading
import uuid
from typing import Any

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from qlab.api import ids
from qlab.attempts import service as attempts
from qlab.attempts.models import MAX_ANSWERS_PER_QUESTION
from qlab.content import service as svc
from qlab.identity import service as identity
from qlab.organizations.service import Role
from tests.api.support import ALL_ROLES, ApiHarness
from tests.api.test_learner_answers import (
    ENGLISH,
    answer,
    assert_problem,
    mcq_answer,
    written_answer,
)
from tests.api.test_learner_view import (
    STAFF,
    Published,
    assert_not_found,
    publish_document,
    qid,
    structured_without_figure,
    vid,
)
from tests.content import samples
from tests.content.support import Env, approve, make_env, publish

pytestmark = [pytest.mark.db, pytest.mark.node]

Json = dict[str, Any]
COLUMNS = {
    "id",
    "account_id",
    "question_version_id",
    "part_id",
    "kind",
    "payload",
    "correct",
    "created_at",
}


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


@pytest.fixture
def world(api: ApiHarness, env: Env) -> dict[str, Published]:
    return {
        "mcq": publish_document(api.session, env, samples.plain_mcq_document(), tag="zzr0x"),
        "other_mcq": publish_document(api.session, env, samples.mcq_document(), tag="zzr1x"),
        "written": publish_document(api.session, env, structured_without_figure(), tag="zzr2x"),
    }


def rows(api: ApiHarness) -> list[Any]:
    api.session.flush()
    return list(
        api.session.connection().execute(
            text(
                "SELECT id, account_id, question_version_id, part_id, kind, payload, correct, "
                "created_at FROM response ORDER BY id"
            )
        )
    )


def listing(api: ApiHarness, *roles: Role, **params: Any) -> Any:
    return api.client.get(
        "/v1/me/responses", params=params, headers=api.headers(*roles or (Role.STUDENT,))
    )


def erase(api: ApiHarness, *roles: Role) -> Any:
    return api.client.delete("/v1/me/responses", headers=api.headers(*roles or (Role.STUDENT,)))


def audit_rows(api: ApiHarness, action: str) -> list[Any]:
    api.session.flush()
    return list(
        api.session.connection().execute(
            text("SELECT actor, entity_type, entity_id, data FROM audit_log WHERE action = :a"),
            {"a": action},
        )
    )


# --- the stored row -----------------------------------------------------------------------------


def test_the_table_has_no_personal_columns(api: ApiHarness) -> None:
    found = {
        row[0]
        for row in api.session.connection().execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = 'response'"
            )
        )
    }
    assert found == COLUMNS  # no name, e-mail, address, device or timing column


def test_an_mcq_answer_is_one_row(api: ApiHarness, world: dict[str, Published]) -> None:
    item = world["mcq"]  # the right option is C
    body = answer(api, item.id, mcq_answer("A")).json()

    (row,) = rows(api)
    assert ids.encode(ids.RESPONSE, row.id) == body["response_id"]
    assert row.account_id == api.account(Role.STUDENT)
    assert row.question_version_id == item.view.id
    assert (row.kind, row.part_id, row.correct) == ("mcq", None, False)
    assert row.payload == {"selected_key": "A"}
    assert row.created_at is not None

    answer(api, item.id, mcq_answer("C"))
    assert [r.correct for r in rows(api)].count(True) == 1


def test_a_written_answer_is_one_row(api: ApiHarness, world: dict[str, Published]) -> None:
    item = world["written"]
    body = answer(api, item.id, written_answer("p-a", f"  {ENGLISH}  ")).json()

    (row,) = rows(api)
    assert ids.encode(ids.RESPONSE, row.id) == body["response_id"]
    assert (row.kind, row.part_id, row.correct) == ("written", "p-a", None)
    assert row.question_version_id == item.view.id
    assert set(row.payload) == {"text"}
    assert row.payload["text"].strip() == ENGLISH


def test_the_row_holds_nothing_but_the_answer_and_opaque_ids(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["written"]
    response = api.client.post(
        f"/v1/questions/{item.id}/answers",
        json=written_answer("p-a"),
        headers={
            **api.headers(Role.STUDENT),
            "User-Agent": "zzagentneedle",
            "X-Forwarded-For": "203.0.113.77",
        },
    )
    assert response.status_code == 201
    (row,) = rows(api)
    stored = " ".join(str(value) for value in row)
    for needle in ("zzagentneedle", "203.0.113.77", api.subject(Role.STUDENT)):
        assert needle not in stored


def test_the_answer_stays_bound_to_the_version_after_a_revision_is_published(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["mcq"]
    answer(api, item.id, mcq_answer("A"))
    (before,) = rows(api)
    assert before.question_version_id == item.view.id

    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)
    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    approve(api.session, revision.id, actor=STAFF)
    publish(api.session, revision.id, actor=STAFF)

    (after,) = rows(api)
    assert after.question_version_id == item.view.id  # not the new version
    assert after.payload == before.payload and after.correct == before.correct
    body = answer(api, item.id, mcq_answer("A")).json()
    assert body["version_id"] == vid(revision)
    assert sorted(r.question_version_id for r in rows(api)) == sorted([item.view.id, revision.id])

    shown = {i["id"]: i["version_id"] for i in listing(api).json()["items"]}
    assert shown[ids.encode(ids.RESPONSE, before.id)] == vid(item.view)
    assert shown[body["response_id"]] == vid(revision)


# --- the cap of 200 ---------------------------------------------------------------------------


def fill(api: ApiHarness, version_id: uuid.UUID, account_id: uuid.UUID, count: int) -> None:
    for _ in range(count):
        attempts.add_response(
            api.session,
            account_id=account_id,
            question_version_id=version_id,
            kind="mcq",
            part_id=None,
            payload={"selected_key": "A"},
            correct=False,
        )


def test_the_cap_is_two_hundred() -> None:
    assert MAX_ANSWERS_PER_QUESTION == 200


def test_the_two_hundred_and_first_answer_is_429(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["mcq"]
    student = api.account(Role.STUDENT)
    fill(api, item.view.id, student, MAX_ANSWERS_PER_QUESTION - 1)

    assert answer(api, item.id, mcq_answer("A")).status_code == 201  # the 200th
    response = answer(api, item.id, mcq_answer("A"))
    assert_problem(response, 429, "too_many_answers")
    assert len(rows(api)) == MAX_ANSWERS_PER_QUESTION
    assert answer(api, item.id, written_answer("p-a")).status_code == 422  # still a misfit


def test_the_counter_belongs_to_the_account_and_the_question(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["mcq"]
    fill(api, item.view.id, api.account(Role.STUDENT), MAX_ANSWERS_PER_QUESTION)
    assert_problem(answer(api, item.id, mcq_answer("A")), 429, "too_many_answers")

    # Another question of the same account.
    assert answer(api, world["other_mcq"].id, mcq_answer("A")).status_code == 201
    assert answer(api, world["written"].id, written_answer("p-a")).status_code == 201
    # The same question, another account (any role).
    for role in ALL_ROLES:
        if role is not Role.STUDENT:
            assert answer(api, item.id, mcq_answer("A"), role).status_code == 201


def test_the_counter_counts_every_version_of_the_question(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["mcq"]
    fill(api, item.view.id, api.account(Role.STUDENT), MAX_ANSWERS_PER_QUESTION)
    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)
    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    approve(api.session, revision.id, actor=STAFF)
    publish(api.session, revision.id, actor=STAFF)

    assert_problem(answer(api, item.id, mcq_answer("A")), 429, "too_many_answers")


def test_deleting_the_answers_frees_the_counter(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["mcq"]
    fill(api, item.view.id, api.account(Role.STUDENT), MAX_ANSWERS_PER_QUESTION)
    assert erase(api).json() == {"deleted": MAX_ANSWERS_PER_QUESTION}
    assert answer(api, item.id, mcq_answer("A")).status_code == 201


def test_concurrent_submissions_cannot_pass_the_cap(throwaway_engine: Engine) -> None:
    factory = sessionmaker(bind=throwaway_engine)
    with factory() as session, session.begin():
        env = make_env(session)
        item = publish_document(
            session, env, samples.plain_mcq_document(), tag="zzrace", plant=False
        )
        account = identity.ensure_account(
            session, issuer="https://issuer.example.invalid", subject="racer"
        )
        for _ in range(MAX_ANSWERS_PER_QUESTION - 5):
            attempts.add_response(
                session,
                account_id=account.id,
                question_version_id=item.view.id,
                kind="mcq",
                part_id=None,
                payload={"selected_key": "B"},
                correct=False,
            )
    workers = 16
    barrier = threading.Barrier(workers)
    results: list[Any] = [None] * workers

    def go(index: int) -> None:
        barrier.wait(timeout=30)
        try:
            with factory() as session, session.begin():
                attempts.add_response(
                    session,
                    account_id=account.id,
                    question_version_id=item.view.id,
                    kind="mcq",
                    part_id=None,
                    payload={"selected_key": "B"},
                    correct=False,
                )
            results[index] = "stored"
        except attempts.TooManyAnswers:
            results[index] = "refused"
        except Exception as error:  # noqa: BLE001 - the test reports what happened
            results[index] = error

    threads = [threading.Thread(target=go, args=(i,)) for i in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)

    assert sorted(map(str, results)) == ["refused"] * (workers - 5) + ["stored"] * 5, results
    with throwaway_engine.connect() as connection:
        stored = connection.execute(text("SELECT count(*) FROM response")).scalar_one()
    assert stored == MAX_ANSWERS_PER_QUESTION


# --- GET /v1/me/responses ---------------------------------------------------------------------


def test_the_list_is_empty_before_the_first_answer(api: ApiHarness) -> None:
    response = listing(api)
    assert response.status_code == 200
    assert response.json() == {"items": [], "next_cursor": None}


def test_the_list_shows_each_answer_newest_first(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    first = answer(api, world["mcq"].id, mcq_answer("A")).json()
    second = answer(api, world["written"].id, written_answer("p-b", "34 m/s")).json()
    third = answer(api, world["mcq"].id, mcq_answer("C")).json()

    body = listing(api).json()

    assert [i["id"] for i in body["items"]] == [
        third["response_id"],
        second["response_id"],
        first["response_id"],
    ]
    assert body["next_cursor"] is None
    one, two, three = reversed(body["items"])
    assert one == {
        "id": first["response_id"],
        "question_id": world["mcq"].id,
        "version_id": vid(world["mcq"].view),
        "kind": "mcq",
        "part_id": None,
        "selected_key": "A",
        "text": None,
        "correct": False,
        "created_at": one["created_at"],
    }
    assert two["kind"] == "written" and two["part_id"] == "p-b" and two["text"] == "34 m/s"
    assert two["selected_key"] is None and two["correct"] is None
    assert three["correct"] is True
    assert one["created_at"] <= two["created_at"] <= three["created_at"]


def test_the_list_pages_with_a_cursor(api: ApiHarness, world: dict[str, Published]) -> None:
    sent = [answer(api, world["mcq"].id, mcq_answer("B")).json()["response_id"] for _ in range(5)]

    seen: list[str] = []
    cursor: str | None = None
    for expected in (2, 2, 1):
        params: Json = {"limit": 2}
        if cursor:
            params["cursor"] = cursor
        body = listing(api, **params).json()
        assert len(body["items"]) == expected
        seen += [i["id"] for i in body["items"]]
        cursor = body["next_cursor"]
    assert cursor is None
    assert seen == list(reversed(sent))


def test_an_exact_page_has_no_next_cursor(api: ApiHarness, world: dict[str, Published]) -> None:
    for _ in range(2):
        answer(api, world["mcq"].id, mcq_answer("B"))
    assert listing(api, limit=2).json()["next_cursor"] is None


def test_the_list_can_be_narrowed_to_one_question(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    mine = answer(api, world["mcq"].id, mcq_answer("A")).json()["response_id"]
    answer(api, world["other_mcq"].id, mcq_answer("A"))
    answer(api, world["written"].id, written_answer("p-a"))

    body = listing(api, question_id=world["mcq"].id).json()
    assert [i["id"] for i in body["items"]] == [mine]
    assert len(listing(api).json()["items"]) == 3
    unknown = ids.encode(ids.QUESTION, uuid.uuid4())
    assert listing(api, question_id=unknown).json()["items"] == []


def test_the_filter_follows_the_question_across_versions(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["mcq"]
    first = answer(api, item.id, mcq_answer("A")).json()["response_id"]
    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)
    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    approve(api.session, revision.id, actor=STAFF)
    publish(api.session, revision.id, actor=STAFF)
    second = answer(api, item.id, mcq_answer("A")).json()["response_id"]

    assert [i["id"] for i in listing(api, question_id=item.id).json()["items"]] == [second, first]


def test_a_malformed_filter_or_cursor_or_limit_is_refused(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    answer(api, world["mcq"].id, mcq_answer("A"))
    assert_not_found(listing(api, question_id="q_notanidentifier"))
    assert_not_found(listing(api, question_id=vid(world["mcq"].view)))
    for cursor in ("rsp_", "nonsense", ids.encode(ids.QUESTION, uuid.uuid4())):
        assert_problem(listing(api, cursor=cursor), 422, "invalid_cursor")
    for limit in (0, 101, -1):
        assert_problem(listing(api, limit=limit), 422, "validation_failed")
    assert listing(api, limit=100).status_code == 200


def test_the_list_holds_only_the_callers_answers(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    sent: dict[Role, set[str]] = {}
    for role in ALL_ROLES:
        sent[role] = {
            answer(api, world["mcq"].id, mcq_answer("A"), role).json()["response_id"],
            answer(
                api, world["written"].id, written_answer("p-a", f"by {role.value}"), role
            ).json()["response_id"],
        }
    for role in ALL_ROLES:  # staff and teachers are no exception
        body = listing(api, role).json()
        assert {i["id"] for i in body["items"]} == sent[role], role
        assert not [i for i in body["items"] if i["text"] and role.value not in i["text"]]
        others = {r.value for r in ALL_ROLES if r is not role}
        assert not [i for i in body["items"] if i["text"] and i["text"][3:] in others]


def test_naming_another_accounts_row_reaches_nothing(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    answer(api, world["mcq"].id, mcq_answer("A"), Role.TEACHER)
    # There is no parameter that names an account; an unknown one is ignored or refused.
    other = api.actor(Role.TEACHER)
    for params in ({"account_id": other}, {"account": other}, {"actor": other}):
        body = listing(api, Role.STUDENT, **params)
        assert body.status_code in (200, 422)
        if body.status_code == 200:
            assert body.json()["items"] == []


def test_the_list_needs_a_token_and_a_role(api: ApiHarness) -> None:
    assert_problem(api.client.get("/v1/me/responses"), 401, "unauthenticated")
    assert_not_found(api.client.get("/v1/me/responses", headers=api.headers()))
    assert_problem(api.client.delete("/v1/me/responses"), 401, "unauthenticated")
    assert_not_found(api.client.delete("/v1/me/responses", headers=api.headers()))


def test_the_list_leaks_nothing_of_the_author(api: ApiHarness, world: dict[str, Published]) -> None:
    secrets = [s for item in world.values() for s in item.sentinels.all()]
    answer(api, world["mcq"].id, mcq_answer("A"))
    answer(api, world["written"].id, written_answer("p-a"))
    text_ = listing(api).text.lower()
    for sentinel in secrets:
        assert sentinel.lower() not in text_


# --- DELETE /v1/me/responses --------------------------------------------------------------------


def test_delete_removes_only_the_callers_rows_and_counts_them(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    for _ in range(3):
        answer(api, world["mcq"].id, mcq_answer("A"))
    answer(api, world["written"].id, written_answer("p-a"))
    answer(api, world["mcq"].id, mcq_answer("A"), Role.TEACHER)
    answer(api, world["mcq"].id, mcq_answer("A"), Role.REVIEWER)

    response = erase(api)

    assert response.status_code == 200
    assert response.json() == {"deleted": 4}
    assert listing(api).json()["items"] == []
    left = {r.account_id for r in rows(api)}
    assert left == {api.account(Role.TEACHER), api.account(Role.REVIEWER)}
    assert len(listing(api, Role.TEACHER).json()["items"]) == 1
    assert erase(api).json() == {"deleted": 0}


@pytest.mark.parametrize("role", ALL_ROLES)
def test_every_role_deletes_only_its_own_answers(
    api: ApiHarness, world: dict[str, Published], role: Role
) -> None:
    for each in ALL_ROLES:
        answer(api, world["mcq"].id, mcq_answer("A"), each)

    assert erase(api, role).json() == {"deleted": 1}

    assert {r.account_id for r in rows(api)} == {api.account(r) for r in ALL_ROLES if r is not role}


def test_delete_audits_the_count_and_the_account_but_not_the_answers(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    needle = "zzauditneedle"
    answer(api, world["written"].id, written_answer("p-a", f"{needle} my answer"))
    answer(api, world["mcq"].id, mcq_answer("B"))
    answer(api, world["mcq"].id, mcq_answer("C"))
    assert audit_rows(api, "learner.responses_deleted") == []  # answering is not audited

    erase(api)

    (entry,) = audit_rows(api, "learner.responses_deleted")
    assert entry.actor == api.actor(Role.STUDENT)
    assert entry.entity_type == "account" and entry.entity_id == api.actor(Role.STUDENT)
    assert entry.data == {"deleted": 3}
    everything = api.session.connection().execute(text("SELECT t::text FROM audit_log t")).scalars()
    assert not [line for line in everything if needle in line]


def test_the_answers_are_gone_from_the_response_table_not_hidden(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    answer(api, world["mcq"].id, mcq_answer("A"))
    erase(api)
    assert rows(api) == []


def test_erasing_an_account_removes_its_answers(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    answer(api, world["mcq"].id, mcq_answer("A"))
    answer(api, world["mcq"].id, mcq_answer("A"), Role.TEACHER)
    student = api.account(Role.STUDENT)
    connection = api.session.connection()
    connection.execute(text("DELETE FROM role_assignment WHERE account_id = :a"), {"a": student})
    connection.execute(text("DELETE FROM account WHERE id = :a"), {"a": student})

    assert {r.account_id for r in rows(api)} == {api.account(Role.TEACHER)}


# --- the answers endpoint and the list agree ---------------------------------------------------


def test_an_answer_is_listed_at_once_and_a_failed_one_is_not(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    ok = answer(api, world["mcq"].id, mcq_answer("D")).json()
    assert answer(api, world["mcq"].id, written_answer("p-a")).status_code == 422
    assert answer(api, qid(world["mcq"].view), mcq_answer("A"), Role.STUDENT).status_code == 201
    items = listing(api).json()["items"]
    assert items[-1]["id"] == ok["response_id"]
    assert len(items) == 2


# --- topic and answered on the learner view (slice 8 review) -------------------------------------


def question_list(api: ApiHarness, *roles: Role) -> dict[str, Json]:
    response = api.client.get(
        "/v1/questions", params={"limit": 50}, headers=api.headers(*roles or (Role.STUDENT,))
    )
    assert response.status_code == 200, response.text
    return {item["id"]: item for item in response.json()["items"]}


def read_question(api: ApiHarness, question_id: str, *roles: Role) -> Json:
    response = api.client.get(
        f"/v1/questions/{question_id}", headers=api.headers(*roles or (Role.STUDENT,))
    )
    assert response.status_code == 200, response.text
    return response.json()  # type: ignore[no-any-return]


def syllabus_titles(api: ApiHarness) -> dict[str, str]:
    response = api.client.get(
        "/v1/programs/ib_dp/subjects/physics/syllabus", headers=api.headers(Role.STUDENT)
    )
    assert response.status_code == 200, response.text
    return {node["code"]: node["title"] for node in response.json()["nodes"]}


def test_the_topic_is_the_primary_syllabus_node_in_the_list_and_in_the_view(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    titles = syllabus_titles(api)
    listed = question_list(api)
    assert set(listed) >= {item.id for item in world.values()}
    for item in world.values():
        code = item.document.primary_syllabus_node
        expected = {"code": code, "title": titles[code]}
        assert listed[item.id]["topic"] == expected
        assert read_question(api, item.id)["topic"] == expected


def test_answered_is_per_account_and_covers_every_version(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item, untouched = world["mcq"], world["other_mcq"]
    assert all(not q["answered"] for q in question_list(api).values())
    assert not read_question(api, item.id)["answered"]

    answer(api, item.id, mcq_answer("A"))

    for role, flag in ((Role.STUDENT, True), (Role.TEACHER, False), (Role.PLATFORM_ADMIN, False)):
        listed = question_list(api, role)
        assert listed[item.id]["answered"] is flag, role
        assert read_question(api, item.id, role)["answered"] is flag, role
        assert listed[untouched.id]["answered"] is False
    # A corrected version is a new row of the same question: the flag follows the question.
    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)
    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    approve(api.session, revision.id, actor=STAFF)
    publish(api.session, revision.id, actor=STAFF)
    assert question_list(api)[item.id]["version_id"] == vid(revision)
    assert question_list(api)[item.id]["answered"] is True
    assert read_question(api, item.id)["answered"] is True
    # Deleting the answers clears it.
    erase(api)
    assert question_list(api)[item.id]["answered"] is False


def test_the_list_costs_the_same_number_of_queries_for_one_row_or_many(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    from sqlalchemy import event

    for item in world.values():
        answer(api, item.id, mcq_answer("A") if item.document.mcq else written_answer("p-a"))
    connection = api.session.connection()
    counted: list[str] = []

    def count(conn: Any, cursor: Any, statement: str, *rest: Any) -> None:
        counted.append(statement)

    event.listen(connection, "before_cursor_execute", count)
    try:
        counted.clear()
        api.client.get("/v1/questions", params={"limit": 1}, headers=api.headers(Role.STUDENT))
        one = len(counted)
        counted.clear()
        api.client.get("/v1/questions", params={"limit": 50}, headers=api.headers(Role.STUDENT))
        many = len(counted)
    finally:
        event.remove(connection, "before_cursor_execute", count)
    assert one == many


# --- the account cap ------------------------------------------------------------------------------


def bulk_fill(api: ApiHarness, version_id: uuid.UUID, account_id: uuid.UUID, count: int) -> None:
    api.session.connection().execute(
        text(
            "INSERT INTO response (id, account_id, question_version_id, kind, payload, correct) "
            "SELECT gen_random_uuid(), :a, :v, 'mcq', '{\"selected_key\": \"A\"}'::jsonb, false "
            "FROM generate_series(1, :n)"
        ),
        {"a": account_id, "v": version_id, "n": count},
    )


def test_the_account_cap_is_five_thousand(
    api: ApiHarness, world: dict[str, Published], monkeypatch: pytest.MonkeyPatch
) -> None:
    from qlab.attempts.models import MAX_ANSWERS_PER_ACCOUNT

    assert MAX_ANSWERS_PER_ACCOUNT == 5000
    # The per-question cap would stop a single question first; lift it for this test only.
    monkeypatch.setattr(attempts, "MAX_ANSWERS_PER_QUESTION", 10**9)
    item = world["mcq"]
    student = api.account(Role.STUDENT)
    bulk_fill(api, item.view.id, student, MAX_ANSWERS_PER_ACCOUNT - 1)

    assert answer(api, world["other_mcq"].id, mcq_answer("A")).status_code == 201  # the 5000th
    for target, body in (
        (item.id, mcq_answer("A")),
        (world["other_mcq"].id, mcq_answer("A")),
        (world["written"].id, written_answer("p-a")),
    ):
        assert_problem(answer(api, target, body), 429, "answer_limit_reached")
    assert len(rows(api)) == MAX_ANSWERS_PER_ACCOUNT
    # Another account is not affected; deleting frees the room.
    assert answer(api, item.id, mcq_answer("A"), Role.TEACHER).status_code == 201
    assert erase(api).json() == {"deleted": MAX_ANSWERS_PER_ACCOUNT}
    assert answer(api, item.id, mcq_answer("A")).status_code == 201


def test_a_refused_answer_is_not_counted_against_the_account(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    for _ in range(5):
        assert answer(api, world["mcq"].id, written_answer("p-a")).status_code == 422
    assert rows(api) == []


# --- control characters ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "char", ["\x00", "\x01", "\x07", "\x08", "\x0b", "\x0c", "\x1b", "\x1f", "\x7f"]
)
def test_a_control_character_in_a_written_answer_is_422_and_nothing_is_stored(
    api: ApiHarness, world: dict[str, Published], char: str
) -> None:
    marker = "zzctrlneedle"
    response = answer(api, world["written"].id, written_answer("p-a", f"{marker}{char}tail"))
    assert_problem(response, 422, "validation_failed")
    assert marker not in response.text
    assert rows(api) == []
    # raw JSON escape of NUL, as a client that does not use our library would send it
    raw = api.client.post(
        f"/v1/questions/{world['written'].id}/answers",
        content=b'{"kind": "written", "part_id": "p-a", "text": "a\\u0000b"}',
        headers={**api.headers(Role.STUDENT), "Content-Type": "application/json"},
    )
    assert_problem(raw, 422, "validation_failed")
    assert rows(api) == []


def test_tab_newline_and_carriage_return_are_accepted_and_stored_as_sent(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    text_ = "line one\n\tindented\r\nline three"
    assert answer(api, world["written"].id, written_answer("p-a", text_)).status_code == 201
    (row,) = rows(api)
    assert row.payload == {"text": text_}


# --- database errors never log the answer ---------------------------------------------------------


def test_a_database_error_logs_its_type_and_never_the_answer(
    api: ApiHarness,
    world: dict[str, Published],
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    needle = "zzdberrorneedle"

    def failing(session: Session, **kwargs: Any) -> Any:
        # A row the table refuses; PostgreSQL's message quotes the row, answer included.
        session.execute(
            text(
                "INSERT INTO response (id, account_id, question_version_id, kind, payload, "
                "correct) VALUES (gen_random_uuid(), :a, :v, 'nonsense', CAST(:p AS jsonb), false)"
            ),
            {
                "a": kwargs["account_id"],
                "v": kwargs["question_version_id"],
                "p": f'{{"text": "{needle}"}}',
            },
        )

    monkeypatch.setattr(attempts, "add_response", failing)
    caplog.set_level("DEBUG")

    response = answer(api, world["written"].id, written_answer("p-a", f"{needle} and more"))

    assert response.status_code == 500
    assert response.json()["code"] == "internal_error"
    assert needle not in response.text
    assert needle not in caplog.text
    assert "database error" in caplog.text
    assert "CheckViolation" in caplog.text
    assert rows(api) == []


# --- delete, nothing to delete; indexes -------------------------------------------------------


def test_deleting_nothing_writes_no_audit_entry(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    assert erase(api).json() == {"deleted": 0}
    assert audit_rows(api, "learner.responses_deleted") == []
    answer(api, world["mcq"].id, mcq_answer("A"))
    assert erase(api).json() == {"deleted": 1}
    assert erase(api).json() == {"deleted": 0}
    assert len(audit_rows(api, "learner.responses_deleted")) == 1


def test_the_indexes_serve_the_list_and_the_counters(api: ApiHarness) -> None:
    found = {
        row[0]: row[1]
        for row in api.session.connection().execute(
            text("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'response'")
        )
    }
    assert "ix_response_account_created" not in found
    assert "(account_id, id DESC)" in found["ix_response_account_id"]
    assert "(account_id, question_version_id)" in found["ix_response_account_version"]
