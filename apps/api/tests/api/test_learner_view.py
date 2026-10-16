"""The learner view through the HTTP API: `GET /v1/questions/{id}` and `GET /v1/questions`
(docs/slices/M1G-5-YETKILER.md sections 1 (rows 4 and 5), 3.1 and 4; docs/slices/M1G-5-SOZLESME.md
sections 3.2 and 3.3; CLAUDE.md rules 2, 7 and 13).

What is checked here, from the outside only:

- nothing a learner must not see appears in any response body (sentinel strings planted in every
  answer, explanation, rationale, outcome, solution model, mark scheme and staff identifier, and a
  list of forbidden key names);
- what a learner may see is present and equals the stored document;
- only the published version is visible, and only while the rights record permits display;
- the list filters, orders and paginates.

Stimulus descriptions and alt texts cannot be planted in a published question: a question with a
stimulus cannot be published (D-49, the database refuses it). That part of the allow-list is
covered by the unpublished-visual test and by the contract tests on the `Learner*` types.
"""

from __future__ import annotations

import copy
import json
import time
import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from qlab.api import ids
from qlab.api import schemas as api_schemas
from qlab.api.schemas import LearnerQuestion, LearnerQuestionPage
from qlab.content import service as svc
from qlab.content.schema import QuestionDocument
from qlab.organizations.service import Role
from qlab.rights import service as rights
from tests.api.support import ALL_ROLES, ApiHarness
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
    republish,
    table_counts,
)

pytestmark = [pytest.mark.db, pytest.mark.node]

Json = dict[str, Any]

STAFF = "u_zzactorsentinel"
SOURCE_REF_SENTINEL = "zzsourcerefsentinel"

# Key names that must not occur anywhere in a learner response (docs/slices/M1G-5-SOZLESME.md
# section 4, acceptance criteria; the task of this suite).
FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {
        "correct_key",
        "rationale",
        "explanation",
        "outcome",
        "description",
        "alt_text",
        "mark_points",
        "notes",
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


# --- sentinels ---------------------------------------------------------------------------------


@dataclass
class Sentinels:
    """Recognisable strings planted in a document, grouped by what they sit in."""

    hidden: list[str] = field(default_factory=list)  # never visible to a learner, ever
    mark_points: dict[str, list[str]] = field(default_factory=dict)  # by part id
    notes: dict[str, list[str]] = field(default_factory=dict)  # by part id

    def all(self) -> list[str]:
        result = list(self.hidden)
        for group in (*self.mark_points.values(), *self.notes.values()):
            result.extend(group)
        return result


def _append(doc: Json, sentinel: str) -> Json:
    out = copy.deepcopy(doc)
    out["content"].append(samples.paragraph(samples.text(sentinel)))
    return out


def sentinelize(source: Json, tag: str) -> tuple[Json, Sentinels]:
    """A copy of `source` with a unique lower-case sentinel in every field a learner must never
    see (and one in each mark point and note, for the check endpoint's tests)."""
    d = copy.deepcopy(source)
    found = Sentinels()

    def hidden(name: str) -> str:
        value = f"{tag}{name}"
        found.hidden.append(value)
        return value

    d["outcome"] = hidden("outcome")
    mcq = d.get("mcq")
    if mcq is not None:
        mcq["explanation"] = samples.line(samples.text(hidden("explanation")))
        for option in mcq["options"]:
            option["rationale"] = samples.line(
                samples.text(hidden(f"rationale{option['key'].lower()}"))
            )
    for part in d.get("parts", []):
        pid = part["id"].replace("-", "")
        for point in part["mark_points"]:
            value = f"{tag}mark{point['id'].replace('-', '')}"
            found.mark_points.setdefault(part["id"], []).append(value)
            point["content"] = _append(point["content"], value)
        for index, note in enumerate(part.get("notes", [])):
            value = f"{tag}note{pid}{index}"
            found.notes.setdefault(part["id"], []).append(value)
            note["content"] = _append(note["content"], value)
    model = d.get("solution_model") or {}
    model.setdefault("parameters", []).append({"name": hidden("param"), "value": "1", "unit": ""})
    model.setdefault("constants", []).append({"name": hidden("const"), "ref": hidden("ref")})
    model.setdefault("steps", []).append(
        {"id": hidden("stepid"), "name": hidden("stepname"), "expr": "1 + 1"}
    )
    d["solution_model"] = model
    found.hidden.extend([STAFF, SOURCE_REF_SENTINEL])
    return d, found


def structured_without_figure() -> Json:
    """The two-part structured sample with its stimulus taken out, so that it can be published."""
    d = samples.structured_document()
    d["stem"]["content"] = [b for b in d["stem"]["content"] if b["type"] != "figure"]
    d["stimuli"] = []
    for part in d["parts"]:
        part["stimulus_refs"] = []
    return d


# name -> builder; every one of these can be published.
PUBLISHABLE: dict[str, Callable[[], Json]] = {
    "mcq": samples.mcq_document,
    "plain_mcq": samples.plain_mcq_document,
    "two_column_mcq": samples.two_column_mcq_document,
    "roman_mcq": samples.roman_mcq_document,
    "structured": structured_without_figure,
    "data_based": samples.data_based_document,
    "show_that": samples.show_that_document,
}


@dataclass
class Published:
    view: svc.QuestionVersionView
    sentinels: Sentinels

    @property
    def id(self) -> str:
        return qid(self.view)

    @property
    def document(self) -> QuestionDocument:
        return self.view.document


def qid(view: svc.QuestionVersionView) -> str:
    return ids.encode(ids.QUESTION, view.question_id)


def vid(view: svc.QuestionVersionView) -> str:
    return ids.encode(ids.QUESTION_VERSION, view.id)


def publish_document(
    session: Session,
    env: Env,
    source: Json,
    *,
    tag: str,
    plant: bool = True,
    rights_record_id: uuid.UUID | None = None,
) -> Published:
    """Create, submit, approve and publish a question through the service. `plant` puts the
    sentinels into the document and uses a sentinel staff identifier and source key."""
    data, found = sentinelize(source, tag) if plant else (copy.deepcopy(source), Sentinels())
    created = svc.create_question(
        session,
        actor=STAFF,
        document=QuestionDocument.model_validate(data),
        rights_record_id=rights_record_id or env.rights_record_id,
        syllabus_version_id=env.syllabus_version_id,
        source_ref=f"{SOURCE_REF_SENTINEL}/{tag}" if plant else None,
    )
    svc.submit(session, actor=STAFF, version_id=created.id)
    approve(session, created.id, actor=STAFF)
    publish(session, created.id, actor=STAFF)
    return Published(svc.get_version(session, created.id), found)


def publish_all(session: Session, env: Env) -> dict[str, Published]:
    return {
        name: publish_document(session, env, build(), tag=f"zz{index}x")
        for index, (name, build) in enumerate(PUBLISHABLE.items())
    }


# --- reading helpers -----------------------------------------------------------------------------


def keys_in(tree: Any) -> set[str]:
    if isinstance(tree, dict):
        found = {str(k) for k in tree}
        for value in tree.values():
            found |= keys_in(value)
        return found
    if isinstance(tree, list):
        found = set()
        for item in tree:
            found |= keys_in(item)
        return found
    return set()


def assert_clean(
    text: str, sentinels: Iterable[str], forbidden: frozenset[str] = FORBIDDEN_KEYS
) -> None:
    lowered = text.lower()
    for sentinel in sentinels:
        assert sentinel.lower() not in lowered, f"{sentinel} leaked"
    assert not (keys_in(json.loads(text)) & forbidden), keys_in(json.loads(text)) & forbidden


def assert_not_found(response: Any) -> None:
    assert response.status_code == 404, response.text
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "not_found"


def get_question(api: ApiHarness, question_id: str, *roles: Role) -> Any:
    return api.client.get(
        f"/v1/questions/{question_id}", headers=api.headers(*roles or (Role.STUDENT,))
    )


def list_questions(api: ApiHarness, *roles: Role, **params: Any) -> Any:
    return api.client.get(
        "/v1/questions", params=params, headers=api.headers(*roles or (Role.STUDENT,))
    )


def listed_ids(api: ApiHarness, **params: Any) -> list[str]:
    response = list_questions(api, limit=50, **params)
    assert response.status_code == 200, response.text
    return [item["id"] for item in response.json()["items"]]


def walk(client: TestClient, headers: dict[str, str], **params: Any) -> list[dict[str, Any]]:
    """Every page of a list, following `next_cursor`."""
    pages: list[dict[str, Any]] = []
    cursor: str | None = None
    for _ in range(1000):
        query = dict(params)
        if cursor is not None:
            query["cursor"] = cursor
        response = client.get("/v1/questions", params=query, headers=headers)
        assert response.status_code == 200, response.text
        page = response.json()
        pages.append(page)
        cursor = page["next_cursor"]
        if cursor is None:
            return pages
    raise AssertionError("pagination does not end")


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


# =============================================================================================
# Contract of the Learner* types
# =============================================================================================


def test_learner_types_have_no_field_named_like_a_forbidden_key() -> None:
    learner_models = [
        value
        for name, value in vars(api_schemas).items()
        if name.startswith("Learner") and hasattr(value, "model_fields")
    ]
    assert learner_models
    for model in learner_models:
        assert not (set(model.model_fields) & FORBIDDEN_KEYS), model.__name__


def test_learner_stimulus_and_option_carry_only_the_documented_fields() -> None:
    assert set(api_schemas.LearnerStimulus.model_fields) == {"id", "kind"}
    assert set(api_schemas.LearnerOption.model_fields) == {"key", "cells"}
    assert set(api_schemas.LearnerQuestionSummary.model_fields) == {
        "id",
        "version_id",
        "question_class",
        "exam_section",
        "levels",
        "total_marks",
        "topic",
        "answered",
    }


# =============================================================================================
# Leaks
# =============================================================================================


def test_the_sentinels_are_really_in_the_stored_documents(session: Session, env: Env) -> None:
    published = publish_all(session, env)
    for name, item in published.items():
        stored = item.document.model_dump_json().lower()
        for sentinel in item.sentinels.all():
            if sentinel in (STAFF, SOURCE_REF_SENTINEL):
                continue
            assert sentinel in stored, f"{name}: {sentinel} did not reach the document"
        assert item.view.created_by == STAFF


@pytest.mark.parametrize("role", ALL_ROLES)
def test_no_get_response_contains_a_sentinel_or_a_forbidden_key(
    api: ApiHarness, env: Env, role: Role
) -> None:
    published = publish_all(api.session, env)
    everything = [s for item in published.values() for s in item.sentinels.all()]

    for name, item in published.items():
        response = get_question(api, item.id, role)
        assert response.status_code == 200, (name, response.text)
        assert_clean(response.text, everything)


@pytest.mark.parametrize("role", ALL_ROLES)
def test_no_list_response_contains_a_sentinel_or_a_forbidden_key(
    api: ApiHarness, env: Env, role: Role
) -> None:
    published = publish_all(api.session, env)
    everything = [s for item in published.values() for s in item.sentinels.all()]

    response = list_questions(api, role, limit=50)

    assert response.status_code == 200
    assert len(response.json()["items"]) == len(published)
    assert_clean(response.text, everything)


def test_list_pages_and_filtered_lists_are_clean_too(api: ApiHarness, env: Env) -> None:
    published = publish_all(api.session, env)
    everything = [s for item in published.values() for s in item.sentinels.all()]
    headers = api.headers(Role.STUDENT)

    for params in ({"limit": 2}, {"exam_section": "paper_2"}, {"syllabus_node": "A.1"}, {}):
        response = api.client.get("/v1/questions", params=params, headers=headers)
        assert response.status_code == 200
        assert_clean(response.text, everything)


def test_error_responses_do_not_leak_either(api: ApiHarness, env: Env) -> None:
    published = publish_all(api.session, env)
    everything = [s for item in published.values() for s in item.sentinels.all()]
    pid = next(iter(published.values())).id

    responses = [
        get_question(api, "q_notanidentifier"),
        get_question(api, ids.encode(ids.QUESTION, uuid.uuid4())),
        list_questions(api, cursor="garbage"),
        list_questions(api, limit=0),
        api.client.get(f"/v1/questions/{pid}"),  # no token
    ]
    for response in responses:
        assert response.status_code in (401, 404, 422)
        assert_clean(response.text, everything)


def test_the_published_staff_view_does_hold_the_sentinels(session: Session, env: Env) -> None:
    # Guards the leak tests: the service view carries the hidden fields, so only the API layer
    # stands between them and a learner.
    item = publish_document(session, env, samples.plain_mcq_document(), tag="zzguard")
    staff_view = svc.get_published_version(session, item.view.question_id)
    text = staff_view.document.model_dump_json().lower()
    assert all(s in text for s in item.sentinels.hidden if s not in (STAFF, SOURCE_REF_SENTINEL))


def test_a_question_with_a_stimulus_is_never_shown(api: ApiHarness, env: Env) -> None:
    # Stimulus descriptions and alt texts cannot be planted in a published question; this is
    # what is reachable: the question cannot be published, so it is not served, and the
    # description does not appear in any learner response.
    source = samples.structured_document()
    source["stimuli"][0]["description"] = "zzstimulusdescriptionsentinel"
    view = bring_to(api.session, api.session.connection(), env, "approved", document(source))
    with pytest.raises(svc.NotPublishable):
        publish(api.session, view.id)

    assert_not_found(get_question(api, qid(view)))
    response = list_questions(api, limit=50)
    assert response.status_code == 200
    assert "zzstimulusdescriptionsentinel" not in response.text
    assert qid(view) not in response.text


# =============================================================================================
# The allow-listed fields
# =============================================================================================


def assert_projection(body: Json, item: Published) -> None:
    doc = item.document
    assert set(body) == {
        "id",
        "version_id",
        "question_class",
        "exam_section",
        "levels",
        "total_marks",
        "topic",
        "answered",
        "stem",
        "stimuli",
        "mcq",
        "parts",
    }
    out = LearnerQuestion.model_validate(body)  # also refuses any unknown field
    assert out.id == item.id
    assert out.version_id == vid(item.view)
    assert out.question_class == doc.question_class
    assert out.exam_section == doc.exam_section
    assert out.levels == doc.levels
    assert out.total_marks == doc.total_marks
    assert out.stem == doc.stem
    assert [(s.id, s.kind) for s in out.stimuli] == [(s.id, s.kind) for s in doc.stimuli]
    if doc.mcq is None:
        assert out.mcq is None
        assert body["mcq"] is None
    else:
        assert out.mcq is not None
        assert set(body["mcq"]) == {"option_layout", "column_headers", "statements", "options"}
        assert out.mcq.option_layout == doc.mcq.option_layout
        assert out.mcq.column_headers == doc.mcq.column_headers
        assert out.mcq.statements == doc.mcq.statements
        assert [(o.key, o.cells) for o in out.mcq.options] == [
            (o.key, o.cells) for o in doc.mcq.options
        ]
        for option in body["mcq"]["options"]:
            assert set(option) == {"key", "cells"}
    assert [
        (p.id, p.label, p.lead_in, p.body, p.marks, p.command_term, p.stimulus_refs)
        for p in out.parts
    ] == [
        (p.id, p.label, p.lead_in, p.body, p.marks, p.command_term, p.stimulus_refs)
        for p in doc.parts
    ]
    for part in body["parts"]:
        assert set(part) == {
            "id",
            "label",
            "lead_in",
            "body",
            "marks",
            "command_term",
            "stimulus_refs",
        }


@pytest.mark.parametrize("name", list(PUBLISHABLE))
def test_get_returns_the_allow_listed_fields_equal_to_the_document(
    api: ApiHarness, env: Env, name: str
) -> None:
    item = publish_document(api.session, env, PUBLISHABLE[name](), tag="zzproj")

    response = get_question(api, item.id)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert_projection(response.json(), item)


def test_ids_are_prefixed_and_well_formed(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzid")
    body = get_question(api, item.id).json()

    assert body["id"].startswith("q_") and len(body["id"]) == 2 + 26
    assert body["version_id"].startswith("qv_") and len(body["version_id"]) == 3 + 26
    assert ids.decode(ids.QUESTION, body["id"]) == item.view.question_id
    assert ids.decode(ids.QUESTION_VERSION, body["version_id"]) == item.view.id


def test_mcq_variants_expose_their_cells_headers_and_statements(api: ApiHarness, env: Env) -> None:
    two_column = publish_document(api.session, env, samples.two_column_mcq_document(), tag="zza")
    roman = publish_document(api.session, env, samples.roman_mcq_document(), tag="zzb")

    wide = get_question(api, two_column.id).json()["mcq"]
    statements = get_question(api, roman.id).json()["mcq"]

    assert wide["option_layout"] == "two_column_table"
    assert len(wide["column_headers"]) == 2
    assert all(len(o["cells"]) == 2 for o in wide["options"])
    assert [o["key"] for o in wide["options"]] == ["A", "B", "C", "D"]
    assert statements["option_layout"] == "roman_statements"
    assert len(statements["statements"]) == 3
    assert statements["column_headers"] == []


def test_structured_parts_carry_label_body_marks_command_term_and_lead_in(
    api: ApiHarness, env: Env
) -> None:
    item = publish_document(api.session, env, structured_without_figure(), tag="zzparts")

    body = get_question(api, item.id).json()

    assert body["mcq"] is None
    assert [p["label"] for p in body["parts"]] == ["a", "b"]
    assert [p["marks"] for p in body["parts"]] == [2, 3]
    assert [p["command_term"] for p in body["parts"]] == ["calculate", "determine"]
    assert body["parts"][0]["lead_in"] is None
    assert body["parts"][1]["lead_in"] is not None
    assert body["stimuli"] == []
    assert body["total_marks"] == 5


def test_a_question_without_a_command_term_shows_null(api: ApiHarness, env: Env) -> None:
    source = samples.data_based_document()
    source["parts"][0]["command_term"] = None
    item = publish_document(api.session, env, source, tag="zznull")

    body = get_question(api, item.id).json()

    assert body["parts"][0]["command_term"] is None
    assert body["parts"][1]["command_term"] == "calculate"


# =============================================================================================
# Only the published version, only while rights permit display
# =============================================================================================

NOT_PUBLISHED = [
    "draft",
    "auto_checking",
    "needs_fix",
    "in_review",
    "approved",
    "rejected",
    "withdrawn",
]


@pytest.mark.parametrize("status", NOT_PUBLISHED)
def test_a_version_that_is_not_published_is_a_404_and_not_listed(
    api: ApiHarness, env: Env, status: str
) -> None:
    visible = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzvis")
    hidden = bring_to(
        api.session,
        api.session.connection(),
        env,
        status,
        document(samples.mcq_document()),
    )

    assert_not_found(get_question(api, qid(hidden)))
    assert listed_ids(api) == [visible.id]


@pytest.mark.parametrize("role", ALL_ROLES)
def test_a_version_that_is_not_published_is_a_404_for_every_role(
    api: ApiHarness, env: Env, role: Role
) -> None:
    hidden = bring_to(
        api.session, api.session.connection(), env, "approved", document(samples.mcq_document())
    )
    assert_not_found(get_question(api, qid(hidden), role))


def test_a_404_for_a_hidden_question_is_the_same_as_for_one_that_never_existed(
    api: ApiHarness, env: Env
) -> None:
    hidden = bring_to(
        api.session, api.session.connection(), env, "draft", document(samples.mcq_document())
    )
    nothing = api.client.get("/v1/nothing-here", headers=api.headers(Role.STUDENT))

    for question_id in (
        qid(hidden),
        ids.encode(ids.QUESTION, uuid.uuid4()),
        "q_notanidentifier",
    ):
        response = get_question(api, question_id)
        assert response.status_code == 404
        assert response.content == nothing.content


def test_a_withdrawn_question_disappears_at_once(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzwd")
    assert get_question(api, item.id).status_code == 200
    assert listed_ids(api) == [item.id]

    svc.withdraw(api.session, actor=STAFF, version_id=item.view.id, reason="taken down")

    assert_not_found(get_question(api, item.id))
    assert listed_ids(api) == []


def test_a_republished_question_is_visible_again(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzrp")
    svc.withdraw(api.session, actor=STAFF, version_id=item.view.id, reason="taken down")
    assert_not_found(get_question(api, item.id))

    republish(api.session, item.view.id, actor=STAFF)

    assert get_question(api, item.id).status_code == 200
    assert listed_ids(api) == [item.id]


def test_after_a_revision_is_published_the_learner_sees_the_new_version(
    api: ApiHarness, env: Env
) -> None:
    item = publish_document(
        api.session, env, samples.plain_mcq_document(), tag="zzrev", plant=False
    )
    old = get_question(api, item.id).json()

    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)
    changed = samples.plain_mcq_document()
    changed["stem"] = samples.line(samples.text("A revised stem about a sealed rigid flask."))
    svc.update_draft(api.session, actor=STAFF, version_id=revision.id, document=document(changed))
    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    approve(api.session, revision.id, actor=STAFF)
    publish(api.session, revision.id, actor=STAFF)

    new = get_question(api, item.id).json()
    assert new["version_id"] == vid(revision)
    assert new["version_id"] != old["version_id"]
    assert new["stem"] != old["stem"]
    assert (
        new["stem"]["content"][0]["content"][0]["text"]
        == "A revised stem about a sealed rigid flask."
    )
    assert new["id"] == old["id"]
    listing = list_questions(api, limit=50).json()["items"]
    assert [(i["id"], i["version_id"]) for i in listing] == [(item.id, vid(revision))]


def test_a_pending_revision_does_not_change_what_the_learner_sees(
    api: ApiHarness, env: Env
) -> None:
    item = publish_document(
        api.session, env, samples.plain_mcq_document(), tag="zzpend", plant=False
    )
    before = get_question(api, item.id).json()
    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)

    def same() -> None:
        assert get_question(api, item.id).json() == before
        listing = list_questions(api, limit=50).json()["items"]
        assert [(i["id"], i["version_id"]) for i in listing] == [(item.id, vid(item.view))]

    same()  # draft
    changed = samples.plain_mcq_document()
    changed["stem"] = samples.line(samples.text("Draft wording that nobody has approved."))
    svc.update_draft(api.session, actor=STAFF, version_id=revision.id, document=document(changed))
    same()  # edited draft
    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    same()  # in review
    approve(api.session, revision.id, actor=STAFF)
    same()  # approved but not published
    assert "Draft wording" not in get_question(api, item.id).text


def test_rejecting_a_revision_leaves_the_published_version_in_place(
    api: ApiHarness, env: Env
) -> None:
    item = publish_document(
        api.session, env, samples.plain_mcq_document(), tag="zzrej", plant=False
    )
    before = get_question(api, item.id).json()
    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)
    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    svc.reject(api.session, actor=STAFF, version_id=revision.id, reason="not suitable")

    assert get_question(api, item.id).json() == before


def test_revoked_rights_make_a_published_question_a_404_and_unlisted(
    api: ApiHarness, env: Env
) -> None:
    kept = publish_document(api.session, env, samples.mcq_document(), tag="zzkept", plant=False)
    record = new_rights(api.session)
    doomed = publish_document(
        api.session,
        env,
        samples.plain_mcq_document(),
        tag="zzdoom",
        plant=False,
        rights_record_id=record,
    )
    assert get_question(api, doomed.id).status_code == 200
    assert sorted(listed_ids(api)) == sorted([kept.id, doomed.id])

    rights.revoke(api.session, record, at=now())

    assert_not_found(get_question(api, doomed.id))
    assert listed_ids(api) == [kept.id]
    assert get_question(api, kept.id).status_code == 200


def test_a_rights_record_that_has_expired_hides_the_question(api: ApiHarness, env: Env) -> None:
    kept = publish_document(api.session, env, samples.mcq_document(), tag="zzkeep", plant=False)
    deadline = now() + timedelta(seconds=3)
    record = new_rights(api.session, valid_until=deadline)
    short_lived = publish_document(
        api.session,
        env,
        samples.plain_mcq_document(),
        tag="zzexp",
        plant=False,
        rights_record_id=record,
    )
    assert get_question(api, short_lived.id).status_code == 200

    while now() < deadline + timedelta(milliseconds=200):
        time.sleep(0.1)

    assert_not_found(get_question(api, short_lived.id))
    assert listed_ids(api) == [kept.id]


def test_revoked_rights_hide_the_question_from_staff_roles_too(api: ApiHarness, env: Env) -> None:
    record = new_rights(api.session)
    item = publish_document(
        api.session,
        env,
        samples.plain_mcq_document(),
        tag="zzstaff",
        plant=False,
        rights_record_id=record,
    )
    rights.revoke(api.session, record, at=now())

    for role in ALL_ROLES:
        assert_not_found(get_question(api, item.id, role))
        assert listed_ids_for(api, role) == []


def listed_ids_for(api: ApiHarness, role: Role) -> list[str]:
    response = list_questions(api, role, limit=50)
    assert response.status_code == 200
    return [item["id"] for item in response.json()["items"]]


# =============================================================================================
# Who may read
# =============================================================================================


@pytest.mark.parametrize("role", ALL_ROLES)
def test_every_role_can_read_a_published_question(api: ApiHarness, env: Env, role: Role) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzrole")

    one = get_question(api, item.id, role)
    many = list_questions(api, role)

    assert one.status_code == 200
    assert many.status_code == 200
    assert [i["id"] for i in many.json()["items"]] == [item.id]


def test_staff_get_exactly_the_learner_view(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.mcq_document(), tag="zzsame")
    student = get_question(api, item.id, Role.STUDENT).json()
    for role in (Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN):
        assert get_question(api, item.id, role).json() == student


def test_a_user_with_two_roles_gets_the_same_learner_view(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.mcq_document(), tag="zztwo")
    both = get_question(api, item.id, Role.STUDENT, Role.PLATFORM_ADMIN).json()
    assert both == get_question(api, item.id, Role.STUDENT).json()


def test_no_token_is_401(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zznotok")

    for response in (api.client.get(f"/v1/questions/{item.id}"), api.client.get("/v1/questions")):
        assert response.status_code == 401
        assert response.headers["content-type"] == "application/problem+json"
        assert response.headers["www-authenticate"] == "Bearer"
        assert response.json()["code"] == "unauthenticated"


def test_a_bad_token_is_401(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzbadtok")
    headers = {"Authorization": "Bearer not.a.token"}
    assert api.client.get(f"/v1/questions/{item.id}", headers=headers).status_code == 401
    assert api.client.get("/v1/questions", headers=headers).status_code == 401


def test_an_account_without_a_role_gets_404_not_the_question(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zznorole")
    headers = api.headers()
    assert api.client.get(f"/v1/questions/{item.id}", headers=headers).status_code == 404
    assert api.client.get("/v1/questions", headers=headers).status_code == 404


def test_reading_writes_nothing(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzro")
    headers = api.headers(Role.STUDENT)
    api.session.flush()
    before = table_counts(api.session.connection())

    api.client.get(f"/v1/questions/{item.id}", headers=headers)
    api.client.get("/v1/questions", headers=headers)
    api.client.get("/v1/questions/q_bad", headers=headers)

    assert table_counts(api.session.connection()) == before


def test_other_methods_on_the_question_are_refused(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzmeth")
    headers = api.headers(Role.PLATFORM_ADMIN)
    for method in ("post", "put", "delete", "patch"):
        response = getattr(api.client, method)(f"/v1/questions/{item.id}", headers=headers)
        assert response.status_code in (404, 405)
    assert get_question(api, item.id).status_code == 200


# =============================================================================================
# Malformed and unknown identifiers
# =============================================================================================

VALID_SHAPE = ids.encode(ids.QUESTION, uuid.UUID(int=1 << 100))


@pytest.mark.parametrize(
    "bad",
    [
        "q_",
        "q_short",
        "not-an-id",
        "x",
        "0",
        str(uuid.uuid4()),
        "q_" + "u" * 26,  # 'u' is not in the alphabet
        "q_" + "i" * 26,
        "q_" + "L" * 26,
        VALID_SHAPE.upper(),
        VALID_SHAPE + "0",
        VALID_SHAPE[:-1],
        "qv_" + VALID_SHAPE[2:],  # a version identifier
        "acc_" + VALID_SHAPE[2:],
        "q_" + "z" * 26,  # does not fit in 128 bits
        "q%20x",
        "..",
    ],
)
def test_a_malformed_identifier_is_404(api: ApiHarness, env: Env, bad: str) -> None:
    publish_document(api.session, env, samples.plain_mcq_document(), tag="zzbad")
    assert_not_found(get_question(api, bad))


def test_a_version_identifier_does_not_open_a_question(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzverid")
    assert_not_found(get_question(api, vid(item.view)))


def test_a_well_formed_unknown_identifier_is_404(api: ApiHarness, env: Env) -> None:
    publish_document(api.session, env, samples.plain_mcq_document(), tag="zzunk")
    assert_not_found(get_question(api, ids.encode(ids.QUESTION, uuid.uuid4())))


# =============================================================================================
# The list
# =============================================================================================


@pytest.fixture
def six(api: ApiHarness, env: Env) -> dict[str, Published]:
    names = ["plain_mcq", "mcq", "two_column_mcq", "data_based", "show_that", "roman_mcq"]
    return {
        name: publish_document(
            api.session, env, PUBLISHABLE[name](), tag=f"zzl{index}x", plant=False
        )
        for index, name in enumerate(names)
    }


def expected_ids(
    six: dict[str, Published], predicate: Callable[[QuestionDocument], bool]
) -> list[str]:
    return sorted(p.id for p in six.values() if predicate(p.document))


def test_list_returns_every_published_question_ordered_by_id(
    api: ApiHarness, six: dict[str, Published]
) -> None:
    result = listed_ids(api)
    assert result == sorted(p.id for p in six.values())
    assert len(set(result)) == len(six)


def test_list_items_have_exactly_the_summary_fields_and_the_documents_values(
    api: ApiHarness, six: dict[str, Published]
) -> None:
    body = list_questions(api, limit=50).json()
    page = LearnerQuestionPage.model_validate(body)
    by_id = {p.id: p for p in six.values()}

    assert set(body) == {"items", "next_cursor"}
    for raw, item in zip(body["items"], page.items, strict=True):
        assert set(raw) == {
            "id",
            "version_id",
            "question_class",
            "exam_section",
            "levels",
            "total_marks",
            "topic",
            "answered",
        }
        source = by_id[item.id]
        assert item.version_id == vid(source.view)
        assert item.question_class == source.document.question_class
        assert item.exam_section == source.document.exam_section
        assert item.levels == source.document.levels
        assert item.total_marks == source.document.total_marks


def test_list_is_empty_when_nothing_is_published(api: ApiHarness, env: Env) -> None:
    bring_to(api.session, api.session.connection(), env, "draft", document())

    response = list_questions(api)

    assert response.status_code == 200
    assert response.json() == {"items": [], "next_cursor": None}


def test_list_leaves_out_everything_that_is_not_published(
    api: ApiHarness, env: Env, six: dict[str, Published]
) -> None:
    for status in NOT_PUBLISHED:
        bring_to(
            api.session, api.session.connection(), env, status, document(samples.mcq_document())
        )

    assert listed_ids(api) == sorted(p.id for p in six.values())


@pytest.mark.parametrize("section", ["paper_1a", "paper_1b", "paper_2"])
def test_filter_by_exam_section(api: ApiHarness, six: dict[str, Published], section: str) -> None:
    wanted = expected_ids(six, lambda d: d.exam_section == section)
    assert wanted
    assert listed_ids(api, exam_section=section) == wanted


@pytest.mark.parametrize("level", ["sl", "hl"])
def test_filter_by_level(api: ApiHarness, six: dict[str, Published], level: str) -> None:
    wanted = expected_ids(six, lambda d: level in [lv.value for lv in d.levels])
    assert wanted
    result = listed_ids(api, level=level)
    assert result == wanted


def test_the_sl_filter_excludes_hl_only_questions(
    api: ApiHarness, six: dict[str, Published]
) -> None:
    sl_only_excluded = {six["two_column_mcq"].id, six["show_that"].id}
    result = set(listed_ids(api, level="sl"))
    assert not (result & sl_only_excluded)
    assert six["plain_mcq"].id in result


@pytest.mark.parametrize(
    "question_class", ["mcq", "data_based", "short_structured", "long_structured"]
)
def test_filter_by_question_class(
    api: ApiHarness, six: dict[str, Published], question_class: str
) -> None:
    wanted = expected_ids(six, lambda d: d.question_class.value == question_class)
    assert listed_ids(api, question_class=question_class) == wanted


@pytest.mark.parametrize("node", ["A.1", "A.2", "A.3", "A.4", "B.2", "C.2", "D.1"])
def test_filter_by_syllabus_node_matches_primary_and_secondary(
    api: ApiHarness, six: dict[str, Published], node: str
) -> None:
    wanted = expected_ids(
        six, lambda d: node in (d.primary_syllabus_node, *d.secondary_syllabus_nodes)
    )
    assert listed_ids(api, syllabus_node=node) == wanted


def test_a_secondary_node_finds_the_question(api: ApiHarness, six: dict[str, Published]) -> None:
    show_that = six["show_that"]
    assert "A.2" in show_that.document.secondary_syllabus_nodes
    assert show_that.id in listed_ids(api, syllabus_node="A.2")
    assert show_that.id in listed_ids(api, syllabus_node=show_that.document.primary_syllabus_node)


def test_filters_combine_with_and(api: ApiHarness, six: dict[str, Published]) -> None:
    wanted = expected_ids(
        six,
        lambda d: (
            d.exam_section == "paper_1a"
            and d.question_class.value == "mcq"
            and "sl" in [lv.value for lv in d.levels]
            and d.primary_syllabus_node == "A.1"
        ),
    )
    assert wanted
    assert (
        listed_ids(
            api, exam_section="paper_1a", question_class="mcq", level="sl", syllabus_node="A.1"
        )
        == wanted
    )
    assert listed_ids(api, exam_section="paper_2", question_class="mcq") == []


def test_a_filter_that_matches_nothing_is_an_empty_page(
    api: ApiHarness, six: dict[str, Published]
) -> None:
    for params in ({"exam_section": "no_such_section"}, {"syllabus_node": "Z.9"}):
        response = list_questions(api, **params)
        assert response.status_code == 200
        assert response.json() == {"items": [], "next_cursor": None}


@pytest.mark.parametrize(
    "params",
    [{"level": "xl"}, {"question_class": "essay"}, {"level": "SL"}, {"question_class": ""}],
)
def test_an_unknown_enum_value_is_422(
    api: ApiHarness, six: dict[str, Published], params: dict[str, str]
) -> None:
    response = list_questions(api, **params)
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "validation_failed"


def test_filters_apply_to_the_published_version(api: ApiHarness, env: Env) -> None:
    item = publish_document(api.session, env, samples.plain_mcq_document(), tag="zzfv", plant=False)
    assert listed_ids(api, exam_section="paper_1a") == [item.id]
    revision = svc.start_revision(api.session, actor=STAFF, question_id=item.view.question_id)
    moved = samples.plain_mcq_document()
    moved["primary_syllabus_node"] = "A.1"
    svc.update_draft(api.session, actor=STAFF, version_id=revision.id, document=document(moved))

    # The draft revision changes nothing for the learner, filters included.
    assert listed_ids(api, syllabus_node="B.2") == [item.id]
    assert listed_ids(api, syllabus_node="A.1") == []

    svc.submit(api.session, actor=STAFF, version_id=revision.id)
    approve(api.session, revision.id, actor=STAFF)
    publish(api.session, revision.id, actor=STAFF)

    assert listed_ids(api, syllabus_node="B.2") == []
    assert listed_ids(api, syllabus_node="A.1") == [item.id]


# --- pagination ----------------------------------------------------------------------------------


@pytest.mark.parametrize("limit", [1, 2, 3, 4, 5, 6, 7, 100])
def test_cursor_pagination_walks_the_whole_set_without_duplicates_or_gaps(
    api: ApiHarness, six: dict[str, Published], limit: int
) -> None:
    everything = sorted(p.id for p in six.values())

    pages = walk(api.client, api.headers(Role.STUDENT), limit=limit)

    walked = [item["id"] for page in pages for item in page["items"]]
    assert walked == everything
    assert len(set(walked)) == len(walked)
    for page in pages[:-1]:
        assert len(page["items"]) == limit
        assert page["next_cursor"] == page["items"][-1]["id"]
    assert pages[-1]["next_cursor"] is None
    assert len(pages) == -(-len(everything) // limit)


def test_next_cursor_is_null_when_the_page_ends_exactly_at_the_last_question(
    api: ApiHarness, six: dict[str, Published]
) -> None:
    exact = list_questions(api, limit=len(six)).json()
    short = list_questions(api, limit=len(six) - 1).json()

    assert len(exact["items"]) == len(six)
    assert exact["next_cursor"] is None
    assert short["next_cursor"] == short["items"][-1]["id"]


def test_a_cursor_returns_only_questions_after_it(
    api: ApiHarness, six: dict[str, Published]
) -> None:
    ordered = sorted(p.id for p in six.values())
    response = list_questions(api, cursor=ordered[2], limit=50)
    assert [i["id"] for i in response.json()["items"]] == ordered[3:]
    last = list_questions(api, cursor=ordered[-1], limit=50)
    assert last.json() == {"items": [], "next_cursor": None}


def test_pagination_with_a_filter(api: ApiHarness, six: dict[str, Published]) -> None:
    wanted = expected_ids(six, lambda d: d.exam_section == "paper_1a")
    assert len(wanted) >= 3

    pages = walk(api.client, api.headers(Role.STUDENT), exam_section="paper_1a", limit=2)

    assert [i["id"] for p in pages for i in p["items"]] == wanted
    assert pages[-1]["next_cursor"] is None


def test_pages_are_full_even_when_questions_are_hidden_by_rights(api: ApiHarness, env: Env) -> None:
    records = [new_rights(api.session) for _ in range(5)]
    items = [
        publish_document(
            api.session,
            env,
            samples.plain_mcq_document(),
            tag=f"zzrt{index}x",
            plant=False,
            rights_record_id=record,
        )
        for index, record in enumerate(records)
    ]
    by_order = sorted(zip(items, records, strict=True), key=lambda pair: pair[0].id)
    for _, record in (by_order[1], by_order[3]):
        rights.revoke(api.session, record, at=now())
    visible = [by_order[i][0].id for i in (0, 2, 4)]

    pages = walk(api.client, api.headers(Role.STUDENT), limit=2)

    assert [len(p["items"]) for p in pages] == [2, 1]
    assert [i["id"] for p in pages for i in p["items"]] == visible
    assert pages[-1]["next_cursor"] is None


def test_a_page_never_repeats_after_a_publication_between_requests(
    api: ApiHarness, env: Env, six: dict[str, Published]
) -> None:
    headers = api.headers(Role.STUDENT)
    first = api.client.get("/v1/questions", params={"limit": 3}, headers=headers).json()
    extra = publish_document(
        api.session, env, samples.plain_mcq_document(), tag="zzlate", plant=False
    )
    second = api.client.get(
        "/v1/questions", params={"limit": 50, "cursor": first["next_cursor"]}, headers=headers
    ).json()

    seen = [i["id"] for i in first["items"]] + [i["id"] for i in second["items"]]
    assert len(set(seen)) == len(seen)
    assert set(seen) >= {p.id for p in six.values()}
    assert extra.id in seen or extra.id < first["items"][-1]["id"]


@pytest.mark.parametrize("limit", [0, 101, -1, 1000])
def test_limit_out_of_bounds_is_422(api: ApiHarness, limit: int) -> None:
    response = list_questions(api, limit=limit)
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "validation_failed"


@pytest.mark.parametrize("limit", ["abc", "", "1.5", "1e1"])
def test_limit_that_is_not_an_integer_is_422(api: ApiHarness, limit: str) -> None:
    response = list_questions(api, limit=limit)
    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"


@pytest.mark.parametrize("limit", [1, 100])
def test_limit_at_its_bounds_is_accepted(
    api: ApiHarness, six: dict[str, Published], limit: int
) -> None:
    response = list_questions(api, limit=limit)
    assert response.status_code == 200
    assert len(response.json()["items"]) == min(limit, len(six))


def test_the_default_page_holds_everything_when_there_are_few_questions(
    api: ApiHarness, six: dict[str, Published]
) -> None:
    body = list_questions(api).json()
    assert len(body["items"]) == len(six)
    assert body["next_cursor"] is None


@pytest.mark.parametrize(
    "cursor",
    [
        "garbage",
        "q_",
        "q_short",
        "q_" + "u" * 26,
        "qv_" + "0" * 26,
        "acc_" + "0" * 26,
        str(uuid.uuid4()),
        VALID_SHAPE.upper(),
        "q_" + "z" * 26,
        " ",
        "q_01j9z3k4m5n6p7q8r9s0t1v2w3 ",
    ],
)
def test_a_cursor_that_cannot_be_decoded_is_422_invalid_cursor(
    api: ApiHarness, six: dict[str, Published], cursor: str
) -> None:
    response = list_questions(api, cursor=cursor)
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "invalid_cursor"


def test_an_overlong_cursor_is_422(api: ApiHarness, six: dict[str, Published]) -> None:
    assert list_questions(api, cursor="q_" + "0" * 400).status_code == 422


def test_the_smallest_possible_cursor_lists_everything(
    api: ApiHarness, six: dict[str, Published]
) -> None:
    smallest = ids.encode(ids.QUESTION, uuid.UUID(int=0))
    assert listed_ids(api, cursor=smallest) == sorted(p.id for p in six.values())


def test_a_list_request_with_an_unknown_parameter_is_still_served(
    api: ApiHarness, six: dict[str, Published]
) -> None:
    # Unknown query parameters are ignored by FastAPI unless the endpoint forbids them; the
    # specification does not say either way (reported as a gap), so only no-leak is asserted.
    response = list_questions(api, status="draft", limit=50)
    assert response.status_code in (200, 422)
    if response.status_code == 200:
        assert [i["id"] for i in response.json()["items"]] == sorted(p.id for p in six.values())


def test_a_staff_status_filter_cannot_be_used_to_see_drafts(
    api: ApiHarness, env: Env, six: dict[str, Published]
) -> None:
    draft = bring_to(
        api.session, api.session.connection(), env, "draft", document(samples.mcq_document())
    )

    response = list_questions(api, Role.PLATFORM_ADMIN, status="draft", limit=50)

    assert qid(draft) not in response.text


# --- part ids are plain strings -----------------------------------------------------------------


def test_a_part_id_of_seventy_characters_is_read_by_a_learner(api: ApiHarness, env: Env) -> None:
    long_id = "p" + "-x" * 34 + "a"
    assert len(long_id) == 70
    source = json.loads(json.dumps(structured_without_figure()).replace('"p-a"', f'"{long_id}"'))
    item = publish_document(api.session, env, source, tag="zzlongv")

    read = api.client.get(f"/v1/questions/{item.id}", headers=api.headers(Role.STUDENT))

    assert read.status_code == 200, read.text
    body = LearnerQuestion.model_validate(read.json())
    assert [p.id for p in body.parts] == [p.id for p in item.document.parts]
    assert long_id in [p.id for p in body.parts]
    listing = api.client.get("/v1/questions", headers=api.headers(Role.STUDENT))
    assert listing.status_code == 200
    assert item.id in [i["id"] for i in listing.json()["items"]]


def test_the_learner_part_type_takes_an_id_of_any_text() -> None:
    fields = api_schemas.LearnerPart.model_fields
    assert fields["id"].annotation is str
    assert api_schemas.WrittenResult.model_fields["part_id"].annotation is str
