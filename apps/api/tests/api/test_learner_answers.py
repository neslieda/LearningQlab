"""Submitting an answer: `POST /v1/questions/{id}/answers`
(docs/slices/M1G-8-OGRENCI.md sections 2 and 3, which carries the slice 5 rules over; CLAUDE.md
rules 2, 7 and 13). Storage, the cap, the list and the delete are in test_learner_responses.py.

Checked from the outside only:

- multiple choice: whether the selected option is the right one, which option is, the explanation
  and the reason each wrong option is wrong (only after answering);
- written: exactly the mark points and notes of the part asked about, with its marks, and a
  language hint that never withholds the mark scheme;
- a request that does not fit the question, or is not valid, is a 422 that reveals nothing;
- the answer is stored (D-66) but only in `response`: the answer text is in no other table and no
  log line, and the audit log has no entry for answering;
- an unpublished, withdrawn or rights-revoked question is a 404, whatever the request says.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from typing import Any

import pytest
from sqlalchemy import Connection, text
from sqlalchemy.orm import Session

from qlab.api import ids
from qlab.api.schemas import McqResult, WrittenResult
from qlab.content import service as svc
from qlab.organizations.service import Role
from qlab.rights import service as rights
from tests.api.support import ALL_ROLES, ApiHarness
from tests.api.test_learner_view import (
    PUBLISHABLE,
    Published,
    assert_clean,
    assert_not_found,
    keys_in,
    publish_document,
    qid,
    structured_without_figure,
    vid,
)
from tests.content import samples
from tests.content.support import (
    Env,
    approve,
    bring_to,
    document,
    make_env,
    new_rights,
    now,
    publish,
)

pytestmark = [pytest.mark.db, pytest.mark.node]

Json = dict[str, Any]

STAFF = "u_zzchecker"
WARNING = {"code": "answer_not_english", "message": "Please write your answer in English."}
ENGLISH = "The torque does work on the disc so its kinetic energy increases"
TURKISH = "Tork disk üzerinde iş yapar çünkü açısal hız artar"

# Keys that no answer response may contain: a written result may not hold the correct option
# either, nor any of the author's private fields.
NEVER_IN_AN_ANSWER: frozenset[str] = frozenset(
    {
        "rationale",
        "explanation",
        "outcome",
        "description",
        "alt_text",
        "solution_model",
        "solution_step",
        "option_kind",
        "answer_type",
        "assessment_objective",
        "level_content",
        "created_by",
        "source_ref",
        "difficulty",
        "primary_syllabus_node",
        "secondary_syllabus_nodes",
        "document",
        "content_sha256",
    }
)
WRITTEN_FORBIDDEN = NEVER_IN_AN_ANSWER | {"correct_key", "correct"}
# An mcq result does carry the explanation and the rationales (D-66), nothing else of the author's.
MCQ_FORBIDDEN = NEVER_IN_AN_ANSWER - {"explanation"}


def allowed_in_mcq_result(sentinel: str) -> bool:
    return "explanation" in sentinel or "rationale" in sentinel


def author_secrets(world: dict[str, Published]) -> list[str]:
    return [
        s for other in world.values() for s in other.sentinels.all() if not allowed_in_mcq_result(s)
    ]


MCQ_NAMES = ["mcq", "plain_mcq", "two_column_mcq", "roman_mcq"]
STRUCTURED_NAMES = ["structured", "data_based", "show_that"]


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


@pytest.fixture
def world(api: ApiHarness, env: Env) -> dict[str, Published]:
    return {
        name: publish_document(api.session, env, PUBLISHABLE[name](), tag=f"zzc{index}x")
        for index, name in enumerate([*MCQ_NAMES, *STRUCTURED_NAMES])
    }


# --- requests ----------------------------------------------------------------------------------


def mcq_answer(key: str) -> Json:
    return {"kind": "mcq", "selected_key": key}


def written_answer(part_id: str, answer: str = ENGLISH) -> Json:
    return {"kind": "written", "part_id": part_id, "text": answer}


def answer(api: ApiHarness, question_id: str, body: Any, *roles: Role) -> Any:
    return api.client.post(
        f"/v1/questions/{question_id}/answers",
        json=body,
        headers=api.headers(*roles or (Role.STUDENT,)),
    )


def correct_key_of(item: Published) -> str:
    assert item.document.mcq is not None
    return item.document.mcq.correct_key


def assert_problem(response: Any, status: int, code: str) -> None:
    assert response.status_code == status, response.text
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == code


# --- what must not change ------------------------------------------------------------------------


def public_tables(connection: Connection) -> list[str]:
    return [
        row[0]
        for row in connection.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY 1")
        )
    ]


def fingerprint(connection: Connection) -> dict[str, tuple[int, str]]:
    """Row count and a hash of the content of every table of the database."""
    result: dict[str, tuple[int, str]] = {}
    for name in public_tables(connection):
        rows = sorted(
            connection.execute(text(f'SELECT t::text FROM "{name}" t')).scalars()  # noqa: S608
        )
        digest = hashlib.sha256("\n".join(rows).encode()).hexdigest()
        result[name] = (len(rows), digest)
    return result


def tables_containing(connection: Connection, needle: str) -> list[str]:
    found = []
    for name in public_tables(connection):
        hits = connection.execute(
            text(f'SELECT count(*) FROM "{name}" t WHERE t::text LIKE :n'),  # noqa: S608
            {"n": f"%{needle}%"},
        ).scalar_one()
        if hits:
            found.append(name)
    return found


def audit_count(connection: Connection) -> int:
    return int(connection.execute(text("SELECT count(*) FROM audit_log")).scalar_one())


# =============================================================================================
# Multiple choice
# =============================================================================================


@pytest.mark.parametrize("name", MCQ_NAMES)
def test_the_right_option_is_correct_and_the_others_are_not(
    api: ApiHarness, world: dict[str, Published], name: str
) -> None:
    item = world[name]
    right = correct_key_of(item)

    for key in "ABCD":
        response = answer(api, item.id, mcq_answer(key))
        assert response.status_code == 201, response.text
        body = response.json()
        assert set(body) == {
            "kind",
            "response_id",
            "version_id",
            "correct",
            "correct_key",
            "explanation",
            "rationales",
        }
        out = McqResult.model_validate(body)
        assert out.kind == "mcq"
        assert out.version_id == vid(item.view)
        assert out.correct is (key == right)
        assert out.correct_key == right


def test_a_wrong_answer_still_reveals_the_correct_option(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["plain_mcq"]  # the right option is C
    body = answer(api, item.id, mcq_answer("A")).json()
    assert body["correct"] is False
    assert body["correct_key"] == "C"


@pytest.mark.parametrize("name", MCQ_NAMES)
def test_an_mcq_answer_carries_the_explanation_and_a_rationale_per_wrong_option(
    api: ApiHarness, world: dict[str, Published], name: str
) -> None:
    item = world[name]
    mcq = item.document.mcq
    assert mcq is not None
    for key in "ABCD":
        response = answer(api, item.id, mcq_answer(key))
        # Nothing but the explanation and the rationales of the author's private text.
        assert_clean(response.text, author_secrets(world), MCQ_FORBIDDEN)
        out = McqResult.model_validate(response.json())
        assert out.explanation == mcq.explanation
        wrong = [o for o in mcq.options if o.key != mcq.correct_key]
        assert [(r.key, r.content) for r in out.rationales] == [(o.key, o.rationale) for o in wrong]
        assert out.correct_key not in [r.key for r in out.rationales]
        # The planted text of the explanation and of each wrong option arrives; the correct
        # option's own rationale does not.
        for sentinel in item.sentinels.hidden:
            if "explanation" in sentinel:
                assert sentinel in response.text
            elif "rationale" in sentinel:
                assert (sentinel in response.text) is (
                    not sentinel.endswith(mcq.correct_key.lower())
                )


def test_an_mcq_without_an_explanation_returns_null(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzne", plant=False)
    assert item.document.mcq is not None
    explained = item.document.mcq.explanation is not None
    body = answer(api, item.id, mcq_answer("C")).json()
    assert (body["explanation"] is not None) is explained
    assert len(body["rationales"]) == 3


def test_answering_is_repeatable_and_every_submission_is_a_new_row(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["mcq"]
    first = answer(api, item.id, mcq_answer("B"))
    second = answer(api, item.id, mcq_answer("B"))
    assert first.status_code == second.status_code == 201
    one, two = first.json(), second.json()
    assert one["response_id"] != two["response_id"]
    assert {**one, "response_id": ""} == {**two, "response_id": ""}


@pytest.mark.parametrize("role", ALL_ROLES)
def test_every_role_can_submit_an_mcq_answer(
    api: ApiHarness, world: dict[str, Published], role: Role
) -> None:
    item = world["mcq"]
    response = answer(api, item.id, mcq_answer("A"), role)
    assert response.status_code == 201
    assert response.json()["correct"] is True


def test_no_token_is_401(api: ApiHarness, world: dict[str, Published]) -> None:
    item = world["mcq"]
    response = api.client.post(f"/v1/questions/{item.id}/answers", json=mcq_answer("A"))
    assert_problem(response, 401, "unauthenticated")
    assert response.headers["www-authenticate"] == "Bearer"


def test_a_bad_token_is_401(api: ApiHarness, world: dict[str, Published]) -> None:
    response = api.client.post(
        f"/v1/questions/{world['mcq'].id}/answers",
        json=mcq_answer("A"),
        headers={"Authorization": "Bearer not.a.token"},
    )
    assert_problem(response, 401, "unauthenticated")


def test_an_account_without_a_role_gets_404(api: ApiHarness, world: dict[str, Published]) -> None:
    assert answer(api, world["mcq"].id, mcq_answer("A")).status_code == 201
    response = api.client.post(
        f"/v1/questions/{world['mcq'].id}/answers", json=mcq_answer("A"), headers=api.headers()
    )
    assert_problem(response, 404, "not_found")


# =============================================================================================
# Written answers
# =============================================================================================


def assert_part_scheme(body: Json, item: Published, part_id: str) -> None:
    part = next(p for p in item.document.parts if p.id == part_id)
    assert set(body) == {
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
    out = WrittenResult.model_validate(body)  # refuses unknown fields
    assert out.kind == "written"
    assert out.version_id == vid(item.view)
    assert out.part_id == part.id
    assert out.marks == part.marks
    assert out.marks_capped is part.marks_capped
    assert [
        (m.id, m.content, m.kind, m.alternative_group, m.route, m.accept_range)
        for m in out.mark_points
    ] == [
        (m.id, m.content, m.kind, m.alternative_group, m.route, m.accept_range)
        for m in part.mark_points
    ]
    assert [(n.kind, n.content, n.mark_point_id) for n in out.notes] == [
        (n.kind, n.content, n.mark_point_id) for n in part.notes
    ]
    for point in body["mark_points"]:
        assert set(point) == {
            "id",
            "content",
            "kind",
            "alternative_group",
            "route",
            "accept_range",
        }
    for note in body["notes"]:
        assert set(note) == {"kind", "content", "mark_point_id"}


def part_cases() -> list[tuple[str, str]]:
    return [
        (name, part["id"]) for name in STRUCTURED_NAMES for part in PUBLISHABLE[name]()["parts"]
    ]


@pytest.mark.parametrize(("name", "part_id"), part_cases())
def test_a_written_answer_returns_exactly_that_parts_mark_scheme(
    api: ApiHarness, world: dict[str, Published], name: str, part_id: str
) -> None:
    item = world[name]

    response = answer(api, item.id, written_answer(part_id))

    assert response.status_code == 201, response.text
    assert_part_scheme(response.json(), item, part_id)


@pytest.mark.parametrize(("name", "part_id"), part_cases())
def test_a_written_answer_returns_no_other_part_and_nothing_hidden(
    api: ApiHarness, world: dict[str, Published], name: str, part_id: str
) -> None:
    item = world[name]
    response = answer(api, item.id, written_answer(part_id))
    body = response.text

    own = item.sentinels.mark_points.get(part_id, []) + item.sentinels.notes.get(part_id, [])
    assert own, "the test document must plant sentinels in this part"
    for sentinel in own:
        assert sentinel in body.lower(), f"{sentinel} missing from its own part"
    others = [
        s
        for other_id, group in item.sentinels.mark_points.items()
        if other_id != part_id
        for s in group
    ]
    others += [
        s for other_id, group in item.sentinels.notes.items() if other_id != part_id for s in group
    ]
    # Sentinels of every other question go too.
    for other_name, other in world.items():
        if other_name != name:
            others += other.sentinels.all()
    assert_clean(body, [*item.sentinels.hidden, *others], WRITTEN_FORBIDDEN)


def test_the_mark_scheme_of_a_part_with_notes_includes_them(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["show_that"]
    body = answer(api, item.id, written_answer("p-b")).json()

    assert [n["kind"] for n in body["notes"]] == ["ecf", "do_not_accept"]
    assert body["notes"][0]["mark_point_id"] is None
    assert body["notes"][1]["mark_point_id"] == "b-2"
    assert [m["id"] for m in body["mark_points"]] == ["b-1", "b-2", "b-3", "b-4"]
    assert [m["route"] for m in body["mark_points"]] == ["r1", "r1", "r2", "r2"]
    assert body["mark_points"][1]["accept_range"] == {
        "minimum": "14.5",
        "maximum": "15.5",
        "unit": "rad/s",
    }
    assert body["marks"] == 2
    assert body["marks_capped"] is False


def test_alternatives_and_the_cap_are_reported(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["show_that"]

    first = answer(api, item.id, written_answer("p-a")).json()
    capped = answer(api, item.id, written_answer("p-c")).json()

    assert [m["alternative_group"] for m in first["mark_points"]] == ["g1", "g1"]
    assert first["marks"] == 1 and first["marks_capped"] is False
    assert capped["marks"] == 2 and capped["marks_capped"] is True
    assert len(capped["mark_points"]) == 3
    assert [n["kind"] for n in capped["notes"]] == ["cap"]


def test_a_part_without_notes_has_an_empty_note_list(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    body = answer(api, world["data_based"].id, written_answer("p-a-i")).json()
    assert body["notes"] == []
    assert body["marks_capped"] is True


def test_the_answer_is_not_marked(api: ApiHarness, world: dict[str, Published]) -> None:
    body = answer(api, world["structured"].id, written_answer("p-a", "34 m/s")).json()
    assert not ({"score", "awarded", "awarded_marks", "correct", "mark"} & keys_in(body))


@pytest.mark.parametrize("role", ALL_ROLES)
def test_every_role_can_submit_a_written_answer(
    api: ApiHarness, world: dict[str, Published], role: Role
) -> None:
    response = answer(api, world["structured"].id, written_answer("p-a"), role)
    assert response.status_code == 201


def test_the_answer_answers_for_the_published_version_only(api: ApiHarness, env: Env) -> None:
    item = publish_document(
        api.session, env, samples.plain_mcq_document(), tag="zzver", plant=False
    )
    assert answer(api, item.id, mcq_answer("C")).json()["version_id"] == vid(item.view)

    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)
    assert answer(api, item.id, mcq_answer("C")).json()["version_id"] == vid(item.view)

    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    approve(api.session, revision.id, actor=STAFF)
    assert answer(api, item.id, mcq_answer("C")).json()["version_id"] == vid(item.view)

    publish(api.session, revision.id, actor=STAFF)
    body = answer(api, item.id, mcq_answer("C")).json()
    assert body["version_id"] == vid(revision)
    assert body["version_id"] != vid(item.view)


# =============================================================================================
# The language hint
# =============================================================================================


def test_a_turkish_sentence_gets_the_warning_and_still_gets_the_mark_scheme(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["show_that"]
    response = answer(api, item.id, written_answer("p-c", TURKISH))
    assert response.status_code == 201
    body = response.json()

    assert body["language_warning"] == WARNING
    assert_part_scheme({**body, "language_warning": None}, item, "p-c")


def test_an_english_sentence_gets_no_warning(api: ApiHarness, world: dict[str, Published]) -> None:
    body = answer(api, world["show_that"].id, written_answer("p-c", ENGLISH)).json()
    assert body["language_warning"] is None
    assert "language_warning" in body
    assert len(body["mark_points"]) == 3


@pytest.mark.parametrize(
    "sentence",
    ["15", "3.0 s", "15 rad/s", "w = alpha * t", "6.0 / 0.40 = 15", "-9.8e-3", "F = m a", "x"],
)
def test_numbers_and_formulas_get_no_warning(
    api: ApiHarness, world: dict[str, Published], sentence: str
) -> None:
    body = answer(api, world["show_that"].id, written_answer("p-b", sentence)).json()
    assert body["language_warning"] is None
    assert len(body["mark_points"]) == 4


@pytest.mark.parametrize(
    "sentence",
    [
        "Cismin hızı zamanla artar",
        "Topun ivmesi sabit kalır",
        "Işık bir dalga olarak yayılır",
        "açısal hız artar çünkü tork vardır",
    ],
)
def test_other_turkish_sentences_get_the_warning(
    api: ApiHarness, world: dict[str, Published], sentence: str
) -> None:
    body = answer(api, world["show_that"].id, written_answer("p-c", sentence)).json()
    assert body["language_warning"] == WARNING
    assert len(body["mark_points"]) == 3


def test_the_warning_is_the_same_for_every_part_and_does_not_depend_on_the_part(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["show_that"]
    for part_id in ("p-a", "p-b", "p-c"):
        body = answer(api, item.id, written_answer(part_id, TURKISH)).json()
        assert body["language_warning"] == WARNING


def test_an_mcq_answer_has_no_language_field(api: ApiHarness, world: dict[str, Published]) -> None:
    assert "language_warning" not in answer(api, world["mcq"].id, mcq_answer("A")).json()


# =============================================================================================
# Requests that do not fit the question
# =============================================================================================


def test_an_mcq_answer_to_a_structured_question_does_not_fit(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    everything = [s for item in world.values() for s in item.sentinels.all()]
    for name in STRUCTURED_NAMES:
        response = answer(api, world[name].id, mcq_answer("A"))
        assert_problem(response, 422, "answer_does_not_fit")
        assert_clean(response.text, everything, WRITTEN_FORBIDDEN)


def test_a_written_answer_to_an_mcq_question_does_not_fit(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    everything = [s for item in world.values() for s in item.sentinels.all()]
    for name in MCQ_NAMES:
        for part_id in ("mcq", "p-a", "a"):
            response = answer(api, world[name].id, written_answer(part_id))
            assert_problem(response, 422, "answer_does_not_fit")
            assert_clean(response.text, everything, WRITTEN_FORBIDDEN)


@pytest.mark.parametrize("part_id", ["p-zz", "a", "p-a-i", "0", "p-a.b", "x" * 64])
def test_an_unknown_part_does_not_fit(
    api: ApiHarness, world: dict[str, Published], part_id: str
) -> None:
    response = answer(api, world["structured"].id, written_answer(part_id))
    assert_problem(response, 422, "answer_does_not_fit")


def test_a_part_of_another_question_does_not_fit(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    # p-a-i belongs to the data-based question only.
    assert answer(api, world["data_based"].id, written_answer("p-a-i")).status_code == 201
    response = answer(api, world["structured"].id, written_answer("p-a-i"))
    assert_problem(response, 422, "answer_does_not_fit")


def test_a_part_id_is_matched_exactly(api: ApiHarness, world: dict[str, Published]) -> None:
    for wrong in ("p-A", "P-A", "p_a", "p-a ", " p-a", "p-a\n"):
        response = answer(api, world["structured"].id, written_answer(wrong))
        assert_problem(response, 422, "answer_does_not_fit")


ODD_PART_IDS = [
    "P A",
    "ş",
    "<script>x</script>",
    "'; DROP TABLE part; --",
    "p-a\u0000",
    "\u0000",
    "../p-a",
    "p-a%20",
    "\U0001f600",
    "a" * 200,
]


@pytest.mark.parametrize("part_id", ODD_PART_IDS)
def test_a_part_id_naming_no_part_is_does_not_fit_whatever_its_characters(
    api: ApiHarness, world: dict[str, Published], part_id: str
) -> None:
    for name in ("structured", "mcq"):
        response = answer(api, world[name].id, written_answer(part_id))
        assert_problem(response, 422, "answer_does_not_fit")


@pytest.mark.parametrize("part_id", ["", "x" * 201, "x" * 5000])
def test_an_empty_or_too_long_part_id_is_validation_failed(
    api: ApiHarness, world: dict[str, Published], part_id: str
) -> None:
    for name in ("structured", "mcq"):
        assert_problem(
            answer(api, world[name].id, written_answer(part_id)), 422, "validation_failed"
        )


def test_a_part_id_of_seventy_characters_can_be_published_read_and_answered(
    api: ApiHarness, env: Env
) -> None:
    long_id = "p" + "-x" * 34 + "a"
    assert len(long_id) == 70
    source = json.loads(json.dumps(structured_without_figure()).replace('"p-a"', f'"{long_id}"'))
    item = publish_document(api.session, env, source, tag="zzlongx")
    assert long_id in [part.id for part in item.document.parts]

    read = api.client.get(f"/v1/questions/{item.id}", headers=api.headers(Role.STUDENT))
    assert read.status_code == 200, read.text
    assert long_id in [part["id"] for part in read.json()["parts"]]

    response = answer(api, item.id, written_answer(long_id))
    assert response.status_code == 201, response.text
    assert response.json()["part_id"] == long_id
    assert_part_scheme(response.json(), item, long_id)
    # The other part is still addressed by its own id.
    assert answer(api, item.id, written_answer("p-b")).json()["part_id"] == "p-b"


def test_a_422_for_a_misfit_leaks_no_mark_scheme(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["show_that"]
    everything = [s for s in item.sentinels.all()]
    response = answer(api, item.id, written_answer("p-zz"))
    assert_problem(response, 422, "answer_does_not_fit")
    assert_clean(response.text, everything, WRITTEN_FORBIDDEN)
    assert not ({"mark_points", "notes", "correct_key"} & keys_in(response.json()))


# =============================================================================================
# Requests that are not valid
# =============================================================================================


@pytest.mark.parametrize("blank", ["", " ", "   ", "\n", "\t \n", " ", "  ", "\r\n"])
def test_an_empty_or_blank_answer_is_422(
    api: ApiHarness, world: dict[str, Published], blank: str
) -> None:
    response = answer(api, world["structured"].id, written_answer("p-a", blank))
    assert_problem(response, 422, "validation_failed")


def test_an_answer_with_surrounding_space_is_accepted(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    response = answer(api, world["structured"].id, written_answer("p-a", "  3.0 s \n"))
    assert response.status_code == 201


def test_the_longest_answer_is_accepted_and_one_more_is_not(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["structured"]
    assert answer(api, item.id, written_answer("p-a", "x" * 5000)).status_code == 201
    assert answer(api, item.id, written_answer("p-a", "ş" * 5000)).status_code == 201
    over = answer(api, item.id, written_answer("p-a", "x" * 5001))
    assert_problem(over, 422, "validation_failed")
    # A body above the 64 KiB limit of this endpoint is refused before it is read.
    assert_problem(
        answer(api, item.id, written_answer("p-a", "x" * 100_000)), 413, "payload_too_large"
    )


@pytest.mark.parametrize(
    "body",
    [
        {"kind": "mcq", "selected_key": "A", "extra": 1},
        {"kind": "mcq", "selected_key": "A", "text": "no"},
        {"kind": "mcq", "selected_key": "A", "part_id": "p-a"},
        {"kind": "written", "part_id": "p-a", "text": "3.0 s", "extra": True},
        {"kind": "written", "part_id": "p-a", "text": "3.0 s", "selected_key": "A"},
    ],
)
def test_unknown_fields_are_rejected(
    api: ApiHarness, world: dict[str, Published], body: Json
) -> None:
    for name in ("mcq", "structured"):
        assert_problem(answer(api, world[name].id, body), 422, "validation_failed")


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"kind": "mcq"},
        {"kind": "mcq", "selected_key": "E"},
        {"kind": "mcq", "selected_key": "a"},
        {"kind": "mcq", "selected_key": ""},
        {"kind": "mcq", "selected_key": None},
        {"kind": "mcq", "selected_key": 1},
        {"kind": "mcq", "selected_key": ["A"]},
        {"kind": "written"},
        {"kind": "written", "part_id": "p-a"},
        {"kind": "written", "text": "3.0 s"},
        {"kind": "written", "part_id": "", "text": "3.0 s"},
        {"kind": "written", "part_id": "x" * 201, "text": "3.0 s"},
        {"kind": "written", "part_id": "p-a", "text": 5},
        {"kind": "written", "part_id": "p-a", "text": None},
        {"kind": "essay", "text": "x"},
        {"kind": None},
        {"selected_key": "A"},
        {"part_id": "p-a", "text": "3.0 s"},
    ],
)
def test_a_malformed_body_is_422(api: ApiHarness, world: dict[str, Published], body: Json) -> None:
    for name in ("mcq", "structured"):
        assert_problem(answer(api, world[name].id, body), 422, "validation_failed")


@pytest.mark.parametrize(
    "body", [[], ["mcq"], "mcq", 5, None, [{"kind": "mcq", "selected_key": "A"}]]
)
def test_a_body_that_is_not_an_object_is_422(
    api: ApiHarness, world: dict[str, Published], body: Any
) -> None:
    assert_problem(answer(api, world["mcq"].id, body), 422, "validation_failed")


def test_a_missing_or_unparsable_body_is_422(api: ApiHarness, world: dict[str, Published]) -> None:
    url = f"/v1/questions/{world['mcq'].id}/answers"
    headers = api.headers(Role.STUDENT)
    assert_problem(api.client.post(url, headers=headers), 422, "validation_failed")
    broken = api.client.post(
        url, content=b'{"kind": "mcq", ', headers={**headers, "Content-Type": "application/json"}
    )
    assert_problem(broken, 422, "validation_failed")


def test_a_validation_error_does_not_echo_the_answer(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    needle = "zzechoneedle"
    response = answer(api, world["structured"].id, written_answer("p-a", needle + "x" * 5000))
    assert response.status_code == 422
    assert needle not in response.text
    response = answer(
        api,
        world["structured"].id,
        {"kind": "written", "part_id": "p-a", "text": needle, "z": needle},
    )
    assert response.status_code == 422
    assert needle not in response.text


def test_the_other_methods_on_the_answer_url_are_refused(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    url = f"/v1/questions/{world['mcq'].id}/answers"
    headers = api.headers(Role.PLATFORM_ADMIN)
    for method in ("get", "put", "delete", "patch"):
        assert getattr(api.client, method)(url, headers=headers).status_code in (404, 405)


# =============================================================================================
# Not published, withdrawn, rights revoked: 404
# =============================================================================================

NOT_PUBLISHED = ["draft", "needs_fix", "in_review", "approved", "rejected", "withdrawn"]


@pytest.mark.parametrize("status", NOT_PUBLISHED)
def test_a_version_that_is_not_published_is_a_404(api: ApiHarness, env: Env, status: str) -> None:
    hidden = bring_to(
        api.session, api.session.connection(), env, status, document(samples.mcq_document())
    )
    assert_not_found(answer(api, qid(hidden), mcq_answer("A")))


@pytest.mark.parametrize("status", NOT_PUBLISHED)
def test_a_misfit_to_a_question_that_is_not_published_is_still_a_404(
    api: ApiHarness, env: Env, status: str
) -> None:
    # The kind of answer must not tell a learner anything about an unpublished question.
    hidden = bring_to(
        api.session, api.session.connection(), env, status, document(samples.mcq_document())
    )
    assert_not_found(answer(api, qid(hidden), written_answer("p-a")))
    assert_not_found(answer(api, qid(hidden), written_answer("mcq")))
    structured = bring_to(
        api.session,
        api.session.connection(),
        env,
        status,
        document(structured_without_figure()),
    )
    assert_not_found(answer(api, qid(structured), mcq_answer("A")))
    assert_not_found(answer(api, qid(structured), written_answer("p-zz")))


def test_a_withdrawn_question_can_no_longer_be_answered(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzwd", plant=False)
    assert answer(api, item.id, mcq_answer("C")).status_code == 201

    svc.withdraw(api.session, actor=STAFF, version_id=item.view.id, reason="taken down")

    assert_not_found(answer(api, item.id, mcq_answer("C")))


def test_a_question_whose_rights_are_revoked_can_no_longer_be_answered(
    api: ApiHarness, env: Env
) -> None:
    record = new_rights(api.session)
    item = publish_document(
        api.session,
        env,
        samples.plain_mcq_document(),
        tag="zzrr",
        plant=False,
        rights_record_id=record,
    )
    assert answer(api, item.id, mcq_answer("C")).status_code == 201

    rights.revoke(api.session, record, at=now())

    for role in ALL_ROLES:
        assert_not_found(answer(api, item.id, mcq_answer("C"), role))


def test_the_404_of_a_hidden_question_equals_that_of_a_missing_one(
    api: ApiHarness, env: Env
) -> None:
    hidden = bring_to(
        api.session, api.session.connection(), env, "draft", document(samples.mcq_document())
    )
    nothing = api.client.get("/v1/nothing-here", headers=api.headers(Role.STUDENT))
    for question_id in (qid(hidden), ids.encode(ids.QUESTION, uuid.uuid4()), "q_notanidentifier"):
        response = answer(api, question_id, mcq_answer("A"))
        assert response.status_code == 404
        assert response.content == nothing.content


@pytest.mark.parametrize(
    "bad",
    ["q_", "q_short", "not-an-id", str(uuid.uuid4()), "q_" + "u" * 26, "q_" + "z" * 26],
)
def test_a_malformed_question_id_is_404_even_with_a_valid_body(
    api: ApiHarness, world: dict[str, Published], bad: str
) -> None:
    assert_not_found(answer(api, bad, mcq_answer("A")))
    assert_not_found(answer(api, bad, written_answer("p-a")))


def test_a_version_id_does_not_open_a_answer(api: ApiHarness, world: dict[str, Published]) -> None:
    assert_not_found(answer(api, vid(world["mcq"].view), mcq_answer("A")))


# =============================================================================================
# Only `response` is written
# =============================================================================================


def changed_tables(before: dict[str, tuple[int, str]], connection: Connection) -> set[str]:
    after = fingerprint(connection)
    return {name for name in after if after[name] != before.get(name)}


def test_a_successful_mcq_answer_changes_only_the_response_table(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["mcq"]
    api.headers(Role.STUDENT)
    api.session.flush()
    connection = api.session.connection()
    before = fingerprint(connection)
    audit_before = audit_count(connection)

    for key in "ABCD":
        assert answer(api, item.id, mcq_answer(key)).status_code == 201

    assert changed_tables(before, connection) == {"response"}
    assert fingerprint(connection)["response"][0] == 4
    assert audit_count(connection) == audit_before


def test_a_successful_written_answer_changes_only_the_response_table(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["show_that"]
    api.headers(Role.STUDENT)
    api.session.flush()
    connection = api.session.connection()
    before = fingerprint(connection)
    audit_before = audit_count(connection)

    for part_id in ("p-a", "p-b", "p-c"):
        assert answer(api, item.id, written_answer(part_id)).status_code == 201
        assert answer(api, item.id, written_answer(part_id, TURKISH)).status_code == 201

    assert changed_tables(before, connection) == {"response"}
    assert fingerprint(connection)["response"][0] == 6
    assert audit_count(connection) == audit_before


def test_failing_answers_change_no_table(
    api: ApiHarness, env: Env, world: dict[str, Published]
) -> None:
    hidden = bring_to(
        api.session, api.session.connection(), env, "draft", document(samples.mcq_document())
    )
    api.headers(Role.STUDENT)
    api.headers()
    api.session.flush()
    connection = api.session.connection()
    before = fingerprint(connection)
    audit_before = audit_count(connection)

    requests: list[tuple[str, Any]] = [
        (world["structured"].id, mcq_answer("A")),  # does not fit
        (world["mcq"].id, written_answer("p-a")),  # does not fit
        (world["structured"].id, written_answer("p-zz")),  # unknown part
        (world["structured"].id, written_answer("p-a", "  ")),  # blank
        (world["structured"].id, written_answer("p-a", "x" * 5001)),  # too long
        (world["structured"].id, {"kind": "mcq", "selected_key": "Z"}),  # invalid
        (qid(hidden), mcq_answer("A")),  # not published
        ("q_notanidentifier", mcq_answer("A")),  # malformed id
        (ids.encode(ids.QUESTION, uuid.uuid4()), mcq_answer("A")),  # unknown id
    ]
    for question_id, body in requests:
        assert answer(api, question_id, body).status_code in (404, 422)
    api.client.post(f"/v1/questions/{world['mcq'].id}/answers", json=mcq_answer("A"))  # no token
    api.client.post(
        f"/v1/questions/{world['mcq'].id}/answers", json=mcq_answer("A"), headers=api.headers()
    )  # no role

    assert fingerprint(connection) == before
    assert audit_count(connection) == audit_before


def test_the_answer_text_is_in_no_table_but_response(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["show_that"]
    connection = api.session.connection()
    needle = "zzanswerneedleone"
    answers = [
        f"{needle} the torque does work on the disc",
        f"{needle} Tork disk üzerinde iş yapar çünkü açısal hız artar",
        f"  {needle}  ",
    ]
    for text_ in answers:
        assert answer(api, item.id, written_answer("p-c", text_)).status_code == 201
    # Also when the request fails after the answer was parsed.
    answer(api, world["mcq"].id, written_answer("p-a", needle))
    answer(api, item.id, written_answer("p-zz", needle))
    answer(api, item.id, {"kind": "written", "part_id": "p-c", "text": needle, "z": 1})

    assert tables_containing(connection, needle) == ["response"]
    count = connection.execute(
        text("SELECT count(*) FROM response WHERE payload->>'text' LIKE :n"), {"n": f"%{needle}%"}
    ).scalar_one()
    assert count == 3  # the failed requests stored nothing


def test_the_answer_text_is_not_written_to_the_log(
    api: ApiHarness, world: dict[str, Published], caplog: pytest.LogCaptureFixture
) -> None:
    item = world["show_that"]
    needle = "zzlogneedletwo"
    caplog.set_level(logging.DEBUG)

    answer(api, item.id, written_answer("p-c", f"{needle} the torque does work"))
    answer(api, item.id, written_answer("p-zz", needle))
    answer(api, world["mcq"].id, written_answer("p-a", needle))
    answer(api, item.id, {"kind": "written", "part_id": "p-c", "text": needle, "z": 1})

    assert needle not in caplog.text


def test_the_answer_is_not_echoed_in_the_response(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    needle = "zzechoneedlethree"
    response = answer(api, world["show_that"].id, written_answer("p-c", f"{needle} is my answer"))
    assert response.status_code == 201
    assert needle not in response.text


def test_answering_writes_no_audit_entry_for_the_answering_account(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    actor = api.actor(Role.STUDENT)
    answer(api, world["mcq"].id, mcq_answer("A"))
    answer(api, world["show_that"].id, written_answer("p-c"))
    api.session.flush()
    connection = api.session.connection()

    hits = connection.execute(
        text("SELECT count(*) FROM audit_log WHERE actor = :a"), {"a": actor}
    ).scalar_one()
    assert hits == 0


def test_before_a_answer_no_response_contains_the_answer(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    # Reading the question and the list gives neither the right option nor any mark point.
    everything = [s for item in world.values() for s in item.sentinels.all()]
    for item in world.values():
        response = api.client.get(f"/v1/questions/{item.id}", headers=api.headers(Role.STUDENT))
        assert_clean(response.text, everything, WRITTEN_FORBIDDEN | {"correct_key"})
    listing = api.client.get("/v1/questions", headers=api.headers(Role.STUDENT))
    assert_clean(listing.text, everything, WRITTEN_FORBIDDEN | {"correct_key"})


def test_answering_changes_only_the_answered_flag_of_the_question_view(
    api: ApiHarness, world: dict[str, Published]
) -> None:
    item = world["structured"]
    headers = api.headers(Role.STUDENT)
    before = api.client.get(f"/v1/questions/{item.id}", headers=headers).json()

    answer(api, item.id, written_answer("p-a"))

    after = api.client.get(f"/v1/questions/{item.id}", headers=headers).json()
    assert (before["answered"], after["answered"]) == (False, True)
    assert {**after, "answered": False} == before
    # and the question view still holds no mark scheme after a check
    assert not ({"mark_points", "notes", "correct_key"} & keys_in(before))
