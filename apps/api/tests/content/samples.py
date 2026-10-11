"""Synthetic question documents used across content tests. Never real exam questions."""

from typing import Any

Json = dict[str, Any]


def text(value: str, *marks: str) -> Json:
    node: Json = {"type": "text", "text": value}
    if marks:
        node["marks"] = [{"type": m} for m in marks]
    return node


def math(latex: str) -> Json:
    return {"type": "math_inline", "attrs": {"latex": latex}}


def quantity(value: str, unit: str, param: str | None = None, *marks: str) -> Json:
    attrs: Json = {"value": value, "unit": unit}
    if param:
        attrs["param"] = param
    node: Json = {"type": "quantity", "attrs": attrs}
    if marks:
        node["marks"] = [{"type": m} for m in marks]
    return node


def paragraph(*inlines: Json) -> Json:
    return {"type": "paragraph", "content": list(inlines)}


def doc(*blocks: Json) -> Json:
    return {"type": "doc", "content": list(blocks)}


def line(*inlines: Json) -> Json:
    """A one-paragraph document."""
    return doc(paragraph(*inlines))


def figure(stimulus_id: str) -> Json:
    return {"type": "figure", "attrs": {"stimulus_id": stimulus_id}}


def table(header: list[Json], *rows: list[Json]) -> Json:
    def row(kind: str, cells: list[Json]) -> Json:
        return {
            "type": "table_row",
            "content": [{"type": kind, "content": [paragraph(c)]} for c in cells],
        }

    return {
        "type": "table",
        "content": [row("table_header", header), *[row("table_cell", r) for r in rows]],
    }


def mcq_document() -> Json:
    return {
        "schema_version": "1.0",
        "question_class": "mcq",
        "exam_section": "paper_1a",
        "levels": ["sl", "hl"],
        "difficulty": "easy",
        "primary_syllabus_node": "A.1",
        "outcome": "distance versus displacement; average velocity",
        "stem": doc(
            paragraph(
                text("A cyclist rides "),
                quantity("600", "m", "d_east"),
                text(" due east in "),
                quantity("60", "s", "t_east"),
                text(" and then "),
                quantity("800", "m", "d_north"),
                text(" due north in "),
                quantity("140", "s", "t_north"),
                text("."),
            ),
            paragraph(text("What is the magnitude of the average velocity of the cyclist?")),
        ),
        "mcq": {
            "option_kind": "numeric_with_unit",
            "option_layout": "single_value",
            "correct_key": "A",
            "assessment_objective": 2,
            "solution_step": "s2",
            "explanation": line(
                text("Displacement 1000 m in 200 s gives "), quantity("5.0", "m/s")
            ),
            "options": [
                {"key": "A", "cells": [line(quantity("5.0", "m/s"))]},
                {
                    "key": "B",
                    "cells": [line(quantity("7.0", "m/s"))],
                    "rationale": line(text("Uses total distance: "), math(r"1400 / 200")),
                },
                {
                    "key": "C",
                    "cells": [line(quantity("7.9", "m/s"))],
                    "rationale": line(text("Averages the two speeds.")),
                },
                {
                    "key": "D",
                    "cells": [line(quantity("10", "m/s"))],
                    "rationale": line(text("Uses the first leg only.")),
                },
            ],
        },
        "total_marks": 1,
        "solution_model": {
            "parameters": [
                {"name": "d_east", "value": "600", "unit": "m"},
                {"name": "t_east", "value": "60", "unit": "s"},
                {"name": "d_north", "value": "800", "unit": "m"},
                {"name": "t_north", "value": "140", "unit": "s"},
            ],
            "steps": [
                {"id": "s1", "name": "s", "expr": "sqrt(d_east**2 + d_north**2)", "unit": "m"},
                {"id": "s2", "name": "v", "expr": "s / (t_east + t_north)", "unit": "m/s"},
            ],
        },
    }


def structured_document() -> Json:
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
            figure("fig-1"),
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
                "body": line(text("Calculate the time taken to reach the ground.")),
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
                        "content": line(math(r"44 = \tfrac{1}{2} \times 9.8 t^2")),
                    },
                    {
                        "id": "a-2",
                        "kind": "answer",
                        "content": line(math("t ="), quantity("3.0", "s", None, "optional")),
                        "solution_step": "s1",
                    },
                ],
            },
            {
                "id": "p-b",
                "label": "b",
                "lead_in": line(text("Air resistance is negligible.")),
                "body": line(text("Determine the speed of the package at the ground.")),
                "marks": 3,
                "command_term": "determine",
                "answer_type": "numeric_with_unit",
                "assessment_objective": 3,
                "syllabus_node": "A.1",
                "depends_on": ["p-a"],
                "ecf_from": ["p-a"],
                "mark_points": [
                    {"id": "b-1", "kind": "method", "content": line(math(r"v_y = 9.8 \times 3.0"))},
                    {
                        "id": "b-2",
                        "kind": "method",
                        "content": line(math(r"v = \sqrt{18^2 + 29^2}")),
                    },
                    {
                        "id": "b-3",
                        "kind": "answer",
                        "content": line(quantity("34", "m/s")),
                        "accept_range": {"minimum": "34", "maximum": "34.5", "unit": "m/s"},
                        "solution_step": "s3",
                    },
                ],
                "notes": [
                    {"kind": "ecf", "content": line(text("Allow ECF from (a)."))},
                    {
                        "kind": "accept",
                        "content": line(text("Accept 35 from "), math("g = 10")),
                        "mark_point_id": "b-3",
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


def data_based_document() -> Json:
    """A data-based question with a table, a list, a display equation and sub-parts."""
    return {
        "schema_version": "1.0",
        "question_class": "data_based",
        "exam_section": "paper_1b",
        "levels": ["sl", "hl"],
        "primary_syllabus_node": "A.1",
        "stem": doc(
            paragraph(text("A student times a ball falling from different heights.")),
            table(
                [text("h / m"), text("t / s ± 0.01 s")],
                [quantity("0.200", "m"), quantity("0.20", "s")],
                [quantity("1.000", "m"), quantity("0.45", "s")],
            ),
            {"type": "math_block", "attrs": {"latex": r"h = \tfrac{1}{2} g t^2"}},
            {
                "type": "bullet_list",
                "content": [
                    {
                        "type": "list_item",
                        "content": [paragraph(text("The ball starts from rest."))],
                    },
                    {
                        "type": "list_item",
                        "content": [paragraph(text("The uncertainty in h is negligible."))],
                    },
                ],
            },
        ),
        "parts": [
            {
                "id": "p-a-i",
                "label": "a.i",
                "body": line(text("Outline why a graph of h against t² is a straight line.")),
                "marks": 2,
                "marks_capped": True,
                "command_term": "outline",
                "answer_type": "explanation",
                "syllabus_node": "A.1",
                "mark_points": [
                    {"id": "ai-1", "content": line(text("h is proportional to t²"))},
                    {"id": "ai-2", "content": line(text("the ball starts from rest"))},
                    {"id": "ai-3", "content": line(text("the gradient is g/2"))},
                ],
            },
            {
                "id": "p-a-ii",
                "label": "a.ii",
                "body": line(text("Calculate the percentage uncertainty in t² for the last row.")),
                "marks": 2,
                "command_term": "calculate",
                "answer_type": "numeric_unitless",
                "syllabus_node": "A.1",
                "mark_points": [
                    {"id": "aii-1", "route": "r1", "content": line(math(r"0.01 / 0.45"))},
                    {"id": "aii-2", "route": "r1", "content": line(text("4.4 %"))},
                    {"id": "aii-3", "route": "r2", "content": line(math(r"2 \times 2.2\,\%"))},
                    {"id": "aii-4", "route": "r2", "content": line(text("4.4 %"))},
                ],
            },
        ],
        "total_marks": 4,
    }
