"""Synthetic question documents used across content tests. Never real exam questions."""

from typing import Any


def text(value: str) -> dict[str, Any]:
    return {"type": "text", "text": value}


def math(latex: str) -> dict[str, Any]:
    return {"type": "math_inline", "attrs": {"latex": latex}}


def quantity(value: str, unit: str, param: str | None = None) -> dict[str, Any]:
    attrs: dict[str, Any] = {"value": value, "unit": unit}
    if param:
        attrs["param"] = param
    return {"type": "quantity", "attrs": attrs}


def paragraph(*inlines: dict[str, Any]) -> dict[str, Any]:
    return {"type": "paragraph", "content": list(inlines)}


def doc(*blocks: dict[str, Any]) -> dict[str, Any]:
    return {"type": "doc", "content": list(blocks)}


def mcq_document() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "question_class": "mcq",
        "exam_section": "paper_1a",
        "levels": ["sl", "hl"],
        "primary_syllabus_node": "A.1",
        "stem": doc(
            paragraph(
                text("A cyclist rides "),
                quantity("600", "m"),
                text(" due east in "),
                quantity("60", "s"),
                text(" and then "),
                quantity("800", "m"),
                text(" due north in "),
                quantity("140", "s"),
                text("."),
            ),
            paragraph(text("What is the magnitude of the average velocity of the cyclist?")),
        ),
        "mcq": {
            "option_kind": "numeric_with_unit",
            "correct_key": "A",
            "options": [
                {"key": "A", "content": [quantity("5.0", "m/s")]},
                {"key": "B", "content": [quantity("7.0", "m/s")], "rationale": "total distance"},
                {"key": "C", "content": [quantity("7.9", "m/s")], "rationale": "mean of speeds"},
                {"key": "D", "content": [quantity("10", "m/s")], "rationale": "first leg only"},
            ],
        },
        "total_marks": 1,
    }


def structured_document() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "question_class": "short_structured",
        "exam_section": "paper_2",
        "levels": ["sl", "hl"],
        "primary_syllabus_node": "A.1",
        "stem": doc(
            paragraph(
                text("A drone flies horizontally at "),
                quantity("18", "m/s", "u"),
                text(" at a height of "),
                quantity("44", "m", "H"),
                text(" above level ground. It releases a small package."),
            ),
            {"type": "figure", "attrs": {"stimulus_id": "fig-1"}},
        ),
        "stimuli": [
            {
                "id": "fig-1",
                "kind": "schematic_diagram",
                "description": "Drone moving right above level ground, package below it.",
            }
        ],
        "parts": [
            {
                "id": "p-a",
                "label": "a",
                "body": doc(paragraph(text("Calculate the time taken to reach the ground."))),
                "marks": 2,
                "command_term": "calculate",
                "answer_type": "numeric_with_unit",
                "assessment_objective": 2,
                "syllabus_node": "A.1",
                "stimulus_refs": ["fig-1"],
                "mark_points": [
                    {
                        "id": "a-1",
                        "kind": "method",
                        "content": [math(r"44 = \tfrac{1}{2} \times 9.8 t^2")],
                    },
                    {
                        "id": "a-2",
                        "kind": "answer",
                        "content": [quantity("3.0", "s")],
                        "solution_step": "s1",
                    },
                ],
            },
            {
                "id": "p-b",
                "label": "b",
                "body": doc(paragraph(text("Determine the speed of the package at the ground."))),
                "marks": 3,
                "command_term": "determine",
                "answer_type": "numeric_with_unit",
                "assessment_objective": 3,
                "syllabus_node": "A.1",
                "depends_on": ["p-a"],
                "ecf_from": ["p-a"],
                "mark_points": [
                    {"id": "b-1", "kind": "method", "content": [math(r"v_y = 9.8 \times 3.0")]},
                    {"id": "b-2", "kind": "method", "content": [math(r"v = \sqrt{18^2 + 29^2}")]},
                    {
                        "id": "b-3",
                        "kind": "answer",
                        "content": [quantity("34", "m/s")],
                        "accept_range": {"minimum": 34.0, "maximum": 34.5, "unit": "m/s"},
                        "solution_step": "s3",
                    },
                ],
            },
        ],
        "total_marks": 5,
        "solution_model": {
            "parameters": [
                {"name": "u", "value": "18", "unit": "m/s"},
                {"name": "H", "value": "44", "unit": "m"},
            ],
            "constants": [{"name": "g", "ref": "data_booklet.g"}],
            "steps": [
                {"id": "s1", "name": "t", "expr": "sqrt(2*H/g)", "unit": "s"},
                {"id": "s2", "name": "v_y", "expr": "g*t", "unit": "m/s"},
                {"id": "s3", "name": "v", "expr": "sqrt(u**2 + v_y**2)", "unit": "m/s"},
            ],
            "answers": [{"part_id": "p-a", "step": "s1"}, {"part_id": "p-b", "step": "s3"}],
        },
    }
