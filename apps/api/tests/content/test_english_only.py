"""The English-only content rule (docs/slices/M1G-EN-INGILIZCE.md sections 4 and 5.4).

The walker is pure; the write-path tests need the database. Documents are synthetic.
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any

import pytest
from sqlalchemy import Connection
from sqlalchemy.orm import Session

from qlab.content import service as svc
from qlab.content.schema import QuestionDocument, non_english_message, non_english_paths
from tests.content import samples
from tests.content.support import (
    AUTHOR,
    Env,
    Json,
    bring_to,
    create,
    document,
    make_env,
    raw_full_version,
    raw_question,
    raw_version,
    raw_walk,
    snapshot,
    table_counts,
    usable,
)

OP_ACTOR = "u_operator"
TURKISH = ["ğ", "Ğ", "ı", "İ", "ş", "Ş"]


def _set(d: Json, path: tuple[str | int, ...], value: str) -> Json:
    out = copy.deepcopy(d)
    node: Any = out
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    return out


def _doc(d: Json) -> QuestionDocument:
    return QuestionDocument.model_validate(d)


FIELD_CASES: dict[str, tuple[Callable[[], Json], tuple[str | int, ...], str]] = {
    "outcome": (samples.mcq_document, ("outcome",), "outcome"),
    "stem_text": (
        samples.structured_document,
        ("stem", "content", 0, "content", 0, "text"),
        "stem.content[0].content[0].text",
    ),
    "stimulus_description": (
        samples.structured_document,
        ("stimuli", 0, "description"),
        "stimuli[0].description",
    ),
    "note": (
        samples.structured_document,
        ("parts", 1, "notes", 0, "content", "content", 0, "content", 0, "text"),
        "parts[1].notes[0].content.content[0].content[0].text",
    ),
    "explanation": (
        samples.mcq_document,
        ("mcq", "explanation", "content", 0, "content", 0, "text"),
        "mcq.explanation.content[0].content[0].text",
    ),
    "rationale": (
        samples.mcq_document,
        ("mcq", "options", 1, "rationale", "content", 0, "content", 0, "text"),
        "mcq.options[1].rationale.content[0].content[0].text",
    ),
}


def test_the_unchanged_samples_are_clean() -> None:
    for build in (samples.mcq_document, samples.structured_document, samples.data_based_document):
        assert non_english_paths(_doc(build())) == []


@pytest.mark.parametrize("name", list(FIELD_CASES))
def test_a_turkish_letter_is_found_in_every_kind_of_field(name: str) -> None:
    build, path, expected = FIELD_CASES[name]
    base = build()
    original: Any = base
    for key in path:
        original = original[key]
    changed = _set(base, path, f"{original}ş")
    found = non_english_paths(_doc(changed))
    assert found == [expected]


@pytest.mark.parametrize("letter", TURKISH)
def test_each_turkish_only_letter_is_flagged(letter: str) -> None:
    d = _set(samples.mcq_document(), ("outcome",), f"speed {letter} of light")
    assert non_english_paths(_doc(d)) == ["outcome"]


def test_latex_attributes_and_solution_model_names_are_walked() -> None:
    d = samples.mcq_document()
    latex_path = ("mcq", "options", 1, "rationale", "content", 0, "content", 1, "attrs", "latex")
    assert non_english_paths(_doc(_set(d, latex_path, "x_ş"))) == [
        "mcq.options[1].rationale.content[0].content[1].attrs.latex"
    ]
    # Names and units are pattern-constrained, so build the model without validation: the walker
    # must still look at every string it can reach.
    document = _doc(d)
    model: Any = document.solution_model
    parameter = model.parameters[0].model_construct(name="hız", value="1", unit="")
    bare = document.model_construct(solution_model=model.model_construct(parameters=(parameter,)))
    assert non_english_paths(bare) == ["solution_model.parameters[0].name"]


def test_dotted_capital_and_dotless_small_i_are_flagged() -> None:
    assert non_english_paths(_doc(_set(samples.mcq_document(), ("outcome",), "İstanbul"))) == [
        "outcome"
    ]
    assert non_english_paths(_doc(_set(samples.mcq_document(), ("outcome",), "kısa"))) == [
        "outcome"
    ]


def test_schrodinger_and_other_shared_letters_are_accepted() -> None:
    text = "Schrödinger equation, Müller, façade, Ångström"
    d = _set(samples.mcq_document(), ("outcome",), text)
    assert non_english_paths(_doc(d)) == []


def test_every_finding_is_listed_and_the_message_is_fixed() -> None:
    d = _set(samples.mcq_document(), ("outcome",), "şekil")
    d = _set(d, ("mcq", "explanation", "content", 0, "content", 0, "text"), "çözüm ve ığ")
    found = non_english_paths(_doc(d))
    assert found == ["outcome", "mcq.explanation.content[0].content[0].text"]
    assert non_english_message(found).startswith(
        "Content must be written in English; found non-English letters at outcome"
    )


# --- write paths ----------------------------------------------------------------------------

db = pytest.mark.db


def _turkish() -> QuestionDocument:
    return _doc(_set(samples.data_based_document(), ("outcome",), "hız ve ivme"))


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


def _english_error(error: svc.InvalidDocument) -> None:
    assert "Content must be written in English; found non-English letters at outcome" in str(error)


@db
def test_create_question_rejects_turkish_and_stores_nothing(
    session: Session, connection: Connection, env: Env
) -> None:
    before = table_counts(connection)
    with pytest.raises(svc.InvalidDocument) as caught:
        create(session, env, _turkish())
    _english_error(caught.value)
    assert table_counts(connection) == before
    usable(session)


@db
def test_create_with_a_source_ref_rejects_turkish_like_the_pilot_import_does(
    session: Session, connection: Connection, env: Env
) -> None:
    before = table_counts(connection)
    with pytest.raises(svc.InvalidDocument) as caught:
        svc.create_question(
            session,
            actor="system:pilot_import",
            document=_turkish(),
            rights_record_id=env.rights_record_id,
            syllabus_version_id=env.syllabus_version_id,
            source_ref="a1-turkish-1",
        )
    _english_error(caught.value)
    assert table_counts(connection) == before


@db
def test_update_draft_rejects_turkish_and_changes_nothing(
    session: Session, connection: Connection, env: Env
) -> None:
    version = create(session, env, document())
    before = snapshot(session, connection, version.question_id)
    with pytest.raises(svc.InvalidDocument) as caught:
        svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=_turkish())
    _english_error(caught.value)
    assert snapshot(session, connection, version.question_id) == before


@db
def test_update_from_needs_fix_rejects_turkish(
    session: Session, connection: Connection, env: Env
) -> None:
    version = bring_to(session, connection, env, "needs_fix")
    with pytest.raises(svc.InvalidDocument):
        svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=_turkish())


@db
def test_a_document_with_schrodinger_is_accepted_by_create_and_update(
    session: Session, env: Env
) -> None:
    d = _doc(_set(samples.data_based_document(), ("outcome",), "Schrödinger model"))
    version = create(session, env, d)
    again = svc.update_draft(session, actor=OP_ACTOR, version_id=version.id, document=d)
    assert again.document.outcome == "Schrödinger model"


@db
def test_start_revision_refuses_to_copy_a_turkish_published_row(
    session: Session, connection: Connection, env: Env
) -> None:
    turkish = _turkish()
    raw = raw_full_version(connection, env, turkish)
    question_id = raw.question_id
    raw_walk(connection, raw.version_id, "published")
    before = table_counts(connection)
    with pytest.raises(svc.InvalidDocument) as caught:
        svc.start_revision(session, actor=OP_ACTOR, question_id=question_id)
    _english_error(caught.value)
    assert table_counts(connection) == before


@db
def test_reading_a_turkish_row_stored_before_the_rule_still_works(
    session: Session, connection: Connection, env: Env
) -> None:
    question_id = raw_question(connection, env)
    version_id = raw_version(connection, question_id, _turkish())
    read = svc.get_version(session, version_id)
    assert read.document.outcome == "hız ve ivme"
    assert [v.id for v in svc.list_versions(session, question_id)] == [version_id]
    assert svc.get_question(session, question_id).id == question_id
    assert AUTHOR  # the row was written by a raw insert, not by the service
