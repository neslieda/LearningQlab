import copy
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from qlab.content.schema import Doc, QuestionDocument, Text
from tests.content.samples import mcq_document, paragraph, structured_document, text


def test_valid_mcq_document() -> None:
    document = QuestionDocument.model_validate(mcq_document())
    assert document.total_marks == 1
    assert not document.visual_pending
    assert len(list(document.quantities())) == 8


def test_valid_structured_document() -> None:
    document = QuestionDocument.model_validate(structured_document())
    assert [p.marks for p in document.parts] == [2, 3]
    assert document.visual_pending  # the stimulus has no asset yet
    assert len(list(document.latex_sources())) == 3


@pytest.mark.parametrize("sample", [mcq_document, structured_document])
def test_json_round_trip(sample: Any) -> None:
    document = QuestionDocument.model_validate(sample())
    again = QuestionDocument.model_validate_json(document.model_dump_json())
    assert again == document


def _mcq(change: Any) -> dict[str, Any]:
    data = copy.deepcopy(mcq_document())
    change(data)
    return data


def _structured(change: Any) -> dict[str, Any]:
    data = copy.deepcopy(structured_document())
    change(data)
    return data


def _set(path: list[Any], value: Any) -> Any:
    def change(data: dict[str, Any]) -> None:
        target: Any = data
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value

    return change


def _delete(path: list[Any]) -> Any:
    def change(data: dict[str, Any]) -> None:
        target: Any = data
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]

    return change


INVALID = {
    "mcq with two marks": _mcq(_set(["total_marks"], 2)),
    "mcq with three options": _mcq(_delete(["mcq", "options", 3])),
    "mcq options out of order": _mcq(_set(["mcq", "options", 0, "key"], "B")),
    "mcq wrong option without rationale": _mcq(_delete(["mcq", "options", 1, "rationale"])),
    "mcq with parts": _mcq(_set(["parts"], structured_document()["parts"])),
    "mcq without mcq block": _mcq(_delete(["mcq"])),
    "no levels": _mcq(_set(["levels"], [])),
    "unknown field": _mcq(_set(["difficulty_guess"], 3)),
    "part with four marks": _structured(_set(["parts", 1, "marks"], 4)),
    "marks do not add up": _structured(_set(["total_marks"], 6)),
    "fewer mark points than marks": _structured(_delete(["parts", 1, "mark_points", 2])),
    "duplicate part label": _structured(_set(["parts", 1, "label"], "a")),
    "dependency on a later part": _structured(_set(["parts", 0, "depends_on"], ["p-b"])),
    "unknown stimulus reference": _structured(_set(["parts", 0, "stimulus_refs"], ["fig-9"])),
    "figure without stimulus": _structured(_set(["stimuli"], [])),
    "asset without alt text": _structured(_set(["stimuli", 0, "asset_id"], "ast_1")),
    "additional-HL part in an SL question": _structured(_set(["parts", 1, "level_content"], "ahl")),
    "quantity differs from parameter": _structured(
        _set(["solution_model", "parameters", 0, "value"], "25")
    ),
    "quantity bound to unknown parameter": _structured(
        _delete(["solution_model", "parameters", 1])
    ),
    "answer bound to unknown step": _structured(
        _set(["solution_model", "answers", 0, "step"], "s9")
    ),
    "mark point with unknown step": _structured(
        _set(["parts", 0, "mark_points", 1, "solution_step"], "s9")
    ),
    "accept range reversed": _structured(
        _set(["parts", 1, "mark_points", 2, "accept_range", "minimum"], 40.0)
    ),
    "structured with mcq block": _structured(_set(["mcq"], mcq_document()["mcq"])),
}


@pytest.mark.parametrize("name", sorted(INVALID))
def test_invalid_documents_are_rejected(name: str) -> None:
    with pytest.raises(ValidationError):
        QuestionDocument.model_validate(INVALID[name])


def test_alternative_mark_points_count_once() -> None:
    data = structured_document()
    points = data["parts"][0]["mark_points"]
    points[0]["alternative_group"] = "alt-1"
    points.append(
        {"id": "a-3", "content": [text("uses energy conservation")], "alternative_group": "alt-1"}
    )
    part = QuestionDocument.model_validate(data).parts[0]
    assert part.awardable_marks == 2


def test_more_mark_points_than_marks_is_allowed() -> None:
    data = structured_document()
    data["parts"][0]["mark_points"].append(
        {"id": "a-3", "content": [text("states initial vertical speed is zero")]}
    )
    part = QuestionDocument.model_validate(data).parts[0]
    assert part.awardable_marks == 3 and part.marks == 2


def test_ahl_part_allowed_when_question_is_hl_only() -> None:
    data = structured_document()
    data["levels"] = ["hl"]
    data["parts"][1]["level_content"] = "ahl"
    QuestionDocument.model_validate(data)


def test_stimulus_with_asset_and_alt_text_is_not_pending() -> None:
    data = structured_document()
    data["stimuli"][0].update({"asset_id": "ast_1", "alt_text": "Drone above level ground."})
    assert not QuestionDocument.model_validate(data).visual_pending


def test_quantity_value_keeps_significant_figures() -> None:
    data = mcq_document()
    data["mcq"]["options"][0]["content"][0]["attrs"]["value"] = "5.00"
    document = QuestionDocument.model_validate(data)
    assert document.mcq is not None
    first = document.mcq.options[0].content[0]
    assert first.type == "quantity" and first.attrs.value == "5.00"


@given(st.lists(st.text(min_size=1, max_size=40), min_size=0, max_size=5))
def test_doc_round_trip_preserves_text(values: list[str]) -> None:
    source = {"type": "doc", "content": [paragraph(*[text(v) for v in values])]}
    document = Doc.model_validate(source)
    again = Doc.model_validate_json(document.model_dump_json())
    assert again == document
    block = again.content[0]
    assert block.type == "paragraph"
    assert [i.text for i in block.content if isinstance(i, Text)] == values
