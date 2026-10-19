"""Learner answers (M1-G slice 8, docs/slices/M1G-8-OGRENCI.md sections 2, 3 and 5; D-66).

Written from the specification and the frozen contract (openapi.json, ENDPOINT_POLICY, migration
0007, schemas) only. Checked from the outside: HTTP responses and SELECTs on the tables.
"""

from __future__ import annotations

import json
import threading
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from qlab.api import ids
from qlab.api.app import create_app
from qlab.api.schemas import MAX_ANSWER_LENGTH
from qlab.api.settings import Environment, Settings
from qlab.content import service as svc
from qlab.identity import service as identity
from qlab.identity.tokens import DEV_AUDIENCE, DEV_ISSUER, TokenVerifier, sign
from qlab.organizations import service as organizations
from qlab.organizations.service import Role
from tests.api.support import ALL_ROLES, ApiHarness
from tests.api.test_learner_view import (
    PUBLISHABLE,
    Published,
    assert_clean,
    keys_in,
    publish_document,
    qid,
    vid,
)
from tests.content import samples
from tests.content.support import Env, approve, make_env, publish

pytestmark = [pytest.mark.db, pytest.mark.node]

Json = dict[str, Any]

STAFF = "u_zzactorsentinel"
ENGLISH = "The torque does work on the disc so its kinetic energy increases"
TURKISH = "Tork disk üzerinde iş yapar çünkü açısal hız artar"
SECRET = "zzsecretanswertext"  # noqa: S105
WARNING_CODE = "answer_not_english"
MCQ_NAMES = ["mcq", "plain_mcq"]
STRUCTURED_NAMES = ["structured", "show_that"]
CAP = 200

# Never in an answer result (section 3: sentence of outcome, figure descriptions, solution model
# stay hidden; author fields too).
NEVER_AFTER_ANSWER: frozenset[str] = frozenset(
    {
        "outcome",
        "assessment_objective",
        "description",
        "alt_text",
        "solution_model",
        "solution_step",
        "created_by",
        "source_ref",
        "option_kind",
        "answer_type",
        "level_content",
        "difficulty",
        "primary_syllabus_node",
        "secondary_syllabus_nodes",
        "document",
        "content_sha256",
        "stimulus",
        "stimuli",
    }
)
# Never in a question as read before answering.
NEVER_BEFORE_ANSWER: frozenset[str] = frozenset(
    {"explanation", "rationale", "rationales", "correct", "correct_key", "solution_model"}
)
CONTRACT_COLUMNS = {
    "id",
    "account_id",
    "question_version_id",
    "part_id",
    "kind",
    "payload",
    "correct",
    "created_at",
}
MCQ_RESULT_KEYS = {
    "kind",
    "response_id",
    "version_id",
    "correct",
    "correct_key",
    "explanation",
    "rationales",
}
WRITTEN_RESULT_KEYS = {
    "kind",
    "response_id",
    "version_id",
    "part_id",
    "marks",
    "marks_capped",
    "mark_points",
    "notes",
    "language_warning",
}
RESPONSE_KEYS = {
    "id",
    "question_id",
    "version_id",
    "kind",
    "part_id",
    "selected_key",
    "text",
    "correct",
    "created_at",
}


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


@pytest.fixture
def world(api: ApiHarness, env: Env) -> dict[str, Published]:
    return {
        name: publish_document(api.session, env, PUBLISHABLE[name](), tag=f"zzs{index}x")
        for index, name in enumerate([*MCQ_NAMES, *STRUCTURED_NAMES])
    }


# --- helpers -------------------------------------------------------------------------------------


def mcq_body(key: str) -> Json:
    return {"kind": "mcq", "selected_key": key}


def written_body(part_id: str, answer: str = ENGLISH) -> Json:
    return {"kind": "written", "part_id": part_id, "text": answer}


def submit(api: ApiHarness, question_id: str, body: Any, *roles: Role) -> Any:
    return api.client.post(
        f"/v1/questions/{question_id}/answers",
        json=body,
        headers=api.headers(*roles or (Role.STUDENT,)),
    )


def my_responses(api: ApiHarness, *roles: Role, **params: Any) -> Any:
    return api.client.get(
        "/v1/me/responses", params=params, headers=api.headers(*roles or (Role.STUDENT,))
    )


def delete_mine(api: ApiHarness, *roles: Role) -> Any:
    return api.client.delete("/v1/me/responses", headers=api.headers(*roles or (Role.STUDENT,)))


def correct_key_of(item: Published) -> str:
    assert item.document.mcq is not None
    return item.document.mcq.correct_key


def rows(api: ApiHarness, account: uuid.UUID | None = None) -> list[Any]:
    api.session.expire_all()
    if account is None:
        result = api.session.execute(text("SELECT * FROM response ORDER BY created_at, id"))
    else:
        result = api.session.execute(
            text("SELECT * FROM response WHERE account_id = :a ORDER BY created_at, id"),
            {"a": account},
        )
    return list(result.mappings())


def uuid7_at(moment: datetime, sequence: int) -> uuid.UUID:
    """A UUIDv7 for `moment`; `sequence` keeps ids of one millisecond ordered."""
    millis = int(moment.timestamp() * 1000)
    value = (
        (millis << 80)
        | (0x7 << 76)
        | (sequence << 64)
        | (0b10 << 62)
        | uuid.uuid4().int % (1 << 62)
    )
    return uuid.UUID(int=value)


def insert_rows(
    api: ApiHarness,
    account: uuid.UUID,
    version: uuid.UUID,
    count: int,
    *,
    start: datetime | None = None,
) -> list[uuid.UUID]:
    """`count` mcq rows with strictly increasing created_at, one second apart."""
    start = start or datetime.now(tz=UTC) - timedelta(days=1)
    made = []
    for index in range(count):
        row_id = uuid7_at(start + timedelta(seconds=index), 0)
        made.append(row_id)
        api.session.execute(
            text(
                "INSERT INTO response (id, account_id, question_version_id, part_id, kind, "
                "payload, correct, created_at) VALUES (:i, :a, :v, NULL, 'mcq', "
                "CAST(:p AS jsonb), true, :t)"
            ),
            {
                "i": row_id,
                "a": account,
                "v": version,
                "p": json.dumps({"selected_key": "A"}),
                "t": start + timedelta(seconds=index),
            },
        )
    api.session.flush()
    return made


def bulk_fill(api: ApiHarness, account: uuid.UUID, version: uuid.UUID, count: int) -> None:
    api.session.execute(
        text(
            "INSERT INTO response (id, account_id, question_version_id, part_id, kind, payload, "
            "correct) SELECT gen_random_uuid(), :a, :v, NULL, 'mcq', "
            '\'{"selected_key": "A"}\'::jsonb, true FROM generate_series(1, :n)'
        ),
        {"a": account, "v": version, "n": count},
    )
    api.session.flush()


def audit_entries(api: ApiHarness, action: str) -> list[Any]:
    api.session.expire_all()
    return list(
        api.session.execute(
            text("SELECT actor, entity_type, entity_id, data FROM audit_log WHERE action = :a"),
            {"a": action},
        ).mappings()
    )


def problem_code(response: Any) -> str:
    return str(response.json()["code"])


# =============================================================================================
# Multiple choice
# =============================================================================================


@pytest.mark.parametrize("name", MCQ_NAMES)
def test_every_option_gets_a_201_with_the_documented_shape(
    api: ApiHarness, world: dict[str, Published], name: str
) -> None:
    item = world[name]
    right = correct_key_of(item)
    for key in "ABCD":
        response = submit(api, item.id, mcq_body(key))
        assert response.status_code == 201, response.text
        body = response.json()
        assert set(body) == MCQ_RESULT_KEYS
        assert body["kind"] == "mcq"
        assert body["correct"] is (key == right)
        assert body["correct_key"] == right
        assert body["version_id"] == vid(item.view)
        assert body["response_id"].startswith("rsp_")
        ids.decode(ids.RESPONSE, body["response_id"])


def test_explanation_and_one_rationale_per_wrong_option_and_never_the_right_ones(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["mcq"]
    right = correct_key_of(item)
    body = submit(api, item.id, mcq_body(right)).json()
    # sentinels planted by publish_document: f"{tag}explanation", f"{tag}rationale{key}"
    tag = "zzs0x"
    wrong = sorted(set("ABCD") - {right})
    assert sorted(r["key"] for r in body["rationales"]) == wrong
    for entry in body["rationales"]:
        assert set(entry) == {"key", "content"}
        assert f"{tag}rationale{entry['key'].lower()}" in json.dumps(entry["content"]).lower()
    text_out = json.dumps(body).lower()
    assert f"{tag}explanation" in json.dumps(body["explanation"]).lower()
    assert f"{tag}rationale{right.lower()}" not in text_out


def test_the_rationales_do_not_depend_on_the_selected_option(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["plain_mcq"]
    first = submit(api, item.id, mcq_body("A")).json()
    second = submit(api, item.id, mcq_body("C")).json()
    assert first["rationales"] == second["rationales"]
    assert first["explanation"] == second["explanation"]
    assert sorted(r["key"] for r in first["rationales"]) == ["A", "B", "D"]


def test_a_question_before_it_is_answered_leaks_nothing(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    everything = [s for item in world.values() for s in item.sentinels.all()]
    for item in world.values():
        response = api.client.get(f"/v1/questions/{item.id}", headers=api.headers(Role.STUDENT))
        assert response.status_code == 200
        assert not (keys_in(response.json()) & NEVER_BEFORE_ANSWER)
        assert_clean(response.text, everything, NEVER_BEFORE_ANSWER)
    listing = api.client.get("/v1/questions", headers=api.headers(Role.STUDENT))
    assert listing.status_code == 200
    assert not (keys_in(listing.json()) & NEVER_BEFORE_ANSWER)


def test_an_mcq_result_holds_nothing_the_learner_may_not_see(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["mcq"]
    response = submit(api, item.id, mcq_body("A"))
    hidden = [s for s in item.sentinels.hidden if "explanation" not in s and "rationale" not in s]
    assert_clean(response.text, hidden, NEVER_AFTER_ANSWER)


def test_a_written_result_holds_nothing_the_learner_may_not_see(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    for name in STRUCTURED_NAMES:
        item = world[name]
        part_id = item.document.parts[0].id
        response = submit(api, item.id, written_body(part_id))
        assert_clean(response.text, item.sentinels.hidden, NEVER_AFTER_ANSWER)


# =============================================================================================
# Written
# =============================================================================================


@pytest.mark.parametrize("name", STRUCTURED_NAMES)
def test_a_written_answer_is_a_201_with_the_documented_shape(
    api: ApiHarness, world: dict[str, Published], name: str
) -> None:
    item = world[name]
    part = item.document.parts[0]
    response = submit(api, item.id, written_body(part.id))
    assert response.status_code == 201, response.text
    body = response.json()
    assert set(body) == WRITTEN_RESULT_KEYS
    assert body["kind"] == "written"
    assert body["part_id"] == part.id
    assert body["version_id"] == vid(item.view)
    assert body["response_id"].startswith("rsp_")
    assert body["language_warning"] is None
    assert not ({"correct", "correct_key", "explanation", "rationales"} & set(body))


def test_stored_answers_are_listed_with_the_documented_fields(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    mcq, structured = world["plain_mcq"], world["structured"]
    part_id = structured.document.parts[0].id
    first = submit(api, mcq.id, mcq_body("B")).json()
    second = submit(api, structured.id, written_body(part_id, "34 m/s")).json()

    page = my_responses(api).json()
    assert set(page) == {"items", "next_cursor"}
    assert page["next_cursor"] is None
    by_id = {item["id"]: item for item in page["items"]}
    assert set(by_id) == {first["response_id"], second["response_id"]}
    for item in page["items"]:
        assert set(item) == RESPONSE_KEYS
        datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
    one, two = by_id[first["response_id"]], by_id[second["response_id"]]
    assert (one["kind"], one["question_id"], one["version_id"]) == ("mcq", mcq.id, vid(mcq.view))
    assert (one["part_id"], one["selected_key"], one["text"]) == (None, "B", None)
    assert one["correct"] is (correct_key_of(mcq) == "B")
    assert (two["kind"], two["question_id"], two["version_id"]) == (
        "written",
        structured.id,
        vid(structured.view),
    )
    assert (two["part_id"], two["selected_key"], two["text"]) == (part_id, None, "34 m/s")
    assert two["correct"] is None


# =============================================================================================
# Answers that do not fit
# =============================================================================================


@pytest.mark.parametrize("name", STRUCTURED_NAMES)
def test_an_mcq_answer_to_a_structured_question_does_not_fit(
    api: ApiHarness, world: dict[str, Published], name: str
) -> None:
    response = submit(api, world[name].id, mcq_body("A"))
    assert response.status_code == 422, response.text
    assert problem_code(response) == "answer_does_not_fit"
    assert rows(api) == []


@pytest.mark.parametrize("name", MCQ_NAMES)
def test_a_written_answer_to_an_mcq_question_does_not_fit(
    api: ApiHarness, world: dict[str, Published], name: str
) -> None:
    response = submit(api, world[name].id, written_body("p-a"))
    assert response.status_code == 422, response.text
    assert problem_code(response) == "answer_does_not_fit"
    assert rows(api) == []


def test_an_unknown_part_does_not_fit(api: ApiHarness, world: dict[str, Published]) -> None:
    response = submit(api, world["structured"].id, written_body("no-such-part"))
    assert response.status_code == 422, response.text
    assert problem_code(response) == "answer_does_not_fit"
    assert rows(api) == []


def test_a_refused_answer_is_not_counted_towards_the_cap(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["structured"]
    for _ in range(3):
        submit(api, item.id, mcq_body("A"))
    assert rows(api) == []


@pytest.mark.parametrize(
    "body",
    [
        {"kind": "mcq", "selected_key": "E"},
        {"kind": "mcq", "selected_key": "a"},
        {"kind": "mcq"},
        {"kind": "mcq", "selected_key": "A", "extra": 1},
        {"kind": "written", "part_id": "p-a"},
        {"kind": "written", "part_id": "", "text": "x"},
        {"kind": "written", "part_id": "p-a", "text": ""},
        {"kind": "essay", "text": "x"},
        {},
    ],
)
def test_an_invalid_body_is_422_and_stores_nothing(
    api: ApiHarness, world: dict[str, Published], body: Json
) -> None:
    for name in ("plain_mcq", "structured"):
        response = submit(api, world[name].id, body)
        assert response.status_code == 422, response.text
    assert rows(api) == []


def test_an_answer_of_the_maximum_length_is_accepted_and_one_more_is_not(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["structured"]
    part_id = item.document.parts[0].id
    ok = submit(api, item.id, written_body(part_id, "7" * MAX_ANSWER_LENGTH))
    assert ok.status_code == 201, ok.text
    too_long = submit(api, item.id, written_body(part_id, "7" * (MAX_ANSWER_LENGTH + 1)))
    assert too_long.status_code == 422
    assert len(rows(api)) == 1


def test_a_body_over_64_kib_is_413_and_stores_nothing(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["structured"]
    part_id = item.document.parts[0].id
    payload = json.dumps(written_body(part_id, "a" * (65 * 1024))).encode()
    response = api.client.post(
        f"/v1/questions/{item.id}/answers",
        content=payload,
        headers={**api.headers(Role.STUDENT), "Content-Type": "application/json"},
    )
    assert response.status_code == 413, response.text
    assert rows(api) == []


def test_the_old_check_path_is_gone(api: ApiHarness, world: dict[str, Published]) -> None:
    for name, body in (("plain_mcq", mcq_body("A")), ("structured", written_body("p-a"))):
        response = api.client.post(
            f"/v1/questions/{world[name].id}/check",
            json=body,
            headers=api.headers(Role.STUDENT),
        )
        assert response.status_code == 404
    assert rows(api) == []


def test_an_unknown_or_unpublished_question_is_404(api: ApiHarness, env: Env) -> None:
    unknown = ids.encode(ids.QUESTION, uuid.uuid4())
    assert submit(api, unknown, mcq_body("A")).status_code == 404
    assert submit(api, "not-an-id", mcq_body("A")).status_code == 404
    assert rows(api) == []


# =============================================================================================
# Language
# =============================================================================================


def test_a_turkish_answer_gets_the_warning_and_is_stored(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["show_that"]
    part_id = item.document.parts[0].id
    response = submit(api, item.id, written_body(part_id, TURKISH))
    assert response.status_code == 201, response.text
    assert response.json()["language_warning"]["code"] == WARNING_CODE
    stored = rows(api)
    assert len(stored) == 1
    assert stored[0]["payload"] == {"text": TURKISH}
    items = my_responses(api).json()["items"]
    assert [i["text"] for i in items] == [TURKISH]


# =============================================================================================
# Stored row
# =============================================================================================


def test_the_response_table_has_exactly_the_contract_columns(api: ApiHarness) -> None:
    columns = {
        r[0]
        for r in api.session.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = 'response'"
            )
        )
    }
    assert columns == CONTRACT_COLUMNS


def test_an_mcq_answer_is_one_row_bound_to_the_version(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["plain_mcq"]
    body = submit(api, item.id, mcq_body("B")).json()
    stored = rows(api)
    assert len(stored) == 1
    row = stored[0]
    assert set(row) == CONTRACT_COLUMNS
    assert ids.encode(ids.RESPONSE, row["id"]) == body["response_id"]
    assert row["account_id"] == api.account(Role.STUDENT)
    assert row["question_version_id"] == item.view.id
    assert row["kind"] == "mcq"
    assert row["part_id"] is None
    assert row["payload"] == {"selected_key": "B"}
    assert row["correct"] is (correct_key_of(item) == "B")
    assert row["created_at"] is not None


def test_a_written_answer_is_one_row_with_no_correct_flag(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["structured"]
    part_id = item.document.parts[0].id
    body = submit(api, item.id, written_body(part_id, "34 m/s")).json()
    stored = rows(api)
    assert len(stored) == 1
    row = stored[0]
    assert ids.encode(ids.RESPONSE, row["id"]) == body["response_id"]
    assert row["kind"] == "written"
    assert row["part_id"] == part_id
    assert row["payload"] == {"text": "34 m/s"}
    assert row["correct"] is None
    assert row["question_version_id"] == item.view.id


def test_the_row_holds_no_name_email_or_address(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["plain_mcq"]
    submit(api, item.id, mcq_body("A"))
    row_text = " ".join(str(v) for v in rows(api)[0].values()).lower()
    subject = api.subject(Role.STUDENT).lower()
    assert subject not in row_text
    assert "testclient" not in row_text
    assert "127.0.0.1" not in row_text


def test_each_submission_is_a_new_row(api: ApiHarness, world: dict[str, Published]) -> None:
    item = world["plain_mcq"]
    first = submit(api, item.id, mcq_body("A")).json()
    second = submit(api, item.id, mcq_body("A")).json()
    assert first["response_id"] != second["response_id"]
    assert len(rows(api)) == 2


def test_the_row_stays_bound_to_the_version_answered_after_a_revision(
    api: ApiHarness, env: Env
) -> None:
    item = publish_document(
        api.session, env, samples.plain_mcq_document(), tag="zzrev", plant=False
    )
    old = submit(api, item.id, mcq_body("C")).json()
    assert old["version_id"] == vid(item.view)

    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)
    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    approve(api.session, revision.id, actor=STAFF)
    publish(api.session, revision.id, actor=STAFF)

    new = submit(api, item.id, mcq_body("C")).json()
    assert new["version_id"] == vid(revision)
    by_id = {r["id"]: r for r in rows(api)}
    assert (
        by_id[ids.decode(ids.RESPONSE, old["response_id"])]["question_version_id"] == item.view.id
    )
    assert by_id[ids.decode(ids.RESPONSE, new["response_id"])]["question_version_id"] == revision.id
    listed = {i["id"]: i["version_id"] for i in my_responses(api).json()["items"]}
    assert listed == {old["response_id"]: vid(item.view), new["response_id"]: vid(revision)}
    assert {i["question_id"] for i in my_responses(api).json()["items"]} == {item.id}


# =============================================================================================
# Roles and isolation
# =============================================================================================


@pytest.mark.parametrize("role", ALL_ROLES)
def test_every_role_can_answer_and_sees_only_its_own_rows(
    api: ApiHarness, world: dict[str, Published], role: Role
) -> None:
    item = world["plain_mcq"]
    # every other role answers first, so that the others' rows exist
    for other in ALL_ROLES:
        if other is not role:
            assert submit(api, item.id, mcq_body("A"), other).status_code == 201
    mine = submit(api, item.id, mcq_body("B"), role)
    assert mine.status_code == 201, mine.text
    page = my_responses(api, role)
    assert page.status_code == 200
    assert [i["id"] for i in page.json()["items"]] == [mine.json()["response_id"]]


@pytest.mark.parametrize("role", ALL_ROLES)
def test_every_role_can_answer_a_written_question(
    api: ApiHarness, world: dict[str, Published], role: Role
) -> None:
    item = world["structured"]
    response = submit(api, item.id, written_body(item.document.parts[0].id), role)
    assert response.status_code == 201, response.text


def test_two_accounts_never_see_each_others_answers(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["plain_mcq"]
    a = submit(api, item.id, mcq_body("A"), Role.STUDENT).json()["response_id"]
    b = submit(api, item.id, mcq_body("D"), Role.TEACHER).json()["response_id"]
    assert [i["id"] for i in my_responses(api, Role.STUDENT).json()["items"]] == [a]
    assert [i["id"] for i in my_responses(api, Role.TEACHER).json()["items"]] == [b]
    filtered = my_responses(api, Role.STUDENT, question_id=item.id).json()["items"]
    assert [i["id"] for i in filtered] == [a]


def test_no_token_is_401_everywhere(api: ApiHarness, world: dict[str, Published]) -> None:
    item = world["plain_mcq"]
    assert (
        api.client.post(f"/v1/questions/{item.id}/answers", json=mcq_body("A")).status_code == 401
    )
    assert api.client.get("/v1/me/responses").status_code == 401
    assert api.client.delete("/v1/me/responses").status_code == 401
    bad = {"Authorization": "Bearer not-a-token"}
    assert api.client.get("/v1/me/responses", headers=bad).status_code == 401
    assert rows(api) == []


def test_an_account_without_a_role_is_404_everywhere(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["plain_mcq"]
    headers = api.headers()
    post = api.client.post(f"/v1/questions/{item.id}/answers", json=mcq_body("A"), headers=headers)
    assert post.status_code == 404
    assert api.client.get("/v1/me/responses", headers=headers).status_code == 404
    assert api.client.delete("/v1/me/responses", headers=headers).status_code == 404
    assert rows(api) == []


# =============================================================================================
# Listing
# =============================================================================================


def test_an_empty_history_is_an_empty_page(api: ApiHarness, world: dict[str, Published]) -> None:
    response = my_responses(api)
    assert response.status_code == 200
    assert response.json() == {"items": [], "next_cursor": None}


def test_newest_first_by_created_at(api: ApiHarness, world: dict[str, Published]) -> None:
    item = world["plain_mcq"]
    account = api.account(Role.STUDENT)
    made = insert_rows(api, account, item.view.id, 5)
    items = my_responses(api).json()["items"]
    assert [i["id"] for i in items] == [ids.encode(ids.RESPONSE, m) for m in reversed(made)]
    stamps = [i["created_at"] for i in items]
    assert stamps == sorted(stamps, reverse=True)


def test_answers_made_through_the_api_come_back_in_non_increasing_time_order(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["plain_mcq"]
    for key in "ABCD":
        submit(api, item.id, mcq_body(key))
    items = my_responses(api).json()["items"]
    assert len(items) == 4
    stamps = [datetime.fromisoformat(i["created_at"].replace("Z", "+00:00")) for i in items]
    assert stamps == sorted(stamps, reverse=True)


def test_the_question_filter_narrows_to_one_question(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    one, two = world["plain_mcq"], world["mcq"]
    submit(api, one.id, mcq_body("A"))
    submit(api, one.id, mcq_body("B"))
    submit(api, two.id, mcq_body("C"))
    only_one = my_responses(api, question_id=one.id).json()["items"]
    only_two = my_responses(api, question_id=two.id).json()["items"]
    assert len(only_one) == 2 and {i["question_id"] for i in only_one} == {one.id}
    assert len(only_two) == 1 and only_two[0]["question_id"] == two.id
    assert len(my_responses(api).json()["items"]) == 3


def test_cursor_paging_walks_every_row_once_in_order(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["plain_mcq"]
    made = insert_rows(api, api.account(Role.STUDENT), item.view.id, 25)
    expected = [ids.encode(ids.RESPONSE, m) for m in reversed(made)]
    seen: list[str] = []
    cursor: str | None = None
    for _ in range(10):
        params: Json = {"limit": 10}
        if cursor:
            params["cursor"] = cursor
        page = my_responses(api, **params).json()
        assert len(page["items"]) <= 10
        seen.extend(i["id"] for i in page["items"])
        cursor = page["next_cursor"]
        if cursor is None:
            break
    else:
        raise AssertionError("paging does not end")
    assert seen == expected


def test_a_page_that_ends_exactly_has_no_next_cursor(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    insert_rows(api, api.account(Role.STUDENT), world["plain_mcq"].view.id, 3)
    page = my_responses(api, limit=3).json()
    assert len(page["items"]) == 3
    assert page["next_cursor"] is None


def test_the_default_page_size_is_20_and_the_maximum_100(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    insert_rows(api, api.account(Role.STUDENT), world["plain_mcq"].view.id, 105)
    first = my_responses(api).json()
    assert len(first["items"]) == 20 and first["next_cursor"] is not None
    big = my_responses(api, limit=100).json()
    assert len(big["items"]) == 100 and big["next_cursor"] is not None
    one = my_responses(api, limit=1).json()
    assert len(one["items"]) == 1 and one["next_cursor"] is not None


@pytest.mark.parametrize("limit", [0, 101, -1, "x"])
def test_limit_out_of_bounds_is_422(api: ApiHarness, limit: Any) -> None:
    response = my_responses(api, limit=limit)
    assert response.status_code == 422, response.text


def test_a_paging_cursor_cannot_reveal_another_accounts_rows(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    version = world["plain_mcq"].view.id
    insert_rows(api, api.account(Role.STUDENT), version, 4)
    other = insert_rows(api, api.account(Role.TEACHER), version, 4)
    cursor = my_responses(api, Role.STUDENT, limit=2).json()["next_cursor"]
    page = my_responses(api, Role.TEACHER, limit=2, cursor=cursor)
    if page.status_code == 200:
        assert {i["id"] for i in page.json()["items"]} <= {
            ids.encode(ids.RESPONSE, m) for m in other
        }
    else:
        assert page.status_code == 422


# =============================================================================================
# Delete
# =============================================================================================


def test_delete_removes_only_the_callers_rows_and_returns_the_count(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item, structured = world["plain_mcq"], world["structured"]
    part_id = structured.document.parts[0].id
    submit(api, item.id, mcq_body("A"), Role.STUDENT)
    submit(api, item.id, mcq_body("B"), Role.STUDENT)
    submit(api, structured.id, written_body(part_id), Role.STUDENT)
    keep = [
        submit(api, item.id, mcq_body("C"), Role.TEACHER).json()["response_id"],
        submit(api, item.id, mcq_body("D"), Role.REVIEWER).json()["response_id"],
    ]
    response = delete_mine(api, Role.STUDENT)
    assert response.status_code == 200, response.text
    assert response.json() == {"deleted": 3}

    assert rows(api, api.account(Role.STUDENT)) == []
    assert my_responses(api, Role.STUDENT).json()["items"] == []
    assert [i["id"] for i in my_responses(api, Role.TEACHER).json()["items"]] == [keep[0]]
    assert [i["id"] for i in my_responses(api, Role.REVIEWER).json()["items"]] == [keep[1]]
    assert len(rows(api)) == 2

    again = delete_mine(api, Role.STUDENT)
    assert again.status_code == 200
    assert again.json() == {"deleted": 0}
    assert len(rows(api)) == 2


def test_delete_with_nothing_stored_is_zero(api: ApiHarness) -> None:
    response = delete_mine(api)
    assert response.status_code == 200
    assert response.json() == {"deleted": 0}


def test_delete_writes_an_audit_entry_with_the_count_and_no_answer_text(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    structured = world["structured"]
    part_id = structured.document.parts[0].id
    for _ in range(3):
        assert submit(api, structured.id, written_body(part_id, SECRET)).status_code == 201
    submit(api, world["plain_mcq"].id, mcq_body("A"), Role.TEACHER)
    before = len(audit_entries(api, "learner.responses_deleted"))

    assert delete_mine(api).json() == {"deleted": 3}
    entries = audit_entries(api, "learner.responses_deleted")
    assert len(entries) == before + 1
    entry = entries[-1]
    account = ids.actor(api.account(Role.STUDENT))
    flat = " ".join([entry["actor"], entry["entity_type"], entry["entity_id"]])
    assert account in flat or account in json.dumps(entry["data"])
    assert 3 in entry["data"].values()
    everything = (flat + json.dumps(entry["data"])).lower()
    assert SECRET not in everything
    assert "selected_key" not in everything
    # nothing of the answers anywhere in the audit log
    api.session.expire_all()
    hits = api.session.execute(
        text("SELECT count(*) FROM audit_log a WHERE a::text ILIKE :n"), {"n": f"%{SECRET}%"}
    ).scalar_one()
    assert hits == 0


def test_a_refused_delete_writes_no_audit_entry(api: ApiHarness) -> None:
    before = len(audit_entries(api, "learner.responses_deleted"))
    assert api.client.delete("/v1/me/responses").status_code == 401
    assert api.client.delete("/v1/me/responses", headers=api.headers()).status_code == 404
    assert len(audit_entries(api, "learner.responses_deleted")) == before


def test_deleting_the_account_row_removes_its_responses(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["plain_mcq"]
    student, teacher = api.account(Role.STUDENT), api.account(Role.TEACHER)
    insert_rows(api, student, item.view.id, 3)
    insert_rows(api, teacher, item.view.id, 2)
    api.session.execute(text("DELETE FROM role_assignment WHERE account_id = :a"), {"a": student})
    api.session.execute(text("DELETE FROM account WHERE id = :a"), {"a": student})
    api.session.flush()
    assert rows(api, student) == []
    assert len(rows(api, teacher)) == 2


def test_the_database_refuses_inconsistent_rows(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    from sqlalchemy.exc import IntegrityError

    account, version = api.account(Role.STUDENT), world["plain_mcq"].view.id
    bad = [
        ("mcq", "p-a", True, {"selected_key": "A"}),  # mcq with a part
        ("mcq", None, None, {"selected_key": "A"}),  # mcq without correct
        ("written", None, None, {"text": "x"}),  # written without a part
        ("written", "p-a", True, {"text": "x"}),  # written with correct
        ("essay", None, None, {"text": "x"}),  # unknown kind
    ]
    for kind, part, correct, payload in bad:
        with pytest.raises(IntegrityError), api.session.begin_nested():
            api.session.execute(
                text(
                    "INSERT INTO response (id, account_id, question_version_id, part_id, "
                    "kind, payload, correct) VALUES (:i, :a, :v, :p, :k, "
                    "CAST(:pl AS jsonb), :c)"
                ),
                {
                    "i": uuid.uuid4(),
                    "a": account,
                    "v": version,
                    "p": part,
                    "k": kind,
                    "pl": json.dumps(payload),
                    "c": correct,
                },
            )


# =============================================================================================
# The cap
# =============================================================================================


def test_the_201st_answer_to_a_question_is_429(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item, other_question = world["plain_mcq"], world["mcq"]
    student = api.account(Role.STUDENT)
    bulk_fill(api, student, item.view.id, CAP - 1)

    last = submit(api, item.id, mcq_body("A"))
    assert last.status_code == 201, last.text
    refused = submit(api, item.id, mcq_body("A"))
    assert refused.status_code == 429, refused.text
    assert problem_code(refused) == "too_many_answers"
    assert len(rows(api, student)) == CAP

    # the counter is per account ...
    assert submit(api, item.id, mcq_body("A"), Role.TEACHER).status_code == 201
    # ... and per question
    assert submit(api, other_question.id, mcq_body("A")).status_code == 201


def test_a_written_answer_counts_towards_the_cap_of_its_question(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["structured"]
    part_id = item.document.parts[0].id
    bulk_written = text(
        "INSERT INTO response (id, account_id, question_version_id, part_id, kind, payload, "
        "correct) SELECT gen_random_uuid(), :a, :v, :p, 'written', "
        '\'{"text": "x"}\'::jsonb, NULL FROM generate_series(1, :n)'
    )
    api.session.execute(
        bulk_written,
        {"a": api.account(Role.STUDENT), "v": item.view.id, "p": part_id, "n": CAP - 1},
    )
    api.session.flush()
    assert submit(api, item.id, written_body(part_id)).status_code == 201
    refused = submit(api, item.id, written_body(part_id))
    assert refused.status_code == 429
    assert problem_code(refused) == "too_many_answers"


def test_deleting_the_answers_frees_the_cap(api: ApiHarness, world: dict[str, Published]) -> None:
    item = world["plain_mcq"]
    bulk_fill(api, api.account(Role.STUDENT), item.view.id, CAP)
    assert submit(api, item.id, mcq_body("A")).status_code == 429
    assert delete_mine(api).json() == {"deleted": CAP}
    assert submit(api, item.id, mcq_body("A")).status_code == 201


def test_the_cap_counts_all_versions_of_the_question(api: ApiHarness, env: Env) -> None:
    item = publish_document(
        api.session, env, samples.plain_mcq_document(), tag="zzcap", plant=False
    )
    student = api.account(Role.STUDENT)
    bulk_fill(api, student, item.view.id, CAP - 1)
    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)
    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    approve(api.session, revision.id, actor=STAFF)
    publish(api.session, revision.id, actor=STAFF)
    # "an account has at most 200 answers to a question": one more is fine, then the cap.
    assert submit(api, item.id, mcq_body("A")).status_code == 201
    refused = submit(api, item.id, mcq_body("A"))
    assert refused.status_code == 429, refused.text
    assert problem_code(refused) == "too_many_answers"


# =============================================================================================
# Concurrency
# =============================================================================================


@pytest.fixture
def committed(
    throwaway_engine: Engine,
) -> Iterator[tuple[Engine, TestClient, str, uuid.UUID, uuid.UUID]]:
    """The application on committed connections, on a database made for this test. Yields the
    engine, a client with a `token` helper, the question id, the version id and the account."""
    engine = throwaway_engine
    key = Ed25519PrivateKey.generate()
    factory = sessionmaker(bind=engine)
    with factory() as session:
        env = make_env(session)
        item = publish_document(
            session, env, samples.plain_mcq_document(), tag="zzrace", plant=False
        )
        account = identity.ensure_account(session, issuer=DEV_ISSUER, subject="race-student")
        organizations.grant(
            session, account_id=account.id, role=Role.STUDENT, granted_by="system:test"
        )
        question_id, version_id, account_id = qid(item.view), item.view.id, account.id
        session.commit()
    app = create_app(
        Settings(environment=Environment.LOCAL, forbid_self_approval=False),
        verifier=TokenVerifier(
            public_keys=[key.public_key()], issuer=DEV_ISSUER, audience=DEV_AUDIENCE
        ),
        session_factory=factory,
        check_renderer=False,
    )
    client = TestClient(app, raise_server_exceptions=False)
    client.headers.update(
        {
            "Authorization": "Bearer "
            + sign(
                key,
                issuer=DEV_ISSUER,
                audience=DEV_AUDIENCE,
                subject="race-student",
                lifetime=timedelta(minutes=5),
                now=datetime.now(tz=UTC),
            )
        }
    )
    yield engine, client, question_id, version_id, account_id


@pytest.mark.parametrize("round_", range(3))
def test_two_parallel_submits_at_199_stored_give_one_201_and_one_429(
    committed: tuple[Engine, TestClient, str, uuid.UUID, uuid.UUID], round_: int
) -> None:
    engine, client, question_id, version_id, account_id = committed
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO response (id, account_id, question_version_id, part_id, kind, "
                "payload, correct) SELECT gen_random_uuid(), :a, :v, NULL, 'mcq', "
                '\'{"selected_key": "A"}\'::jsonb, true FROM generate_series(1, 199)'
            ),
            {"a": account_id, "v": version_id},
        )
    barrier = threading.Barrier(2)
    statuses: list[int] = [0, 0]

    def go(index: int) -> None:
        barrier.wait(timeout=30)
        statuses[index] = client.post(
            f"/v1/questions/{question_id}/answers", json=mcq_body("A")
        ).status_code

    threads = [threading.Thread(target=go, args=(i,)) for i in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert sorted(statuses) == [201, 429], statuses
    with engine.connect() as connection:
        stored = connection.execute(
            text("SELECT count(*) FROM response WHERE account_id = :a"), {"a": account_id}
        ).scalar_one()
    assert stored == CAP
