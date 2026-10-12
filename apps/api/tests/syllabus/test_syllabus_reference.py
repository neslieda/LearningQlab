"""Shape of a syllabus reference file: pure Pydantic validation, no database."""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from qlab.syllabus.reference import ExamFormatDefinition, SyllabusReference
from tests.conftest import REPO_ROOT

REAL_FILE = REPO_ROOT / "content" / "reference" / "dp-physics-2025-syllabus.json"


def valid_data() -> dict[str, Any]:
    """A small synthetic reference; every test starts from a fresh copy."""
    return {
        "status": "synthetic test data",
        "program": {"code": "demo", "name": "Demo programme"},
        "subject": {"code": "sub", "name": "Demo subject"},
        "syllabus_version": {"code": "v1", "title": "Version one"},
        "nodes": [
            {"code": "X", "title": "Topic X"},
            {"code": "X.1", "title": "Subtopic", "parent": "X", "attributes": {"level": "core"}},
            {"code": "X.2", "title": "Another", "parent": "X"},
            {"code": "Y", "title": "Topic Y"},
        ],
        "exam_format": {
            "code": "main",
            "sections": [
                {"code": "s1", "title": "Section one"},
                {"code": "s2", "title": "Section two"},
            ],
            "command_terms": ["alpha", "beta"],
        },
    }


def _assign(target: object, name: str, value: object) -> None:
    setattr(target, name, value)


def validate(data: dict[str, Any]) -> SyllabusReference:
    return SyllabusReference.model_validate(data)


# --- valid inputs ---------------------------------------------------------------------------


def test_the_real_reference_file_validates() -> None:
    reference = SyllabusReference.model_validate_json(REAL_FILE.read_bytes())

    assert reference.program.code == "ib_dp"
    assert reference.subject.code == "physics"
    assert reference.syllabus_version.code == "2025"
    assert len(reference.nodes) > 1


def test_the_real_reference_file_validates_from_parsed_json() -> None:
    reference = SyllabusReference.model_validate(json.loads(REAL_FILE.read_text("utf-8")))

    assert reference.exam_format.sections
    assert reference.exam_format.command_terms


def test_a_small_synthetic_reference_validates() -> None:
    reference = validate(valid_data())

    assert [n.code for n in reference.nodes] == ["X", "X.1", "X.2", "Y"]
    assert reference.nodes[1].parent == "X"
    assert reference.nodes[1].attributes == {"level": "core"}
    assert reference.exam_format.code == "main"
    assert reference.exam_format.command_terms == ("alpha", "beta")


def test_node_defaults_are_no_parent_and_empty_attributes() -> None:
    node = validate(valid_data()).nodes[0]

    assert node.parent is None
    assert node.attributes == {}


def test_single_node_reference_validates() -> None:
    data = valid_data()
    data["nodes"] = [{"code": "X", "title": "Only"}]

    assert len(validate(data).nodes) == 1


def test_deep_tree_validates() -> None:
    data = valid_data()
    data["nodes"] = [
        {"code": "A", "title": "a"},
        {"code": "A.1", "title": "b", "parent": "A"},
        {"code": "A.1.1", "title": "c", "parent": "A.1"},
        {"code": "A.1.1.1", "title": "d", "parent": "A.1.1"},
    ]

    assert len(validate(data).nodes) == 4


def test_children_may_be_listed_apart_from_their_parent() -> None:
    data = valid_data()
    data["nodes"] = [
        {"code": "A", "title": "a"},
        {"code": "B", "title": "b"},
        {"code": "A.1", "title": "c", "parent": "A"},
        {"code": "B.1", "title": "d", "parent": "B"},
    ]

    assert len(validate(data).nodes) == 4


def test_attributes_may_hold_arbitrary_json() -> None:
    data = valid_data()
    data["nodes"][0]["attributes"] = {"a": [1, {"b": None}], "c": "d", "e": 1.5, "f": True}

    assert validate(data).nodes[0].attributes["a"] == [1, {"b": None}]


def test_validated_reference_round_trips_through_json() -> None:
    reference = validate(valid_data())

    again = SyllabusReference.model_validate_json(reference.model_dump_json())

    assert again == reference


def test_reference_is_immutable() -> None:
    reference = validate(valid_data())

    with pytest.raises(ValidationError):
        _assign(reference, "status", "changed")


def test_exam_format_definition_accepts_sections_and_terms_only() -> None:
    definition = ExamFormatDefinition.model_validate(
        {"sections": [{"code": "s1", "title": "One"}], "command_terms": ["alpha"]}
    )

    assert definition.sections[0].code == "s1"
    assert definition.command_terms == ("alpha",)


# --- unknown fields are rejected at every level ---------------------------------------------


def _top(data: dict[str, Any]) -> dict[str, Any]:
    return data


def _program(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = data["program"]
    return result


def _subject(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = data["subject"]
    return result


def _version(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = data["syllabus_version"]
    return result


def _node(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = data["nodes"][1]
    return result


def _exam_format(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = data["exam_format"]
    return result


def _section(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = data["exam_format"]["sections"][0]
    return result


LEVELS = {
    "top": _top,
    "program": _program,
    "subject": _subject,
    "syllabus_version": _version,
    "node": _node,
    "exam_format": _exam_format,
    "section": _section,
}


@pytest.mark.parametrize("level", LEVELS.values(), ids=LEVELS.keys())
def test_unknown_field_is_rejected(level: Any) -> None:
    data = valid_data()
    level(data)["surprise"] = "value"

    with pytest.raises(ValidationError, match="surprise"):
        validate(data)


def test_unknown_field_inside_node_attributes_is_allowed() -> None:
    data = valid_data()
    data["nodes"][1]["attributes"]["anything"] = "goes"

    assert validate(data).nodes[1].attributes["anything"] == "goes"


def test_unknown_field_in_exam_format_definition_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ExamFormatDefinition.model_validate(
            {"sections": [{"code": "s1", "title": "One"}], "command_terms": ["a"], "extra": 1}
        )


# --- required fields ------------------------------------------------------------------------


@pytest.mark.parametrize(
    "missing",
    ["status", "program", "subject", "syllabus_version", "nodes", "exam_format"],
)
def test_missing_top_level_field_is_rejected(missing: str) -> None:
    data = valid_data()
    del data[missing]

    with pytest.raises(ValidationError):
        validate(data)


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("program", "code"),
        ("program", "name"),
        ("subject", "code"),
        ("subject", "name"),
        ("syllabus_version", "code"),
        ("syllabus_version", "title"),
        ("exam_format", "code"),
        ("exam_format", "sections"),
        ("exam_format", "command_terms"),
    ],
)
def test_missing_nested_field_is_rejected(section: str, field: str) -> None:
    data = valid_data()
    del data[section][field]

    with pytest.raises(ValidationError):
        validate(data)


@pytest.mark.parametrize("field", ["code", "title"])
def test_node_without_code_or_title_is_rejected(field: str) -> None:
    data = valid_data()
    del data["nodes"][0][field]

    with pytest.raises(ValidationError):
        validate(data)


# --- structural rules -----------------------------------------------------------------------


def test_empty_nodes_are_rejected() -> None:
    data = valid_data()
    data["nodes"] = []

    with pytest.raises(ValidationError):
        validate(data)


def test_duplicate_node_code_is_rejected() -> None:
    data = valid_data()
    data["nodes"].append({"code": "X.1", "title": "Again", "parent": "X"})

    with pytest.raises(ValidationError, match=r"duplicate node code X\.1"):
        validate(data)


def test_duplicate_top_level_node_code_is_rejected() -> None:
    data = valid_data()
    data["nodes"].append({"code": "X", "title": "Again"})

    with pytest.raises(ValidationError, match="duplicate node code X"):
        validate(data)


def test_parent_listed_after_child_is_rejected() -> None:
    data = valid_data()
    data["nodes"] = [
        {"code": "X.1", "title": "Child", "parent": "X"},
        {"code": "X", "title": "Parent"},
    ]

    with pytest.raises(ValidationError, match="parent X is not listed before"):
        validate(data)


def test_missing_parent_is_rejected() -> None:
    data = valid_data()
    data["nodes"].append({"code": "Z.1", "title": "Orphan", "parent": "Z"})

    with pytest.raises(ValidationError, match="parent Z is not listed before"):
        validate(data)


def test_node_that_is_its_own_parent_is_rejected() -> None:
    data = valid_data()
    data["nodes"] = [{"code": "X", "title": "Loop", "parent": "X"}]

    with pytest.raises(ValidationError):
        validate(data)


def test_first_node_with_a_parent_is_rejected() -> None:
    data = valid_data()
    data["nodes"] = [{"code": "X.1", "title": "Child", "parent": "X"}]

    with pytest.raises(ValidationError):
        validate(data)


def test_duplicate_exam_section_is_rejected() -> None:
    data = valid_data()
    data["exam_format"]["sections"].append({"code": "s1", "title": "Different title"})

    with pytest.raises(ValidationError, match="duplicate exam section code"):
        validate(data)


def test_duplicate_command_term_is_rejected() -> None:
    data = valid_data()
    data["exam_format"]["command_terms"].append("alpha")

    with pytest.raises(ValidationError, match="duplicate command term"):
        validate(data)


def test_empty_sections_are_rejected() -> None:
    data = valid_data()
    data["exam_format"]["sections"] = []

    with pytest.raises(ValidationError):
        validate(data)


def test_empty_command_terms_are_rejected() -> None:
    data = valid_data()
    data["exam_format"]["command_terms"] = []

    with pytest.raises(ValidationError):
        validate(data)


def test_exam_format_definition_checks_duplicates_on_its_own() -> None:
    with pytest.raises(ValidationError):
        ExamFormatDefinition.model_validate(
            {
                "sections": [{"code": "s1", "title": "a"}, {"code": "s1", "title": "b"}],
                "command_terms": ["alpha"],
            }
        )
    with pytest.raises(ValidationError):
        ExamFormatDefinition.model_validate(
            {"sections": [{"code": "s1", "title": "a"}], "command_terms": ["alpha", "alpha"]}
        )


# --- field formats --------------------------------------------------------------------------


@pytest.mark.parametrize("bad", ["", "  ", "\t\n"])
@pytest.mark.parametrize(
    "path",
    [
        ("status",),
        ("program", "name"),
        ("subject", "name"),
        ("syllabus_version", "title"),
        ("nodes", 0, "title"),
        ("exam_format", "sections", 0, "title"),
    ],
    ids=lambda path: ".".join(str(p) for p in path),
)
def test_blank_text_fields_are_rejected(path: tuple[str | int, ...], bad: str) -> None:
    data = valid_data()
    target: Any = data
    for step in path[:-1]:
        target = target[step]
    target[path[-1]] = bad

    with pytest.raises(ValidationError):
        validate(data)


@pytest.mark.parametrize("bad", ["", "Ib", "ib dp", "ib-dp", "_ib", "ib.dp", "ıb"])
@pytest.mark.parametrize(
    "path",
    [
        ("program", "code"),
        ("subject", "code"),
        ("syllabus_version", "code"),
        ("exam_format", "code"),
        ("exam_format", "sections", 0, "code"),
    ],
    ids=lambda path: ".".join(str(p) for p in path),
)
def test_malformed_codes_are_rejected(path: tuple[str | int, ...], bad: str) -> None:
    data = valid_data()
    target: Any = data
    for step in path[:-1]:
        target = target[step]
    target[path[-1]] = bad

    with pytest.raises(ValidationError):
        validate(data)


@pytest.mark.parametrize("good", ["a", "0", "2025", "ib_dp", "a1_b2", "9_9"])
def test_well_formed_codes_are_accepted(good: str) -> None:
    data = valid_data()
    data["program"]["code"] = good
    data["subject"]["code"] = good
    data["syllabus_version"]["code"] = good

    assert validate(data).program.code == good


@pytest.mark.parametrize("bad", ["Alpha", "two words", "a-b", "", "_a"])
def test_malformed_command_term_is_rejected(bad: str) -> None:
    data = valid_data()
    data["exam_format"]["command_terms"] = [bad]

    with pytest.raises(ValidationError):
        validate(data)


@pytest.mark.parametrize("bad", ["", "A.", ".A", "A..1", "A.1.", "A 1", "A-1", "A_1", "A.1 ", "é"])
def test_malformed_node_codes_are_rejected(bad: str) -> None:
    data = valid_data()
    data["nodes"] = [{"code": bad, "title": "t"}]

    with pytest.raises(ValidationError):
        validate(data)


@pytest.mark.parametrize("good", ["A", "a", "7", "A.1", "A.1.2", "B12.3c", "aB.Cd"])
def test_well_formed_node_codes_are_accepted(good: str) -> None:
    data = valid_data()
    data["nodes"] = [{"code": good, "title": "t"}]

    assert validate(data).nodes[0].code == good


def test_malformed_parent_code_is_rejected() -> None:
    data = valid_data()
    data["nodes"][1]["parent"] = "X..1"

    with pytest.raises(ValidationError):
        validate(data)


def test_node_codes_are_case_sensitive() -> None:
    data = valid_data()
    data["nodes"] = [
        {"code": "A", "title": "upper"},
        {"code": "a", "title": "lower"},
        {"code": "a.1", "title": "child of lower", "parent": "a"},
    ]

    assert len(validate(data).nodes) == 3


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("nodes",), "X"),
        (("program",), "demo"),
        (("nodes", 0, "attributes"), ["not", "a", "mapping"]),
        (("exam_format", "command_terms"), "alpha"),
        (("exam_format", "sections"), ["s1"]),
        (("exam_format", "sections", 0, "code"), 7),
        (("status",), 5),
    ],
    ids=lambda value: ".".join(str(p) for p in value) if isinstance(value, tuple) else "value",
)
def test_wrong_types_are_rejected(path: tuple[str | int, ...], value: Any) -> None:
    data = valid_data()
    target: Any = data
    for step in path[:-1]:
        target = target[step]
    target[path[-1]] = value

    with pytest.raises(ValidationError):
        validate(data)
