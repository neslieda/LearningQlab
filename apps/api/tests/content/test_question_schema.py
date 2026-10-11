"""Acceptance suite for question schema v1.

Written from the specification only: docs/DATA_ARCHITECTURE.md section 3.5. The sections below
follow the headings of that section. Every rejection test starts from a document that is first
shown to validate, changes one thing, and checks that the error names the intended rule.
All question content here is synthetic.
"""

import json
import re
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from pydantic import ValidationError

from qlab.content.schema import Doc, QuestionDocument
from tests.content.samples import (
    Json,
    bullet_list,
    cell,
    data_based_document,
    doc,
    figure,
    figure_options_mcq_document,
    gallery_document,
    grid,
    hard_break,
    line,
    list_item,
    mark_point,
    math,
    math_block,
    mcq_document,
    measured,
    ordered_list,
    paragraph,
    part,
    plain_mcq_document,
    quantity,
    question,
    roman_mcq_document,
    row,
    show_that_document,
    stimulus,
    structured_document,
    text,
    two_column_mcq_document,
    with_marks,
)

Base = Callable[[], Json]
Mutation = Callable[[Json], None]
Key = str | int

ALL_SAMPLES: list[Base] = [
    mcq_document,
    plain_mcq_document,
    two_column_mcq_document,
    roman_mcq_document,
    figure_options_mcq_document,
    structured_document,
    data_based_document,
    show_that_document,
    gallery_document,
]


# --- Helpers -----------------------------------------------------------------------------------


def _at(data: Any, path: Sequence[Key]) -> Any:
    for key in path:
        data = data[key]
    return data


def put(*path: Key, value: Any) -> Mutation:
    """Set (or add) the value at `path`."""

    def mutate(data: Json) -> None:
        _at(data, path[:-1])[path[-1]] = value

    return mutate


def drop(*path: Key) -> Mutation:
    def mutate(data: Json) -> None:
        del _at(data, path[:-1])[path[-1]]

    return mutate


def add(*path: Key, value: Any) -> Mutation:
    """Append to the list at `path`."""

    def mutate(data: Json) -> None:
        _at(data, path).append(value)

    return mutate


def cut(*path: Key) -> Mutation:
    """Remove the last item of the list at `path`."""

    def mutate(data: Json) -> None:
        _at(data, path).pop()

    return mutate


def both(*mutations: Mutation) -> Mutation:
    def mutate(data: Json) -> None:
        for mutation in mutations:
            mutation(data)

    return mutate


def validate(data: Json) -> QuestionDocument:
    return QuestionDocument.model_validate(data)


def dump(document: QuestionDocument) -> Json:
    dumped: Json = document.model_dump(mode="json")
    return dumped


def error_lines(error: ValidationError) -> list[str]:
    """One line per error: `<type> @ <dotted location>: <message>`."""
    return [
        f"{e['type']} @ {'.'.join(str(key) for key in e['loc'])}: {e['msg']}"
        for e in error.errors()
    ]


def accepts(base: Base, mutate: Mutation) -> QuestionDocument:
    data = base()
    mutate(data)
    assert data != base(), "the mutation changed nothing"
    return validate(data)


def rejects(base: Base, mutate: Mutation, match: str) -> None:
    """The base validates; with one change it fails, and an error line matches `match`."""
    validate(base())
    data = base()
    mutate(data)
    assert data != base(), "the mutation changed nothing"
    with pytest.raises(ValidationError) as caught:
        validate(data)
    lines = error_lines(caught.value)
    assert any(re.search(match, entry) for entry in lines), lines


@dataclass(frozen=True)
class Reject:
    label: str
    base: Base
    mutate: Mutation
    match: str


@dataclass(frozen=True)
class Accept:
    label: str
    base: Base
    mutate: Mutation


def rejected(*items: Reject) -> pytest.MarkDecorator:
    return pytest.mark.parametrize("case", items, ids=[item.label for item in items])


def accepted(*items: Accept) -> pytest.MarkDecorator:
    return pytest.mark.parametrize("case", items, ids=[item.label for item in items])


def permitted_values(base: Base, *path: Key) -> list[str]:
    """The values the schema lists as permitted when an enumerated field holds a wrong one."""
    data = base()
    put(*path, value="no_such_value")(data)
    with pytest.raises(ValidationError) as caught:
        validate(data)
    where = tuple(path)
    messages = [
        e["msg"]
        for e in caught.value.errors()
        if e["type"] in {"enum", "literal_error"} and e["loc"][-1] == where[-1]
    ]
    assert len(messages) == 1, error_lines(caught.value)
    return re.findall(r"'([^']+)'", messages[0])


def assert_contains(expected: Any, actual: Any, where: str = "$") -> None:
    """Everything given as input is present, unchanged, in the serialised form."""
    if isinstance(expected, dict):
        assert isinstance(actual, dict), where
        for key, value in expected.items():
            assert key in actual, f"{where}.{key} is missing"
            assert_contains(value, actual[key], f"{where}.{key}")
    elif isinstance(expected, list):
        assert isinstance(actual, list), where
        assert len(actual) == len(expected), where
        for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
            assert_contains(left, right, f"{where}[{index}]")
    else:
        assert actual == expected, where


def reorder_keys(data: Any) -> Any:
    """The same JSON value with every object's keys in reverse order."""
    if isinstance(data, dict):
        return {key: reorder_keys(data[key]) for key in reversed(list(data))}
    if isinstance(data, list):
        return [reorder_keys(item) for item in data]
    return data


def nodes_of(data: Any) -> Iterator[Json]:
    """Every node and mark in a serialised document: items of `content` and `marks` arrays."""
    if isinstance(data, dict):
        if isinstance(data.get("content"), list):
            yield data
        for key, value in data.items():
            if key == "marks" and isinstance(value, list):
                yield from (mark for mark in value)
            if key == "content" and isinstance(value, list):
                yield from (child for child in value if "content" not in child)
            yield from nodes_of(value)
    elif isinstance(data, list):
        for item in data:
            yield from nodes_of(item)


# Paths into gallery_document(); see its docstring for the layout.
PARA: tuple[Key, ...] = ("stem", "content", 0)
MATH_BLOCK: tuple[Key, ...] = ("stem", "content", 1)
TABLE: tuple[Key, ...] = ("stem", "content", 2)
BULLETS: tuple[Key, ...] = ("stem", "content", 3)
NUMBERED: tuple[Key, ...] = ("stem", "content", 4)
FIGURE: tuple[Key, ...] = ("stem", "content", 5)


def inline(index: int) -> tuple[Key, ...]:
    return (*PARA, "content", index)


TEXT = inline(0)
MEASURED = inline(1)
BREAK = inline(3)
MARKED_TEXT = inline(4)
MATH = inline(6)
QUANTITY = inline(8)

MARKABLE = {"text": TEXT, "math_inline": MATH, "quantity": QUANTITY}
MARK_TYPES = ["bold", "italic", "sub", "sup", "optional", "essential"]


def marks(*names: str) -> list[Json]:
    return [{"type": name} for name in names]


# --- Baselines ---------------------------------------------------------------------------------


@pytest.mark.parametrize("sample", ALL_SAMPLES)
def test_every_sample_validates_and_keeps_its_content(sample: Base) -> None:
    source = sample()
    assert_contains(source, dump(validate(source)))


# --- General rules: unknown fields, immutability, byte-stable serialisation ---------------------

UNKNOWN_FIELD_PATHS: list[tuple[str, Base, tuple[Key, ...]]] = [
    ("document", gallery_document, ()),
    ("doc", gallery_document, ("stem",)),
    ("paragraph", gallery_document, PARA),
    ("text", gallery_document, TEXT),
    ("quantity", gallery_document, QUANTITY),
    ("quantity attrs", gallery_document, (*QUANTITY, "attrs")),
    ("math_inline", gallery_document, MATH),
    ("math_inline attrs", gallery_document, (*MATH, "attrs")),
    ("hard_break", gallery_document, BREAK),
    ("mark", gallery_document, (*MARKED_TEXT, "marks", 0)),
    ("math_block", gallery_document, MATH_BLOCK),
    ("math_block attrs", gallery_document, (*MATH_BLOCK, "attrs")),
    ("table", gallery_document, TABLE),
    ("table_row", gallery_document, (*TABLE, "content", 0)),
    ("table_header", gallery_document, (*TABLE, "content", 0, "content", 0)),
    ("table_header attrs", gallery_document, (*TABLE, "content", 0, "content", 0, "attrs")),
    ("table_cell", gallery_document, (*TABLE, "content", 2, "content", 0)),
    ("cell paragraph", gallery_document, (*TABLE, "content", 2, "content", 0, "content", 0)),
    ("bullet_list", gallery_document, BULLETS),
    ("ordered_list", gallery_document, NUMBERED),
    ("list_item", gallery_document, (*BULLETS, "content", 0)),
    ("figure", gallery_document, FIGURE),
    ("figure attrs", gallery_document, (*FIGURE, "attrs")),
    ("stimulus", gallery_document, ("stimuli", 0)),
    ("part", gallery_document, ("parts", 0)),
    ("part body", gallery_document, ("parts", 0, "body")),
    ("lead_in", show_that_document, ("parts", 1, "lead_in")),
    ("mark point", show_that_document, ("parts", 1, "mark_points", 1)),
    ("mark point content", show_that_document, ("parts", 1, "mark_points", 1, "content")),
    ("accept_range", show_that_document, ("parts", 1, "mark_points", 1, "accept_range")),
    ("note", show_that_document, ("parts", 1, "notes", 0)),
    ("solution_model", show_that_document, ("solution_model",)),
    ("parameter", show_that_document, ("solution_model", "parameters", 0)),
    ("step", show_that_document, ("solution_model", "steps", 0)),
    ("answer binding", show_that_document, ("solution_model", "answers", 0)),
    ("constant", structured_document, ("solution_model", "constants", 0)),
    ("mcq", two_column_mcq_document, ("mcq",)),
    ("column header", two_column_mcq_document, ("mcq", "column_headers", 0)),
    ("option", two_column_mcq_document, ("mcq", "options", 0)),
    ("option cell", two_column_mcq_document, ("mcq", "options", 0, "cells", 1)),
    ("rationale", two_column_mcq_document, ("mcq", "options", 0, "rationale")),
    ("explanation", two_column_mcq_document, ("mcq", "explanation")),
    ("statement", roman_mcq_document, ("mcq", "statements", 0)),
]


@pytest.mark.parametrize(
    ("base", "path"),
    [(base, path) for _, base, path in UNKNOWN_FIELD_PATHS],
    ids=[label for label, _, _ in UNKNOWN_FIELD_PATHS],
)
def test_unknown_field_is_rejected_at_every_depth(base: Base, path: tuple[Key, ...]) -> None:
    rejects(base, put(*path, "zzz", value=1), r"extra_forbidden @ (.*\.)?zzz:")


# Fields of the older drafts (sections 3.1-3.3 and 4) that section 3.5 does not carry.
@rejected(
    Reject(
        "answer_space node",
        gallery_document,
        add("stem", "content", value={"type": "answer_space", "attrs": {"lines": 4}}),
        r"union_tag_invalid @ stem\.content\.6:",
    ),
    Reject(
        "list node with ordered attribute",
        gallery_document,
        put(*BULLETS, "type", value="list"),
        r"union_tag_invalid @ stem\.content\.3:",
    ),
    Reject(
        "quantity sig_figs",
        gallery_document,
        put(*QUANTITY, "attrs", "sig_figs", value=2),
        r"extra_forbidden @ .*quantity\.attrs\.sig_figs:",
    ),
    Reject(
        "figure asset_id",
        gallery_document,
        put(*FIGURE, "attrs", "asset_id", value="asset-1"),
        r"extra_forbidden @ .*figure\.attrs\.asset_id:",
    ),
    Reject(
        "figure role",
        gallery_document,
        put(*FIGURE, "attrs", "role", value="question_diagram"),
        r"extra_forbidden @ .*figure\.attrs\.role:",
    ),
    Reject(
        "solution model ranges",
        show_that_document,
        put("solution_model", "ranges", value=[]),
        r"extra_forbidden @ solution_model\.ranges:",
    ),
    Reject(
        "solution model schema_version",
        show_that_document,
        put("solution_model", "schema_version", value="1.0"),
        r"extra_forbidden @ solution_model\.schema_version:",
    ),
    Reject(
        "answer sig_figs",
        show_that_document,
        put("solution_model", "answers", 0, "sig_figs", value=2),
        r"extra_forbidden @ solution_model\.answers\.0\.sig_figs:",
    ),
    Reject(
        "answer part_label",
        show_that_document,
        put("solution_model", "answers", 0, "part_label", value="a"),
        r"extra_forbidden @ solution_model\.answers\.0\.part_label:",
    ),
)
def test_fields_of_older_drafts_are_rejected(case: Reject) -> None:
    rejects(case.base, case.mutate, case.match)


def test_models_are_immutable() -> None:
    document = validate(show_that_document())
    solution_model = document.solution_model
    assert solution_model is not None
    stem_paragraph = document.stem.content[0]
    targets: list[tuple[Any, str, Any]] = [
        (document, "total_marks", 9),
        (document, "stem", document.parts[0].body),
        (document.stem, "content", ()),
        (stem_paragraph, "content", ()),
        (document.parts[0], "marks", 3),
        (document.parts[0].mark_points[0], "kind", "method"),
        (document.parts[1].notes[0], "kind", "general"),
        (solution_model, "steps", ()),
        (solution_model.parameters[0], "value", "1"),
        (solution_model.steps[0], "stated_value", "4"),
    ]
    for quantity_node in document.quantities():
        targets.append((quantity_node.attrs, "value", "1"))
    for target, name, value in targets:
        with pytest.raises(ValidationError, match="frozen"):
            setattr(target, name, value)

    mcq = validate(mcq_document()).mcq
    assert mcq is not None
    with pytest.raises(ValidationError, match="frozen"):
        setattr(mcq, "correct_key", "B")  # noqa: B010 - bypasses the static read-only check
    with pytest.raises(ValidationError, match="frozen"):
        setattr(mcq.options[0], "key", "B")  # noqa: B010


def test_collections_cannot_be_mutated_in_place() -> None:
    document = validate(show_that_document())
    solution_model = document.solution_model
    assert solution_model is not None
    collections: list[Any] = [
        document.levels,
        document.secondary_syllabus_nodes,
        document.stimuli,
        document.parts,
        document.stem.content,
        document.parts[1].mark_points,
        document.parts[1].notes,
        document.parts[1].depends_on,
        document.parts[1].ecf_from,
        solution_model.parameters,
        solution_model.steps,
        solution_model.answers,
    ]
    for collection in collections:
        assert isinstance(collection, tuple), type(collection)


@pytest.mark.parametrize("sample", ALL_SAMPLES)
def test_serialisation_is_byte_stable(sample: Base) -> None:
    first = validate(sample()).model_dump_json()
    second = QuestionDocument.model_validate_json(first).model_dump_json()
    assert second.encode() == first.encode()
    assert validate(json.loads(first)).model_dump_json() == first
    assert json.loads(first) == dump(validate(sample()))


@pytest.mark.parametrize("sample", ALL_SAMPLES)
def test_same_content_serialises_to_same_bytes_whatever_the_key_order(sample: Base) -> None:
    source = sample()
    shuffled = reorder_keys(source)
    assert shuffled == source
    assert json.dumps(shuffled) != json.dumps(source)
    assert validate(shuffled).model_dump_json() == validate(source).model_dump_json()


@pytest.mark.parametrize("sample", ALL_SAMPLES)
def test_arrays_keep_their_order(sample: Base) -> None:
    source = sample()
    dumped = dump(validate(source))
    for name in ("parts", "stimuli"):
        assert [item["id"] for item in dumped[name]] == [
            item["id"] for item in source.get(name, [])
        ]
    assert dumped["stem"]["content"][0] == dump(validate(source))["stem"]["content"][0]
    assert_contains(source["stem"], dumped["stem"])


# --- Nodes -------------------------------------------------------------------------------------

TYPE_PATHS: list[tuple[str, tuple[Key, ...], str]] = [
    ("doc", ("stem",), r"missing @ stem\.type:"),
    ("paragraph", PARA, r"union_tag_not_found @ stem\.content\.0:"),
    ("text", TEXT, r"union_tag_not_found @ stem\.content\.0\.paragraph\.content\.0:"),
    ("quantity", MEASURED, r"union_tag_not_found @ stem\.content\.0\.paragraph\.content\.1:"),
    ("hard_break", BREAK, r"union_tag_not_found @ stem\.content\.0\.paragraph\.content\.3:"),
    ("math_inline", MATH, r"union_tag_not_found @ stem\.content\.0\.paragraph\.content\.6:"),
    ("mark", (*MARKED_TEXT, "marks", 0), r"missing @ .*\.marks\.0\.type:"),
    ("math_block", MATH_BLOCK, r"union_tag_not_found @ stem\.content\.1:"),
    ("table", TABLE, r"union_tag_not_found @ stem\.content\.2:"),
    ("table_row", (*TABLE, "content", 0), r"missing @ .*table\.content\.0\.type:"),
    (
        "table_header",
        (*TABLE, "content", 0, "content", 0),
        r"union_tag_not_found @ .*table\.content\.0\.content\.0:",
    ),
    (
        "table_cell",
        (*TABLE, "content", 2, "content", 1),
        r"union_tag_not_found @ .*table\.content\.2\.content\.1:",
    ),
    ("bullet_list", BULLETS, r"union_tag_not_found @ stem\.content\.3:"),
    ("ordered_list", NUMBERED, r"union_tag_not_found @ stem\.content\.4:"),
    (
        "bullet list_item",
        (*BULLETS, "content", 0),
        r"missing @ .*bullet_list\.content\.0\.type:",
    ),
    (
        "ordered list_item",
        (*NUMBERED, "content", 1),
        r"missing @ .*ordered_list\.content\.1\.type:",
    ),
    ("figure", FIGURE, r"union_tag_not_found @ stem\.content\.5:"),
]


@pytest.mark.parametrize(
    ("path", "match"),
    [(path, match) for _, path, match in TYPE_PATHS],
    ids=[label for label, _, _ in TYPE_PATHS],
)
def test_type_is_required_on_every_node(path: tuple[Key, ...], match: str) -> None:
    rejects(gallery_document, drop(*path, "type"), match)


@pytest.mark.parametrize("sample", ALL_SAMPLES)
def test_every_serialised_node_and_mark_carries_its_type(sample: Base) -> None:
    found = list(nodes_of(dump(validate(sample()))))
    assert found
    for node in found:
        assert isinstance(node.get("type"), str), node


def test_type_is_required_when_a_doc_is_validated_on_its_own() -> None:
    Doc.model_validate(line(text("x")))
    with pytest.raises(ValidationError, match="type"):
        Doc.model_validate({"content": [paragraph(text("x"))]})


@rejected(
    Reject(
        "doc without blocks",
        gallery_document,
        put("stem", "content", value=[]),
        r"too_short @ stem\.content:",
    ),
    Reject(
        "math_block with empty latex",
        gallery_document,
        put(*MATH_BLOCK, "attrs", "latex", value=""),
        r"string_too_short @ .*math_block\.attrs\.latex:",
    ),
    Reject(
        "text with empty text",
        gallery_document,
        put(*TEXT, "text", value=""),
        r"string_too_short @ .*text\.text:",
    ),
    Reject(
        "header cell without a paragraph",
        gallery_document,
        put(*TABLE, "content", 0, "content", 0, "content", value=[]),
        r"too_short @ .*table\.content\.0\.content\.0\.table_header\.content:",
    ),
    Reject(
        "body cell without a paragraph",
        gallery_document,
        put(*TABLE, "content", 2, "content", 0, "content", value=[]),
        r"too_short @ .*table\.content\.2\.content\.0\.table_cell\.content:",
    ),
    Reject(
        "bullet item without a paragraph",
        gallery_document,
        put(*BULLETS, "content", 0, "content", value=[]),
        r"too_short @ .*bullet_list\.content\.0\.content:",
    ),
    Reject(
        "ordered item without a paragraph",
        gallery_document,
        put(*NUMBERED, "content", 0, "content", value=[]),
        r"too_short @ .*ordered_list\.content\.0\.content:",
    ),
    Reject(
        "row narrower than the others",
        gallery_document,
        cut(*TABLE, "content", 3, "content"),
        "different widths",
    ),
    Reject(
        "colspan wider than the other rows",
        gallery_document,
        put(*TABLE, "content", 0, "content", 0, "attrs", "colspan", value=3),
        "different widths",
    ),
    Reject(
        "colspan removed from the spanning header",
        gallery_document,
        drop(*TABLE, "content", 0, "content", 0, "attrs"),
        "different widths",
    ),
)
def test_node_content_rules(case: Reject) -> None:
    rejects(case.base, case.mutate, case.match)


def test_paragraph_may_be_empty() -> None:
    document = accepts(
        gallery_document, put(*BULLETS, "content", 0, "content", 0, value=paragraph())
    )
    assert dump(document)["stem"]["content"][3]["content"][0]["content"][0]["content"] == []


def one_cell_table(**attrs: int) -> Mutation:
    return put(*TABLE, value=grid(row(cell(text("only cell"), header=False, **attrs))))


@pytest.mark.parametrize(
    ("name", "value", "ok"),
    [
        ("colspan", 0, False),
        ("colspan", 1, True),
        ("colspan", 12, True),
        ("colspan", 13, False),
        ("rowspan", 0, False),
        ("rowspan", 1, True),
        ("rowspan", 50, True),
        ("rowspan", 51, False),
    ],
)
def test_span_bounds(name: str, value: int, ok: bool) -> None:
    mutate = one_cell_table(**{name: value})
    if ok:
        document = accepts(gallery_document, mutate)
        spanned = dump(document)["stem"]["content"][2]["content"][0]["content"][0]
        assert spanned["attrs"][name] == value
    else:
        kind = "less_than_equal" if value > 1 else "greater_than_equal"
        rejects(gallery_document, mutate, rf"{kind} @ .*table_cell\.attrs\.{name}:")


def test_row_widths_are_only_compared_when_no_cell_spans_rows() -> None:
    def ragged(**first_cell: int) -> Mutation:
        return put(
            *TABLE,
            value=grid(
                row(cell(text("label"), header=False, **first_cell), cell(text("first"))),
                row(cell(text("second"))),
            ),
        )

    accepts(gallery_document, ragged(rowspan=2))
    rejects(gallery_document, ragged(), "different widths")


def test_table_with_header_body_and_colspan_is_kept() -> None:
    table_node = dump(validate(gallery_document()))["stem"]["content"][2]
    kinds = [[c["type"] for c in r["content"]] for r in table_node["content"]]
    assert kinds == [
        ["table_header"],
        ["table_header", "table_header"],
        ["table_cell", "table_cell"],
        ["table_cell", "table_cell"],
    ]
    assert table_node["content"][0]["content"][0]["attrs"]["colspan"] == 2
    assert all(r["type"] == "table_row" for r in table_node["content"])


def test_lists_math_block_and_hard_break_are_kept() -> None:
    stem = dump(validate(gallery_document()))["stem"]["content"]
    assert [block["type"] for block in stem] == [
        "paragraph",
        "math_block",
        "table",
        "bullet_list",
        "ordered_list",
        "figure",
    ]
    assert stem[1]["attrs"]["latex"] == r"a = g \sin\theta"
    assert [item["type"] for item in stem[3]["content"]] == ["list_item", "list_item"]
    assert [item["type"] for item in stem[4]["content"]] == ["list_item", "list_item"]
    assert len(stem[3]["content"][1]["content"]) == 2
    assert stem[0]["content"][3]["type"] == "hard_break"
    assert stem[5]["attrs"]["stimulus_id"] == "ramp"


# Marks


@pytest.mark.parametrize("node", list(MARKABLE))
@pytest.mark.parametrize("mark", MARK_TYPES)
def test_every_mark_type_is_accepted_on_every_markable_node(node: str, mark: str) -> None:
    path = MARKABLE[node]
    data = gallery_document()
    put(*path, "marks", value=marks(mark))(data)
    kept = _at(dump(validate(data)), path)
    assert kept["type"] == node
    assert kept["marks"] == marks(mark)


def test_mark_types_are_exactly_the_six_of_the_spec() -> None:
    assert set(permitted_values(gallery_document, *MARKED_TEXT, "marks", 0, "type")) == set(
        MARK_TYPES
    )


@pytest.mark.parametrize("node", list(MARKABLE))
@pytest.mark.parametrize(
    ("names", "match"),
    [
        (("bold", "bold"), "duplicate mark"),
        (("optional", "bold", "optional"), "duplicate mark"),
        (("sub", "sup"), "mutually exclusive"),
        (("sup", "italic", "sub"), "mutually exclusive"),
        (("optional", "essential"), "mutually exclusive"),
        (("essential", "optional"), "mutually exclusive"),
    ],
)
def test_conflicting_marks_are_rejected(node: str, names: tuple[str, ...], match: str) -> None:
    path = MARKABLE[node]
    rejects(gallery_document, put(*path, "marks", value=marks(*names)), match)


@pytest.mark.parametrize("node", list(MARKABLE))
@pytest.mark.parametrize(
    "names",
    [("bold", "italic", "sub", "optional"), ("sup", "essential"), ("sub", "essential")],
)
def test_compatible_marks_combine(node: str, names: tuple[str, ...]) -> None:
    path = MARKABLE[node]
    document = accepts(gallery_document, put(*path, "marks", value=marks(*names)))
    assert _at(dump(document), path)["marks"] == marks(*names)


@rejected(
    Reject(
        "marks as strings",
        gallery_document,
        put(*MARKED_TEXT, "marks", value=["bold"]),
        r"model_type @ .*text\.marks\.0:",
    ),
    Reject(
        "marks as strings on math_inline",
        gallery_document,
        put(*MATH, "marks", value=["italic"]),
        r"model_type @ .*math_inline\.marks\.0:",
    ),
    Reject(
        "marks as strings on quantity",
        gallery_document,
        put(*QUANTITY, "marks", value=["essential"]),
        r"model_type @ .*quantity\.marks\.0:",
    ),
    Reject(
        "unknown mark type",
        gallery_document,
        put(*MARKED_TEXT, "marks", 0, "type", value="underline"),
        r"enum @ .*text\.marks\.0\.type:",
    ),
    Reject(
        "marks on hard_break",
        gallery_document,
        put(*BREAK, "marks", value=marks("bold")),
        r"extra_forbidden @ .*hard_break\.marks:",
    ),
)
def test_marks_are_objects_on_markable_nodes_only(case: Reject) -> None:
    rejects(case.base, case.mutate, case.match)


def test_optional_mark_on_a_quantity_in_a_mark_point() -> None:
    document = validate(structured_document())
    answer = dump(document)["parts"][0]["mark_points"][1]["content"]["content"][0]["content"][1]
    assert answer["type"] == "quantity"
    assert answer["attrs"]["value"] == "3.0"
    assert answer["marks"] == marks("optional")


# Number text

NUMBERS_ACCEPTED = [
    "20",
    "20.0",
    "-5",
    "1.5e-3",
    "1e+3",
    "0",
    "0.5",
    "-0.25",
    "1E-3",
    "1.5E+3",
    "6.02e+23",
    "-1.6e-19",
]
NUMBERS_REJECTED = [
    "+5",
    ".5",
    "5.",
    "−5",  # Unicode minus sign
    "1.5e−3",  # Unicode minus sign in the exponent
    "٢٠",  # Arabic-Indic digits
    "２０",  # full-width digits
    "२०",  # Devanagari digits
    "2²",  # superscript two
    "",
    "-",
    " 20",
    "20 ",
    "20\n",
    "1,5",
    "--5",
    "5-",
    "-.5",
    "5.e+3",
    "1e",
    "1e-",
    "1e+",
    "e+5",
    "1e+1.5",
    "1.2.3",
    "1 000",
    "1_000",
    "0x10",
    "abc",
    "NaN",
    "inf",
]
UNSIGNED_ACCEPTED = [value for value in NUMBERS_ACCEPTED if not value.startswith("-")]
UNSIGNED_REJECTED = [*NUMBERS_REJECTED, "-5", "-0.1", "-1.6e-19"]


def spare_parameter_document() -> Json:
    """show_that_document() plus a parameter that no quantity is bound to."""
    data = show_that_document()
    data["solution_model"]["parameters"].append({"name": "m", "value": "1", "unit": "kg"})
    return data


def wide_range_document() -> Json:
    """show_that_document() with an accept range wide enough for any test bound."""
    data = show_that_document()
    data["parts"][1]["mark_points"][1]["accept_range"] = {
        "minimum": "-1e+30",
        "maximum": "1e+30",
        "unit": "rad/s",
    }
    return data


RANGE: tuple[Key, ...] = ("parts", 1, "mark_points", 1, "accept_range")
SIGNED_NUMBER_FIELDS: dict[str, tuple[Base, tuple[Key, ...]]] = {
    "quantity value": (gallery_document, (*MEASURED, "attrs", "value")),
    "parameter value": (spare_parameter_document, ("solution_model", "parameters", 3, "value")),
    "accept minimum": (wide_range_document, (*RANGE, "minimum")),
    "accept maximum": (wide_range_document, (*RANGE, "maximum")),
}
UNCERTAINTY: tuple[Base, tuple[Key, ...]] = (gallery_document, (*MEASURED, "attrs", "uncertainty"))


def number_field(name: str) -> tuple[Base, tuple[Key, ...]]:
    return UNCERTAINTY if name == "uncertainty" else SIGNED_NUMBER_FIELDS[name]


def assert_number_accepted(name: str, value: str) -> None:
    base, path = number_field(name)
    validate(base())
    data = base()
    put(*path, value=value)(data)
    assert _at(dump(validate(data)), path) == value


def assert_number_rejected(name: str, value: str) -> None:
    base, path = number_field(name)
    validate(base())
    data = base()
    put(*path, value=value)(data)
    with pytest.raises(ValidationError) as caught:
        validate(data)
    where = ".".join(str(key) for key in path[-2:])
    lines = error_lines(caught.value)
    assert any(re.search(rf"string_pattern_mismatch @ .*{where}:", entry) for entry in lines), lines


@pytest.mark.parametrize("field", list(SIGNED_NUMBER_FIELDS))
@pytest.mark.parametrize("value", NUMBERS_ACCEPTED)
def test_number_text_accepted_and_stored_as_written(field: str, value: str) -> None:
    assert_number_accepted(field, value)


@pytest.mark.parametrize("field", list(SIGNED_NUMBER_FIELDS))
@pytest.mark.parametrize("value", NUMBERS_REJECTED, ids=ascii)
def test_number_text_rejected(field: str, value: str) -> None:
    assert_number_rejected(field, value)


@pytest.mark.parametrize("value", UNSIGNED_ACCEPTED)
def test_uncertainty_accepted_and_stored_as_written(value: str) -> None:
    assert_number_accepted("uncertainty", value)


@pytest.mark.parametrize("value", UNSIGNED_REJECTED, ids=ascii)
def test_uncertainty_rejected(value: str) -> None:
    assert_number_rejected("uncertainty", value)


@pytest.mark.parametrize("field", [*SIGNED_NUMBER_FIELDS, "uncertainty"])
@pytest.mark.parametrize("value", [20, 20.0, True])
def test_number_must_be_text_not_a_json_number(field: str, value: Any) -> None:
    base, path = number_field(field)
    rejects(base, put(*path, value=value), rf"string_type @ .*{path[-1]}:")


def test_twenty_and_twenty_point_zero_are_different_values() -> None:
    plain = accepts(gallery_document, put(*MEASURED, "attrs", "value", value="20"))
    padded = accepts(gallery_document, put(*MEASURED, "attrs", "value", value="20.0"))
    assert plain != padded
    assert plain.model_dump_json() != padded.model_dump_json()


def test_quantity_with_uncertainty_is_kept() -> None:
    document = validate(gallery_document())
    found = [q for q in document.quantities() if q.attrs.uncertainty is not None]
    assert sorted((q.attrs.value, q.attrs.unit, q.attrs.uncertainty) for q in found) == [
        ("1.20", "kg", "0.01"),
        ("1.7", "s", "0.1"),
        ("2.4", "s", "0.1"),
    ]


DIGITS = st.text(alphabet="0123456789", min_size=1, max_size=6)


@st.composite
def unsigned_numbers(draw: st.DrawFn) -> str:
    """Number text inside the grammar of the spec, with an explicitly signed exponent."""
    value = draw(DIGITS)
    if draw(st.booleans()):
        value += "." + draw(DIGITS)
    if draw(st.booleans()):
        value += draw(st.sampled_from("eE")) + draw(st.sampled_from("+-")) + draw(DIGITS)
    return value


@st.composite
def signed_numbers(draw: st.DrawFn) -> str:
    return ("-" if draw(st.booleans()) else "") + draw(unsigned_numbers())


@st.composite
def corrupted_numbers(draw: st.DrawFn) -> str:
    """A valid number with one character inserted that no number may contain."""
    value = draw(signed_numbers())
    foreign = draw(st.sampled_from([" ", "\n", "\t", "−", "٣", "３", ",", "_", "x"]))
    position = draw(st.integers(min_value=0, max_value=len(value)))
    return value[:position] + foreign + value[position:]


LOOSE_NUMBER = re.compile(r"-?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?")


@pytest.mark.parametrize("field", ["quantity value", "parameter value"])
@given(value=signed_numbers())
def test_property_any_number_in_the_grammar_is_accepted(field: str, value: str) -> None:
    assert_number_accepted(field, value)


@given(value=signed_numbers())
def test_property_any_number_in_the_grammar_is_an_accept_bound(value: str) -> None:
    # Both bounds are set so that the test does not depend on how two bounds compare.
    data = wide_range_document()
    put(*RANGE, "minimum", value=value)(data)
    put(*RANGE, "maximum", value=value)(data)
    kept = _at(dump(validate(data)), RANGE)
    assert kept["minimum"] == kept["maximum"] == value


@given(value=unsigned_numbers())
def test_property_any_unsigned_number_is_an_uncertainty(value: str) -> None:
    assert_number_accepted("uncertainty", value)


@given(value=unsigned_numbers())
def test_property_a_signed_number_is_never_an_uncertainty(value: str) -> None:
    assert_number_rejected("uncertainty", "-" + value)


@pytest.mark.parametrize("field", [*SIGNED_NUMBER_FIELDS, "uncertainty"])
@given(value=corrupted_numbers())
def test_property_a_foreign_character_makes_a_number_invalid(field: str, value: str) -> None:
    assert_number_rejected(field, value)


@pytest.mark.parametrize("field", [*SIGNED_NUMBER_FIELDS, "uncertainty"])
@given(value=st.text(max_size=12))
def test_property_arbitrary_text_is_not_a_number(field: str, value: str) -> None:
    assume(LOOSE_NUMBER.fullmatch(value) is None)
    assert_number_rejected(field, value)


@given(value=signed_numbers())
def test_property_quantity_value_survives_a_doc_round_trip(value: str) -> None:
    first = Doc.model_validate(line(quantity(value, "m"))).model_dump_json()
    assert json.loads(first)["content"][0]["content"][0]["attrs"]["value"] == value
    assert Doc.model_validate_json(first).model_dump_json() == first


# Unit text

UNITS_ACCEPTED = ["", "m", "m/s", "m s^-1", "kg m^2", "N m", "µm", "Ω", "°C", "%"]
UNITS_REJECTED = [" m", "m ", " ", "\tm", "m\n", "1/s", "2m", "/s", "-m", "^2", "(m)", ".m"]
UNIT_FIELDS: dict[str, tuple[Base, tuple[Key, ...]]] = {
    "quantity unit": (gallery_document, (*MEASURED, "attrs", "unit")),
    "parameter unit": (spare_parameter_document, ("solution_model", "parameters", 3, "unit")),
    "accept range unit": (wide_range_document, (*RANGE, "unit")),
    "step unit": (spare_parameter_document, ("solution_model", "steps", 1, "unit")),
}
# Spec 3.5: "Birim metni: ... baş ve sonda boşluk olamaz". Fields listed here are known to violate
# it and are marked xfail; the set is empty since the rule was fixed for all unit fields.
TRAILING_SPACE_ACCEPTED: set[str] = set()


def unit_rejections() -> list[Any]:
    params = []
    for field in UNIT_FIELDS:
        for unit in UNITS_REJECTED:
            defect = unit.endswith(" ") and unit.strip() and field in TRAILING_SPACE_ACCEPTED
            params.append(
                pytest.param(
                    field,
                    unit,
                    id=f"{field}-{unit!a}",
                    marks=[
                        pytest.mark.xfail(
                            strict=True,
                            reason="spec 3.5: a unit cannot end with a space; "
                            f"the {field} accepts one",
                        )
                    ]
                    if defect
                    else [],
                )
            )
    return params


@pytest.mark.parametrize("field", list(UNIT_FIELDS))
@pytest.mark.parametrize("unit", UNITS_ACCEPTED, ids=ascii)
def test_unit_text_accepted_and_stored_as_written(field: str, unit: str) -> None:
    base, path = UNIT_FIELDS[field]
    validate(base())
    data = base()
    put(*path, value=unit)(data)
    assert _at(dump(validate(data)), path) == unit


@pytest.mark.parametrize(("field", "unit"), unit_rejections())
def test_unit_text_rejected(field: str, unit: str) -> None:
    base, path = UNIT_FIELDS[field]
    rejects(base, put(*path, value=unit), r"(string_pattern_mismatch|value_error) @ .*(unit|attrs)")


# --- QuestionDocument --------------------------------------------------------------------------


@rejected(
    Reject(
        "schema_version missing",
        structured_document,
        drop("schema_version"),
        r"missing @ schema_version:",
    ),
    Reject(
        "schema_version 2.0",
        structured_document,
        put("schema_version", value="2.0"),
        r"literal_error @ schema_version:",
    ),
    Reject(
        "schema_version 1",
        structured_document,
        put("schema_version", value="1"),
        r"literal_error @ schema_version:",
    ),
    Reject(
        "schema_version as a number",
        structured_document,
        put("schema_version", value=1.0),
        r"literal_error @ schema_version:",
    ),
    Reject(
        "unknown question_class",
        structured_document,
        put("question_class", value="essay"),
        r"enum @ question_class:",
    ),
    Reject(
        "exam_section with upper case",
        structured_document,
        put("exam_section", value="Paper_2"),
        r"string_pattern_mismatch @ exam_section:",
    ),
    Reject(
        "exam_section empty",
        structured_document,
        put("exam_section", value=""),
        r"string_pattern_mismatch @ exam_section:",
    ),
    Reject("levels empty", structured_document, put("levels", value=[]), r"too_short @ levels:"),
    Reject(
        "levels repeated",
        structured_document,
        put("levels", value=["sl", "sl"]),
        "levels must be unique",
    ),
    Reject(
        "levels in non-canonical order",
        structured_document,
        put("levels", value=["hl", "sl"]),
        "canonical order",
    ),
    Reject(
        "unknown level",
        structured_document,
        put("levels", value=["sl", "ahl"]),
        r"enum @ levels\.1:",
    ),
    Reject(
        "unknown difficulty",
        structured_document,
        put("difficulty", value="extreme"),
        r"enum @ difficulty:",
    ),
    Reject(
        "secondary syllabus node repeated",
        structured_document,
        put("secondary_syllabus_nodes", value=["A.2", "A.2"]),
        "duplicate syllabus node",
    ),
    Reject(
        "secondary syllabus node repeats the primary",
        structured_document,
        put("secondary_syllabus_nodes", value=["A.2", "A.1"]),
        "duplicate syllabus node",
    ),
    Reject(
        "stem with only an empty paragraph",
        structured_document,
        put("stem", value=doc(paragraph())),
        "empty stem",
    ),
    Reject(
        "stem without blocks",
        structured_document,
        put("stem", "content", value=[]),
        r"too_short @ stem\.content:",
    ),
    Reject(
        "stimulus id repeated",
        structured_document,
        add("stimuli", value=stimulus("fig-1")),
        "duplicate stimulus id",
    ),
    Reject(
        "unknown stimulus use",
        structured_document,
        put("stimuli", 0, "use", value="decorative"),
        r"enum @ stimuli\.0\.use:",
    ),
    Reject(
        "stimulus description empty",
        structured_document,
        put("stimuli", 0, "description", value=""),
        r"string_too_short @ stimuli\.0\.description:",
    ),
    Reject(
        "stimulus with asset but no alt text",
        structured_document,
        put("stimuli", 0, "asset_id", value="asset-1"),
        "must have alt text",
    ),
    Reject(
        "structured question with an mcq block",
        structured_document,
        put("mcq", value=plain_mcq_document()["mcq"]),
        "structured question has parts and no mcq",
    ),
    Reject(
        "structured question without parts",
        question(part("p-a", "a")).copy,
        put("parts", value=[]),
        "structured question has parts",
    ),
    Reject(
        "total above the sum of part marks",
        structured_document,
        put("total_marks", value=6),
        "do not add up to total_marks",
    ),
    Reject(
        "total below the sum of part marks",
        structured_document,
        put("total_marks", value=4),
        "do not add up to total_marks",
    ),
    Reject(
        "multiple-choice question without an mcq block",
        plain_mcq_document,
        drop("mcq"),
        "multiple-choice question has an mcq block",
    ),
    Reject(
        "multiple-choice question with parts",
        plain_mcq_document,
        put("parts", value=[part("p-a", "a")]),
        "multiple-choice question has an mcq block and no parts",
    ),
    Reject(
        "multiple-choice question worth two marks",
        plain_mcq_document,
        put("total_marks", value=2),
        "exactly 1 mark",
    ),
)
def test_question_document_rules(case: Reject) -> None:
    rejects(case.base, case.mutate, case.match)


@accepted(
    Accept("class data_based", structured_document, put("question_class", value="data_based")),
    Accept(
        "class long_structured", structured_document, put("question_class", value="long_structured")
    ),
    Accept("exam_section paper_1a", structured_document, put("exam_section", value="paper_1a")),
    Accept("levels sl only", structured_document, put("levels", value=["sl"])),
    Accept("levels hl only", structured_document, put("levels", value=["hl"])),
    Accept("difficulty easy", structured_document, put("difficulty", value="easy")),
    Accept("difficulty medium", structured_document, put("difficulty", value="medium")),
    Accept("difficulty hard", structured_document, put("difficulty", value="hard")),
    Accept("language", structured_document, put("language", value="en")),
    Accept("calculator", structured_document, put("calculator", value=False)),
    Accept("outcome", structured_document, put("outcome", value="projectile from a height")),
    Accept(
        "distinct secondary nodes",
        structured_document,
        put("secondary_syllabus_nodes", value=["A.2", "A.3"]),
    ),
    Accept("use read_only", structured_document, put("stimuli", 0, "use", value="read_only")),
    Accept("use read_values", structured_document, put("stimuli", 0, "use", value="read_values")),
    Accept(
        "use student_annotates",
        structured_document,
        put("stimuli", 0, "use", value="student_annotates"),
    ),
    Accept(
        "stimulus with asset and alt text",
        structured_document,
        both(
            put("stimuli", 0, "asset_id", value="asset-1"),
            put("stimuli", 0, "alt_text", value="A drone above flat ground."),
        ),
    ),
    Accept("no solution model", plain_mcq_document, put("outcome", value="rigid container")),
)
def test_question_document_accepts(case: Accept) -> None:
    accepts(case.base, case.mutate)


def test_enumerations_named_by_the_spec() -> None:
    assert set(permitted_values(structured_document, "question_class")) == {
        "mcq",
        "data_based",
        "short_structured",
        "long_structured",
    }
    assert permitted_values(structured_document, "levels", 0) == ["sl", "hl"]
    assert set(permitted_values(structured_document, "difficulty")) == {"easy", "medium", "hard"}
    assert set(permitted_values(structured_document, "stimuli", 0, "use")) == {
        "read_only",
        "read_values",
        "student_annotates",
    }
    assert permitted_values(structured_document, "schema_version") == ["1.0"]


def test_optional_metadata_may_be_left_out() -> None:
    source = question(part("p-a", "a"))
    for name in ("language", "calculator", "difficulty", "outcome", "solution_model", "stimuli"):
        assert name not in source
    validate(source)


def test_levels_given_in_another_order_are_rejected_not_reordered() -> None:
    canonical = validate(structured_document())
    assert dump(canonical)["levels"] == ["sl", "hl"]
    rejects(structured_document, put("levels", value=["hl", "sl"]), "canonical order")


def test_visual_pending_follows_missing_assets() -> None:
    assert validate(question(part("p-a", "a"))).visual_pending is False
    assert validate(structured_document()).visual_pending is True
    with_asset = both(
        put("stimuli", 0, "asset_id", value="asset-1"),
        put("stimuli", 0, "alt_text", value="A drone above flat ground."),
    )
    assert accepts(structured_document, with_asset).visual_pending is False
    assert validate(figure_options_mcq_document()).visual_pending is False
    one_missing = both(drop("stimuli", 2, "asset_id"), drop("stimuli", 2, "alt_text"))
    assert accepts(figure_options_mcq_document, one_missing).visual_pending is True
    mixed = both(with_asset, add("stimuli", value=stimulus("fig-2")))
    assert accepts(structured_document, mixed).visual_pending is True


# Figure and stimulus references

FIGURE_PLACES: list[tuple[str, Base, tuple[Key, ...], str]] = [
    ("stem", structured_document, ("stem",), "fig-1"),
    ("lead_in", structured_document, ("parts", 1, "lead_in"), "fig-1"),
    ("part body", structured_document, ("parts", 0, "body"), "fig-1"),
    ("mark point", structured_document, ("parts", 0, "mark_points", 0, "content"), "fig-1"),
    ("note", structured_document, ("parts", 1, "notes", 1, "content"), "fig-1"),
    ("option cell", figure_options_mcq_document, ("mcq", "options", 0, "cells", 0), "opt-b"),
    ("rationale", figure_options_mcq_document, ("mcq", "options", 0, "rationale"), "opt-a"),
    ("explanation", figure_options_mcq_document, ("mcq", "explanation"), "opt-c"),
]


@pytest.mark.parametrize(
    ("base", "path", "known"),
    [(base, path, known) for _, base, path, known in FIGURE_PLACES],
    ids=[label for label, _, _, _ in FIGURE_PLACES],
)
def test_figure_reference_must_resolve_wherever_it_stands(
    base: Base, path: tuple[Key, ...], known: str
) -> None:
    accepts(base, add(*path, "content", value=figure(known)))
    rejects(base, add(*path, "content", value=figure("missing")), "unknown stimulus missing")


def test_figure_in_column_header_and_statement_must_resolve() -> None:
    rejects(
        two_column_mcq_document,
        add("mcq", "column_headers", 0, "content", value=figure("missing")),
        "unknown stimulus missing",
    )
    rejects(
        roman_mcq_document,
        add("mcq", "statements", 0, "content", value=figure("missing")),
        "unknown stimulus missing",
    )


def test_stimulus_refs_must_resolve() -> None:
    rejects(
        structured_document,
        put("parts", 0, "stimulus_refs", value=["fig-9"]),
        "unknown stimulus fig-9",
    )
    rejects(
        structured_document,
        put("parts", 1, "stimulus_refs", value=["fig-1", "fig-9"]),
        "unknown stimulus fig-9",
    )
    accepts(structured_document, put("parts", 1, "stimulus_refs", value=["fig-1"]))


def test_renaming_a_stimulus_breaks_the_figures_that_point_at_it() -> None:
    rejects(structured_document, put("stimuli", 0, "id", value="fig-2"), "unknown stimulus fig-1")


# --- Multiple-choice block ---------------------------------------------------------------------

OPTIONS: tuple[Key, ...] = ("mcq", "options")


def swap_first_two_options(data: Json) -> None:
    options = data["mcq"]["options"]
    options[0], options[1] = options[1], options[0]


@rejected(
    Reject(
        "unknown option_kind",
        plain_mcq_document,
        put("mcq", "option_kind", value="essay"),
        r"enum @ mcq\.option_kind:",
    ),
    Reject(
        "unknown option_layout",
        plain_mcq_document,
        put("mcq", "option_layout", value="grid"),
        r"enum @ mcq\.option_layout:",
    ),
    Reject("three options", plain_mcq_document, cut(*OPTIONS), "exactly A, B, C, D"),
    Reject(
        "a fifth option E",
        plain_mcq_document,
        add(
            *OPTIONS,
            value={
                "key": "E",
                "cells": [line(text("density"))],
                "rationale": line(text("Mass and volume are both fixed.")),
            },
        ),
        r"literal_error @ mcq\.options\.4\.key:",
    ),
    Reject(
        "a fifth option keyed D",
        plain_mcq_document,
        add(
            *OPTIONS,
            value={
                "key": "D",
                "cells": [line(text("density"))],
                "rationale": line(text("Mass and volume are both fixed.")),
            },
        ),
        "exactly A, B, C, D",
    ),
    Reject("options out of order", plain_mcq_document, swap_first_two_options, "in that order"),
    Reject(
        "option key repeated",
        plain_mcq_document,
        put(*OPTIONS, 1, "key", value="A"),
        "exactly A, B, C, D",
    ),
    Reject(
        "single_value option with two cells",
        plain_mcq_document,
        add(*OPTIONS, 0, "cells", value=line(text("rises"))),
        r"1 cell\(s\) for this layout",
    ),
    Reject(
        "single_value with column headers",
        plain_mcq_document,
        put("mcq", "column_headers", value=[line(text("Quantity")), line(text("Change"))]),
        "column headers",
    ),
    Reject(
        "single_value with statements",
        plain_mcq_document,
        put("mcq", "statements", value=[line(text("first")), line(text("second"))]),
        "others none",
    ),
    Reject(
        "figure_options with statements",
        figure_options_mcq_document,
        put("mcq", "statements", value=[line(text("first")), line(text("second"))]),
        "others none",
    ),
    Reject(
        "figure_options with column headers",
        figure_options_mcq_document,
        put("mcq", "column_headers", value=[line(text("Graph")), line(text("Shape"))]),
        "column headers",
    ),
    Reject(
        "figure_options option with two cells",
        figure_options_mcq_document,
        add(*OPTIONS, 0, "cells", value=line(text("rises"))),
        r"1 cell\(s\) for this layout",
    ),
    Reject(
        "two_column_table option with one cell",
        two_column_mcq_document,
        cut(*OPTIONS, 0, "cells"),
        r"2 cell\(s\) for this layout",
    ),
    Reject(
        "two_column_table option with three cells",
        two_column_mcq_document,
        add(*OPTIONS, 0, "cells", value=line(text("extra"))),
        r"mcq\.options\.0\.cells:|cell\(s\) for this layout",
    ),
    Reject(
        "two_column_table without column headers",
        two_column_mcq_document,
        drop("mcq", "column_headers"),
        "column headers",
    ),
    Reject(
        "two_column_table with one column header",
        two_column_mcq_document,
        cut("mcq", "column_headers"),
        "column headers",
    ),
    Reject(
        "two_column_table with three column headers",
        two_column_mcq_document,
        add("mcq", "column_headers", value=line(text("Power"))),
        "column headers",
    ),
    Reject(
        "two_column_table with statements",
        two_column_mcq_document,
        put("mcq", "statements", value=[line(text("first")), line(text("second"))]),
        "others none",
    ),
    Reject(
        "roman_statements with one statement",
        roman_mcq_document,
        both(cut("mcq", "statements"), cut("mcq", "statements")),
        "at least two statements",
    ),
    Reject(
        "roman_statements without statements",
        roman_mcq_document,
        drop("mcq", "statements"),
        "at least two statements",
    ),
    Reject(
        "roman_statements with column headers",
        roman_mcq_document,
        put("mcq", "column_headers", value=[line(text("first")), line(text("second"))]),
        "column headers",
    ),
    Reject(
        "roman_statements option with two cells",
        roman_mcq_document,
        add(*OPTIONS, 1, "cells", value=line(text("extra"))),
        r"1 cell\(s\) for this layout",
    ),
    Reject(
        "wrong option without rationale",
        plain_mcq_document,
        drop(*OPTIONS, 0, "rationale"),
        "wrong option A needs a rationale",
    ),
    Reject(
        "last wrong option without rationale",
        plain_mcq_document,
        drop(*OPTIONS, 3, "rationale"),
        "wrong option D needs a rationale",
    ),
    Reject(
        "wrong option with an empty rationale",
        plain_mcq_document,
        put(*OPTIONS, 1, "rationale", value=doc(paragraph())),
        "wrong option B needs a rationale",
    ),
    Reject(
        "changing the key leaves a wrong option without rationale",
        plain_mcq_document,
        put("mcq", "correct_key", value="A"),
        "wrong option C needs a rationale",
    ),
    Reject(
        "two identical options",
        plain_mcq_document,
        put(*OPTIONS, 0, "cells", value=[line(text("volume"))]),
        "identical",
    ),
    Reject(
        "two identical two-column options",
        two_column_mcq_document,
        put(*OPTIONS, 3, "cells", value=[line(math(r"\times 2")), line(math(r"\times 4"))]),
        "identical",
    ),
    Reject(
        "correct_key missing",
        plain_mcq_document,
        drop("mcq", "correct_key"),
        r"missing @ mcq\.correct_key:",
    ),
    Reject(
        "correct_key outside A-D",
        plain_mcq_document,
        put("mcq", "correct_key", value="E"),
        r"literal_error @ mcq\.correct_key:",
    ),
    Reject(
        "unknown level_content",
        plain_mcq_document,
        put("mcq", "level_content", value="hl"),
        r"enum @ mcq\.level_content:",
    ),
)
def test_mcq_rules(case: Reject) -> None:
    rejects(case.base, case.mutate, case.match)


@accepted(
    Accept("roman_statements with two statements", roman_mcq_document, cut("mcq", "statements")),
    Accept(
        "two-column options that share one column",
        two_column_mcq_document,
        put(*OPTIONS, 3, "cells", value=[line(math(r"\times 2")), line(math(r"\times 8"))]),
    ),
    Accept(
        "options that differ only in the unit",
        mcq_document,
        put(*OPTIONS, 1, "cells", value=[line(quantity("5.0", "km/s"))]),
    ),
    Accept("sl_core content", plain_mcq_document, put("mcq", "level_content", value="sl_core")),
)
def test_mcq_accepts(case: Accept) -> None:
    accepts(case.base, case.mutate)


def test_mcq_enumerations() -> None:
    assert set(permitted_values(plain_mcq_document, "mcq", "option_layout")) == {
        "single_value",
        "two_column_table",
        "figure_options",
        "roman_statements",
    }
    assert permitted_values(plain_mcq_document, "mcq", "correct_key") == ["A", "B", "C", "D"]
    assert set(permitted_values(plain_mcq_document, "mcq", "level_content")) == {"sl_core", "ahl"}


def test_option_kind_has_six_values_and_each_is_accepted() -> None:
    kinds = permitted_values(plain_mcq_document, "mcq", "option_kind")
    assert len(kinds) == len(set(kinds)) == 6
    for kind in kinds:
        data = plain_mcq_document()
        data["mcq"]["option_kind"] = kind
        assert dump(validate(data))["mcq"]["option_kind"] == kind


def test_two_column_options_with_column_headers() -> None:
    mcq = dump(validate(two_column_mcq_document()))["mcq"]
    assert mcq["option_layout"] == "two_column_table"
    assert len(mcq["column_headers"]) == 2
    assert [option["key"] for option in mcq["options"]] == ["A", "B", "C", "D"]
    assert all(len(option["cells"]) == 2 for option in mcq["options"])
    assert all(c["type"] == "doc" for option in mcq["options"] for c in option["cells"])


def test_roman_statement_options() -> None:
    mcq = dump(validate(roman_mcq_document()))["mcq"]
    assert mcq["option_layout"] == "roman_statements"
    assert len(mcq["statements"]) == 3
    assert all(len(option["cells"]) == 1 for option in mcq["options"])
    assert mcq["column_headers"] == []


def test_figure_placed_in_an_option_cell() -> None:
    mcq = dump(validate(figure_options_mcq_document()))["mcq"]
    placed = [option["cells"][0]["content"][0] for option in mcq["options"]]
    assert [node["type"] for node in placed] == ["figure"] * 4
    assert [node["attrs"]["stimulus_id"] for node in placed] == [
        "opt-a",
        "opt-b",
        "opt-c",
        "opt-d",
    ]


def test_mcq_bound_to_a_solution_step() -> None:
    document = validate(mcq_document())
    assert document.mcq is not None
    assert document.mcq.solution_step == "s2"
    assert document.mcq.correct_key == "A"
    assert document.parts == ()
    rejects(mcq_document, put("mcq", "solution_step", value="s9"), "unknown solution step s9")


def test_hl_only_question_with_additional_hl_content() -> None:
    document = validate(two_column_mcq_document())
    assert dump(document)["levels"] == ["hl"]
    assert dump(document)["mcq"]["level_content"] == "ahl"
    rejects(two_column_mcq_document, put("levels", value=["sl", "hl"]), "additional-HL")
    rejects(two_column_mcq_document, put("levels", value=["sl"]), "additional-HL")
    rejects(plain_mcq_document, put("mcq", "level_content", value="ahl"), "additional-HL")


# --- Parts -------------------------------------------------------------------------------------


def labelled(*labels: str) -> Json:
    return question(*[part(f"p{index}", label) for index, label in enumerate(labels)])


@pytest.mark.parametrize(
    "labels",
    [
        ["a"],
        ["z"],
        ["a", "b"],
        ["a", "b", "c"],
        ["b.ii"],
        ["a.i", "a.ii"],
        ["a.i", "a.ii", "a.iii", "a.iv", "a.v", "a.vi", "a.vii", "a.viii"],
        ["a.i", "a.ii", "b", "c.i", "c.ii"],
        ["a", "b.i", "b.ii", "c"],
    ],
    ids=" ".join,
)
def test_labels_accepted(labels: list[str]) -> None:
    document = validate(labelled(*labels))
    assert [p.label for p in document.parts] == labels


@pytest.mark.parametrize(
    "label",
    ["A", "aa", "1", "", "a.", "a.ix", "a.x", "a.iiii", "a.0", "a.1", "a.I", "a.i.i", "a i", "(a)"],
    ids=ascii,
)
def test_label_format_rejected(label: str) -> None:
    rejects(
        lambda: labelled("a"),
        put("parts", 0, "label", value=label),
        r"string_pattern_mismatch @ parts\.0\.label:",
    )


@pytest.mark.parametrize(
    ("good", "bad", "match"),
    [
        (["a", "b"], ["b", "a"], "unique and in order"),
        (["a", "b"], ["a", "a"], "unique and in order"),
        (["a.i", "a.ii"], ["a.ii", "a.i"], "unique and in order"),
        (["a.i", "a.ii"], ["a.i", "a.i"], "unique and in order"),
        (["a.iv", "a.v"], ["a.v", "a.iv"], "unique and in order"),
        (["a.i", "a.ii", "b"], ["a.i", "b", "a.ii"], "unique and in order"),
        (["a.i", "b.i"], ["b.i", "a.i"], "unique and in order"),
        (["a", "b.i"], ["a", "a.i"], "with and without sub-parts"),
        (["a.i", "b"], ["a.i", "a"], "sub-parts|unique and in order"),
    ],
    ids=lambda value: " ".join(value) if isinstance(value, list) else None,
)
def test_labels_are_unique_ordered_and_not_mixed(
    good: list[str], bad: list[str], match: str
) -> None:
    validate(labelled(*good))
    with pytest.raises(ValidationError) as caught:
        validate(labelled(*bad))
    lines = error_lines(caught.value)
    assert any(re.search(match, entry) for entry in lines), lines


ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"]


@st.composite
def ordered_labels(draw: st.DrawFn) -> list[str]:
    """Labels in the order of the spec: letters ascending, sub-parts ascending within a letter."""
    letters = sorted(draw(st.sets(st.sampled_from("abcdefghijklmnopqrstuvwxyz"), max_size=4)))
    labels: list[str] = []
    for letter in letters:
        subs = sorted(draw(st.sets(st.integers(min_value=0, max_value=7), max_size=3)))
        labels.extend(f"{letter}.{ROMAN[sub]}" for sub in subs)
        if not subs:
            labels.append(letter)
    assume(labels)
    return labels


@given(labels=ordered_labels())
def test_property_labels_in_order_are_accepted(labels: list[str]) -> None:
    document = validate(labelled(*labels))
    assert [p.label for p in document.parts] == labels
    assert document.model_dump_json() == validate(dump(document)).model_dump_json()


@given(data=st.data())
def test_property_labels_out_of_order_are_rejected(data: st.DataObject) -> None:
    labels = data.draw(ordered_labels())
    assume(len(labels) > 1)
    shuffled = data.draw(st.permutations(labels))
    assume(shuffled != labels)
    with pytest.raises(ValidationError, match="unique and in order"):
        validate(labelled(*shuffled))


@given(labels=ordered_labels(), data=st.data())
def test_property_a_repeated_label_is_rejected(labels: list[str], data: st.DataObject) -> None:
    repeated = data.draw(st.sampled_from(labels))
    position = labels.index(repeated)
    with pytest.raises(ValidationError, match="unique and in order"):
        validate(labelled(*labels[: position + 1], *labels[position:]))


def two_parts() -> Json:
    return question(
        part("p-a", "a", 2),
        part("p-b", "b", 1),
        secondary_syllabus_nodes=["B.3"],
        stimuli=[stimulus("fig-1")],
    )


def three_mark_part() -> Json:
    return question(part("p-a", "a", 3))


@rejected(
    Reject("part id repeated", two_parts, put("parts", 1, "id", value="p-a"), "duplicate part id"),
    Reject(
        "body with only an empty paragraph",
        two_parts,
        put("parts", 0, "body", value=doc(paragraph())),
        "part a: empty body",
    ),
    Reject(
        "body without blocks",
        two_parts,
        put("parts", 0, "body", "content", value=[]),
        r"too_short @ parts\.0\.body\.content:",
    ),
    Reject(
        "zero marks",
        two_parts,
        put("parts", 1, "marks", value=0),
        r"greater_than_equal @ parts\.1\.marks:",
    ),
    Reject(
        "four marks",
        three_mark_part,
        put("parts", 0, "marks", value=4),
        r"less_than_equal @ parts\.0\.marks:",
    ),
    Reject(
        "four marks with four mark points",
        three_mark_part,
        both(
            put("parts", 0, "marks", value=4),
            add("parts", 0, "mark_points", value=mark_point("p-a-m4")),
            put("total_marks", value=4),
        ),
        r"less_than_equal @ parts\.0\.marks:",
    ),
    Reject(
        "unknown answer_type",
        two_parts,
        put("parts", 0, "answer_type", value="doodle"),
        r"enum @ parts\.0\.answer_type:",
    ),
    Reject(
        "unknown level_content",
        two_parts,
        put("parts", 0, "level_content", value="hl"),
        r"enum @ parts\.0\.level_content:",
    ),
    Reject(
        "syllabus node not on the question",
        two_parts,
        put("parts", 0, "syllabus_node", value="D.1"),
        "part a: syllabus node is not listed",
    ),
    Reject(
        "depends_on a later part",
        two_parts,
        put("parts", 0, "depends_on", value=["p-b"]),
        "part a refers to p-b: not an earlier part",
    ),
    Reject(
        "depends_on itself",
        two_parts,
        put("parts", 1, "depends_on", value=["p-b"]),
        "part b refers to p-b: not an earlier part",
    ),
    Reject(
        "depends_on an unknown part",
        two_parts,
        put("parts", 1, "depends_on", value=["p-z"]),
        "part b refers to p-z",
    ),
    Reject(
        "depends_on repeats a part",
        two_parts,
        put("parts", 1, "depends_on", value=["p-a", "p-a"]),
        "part b: duplicate reference",
    ),
    Reject(
        "ecf_from a later part",
        two_parts,
        put("parts", 0, "ecf_from", value=["p-b"]),
        "part a refers to p-b: not an earlier part",
    ),
    Reject(
        "ecf_from itself",
        two_parts,
        put("parts", 1, "ecf_from", value=["p-b"]),
        "part b refers to p-b: not an earlier part",
    ),
    Reject(
        "ecf_from an unknown part",
        two_parts,
        put("parts", 1, "ecf_from", value=["p-z"]),
        "part b refers to p-z",
    ),
    Reject(
        "ecf_from repeats a part",
        two_parts,
        put("parts", 1, "ecf_from", value=["p-a", "p-a"]),
        "part b: duplicate reference",
    ),
    Reject(
        "additional-HL part in a question usable at SL",
        two_parts,
        put("parts", 1, "level_content", value="ahl"),
        "additional-HL",
    ),
)
def test_part_rules(case: Reject) -> None:
    rejects(case.base, case.mutate, case.match)


@accepted(
    Accept("three marks", three_mark_part, put("parts", 0, "command_term", value="outline")),
    Accept(
        "syllabus node from the secondary list",
        two_parts,
        put("parts", 0, "syllabus_node", value="B.3"),
    ),
    Accept("depends_on an earlier part", two_parts, put("parts", 1, "depends_on", value=["p-a"])),
    Accept("ecf_from an earlier part", two_parts, put("parts", 1, "ecf_from", value=["p-a"])),
    Accept("stimulus_refs", two_parts, put("parts", 0, "stimulus_refs", value=["fig-1"])),
    Accept(
        "additional-HL part in an HL-only question",
        two_parts,
        both(put("parts", 1, "level_content", value="ahl"), put("levels", value=["hl"])),
    ),
    Accept("sl_core part", two_parts, put("parts", 1, "level_content", value="sl_core")),
    Accept("show_that flag", two_parts, put("parts", 0, "show_that", value=True)),
    Accept(
        "lead_in",
        two_parts,
        put("parts", 1, "lead_in", value=line(text("The container is now heated."))),
    ),
)
def test_part_accepts(case: Accept) -> None:
    accepts(case.base, case.mutate)


@pytest.mark.parametrize("marks_value", [1, 2, 3])
def test_part_marks_from_one_to_three(marks_value: int) -> None:
    document = validate(question(part("p-a", "a", marks_value)))
    assert document.parts[0].marks == marks_value
    assert document.parts[0].awardable_marks == marks_value
    assert document.total_marks == marks_value


def test_answer_type_has_fourteen_values_and_each_is_accepted() -> None:
    answer_types = permitted_values(two_parts, "parts", 0, "answer_type")
    assert len(answer_types) == len(set(answer_types)) == 14
    for answer_type in answer_types:
        data = two_parts()
        data["parts"][0]["answer_type"] = answer_type
        assert dump(validate(data))["parts"][0]["answer_type"] == answer_type


def test_part_level_content_values() -> None:
    assert set(permitted_values(two_parts, "parts", 0, "level_content")) == {"sl_core", "ahl"}


def test_lead_in_is_kept_before_the_body() -> None:
    source = structured_document()
    second = dump(validate(source))["parts"][1]
    assert_contains(source["parts"][1]["lead_in"], second["lead_in"])
    assert second["lead_in"] != second["body"]
    assert dump(validate(source))["parts"][0]["lead_in"] is None


def test_hl_only_structured_question_with_additional_hl_parts() -> None:
    document = validate(show_that_document())
    assert dump(document)["levels"] == ["hl"]
    assert [p["level_content"] for p in dump(document)["parts"]][:2] == ["ahl", "ahl"]
    rejects(show_that_document, put("levels", value=["sl", "hl"]), "additional-HL")


# --- Markscheme --------------------------------------------------------------------------------

POINTS_A: tuple[Key, ...] = ("parts", 0, "mark_points")
POINTS_B: tuple[Key, ...] = ("parts", 1, "mark_points")


@rejected(
    Reject(
        "mark point id repeated in another part",
        two_parts,
        put(*POINTS_B, 0, "id", value="p-a-m1"),
        "duplicate mark point id",
    ),
    Reject(
        "mark point id repeated in the same part",
        two_parts,
        put(*POINTS_A, 1, "id", value="p-a-m1"),
        "duplicate mark point id",
    ),
    Reject(
        "unknown mark point kind",
        two_parts,
        put(*POINTS_A, 0, "kind", value="bonus"),
        r"enum @ parts\.0\.mark_points\.0\.kind:",
    ),
    Reject(
        "fewer mark points than marks",
        two_parts,
        cut(*POINTS_A),
        "part a: 1 awardable mark points for 2 marks",
    ),
    Reject(
        "more mark points than marks without a cap",
        two_parts,
        add(*POINTS_A, value=mark_point("p-a-m3")),
        "part a: 3 awardable mark points for 2 marks",
    ),
    Reject(
        "no mark points",
        two_parts,
        put(*POINTS_B, value=[]),
        r"too_short @ parts\.1\.mark_points:|part b: 0 awardable mark points",
    ),
    Reject(
        "capped with as many points as marks",
        two_parts,
        put("parts", 0, "marks_capped", value=True),
        "part a: capped but no more points than marks",
    ),
    Reject(
        "capped part loses its extra point",
        data_based_document,
        cut(*POINTS_A),
        "capped but no more points than marks",
    ),
    Reject(
        "capped part stops being capped",
        data_based_document,
        put("parts", 0, "marks_capped", value=False),
        "3 awardable mark points for 2 marks",
    ),
    Reject(
        "alternatives count once, leaving too few points",
        two_parts,
        both(
            put(*POINTS_A, 0, "alternative_group", value="g1"),
            put(*POINTS_A, 1, "alternative_group", value="g1"),
        ),
        "part a: 1 awardable mark points for 2 marks",
    ),
    Reject(
        "alternatives split into two groups count twice",
        show_that_document,
        put(*POINTS_A, 1, "alternative_group", value="g2"),
        "part a: 2 awardable mark points for 1 marks",
    ),
    Reject(
        "alternative loses its group",
        show_that_document,
        drop(*POINTS_A, 1, "alternative_group"),
        "part a: 2 awardable mark points for 1 marks",
    ),
    Reject(
        "a single route",
        two_parts,
        both(put(*POINTS_A, 0, "route", value="r1"), put(*POINTS_A, 1, "route", value="r1")),
        "single route",
    ),
    Reject(
        "a single route beside unrouted points",
        two_parts,
        put(*POINTS_A, 0, "route", value="r1"),
        "single route",
    ),
    Reject(
        "second route merged into the first",
        data_based_document,
        both(put(*POINTS_B, 2, "route", value="r1"), put(*POINTS_B, 3, "route", value="r1")),
        "single route",
    ),
    Reject(
        "routes are not added together",
        show_that_document,
        put("parts", 1, "marks_capped", value=True),
        "part b: capped but no more points than marks",
    ),
    Reject(
        "points common to both routes add to the best route",
        data_based_document,
        add(*POINTS_B, value=mark_point("aii-5")),
        "3 awardable mark points for 2 marks",
    ),
    Reject(
        "note tied to a mark point of another part",
        two_parts,
        put(
            "parts",
            0,
            "notes",
            value=[{"kind": "accept", "content": line(text("x")), "mark_point_id": "p-b-m1"}],
        ),
        "part a: note refers to an unknown mark point",
    ),
    Reject(
        "note tied to a mark point that does not exist",
        two_parts,
        put(
            "parts",
            0,
            "notes",
            value=[{"kind": "accept", "content": line(text("x")), "mark_point_id": "nope"}],
        ),
        "part a: note refers to an unknown mark point",
    ),
    Reject(
        "unknown note kind",
        show_that_document,
        put("parts", 1, "notes", 0, "kind", value="hint"),
        r"enum @ parts\.1\.notes\.0\.kind:",
    ),
)
def test_markscheme_rules(case: Reject) -> None:
    rejects(case.base, case.mutate, case.match)


def test_markscheme_enumerations() -> None:
    assert set(permitted_values(two_parts, *POINTS_A, 0, "kind")) == {
        "method",
        "answer",
        "statement",
    }
    assert set(permitted_values(show_that_document, "parts", 1, "notes", 0, "kind")) == {
        "general",
        "owtte",
        "accept",
        "do_not_accept",
        "cap",
        "ecf",
    }


@pytest.mark.parametrize("kind", ["method", "answer", "statement"])
def test_mark_point_kinds_accepted(kind: str) -> None:
    document = accepts(two_parts, put(*POINTS_A, 0, "kind", value=kind))
    assert dump(document)["parts"][0]["mark_points"][0]["kind"] == kind


@pytest.mark.parametrize("kind", ["general", "owtte", "accept", "do_not_accept", "cap", "ecf"])
def test_note_kinds_accepted(kind: str) -> None:
    note = {"kind": kind, "content": line(text("Marker guidance."))}
    document = accepts(two_parts, put("parts", 0, "notes", value=[note]))
    assert dump(document)["parts"][0]["notes"][0]["kind"] == kind
    assert dump(document)["parts"][0]["notes"][0]["mark_point_id"] is None


def test_note_tied_to_a_mark_point_of_its_own_part() -> None:
    document = validate(show_that_document())
    notes = dump(document)["parts"][1]["notes"]
    assert [note["mark_point_id"] for note in notes] == [None, "b-2"]
    assert "b-2" in [p["id"] for p in dump(document)["parts"][1]["mark_points"]]
    document = validate(structured_document())
    assert dump(document)["parts"][1]["notes"][1]["mark_point_id"] == "b-3"


def test_alternative_group_is_one_awardable_mark() -> None:
    document = validate(show_that_document())
    first = document.parts[0]
    assert first.marks == 1
    assert len(first.mark_points) == 2
    assert {p.alternative_group for p in first.mark_points} == {"g1"}
    assert first.awardable_marks == 1


def test_two_routes_of_two_marks_for_a_two_mark_part() -> None:
    for sample, index in ((data_based_document, 1), (show_that_document, 1)):
        routed = validate(sample()).parts[index]
        assert routed.marks == 2
        assert sorted(str(p.route) for p in routed.mark_points) == ["r1", "r1", "r2", "r2"]
        assert routed.awardable_marks == 2
        assert routed.marks_capped is False


def test_three_routes_are_allowed() -> None:
    third = both(
        add(*POINTS_B, value=mark_point("aii-5", route="r3")),
        add(*POINTS_B, value=mark_point("aii-6", route="r3")),
    )
    assert accepts(data_based_document, third).parts[1].awardable_marks == 2


def test_unrouted_points_add_to_the_best_route() -> None:
    def one_common_point(data: Json) -> None:
        points = data["parts"][1]["mark_points"]
        data["parts"][1]["mark_points"] = [points[0], points[2], mark_point("aii-5")]

    routed = accepts(data_based_document, one_common_point).parts[1]
    assert sorted(str(p.route) for p in routed.mark_points) == ["None", "r1", "r2"]
    assert routed.awardable_marks == 2


def test_alternative_group_inside_a_route_counts_once() -> None:
    grouped = both(
        put(*POINTS_B, 1, "alternative_group", value="g1"),
        add(*POINTS_B, value=mark_point("b-5", route="r1", alternative_group="g1")),
    )
    assert accepts(show_that_document, grouped).parts[1].awardable_marks == 2


def test_capped_part_has_more_awardable_marks_than_marks() -> None:
    for sample, index in ((data_based_document, 0), (show_that_document, 2)):
        capped = validate(sample()).parts[index]
        assert capped.marks_capped is True
        assert capped.marks == 2
        assert capped.awardable_marks == 3
    uncapped = validate(structured_document()).parts
    assert [(p.marks_capped, p.marks, p.awardable_marks) for p in uncapped] == [
        (False, 2, 2),
        (False, 3, 3),
    ]


def test_part_marks_add_up_to_the_total_even_when_capped() -> None:
    document = validate(show_that_document())
    assert [p.marks for p in document.parts] == [1, 2, 2]
    assert [p.awardable_marks for p in document.parts] == [1, 2, 3]
    assert document.total_marks == 5
    rejects(show_that_document, put("total_marks", value=6), "do not add up to total_marks")


def test_accept_range_is_kept_as_text() -> None:
    kept = dump(validate(structured_document()))["parts"][1]["mark_points"][2]["accept_range"]
    assert kept == {"minimum": "34", "maximum": "34.5", "unit": "m/s"}


@st.composite
def mark_schemes(draw: st.DrawFn) -> tuple[list[Json], int]:
    """Mark points for one part and the awardable marks the spec gives them.

    Awardable = unrouted points (each alternative group once) + the points of one route counted
    the same way. Every route is worth the same here, so "best route" is not in question.
    """
    counter = iter(range(1000))

    def points(free: int, groups: list[int], route: str | None, prefix: str) -> list[Json]:
        extra: Json = {"route": route} if route else {}
        made = [mark_point(f"m{next(counter)}", **extra) for _ in range(free)]
        for number, size in enumerate(groups):
            made.extend(
                mark_point(f"m{next(counter)}", alternative_group=f"{prefix}g{number}", **extra)
                for _ in range(size)
            )
        return made

    sizes = st.lists(st.integers(min_value=1, max_value=3), max_size=2)
    free = draw(st.integers(min_value=0, max_value=2))
    groups = draw(sizes)
    made = points(free, groups, None, "u")
    awardable = free + len(groups)
    route_count = draw(st.sampled_from([0, 2, 3]))
    if route_count:
        route_worth = draw(st.integers(min_value=1, max_value=2))
        for number in range(route_count):
            route_groups = draw(st.lists(st.integers(1, 3), max_size=route_worth))
            route_free = route_worth - len(route_groups)
            made.extend(points(route_free, route_groups, f"r{number}", f"r{number}"))
        awardable += route_worth
    assume(awardable >= 1)
    return draw(st.permutations(made)), awardable


@given(scheme=mark_schemes(), data=st.data())
def test_property_awardable_marks_decide_whether_a_part_is_valid(
    scheme: tuple[list[Json], int], data: st.DataObject
) -> None:
    points, awardable = scheme
    marks_value = data.draw(st.integers(min_value=1, max_value=3))
    capped = data.draw(st.booleans())
    source = question(part("p-a", "a", marks_value, mark_points=points, marks_capped=capped))
    valid = awardable > marks_value if capped else awardable == marks_value
    if valid:
        validated = validate(source).parts[0]
        assert validated.awardable_marks == awardable
    else:
        with pytest.raises(ValidationError, match="awardable mark points|capped but no more"):
            validate(source)


# --- Solution model ----------------------------------------------------------------------------

MODEL: tuple[Key, ...] = ("solution_model",)


def with_constant() -> Json:
    data = show_that_document()
    data["solution_model"]["constants"] = [{"name": "k", "ref": "data_booklet.k"}]
    return data


def unbound_question() -> Json:
    """A structured question with no solution model, no bound quantity and no step reference."""
    return question(
        part(
            "p-a",
            "a",
            body=line(text("State the pressure when the volume is "), quantity("2.0", "m^3")),
        ),
        stem=line(text("A gas is held at "), quantity("300", "K"), text(".")),
    )


@rejected(
    Reject(
        "two parameters share a name",
        show_that_document,
        add(*MODEL, "parameters", value={"name": "I", "value": "1", "unit": "kg"}),
        "duplicate parameter, constant or step name",
    ),
    Reject(
        "constant named like a parameter",
        with_constant,
        put(*MODEL, "constants", 0, "name", value="tau"),
        "duplicate parameter, constant or step name",
    ),
    Reject(
        "two constants share a name",
        with_constant,
        add(*MODEL, "constants", value={"name": "k", "ref": "data_booklet.other"}),
        "duplicate parameter, constant or step name",
    ),
    Reject(
        "step named like a parameter",
        show_that_document,
        put(*MODEL, "steps", 1, "name", value="tau"),
        "duplicate parameter, constant or step name",
    ),
    Reject(
        "step named like a constant",
        with_constant,
        put(*MODEL, "steps", 1, "name", value="k"),
        "duplicate parameter, constant or step name",
    ),
    Reject(
        "two steps share a name",
        show_that_document,
        put(*MODEL, "steps", 1, "name", value="alpha"),
        "duplicate parameter, constant or step name",
    ),
    Reject(
        "two steps share an id",
        show_that_document,
        add(*MODEL, "steps", value={"id": "s1", "name": "extra", "expr": "tau * t", "unit": "J"}),
        "duplicate step id",
    ),
    Reject(
        "two answer bindings for one part",
        show_that_document,
        add(*MODEL, "answers", value={"part_id": "p-a", "step": "s2"}),
        "more than one answer binding",
    ),
    Reject(
        "answer bound to an unknown part",
        show_that_document,
        put(*MODEL, "answers", 0, "part_id", value="p-z"),
        "answer bound to unknown part p-z",
    ),
    Reject(
        "answer bound to an unknown step",
        show_that_document,
        put(*MODEL, "answers", 0, "step", value="s9"),
        "answer bound to unknown step s9",
    ),
    Reject(
        "mark point bound to an unknown step",
        show_that_document,
        put(*POINTS_A, 0, "solution_step", value="s9"),
        "mark point a-1: unknown solution step s9",
    ),
    Reject(
        "mcq bound to an unknown step",
        mcq_document,
        put("mcq", "solution_step", value="s9"),
        "mcq: unknown solution step s9",
    ),
    Reject(
        "bound quantity differs in trailing zero (stem)",
        show_that_document,
        put(*MODEL, "parameters", 0, "value", value="0.4"),
        "parameter I differ in value or unit",
    ),
    Reject(
        "bound quantity is 20 where the parameter is 20.0 style (part body)",
        show_that_document,
        put(*MODEL, "parameters", 2, "value", value="5"),
        "parameter t differ in value or unit",
    ),
    Reject(
        "bound quantity differs in unit spelling",
        show_that_document,
        put(*MODEL, "parameters", 1, "unit", value="N*m"),
        "parameter tau differ in value or unit",
    ),
    Reject(
        "m/s is not m s^-1",
        structured_document,
        put(*MODEL, "parameters", 0, "unit", value="m s^-1"),
        "parameter u differ in value or unit",
    ),
    Reject(
        "equal numbers written differently",
        mcq_document,
        put(*MODEL, "parameters", 0, "value", value="6e+2"),
        "parameter d_east differ in value or unit",
    ),
    Reject(
        "quantity bound to a parameter that does not exist",
        show_that_document,
        put("stem", "content", 0, "content", 1, "attrs", "param", value="J"),
        "unknown parameter J",
    ),
    Reject(
        "parameter renamed away from its quantity",
        show_that_document,
        put(*MODEL, "parameters", 0, "name", value="J"),
        "unknown parameter I",
    ),
    Reject(
        "param in the stem without a solution model",
        unbound_question,
        put("stem", "content", 0, "content", 1, "attrs", "param", value="T"),
        "unknown parameter T",
    ),
    Reject(
        "param in a part body without a solution model",
        unbound_question,
        put("parts", 0, "body", "content", 0, "content", 1, "attrs", "param", value="V"),
        "unknown parameter V",
    ),
    Reject(
        "param in a mark point without a solution model",
        unbound_question,
        put(*POINTS_A, 0, "content", value=line(quantity("150", "kPa", "p"))),
        "unknown parameter p",
    ),
    Reject(
        "mark point solution_step without a solution model",
        unbound_question,
        put(*POINTS_A, 0, "solution_step", value="s1"),
        "mark point p-a-m1: unknown solution step s1",
    ),
    Reject(
        "mcq solution_step without a solution model",
        plain_mcq_document,
        put("mcq", "solution_step", value="s1"),
        "mcq: unknown solution step s1",
    ),
    Reject(
        "param in an option cell without a solution model",
        plain_mcq_document,
        put(*OPTIONS, 0, "cells", value=[line(quantity("2.0", "Pa", "p"))]),
        "unknown parameter p",
    ),
    Reject(
        "solution model removed from a bound multiple-choice question",
        mcq_document,
        drop("solution_model"),
        "unknown solution step|unknown parameter",
    ),
    Reject(
        "solution model removed from a bound structured question",
        structured_document,
        drop("solution_model"),
        "unknown solution step|unknown parameter",
    ),
)
def test_solution_model_rules(case: Reject) -> None:
    rejects(case.base, case.mutate, case.match)


@accepted(
    Accept(
        "a parameter no quantity is bound to",
        show_that_document,
        add(*MODEL, "parameters", value={"name": "m", "value": "1", "unit": "kg"}),
    ),
    Accept(
        "a constant with its own name",
        show_that_document,
        put(*MODEL, "constants", value=[{"name": "k", "ref": "data_booklet.k"}]),
    ),
    Accept(
        "a part without an answer binding", show_that_document, cut("solution_model", "answers")
    ),
    Accept(
        "unbound quantities need no solution model",
        unbound_question,
        put("outcome", value="gas laws"),
    ),
    Accept(
        "an unbound quantity may differ from every parameter",
        show_that_document,
        add("stem", "content", 0, "content", value=quantity("99", "N m")),
    ),
)
def test_solution_model_accepts(case: Accept) -> None:
    accepts(case.base, case.mutate)


def test_show_that_part_with_a_stated_value_step() -> None:
    document = validate(show_that_document())
    dumped = dump(document)
    assert dumped["parts"][0]["show_that"] is True
    assert dumped["parts"][1]["show_that"] is False
    steps = dumped["solution_model"]["steps"]
    assert [(step["id"], step["stated_value"]) for step in steps] == [("s1", "3"), ("s2", None)]
    assert {"part_id": "p-a", "step": "s1"} in dumped["solution_model"]["answers"]
    assert dumped["parts"][0]["mark_points"][0]["solution_step"] == "s1"


def test_solution_model_is_stored_as_data() -> None:
    source = structured_document()
    stored = dump(validate(source))["solution_model"]
    assert_contains(source["solution_model"], stored)
    assert [step["expr"] for step in stored["steps"]] == [
        "sqrt(2*H/g)",
        "g*t",
        "sqrt(u**2 + v_y**2)",
    ]
    assert stored["constants"] == [{"name": "g", "ref": "data_booklet.g"}]


def test_bound_quantities_match_their_parameters() -> None:
    for sample in (mcq_document, structured_document, show_that_document):
        document = validate(sample())
        parameters = {
            p["name"]: (p["value"], p["unit"])
            for p in dump(document)["solution_model"]["parameters"]
        }
        bound = [q for q in document.quantities() if q.attrs.param is not None]
        assert bound
        for node in bound:
            assert parameters[str(node.attrs.param)] == (node.attrs.value, node.attrs.unit)


# Bound quantities and node types in every place that holds a document


def with_length_parameter(data: Json) -> Json:
    data["solution_model"] = {"parameters": [{"name": "L", "value": "1.50", "unit": "m"}]}
    return data


def bound_gallery() -> Json:
    data = gallery_document()
    data["parts"][0]["lead_in"] = line(text("The ramp is now tilted further."))
    data["parts"][0]["notes"] = [
        {"kind": "general", "content": line(text("Accept reasoning in words."))}
    ]
    return with_length_parameter(data)


def bound_two_column() -> Json:
    return with_length_parameter(two_column_mcq_document())


def bound_roman() -> Json:
    return with_length_parameter(roman_mcq_document())


# (label, base, path of the node whose `content` takes one more paragraph)
PARAGRAPH_HOLDERS: list[tuple[str, Base, tuple[Key, ...]]] = [
    ("stem", bound_gallery, ("stem",)),
    ("table header cell", bound_gallery, (*TABLE, "content", 0, "content", 0)),
    ("table body cell", bound_gallery, (*TABLE, "content", 2, "content", 1)),
    ("bullet list item", bound_gallery, (*BULLETS, "content", 1)),
    ("ordered list item", bound_gallery, (*NUMBERED, "content", 0)),
    ("lead_in", bound_gallery, ("parts", 0, "lead_in")),
    ("part body", bound_gallery, ("parts", 0, "body")),
    ("mark point", bound_gallery, ("parts", 0, "mark_points", 0, "content")),
    ("note", bound_gallery, ("parts", 0, "notes", 0, "content")),
    ("column header", bound_two_column, ("mcq", "column_headers", 1)),
    ("option cell", bound_two_column, ("mcq", "options", 0, "cells", 1)),
    ("rationale", bound_two_column, ("mcq", "options", 0, "rationale")),
    ("explanation", bound_two_column, ("mcq", "explanation")),
    ("statement", bound_roman, ("mcq", "statements", 2)),
]
HOLDER_IDS = [label for label, _, _ in PARAGRAPH_HOLDERS]
HOLDER_ARGS = [(base, path) for _, base, path in PARAGRAPH_HOLDERS]


def one_more_paragraph(path: tuple[Key, ...], node: Json) -> Mutation:
    return add(*path, "content", value=paragraph(text("Length "), node))


@pytest.mark.parametrize(("base", "path"), HOLDER_ARGS, ids=HOLDER_IDS)
def test_bound_quantity_is_checked_wherever_it_stands(base: Base, path: tuple[Key, ...]) -> None:
    document = accepts(base, one_more_paragraph(path, quantity("1.50", "m", "L")))
    assert [q.attrs.value for q in document.quantities() if q.attrs.param == "L"] == ["1.50"]
    rejects(
        base,
        one_more_paragraph(path, quantity("1.5", "m", "L")),
        "parameter L differ in value or unit",
    )
    rejects(
        base,
        one_more_paragraph(path, quantity("1.50", "cm", "L")),
        "parameter L differ in value or unit",
    )
    rejects(base, one_more_paragraph(path, quantity("1.50", "m", "W")), "unknown parameter W")
    accepts(base, one_more_paragraph(path, quantity("1.5", "cm")))


@pytest.mark.parametrize(("base", "path"), HOLDER_ARGS, ids=HOLDER_IDS)
def test_param_without_a_solution_model_is_an_error_wherever_it_stands(
    base: Base, path: tuple[Key, ...]
) -> None:
    def unbound() -> Json:
        data = base()
        del data["solution_model"]
        return data

    rejects(unbound, one_more_paragraph(path, quantity("1.50", "m", "L")), "unknown parameter L")
    accepts(unbound, one_more_paragraph(path, quantity("1.50", "m")))


DOC_HOLDERS = [
    (label, base, path)
    for label, base, path in PARAGRAPH_HOLDERS
    if "cell" not in label.replace("option cell", "") and "item" not in label
]


@pytest.mark.parametrize(
    ("base", "path"),
    [(base, path) for _, base, path in DOC_HOLDERS],
    ids=[label for label, _, _ in DOC_HOLDERS],
)
def test_every_document_field_is_a_typed_doc_with_at_least_one_block(
    base: Base, path: tuple[Key, ...]
) -> None:
    where = r"\.".join(str(key) for key in path)
    rejects(base, drop(*path, "type"), rf"missing @ {where}\.type:")
    rejects(base, put(*path, "type", value="paragraph"), rf"literal_error @ {where}\.type:")
    rejects(base, put(*path, "content", value=[]), rf"too_short @ {where}\.content:")
    rejects(base, put(*path, "content", 0, "text", value="x"), r"extra_forbidden @ .*\.text:")


# --- Iterators ---------------------------------------------------------------------------------


class Tags:
    """Builds content with a distinct LaTeX source and quantity value for each place."""

    def __init__(self) -> None:
        self.latex: list[str] = []
        self.values: list[str] = []

    def inlines(self, place: str) -> list[Json]:
        source = rf"x_{{\text{{{place}}}}}"
        value = f"{len(self.values) + 1}.25"
        self.latex.append(source)
        self.values.append(value)
        return [text(f"{place}: "), math(source), text(" is "), quantity(value, "m")]

    def paragraph(self, place: str) -> Json:
        return paragraph(*self.inlines(place))

    def line(self, place: str) -> Json:
        return doc(self.paragraph(place))

    def display(self, place: str) -> Json:
        source = rf"y_{{\text{{{place}}}}} = 1"
        self.latex.append(source)
        return math_block(source)


def structured_with_math_everywhere(tags: Tags) -> Json:
    return question(
        part(
            "p-a",
            "a",
            lead_in=doc(tags.paragraph("lead-in"), tags.display("lead-in block")),
            body=doc(
                tags.paragraph("body"),
                tags.display("body block"),
                grid(row(cell(*tags.inlines("body table")))),
                bullet_list(list_item(tags.paragraph("body list"))),
            ),
            mark_points=[
                {
                    "id": "a-1",
                    "content": doc(tags.paragraph("mark point"), tags.display("mark point block")),
                    "alternative_group": "g",
                },
                {"id": "a-2", "content": tags.line("alternative"), "alternative_group": "g"},
            ],
            notes=[
                {"kind": "general", "content": tags.line("note")},
                {"kind": "accept", "content": tags.line("tied note"), "mark_point_id": "a-1"},
            ],
        ),
        part(
            "p-b",
            "b",
            2,
            body=tags.line("second body"),
            mark_points=[
                {"id": "b-1", "content": tags.line("route one first"), "route": "r1"},
                {"id": "b-2", "content": tags.line("route one second"), "route": "r1"},
                {"id": "b-3", "content": tags.line("route two first"), "route": "r2"},
                {"id": "b-4", "content": tags.line("route two second"), "route": "r2"},
            ],
        ),
        stem=doc(
            tags.paragraph("stem"),
            tags.display("stem block"),
            grid(
                row(
                    cell(*tags.inlines("header cell"), header=True),
                    cell(*tags.inlines("second header cell"), header=True),
                ),
                row(cell(*tags.inlines("body cell")), cell(*tags.inlines("second body cell"))),
            ),
            bullet_list(
                list_item(tags.paragraph("bullet item")),
                list_item(tags.paragraph("second bullet item"), tags.paragraph("its second line")),
            ),
            ordered_list(list_item(tags.paragraph("ordered item"))),
            tags.paragraph("last stem paragraph"),
        ),
    )


def mcq_with_math_everywhere(tags: Tags) -> Json:
    data = two_column_mcq_document()
    data["stem"] = doc(
        tags.paragraph("stem"),
        tags.display("stem block"),
        grid(row(cell(*tags.inlines("stem table")))),
        ordered_list(list_item(tags.paragraph("stem list"))),
    )
    data["mcq"]["column_headers"] = [tags.line("first header"), tags.line("second header")]
    data["mcq"]["explanation"] = doc(tags.paragraph("explanation"), tags.display("explained"))
    for option in data["mcq"]["options"]:
        key = option["key"]
        option["cells"] = [tags.line(f"option {key} left"), tags.line(f"option {key} right")]
        option["rationale"] = tags.line(f"rationale {key}")
    return data


def roman_with_math_everywhere(tags: Tags) -> Json:
    data = roman_mcq_document()
    data["mcq"]["statements"] = [tags.line(f"statement {n}") for n in ("I", "II", "III")]
    for option in data["mcq"]["options"]:
        option["cells"] = [tags.line(f"option {option['key']}")]
    return data


EVERYWHERE = [
    structured_with_math_everywhere,
    mcq_with_math_everywhere,
    roman_with_math_everywhere,
]


@pytest.mark.parametrize("build", EVERYWHERE)
def test_latex_sources_yields_every_math_node(build: Callable[[Tags], Json]) -> None:
    tags = Tags()
    document = validate(build(tags))
    found = list(document.latex_sources())
    missing = sorted(set(tags.latex) - set(found))
    assert not missing, missing
    assert sorted(found) == sorted(tags.latex)


@pytest.mark.parametrize("build", EVERYWHERE)
def test_quantities_yields_every_quantity_node(build: Callable[[Tags], Json]) -> None:
    tags = Tags()
    document = validate(build(tags))
    found = [node.attrs.value for node in document.quantities()]
    missing = sorted(set(tags.values) - set(found))
    assert not missing, missing
    assert sorted(found) == sorted(tags.values)
    assert all(node.attrs.unit == "m" for node in document.quantities())


def test_iterators_on_the_plain_samples() -> None:
    document = validate(data_based_document())
    assert sorted(document.latex_sources()) == sorted(
        [r"h = \tfrac{1}{2} g t^2", r"0.01 / 0.45", r"2 \times 2.2\,\%"]
    )
    assert sorted(node.attrs.value for node in document.quantities()) == [
        "0.20",
        "0.200",
        "0.45",
        "1.000",
    ]
    empty = validate(plain_mcq_document())
    assert list(empty.latex_sources()) == []
    assert list(empty.quantities()) == []


def test_iterators_keep_marked_nodes_and_uncertainties() -> None:
    document = validate(gallery_document())
    assert sorted(document.latex_sources()) == sorted([r"a = g \sin\theta", "g", "m"])
    described = sorted(
        (node.attrs.value, node.attrs.unit, node.attrs.uncertainty or "")
        for node in document.quantities()
    )
    assert described == sorted(
        [
            ("1.20", "kg", "0.01"),
            ("9.8", "m s^-2", ""),
            ("10", "°", ""),
            ("2.4", "s", "0.1"),
            ("20", "°", ""),
            ("1.7", "s", "0.1"),
            ("1.50", "m", ""),
        ]
    )


# --- Round trips through a Doc ------------------------------------------------------------------


@given(value=st.text(min_size=1))
def test_property_text_survives_a_doc_round_trip(value: str) -> None:
    first = Doc.model_validate(line(text("lead "), text(value))).model_dump_json()
    assert json.loads(first)["content"][0]["content"][1]["text"] == value
    again = Doc.model_validate_json(first)
    assert again.model_dump_json() == first
    assert again == Doc.model_validate(json.loads(first))


@given(value=st.text(min_size=1))
def test_property_latex_survives_a_doc_round_trip(value: str) -> None:
    source = doc(paragraph(text("lead "), math(value)), math_block(value))
    first = Doc.model_validate(source).model_dump_json()
    loaded = json.loads(first)
    assert loaded["content"][0]["content"][1]["attrs"]["latex"] == value
    assert loaded["content"][1]["attrs"]["latex"] == value
    assert Doc.model_validate_json(first).model_dump_json() == first


@given(
    names=st.lists(st.sampled_from(MARK_TYPES), unique=True, max_size=4),
    node=st.sampled_from(["text", "math_inline", "quantity"]),
)
def test_property_marks_are_accepted_exactly_when_compatible(names: list[str], node: str) -> None:
    plain = {"text": text("x"), "math_inline": math("x"), "quantity": quantity("1", "m")}[node]
    source = line(text("lead "), with_marks(plain, *names))
    clash = {"sub", "sup"} <= set(names) or {"optional", "essential"} <= set(names)
    if clash:
        with pytest.raises(ValidationError, match="mutually exclusive"):
            Doc.model_validate(source)
    else:
        kept = json.loads(Doc.model_validate(source).model_dump_json())
        assert kept["content"][0]["content"][1]["marks"] == marks(*names)


def test_doc_serialisation_shape() -> None:
    source = doc(
        paragraph(text("Speed "), with_marks(math("v"), "italic"), hard_break(), text("x", "sup")),
        math_block("v = u + at"),
    )
    validated = Doc.model_validate(source)
    assert_contains(source, json.loads(validated.model_dump_json()))
    assert validated.model_dump(mode="json") == json.loads(validated.model_dump_json())
    assert Doc.model_validate(reorder_keys(source)).model_dump_json() == validated.model_dump_json()
    with pytest.raises(ValidationError, match="frozen"):
        setattr(validated, "content", ())  # noqa: B010
    with pytest.raises(ValidationError, match="Extra inputs"):
        Doc.model_validate({**source, "attrs": {}})
    assert measured("1.0", "m", "0.1")["attrs"]["uncertainty"] == "0.1"
