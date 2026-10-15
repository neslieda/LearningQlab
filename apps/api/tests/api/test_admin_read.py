"""Staff reads through HTTP: the question list, a question, a version, a version's history.

Specification: docs/slices/M1G-5-SOZLESME.md sections 3.2 and 3.5, docs/slices/M1G-5-YETKILER.md
section 1 (rows 7 to 10), the `api.schemas` contract and the docstrings of `content.service`.
Written without reading the handlers.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

import pytest
from httpx2 import Response
from sqlalchemy import Connection
from sqlalchemy.orm import Session

from qlab.api import ids
from qlab.content import service as svc
from qlab.content.schema import QuestionDocument
from qlab.organizations.service import Role
from qlab.rights import service as rights
from tests.api.support import ApiHarness
from tests.content import samples
from tests.content.support import (
    AUTHOR,
    PUBLISHER,
    Env,
    bring_to,
    create,
    document,
    failed_critical,
    make_env,
    new_rights,
    now,
    stored_hash,
)

pytestmark = [pytest.mark.db, pytest.mark.node]

LIST_URL = "/v1/admin/questions"
VERSION_KEYS = {
    "id",
    "question_id",
    "version_no",
    "status",
    "content_sha256",
    "question_class",
    "exam_section",
    "levels",
    "total_marks",
    "has_unverified_visuals",
    "created_by",
    "created_at",
    "updated_at",
}
HISTORY_KEYS = {
    "occurred_at",
    "actor",
    "action",
    "status",
    "previous_status",
    "content_sha256",
    "previous_content_sha256",
    "reason",
    "failed_checks",
    "check",
    "severity",
    "outcome",
    "based_on",
    "superseded_by",
    "source_ref",
    "approver_is_last_editor",
}


def qid(value: uuid.UUID) -> str:
    return ids.encode(ids.QUESTION, value)


def vid(value: uuid.UUID) -> str:
    return ids.encode(ids.QUESTION_VERSION, value)


def vurl(version_id: uuid.UUID, suffix: str = "") -> str:
    return f"/v1/admin/question-versions/{vid(version_id)}{suffix}"


def keys_in(value: Any) -> set[str]:
    """Every object key anywhere in a JSON value."""
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.add(key)
            found |= keys_in(child)
    elif isinstance(value, list):
        for child in value:
            found |= keys_in(child)
    return found


# --- a small bank of questions ---------------------------------------------------------------


@dataclass
class Bank:
    """Six questions in different statuses. `by_name` maps a name to its question id."""

    draft_mcq: svc.QuestionVersionView  # paper_1a, B.2, mcq, sl+hl, draft
    review_data: svc.QuestionVersionView  # paper_1b, A.1, data_based, sl+hl, in_review
    published_hl: svc.QuestionVersionView  # paper_1a, A.4, mcq, hl only, published; v2 is a draft
    approved_long: (
        svc.QuestionVersionView
    )  # paper_2, A.4 (+A.2, A.3), long_structured, hl, approved
    visual: svc.QuestionVersionView  # paper_2, A.1, short_structured, stimuli, draft
    fix_mcq: svc.QuestionVersionView  # paper_1a, A.1, mcq, sl+hl, needs_fix
    revision: svc.QuestionVersionView  # the second version of `published_hl`

    @property
    def all_questions(self) -> list[uuid.UUID]:
        return sorted(
            v.question_id
            for v in (
                self.draft_mcq,
                self.review_data,
                self.published_hl,
                self.approved_long,
                self.visual,
                self.fix_mcq,
            )
        )


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


@pytest.fixture
def bank(session: Session, connection: Connection, env: Env, api: ApiHarness) -> Bank:
    draft_mcq = bring_to(session, connection, env, "draft", document(samples.plain_mcq_document()))
    review_data = bring_to(
        session, connection, env, "in_review", document(samples.data_based_document())
    )
    published_hl = bring_to(
        session, connection, env, "published", document(samples.two_column_mcq_document())
    )
    approved_long = bring_to(
        session, connection, env, "approved", document(samples.show_that_document())
    )
    visual = bring_to(session, connection, env, "draft", document(samples.structured_document()))
    fix_mcq = bring_to(session, connection, env, "needs_fix", document(samples.mcq_document()))
    # A revision of the published question whose content is of another class and section.
    started = svc.start_revision(session, actor=AUTHOR, question_id=published_hl.question_id)
    revision = svc.update_draft(
        session,
        actor=AUTHOR,
        version_id=started.id,
        document=document(samples.data_based_document()),
    )
    return Bank(draft_mcq, review_data, published_hl, approved_long, visual, fix_mcq, revision)


def listed(response: Response) -> list[str]:
    assert response.status_code == 200, response.text
    return [item["id"] for item in response.json()["items"]]


def names(bank: Bank, response: Response) -> set[str]:
    by_id = {
        qid(bank.draft_mcq.question_id): "draft_mcq",
        qid(bank.review_data.question_id): "review_data",
        qid(bank.published_hl.question_id): "published_hl",
        qid(bank.approved_long.question_id): "approved_long",
        qid(bank.visual.question_id): "visual",
        qid(bank.fix_mcq.question_id): "fix_mcq",
    }
    return {by_id[i] for i in listed(response)}


def get_list(api: ApiHarness, query: str = "", role: Role = Role.REVIEWER) -> Response:
    return api.client.get(f"{LIST_URL}?{query}" if query else LIST_URL, headers=api.headers(role))


# --- GET /v1/admin/questions -----------------------------------------------------------------


def test_the_list_has_every_question_in_id_order_whatever_its_status(
    api: ApiHarness, bank: Bank
) -> None:
    response = get_list(api)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "next_cursor"}
    assert body["next_cursor"] is None
    assert listed(response) == [qid(q) for q in bank.all_questions]
    assert {i["latest_version"]["status"] for i in body["items"]} == {
        "draft",
        "in_review",
        "approved",
        "needs_fix",
    }


def test_a_list_item_names_the_question_its_latest_version_and_its_pointers(
    api: ApiHarness, bank: Bank
) -> None:
    items = {i["id"]: i for i in get_list(api).json()["items"]}
    item = items[qid(bank.published_hl.question_id)]
    assert set(item) == {
        "id",
        "origin",
        "source_ref",
        "created_at",
        "latest_version",
        "published_version_id",
        "working_version_id",
    }
    assert item["origin"] == "authored"
    assert item["source_ref"] is None
    latest = item["latest_version"]
    assert set(latest) == VERSION_KEYS
    assert latest["id"] == vid(bank.revision.id)
    assert latest["version_no"] == 2
    assert latest["status"] == "draft"
    assert latest["question_class"] == "data_based"
    assert latest["exam_section"] == "paper_1b"
    assert latest["total_marks"] == 4
    assert latest["content_sha256"] == bank.revision.content_sha256
    assert latest["has_unverified_visuals"] is False
    assert latest["created_by"] == AUTHOR
    assert item["published_version_id"] == vid(bank.published_hl.id)
    assert item["working_version_id"] == vid(bank.revision.id)

    plain = items[qid(bank.draft_mcq.question_id)]
    assert plain["published_version_id"] is None
    assert plain["working_version_id"] == vid(bank.draft_mcq.id)
    assert items[qid(bank.visual.question_id)]["latest_version"]["has_unverified_visuals"] is True


def test_a_list_carries_no_document_anywhere(api: ApiHarness, bank: Bank) -> None:
    keys = keys_in(get_list(api).json())
    assert keys.isdisjoint({"document", "stem", "parts", "mcq", "mark_points", "correct_key"})


@pytest.mark.parametrize("role", [Role.REVIEWER, Role.CONTENT_ADMIN, Role.PLATFORM_ADMIN])
def test_every_staff_role_sees_the_same_list(api: ApiHarness, bank: Bank, role: Role) -> None:
    assert listed(get_list(api, role=role)) == [qid(q) for q in bank.all_questions]


def test_an_empty_bank_gives_an_empty_page(api: ApiHarness) -> None:
    body = get_list(api).json()
    assert body == {"items": [], "next_cursor": None}


# filters -- they apply to each question's latest version


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("status=draft", {"draft_mcq", "visual", "published_hl"}),  # published_hl: v2 is a draft
        ("status=in_review", {"review_data"}),
        ("status=approved", {"approved_long"}),
        ("status=needs_fix", {"fix_mcq"}),
        ("status=published", set()),  # the published version is not the latest
        ("status=rejected", set()),
        ("status=withdrawn", set()),
        ("exam_section=paper_1a", {"draft_mcq", "fix_mcq"}),  # published_hl's latest is paper_1b
        ("exam_section=paper_1b", {"review_data", "published_hl"}),
        ("exam_section=paper_2", {"approved_long", "visual"}),
        ("exam_section=paper_3", set()),
        ("level=sl", {"draft_mcq", "review_data", "visual", "fix_mcq", "published_hl"}),
        (
            "level=hl",
            {"draft_mcq", "review_data", "approved_long", "visual", "fix_mcq", "published_hl"},
        ),
        ("question_class=mcq", {"draft_mcq", "fix_mcq"}),
        ("question_class=data_based", {"review_data", "published_hl"}),
        ("question_class=long_structured", {"approved_long"}),
        ("question_class=short_structured", {"visual"}),
        ("syllabus_node=A.1", {"review_data", "visual", "fix_mcq", "published_hl"}),
        ("syllabus_node=B.2", {"draft_mcq"}),
        ("syllabus_node=A.4", {"approved_long"}),  # the published v1 was A.4, the latest is A.1
        ("syllabus_node=A.2", {"approved_long"}),  # a secondary node matches too
        ("syllabus_node=A.3", {"approved_long"}),
        ("syllabus_node=C.2", set()),
        ("has_unverified_visuals=true", {"visual"}),
        (
            "has_unverified_visuals=false",
            {"draft_mcq", "review_data", "published_hl", "approved_long", "fix_mcq"},
        ),
        ("status=draft&question_class=mcq", {"draft_mcq"}),
        ("status=draft&exam_section=paper_2&has_unverified_visuals=true", {"visual"}),
        ("status=approved&level=sl", set()),
        ("exam_section=paper_1a&syllabus_node=A.1&level=sl", {"fix_mcq"}),
    ],
)
def test_filters_apply_to_the_latest_version(
    api: ApiHarness, bank: Bank, query: str, expected: set[str]
) -> None:
    assert names(bank, get_list(api, query)) == expected


def test_a_filter_does_not_hide_the_published_and_working_pointers(
    api: ApiHarness, bank: Bank
) -> None:
    items = get_list(api, "status=draft&question_class=data_based").json()["items"]
    assert [i["id"] for i in items] == [qid(bank.published_hl.question_id)]
    assert items[0]["published_version_id"] == vid(bank.published_hl.id)
    assert items[0]["working_version_id"] == vid(bank.revision.id)


@pytest.mark.parametrize(
    "query",
    [
        "status=bogus",
        "level=xl",
        "question_class=essay",
        "has_unverified_visuals=maybe",
        "status=",
        "syllabus_node=" + "x" * 121,
        "exam_section=" + "x" * 121,
    ],
)
def test_an_invalid_filter_value_is_validation_failed(
    api: ApiHarness, bank: Bank, query: str
) -> None:
    response = get_list(api, query)
    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"


def test_an_unknown_query_parameter_does_not_widen_the_result(api: ApiHarness, bank: Bank) -> None:
    # Whether it is ignored or refused, it must never reveal more than the plain list.
    response = get_list(api, "unknown=1")
    assert response.status_code in (200, 422)
    if response.status_code == 200:
        assert listed(response) == [qid(q) for q in bank.all_questions]


# pagination


def pages(api: ApiHarness, limit: int, query: str = "") -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    cursor: str | None = None
    for _ in range(50):
        parameters = f"limit={limit}" + (f"&{query}" if query else "")
        if cursor is not None:
            parameters += f"&cursor={cursor}"
        response = get_list(api, parameters)
        assert response.status_code == 200, response.text
        body = response.json()
        result.append(body)
        cursor = body["next_cursor"]
        if cursor is None:
            return result
    raise AssertionError("pagination did not end")


@pytest.mark.parametrize("limit", [1, 2, 4, 5])
def test_following_the_cursor_visits_every_question_once_in_order(
    api: ApiHarness, bank: Bank, limit: int
) -> None:
    result = pages(api, limit)
    seen = [item["id"] for page in result for item in page["items"]]
    assert seen == [qid(q) for q in bank.all_questions]
    assert all(len(page["items"]) == limit for page in result[:-1])
    assert 1 <= len(result[-1]["items"]) <= limit
    assert result[-1]["next_cursor"] is None


def test_next_cursor_is_the_id_of_the_last_question_on_the_page(
    api: ApiHarness, bank: Bank
) -> None:
    first = get_list(api, "limit=2").json()
    assert first["next_cursor"] == first["items"][-1]["id"]
    assert first["next_cursor"].startswith("q_")


def test_next_cursor_is_null_when_the_page_is_exactly_the_rest(api: ApiHarness, bank: Bank) -> None:
    exact = get_list(api, "limit=6").json()
    assert len(exact["items"]) == 6
    assert exact["next_cursor"] is None
    short = get_list(api, "limit=5").json()
    assert len(short["items"]) == 5
    assert short["next_cursor"] == short["items"][-1]["id"]
    rest = get_list(api, f"limit=5&cursor={short['next_cursor']}").json()
    assert len(rest["items"]) == 1
    assert rest["next_cursor"] is None


def test_the_cursor_works_together_with_filters(api: ApiHarness, bank: Bank) -> None:
    result = pages(api, 1, "exam_section=paper_2")
    assert [len(p["items"]) for p in result] == [1, 1]
    seen = {item["id"] for page in result for item in page["items"]}
    assert seen == {qid(bank.approved_long.question_id), qid(bank.visual.question_id)}


def test_a_cursor_before_every_id_gives_the_whole_list(api: ApiHarness, bank: Bank) -> None:
    first = ids.encode(ids.QUESTION, uuid.UUID(int=0))
    assert listed(get_list(api, f"cursor={first}")) == [qid(q) for q in bank.all_questions]


def test_a_cursor_after_every_id_gives_an_empty_page(api: ApiHarness, bank: Bank) -> None:
    last = ids.encode(ids.QUESTION, uuid.UUID(int=(1 << 128) - 1))
    body = get_list(api, f"cursor={last}").json()
    assert body == {"items": [], "next_cursor": None}


@pytest.mark.parametrize(
    "cursor",
    [
        "garbage",
        "q_",
        "q_" + "0" * 25,
        "q_" + "0" * 27,
        "q_" + "u" * 26,
        "qv_" + "0" * 26,
        "Q_" + "0" * 26,
        "0" * 26,
        "%20",
    ],
)
def test_an_undecodable_cursor_is_invalid_cursor(api: ApiHarness, bank: Bank, cursor: str) -> None:
    response = get_list(api, f"cursor={cursor}")
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_cursor"


@pytest.mark.parametrize("limit", ["0", "-1", "101", "1000", "abc", "1.5", ""])
def test_a_limit_outside_1_to_100_is_validation_failed(
    api: ApiHarness, bank: Bank, limit: str
) -> None:
    response = get_list(api, f"limit={limit}")
    assert response.status_code == 422
    assert response.json()["code"] == "validation_failed"


@pytest.mark.parametrize("limit", ["1", "50", "100"])
def test_the_limits_at_the_boundary_are_accepted(api: ApiHarness, bank: Bank, limit: str) -> None:
    response = get_list(api, f"limit={limit}")
    assert response.status_code == 200
    assert len(response.json()["items"]) == min(int(limit), 6)


def test_the_default_page_is_large_enough_for_a_small_bank(api: ApiHarness, bank: Bank) -> None:
    assert len(get_list(api).json()["items"]) == 6


def test_a_revoked_question_is_not_listed_and_pages_are_not_short(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    revoked_id = new_rights(session)
    views = []
    for index in range(7):
        views.append(
            bring_to(
                session,
                connection,
                env,
                "draft",
                rights_record_id=revoked_id if index % 2 == 0 else None,
            )
        )
    rights.revoke(session, revoked_id, at=now())
    session.flush()
    visible = sorted(v.question_id for index, v in enumerate(views) if index % 2 == 1)
    assert len(visible) == 3
    result = pages(api, 2)
    assert [len(p["items"]) for p in result] == [2, 1]
    assert [i["id"] for p in result for i in p["items"]] == [qid(q) for q in visible]


# --- GET /v1/admin/questions/{id} ------------------------------------------------------------


def test_a_question_shows_its_versions_oldest_first_and_no_content(
    api: ApiHarness, bank: Bank
) -> None:
    response = api.client.get(
        f"/v1/admin/questions/{qid(bank.published_hl.question_id)}",
        headers=api.headers(Role.REVIEWER),
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"id", "origin", "source_ref", "created_by", "created_at", "versions"}
    assert body["id"] == qid(bank.published_hl.question_id)
    assert body["created_by"] == AUTHOR
    assert [v["version_no"] for v in body["versions"]] == [1, 2]
    assert [v["id"] for v in body["versions"]] == [vid(bank.published_hl.id), vid(bank.revision.id)]
    assert [v["status"] for v in body["versions"]] == ["published", "draft"]
    assert all(set(v) == VERSION_KEYS for v in body["versions"])
    assert body["versions"][0]["question_class"] == "mcq"
    assert body["versions"][1]["question_class"] == "data_based"
    assert keys_in(body).isdisjoint({"document", "stem", "parts", "mcq", "checks"})


def test_a_question_with_one_version_has_a_list_of_one(api: ApiHarness, bank: Bank) -> None:
    body = api.client.get(
        f"/v1/admin/questions/{qid(bank.draft_mcq.question_id)}",
        headers=api.headers(Role.CONTENT_ADMIN),
    ).json()
    assert len(body["versions"]) == 1


def test_an_imported_question_shows_its_source_ref(
    api: ApiHarness, session: Session, env: Env
) -> None:
    view = svc.create_question(
        session,
        actor=AUTHOR,
        document=document(),
        rights_record_id=env.rights_record_id,
        syllabus_version_id=env.syllabus_version_id,
        source_ref="synthetic/import-1",
    )
    body = api.client.get(
        f"/v1/admin/questions/{qid(view.question_id)}", headers=api.headers(Role.REVIEWER)
    ).json()
    assert body["source_ref"] == "synthetic/import-1"
    listed_item = get_list(api).json()["items"][0]
    assert listed_item["source_ref"] == "synthetic/import-1"


def test_an_unknown_question_is_404(api: ApiHarness, bank: Bank) -> None:
    response = api.client.get(
        f"/v1/admin/questions/{qid(uuid.uuid4())}", headers=api.headers(Role.REVIEWER)
    )
    assert response.status_code == 404


# --- GET /v1/admin/question-versions/{id} ----------------------------------------------------


def test_a_version_has_the_whole_document_exactly_as_stored(api: ApiHarness, bank: Bank) -> None:
    response = api.client.get(vurl(bank.review_data.id), headers=api.headers(Role.REVIEWER))
    assert response.status_code == 200
    body = response.json()
    assert set(body) == VERSION_KEYS | {"document", "checks"}
    assert QuestionDocument.model_validate(body["document"]) == bank.review_data.document
    assert body["id"] == vid(bank.review_data.id)
    assert body["question_id"] == qid(bank.review_data.question_id)
    assert body["version_no"] == 1
    assert body["status"] == "in_review"
    assert body["content_sha256"] == svc.content_sha256(bank.review_data.document)
    assert body["total_marks"] == bank.review_data.document.total_marks
    assert body["levels"] == ["sl", "hl"]


@pytest.mark.parametrize("status", ["draft", "needs_fix", "in_review", "approved", "published"])
def test_a_version_in_any_status_can_be_read_by_staff(
    api: ApiHarness, session: Session, connection: Connection, env: Env, status: str
) -> None:
    view = bring_to(session, connection, env, status)
    response = api.client.get(vurl(view.id), headers=api.headers(Role.PLATFORM_ADMIN))
    assert response.status_code == 200
    assert response.json()["status"] == status


def test_the_checks_of_a_submitted_version_are_listed_with_their_outcomes(
    api: ApiHarness, bank: Bank
) -> None:
    checks = api.client.get(vurl(bank.review_data.id), headers=api.headers(Role.REVIEWER)).json()[
        "checks"
    ]
    by_code = {c["code"]: c for c in checks}
    assert {"schema_valid", "vocabulary_valid", "math_renders"} <= set(by_code)
    for code in ("schema_valid", "vocabulary_valid", "math_renders"):
        assert set(by_code[code]) == {"code", "severity", "outcome", "detail"}
        assert by_code[code]["severity"] == "critical"
        assert by_code[code]["outcome"] == "passed"
    assert [c["code"] for c in checks] == sorted(c["code"] for c in checks)


def test_a_recorded_failed_check_is_listed_with_its_detail(
    api: ApiHarness, session: Session, env: Env
) -> None:
    view = create(session, env)
    svc.record_check(session, actor=AUTHOR, version_id=view.id, result=failed_critical("ext_check"))
    svc.submit(session, actor=AUTHOR, version_id=view.id)
    body = api.client.get(vurl(view.id), headers=api.headers(Role.REVIEWER)).json()
    assert body["status"] == "needs_fix"
    failed = [c for c in body["checks"] if c["outcome"] == "failed"]
    assert [c["code"] for c in failed] == ["ext_check"]
    assert failed[0]["severity"] == "critical"
    assert failed[0]["detail"] == {"note": "synthetic"}


def test_a_version_with_stimuli_says_so(api: ApiHarness, bank: Bank) -> None:
    body = api.client.get(vurl(bank.visual.id), headers=api.headers(Role.REVIEWER)).json()
    assert body["has_unverified_visuals"] is True
    assert body["document"]["stimuli"]


def test_the_ids_of_the_version_response_are_prefixed(api: ApiHarness, bank: Bank) -> None:
    body = api.client.get(vurl(bank.draft_mcq.id), headers=api.headers(Role.REVIEWER)).json()
    assert body["id"].startswith("qv_")
    assert body["question_id"].startswith("q_")
    assert ids.decode(ids.QUESTION_VERSION, body["id"]) == bank.draft_mcq.id


def test_an_unknown_version_is_404(api: ApiHarness) -> None:
    response = api.client.get(vurl(uuid.uuid4()), headers=api.headers(Role.REVIEWER))
    assert response.status_code == 404


# --- GET .../history -------------------------------------------------------------------------


def history(
    api: ApiHarness, version_id: uuid.UUID, role: Role = Role.REVIEWER
) -> list[dict[str, Any]]:
    response = api.client.get(vurl(version_id, "/history"), headers=api.headers(role))
    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == {"items"}
    items: list[dict[str, Any]] = body["items"]
    return items


def test_the_history_lists_what_happened_in_order_without_the_action_prefix(
    api: ApiHarness, session: Session, env: Env
) -> None:
    reviewer, admin = api.headers(Role.REVIEWER), api.headers(Role.CONTENT_ADMIN)
    view = create(session, env, actor=api.actor(Role.CONTENT_ADMIN))
    edit = api.client.put(
        vurl(view.id),
        headers=reviewer,
        json={
            "document": samples.mcq_document(),
            "expected_content_sha256": stored_hash(session, view.id),
        },
    )
    assert edit.status_code == 200
    api.client.post(vurl(view.id, "/submit"), headers=reviewer)
    api.client.post(
        vurl(view.id, "/request-changes"), headers=reviewer, json={"reason": "fix the stem"}
    )
    api.client.put(
        vurl(view.id),
        headers=reviewer,
        json={
            "document": samples.mcq_document(),
            "expected_content_sha256": stored_hash(session, view.id),
        },
    )
    api.client.post(vurl(view.id, "/submit"), headers=reviewer)
    api.client.post(
        vurl(view.id, "/approve"),
        headers=admin,
        json={"expected_content_sha256": stored_hash(session, view.id)},
    )
    api.client.post(
        vurl(view.id, "/publish"),
        headers=admin,
        json={"expected_content_sha256": stored_hash(session, view.id)},
    )
    items = history(api, view.id)
    assert [i["action"] for i in items] == [
        "created",
        "updated",
        "submitted",
        "checks_passed",
        "changes_requested",
        "updated",
        "submitted",
        "checks_passed",
        "approved",
        "published",
    ]
    assert all(set(i) == HISTORY_KEYS for i in items)
    assert [i["occurred_at"] for i in items] == sorted(i["occurred_at"] for i in items)
    assert items[0]["actor"] == api.actor(Role.CONTENT_ADMIN)
    assert items[1]["actor"] == api.actor(Role.REVIEWER)
    assert items[-1]["actor"] == api.actor(Role.CONTENT_ADMIN)
    assert all(i["actor"].startswith("acc_") for i in items)
    assert all("." not in i["action"] for i in items)

    created, updated, approved, published = items[0], items[1], items[8], items[9]
    assert created["status"] == "draft"
    assert created["previous_status"] is None
    assert created["previous_content_sha256"] is None
    assert updated["status"] == "draft"
    assert updated["previous_content_sha256"] == created["content_sha256"]
    assert updated["content_sha256"] == svc.content_sha256(document(samples.mcq_document()))
    assert approved["status"] == "approved"
    assert approved["previous_status"] == "in_review"
    assert published["status"] == "published"
    assert published["previous_status"] == "approved"
    assert items[4]["reason"] == "fix the stem"
    assert items[4]["status"] == "needs_fix"
    assert items[4]["previous_status"] == "in_review"


def test_an_entry_has_nulls_for_the_fields_its_action_does_not_carry(
    api: ApiHarness, session: Session, env: Env
) -> None:
    view = create(session, env)
    entry = history(api, view.id)[0]
    assert entry["action"] == "created"
    for field in (
        "reason",
        "failed_checks",
        "check",
        "severity",
        "outcome",
        "based_on",
        "superseded_by",
        "source_ref",
        "approver_is_last_editor",
    ):
        assert entry[field] is None, field


def test_failed_checks_lists_the_blocking_codes(
    api: ApiHarness, session: Session, env: Env
) -> None:
    view = create(session, env)
    svc.record_check(session, actor=AUTHOR, version_id=view.id, result=failed_critical("ext_check"))
    api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.REVIEWER))
    items = history(api, view.id)
    by_action = {i["action"]: i for i in items}
    assert items[-1]["action"] == "checks_failed"
    assert by_action["checks_failed"]["failed_checks"] == ["ext_check"]
    assert by_action["checks_failed"]["status"] == "needs_fix"
    assert by_action["submitted"]["failed_checks"] is None
    recorded = by_action["check_recorded"]
    assert recorded["check"] == "ext_check"
    assert recorded["severity"] == "critical"
    assert recorded["outcome"] == "failed"
    assert recorded["actor"] == AUTHOR  # an actor that is not an account is returned as written


def test_a_revision_and_its_predecessor_point_at_each_other(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    v1 = bring_to(session, connection, env, "published")
    started = api.client.post(
        f"/v1/admin/questions/{qid(v1.question_id)}/revisions", headers=api.headers(Role.REVIEWER)
    )
    v2 = ids.decode(ids.QUESTION_VERSION, started.json()["id"])
    created = history(api, v2)[0]
    assert created["action"] == "created"
    assert created["based_on"] == vid(v1.id)
    assert created["superseded_by"] is None

    sub = api.client.post(vurl(v2, "/submit"), headers=api.headers(Role.REVIEWER))
    api.client.post(
        vurl(v2, "/approve"),
        headers=api.headers(Role.CONTENT_ADMIN),
        json={"expected_content_sha256": sub.json()["content_sha256"]},
    )
    published = api.client.post(
        vurl(v2, "/publish"),
        headers=api.headers(Role.CONTENT_ADMIN),
        json={"expected_content_sha256": sub.json()["content_sha256"]},
    )
    assert published.status_code == 200
    old = history(api, v1.id)
    assert old[-1]["action"] == "superseded"
    assert old[-1]["superseded_by"] == vid(v2)
    assert old[-1]["status"] == "withdrawn"
    assert old[-1]["previous_status"] == "published"
    assert old[-1]["actor"] == api.actor(Role.CONTENT_ADMIN)
    assert old[-1]["based_on"] is None
    # the history of one version holds nothing about another
    assert {i["content_sha256"] for i in history(api, v2)} <= {
        created["content_sha256"],
    } | {sub.json()["content_sha256"]}


def test_approver_is_last_editor_is_set_on_the_approval_only(
    api: ApiHarness, session: Session, env: Env
) -> None:
    view = create(session, env, actor=api.actor(Role.REVIEWER))
    api.client.post(vurl(view.id, "/submit"), headers=api.headers(Role.REVIEWER))
    api.client.post(
        vurl(view.id, "/approve"),
        headers=api.headers(Role.REVIEWER),
        json={"expected_content_sha256": stored_hash(session, view.id)},
    )
    items = history(api, view.id)
    flags = {i["action"]: i["approver_is_last_editor"] for i in items}
    assert flags["approved"] is True
    assert all(v is None for action, v in flags.items() if action != "approved")


def test_an_imported_questions_first_entry_carries_the_source_ref(
    api: ApiHarness, session: Session, env: Env
) -> None:
    view = svc.create_question(
        session,
        actor=AUTHOR,
        document=document(),
        rights_record_id=env.rights_record_id,
        syllabus_version_id=env.syllabus_version_id,
        source_ref="synthetic/import-2",
    )
    entry = history(api, view.id)[0]
    assert entry["source_ref"] == "synthetic/import-2"
    assert entry["actor"] == AUTHOR


def test_withdraw_and_republish_reasons_show_in_the_history(
    api: ApiHarness, session: Session, connection: Connection, env: Env
) -> None:
    view = bring_to(session, connection, env, "published")
    api.client.post(
        vurl(view.id, "/withdraw"),
        headers=api.headers(Role.CONTENT_ADMIN),
        json={"reason": "wrong mark scheme"},
    )
    api.client.post(
        vurl(view.id, "/republish"),
        headers=api.headers(Role.CONTENT_ADMIN),
        json={
            "expected_content_sha256": stored_hash(session, view.id),
            "reason": "mark scheme fixed",
        },
    )
    tail = history(api, view.id)[-2:]
    assert [(i["action"], i["reason"]) for i in tail] == [
        ("withdrawn", "wrong mark scheme"),
        ("republished", "mark scheme fixed"),
    ]


def test_the_history_of_an_unknown_version_is_404(api: ApiHarness) -> None:
    response = api.client.get(vurl(uuid.uuid4(), "/history"), headers=api.headers(Role.REVIEWER))
    assert response.status_code == 404


def test_the_history_does_not_echo_service_actors_as_account_ids(
    api: ApiHarness, session: Session, env: Env
) -> None:
    # `actor` is returned as written (spec 3.5): a seeded actor is not rewritten to acc_...
    view = create(session, env, actor=PUBLISHER)
    assert history(api, view.id)[0]["actor"] == PUBLISHER
