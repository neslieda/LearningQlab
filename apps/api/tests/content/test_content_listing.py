"""The content service's listing and history functions, from their docstrings.

`list_questions`, `list_published`, `get_history` and `ListFilter` in qlab.content.service;
CLAUDE.md rules 2 and 7; docs/slices/M1G-5-SOZLESME.md sections 3.2 and 3.5. Written without
reading their bodies.
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any

import pytest
from sqlalchemy import Connection
from sqlalchemy.orm import Session

from qlab.content import service as svc
from qlab.content.schema import Level, QuestionClass
from qlab.content.service import ListFilter, VersionStatus
from qlab.rights import service as rights
from tests.content import samples
from tests.content.support import (
    AUTHOR,
    PUBLISHER,
    REVIEWER,
    Env,
    approve,
    audit_for,
    bring_to,
    create,
    document,
    make_env,
    new_rights,
    now,
    publish,
    raw_question,
    raw_version,
    usable,
)

pytestmark = [pytest.mark.db, pytest.mark.node]

MAX = svc.MAX_LIST_LIMIT
FIRST = uuid.UUID(int=0)
LAST = uuid.UUID(int=(1 << 128) - 1)


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


def question_ids(items: Any) -> list[uuid.UUID]:
    return [i.question.id if isinstance(i, svc.QuestionListItem) else i.question_id for i in items]


def listing(session: Session, **kwargs: Any) -> list[svc.QuestionListItem]:
    kwargs.setdefault("limit", MAX)
    return svc.list_questions(session, **kwargs)


def published(session: Session, **kwargs: Any) -> list[svc.VersionSummary]:
    kwargs.setdefault("limit", MAX)
    return svc.list_published(session, **kwargs)


# --- limit validation ------------------------------------------------------------------------


@pytest.mark.parametrize("limit", [0, -1, MAX + 1, 10_000])
@pytest.mark.parametrize("function", ["list_questions", "list_published"])
def test_a_limit_outside_1_to_the_maximum_is_a_value_error_and_the_session_survives(
    session: Session, env: Env, function: str, limit: int
) -> None:
    create(session, env)
    with pytest.raises(ValueError):
        getattr(svc, function)(session, limit=limit)
    usable(session)


@pytest.mark.parametrize("limit", [1, 2, MAX - 1, MAX])
@pytest.mark.parametrize("function", ["list_questions", "list_published"])
def test_limits_inside_the_range_are_accepted(
    session: Session, connection: Connection, env: Env, function: str, limit: int
) -> None:
    bring_to(session, connection, env, "published")
    result = getattr(svc, function)(session, limit=limit)
    assert len(result) == 1


def test_the_maximum_limit_is_one_more_than_an_api_page() -> None:
    assert svc.MAX_LIST_LIMIT == 101


def test_a_page_is_at_most_limit_long(session: Session, env: Env) -> None:
    for _ in range(5):
        create(session, env)
    assert len(listing(session, limit=3)) == 3
    assert len(listing(session, limit=5)) == 5
    assert len(listing(session, limit=100)) == 5


# --- ordering and `after` --------------------------------------------------------------------


def test_questions_come_in_ascending_id_order(session: Session, env: Env) -> None:
    created = [create(session, env).question_id for _ in range(6)]
    got = question_ids(listing(session))
    assert got == sorted(created)
    assert got == sorted(got)


def test_after_returns_only_larger_ids(session: Session, env: Env) -> None:
    created = sorted(create(session, env).question_id for _ in range(5))
    assert question_ids(listing(session, after=created[1])) == created[2:]
    assert question_ids(listing(session, after=created[-1])) == []
    assert question_ids(listing(session, after=FIRST)) == created
    assert question_ids(listing(session, after=LAST)) == []


def test_after_with_an_id_that_does_not_exist_still_splits_the_list(
    session: Session, env: Env
) -> None:
    created = sorted(create(session, env).question_id for _ in range(4))
    midpoint = uuid.UUID(int=(created[1].int + created[2].int) // 2)
    assert question_ids(listing(session, after=midpoint)) == created[2:]


def test_walking_pages_with_after_covers_everything_exactly_once(
    session: Session, env: Env
) -> None:
    created = sorted(create(session, env).question_id for _ in range(7))
    seen: list[uuid.UUID] = []
    after: uuid.UUID | None = None
    while True:
        page = question_ids(listing(session, after=after, limit=3))
        if not page:
            break
        seen += page
        after = page[-1]
    assert seen == created


def test_an_empty_bank_gives_an_empty_list(session: Session, env: Env) -> None:
    assert listing(session) == []
    assert published(session) == []


# --- list_questions --------------------------------------------------------------------------


def test_every_status_is_listed_and_the_item_describes_the_latest_version(
    session: Session, connection: Connection, env: Env
) -> None:
    drafts = bring_to(session, connection, env, "draft")
    in_review = bring_to(session, connection, env, "in_review")
    live = bring_to(session, connection, env, "published")
    gone = bring_to(session, connection, env, "withdrawn")
    rejected = bring_to(session, connection, env, "rejected")
    items = {i.question.id: i for i in listing(session)}
    assert set(items) == {v.question_id for v in (drafts, in_review, live, gone, rejected)}
    assert items[drafts.question_id].latest.status is VersionStatus.DRAFT
    assert items[in_review.question_id].latest.status is VersionStatus.IN_REVIEW
    assert items[live.question_id].latest.status is VersionStatus.PUBLISHED
    assert items[gone.question_id].latest.status is VersionStatus.WITHDRAWN
    assert items[rejected.question_id].latest.status is VersionStatus.REJECTED
    item = items[live.question_id]
    assert isinstance(item.latest, svc.VersionSummary)
    assert item.latest == svc.summarize(svc.get_version(session, live.id))
    assert item.question == svc.get_question(session, live.question_id)


def test_published_and_working_pointers(session: Session, connection: Connection, env: Env) -> None:
    plain = bring_to(session, connection, env, "draft")
    live = bring_to(session, connection, env, "published")
    gone = bring_to(session, connection, env, "withdrawn")
    revised = bring_to(session, connection, env, "published")
    revision = svc.start_revision(session, actor=AUTHOR, question_id=revised.question_id)
    items = {i.question.id: i for i in listing(session)}
    assert (
        items[plain.question_id].published_version_id,
        items[plain.question_id].working_version_id,
    ) == (
        None,
        plain.id,
    )
    assert (
        items[live.question_id].published_version_id,
        items[live.question_id].working_version_id,
    ) == (
        live.id,
        None,
    )
    assert (
        items[gone.question_id].published_version_id,
        items[gone.question_id].working_version_id,
    ) == (
        None,
        None,
    )
    assert items[revised.question_id].latest.id == revision.id
    assert items[revised.question_id].latest.version_no == 2
    assert items[revised.question_id].published_version_id == revised.id
    assert items[revised.question_id].working_version_id == revision.id


@pytest.fixture
def varied(
    session: Session, connection: Connection, env: Env
) -> dict[str, svc.QuestionVersionView]:
    """Questions that differ in every filter field."""
    bank = {
        "mcq_draft": bring_to(
            session, connection, env, "draft", document(samples.plain_mcq_document())
        ),
        "data_review": bring_to(
            session, connection, env, "in_review", document(samples.data_based_document())
        ),
        "hl_published": bring_to(
            session, connection, env, "published", document(samples.two_column_mcq_document())
        ),
        "long_approved": bring_to(
            session, connection, env, "approved", document(samples.show_that_document())
        ),
        "visual_draft": bring_to(
            session, connection, env, "draft", document(samples.structured_document())
        ),
    }
    return bank


def by_filter(
    session: Session, varied: dict[str, svc.QuestionVersionView], **kwargs: Any
) -> set[str]:
    wanted = {v.question_id: name for name, v in varied.items()}
    return {wanted[i] for i in question_ids(listing(session, filter=ListFilter(**kwargs)))}


def test_an_empty_filter_matches_everything(
    session: Session, varied: dict[str, svc.QuestionVersionView]
) -> None:
    assert by_filter(session, varied) == set(varied)
    none_filter = question_ids(listing(session, filter=None))
    assert len(none_filter) == len(varied)


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"status": VersionStatus.DRAFT}, {"mcq_draft", "visual_draft"}),
        ({"status": VersionStatus.IN_REVIEW}, {"data_review"}),
        ({"status": VersionStatus.PUBLISHED}, {"hl_published"}),
        ({"status": VersionStatus.APPROVED}, {"long_approved"}),
        ({"status": VersionStatus.REJECTED}, set()),
        ({"exam_section": "paper_1a"}, {"mcq_draft", "hl_published"}),
        ({"exam_section": "paper_2"}, {"long_approved", "visual_draft"}),
        ({"exam_section": "nonexistent"}, set()),
        ({"level": Level.SL}, {"mcq_draft", "data_review", "visual_draft"}),
        (
            {"level": Level.HL},
            {"mcq_draft", "data_review", "hl_published", "long_approved", "visual_draft"},
        ),
        ({"question_class": QuestionClass.MCQ}, {"mcq_draft", "hl_published"}),
        ({"question_class": QuestionClass.LONG_STRUCTURED}, {"long_approved"}),
        ({"syllabus_node": "A.4"}, {"hl_published", "long_approved"}),
        ({"syllabus_node": "A.2"}, {"long_approved"}),  # a secondary node
        ({"syllabus_node": "B.2"}, {"mcq_draft"}),
        ({"syllabus_node": "A.1"}, {"data_review", "visual_draft"}),
        ({"has_unverified_visuals": True}, {"visual_draft"}),
        (
            {"has_unverified_visuals": False},
            {"mcq_draft", "data_review", "hl_published", "long_approved"},
        ),
        ({"status": VersionStatus.DRAFT, "question_class": QuestionClass.MCQ}, {"mcq_draft"}),
        (
            {"exam_section": "paper_2", "level": Level.SL, "has_unverified_visuals": True},
            {"visual_draft"},
        ),
        ({"exam_section": "paper_2", "level": Level.SL, "status": VersionStatus.APPROVED}, set()),
    ],
)
def test_each_filter_field_and_their_combinations(
    session: Session,
    varied: dict[str, svc.QuestionVersionView],
    kwargs: dict[str, Any],
    expected: set[str],
) -> None:
    assert by_filter(session, varied, **kwargs) == expected


def test_the_filter_is_about_the_latest_version_only(
    session: Session, connection: Connection, env: Env
) -> None:
    old = bring_to(
        session, connection, env, "published", document(samples.two_column_mcq_document())
    )
    started = svc.start_revision(session, actor=AUTHOR, question_id=old.question_id)
    latest = svc.update_draft(
        session,
        actor=AUTHOR,
        version_id=started.id,
        document=document(samples.show_that_document()),
    )

    def matches(**kwargs: Any) -> list[uuid.UUID]:
        return question_ids(listing(session, filter=ListFilter(**kwargs)))

    assert matches(question_class=QuestionClass.MCQ) == []
    assert matches(question_class=QuestionClass.LONG_STRUCTURED) == [old.question_id]
    assert matches(status=VersionStatus.PUBLISHED) == []
    assert matches(status=VersionStatus.DRAFT) == [old.question_id]
    assert matches(syllabus_node="A.2") == [old.question_id]  # a secondary node of the latest
    assert matches(exam_section="paper_1a") == []
    assert matches(exam_section="paper_2") == [old.question_id]
    assert latest.version_no == 2

    # the pointers do not depend on the filter
    item = listing(session, filter=ListFilter(status=VersionStatus.DRAFT))[0]
    assert item.published_version_id == old.id
    assert item.working_version_id == latest.id
    assert item.latest.id == latest.id


def test_a_question_whose_latest_version_was_rejected_is_described_by_it(
    session: Session, connection: Connection, env: Env
) -> None:
    live = bring_to(session, connection, env, "published")
    revision = svc.start_revision(session, actor=AUTHOR, question_id=live.question_id)
    svc.submit(session, actor=AUTHOR, version_id=revision.id)
    svc.reject(session, actor=REVIEWER, version_id=revision.id, reason="not good")
    item = listing(session)[0]
    assert item.latest.id == revision.id
    assert item.latest.status is VersionStatus.REJECTED
    assert item.published_version_id == live.id
    assert item.working_version_id is None


# --- rights ----------------------------------------------------------------------------------


def bad_record(session: Session, how: str) -> uuid.UUID:
    """A record that does not permit display to everyone now."""
    if how == "revoked":
        return new_rights(session, revoked=True)
    if how == "expired":
        return new_rights(
            session, valid_from=now() - timedelta(days=10), valid_until=now() - timedelta(days=1)
        )
    if how == "future":
        return new_rights(session, valid_from=now() + timedelta(days=1))
    assert how == "organization_only"
    return new_rights(session, scope=rights.DisplayScope.ORGANIZATION)


def raw_with_record(connection: Connection, env: Env, record: uuid.UUID) -> uuid.UUID:
    """A question (one draft version, written with raw SQL) under another rights record: the
    service refuses to create one under a record that does not permit display."""
    question = raw_question(connection, Env(env.syllabus_version_id, record))
    raw_version(connection, question)
    return question


def lose_display_rights(
    connection: Connection, session: Session, how: str, record: uuid.UUID
) -> None:
    """Make an existing record stop permitting display (revocation is the only change a
    record allows)."""
    assert how == "revoked"
    rights.revoke(session, record, at=now())
    session.flush()
    session.expire_all()


@pytest.mark.parametrize("how", ["revoked", "expired", "future", "organization_only"])
def test_questions_whose_rights_do_not_permit_display_are_not_listed(
    session: Session, connection: Connection, env: Env, how: str
) -> None:
    visible = create(session, env)
    raw_with_record(connection, env, bad_record(session, how))
    assert question_ids(listing(session)) == [visible.question_id]
    raw_with_record(connection, env, env.rights_record_id)
    assert len(listing(session)) == 2


def test_rights_filtering_happens_before_the_limit_so_a_page_is_short_only_at_the_end(
    session: Session, connection: Connection, env: Env
) -> None:
    good, bad = new_rights(session), new_rights(session)
    views = []
    for index in range(9):
        record = good if index % 3 == 2 else bad
        views.append(create(session, env, rights_record_id=record))
    lose_display_rights(connection, session, "revoked", bad)
    visible = sorted(v.question_id for index, v in enumerate(views) if index % 3 == 2)
    assert len(visible) == 3
    first = question_ids(listing(session, limit=2))
    assert first == visible[:2]
    second = question_ids(listing(session, after=first[-1], limit=2))
    assert second == visible[2:]
    assert len(second) < 2  # short because it is the end
    assert question_ids(listing(session, limit=3)) == visible


def test_rights_are_decided_once_per_distinct_record(
    session: Session, connection: Connection, env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    good, bad = new_rights(session), new_rights(session)
    for index in range(6):
        create(session, env, rights_record_id=good if index % 2 else bad)
    lose_display_rights(connection, session, "revoked", bad)
    calls: list[uuid.UUID | None] = []
    original = rights.is_permitted

    def counting(session: Session, record_id: uuid.UUID | None, *args: Any, **kwargs: Any) -> bool:
        calls.append(record_id)
        return original(session, record_id, *args, **kwargs)

    monkeypatch.setattr(rights, "is_permitted", counting)
    assert len(listing(session)) == 3
    assert sorted(calls, key=str) == sorted([good, bad], key=str)


def test_a_record_revoked_after_publishing_removes_the_question_from_both_lists(
    session: Session, connection: Connection, env: Env
) -> None:
    record = new_rights(session)
    live = bring_to(session, connection, env, "published", rights_record_id=record)
    assert question_ids(listing(session)) == [live.question_id]
    assert question_ids(published(session)) == [live.question_id]
    rights.revoke(session, record, at=now())
    session.flush()
    assert listing(session) == []
    assert published(session) == []


# --- list_published --------------------------------------------------------------------------


def test_list_published_returns_only_the_published_version_of_questions_that_have_one(
    session: Session, connection: Connection, env: Env
) -> None:
    for status in ("draft", "needs_fix", "in_review", "approved", "withdrawn", "rejected"):
        bring_to(session, connection, env, status)
    live = bring_to(session, connection, env, "published")
    result = published(session)
    assert [v.id for v in result] == [live.id]
    assert all(isinstance(v, svc.VersionSummary) for v in result)
    assert all(v.status is VersionStatus.PUBLISHED for v in result)
    assert result[0] == svc.summarize(svc.get_version(session, live.id))


def test_list_published_shows_the_published_version_not_the_newer_working_one(
    session: Session, connection: Connection, env: Env
) -> None:
    live = bring_to(
        session, connection, env, "published", document(samples.two_column_mcq_document())
    )
    revision = svc.start_revision(session, actor=AUTHOR, question_id=live.question_id)
    svc.update_draft(
        session,
        actor=AUTHOR,
        version_id=revision.id,
        document=document(samples.show_that_document()),
    )
    [summary] = published(session)
    assert summary.id == live.id
    assert summary.version_no == 1
    assert summary.question_class is QuestionClass.MCQ


def test_a_superseded_version_is_never_listed(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = bring_to(session, connection, env, "published")
    v2 = svc.start_revision(session, actor=AUTHOR, question_id=v1.question_id)
    svc.submit(session, actor=AUTHOR, version_id=v2.id)
    approve(session, v2.id)
    publish(session, v2.id, PUBLISHER)
    assert [v.id for v in published(session)] == [v2.id]


def test_list_published_orders_and_pages_by_question_id(
    session: Session, connection: Connection, env: Env
) -> None:
    created = sorted(bring_to(session, connection, env, "published").question_id for _ in range(4))
    assert question_ids(published(session)) == created
    assert question_ids(published(session, after=created[1])) == created[2:]
    assert question_ids(published(session, limit=2)) == created[:2]
    assert question_ids(published(session, after=LAST)) == []


def test_list_published_filter_applies_to_the_published_version(
    session: Session, connection: Connection, env: Env
) -> None:
    live = bring_to(
        session, connection, env, "published", document(samples.two_column_mcq_document())
    )
    started = svc.start_revision(session, actor=AUTHOR, question_id=live.question_id)
    svc.update_draft(
        session,
        actor=AUTHOR,
        version_id=started.id,
        document=document(samples.show_that_document()),
    )
    other = bring_to(session, connection, env, "published", document(samples.mcq_document()))

    def matches(**kwargs: Any) -> set[uuid.UUID]:
        return set(question_ids(published(session, filter=ListFilter(**kwargs))))

    assert matches(question_class=QuestionClass.MCQ) == {live.question_id, other.question_id}
    assert matches(question_class=QuestionClass.LONG_STRUCTURED) == set()
    assert matches(syllabus_node="A.4") == {live.question_id}
    assert matches(syllabus_node="A.2") == set()  # a secondary node of the working version only
    assert matches(level=Level.SL) == {other.question_id}
    assert matches(level=Level.HL) == {live.question_id, other.question_id}
    assert matches(exam_section="paper_1a") == {live.question_id, other.question_id}
    assert matches(exam_section="paper_2") == set()
    assert matches(has_unverified_visuals=False) == {live.question_id, other.question_id}
    assert matches(has_unverified_visuals=True) == set()


@pytest.mark.parametrize("status", list(VersionStatus))
def test_list_published_rejects_a_status_filter_of_any_value(
    session: Session, connection: Connection, env: Env, status: VersionStatus
) -> None:
    bring_to(session, connection, env, "published")
    with pytest.raises(ValueError):
        published(session, filter=ListFilter(status=status))
    usable(session)


def test_list_published_accepts_a_filter_without_a_status(
    session: Session, connection: Connection, env: Env
) -> None:
    bring_to(session, connection, env, "published")
    assert len(published(session, filter=ListFilter())) == 1
    assert len(published(session, filter=None)) == 1


# --- get_history -----------------------------------------------------------------------------


def test_history_is_the_audit_of_that_version_oldest_first(
    session: Session, connection: Connection, env: Env
) -> None:
    view = bring_to(session, connection, env, "published")
    other = bring_to(session, connection, env, "in_review")
    entries = svc.get_history(session, view.id)
    assert [e.action for e in entries] == [
        "question_version.created",
        "question_version.submitted",
        "question_version.checks_passed",
        "question_version.approved",
        "question_version.published",
    ]
    assert all(e.entity_type == "question_version" for e in entries)
    assert all(e.entity_id == str(view.id) for e in entries)
    assert entries == audit_for(session, view.id)
    assert [e.actor for e in entries][0] == AUTHOR
    assert [e.actor for e in entries][-1] == PUBLISHER
    assert svc.get_history(session, other.id)[-1].action == "question_version.checks_passed"
    assert all(e.entity_id == str(other.id) for e in svc.get_history(session, other.id))


def test_history_of_a_superseded_version_ends_with_the_superseding_entry(
    session: Session, connection: Connection, env: Env
) -> None:
    v1 = bring_to(session, connection, env, "published")
    v2 = svc.start_revision(session, actor=AUTHOR, question_id=v1.question_id)
    svc.submit(session, actor=AUTHOR, version_id=v2.id)
    approve(session, v2.id)
    publish(session, v2.id, PUBLISHER)
    last = svc.get_history(session, v1.id)[-1]
    assert last.action == "question_version.superseded"
    assert str(v2.id) in str(dict(last.data))
    assert svc.get_history(session, v2.id)[0].action == "question_version.created"


def test_history_reflects_a_new_entry_immediately(session: Session, env: Env) -> None:
    view = create(session, env)
    before = len(svc.get_history(session, view.id))
    svc.update_draft(
        session, actor=AUTHOR, version_id=view.id, document=document(samples.mcq_document())
    )
    after = svc.get_history(session, view.id)
    assert len(after) == before + 1
    assert after[-1].action == "question_version.updated"


def test_history_of_an_unknown_version_is_not_found(session: Session, env: Env) -> None:
    create(session, env)
    with pytest.raises(svc.NotFound):
        svc.get_history(session, uuid.uuid4())
    usable(session)


def test_history_when_rights_do_not_permit_display_is_not_found(
    session: Session, connection: Connection, env: Env
) -> None:
    record = new_rights(session)
    view = bring_to(session, connection, env, "published", rights_record_id=record)
    assert svc.get_history(session, view.id)
    rights.revoke(session, record, at=now())
    session.flush()
    with pytest.raises(svc.NotFound):
        svc.get_history(session, view.id)
    usable(session)


def test_history_of_a_withdrawn_version_stays_readable_while_rights_hold(
    session: Session, connection: Connection, env: Env
) -> None:
    view = bring_to(session, connection, env, "withdrawn")
    assert svc.get_history(session, view.id)[-1].action == "question_version.withdrawn"
