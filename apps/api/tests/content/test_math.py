"""Save-time math check: the closed command list, node extraction, and the pinned KaTeX renderer.

Written from the docstrings and constants of qlab.content.math (commit 0ec1b26), CLAUDE.md rule 6
and docs/DATA_ARCHITECTURE.md section 3.4. The first part needs neither Node nor a database. Tests
marked `node` start the real renderer (`apps/api/katex`, `npm ci`); a missing Node is a failure.

The renderer keeps its answers for the life of the process, so every test that must reach the
renderer (or see it fail) uses a formula that is unique to that test.
"""

from __future__ import annotations

import json
import re
import socket
import threading
import uuid
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qlab.content import math as qmath
from qlab.content.math import (
    ALLOWED_COMMANDS,
    ALLOWED_ENVIRONMENTS,
    ALLOWED_ESCAPES,
    KATEX_VERSION,
    MAX_LATEX_LENGTH,
    MAX_MATH_NODES,
    MathNode,
    RendererUnavailable,
    check,
    disallowed,
    math_nodes,
    render_errors,
)
from qlab.content.schema import QuestionDocument
from tests.conftest import API_ROOT
from tests.content import samples
from tests.content.support import ALL_SAMPLES, Json, document

node = pytest.mark.node

KATEX_PACKAGE = API_ROOT / "katex"


def unique() -> str:
    """A formula nobody else renders: letters only, so it is valid LaTeX."""
    return "u" + "".join(chr(ord("a") + int(c, 16)) for c in uuid.uuid4().hex)


# =============================================================================================
# disallowed: the closed list (pure)
# =============================================================================================


@pytest.mark.parametrize("name", sorted(ALLOWED_COMMANDS))
def test_every_allowed_command_example_is_accepted(name: str) -> None:
    assert disallowed(ALLOWED_COMMANDS[name]) == []


@pytest.mark.parametrize("name", sorted(ALLOWED_ENVIRONMENTS))
def test_every_allowed_environment_example_is_accepted(name: str) -> None:
    assert disallowed(ALLOWED_ENVIRONMENTS[name]) == []


@pytest.mark.parametrize("name", sorted(ALLOWED_COMMANDS))
def test_every_allowed_command_is_named_by_its_own_example(name: str) -> None:
    assert rf"\{name}" in ALLOWED_COMMANDS[name]


@pytest.mark.parametrize("escape", sorted(ALLOWED_ESCAPES))
def test_every_allowed_escape_is_accepted(escape: str) -> None:
    assert disallowed("a\\" + escape + "b") == []


REFUSED = [
    (r"\href{http://example.org}{x}", r"\href"),
    (r"\url{http://example.org}", r"\url"),
    (r"\includegraphics{x}", r"\includegraphics"),
    (r"\htmlClass{c}{x}", r"\htmlClass"),
    (r"\def\a{b}", r"\def"),
    (r"\newcommand{\a}{b}", r"\newcommand"),
    (r"\gdef\a{b}", r"\gdef"),
    (r"\let\a=b", r"\let"),
    (r"\input{file}", r"\input"),
    (r"\catcode`\@=11", r"\catcode"),
    (r"\unknowncmd x", r"\unknowncmd"),
    (r"\begin{verbatim} x \end{verbatim}", "verbatim"),
    (r"\begin{} x \end{}", "(empty)"),
    ("x \\", "trailing backslash"),
    (r"a \@ b", r"\@"),
    ('a \\" b', '\\"'),
    ("a\x01b", "control character"),
    ("a\x00b", "control character"),
    ("a\x7fb" + "\x1f", "control character"),
    ("x" * (MAX_LATEX_LENGTH + 1), "longer than"),
]


@pytest.mark.parametrize(("latex", "item"), REFUSED, ids=[repr(r[0])[:30] for r in REFUSED])
def test_refused_input_is_named_in_the_result(latex: str, item: str) -> None:
    result = disallowed(latex)
    assert result, latex
    assert any(item in problem for problem in result), (item, result)


def test_exactly_the_maximum_length_is_fine_and_one_more_is_not() -> None:
    assert disallowed("x" * MAX_LATEX_LENGTH) == []
    too_long = disallowed("x" * (MAX_LATEX_LENGTH + 1))
    assert len(too_long) == 1 and str(MAX_LATEX_LENGTH) in too_long[0]


@pytest.mark.parametrize("latex", ["a\tb", "a\nb", "a\r\nb", "é in text? no, just accents é"])
def test_tab_newline_and_return_are_not_control_characters_and_text_is_not_policed(
    latex: str,
) -> None:
    assert not any("control" in p for p in disallowed(latex))


def test_a_command_name_is_matched_whole() -> None:
    assert disallowed(r"\sin x") == []
    refused = disallowed(r"\sinx")
    assert refused and any(r"\sinx" in p for p in refused)
    assert disallowed(r"\alpha2") == []  # digits end a command name
    assert disallowed(r"\alpha_1") == []


def test_command_names_are_case_sensitive() -> None:
    assert disallowed(r"\alpha") == []
    assert any(r"\Alpha" in p for p in disallowed(r"\Alpha"))
    assert any(r"\SIN" in p for p in disallowed(r"\SIN x"))
    assert disallowed(r"\Gamma") == [] and disallowed(r"\gamma") == []


def test_a_non_ascii_command_name_is_refused() -> None:
    assert disallowed("\\é") != []


def test_the_same_problem_is_reported_once() -> None:
    result = disallowed(r"\href{a}{b} \href{c}{d} \href{e}{f}")
    assert len(result) == 1
    assert len(disallowed(r"\foo \qux \foo")) == 2  # different problems stay separate


def test_an_escaped_backslash_does_not_start_a_command() -> None:
    assert disallowed(r"a \\ href") == []
    assert disallowed(r"a \\\\ b") == []


def test_environments_inside_other_text_are_still_checked() -> None:
    assert disallowed(r"\begin{aligned} \begin{weird} x \end{weird} \end{aligned}") != []
    assert disallowed(r"\begin {aligned} a \end {aligned}") == []


def test_empty_latex_has_nothing_to_refuse() -> None:
    assert disallowed("") == []


def accepted_scanner_problems(latex: str) -> list[str]:
    """An independent reading of LaTeX control sequences, to compare with `disallowed`."""
    problems: list[str] = []
    i = 0
    while i < len(latex):
        if latex[i] != "\\":
            i += 1
            continue
        j = i + 1
        if j < len(latex) and latex[j].isascii() and latex[j].isalpha():
            while j < len(latex) and latex[j].isascii() and latex[j].isalpha():
                j += 1
            name = latex[i + 1 : j]
            if name not in ALLOWED_COMMANDS:
                problems.append(name)
            i = j
        else:
            i = j + 1  # the backslash and the one character it escapes
    for match in re.finditer(r"\\(?:begin|end)\s*\{([^{}]*)\}", latex):
        if match.group(1) not in ALLOWED_ENVIRONMENTS:
            problems.append(match.group(1))
    return problems


FRAGMENTS = [
    "\\",
    "\\\\",
    "{",
    "}",
    "alpha",
    "sin",
    "foo",
    "href",
    "begin",
    "end",
    "aligned",
    "cases",
    "x",
    "y2",
    " ",
    "^",
    "_",
    "@",
    '"',
    "é",
    "\n",
]


@settings(max_examples=300, deadline=None)
@given(
    st.one_of(
        st.text(max_size=80),
        st.lists(st.sampled_from(FRAGMENTS), max_size=24).map("".join),
    )
)
def test_disallowed_never_raises_and_what_it_accepts_has_no_unlisted_command(
    latex: str,
) -> None:
    result = disallowed(latex)
    assert isinstance(result, list)
    assert len(result) == len(set(result))
    if not result:
        assert accepted_scanner_problems(latex) == [], latex


# =============================================================================================
# math_nodes (pure)
# =============================================================================================


def inline_math(latex: str) -> Json:
    return samples.paragraph(samples.math(latex))


def block_math(latex: str) -> Json:
    return samples.math_block(latex)


def doc_with(*blocks: Json) -> Json:
    return samples.doc(*blocks)


def test_math_nodes_cover_every_place_of_a_multiple_choice_question_in_reading_order() -> None:
    d = samples.two_column_mcq_document()
    d["stem"] = doc_with(inline_math("stem_i"), block_math("stem_b"))
    d["mcq"]["column_headers"] = [
        doc_with(inline_math("header1")),
        doc_with(inline_math("header2")),
    ]
    for option in d["mcq"]["options"]:
        option["cells"] = [
            doc_with(inline_math(f"cell_{option['key']}_1")),
            doc_with(inline_math(f"cell_{option['key']}_2")),
        ]
        option["rationale"] = doc_with(inline_math(f"why_{option['key']}"))
    d["mcq"]["explanation"] = doc_with(inline_math("explain"), block_math("explain_b"))

    found = [(n.latex, n.display) for n in math_nodes(document(d))]

    expected: list[tuple[str, bool]] = [("stem_b", True), ("stem_i", False)]
    expected += [("header1", False), ("header2", False)]
    for key in "ABCD":
        expected += [(f"cell_{key}_1", False), (f"cell_{key}_2", False), (f"why_{key}", False)]
    expected += [("explain_b", True), ("explain", False)]
    # Within one rich-text document the block-level nodes come first; documents keep their order.
    assert found == expected


def test_math_nodes_cover_every_place_of_a_structured_question() -> None:
    d = samples.question(
        samples.part(
            "p-a",
            "a",
            1,
            lead_in=doc_with(inline_math("lead")),
            body=doc_with(inline_math("body")),
            mark_points=[{"id": "a-1", "content": doc_with(inline_math("point1"))}],
            notes=[
                {"kind": "general", "content": doc_with(inline_math("note1"))},
                {"kind": "general", "content": doc_with(block_math("note2"))},
            ],
        ),
        samples.part(
            "p-b",
            "b",
            1,
            body=doc_with(block_math("b_body")),
            mark_points=[{"id": "b-1", "content": doc_with(inline_math("b_point"))}],
        ),
    )
    d["stem"] = doc_with(inline_math("stem"))

    found = [(n.latex, n.display) for n in math_nodes(document(d))]

    assert found == [
        ("stem", False),
        ("lead", False),
        ("body", False),
        ("point1", False),
        ("note1", False),
        ("note2", True),
        ("b_body", True),
        ("b_point", False),
    ]


def test_math_nodes_find_inline_math_in_lists_and_tables() -> None:
    d = samples.data_based_document()
    d["stem"] = samples.doc(
        samples.bullet_list(samples.list_item(inline_math("in_list"))),
        samples.grid(
            samples.row(samples.cell(samples.math("in_header"), header=True)),
            samples.row(samples.cell(samples.math("in_cell"))),
        ),
        samples.ordered_list(samples.list_item(inline_math("in_ordered"))),
    )
    found = {(n.latex, n.display) for n in math_nodes(document(d))}
    assert {
        ("in_list", False),
        ("in_header", False),
        ("in_cell", False),
        ("in_ordered", False),
    } <= (found)


def test_math_nodes_marks_inline_false_and_block_true() -> None:
    d = samples.data_based_document()
    d["stem"] = doc_with(inline_math("inl"), block_math("blk"))
    nodes = list(math_nodes(document(d)))
    by_latex = {n.latex: n.display for n in nodes if n.latex in ("inl", "blk")}
    assert by_latex == {"inl": False, "blk": True}
    assert all(isinstance(n, MathNode) for n in nodes)


def test_math_nodes_of_a_document_without_math_is_empty() -> None:
    assert list(math_nodes(document(samples.plain_mcq_document()))) == []


@pytest.mark.parametrize("name", list(ALL_SAMPLES))
def test_math_nodes_agree_with_the_schemas_own_latex_listing(name: str) -> None:
    doc = document(ALL_SAMPLES[name]())
    assert sorted(n.latex for n in math_nodes(doc)) == sorted(doc.latex_sources())
    assert all(isinstance(n.display, bool) for n in math_nodes(doc))


def test_the_same_latex_inline_and_as_a_block_are_different_nodes() -> None:
    assert MathNode("x", display=False) != MathNode("x", display=True)
    assert len({MathNode("x", display=False), MathNode("x", display=False)}) == 1


# =============================================================================================
# check without a renderer (pure: no formula reaches Node)
# =============================================================================================


def doc_with_math(*latex: str, block: bool = False) -> QuestionDocument:
    d = samples.data_based_document()
    d["stem"] = samples.doc(*[block_math(x) if block else inline_math(x) for x in latex])
    # drop other math so only the given formulas count
    for part in d["parts"]:
        part["body"] = samples.line(samples.text("Explain."))
        for point in part["mark_points"]:
            point["content"] = samples.line(samples.text("idea"))
    return document(d)


@pytest.fixture
def no_node(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QLAB_NODE_BIN", "no-such-node-binary-" + uuid.uuid4().hex)


def test_a_document_without_math_needs_no_renderer(no_node: None) -> None:
    assert check(document(samples.plain_mcq_document())) == ()
    assert render_errors([]) == []


def test_empty_input_does_not_start_a_process(no_node: None) -> None:
    assert render_errors([]) == []


def test_a_refused_command_is_reported_and_never_sent_to_the_renderer(no_node: None) -> None:
    problems = check(doc_with_math(r"\href{http://example.org}{click}"))
    assert len(problems) == 1
    assert r"\href" in problems[0] and "not allowed" in problems[0]
    assert r"\href{http://example.org}{click}" in problems[0]


def test_several_refused_nodes_are_each_reported_once(no_node: None) -> None:
    problems = check(doc_with_math(r"\def\a{b}", r"\input{f}", r"\def\a{b}"))
    assert len(problems) == 2
    assert all("not allowed" in p for p in problems)


def test_more_than_the_maximum_distinct_nodes_is_one_problem(no_node: None) -> None:
    formulas = [f"a{i}" for i in range(MAX_MATH_NODES + 1)]
    problems = check(doc_with_math(*formulas))
    assert len(problems) == 1
    assert str(MAX_MATH_NODES) in problems[0]


def test_duplicates_count_once_toward_the_maximum_and_in_the_report(no_node: None) -> None:
    problems = check(doc_with_math(*([r"\href{u}{v}"] * (MAX_MATH_NODES + 5))))
    assert len(problems) == 1 and "not allowed" in problems[0]


def test_a_long_refused_formula_is_quoted_shortened(no_node: None) -> None:
    long = r"\href{" + "x" * 300 + "}{y}"
    (problem,) = check(doc_with_math(long))
    assert long not in problem
    assert long[:40] in problem
    assert len(problem) < len(long)


# =============================================================================================
# The renderer (needs Node)
# =============================================================================================


def nodes(*latex: str, display: bool = False) -> list[MathNode]:
    return [MathNode(x, display=display) for x in latex]


@node
@pytest.mark.parametrize("display", [False, True], ids=["inline", "display"])
def test_every_allowed_example_renders_in_both_modes(display: bool) -> None:
    examples = {
        **{f"command {k}": v for k, v in ALLOWED_COMMANDS.items()},
        **{f"environment {k}": v for k, v in ALLOWED_ENVIRONMENTS.items()},
    }
    names = list(examples)
    errors = render_errors([MathNode(examples[n], display=display) for n in names])
    assert len(errors) == len(names)
    failing = {n: e for n, e in zip(names, errors, strict=True) if e is not None}
    assert failing == {}


@node
def test_every_allowed_escape_renders() -> None:
    latexes = ["a\\" + e + "b" for e in sorted(ALLOWED_ESCAPES)]
    assert render_errors(nodes(*latexes)) == [None] * len(latexes)


MALFORMED = [
    "x^",
    r"\frac{a}",
    "{x",
    "x}",
    r"\begin{aligned} a &= b",
    "é = mc^2",
    r"\left( x",
    "x_",
]


@node
@pytest.mark.parametrize("latex", MALFORMED)
def test_malformed_latex_gets_an_error_string(latex: str) -> None:
    (error,) = render_errors(nodes(latex))
    assert isinstance(error, str) and error


@node
def test_good_and_bad_nodes_are_answered_one_by_one_in_order() -> None:
    items = ["a + b", "x^", r"\frac{1}{2}", r"\frac{a}", "{x", r"\sin x", "x^"]
    result = render_errors(nodes(*items))
    assert [e is None for e in result] == [True, False, True, False, False, True, False]
    assert result[1] == result[6]  # duplicates are answered consistently


@node
def test_the_same_latex_is_asked_for_each_display_mode() -> None:
    result = render_errors([MathNode("a+b", display=False), MathNode("a+b", display=True)])
    assert result == [None, None]


@node
def test_repeated_requests_give_the_same_answer() -> None:
    first = render_errors(nodes("x^", "a+b"))
    second = render_errors(nodes("x^", "a+b"))
    assert first == second


@node
def test_a_large_batch_is_one_answer_per_node() -> None:
    latexes = [f"q_{i} + {i}" for i in range(500)]
    assert render_errors(nodes(*latexes)) == [None] * 500


@node
def test_the_pinned_version_is_the_installed_one() -> None:
    package = json.loads((KATEX_PACKAGE / "package.json").read_text())
    assert package["dependencies"]["katex"] == KATEX_VERSION
    installed = json.loads((KATEX_PACKAGE / "node_modules" / "katex" / "package.json").read_text())
    assert installed["version"] == KATEX_VERSION


def test_the_render_script_keeps_the_rendering_contract_options() -> None:
    script = (KATEX_PACKAGE / "render.mjs").read_text()
    assert re.search(r"trust:\s*false", script)
    assert re.search(r"strict:\s*\"error\"", script)
    assert re.search(r"throwOnError:\s*true", script)
    assert not re.search(r"trust:\s*true", script)


# --- check() on documents (needs Node) ----------------------------------------------------


@node
@pytest.mark.parametrize("name", list(ALL_SAMPLES))
def test_every_clean_sample_has_no_math_problems(name: str) -> None:
    assert check(document(ALL_SAMPLES[name]())) == ()


def add_math(target: Json, latex: str, *, block: bool = False) -> None:
    target["content"].append(block_math(latex) if block else inline_math(latex))


def locate_stem(d: Json, latex: str, block: bool) -> None:
    add_math(d["stem"], latex, block=block)


def locate_option_cell(d: Json, latex: str, block: bool) -> None:
    add_math(d["mcq"]["options"][0]["cells"][0], latex, block=block)


def locate_rationale(d: Json, latex: str, block: bool) -> None:
    add_math(d["mcq"]["options"][1]["rationale"], latex, block=block)


def locate_explanation(d: Json, latex: str, block: bool) -> None:
    add_math(d["mcq"]["explanation"], latex, block=block)


def locate_column_header(d: Json, latex: str, block: bool) -> None:
    add_math(d["mcq"]["column_headers"][0], latex, block=block)


def locate_statement(d: Json, latex: str, block: bool) -> None:
    add_math(d["mcq"]["statements"][0], latex, block=block)


def locate_lead_in(d: Json, latex: str, block: bool) -> None:
    add_math(d["parts"][1]["lead_in"], latex, block=block)


def locate_body(d: Json, latex: str, block: bool) -> None:
    add_math(d["parts"][0]["body"], latex, block=block)


def locate_mark_point(d: Json, latex: str, block: bool) -> None:
    add_math(d["parts"][0]["mark_points"][0]["content"], latex, block=block)


def locate_note(d: Json, latex: str, block: bool) -> None:
    add_math(d["parts"][1]["notes"][0]["content"], latex, block=block)


LOCATIONS: dict[str, tuple[Callable[[], Json], Callable[[Json, str, bool], None]]] = {
    "stem": (samples.mcq_document, locate_stem),
    "option_cell": (samples.mcq_document, locate_option_cell),
    "rationale": (samples.mcq_document, locate_rationale),
    "explanation": (samples.mcq_document, locate_explanation),
    "column_header": (samples.two_column_mcq_document, locate_column_header),
    "statement": (samples.roman_mcq_document, locate_statement),
    "lead_in": (samples.show_that_document, locate_lead_in),
    "body": (samples.show_that_document, locate_body),
    "mark_point": (samples.show_that_document, locate_mark_point),
    "note": (samples.show_that_document, locate_note),
}


@node
@pytest.mark.parametrize("block", [False, True], ids=["inline", "block"])
@pytest.mark.parametrize("location", list(LOCATIONS))
def test_a_formula_that_does_not_render_is_reported_once_wherever_it_is(
    location: str, block: bool
) -> None:
    build, put = LOCATIONS[location]
    bad = f"{unique()}^"
    d = build()
    put(d, bad, block)
    problems = check(document(d))
    assert len(problems) == 1, problems
    assert f"`{bad}`" in problems[0]
    assert "does not render" in problems[0]


@node
@pytest.mark.parametrize("location", list(LOCATIONS))
def test_a_refused_command_is_reported_wherever_it_is(location: str) -> None:
    build, put = LOCATIONS[location]
    bad = rf"{unique()} \href{{http://example.org}}{{x}}"
    d = build()
    put(d, bad, False)
    problems = check(document(d))
    assert len(problems) == 1, problems
    assert "not allowed" in problems[0] and r"\href" in problems[0]


@node
def test_the_same_bad_formula_in_two_places_is_one_problem() -> None:
    bad = f"{unique()}^"
    d = samples.show_that_document()
    locate_body(d, bad, False)
    locate_note(d, bad, False)
    locate_stem(d, bad, False)
    assert len(check(document(d))) == 1


@node
def test_a_good_and_a_bad_node_in_one_document_give_one_problem_for_the_bad_one() -> None:
    bad = f"{unique()}^"
    problems = check(doc_with_math(unique(), bad, unique()))
    assert len(problems) == 1 and bad in problems[0]


@node
def test_a_long_formula_that_does_not_render_is_quoted_shortened() -> None:
    long = unique() * 4 + "^"
    assert len(long) > 100
    (problem,) = check(doc_with_math(long))
    assert long not in problem
    assert long[:50] in problem


@node
def test_exactly_the_maximum_number_of_distinct_nodes_is_checked_not_refused() -> None:
    formulas = [f"{unique()[:6]}{i}" for i in range(MAX_MATH_NODES)]
    assert check(doc_with_math(*formulas)) == ()


@node
def test_a_document_mixing_refused_and_non_rendering_nodes_reports_both_kinds() -> None:
    refused = rf"{unique()} \input{{f}}"
    broken = f"{unique()}^"
    problems = check(doc_with_math(refused, broken))
    assert len(problems) == 2
    assert any("not allowed" in p for p in problems)
    assert any("does not render" in p for p in problems)


# =============================================================================================
# What happens when the renderer cannot run
# =============================================================================================


def fresh_node() -> list[MathNode]:
    return nodes(unique())


@node
def test_a_missing_node_binary_is_renderer_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QLAB_NODE_BIN", "no-such-node-binary-" + uuid.uuid4().hex)
    with pytest.raises(RendererUnavailable):
        render_errors(fresh_node())
    with pytest.raises(RendererUnavailable):
        check(doc_with_math(unique()))


@node
def test_an_unusable_node_binary_path_is_renderer_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    not_executable = tmp_path / "node"
    not_executable.write_text("#!/bin/sh\nexit 0\n")
    monkeypatch.setenv("QLAB_NODE_BIN", str(not_executable))
    with pytest.raises(RendererUnavailable):
        render_errors(fresh_node())


@node
def test_a_katex_directory_without_the_script_is_renderer_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QLAB_KATEX_DIR", str(tmp_path))
    with pytest.raises(RendererUnavailable):
        render_errors(fresh_node())


@node
def test_a_katex_directory_that_does_not_exist_is_renderer_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QLAB_KATEX_DIR", str(tmp_path / "nowhere"))
    with pytest.raises(RendererUnavailable):
        render_errors(fresh_node())


@node
def test_the_real_script_without_the_katex_package_is_renderer_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "render.mjs").write_text((KATEX_PACKAGE / "render.mjs").read_text())
    monkeypatch.setenv("QLAB_KATEX_DIR", str(tmp_path))
    with pytest.raises(RendererUnavailable):
        render_errors(fresh_node())


PRELUDE = """
let input = "";
for await (const chunk of process.stdin) input += chunk;
const { items } = JSON.parse(input);
const answer = (version, results) =>
  process.stdout.write(JSON.stringify({ version, results }));
"""


def fake_renderer(tmp_path: Path, body: str) -> Path:
    directory = tmp_path / "katex"
    directory.mkdir()
    (directory / "render.mjs").write_text(PRELUDE + body)
    return directory


FAKE_FAILURES = {
    "exits_non_zero": "process.exit(3);",
    "crashes": "throw new Error('boom');",
    "not_json": "process.stdout.write('hello');",
    "empty_output": "",
    "json_but_not_an_answer": "process.stdout.write(JSON.stringify([1, 2]));",
    "missing_results": f"process.stdout.write(JSON.stringify({{ version: '{KATEX_VERSION}' }}));",
    "results_not_a_list": (
        f"process.stdout.write(JSON.stringify({{ version: '{KATEX_VERSION}', results: 5 }}));"
    ),
    "result_without_ok": (f"answer('{KATEX_VERSION}', items.map(() => ({{ error: 'x' }})));"),
    "a_different_version": "answer('9.9.9', items.map(() => ({ ok: true })));",
    "no_version": (
        "process.stdout.write(JSON.stringify({ results: items.map(() => ({ ok: true })) }));"
    ),
    "too_few_results": f"answer('{KATEX_VERSION}', []);",
    "too_many_results": (
        f"answer('{KATEX_VERSION}', [...items, ...items].map(() => ({{ ok: true }})));"
    ),
}


@node
@pytest.mark.parametrize("failure", list(FAKE_FAILURES))
def test_a_renderer_that_misbehaves_is_renderer_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, failure: str
) -> None:
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, FAKE_FAILURES[failure])))
    with pytest.raises(RendererUnavailable):
        render_errors(fresh_node())


@node
def test_a_misbehaving_renderer_leaves_nothing_in_the_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    latex = unique()
    monkeypatch.setenv(
        "QLAB_KATEX_DIR", str(fake_renderer(tmp_path, FAKE_FAILURES["too_few_results"]))
    )
    with pytest.raises(RendererUnavailable):
        render_errors(nodes(latex))
    monkeypatch.delenv("QLAB_KATEX_DIR")
    assert render_errors(nodes(latex)) == [None]  # asked again, not remembered as a failure


@node
def test_a_fake_renderer_that_answers_correctly_is_accepted(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = (
        f"answer('{KATEX_VERSION}', items.map(({{ latex }}) => "
        "latex.endsWith('!') ? { ok: false, error: 'told so' } : { ok: true }));"
    )
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    good, bad = unique(), unique() + "!"
    assert render_errors(nodes(good, bad)) == [None, "told so"]


@node
def test_a_renderer_error_message_is_kept_as_text(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = f"answer('{KATEX_VERSION}', items.map(() => ({{ ok: false, error: 12345 }})));"
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    assert render_errors(fresh_node()) == ["12345"]


@node
def test_a_renderer_that_runs_past_the_time_limit_is_renderer_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = "await new Promise((resolve) => setTimeout(resolve, 60000));"
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    monkeypatch.setattr(qmath, "RENDER_TIMEOUT_SECONDS", 1)
    with pytest.raises(RendererUnavailable):
        render_errors(fresh_node())


@node
def test_the_time_limit_applies_to_a_busy_loop_too(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, "while (true) {}")))
    monkeypatch.setattr(qmath, "RENDER_TIMEOUT_SECONDS", 1)
    with pytest.raises(RendererUnavailable):
        render_errors(fresh_node())


@node
def test_latex_travels_on_stdin_and_never_on_the_command_line(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = (
        "const leaked = process.argv.slice(2).join(' ');\n"
        f"answer('{KATEX_VERSION}', items.map(({{ latex }}) => "
        "leaked.includes(latex) ? { ok: false, error: 'on the command line' } : { ok: true }));"
    )
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    secret = unique()
    assert render_errors(nodes(secret)) == [None]


# --- what the Node process may do ---------------------------------------------------------


@pytest.fixture
def listening_port() -> Iterator[int]:
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(5)
    stop = threading.Event()

    def accept() -> None:
        server.settimeout(0.2)
        while not stop.is_set():
            try:
                connection, _ = server.accept()
                connection.close()
            except OSError:
                continue

    thread = threading.Thread(target=accept, daemon=True)
    thread.start()
    try:
        yield int(server.getsockname()[1])
    finally:
        stop.set()
        thread.join(timeout=2)
        server.close()


def probe_script(action: str) -> str:
    """Try `action`; answer with a marker error that says whether it was allowed."""
    return f"""
import fs from "node:fs";
import net from "node:net";
import cp from "node:child_process";
let outcome;
try {{
  {action}
  outcome = "allowed";
}} catch (error) {{
  outcome = "denied " + (error.code ?? error.message);
}}
answer("{KATEX_VERSION}", items.map(() => ({{ ok: false, error: outcome }})));
"""


@node
def test_the_node_process_cannot_write_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = probe_script('fs.writeFileSync("./written-by-the-renderer.txt", "x");')
    directory = fake_renderer(tmp_path, body)
    monkeypatch.setenv("QLAB_KATEX_DIR", str(directory))
    (error,) = render_errors(fresh_node())
    assert error is not None and error.startswith("denied"), error
    assert not (directory / "written-by-the-renderer.txt").exists()
    assert list(tmp_path.glob("**/written-by-the-renderer.txt")) == []


@node
def test_the_node_process_cannot_create_a_directory_or_delete_its_own_script(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = probe_script('fs.mkdirSync("./made-by-the-renderer"); fs.unlinkSync("./render.mjs");')
    directory = fake_renderer(tmp_path, body)
    monkeypatch.setenv("QLAB_KATEX_DIR", str(directory))
    (error,) = render_errors(fresh_node())
    assert error is not None and error.startswith("denied"), error
    assert (directory / "render.mjs").exists()
    assert not (directory / "made-by-the-renderer").exists()


@node
def test_the_node_process_cannot_read_outside_the_katex_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("do not read")
    body = probe_script(f"fs.readFileSync({json.dumps(str(secret))}, 'utf8');")
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    (error,) = render_errors(fresh_node())
    assert error is not None and error.startswith("denied"), error


@node
def test_the_node_process_can_read_inside_the_katex_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = probe_script('fs.readFileSync("./render.mjs", "utf8");')
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    assert render_errors(fresh_node()) == ["allowed"]


@node
def test_the_node_process_cannot_start_another_program(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    marker = tmp_path / "spawned.txt"
    body = probe_script(f'cp.execSync("touch {marker}");')
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    (error,) = render_errors(fresh_node())
    assert error is not None and error.startswith("denied"), error
    assert not marker.exists()


@node
def test_the_node_process_cannot_open_the_network(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, listening_port: int
) -> None:
    body = f"""
import net from "node:net";
const outcome = await new Promise((resolve) => {{
  try {{
    const socket = net.connect({listening_port}, "127.0.0.1", () => {{
      socket.destroy();
      resolve("allowed");
    }});
    socket.on("error", (error) => resolve("denied " + (error.code ?? error.message)));
  }} catch (error) {{
    resolve("denied " + (error.code ?? error.message));
  }}
}});
answer("{KATEX_VERSION}", items.map(() => ({{ ok: false, error: outcome }})));
"""
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    (error,) = render_errors(fresh_node())
    assert error is not None and error.startswith("denied"), error


@node
def test_the_node_process_gets_no_secrets_from_the_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QLAB_TEST_SECRET_PROBE", "hunter2")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pw@host/db")
    body = (
        "const names = Object.keys(process.env).filter((n) => !['PATH', 'NODE_ENV'].includes(n));"
        f"answer('{KATEX_VERSION}', items.map(() => ({{ ok: false, error: names.join(',') }})));"
    )
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    (names,) = render_errors(fresh_node())
    assert names is not None
    leaked = {n for n in names.split(",") if n}
    assert "QLAB_TEST_SECRET_PROBE" not in leaked and "DATABASE_URL" not in leaked
    # only what the operating system itself adds to a new process (macOS: __CF_USER_TEXT_ENCODING)
    assert leaked <= {"__CF_USER_TEXT_ENCODING"}, leaked


@node
def test_the_node_process_runs_inside_the_katex_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = f"answer('{KATEX_VERSION}', items.map(() => ({{ ok: false, error: process.cwd() }})));"
    directory = fake_renderer(tmp_path, body)
    monkeypatch.setenv("QLAB_KATEX_DIR", str(directory))
    (error,) = render_errors(fresh_node())
    assert error is not None and Path(error).resolve() == directory.resolve()


def test_the_default_directory_is_the_one_in_the_repository() -> None:
    assert (KATEX_PACKAGE / "render.mjs").is_file()
    assert (KATEX_PACKAGE / "package.json").is_file()


def test_nothing_in_the_module_namespace_promises_more_than_the_contract() -> None:
    public = {n for n in vars(qmath) if not n.startswith("_")}
    for name in (
        "KATEX_VERSION",
        "MAX_LATEX_LENGTH",
        "MAX_MATH_NODES",
        "ALLOWED_COMMANDS",
        "ALLOWED_ENVIRONMENTS",
        "ALLOWED_ESCAPES",
        "MathNode",
        "math_nodes",
        "disallowed",
        "render_errors",
        "check",
        "RendererUnavailable",
    ):
        assert name in public
    assert qmath.KATEX_DIR_ENV == "QLAB_KATEX_DIR" and qmath.NODE_BIN_ENV == "QLAB_NODE_BIN"
    assert isinstance(qmath.RENDER_TIMEOUT_SECONDS, int)
    assert qmath.MAX_LATEX_LENGTH == 2000 and qmath.MAX_MATH_NODES == 2000
