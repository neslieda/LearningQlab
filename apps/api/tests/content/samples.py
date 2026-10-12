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


# --- Builders and samples added for the acceptance suite (test_question_schema.py) -------------


def with_marks(node: Json, *marks: str) -> Json:
    """A copy of an inline node carrying the given marks."""
    return {**node, "marks": [{"type": m} for m in marks]}


def measured(value: str, unit: str, uncertainty: str) -> Json:
    """A quantity with an absolute uncertainty."""
    return {
        "type": "quantity",
        "attrs": {"value": value, "unit": unit, "uncertainty": uncertainty},
    }


def hard_break() -> Json:
    return {"type": "hard_break"}


def math_block(latex: str) -> Json:
    return {"type": "math_block", "attrs": {"latex": latex}}


def cell(*inlines: Json, header: bool = False, **attrs: int) -> Json:
    """A table cell holding one paragraph; `colspan` / `rowspan` go to attrs."""
    node: Json = {
        "type": "table_header" if header else "table_cell",
        "content": [paragraph(*inlines)],
    }
    if attrs:
        node["attrs"] = dict(attrs)
    return node


def row(*cells: Json) -> Json:
    return {"type": "table_row", "content": list(cells)}


def grid(*rows: Json) -> Json:
    """A table built from explicit rows (use `table` for the simple header + body case)."""
    return {"type": "table", "content": list(rows)}


def list_item(*blocks: Json) -> Json:
    return {"type": "list_item", "content": list(blocks)}


def bullet_list(*items: Json) -> Json:
    return {"type": "bullet_list", "content": list(items)}


def ordered_list(*items: Json) -> Json:
    return {"type": "ordered_list", "content": list(items)}


def stimulus(stimulus_id: str, **extra: Any) -> Json:
    return {
        "id": stimulus_id,
        "kind": "graph",
        "description": "Straight line through the origin on unlabelled axes.",
        **extra,
    }


def mark_point(point_id: str, *inlines: Json, **extra: Any) -> Json:
    content = line(*inlines) if inlines else line(text(f"creditworthy idea {point_id}"))
    return {"id": point_id, "content": content, **extra}


def part(part_id: str, label: str, marks: int = 1, **extra: Any) -> Json:
    """A valid part worth `marks`, with one plain mark point per mark unless overridden."""
    node: Json = {
        "id": part_id,
        "label": label,
        "body": line(text(f"State one feature of situation {part_id}.")),
        "marks": marks,
        "answer_type": "word_phrase",
        "syllabus_node": "B.2",
        "mark_points": [mark_point(f"{part_id}-m{i}") for i in range(1, marks + 1)],
    }
    node.update(extra)
    return node


def question(*parts: Json, **extra: Any) -> Json:
    """A valid structured question without a solution model, built from the given parts."""
    node: Json = {
        "schema_version": "1.0",
        "question_class": "short_structured",
        "exam_section": "paper_2",
        "levels": ["sl", "hl"],
        "primary_syllabus_node": "B.2",
        "stem": line(text("A sealed container holds a fixed mass of gas.")),
        "parts": list(parts),
        "total_marks": sum(int(p["marks"]) for p in parts),
    }
    node.update(extra)
    return node


def plain_mcq_document() -> Json:
    """A word-phrase multiple-choice question with no solution model."""
    return {
        "schema_version": "1.0",
        "question_class": "mcq",
        "exam_section": "paper_1a",
        "levels": ["sl", "hl"],
        "primary_syllabus_node": "B.2",
        "stem": line(text("Which quantity stays constant when a sealed rigid flask is warmed?")),
        "mcq": {
            "option_kind": "word_phrase",
            "option_layout": "single_value",
            "correct_key": "C",
            "explanation": line(text("The flask is rigid, so the volume cannot change.")),
            "options": [
                {
                    "key": "A",
                    "cells": [line(text("pressure"))],
                    "rationale": line(text("Pressure rises with temperature.")),
                },
                {
                    "key": "B",
                    "cells": [line(text("mean molecular speed"))],
                    "rationale": line(text("Molecules move faster when warmer.")),
                },
                {"key": "C", "cells": [line(text("volume"))]},
                {
                    "key": "D",
                    "cells": [line(text("internal energy"))],
                    "rationale": line(text("Energy is transferred to the gas.")),
                },
            ],
        },
        "total_marks": 1,
    }


def two_column_mcq_document() -> Json:
    """HL-only question on additional-HL content; options are rows of a two-column table."""

    def option(key: str, omega: str, energy: str, why: str | None) -> Json:
        node: Json = {"key": key, "cells": [line(math(omega)), line(math(energy))]}
        if why:
            node["rationale"] = line(text(why))
        return node

    return {
        "schema_version": "1.0",
        "question_class": "mcq",
        "exam_section": "paper_1a",
        "levels": ["hl"],
        "primary_syllabus_node": "A.4",
        "stem": line(
            text("A flywheel doubles its angular speed "),
            math(r"\omega"),
            text(". What happens to its angular momentum and rotational kinetic energy?"),
        ),
        "mcq": {
            "option_kind": "ratio",
            "option_layout": "two_column_table",
            "column_headers": [line(text("Angular momentum")), line(text("Kinetic energy"))],
            "correct_key": "B",
            "level_content": "ahl",
            "assessment_objective": 2,
            "explanation": line(math(r"L = I\omega"), text(" and "), math(r"E = I\omega^2 / 2")),
            "options": [
                option("A", r"\times 2", r"\times 2", "Treats energy as linear in speed."),
                option("B", r"\times 2", r"\times 4", None),
                option("C", r"\times 4", r"\times 2", "Swaps the two dependences."),
                option("D", r"\times 4", r"\times 4", "Squares both."),
            ],
        },
        "total_marks": 1,
    }


def roman_mcq_document() -> Json:
    """Three roman-numeral statements; the options are combinations of them."""
    return {
        "schema_version": "1.0",
        "question_class": "mcq",
        "exam_section": "paper_1a",
        "levels": ["sl", "hl"],
        "primary_syllabus_node": "C.2",
        "stem": line(text("Which statements about a transverse pulse on a rope are correct?")),
        "mcq": {
            "option_kind": "statement",
            "option_layout": "roman_statements",
            "statements": [
                line(text("The rope moves at right angles to the pulse.")),
                line(text("The pulse carries energy along the rope.")),
                line(text("The rope ends up displaced along its length.")),
            ],
            "correct_key": "A",
            "explanation": line(text("Only the first two statements describe a transverse pulse.")),
            "options": [
                {"key": "A", "cells": [line(text("I and II only"))]},
                {
                    "key": "B",
                    "cells": [line(text("I and III only"))],
                    "rationale": line(text("The rope returns to where it started.")),
                },
                {
                    "key": "C",
                    "cells": [line(text("II and III only"))],
                    "rationale": line(text("Omits the defining property.")),
                },
                {
                    "key": "D",
                    "cells": [line(text("I, II and III"))],
                    "rationale": line(text("Statement III is false.")),
                },
            ],
        },
        "total_marks": 1,
    }


def figure_options_mcq_document() -> Json:
    """Each option is a figure placed in the option cell; every figure has an asset."""
    keys = ["A", "B", "C", "D"]
    shapes = ["rising line", "falling line", "horizontal line", "upward curve"]
    return {
        "schema_version": "1.0",
        "question_class": "mcq",
        "exam_section": "paper_1a",
        "levels": ["sl", "hl"],
        "primary_syllabus_node": "A.1",
        "stem": line(text("Which graph shows speed against time for a trolley at rest?")),
        "stimuli": [
            {
                "id": f"opt-{k.lower()}",
                "kind": "graph",
                "use": "read_only",
                "description": f"Speed-time axes with a {shape}.",
                "asset_id": f"asset-{k.lower()}",
                "alt_text": f"Graph: {shape}.",
            }
            for k, shape in zip(keys, shapes, strict=True)
        ],
        "mcq": {
            "option_kind": "figure_choice",
            "option_layout": "figure_options",
            "correct_key": "C",
            "explanation": line(text("At rest the speed is zero at all times.")),
            "options": [
                {
                    "key": k,
                    "cells": [doc(figure(f"opt-{k.lower()}"))],
                    **({} if k == "C" else {"rationale": line(text(f"Shows a {shape}."))}),
                }
                for k, shape in zip(keys, shapes, strict=True)
            ],
        },
        "total_marks": 1,
    }


def show_that_document() -> Json:
    """HL-only long question: show-that step, OR alternatives, two routes, a capped part, notes."""
    return {
        "schema_version": "1.0",
        "question_class": "long_structured",
        "exam_section": "paper_2",
        "levels": ["hl"],
        "language": "en",
        "calculator": True,
        "difficulty": "hard",
        "outcome": "rotational dynamics of a uniform disc",
        "primary_syllabus_node": "A.4",
        "secondary_syllabus_nodes": ["A.2", "A.3"],
        "stem": line(
            text("A uniform disc of moment of inertia "),
            quantity("0.40", "kg m^2", "I"),
            text(" is acted on by a constant torque of "),
            quantity("1.2", "N m", "tau"),
            text("."),
        ),
        "parts": [
            part(
                "p-a",
                "a",
                1,
                show_that=True,
                command_term="show",
                answer_type="derivation_numeric",
                level_content="ahl",
                syllabus_node="A.4",
                body=line(
                    text("Show that the angular acceleration is about "),
                    quantity("3", "rad/s^2"),
                    text("."),
                ),
                mark_points=[
                    mark_point(
                        "a-1",
                        math(r"\alpha = 1.2 / 0.40 = 3.0"),
                        kind="answer",
                        alternative_group="g1",
                        solution_step="s1",
                    ),
                    mark_point(
                        "a-2",
                        math(r"1.2 = 0.40 \alpha"),
                        text(" rearranged"),
                        kind="answer",
                        alternative_group="g1",
                    ),
                ],
            ),
            part(
                "p-b",
                "b",
                2,
                level_content="ahl",
                syllabus_node="A.4",
                depends_on=["p-a"],
                ecf_from=["p-a"],
                answer_type="numeric_with_unit",
                lead_in=line(text("The disc starts from rest.")),
                body=line(
                    text("Calculate the angular speed after "), quantity("5.0", "s", "t"), text(".")
                ),
                mark_points=[
                    mark_point("b-1", math(r"\omega = \alpha t"), kind="method", route="r1"),
                    mark_point(
                        "b-2",
                        quantity("15", "rad/s"),
                        kind="answer",
                        route="r1",
                        accept_range={"minimum": "14.5", "maximum": "15.5", "unit": "rad/s"},
                        solution_step="s2",
                    ),
                    mark_point("b-3", math(r"L = \tau t = 6.0"), kind="method", route="r2"),
                    mark_point("b-4", math(r"\omega = L / I = 15"), kind="answer", route="r2"),
                ],
                notes=[
                    {"kind": "ecf", "content": line(text("Allow ECF from (a)."))},
                    {
                        "kind": "do_not_accept",
                        "content": line(text("Do not accept an answer in degrees.")),
                        "mark_point_id": "b-2",
                    },
                ],
            ),
            part(
                "p-c",
                "c",
                2,
                marks_capped=True,
                syllabus_node="A.3",
                answer_type="explanation",
                body=line(text("Outline why the kinetic energy of the disc increases.")),
                mark_points=[
                    mark_point("c-1", text("the torque does work on the disc"), kind="statement"),
                    mark_point("c-2", text("work done equals torque times angle")),
                    mark_point("c-3", text("there are no resistive torques")),
                ],
                notes=[{"kind": "cap", "content": line(text("Maximum two marks."))}],
            ),
        ],
        "total_marks": 5,
        "solution_model": {
            "parameters": [
                {"name": "I", "value": "0.40", "unit": "kg m^2"},
                {"name": "tau", "value": "1.2", "unit": "N m"},
                {"name": "t", "value": "5.0", "unit": "s"},
            ],
            "steps": [
                {
                    "id": "s1",
                    "name": "alpha",
                    "expr": "tau / I",
                    "unit": "rad/s^2",
                    "stated_value": "3",
                },
                {"id": "s2", "name": "omega", "expr": "alpha * t", "unit": "rad/s"},
            ],
            "answers": [{"part_id": "p-a", "step": "s1"}, {"part_id": "p-b", "step": "s2"}],
        },
    }


def gallery_document() -> Json:
    """A structured question whose stem uses every node type; indices are relied on by tests.

    Stem blocks: 0 paragraph, 1 math_block, 2 table, 3 bullet_list, 4 ordered_list, 5 figure.
    Paragraph inlines: 0 text, 1 quantity with uncertainty, 2 text, 3 hard_break, 4 marked text,
    5 text, 6 marked math_inline, 7 text, 8 marked quantity, 9 text.
    """
    return question(
        part("p-a", "a", stimulus_refs=["ramp"]),
        stimuli=[stimulus("ramp", kind="schematic_diagram", use="read_only")],
        stem=doc(
            paragraph(
                text("A cart of mass "),
                measured("1.20", "kg", "0.01"),
                text(" rolls from rest down a straight ramp."),
                hard_break(),
                text("Friction", "bold", "italic"),
                text(" is negligible; take "),
                with_marks(math("g"), "italic"),
                text(" as "),
                quantity("9.8", "m s^-2", None, "essential"),
                text("."),
            ),
            math_block(r"a = g \sin\theta"),
            grid(
                row(cell(text("Trial data"), header=True, colspan=2)),
                row(cell(text("angle / °"), header=True), cell(text("time / s"), header=True)),
                row(cell(quantity("10", "°")), cell(measured("2.4", "s", "0.1"))),
                row(cell(quantity("20", "°")), cell(measured("1.7", "s", "0.1"))),
            ),
            bullet_list(
                list_item(paragraph(text("The ramp is rigid."))),
                list_item(paragraph(text("The cart is a point mass.")), paragraph(math("m"))),
            ),
            ordered_list(
                list_item(paragraph(text("Release the cart."))),
                list_item(paragraph(text("Time it over "), quantity("1.50", "m"), text("."))),
            ),
            figure("ramp"),
        ),
    )
