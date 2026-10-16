"""Where a refused document is wrong: `InvalidDocument.errors` are `DocumentProblem`s whose
`location` is a dotted path inside the document (list indices as numbers), or None when the
problem is about the document as a whole (docs/slices/M1G-7C-YAZIM.md section 1, item 2).
"""

from __future__ import annotations

import pytest
from sqlalchemy import Connection
from sqlalchemy.orm import Session

from qlab.content import service as svc
from tests.content import samples
from tests.content.support import (
    Env,
    Json,
    create,
    document,
    make_env,
    table_counts,
    with_command_term,
    with_exam_section,
    with_nodes,
)

db = pytest.mark.db
node = pytest.mark.node


@pytest.fixture
def env(session: Session) -> Env:
    return make_env(session)


def problems(doc: Json, session: Session, env: Env) -> list[svc.DocumentProblem]:
    with pytest.raises(svc.InvalidDocument) as caught:
        create(session, env, document(doc))
    return list(caught.value.errors)


def locations(found: list[svc.DocumentProblem]) -> list[str | None]:
    return [p.location for p in found]


@db
def test_unknown_exam_section_is_located(session: Session, env: Env) -> None:
    found = problems(with_exam_section("paper_9"), session, env)
    assert locations(found) == ["exam_section"]
    assert "paper_9" in found[0].message


@db
def test_unknown_command_term_is_located_at_its_part(session: Session, env: Env) -> None:
    doc = samples.question(samples.part("p1", "a"), samples.part("p2", "b", command_term="juggle"))
    found = problems(doc, session, env)
    assert locations(found) == ["parts.1.command_term"]
    assert "juggle" in found[0].message


@db
def test_command_term_on_the_first_part(session: Session, env: Env) -> None:
    found = problems(with_command_term("juggle"), session, env)
    assert locations(found) == ["parts.0.command_term"]


@db
def test_unknown_nodes_are_located(session: Session, env: Env) -> None:
    found = problems(with_nodes("Z.9", ("Z.8",)), session, env)
    assert locations(found) == ["primary_syllabus_node", "secondary_syllabus_nodes.0"]


@db
def test_every_vocabulary_problem_has_its_own_location(session: Session, env: Env) -> None:
    doc = with_exam_section("paper_9")
    doc["parts"][0]["command_term"] = "juggle"
    found = problems(doc, session, env)
    assert locations(found) == ["exam_section", "parts.0.command_term"]


@db
def test_a_document_too_large_has_no_location(session: Session, env: Env) -> None:
    doc = samples.data_based_document()
    doc["outcome"] = "x" * (svc.MAX_DOCUMENT_BYTES + 1)
    found = problems(doc, session, env)
    assert len(found) == 1 and found[0].location is None
    assert "larger than" in found[0].message


@db
def test_a_nul_character_has_no_location(session: Session, env: Env) -> None:
    doc = samples.data_based_document()
    doc["outcome"] = "a\u0000b"
    found = problems(doc, session, env)
    assert len(found) == 1 and found[0].location is None
    assert "NUL" in found[0].message


@db
def test_each_turkish_path_is_its_own_located_problem(session: Session, env: Env) -> None:
    doc = samples.data_based_document()
    doc["outcome"] = "hız"
    doc["parts"][1]["mark_points"][0]["content"] = samples.line(samples.text("şu"))
    found = problems(doc, session, env)
    assert locations(found) == [
        "outcome",
        "parts.1.mark_points.0.content.content.0.content.0.text",
    ]
    assert len({p.message for p in found}) == 1
    assert "Content must be written in English" in found[0].message


@db
def test_turkish_in_an_mcq_option_uses_numeric_indices(session: Session, env: Env) -> None:
    doc = samples.mcq_document()
    doc["mcq"]["options"][1]["rationale"] = samples.line(samples.text("ı"))
    found = problems(doc, session, env)
    assert locations(found) == ["mcq.options.1.rationale.content.0.content.0.text"]


def bad_math_in_mark_point(latex: str, *, other_good: str = "x^2") -> Json:
    doc = samples.question(samples.part("p1", "a", 2))
    doc["parts"][0]["mark_points"][1]["content"] = samples.line(
        samples.text("one "), samples.math(other_good), samples.math(latex)
    )
    return doc


@node
@db
def test_a_math_node_deep_in_a_mark_point_is_located(session: Session, env: Env) -> None:
    found = problems(bad_math_in_mark_point(r"\href{http://example.org}{x}"), session, env)
    assert locations(found) == ["parts.0.mark_points.1.content.content.0.content.2.attrs.latex"]
    assert "not allowed" in found[0].message


@node
@db
def test_math_that_does_not_render_is_located(session: Session, env: Env) -> None:
    found = problems(bad_math_in_mark_point("x^"), session, env)
    assert locations(found) == ["parts.0.mark_points.1.content.content.0.content.2.attrs.latex"]
    assert "does not render" in found[0].message


@node
@db
def test_a_math_block_is_located(session: Session, env: Env) -> None:
    doc = samples.data_based_document()
    doc["stem"] = samples.doc(
        samples.paragraph(samples.text("Given:")), samples.math_block(r"\def\q{1}")
    )
    found = problems(doc, session, env)
    assert locations(found) == ["stem.content.1.attrs.latex"]


@node
@db
def test_the_same_bad_node_in_two_places_is_reported_at_both(
    session: Session, env: Env, connection: Connection
) -> None:
    doc = samples.question(samples.part("p1", "a", 2))
    bad = r"\href{http://example.org}{x}"
    doc["parts"][0]["mark_points"][0]["content"] = samples.line(samples.math(bad))
    doc["parts"][0]["mark_points"][1]["content"] = samples.line(samples.math(bad))
    before = table_counts(connection)
    found = problems(doc, session, env)
    assert locations(found) == [
        "parts.0.mark_points.0.content.content.0.content.0.attrs.latex",
        "parts.0.mark_points.1.content.content.0.content.0.attrs.latex",
    ]
    assert table_counts(connection) == before


@node
@db
def test_update_draft_reports_the_same_locations(session: Session, env: Env) -> None:
    version = create(session, env)
    with pytest.raises(svc.InvalidDocument) as caught:
        svc.update_draft(
            session,
            actor="u_editor",
            version_id=version.id,
            document=document(with_exam_section("paper_9")),
        )
    assert locations(list(caught.value.errors)) == ["exam_section"]


def test_the_error_message_joins_the_problem_messages() -> None:
    error = svc.InvalidDocument((svc.DocumentProblem("one", "a.0"), svc.DocumentProblem("two")))
    assert str(error) == "one; two"
    assert error.errors[1].location is None
