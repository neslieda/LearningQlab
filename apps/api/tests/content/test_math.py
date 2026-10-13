"""Save-time math check: the closed command list, node extraction, and the pinned KaTeX renderer.

Written from the docstrings and constants of qlab.content.math (commit 0ec1b26), CLAUDE.md rule 6
and docs/DATA_ARCHITECTURE.md section 3.4. The first part needs neither Node nor a database. Tests
marked `node` start the real renderer (`apps/api/katex`, `npm ci`); a missing Node is a failure.

The renderer keeps its answers for the life of the process, so every test that must reach the
renderer (or see it fail) uses a formula that is unique to that test.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import threading
import traceback
import uuid
from collections import Counter
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
    MAX_ALIGNMENT_TABS,
    MAX_GROUP_DEPTH,
    MAX_LATEX_LENGTH,
    MAX_LINE_BREAKS,
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


@pytest.fixture(autouse=True)
def clean_cache() -> Iterator[None]:
    """Answers are kept per process; every test here starts and ends with an empty cache so that
    what it asserts about the renderer is about the renderer, not about an earlier test."""
    qmath._CACHE.clear()
    yield
    qmath._CACHE.clear()


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
    ("a\x01b", "outside printable ASCII"),
    ("a\x00b", "outside printable ASCII"),
    ("a\x7fb" + "\x1f", "outside printable ASCII"),
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


@pytest.mark.parametrize(
    "latex", ["a\tb", "a\nb", "a\n\tb", " ~ ", "".join(map(chr, range(32, 127)))[:90]]
)
def test_tab_newline_and_printable_ascii_are_not_policed_as_characters(latex: str) -> None:
    assert not any("outside printable ASCII" in p for p in disallowed(latex))


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
    assert disallowed(r"\begin {aligned} a \end {aligned}") != []  # the name must follow directly


def test_empty_latex_has_nothing_to_refuse() -> None:
    assert disallowed("") == []


def lex_problems(latex: str) -> list[str]:
    r"""An independent reading of LaTeX control sequences, to compare with `disallowed`.

    The lexer is KaTeX's: "@" is a letter, a backslash takes the next character, `%` starts a
    comment, and `\begin` / `\end` take `{name}` directly after them.
    """
    problems: list[str] = []
    i = 0
    while i < len(latex):
        char = latex[i]
        if char == "%":
            problems.append("comment")
            i += 1
        elif char != "\\":
            i += 1
        else:
            j = i + 1
            if j < len(latex) and latex[j].isascii() and (latex[j].isalpha() or latex[j] == "@"):
                while (
                    j < len(latex)
                    and latex[j].isascii()
                    and (latex[j].isalpha() or latex[j] == "@")
                ):
                    j += 1
                name = latex[i + 1 : j]
                if name not in ALLOWED_COMMANDS:
                    problems.append(name)
                if name in ("begin", "end"):
                    match = re.match(r"\{([A-Za-z*]*)\}", latex[j:])
                    if match is None or match.group(1) not in ALLOWED_ENVIRONMENTS:
                        problems.append(f"environment after \\{name}")
                i = j
            else:
                i = j + 1  # the backslash and the one character it escapes
    return problems


def limit_problems(latex: str) -> list[str]:
    """Counts the limits independently: groups, alignment tabs, line breaks."""
    stripped = re.sub(r"\\.", "", latex, flags=re.DOTALL)
    problems: list[str] = []
    depth = deepest = 0
    for char in stripped:
        depth += (char == "{") - (char == "}")
        deepest = max(deepest, depth)
    if deepest > MAX_GROUP_DEPTH:
        problems.append("depth")
    if stripped.count("&") > MAX_ALIGNMENT_TABS:
        problems.append("tabs")
    if latex.count("\\\\") > MAX_LINE_BREAKS:
        problems.append("breaks")
    return problems


def only_allowed_characters(latex: str) -> bool:
    return all(32 <= ord(c) < 127 or c in "\t\n" for c in latex)


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
    "%",
    "\\%",
    "&",
    "[",
    "]",
    "\r",
    "\x7f",
    "×",
    "operatorname",
    "\\[",
    "{{",
    "}}",
]


@settings(max_examples=500, deadline=None)
@given(
    st.one_of(
        st.text(max_size=80),
        st.lists(st.sampled_from(FRAGMENTS), max_size=30).map("".join),
    )
)
def test_disallowed_never_raises_and_what_it_accepts_is_clean(latex: str) -> None:
    result = disallowed(latex)
    assert isinstance(result, list)
    assert len(result) == len(set(result))
    if not result:
        assert only_allowed_characters(latex), repr(latex)
        assert lex_problems(latex) == [], repr(latex)
        assert limit_problems(latex) == [], repr(latex)
        assert not re.search(r"\\\\\s*\[", latex), repr(latex)
        assert len(latex) <= MAX_LATEX_LENGTH


@settings(max_examples=200, deadline=None)
@given(
    st.lists(
        st.sampled_from(["{", "}", "\\{", "\\}", "&", "\\&", "\\\\", "x", " "]), max_size=500
    ).map("".join)
)
def test_the_size_limits_accept_exactly_what_an_independent_count_accepts(latex: str) -> None:
    refused_for_limits = bool(limit_problems(latex)) and len(latex) <= MAX_LATEX_LENGTH
    problems = disallowed(latex)
    mentions_limit = any(
        "nested deeper" in p or "alignment tabs" in p or "line breaks" in p for p in problems
    )
    assert mentions_limit == refused_for_limits, repr(latex)


# --- one symbol, one spelling: printable ASCII only -------------------------------------------

NOT_ASCII = [
    "×",
    "α",
    "µ",
    r"\text{é}",
    "\u00a0",
    "\u200b",
    "\x7f",
    "a\rb",
    "ℝ",
    "∑",
    "ℏ",
    "²",
    "°",
]


@pytest.mark.parametrize("latex", NOT_ASCII, ids=[ascii(x) for x in NOT_ASCII])
def test_anything_outside_printable_ascii_tab_and_newline_is_refused(latex: str) -> None:
    assert any("outside printable ASCII" in p for p in disallowed(latex)), latex


@pytest.mark.parametrize(
    ("code", "accepted"),
    [
        (31, False),
        (32, True),
        (126, True),
        (127, False),
        (9, True),
        (10, True),
        (13, False),
        (0, False),
    ],
)
def test_the_printable_ascii_range_has_exact_edges(code: int, accepted: bool) -> None:
    result = disallowed("a" + chr(code) + "b")
    assert (not any("outside printable ASCII" in p for p in result)) is accepted


# --- comments ---------------------------------------------------------------------------------


def test_a_percent_sign_is_fine_only_when_escaped() -> None:
    assert disallowed(r"50\% of x") == []
    assert disallowed(r"a \\\% b") == []  # a line break, then an escaped percent
    for latex in ["a % b", "%", "x%", "a\\\\% b", "a\\\\\\\\%", "50\\% % z"]:
        assert any("comment" in p for p in disallowed(latex)), latex


# --- internal commands: "@" is a letter for KaTeX ---------------------------------------------


def test_a_command_with_an_at_sign_is_a_different_command() -> None:
    result = disallowed(r"\operatorname@{x}")
    assert any(r"\operatorname@" in p for p in result), result
    assert any(r"\sin@" in p for p in disallowed(r"\sin@ x"))
    assert any(r"\@" in p for p in disallowed(r"\@"))
    assert disallowed(r"\operatorname{x}") == []


# --- \begin and \end need {name} directly after them ------------------------------------------

BAD_ENVIRONMENT_FORMS = [
    r"\begin {aligned} a \end {aligned}",
    "\\begin%\n{equation} a \\end%\n{equation}",
    r"\begin{{aligned}} a \end{{aligned}}",
    r"\begin",
    r"\end",
    r"a \begin b",
    r"\begin[x]{aligned}",
]


@pytest.mark.parametrize(
    "latex", BAD_ENVIRONMENT_FORMS, ids=[repr(x)[:30] for x in BAD_ENVIRONMENT_FORMS]
)
def test_begin_and_end_must_be_followed_directly_by_a_name_in_braces(latex: str) -> None:
    assert disallowed(latex), latex


def test_a_bare_begin_is_named() -> None:
    assert any("without an environment name" in p for p in disallowed(r"x \begin y"))


def test_an_escaped_backslash_before_begin_is_a_line_break_and_a_word() -> None:
    assert disallowed(r"a \\begin b") == []
    assert disallowed(r"a \\end") == []
    # three backslashes: a line break, then a real \begin that is then not followed by a name
    assert any("without an environment name" in p for p in disallowed(r"a \\\begin b"))


# --- length option after a line break ---------------------------------------------------------

LENGTH_OPTIONS = [
    r"a \\[2em] b",
    r"a \\ [2em] b",
    r"a \\[-1000em] b",
    r"a \\ [-1em] b",
    "a \\\\\n[1em] b",
    "a \\\\\t [1em] b",
    r"\begin{aligned} a \\[-1000em] b \end{aligned}",
]


@pytest.mark.parametrize("latex", LENGTH_OPTIONS, ids=[repr(x)[:30] for x in LENGTH_OPTIONS])
def test_a_length_option_after_a_line_break_is_refused(latex: str) -> None:
    assert any("length option" in p for p in disallowed(latex)), latex


def test_a_line_break_followed_by_text_or_a_group_is_fine() -> None:
    assert disallowed(r"a \\ b") == []
    assert disallowed(r"a \\ {[b]} c") == []


# --- limits: exactly at the limit passes, one over is refused ----------------------------------


def test_groups_nested_up_to_the_limit_pass_and_one_deeper_is_refused() -> None:
    at_limit = "{" * MAX_GROUP_DEPTH + "x" + "}" * MAX_GROUP_DEPTH
    assert disallowed(at_limit) == []
    over = "{" * (MAX_GROUP_DEPTH + 1) + "x" + "}" * (MAX_GROUP_DEPTH + 1)
    assert any("nested deeper" in p for p in disallowed(over))


def test_escaped_braces_do_not_count_as_nesting() -> None:
    assert disallowed(r"\{" * 200) == []
    assert disallowed(r"\{" * 100 + "{" * MAX_GROUP_DEPTH + "x" + "}" * MAX_GROUP_DEPTH) == []
    over = "{" * (MAX_GROUP_DEPTH + 1) + "x" + "}" * (MAX_GROUP_DEPTH + 1)
    assert any("nested deeper" in p for p in disallowed(r"\{" * 5 + over))


def test_depth_is_the_deepest_point_not_the_total_number_of_groups() -> None:
    wide = "{x}" * 500  # 1500 characters, depth 1
    assert disallowed(wide) == []
    assert disallowed("{" * MAX_GROUP_DEPTH + "}" * MAX_GROUP_DEPTH + "{" * MAX_GROUP_DEPTH) == []


def test_alignment_tabs_up_to_the_limit_pass_and_one_more_is_refused() -> None:
    assert disallowed("&" * MAX_ALIGNMENT_TABS) == []
    over = disallowed("&" * (MAX_ALIGNMENT_TABS + 1))
    assert any("alignment tabs" in p for p in over)


def test_escaped_ampersands_are_not_alignment_tabs() -> None:
    assert disallowed("&" * MAX_ALIGNMENT_TABS + r"\&" * 300) == []
    assert disallowed(r"\&" * 900) == []


def test_line_breaks_up_to_the_limit_pass_and_one_more_is_refused() -> None:
    assert disallowed(r"\\" * MAX_LINE_BREAKS) == []
    assert disallowed(" ".join([r"\\"] * MAX_LINE_BREAKS)) == []
    over = disallowed(r"\\" * (MAX_LINE_BREAKS + 1))
    assert any("line breaks" in p for p in over)


# --- the reviewers' confirmed bypass inputs, kept as a regression table -------------------------

BYPASSES = [
    ("\\begin%\n{equation} a \\end%\n{equation}", ""),
    ("\\begin%\n{smallmatrix} a \\end%\n{smallmatrix}", ""),
    ("\\begin%\n{align*} a \\end%\n{align*}", ""),
    ("\\begin%\n{CD} a \\end%\n{CD}", ""),
    (r"\operatorname@{x}", r"\operatorname@"),
    ("ℝ", "outside printable ASCII"),
    ("∑", "outside printable ASCII"),
    ("×", "outside printable ASCII"),
    ("α", "outside printable ASCII"),
    ("ℏ", "outside printable ASCII"),
    ("²", "outside printable ASCII"),
    (r"\begin{aligned} a \\[-1000em] b \end{aligned}", "length option"),
    (r"\begin{aligned}" + "&" * 1970 + r"\end{aligned}", "alignment tabs"),
    (r"\begin{array}{" + "c" * 950 + "}" + "&" * 949 + r"\end{array}", "alignment tabs"),
]


@pytest.mark.parametrize(("latex", "item"), BYPASSES, ids=[repr(b[0])[:28] for b in BYPASSES])
def test_every_confirmed_bypass_input_is_refused(latex: str, item: str) -> None:
    result = disallowed(latex)
    assert result, latex
    assert all(isinstance(p, str) and p for p in result)
    if item:
        assert any(item in p for p in result), (item, result)


# --- every list entry is really used by its own example -----------------------------------------


@pytest.mark.parametrize("name", sorted(ALLOWED_COMMANDS))
def test_every_command_occurs_as_a_command_token_in_its_own_example(name: str) -> None:
    assert re.search(rf"\\{re.escape(name)}(?![A-Za-z@])", ALLOWED_COMMANDS[name]), name


@pytest.mark.parametrize("name", sorted(ALLOWED_ENVIRONMENTS))
def test_every_environment_example_contains_its_own_begin_and_end(name: str) -> None:
    example = ALLOWED_ENVIRONMENTS[name]
    assert rf"\begin{{{name}}}" in example and rf"\end{{{name}}}" in example


def test_the_lists_hold_no_symbol_spelled_outside_ascii() -> None:
    for example in [*ALLOWED_COMMANDS.values(), *ALLOWED_ENVIRONMENTS.values()]:
        assert all(32 <= ord(c) < 127 for c in example), example


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


def node_major() -> int:
    """Major version of the Node that the renderer will be started with."""
    binary = shutil.which(os.environ.get("QLAB_NODE_BIN") or "node")
    assert binary is not None, "Node is required for the tests marked `node`"
    out = subprocess.run([binary, "--version"], capture_output=True, text=True, check=True)  # noqa: S603
    return int(out.stdout.strip().lstrip("v").split(".")[0])


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
    assert error is not None
    if node_major() >= 25:
        assert error.startswith("denied"), error
    # On Node 24 the permission model has no network rule (the module docstring says so); the
    # deployment blocks egress at the container level. Nothing is asserted there on purpose.


@node
def test_the_node_process_inherits_no_environment_but_node_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QLAB_TEST_SECRET_PROBE", "hunter2")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pw@host/db")
    body = (
        "const names = Object.keys(process.env);\n"
        f"answer('{KATEX_VERSION}', items.map(() => ({{ ok: false, "
        "error: names.join(',') + '|' + process.env.NODE_ENV })));"
    )
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    (answer,) = render_errors(fresh_node())
    assert answer is not None
    names, _, node_env = answer.partition("|")
    names_seen = {n for n in names.split(",") if n}
    assert node_env == "production"
    assert "NODE_ENV" in names_seen
    assert "PATH" not in names_seen  # not even PATH is passed on
    assert "QLAB_TEST_SECRET_PROBE" not in names_seen and "DATABASE_URL" not in names_seen
    # only what the operating system itself adds to a new process (macOS: __CF_USER_TEXT_ENCODING)
    assert names_seen <= {"NODE_ENV", "__CF_USER_TEXT_ENCODING"}, names_seen


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


# =============================================================================================
# Output cap, process flags, path handling, failure messages (needs Node)
# =============================================================================================


def max_output_chars() -> int:
    match = re.search(
        r"MAX_OUTPUT_CHARS\s*=\s*([\d_]+)", (KATEX_PACKAGE / "render.mjs").read_text()
    )
    assert match is not None, "render.mjs must export MAX_OUTPUT_CHARS"
    return int(match.group(1).replace("_", ""))


def test_the_render_script_exports_an_output_cap() -> None:
    assert re.search(r"export const MAX_OUTPUT_CHARS", (KATEX_PACKAGE / "render.mjs").read_text())
    assert max_output_chars() >= 10_000


HUGE_BUT_ALLOWED = {
    "fractions": r"\frac{a}{b}" * 160,
    "binomials": r"\binom{n}{k}" * 150,
    "roots": r"\sqrt[3]{x}" * 160,
    "braces": r"\overbrace{x}^{y}" * 100,
    "wide_matrix": r"\begin{matrix}" + " & ".join(["a"] * 200) + r"\end{matrix}",
}


@node
@pytest.mark.parametrize("display", [False, True], ids=["inline", "display"])
@pytest.mark.parametrize("case", list(HUGE_BUT_ALLOWED))
def test_a_formula_the_closed_list_accepts_but_whose_markup_is_too_large_is_reported_failed(
    case: str, display: bool
) -> None:
    latex = HUGE_BUT_ALLOWED[case]
    assert len(latex) <= MAX_LATEX_LENGTH and disallowed(latex) == []  # accepted before KaTeX
    (error,) = render_errors([MathNode(latex, display=display)])
    assert error is not None and str(max_output_chars()) in error, error


@node
def test_a_smaller_amount_of_the_same_markup_renders() -> None:
    assert render_errors(nodes(r"\frac{a}{b}" * 20)) == [None]
    assert render_errors(nodes(r"\begin{matrix}" + " & ".join(["a"] * 20) + r"\end{matrix}")) == [
        None
    ]


@node
def test_check_reports_a_too_large_formula_to_the_author() -> None:
    (problem,) = check(doc_with_math(HUGE_BUT_ALLOWED["fractions"]))
    assert "does not render" in problem and "larger than" in problem


@node
def test_the_largest_constructs_within_every_limit_are_answered_without_a_crash() -> None:
    """Each limit's extreme (deepest groups, most line breaks, most tabs, longest text) is
    answered one way or the other: it renders, or it is refused for its markup size."""
    deep = "".join(r"\frac{a}{" for _ in range(MAX_GROUP_DEPTH)) + "b" + "}" * MAX_GROUP_DEPTH
    breaks = r"\begin{aligned}" + r"\\".join(["a&b"] * MAX_LINE_BREAKS) + r"\end{aligned}"
    tabs = r"\begin{matrix}" + "&".join(["a"] * MAX_ALIGNMENT_TABS) + r"\end{matrix}"
    letters = "a" * MAX_LATEX_LENGTH
    for latex in (deep, breaks, tabs, letters):
        assert disallowed(latex) == [], latex[:30]
        (error,) = render_errors(nodes(latex))
        assert error is None or "larger than" in error, (latex[:30], error)
    # observed: deep, breaks and letters render; the 200-tab matrix exceeds the output cap
    assert render_errors(nodes(deep, breaks, letters)) == [None, None, None]


@node
def probe_answer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, script: str) -> str:
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, script)))
    (answer,) = render_errors(fresh_node())
    assert answer is not None
    return answer


@node
@pytest.mark.parametrize(
    "code",
    [
        'new Function("return 1")()',
        'eval("1 + 1")',
        '(0, eval)("2")',
        'new (async function () {}).constructor("return 1")()',
    ],
    ids=["Function", "eval", "indirect_eval", "AsyncFunction"],
)
def test_the_node_process_cannot_generate_code_from_strings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, code: str
) -> None:
    script = f"""
let outcome;
try {{ {code}; outcome = "allowed"; }} catch (error) {{ outcome = "denied " + error.name; }}
answer("{KATEX_VERSION}", items.map(() => ({{ ok: false, error: outcome }})));
"""
    answer = probe_answer(tmp_path, monkeypatch, script)
    assert answer.startswith("denied"), answer


@node
def test_the_node_process_is_started_with_the_documented_flags(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    script = (
        f"answer('{KATEX_VERSION}', "
        "items.map(() => ({ ok: false, error: process.execArgv.join(' ') })));"
    )
    flags = probe_answer(tmp_path, monkeypatch, script).split()
    assert "--permission" in flags
    assert "--disallow-code-generation-from-strings" in flags
    assert f"--max-old-space-size={qmath.RENDERER_MEMORY_MB}" in flags
    assert any(f.startswith("--allow-fs-read=") for f in flags)
    assert not any(
        f.startswith(("--allow-fs-write", "--allow-child-process", "--allow-worker", "--allow-net"))
        for f in flags
    )


@node
def test_the_node_process_cannot_start_a_worker(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    script = """
import { Worker } from "node:worker_threads";
let outcome;
try { new Worker("1", { eval: true }); outcome = "allowed"; }
catch (error) { outcome = "denied " + (error.code ?? error.name); }
answer("VERSION", items.map(() => ({ ok: false, error: outcome })));
""".replace("VERSION", KATEX_VERSION)
    assert probe_answer(tmp_path, monkeypatch, script).startswith("denied")


def test_the_time_limit_is_ten_seconds_and_memory_is_bounded() -> None:
    assert qmath.RENDER_TIMEOUT_SECONDS == 10
    assert 64 <= qmath.RENDERER_MEMORY_MB <= 1024


@node
def test_a_relative_katex_directory_is_resolved(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("QLAB_KATEX_DIR", os.path.relpath(KATEX_PACKAGE, tmp_path))
    assert not Path(os.environ["QLAB_KATEX_DIR"]).is_absolute()
    assert render_errors(nodes("x^", unique()))[0] is not None
    assert render_errors(nodes(r"\frac{a}{b}")) == [None]


@node
def test_a_symlink_to_the_katex_directory_works(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    link = tmp_path / "katex-link"
    link.symlink_to(KATEX_PACKAGE, target_is_directory=True)
    monkeypatch.setenv("QLAB_KATEX_DIR", str(link))
    assert render_errors(nodes(r"\frac{a}{b}", "x^"))[0] is None
    assert render_errors(nodes("x^"))[0] is not None


@node
def test_a_relative_directory_works_from_another_working_directory_too(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    copy = tmp_path / "work" / "sub"
    copy.mkdir(parents=True)
    monkeypatch.chdir(copy)
    link = tmp_path / "work" / "k"
    link.symlink_to(KATEX_PACKAGE, target_is_directory=True)
    monkeypatch.setenv("QLAB_KATEX_DIR", "../k")
    assert render_errors(nodes(unique())) == [None]


ECHOING = {
    "echoes_input_on_stderr_then_exits": "console.error(input); process.exit(1);",
    "throws_with_the_input_in_the_message": "throw new Error(input);",
    "echoes_input_as_the_answer": "process.stdout.write(input);",
    "echoes_input_inside_a_valid_shape": (
        "process.stdout.write(JSON.stringify({ version: input, results: [input] }));"
    ),
}


def raised_text(error: BaseException) -> str:
    return "".join(traceback.format_exception(error))


@node
@pytest.mark.parametrize("failure", [*FAKE_FAILURES, *ECHOING])
def test_no_failure_message_contains_the_latex_that_was_sent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, failure: str
) -> None:
    marker = unique()
    script = {**FAKE_FAILURES, **ECHOING}[failure]
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, script)))
    with pytest.raises(RendererUnavailable) as caught:
        render_errors(nodes(marker))
    assert marker not in raised_text(caught.value)
    assert marker not in str(caught.value)


@node
@pytest.mark.parametrize(
    "failure", ["exits_non_zero", "crashes", "echoes_input_on_stderr_then_exits"]
)
def test_a_non_zero_exit_hints_at_npm_ci_and_the_node_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, failure: str
) -> None:
    script = {**FAKE_FAILURES, **ECHOING}[failure]
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, script)))
    with pytest.raises(RendererUnavailable) as caught:
        render_errors(fresh_node())
    message = str(caught.value)
    assert "npm ci" in message and "Node" in message


@node
def test_missing_pieces_name_the_settings_to_look_at_and_never_the_latex(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    marker = unique()
    monkeypatch.setenv("QLAB_NODE_BIN", "no-such-node-binary-" + uuid.uuid4().hex)
    with pytest.raises(RendererUnavailable) as caught:
        render_errors(nodes(marker))
    assert "QLAB_NODE_BIN" in str(caught.value) and marker not in raised_text(caught.value)
    monkeypatch.delenv("QLAB_NODE_BIN")
    monkeypatch.setenv("QLAB_KATEX_DIR", str(tmp_path))
    with pytest.raises(RendererUnavailable) as caught:
        render_errors(nodes(marker))
    assert "QLAB_KATEX_DIR" in str(caught.value) and marker not in raised_text(caught.value)


# --- the answer cache ---------------------------------------------------------------------------


@node
def test_eviction_while_mixing_known_and_new_nodes_never_loses_an_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(qmath, "_CACHE_LIMIT", 5)
    good = [f"{unique()}" for _ in range(6)]
    bad = [f"{unique()}^" for _ in range(4)]
    first = render_errors(nodes(good[0], good[1], bad[0]))  # fills part of the cache
    assert [e is None for e in first] == [True, True, False]
    # known nodes mixed with enough new ones to cross the limit, duplicates included
    batch = [good[0], bad[0], good[2], good[3], good[4], bad[1], good[1], good[2], bad[2]]
    result = render_errors(nodes(*batch))
    assert [e is None for e in result] == [not b.endswith("^") for b in batch]
    assert result[0] is None and result[2] is None and result[2] == result[7]
    # and again, after the eviction
    again = render_errors(nodes(*batch, good[5], bad[3]))
    assert [e is None for e in again] == [not b.endswith("^") for b in [*batch, good[5], bad[3]]]
    assert again[: len(batch)] == result


@node
@pytest.mark.parametrize("limit", [1, 2, 3, 7])
def test_answers_stay_correct_over_many_batches_whatever_the_cache_limit(
    monkeypatch: pytest.MonkeyPatch, limit: int
) -> None:
    monkeypatch.setattr(qmath, "_CACHE_LIMIT", limit)
    pool = [f"p{i}" for i in range(6)] + [f"q{i}^" for i in range(4)]
    expected = {latex: not latex.endswith("^") for latex in pool}
    for start in range(0, 20):
        batch = [pool[(start * 3 + k * 7) % len(pool)] for k in range(1 + start % 5)]
        result = render_errors(nodes(*batch))
        assert [e is None for e in result] == [expected[b] for b in batch]


@node
def test_the_cache_serves_known_nodes_without_the_renderer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    latex = unique()
    assert render_errors(nodes(latex)) == [None]
    monkeypatch.setenv("QLAB_NODE_BIN", "no-such-node-binary-" + uuid.uuid4().hex)
    assert render_errors(nodes(latex)) == [None]
    with pytest.raises(RendererUnavailable):
        render_errors(nodes(latex, unique()))  # one unknown node needs the renderer


@node
def test_a_failed_run_caches_nothing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(
        "QLAB_KATEX_DIR", str(fake_renderer(tmp_path, FAKE_FAILURES["too_few_results"]))
    )
    before = dict(qmath._CACHE)
    with pytest.raises(RendererUnavailable):
        render_errors(nodes(unique(), unique(), unique()))
    assert dict(qmath._CACHE) == before == {}


@node
def test_a_failed_run_does_not_disturb_what_was_cached_before(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    known = unique()
    assert render_errors(nodes(known, "x^"))[0] is None
    snapshot = dict(qmath._CACHE)
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, FAKE_FAILURES["not_json"])))
    with pytest.raises(RendererUnavailable):
        render_errors(nodes(known, unique()))
    assert dict(qmath._CACHE) == snapshot


# --- ensure_renderer ----------------------------------------------------------------------------


@node
def test_ensure_renderer_passes_silently_when_the_renderer_works() -> None:
    qmath.ensure_renderer()  # returns None; any failure is an exception


@node
def test_ensure_renderer_does_not_trust_the_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    assert render_errors(nodes("x")) == [None]  # the trivial formula is now cached
    monkeypatch.setenv("QLAB_NODE_BIN", "no-such-node-binary-" + uuid.uuid4().hex)
    with pytest.raises(RendererUnavailable):
        qmath.ensure_renderer()


@node
def test_ensure_renderer_fails_for_a_missing_package_even_when_cached(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert render_errors(nodes("x")) == [None]
    (tmp_path / "render.mjs").write_text((KATEX_PACKAGE / "render.mjs").read_text())
    monkeypatch.setenv("QLAB_KATEX_DIR", str(tmp_path))
    with pytest.raises(RendererUnavailable):
        qmath.ensure_renderer()


@node
def test_ensure_renderer_fails_for_a_missing_script_even_when_cached(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert render_errors(nodes("x")) == [None]
    monkeypatch.setenv("QLAB_KATEX_DIR", str(tmp_path))
    with pytest.raises(RendererUnavailable):
        qmath.ensure_renderer()


@node
def test_ensure_renderer_fails_for_the_wrong_version_even_when_cached(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert render_errors(nodes("x")) == [None]
    monkeypatch.setenv(
        "QLAB_KATEX_DIR", str(fake_renderer(tmp_path, FAKE_FAILURES["a_different_version"]))
    )
    with pytest.raises(RendererUnavailable):
        qmath.ensure_renderer()


@node
@pytest.mark.parametrize("failure", list(FAKE_FAILURES))
def test_ensure_renderer_fails_for_every_misbehaving_renderer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, failure: str
) -> None:
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, FAKE_FAILURES[failure])))
    with pytest.raises(RendererUnavailable):
        qmath.ensure_renderer()


@node
def test_ensure_renderer_fails_when_the_trivial_formula_does_not_render(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = f"answer('{KATEX_VERSION}', items.map(() => ({{ ok: false, error: 'nope' }})));"
    monkeypatch.setenv("QLAB_KATEX_DIR", str(fake_renderer(tmp_path, body)))
    with pytest.raises(RendererUnavailable):
        qmath.ensure_renderer()


@node
def test_ensure_renderer_leaves_the_cache_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    qmath.ensure_renderer()
    assert qmath._CACHE == {}


# --- math_nodes and the schema's own listing ---------------------------------------------------


def with_formulas_everywhere(build: Callable[[], Json], places: list[str]) -> QuestionDocument:
    d = build()
    for place in places:
        LOCATIONS[place][1](d, f"f_{place}", False)
        LOCATIONS[place][1](d, f"b_{place}", True)
    return document(d)


@pytest.mark.parametrize("location", list(LOCATIONS))
def test_math_nodes_are_exactly_the_schemas_latex_sources_for_each_location(location: str) -> None:
    build, _ = LOCATIONS[location]
    doc = with_formulas_everywhere(build, [location])
    assert Counter(n.latex for n in math_nodes(doc)) == Counter(doc.latex_sources())
    assert {f"f_{location}", f"b_{location}"} <= {n.latex for n in math_nodes(doc)}


@pytest.mark.parametrize(
    ("build", "places"),
    [
        (samples.mcq_document, ["stem", "option_cell", "rationale", "explanation"]),
        (samples.two_column_mcq_document, ["stem", "column_header", "option_cell"]),
        (samples.roman_mcq_document, ["stem", "statement", "option_cell"]),
        (samples.show_that_document, ["stem", "lead_in", "body", "mark_point", "note"]),
    ],
    ids=["mcq", "two_column", "roman", "show_that"],
)
def test_math_nodes_are_exactly_the_schemas_latex_sources_with_math_in_every_location(
    build: Callable[[], Json], places: list[str]
) -> None:
    doc = with_formulas_everywhere(build, places)
    mine = Counter(n.latex for n in math_nodes(doc))
    assert mine == Counter(doc.latex_sources())
    assert all(mine[f"f_{p}"] == 1 and mine[f"b_{p}"] == 1 for p in places)
    displays = {n.latex: n.display for n in math_nodes(doc)}
    assert all(displays[f"f_{p}"] is False and displays[f"b_{p}"] is True for p in places)
