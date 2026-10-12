"""Syllabus service: loading reference files, idempotency, updates, conflicts, vocabulary."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest
from sqlalchemy import Connection, text
from sqlalchemy.orm import Session

from qlab.syllabus.reference import ExamFormatDefinition, SyllabusReference
from qlab.syllabus.service import (
    ReferenceConflict,
    Vocabulary,
    find_syllabus_version,
    get_vocabulary,
    load_reference,
    node_ids,
)
from tests.conftest import REPO_ROOT

pytestmark = pytest.mark.db

REAL_FILE = REPO_ROOT / "content" / "reference" / "dp-physics-2025-syllabus.json"

# --- helpers --------------------------------------------------------------------------------

COUNT_SQL = {
    "program": "SELECT count(*) FROM program",
    "subject": "SELECT count(*) FROM subject",
    "syllabus_version": "SELECT count(*) FROM syllabus_version",
    "syllabus_node": "SELECT count(*) FROM syllabus_node",
    "exam_format": "SELECT count(*) FROM exam_format",
}


def counts(connection: Connection) -> dict[str, int]:
    return {table: connection.execute(text(sql)).scalar_one() for table, sql in COUNT_SQL.items()}


@dataclass(frozen=True)
class NodeRow:
    id: uuid.UUID
    title: str
    position: int
    parent: str | None
    attributes: dict[str, Any]


def read_nodes(connection: Connection, version_id: uuid.UUID) -> dict[str, NodeRow]:
    rows = connection.execute(
        text(
            "SELECT n.id, n.code, n.title, n.position, p.code AS parent_code, n.attributes "
            "FROM syllabus_node n LEFT JOIN syllabus_node p ON p.id = n.parent_id "
            "WHERE n.syllabus_version_id = :version_id"
        ),
        {"version_id": version_id},
    ).mappings()
    return {
        row["code"]: NodeRow(
            id=row["id"],
            title=row["title"],
            position=row["position"],
            parent=row["parent_code"],
            attributes=row["attributes"],
        )
        for row in rows
    }


@dataclass(frozen=True)
class Names:
    program: str
    subject: str
    version: str


def read_names(connection: Connection, version_id: uuid.UUID) -> Names:
    row = connection.execute(
        text(
            "SELECT p.name AS program, s.name AS subject, v.title AS version "
            "FROM syllabus_version v JOIN subject s ON s.id = v.subject_id "
            "JOIN program p ON p.id = s.program_id WHERE v.id = :version_id"
        ),
        {"version_id": version_id},
    ).one()
    return Names(program=row.program, subject=row.subject, version=row.version)


def read_exam_definition(connection: Connection, version_id: uuid.UUID) -> ExamFormatDefinition:
    stored = connection.execute(
        text("SELECT definition FROM exam_format WHERE syllabus_version_id = :version_id"),
        {"version_id": version_id},
    ).scalar_one()
    return ExamFormatDefinition.model_validate(stored)


def snapshot(connection: Connection, session: Session, version_id: uuid.UUID) -> dict[str, Any]:
    """Everything observable about one version and the table sizes."""
    return {
        "counts": counts(connection),
        "names": read_names(connection, version_id),
        "nodes": read_nodes(connection, version_id),
        "definition": read_exam_definition(connection, version_id),
        "vocabulary": get_vocabulary(session, version_id),
    }


def node(code: str, title: str | None = None, **extra: Any) -> dict[str, Any]:
    return {"code": code, "title": title or f"Title of {code}", **extra}


def default_nodes() -> list[dict[str, Any]]:
    return [
        node("X"),
        node("X.1", parent="X", attributes={"level": "core"}),
        node("X.2", parent="X"),
    ]


def make_reference(
    *,
    program: str = "demo",
    program_name: str = "Demo programme",
    subject: str = "sub",
    subject_name: str = "Demo subject",
    version: str = "v1",
    version_title: str = "Version one",
    nodes: list[dict[str, Any]] | None = None,
    format_code: str = "main",
    sections: list[tuple[str, str]] | None = None,
    command_terms: list[str] | None = None,
) -> SyllabusReference:
    return SyllabusReference.model_validate(
        {
            "status": "synthetic test data",
            "program": {"code": program, "name": program_name},
            "subject": {"code": subject, "name": subject_name},
            "syllabus_version": {"code": version, "title": version_title},
            "nodes": nodes if nodes is not None else default_nodes(),
            "exam_format": {
                "code": format_code,
                "sections": [
                    {"code": code, "title": title}
                    for code, title in (sections or [("s1", "Section one"), ("s2", "Section two")])
                ],
                "command_terms": command_terms or ["alpha", "beta"],
            },
        }
    )


def load_demo(session: Session, **kwargs: Any) -> uuid.UUID:
    return load_reference(session, make_reference(**kwargs))


def real_reference() -> SyllabusReference:
    return SyllabusReference.model_validate_json(REAL_FILE.read_bytes())


def leaf_codes(reference: SyllabusReference) -> frozenset[str]:
    parents = {n.parent for n in reference.nodes if n.parent is not None}
    return frozenset(n.code for n in reference.nodes if n.code not in parents)


# =============================================================================================
# The real reference file
# =============================================================================================


def test_loading_the_real_file_gives_a_findable_version(session: Session) -> None:
    version_id = load_reference(session, real_reference())

    assert isinstance(version_id, uuid.UUID)
    assert (
        find_syllabus_version(session, program="ib_dp", subject="physics", version="2025")
        == version_id
    )


def test_real_file_vocabulary_matches_the_file(session: Session) -> None:
    reference = real_reference()
    version_id = load_reference(session, reference)

    vocabulary = get_vocabulary(session, version_id)

    assert isinstance(vocabulary, Vocabulary)
    assert vocabulary.exam_sections == frozenset(s.code for s in reference.exam_format.sections)
    assert vocabulary.command_terms == frozenset(reference.exam_format.command_terms)
    assert vocabulary.node_codes == frozenset(n.code for n in reference.nodes)
    assert vocabulary.leaf_node_codes == leaf_codes(reference)
    assert vocabulary.leaf_node_codes < vocabulary.node_codes


def test_real_file_leaf_codes_are_the_nodes_without_children(session: Session) -> None:
    reference = real_reference()
    version_id = load_reference(session, reference)

    vocabulary = get_vocabulary(session, version_id)

    parents = {n.parent for n in reference.nodes if n.parent is not None}
    assert parents  # the real file has a tree, not a flat list
    assert vocabulary.leaf_node_codes.isdisjoint(parents)
    assert vocabulary.node_codes - vocabulary.leaf_node_codes == frozenset(parents)


def test_real_file_nodes_are_stored_as_listed(session: Session, connection: Connection) -> None:
    reference = real_reference()
    version_id = load_reference(session, reference)

    stored = read_nodes(connection, version_id)

    assert set(stored) == {n.code for n in reference.nodes}
    for index, entry in enumerate(reference.nodes):
        row = stored[entry.code]
        assert row.title == entry.title
        assert row.position == index
        assert row.parent == entry.parent
        assert row.attributes == entry.attributes


def test_real_file_creates_one_of_each_parent_row(session: Session, connection: Connection) -> None:
    before = counts(connection)
    reference = real_reference()

    load_reference(session, reference)

    after = counts(connection)
    assert after["program"] - before["program"] == 1
    assert after["subject"] - before["subject"] == 1
    assert after["syllabus_version"] - before["syllabus_version"] == 1
    assert after["exam_format"] - before["exam_format"] == 1
    assert after["syllabus_node"] - before["syllabus_node"] == len(reference.nodes)


def test_real_file_names_and_exam_format_are_stored(
    session: Session, connection: Connection
) -> None:
    reference = real_reference()
    version_id = load_reference(session, reference)

    names = read_names(connection, version_id)
    definition = read_exam_definition(connection, version_id)

    assert names == Names(
        program=reference.program.name,
        subject=reference.subject.name,
        version=reference.syllabus_version.title,
    )
    assert {s.code: s.title for s in definition.sections} == {
        s.code: s.title for s in reference.exam_format.sections
    }
    assert set(definition.command_terms) == set(reference.exam_format.command_terms)


def test_real_file_node_ids_map_every_code(session: Session) -> None:
    reference = real_reference()
    version_id = load_reference(session, reference)
    codes = frozenset(n.code for n in reference.nodes)

    mapping = node_ids(session, version_id, codes)

    assert set(mapping) == codes
    assert len(set(mapping.values())) == len(codes)


def test_real_file_loaded_twice_is_idempotent(session: Session, connection: Connection) -> None:
    reference = real_reference()
    first = load_reference(session, reference)
    codes = frozenset(n.code for n in reference.nodes)
    ids_before = node_ids(session, first, codes)
    state_before = snapshot(connection, session, first)

    second = load_reference(session, reference)

    assert second == first
    assert node_ids(session, second, codes) == ids_before
    assert snapshot(connection, session, second) == state_before


# =============================================================================================
# find_syllabus_version
# =============================================================================================


def test_find_returns_the_id_for_the_three_codes(session: Session) -> None:
    version_id = load_demo(session)

    assert find_syllabus_version(session, program="demo", subject="sub", version="v1") == version_id


def test_find_returns_none_on_an_empty_database(session: Session) -> None:
    assert find_syllabus_version(session, program="demo", subject="sub", version="v1") is None


@pytest.mark.parametrize(
    ("program", "subject", "version"),
    [
        ("other", "sub", "v1"),
        ("demo", "other", "v1"),
        ("demo", "sub", "other"),
        ("other", "other", "other"),
        ("DEMO", "sub", "v1"),
        ("demo", "SUB", "v1"),
        ("demo", "sub", "V1"),
        ("", "", ""),
        ("sub", "demo", "v1"),
        ("v1", "sub", "demo"),
    ],
)
def test_find_returns_none_unless_all_three_codes_match(
    session: Session, program: str, subject: str, version: str
) -> None:
    load_demo(session)

    assert find_syllabus_version(session, program=program, subject=subject, version=version) is None


# =============================================================================================
# get_vocabulary / node_ids
# =============================================================================================


def test_vocabulary_of_a_synthetic_version(session: Session) -> None:
    version_id = load_demo(
        session,
        nodes=[node("X"), node("X.1", parent="X"), node("X.2", parent="X"), node("Y")],
        sections=[("s1", "Section one"), ("s2", "Section two"), ("s3", "Section three")],
        command_terms=["alpha", "beta", "gamma"],
    )

    vocabulary = get_vocabulary(session, version_id)

    assert vocabulary == Vocabulary(
        exam_sections=frozenset({"s1", "s2", "s3"}),
        command_terms=frozenset({"alpha", "beta", "gamma"}),
        node_codes=frozenset({"X", "X.1", "X.2", "Y"}),
        leaf_node_codes=frozenset({"X.1", "X.2", "Y"}),
    )


def test_deeper_tree_has_only_the_deepest_nodes_as_leaves(session: Session) -> None:
    version_id = load_demo(
        session,
        nodes=[
            node("A"),
            node("A.1", parent="A"),
            node("A.1.1", parent="A.1"),
            node("A.2", parent="A"),
        ],
    )

    vocabulary = get_vocabulary(session, version_id)

    assert vocabulary.leaf_node_codes == frozenset({"A.1.1", "A.2"})
    assert vocabulary.node_codes == frozenset({"A", "A.1", "A.1.1", "A.2"})


def test_single_node_version_has_that_node_as_leaf(session: Session) -> None:
    version_id = load_demo(session, nodes=[node("X")])

    vocabulary = get_vocabulary(session, version_id)

    assert vocabulary.node_codes == frozenset({"X"})
    assert vocabulary.leaf_node_codes == frozenset({"X"})


def test_vocabulary_sets_are_frozensets(session: Session) -> None:
    vocabulary = get_vocabulary(session, load_demo(session))

    assert isinstance(vocabulary.exam_sections, frozenset)
    assert isinstance(vocabulary.command_terms, frozenset)
    assert isinstance(vocabulary.node_codes, frozenset)
    assert isinstance(vocabulary.leaf_node_codes, frozenset)


def test_get_vocabulary_unknown_version_raises_lookup_error(session: Session) -> None:
    with pytest.raises(LookupError):
        get_vocabulary(session, uuid.uuid4())


def test_get_vocabulary_unknown_version_raises_even_when_others_exist(session: Session) -> None:
    load_demo(session)

    with pytest.raises(LookupError):
        get_vocabulary(session, uuid.uuid4())


def test_get_vocabulary_for_a_version_without_exam_format_raises_lookup_error(
    session: Session, connection: Connection
) -> None:
    program_id, subject_id, version_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    connection.execute(
        text("INSERT INTO program (id, code, name) VALUES (:id, 'bare', 'Bare')"),
        {"id": program_id},
    )
    connection.execute(
        text("INSERT INTO subject (id, program_id, code, name) VALUES (:id, :p, 'bare', 'Bare')"),
        {"id": subject_id, "p": program_id},
    )
    connection.execute(
        text(
            "INSERT INTO syllabus_version (id, subject_id, code, title, status) "
            "VALUES (:id, :s, 'v0', 'Bare', 'draft')"
        ),
        {"id": version_id, "s": subject_id},
    )

    with pytest.raises(LookupError):
        get_vocabulary(session, version_id)


def test_node_ids_maps_codes_to_distinct_ids(session: Session, connection: Connection) -> None:
    version_id = load_demo(session)

    mapping = node_ids(session, version_id, frozenset({"X", "X.1", "X.2"}))

    assert set(mapping) == {"X", "X.1", "X.2"}
    assert len(set(mapping.values())) == 3
    stored = read_nodes(connection, version_id)
    assert {code: stored[code].id for code in mapping} == mapping


def test_node_ids_returns_only_the_requested_codes(session: Session) -> None:
    version_id = load_demo(session)

    mapping = node_ids(session, version_id, frozenset({"X.2"}))

    assert set(mapping) == {"X.2"}


def test_node_ids_of_no_codes_is_empty(session: Session) -> None:
    version_id = load_demo(session)

    assert node_ids(session, version_id, frozenset()) == {}


@pytest.mark.parametrize("unknown", ["Z", "x", "X.3", "X.1.1", "", "X.", "demo"])
def test_node_ids_unknown_code_raises_lookup_error(session: Session, unknown: str) -> None:
    version_id = load_demo(session)

    with pytest.raises(LookupError):
        node_ids(session, version_id, frozenset({unknown}))


def test_node_ids_one_unknown_code_among_known_ones_raises_lookup_error(
    session: Session,
) -> None:
    version_id = load_demo(session)

    with pytest.raises(LookupError):
        node_ids(session, version_id, frozenset({"X", "X.1", "nope"}))


def test_node_ids_unknown_version_raises_lookup_error(session: Session) -> None:
    load_demo(session)

    with pytest.raises(LookupError):
        node_ids(session, uuid.uuid4(), frozenset({"X"}))


# =============================================================================================
# Idempotency
# =============================================================================================


def test_second_load_returns_the_same_id_and_leaves_rows_unchanged(
    session: Session, connection: Connection
) -> None:
    reference = make_reference()
    first = load_reference(session, reference)
    codes = frozenset({"X", "X.1", "X.2"})
    ids_before = node_ids(session, first, codes)
    state_before = snapshot(connection, session, first)

    second = load_reference(session, reference)

    assert second == first
    assert node_ids(session, first, codes) == ids_before
    assert snapshot(connection, session, first) == state_before


def test_loading_equal_but_separately_built_references_is_idempotent(
    session: Session, connection: Connection
) -> None:
    first = load_demo(session)
    state = snapshot(connection, session, first)

    second = load_demo(session)

    assert second == first
    assert snapshot(connection, session, second) == state


def test_many_repeated_loads_never_add_rows(session: Session, connection: Connection) -> None:
    first = load_demo(session)
    expected = counts(connection)

    for _ in range(5):
        assert load_demo(session) == first

    assert counts(connection) == expected


def test_first_load_creates_the_expected_rows(session: Session, connection: Connection) -> None:
    before = counts(connection)

    load_demo(session)

    after = counts(connection)
    assert {table: after[table] - before[table] for table in after} == {
        "program": 1,
        "subject": 1,
        "syllabus_version": 1,
        "syllabus_node": 3,
        "exam_format": 1,
    }


def test_load_runs_inside_the_callers_transaction(session: Session, connection: Connection) -> None:
    before = counts(connection)

    savepoint = session.begin_nested()
    version_id = load_demo(session)
    assert find_syllabus_version(session, program="demo", subject="sub", version="v1") == version_id
    savepoint.rollback()

    assert find_syllabus_version(session, program="demo", subject="sub", version="v1") is None
    assert counts(connection) == before


def test_nodes_are_stored_with_positions_parents_and_attributes(
    session: Session, connection: Connection
) -> None:
    version_id = load_demo(
        session,
        nodes=[
            node("X", attributes={"a": "b"}),
            node("X.1", parent="X"),
            node("Y"),
            node("Y.1", parent="Y", attributes={"level": "core"}),
        ],
    )

    stored = read_nodes(connection, version_id)

    assert {code: row.position for code, row in stored.items()} == {
        "X": 0,
        "X.1": 1,
        "Y": 2,
        "Y.1": 3,
    }
    assert {code: row.parent for code, row in stored.items()} == {
        "X": None,
        "X.1": "X",
        "Y": None,
        "Y.1": "Y",
    }
    assert stored["X"].attributes == {"a": "b"}
    assert stored["X.1"].attributes == {}
    assert stored["Y.1"].attributes == {"level": "core"}
    assert stored["X"].title == "Title of X"


# =============================================================================================
# Updates
# =============================================================================================


def test_update_changes_programme_subject_and_version_names(
    session: Session, connection: Connection
) -> None:
    first = load_demo(session)

    second = load_demo(
        session,
        program_name="Renamed programme",
        subject_name="Renamed subject",
        version_title="Renamed version",
    )

    assert second == first
    assert read_names(connection, first) == Names(
        program="Renamed programme", subject="Renamed subject", version="Renamed version"
    )
    assert counts(connection)["program"] == 1


def test_update_changes_node_titles_and_keeps_ids(session: Session, connection: Connection) -> None:
    first = load_demo(session)
    ids_before = node_ids(session, first, frozenset({"X", "X.1", "X.2"}))

    nodes = default_nodes()
    nodes[0]["title"] = "New title of X"
    nodes[1]["title"] = "New title of X.1"
    load_demo(session, nodes=nodes)

    stored = read_nodes(connection, first)
    assert stored["X"].title == "New title of X"
    assert stored["X.1"].title == "New title of X.1"
    assert stored["X.2"].title == "Title of X.2"
    assert {code: row.id for code, row in stored.items()} == ids_before


def test_update_changes_positions_to_the_list_order(
    session: Session, connection: Connection
) -> None:
    first = load_demo(session)
    assert [read_nodes(connection, first)[c].position for c in ("X", "X.1", "X.2")] == [0, 1, 2]

    nodes = [
        node("X"),
        node("X.2", parent="X"),
        node("X.1", parent="X", attributes={"level": "core"}),
    ]
    load_demo(session, nodes=nodes)

    stored = read_nodes(connection, first)
    assert {code: row.position for code, row in stored.items()} == {"X": 0, "X.2": 1, "X.1": 2}


def test_update_changes_the_parent(session: Session, connection: Connection) -> None:
    first = load_demo(session)

    nodes = [node("X"), node("X.1", parent="X"), node("X.2", parent="X.1")]
    load_demo(session, nodes=nodes)

    stored = read_nodes(connection, first)
    assert stored["X.2"].parent == "X.1"
    assert stored["X.1"].parent == "X"
    vocabulary = get_vocabulary(session, first)
    assert vocabulary.leaf_node_codes == frozenset({"X.2"})


def test_update_can_move_a_node_to_the_top_level(session: Session, connection: Connection) -> None:
    first = load_demo(session)

    nodes = [node("X"), node("X.1", parent="X"), node("X.2")]
    load_demo(session, nodes=nodes)

    assert read_nodes(connection, first)["X.2"].parent is None
    assert get_vocabulary(session, first).leaf_node_codes == frozenset({"X.1", "X.2"})


def test_update_changes_attributes(session: Session, connection: Connection) -> None:
    first = load_demo(session)

    nodes = [
        node("X", attributes={"new": "yes"}),
        node("X.1", parent="X", attributes={"level": "extension", "extra": "one"}),
        node("X.2", parent="X"),
    ]
    load_demo(session, nodes=nodes)

    stored = read_nodes(connection, first)
    assert stored["X"].attributes == {"new": "yes"}
    assert stored["X.1"].attributes == {"level": "extension", "extra": "one"}
    assert stored["X.2"].attributes == {}


def test_update_removing_attributes_from_the_file_empties_them(
    session: Session, connection: Connection
) -> None:
    first = load_demo(session)
    assert read_nodes(connection, first)["X.1"].attributes == {"level": "core"}

    nodes = [node("X"), node("X.1", parent="X"), node("X.2", parent="X")]
    load_demo(session, nodes=nodes)

    assert read_nodes(connection, first)["X.1"].attributes == {}


def test_update_adds_new_nodes_and_keeps_existing_ids(
    session: Session, connection: Connection
) -> None:
    first = load_demo(session)
    ids_before = node_ids(session, first, frozenset({"X", "X.1", "X.2"}))
    before = counts(connection)

    nodes = [*default_nodes(), node("X.3", parent="X"), node("Y"), node("Y.1", parent="Y")]
    second = load_demo(session, nodes=nodes)

    assert second == first
    assert counts(connection)["syllabus_node"] == before["syllabus_node"] + 3
    mapping = node_ids(session, first, frozenset({"X", "X.1", "X.2", "X.3", "Y", "Y.1"}))
    assert {code: mapping[code] for code in ids_before} == ids_before
    assert len(set(mapping.values())) == 6
    stored = read_nodes(connection, first)
    assert stored["X.3"].parent == "X"
    assert stored["Y.1"].parent == "Y"
    assert get_vocabulary(session, first).node_codes == frozenset(mapping)


def test_update_inserting_a_node_in_the_middle_shifts_positions(
    session: Session, connection: Connection
) -> None:
    first = load_demo(session)

    nodes = [node("X"), node("X.0", parent="X"), node("X.1", parent="X"), node("X.2", parent="X")]
    load_demo(session, nodes=nodes)

    stored = read_nodes(connection, first)
    assert {code: row.position for code, row in stored.items()} == {
        "X": 0,
        "X.0": 1,
        "X.1": 2,
        "X.2": 3,
    }


def test_update_adds_a_command_term_and_a_section(session: Session, connection: Connection) -> None:
    first = load_demo(session)

    load_demo(
        session,
        sections=[("s1", "Section one"), ("s2", "Section two"), ("s3", "Section three")],
        command_terms=["alpha", "beta", "gamma"],
    )

    vocabulary = get_vocabulary(session, first)
    assert vocabulary.exam_sections == frozenset({"s1", "s2", "s3"})
    assert vocabulary.command_terms == frozenset({"alpha", "beta", "gamma"})
    definition = read_exam_definition(connection, first)
    assert {s.code: s.title for s in definition.sections}["s3"] == "Section three"
    assert counts(connection)["exam_format"] == 1


def test_update_changes_a_section_title(session: Session, connection: Connection) -> None:
    first = load_demo(session)

    load_demo(session, sections=[("s1", "Renamed section"), ("s2", "Section two")])

    definition = read_exam_definition(connection, first)
    assert {s.code: s.title for s in definition.sections} == {
        "s1": "Renamed section",
        "s2": "Section two",
    }
    assert get_vocabulary(session, first).exam_sections == frozenset({"s1", "s2"})


def test_update_keeps_the_exam_format_row(session: Session, connection: Connection) -> None:
    first = load_demo(session)
    format_id = connection.execute(text("SELECT id FROM exam_format")).scalar_one()

    load_demo(session, command_terms=["alpha", "beta", "delta"])

    assert connection.execute(text("SELECT id FROM exam_format")).scalar_one() == format_id
    assert get_vocabulary(session, first).command_terms == {"alpha", "beta", "delta"}


def test_update_applies_everything_at_once(session: Session, connection: Connection) -> None:
    first = load_demo(session)

    nodes = [
        node("X", "Changed X", attributes={"k": "v"}),
        node("X.2", "Changed X.2", parent="X"),
        node("X.1", "Changed X.1", parent="X.2"),
        node("Z", "Brand new"),
    ]
    second = load_demo(
        session,
        version_title="Changed version",
        nodes=nodes,
        sections=[("s1", "One"), ("s2", "Two"), ("s9", "Nine")],
        command_terms=["alpha", "beta", "omega"],
    )

    assert second == first
    stored = read_nodes(connection, first)
    assert {code: (row.title, row.position, row.parent) for code, row in stored.items()} == {
        "X": ("Changed X", 0, None),
        "X.2": ("Changed X.2", 1, "X"),
        "X.1": ("Changed X.1", 2, "X.2"),
        "Z": ("Brand new", 3, None),
    }
    assert stored["X"].attributes == {"k": "v"}
    assert stored["X.1"].attributes == {}
    assert read_names(connection, first).version == "Changed version"
    vocabulary = get_vocabulary(session, first)
    assert vocabulary.exam_sections == frozenset({"s1", "s2", "s9"})
    assert vocabulary.command_terms == frozenset({"alpha", "beta", "omega"})


# =============================================================================================
# Conflicts: nothing is ever deleted
# =============================================================================================


def _drop_leaf() -> dict[str, Any]:
    return {"nodes": [node("X"), node("X.1", parent="X", attributes={"level": "core"})]}


def _drop_inner_node_and_its_children() -> dict[str, Any]:
    return {"nodes": [node("Q")]}


def _drop_first_node_only() -> dict[str, Any]:
    return {"nodes": [node("X.1"), node("X.2")]}


def _rename_a_node() -> dict[str, Any]:
    return {"nodes": [node("X"), node("X.1", parent="X"), node("X.9", parent="X")]}


def _drop_a_section() -> dict[str, Any]:
    return {"sections": [("s1", "Section one")]}


def _replace_a_section() -> dict[str, Any]:
    return {"sections": [("s1", "Section one"), ("s3", "Section three")]}


def _drop_a_command_term() -> dict[str, Any]:
    return {"command_terms": ["alpha"]}


def _replace_a_command_term() -> dict[str, Any]:
    return {"command_terms": ["alpha", "gamma"]}


def _drop_node_and_a_term_and_a_section() -> dict[str, Any]:
    return {**_drop_leaf(), **_drop_a_section(), **_drop_a_command_term()}


CONFLICTS = {
    "drop_a_node": _drop_leaf,
    "drop_inner_node_and_children": _drop_inner_node_and_its_children,
    "drop_first_node": _drop_first_node_only,
    "rename_a_node": _rename_a_node,
    "drop_a_section": _drop_a_section,
    "replace_a_section": _replace_a_section,
    "drop_a_command_term": _drop_a_command_term,
    "replace_a_command_term": _replace_a_command_term,
    "drop_all_three": _drop_node_and_a_term_and_a_section,
}


@pytest.mark.parametrize("changes", CONFLICTS.values(), ids=CONFLICTS.keys())
def test_a_file_that_drops_something_raises_conflict_and_changes_nothing(
    session: Session, connection: Connection, changes: Callable[[], dict[str, Any]]
) -> None:
    first = load_demo(session)
    before = snapshot(connection, session, first)

    # The conflicting file also contains harmless edits; none of them may be applied.
    with pytest.raises(ReferenceConflict):
        load_reference(
            session,
            make_reference(
                program_name="Edited programme",
                subject_name="Edited subject",
                version_title="Edited version",
                **changes(),
            ),
        )

    assert snapshot(connection, session, first) == before


@pytest.mark.parametrize("changes", CONFLICTS.values(), ids=CONFLICTS.keys())
def test_after_a_conflict_the_original_file_still_loads_unchanged(
    session: Session, connection: Connection, changes: Callable[[], dict[str, Any]]
) -> None:
    first = load_demo(session)
    before = snapshot(connection, session, first)
    with pytest.raises(ReferenceConflict):
        load_reference(session, make_reference(**changes()))

    again = load_demo(session)

    assert again == first
    assert snapshot(connection, session, again) == before


def test_conflict_with_edited_titles_and_a_dropped_node_applies_no_title(
    session: Session, connection: Connection
) -> None:
    first = load_demo(session)
    nodes = [node("X", "Edited X"), node("X.1", "Edited X.1", parent="X")]  # X.2 dropped

    with pytest.raises(ReferenceConflict):
        load_demo(session, nodes=nodes)

    stored = read_nodes(connection, first)
    assert stored["X"].title == "Title of X"
    assert stored["X.1"].title == "Title of X.1"
    assert set(stored) == {"X", "X.1", "X.2"}


def test_conflict_is_a_plain_exception_type() -> None:
    assert issubclass(ReferenceConflict, Exception)


def test_dropping_something_in_another_version_is_not_a_conflict(
    session: Session, connection: Connection
) -> None:
    v1 = load_demo(session, version="v1")
    v2 = load_demo(session, version="v2", nodes=[node("X"), node("X.1", parent="X")])

    assert v1 != v2
    assert get_vocabulary(session, v1).node_codes == frozenset({"X", "X.1", "X.2"})
    assert get_vocabulary(session, v2).node_codes == frozenset({"X", "X.1"})


def test_a_new_version_never_conflicts_on_first_load(session: Session) -> None:
    load_demo(session)

    other = load_demo(
        session,
        version="v2",
        nodes=[node("Q")],
        sections=[("only", "Only")],
        command_terms=["omega"],
    )

    assert other == find_syllabus_version(session, program="demo", subject="sub", version="v2")


# =============================================================================================
# Coexisting versions
# =============================================================================================


def test_two_versions_of_the_same_subject_coexist_without_sharing_nodes(
    session: Session, connection: Connection
) -> None:
    v1 = load_demo(session, version="v1", version_title="One")
    v2 = load_demo(
        session,
        version="v2",
        version_title="Two",
        nodes=[node("X", "Two X"), node("X.1", "Two X.1", parent="X"), node("W")],
        sections=[("s1", "Section one"), ("t1", "Other")],
        command_terms=["alpha", "zeta"],
    )

    assert v1 != v2
    assert find_syllabus_version(session, program="demo", subject="sub", version="v1") == v1
    assert find_syllabus_version(session, program="demo", subject="sub", version="v2") == v2

    ids_1 = node_ids(session, v1, frozenset({"X", "X.1"}))
    ids_2 = node_ids(session, v2, frozenset({"X", "X.1"}))
    assert set(ids_1.values()).isdisjoint(ids_2.values())

    vocabulary_1 = get_vocabulary(session, v1)
    vocabulary_2 = get_vocabulary(session, v2)
    assert vocabulary_1.node_codes == frozenset({"X", "X.1", "X.2"})
    assert vocabulary_2.node_codes == frozenset({"X", "X.1", "W"})
    assert vocabulary_1.exam_sections == frozenset({"s1", "s2"})
    assert vocabulary_2.exam_sections == frozenset({"s1", "t1"})
    assert vocabulary_1.command_terms == frozenset({"alpha", "beta"})
    assert vocabulary_2.command_terms == frozenset({"alpha", "zeta"})

    assert read_nodes(connection, v1)["X"].title == "Title of X"
    assert read_nodes(connection, v2)["X"].title == "Two X"
    assert read_names(connection, v1).version == "One"
    assert read_names(connection, v2).version == "Two"


def test_node_ids_do_not_cross_versions(session: Session) -> None:
    v1 = load_demo(session, version="v1")
    v2 = load_demo(session, version="v2", nodes=[node("X"), node("W")])

    with pytest.raises(LookupError):
        node_ids(session, v2, frozenset({"X.1"}))  # exists only in v1
    with pytest.raises(LookupError):
        node_ids(session, v1, frozenset({"W"}))  # exists only in v2


def test_second_version_shares_the_programme_and_subject_rows(
    session: Session, connection: Connection
) -> None:
    load_demo(session, version="v1")
    before = counts(connection)

    load_demo(session, version="v2")

    after = counts(connection)
    assert after["program"] == before["program"]
    assert after["subject"] == before["subject"]
    assert after["syllabus_version"] == before["syllabus_version"] + 1
    assert after["syllabus_node"] == before["syllabus_node"] + 3
    assert after["exam_format"] == before["exam_format"] + 1


def test_loading_the_second_version_leaves_the_first_untouched(
    session: Session, connection: Connection
) -> None:
    v1 = load_demo(session, version="v1")
    before = {k: v for k, v in snapshot(connection, session, v1).items() if k != "counts"}

    load_demo(session, version="v2", nodes=[node("X", "other"), node("Q")])

    after = {k: v for k, v in snapshot(connection, session, v1).items() if k != "counts"}
    assert after == before


def test_updating_one_version_does_not_touch_the_other(
    session: Session, connection: Connection
) -> None:
    v1 = load_demo(session, version="v1")
    v2 = load_demo(session, version="v2")
    before_v2 = {k: v for k, v in snapshot(connection, session, v2).items() if k != "counts"}

    nodes = [node("X", "Edited"), node("X.1", parent="X"), node("X.2", parent="X"), node("N")]
    load_demo(session, version="v1", nodes=nodes, command_terms=["alpha", "beta", "new"])

    assert read_nodes(connection, v1)["X"].title == "Edited"
    after_v2 = {k: v for k, v in snapshot(connection, session, v2).items() if k != "counts"}
    assert after_v2 == before_v2


def test_same_version_code_under_different_subjects_is_a_different_version(
    session: Session, connection: Connection
) -> None:
    a = load_demo(session, subject="sub_a", subject_name="Subject A")
    b = load_demo(session, subject="sub_b", subject_name="Subject B")

    assert a != b
    assert find_syllabus_version(session, program="demo", subject="sub_a", version="v1") == a
    assert find_syllabus_version(session, program="demo", subject="sub_b", version="v1") == b
    counts_now = counts(connection)
    assert counts_now["program"] == 1
    assert counts_now["subject"] == 2
    assert not set(node_ids(session, a, frozenset({"X"})).values()) & set(
        node_ids(session, b, frozenset({"X"})).values()
    )


def test_same_subject_and_version_codes_under_different_programmes_do_not_collide(
    session: Session,
) -> None:
    a = load_demo(session, program="prog_a", program_name="Programme A")
    b = load_demo(session, program="prog_b", program_name="Programme B")

    assert a != b
    assert find_syllabus_version(session, program="prog_a", subject="sub", version="v1") == a
    assert find_syllabus_version(session, program="prog_b", subject="sub", version="v1") == b


def test_real_file_and_a_synthetic_version_coexist(session: Session) -> None:
    real = load_reference(session, real_reference())
    demo = load_demo(session)

    assert real != demo
    assert get_vocabulary(session, demo).node_codes == frozenset({"X", "X.1", "X.2"})
    assert "X" not in get_vocabulary(session, real).node_codes
