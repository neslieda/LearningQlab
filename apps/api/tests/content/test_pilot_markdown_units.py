"""Unit tests of the building blocks of the pilot Markdown converter (qlab.content.pilot.markdown).

Pure functions only: no database, no files. The inputs are short texts written for these tests.
The independent comparison of the converted files with their sources is a separate test module.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from qlab.content.pilot.__main__ import _layout_problems
from qlab.content.pilot.markdown import (
    FIGURE_NOTE_DESCRIPTION,
    MAX_FILE_BYTES,
    MAX_LINE_CHARS,
    ConversionError,
    ConversionFailed,
    Env,
    Line,
    Span,
    Tally,
    Vocabulary,
    answer_type_of,
    ascii_unit,
    classify_italic,
    command_term_of,
    convert_answers,
    convert_markdown,
    convert_notes,
    greek_command,
    note_kind,
    option_kind,
    parse_heading,
    parse_inline,
    plain_text,
    solution_model,
    split_row,
    stimulus_kind,
    to_latex,
    turkish_lower,
)
from qlab.content.schema import (
    AnswerType,
    MarkType,
    NoteKind,
    OptionKind,
    StimulusKind,
)

COMMAND_TERMS = frozenset(
    [
        "state",
        "draw",
        "annotate",
        "calculate",
        "describe",
        "estimate",
        "outline",
        "analyse",
        "determine",
        "discuss",
        "explain",
        "predict",
        "show",
        "sketch",
        "suggest",
        "deduce",
        "identify",
        "complete",
    ]
)
VOCABULARY = Vocabulary(
    nodes=frozenset({"A.1", "B.2"}),
    sections=frozenset({"paper_1a", "paper_1b", "paper_2"}),
    command_terms=COMMAND_TERMS,
)


def make_env() -> Env:
    return Env(stem="a1-test", tally=Tally(), question=3, line=7)


def spans(text: str) -> list[Span]:
    return parse_inline(text, make_env())


def shape(items: list[Span]) -> list[tuple[str, str, frozenset[MarkType]]]:
    return [(s.kind, s.value, s.marks) for s in items]


# --- Italic classification (section 4.2) -------------------------------------------------------


@pytest.mark.parametrize("token", ["x", "T", "g", "γ", "Δ", "ω"])
def test_rule_1_single_letter_is_a_variable(token: str) -> None:
    assert classify_italic(token, make_env()).kind == "variable"
    assert classify_italic(token, make_env()).rule == "1"


@pytest.mark.parametrize("token", ["MR", "Mv", "GMm", "Iω", "ωt", "evB", "eV"])
def test_rule_2_short_letter_runs_with_a_capital_or_greek_letter_are_variables(
    token: str,
) -> None:
    result = classify_italic(token, make_env())
    assert (result.kind, result.rule) == ("variable", "2")


def test_rule_2_stops_at_four_characters() -> None:
    with pytest.raises(ConversionError, match="Vxyzw"):
        classify_italic("Vxyzw", make_env())


@pytest.mark.parametrize("token", ["mv", "mg", "ct", "hf", "gt", "vx", "vt", "mr"])
def test_rule_3_names_in_the_specification_are_on_the_closed_variable_list(token: str) -> None:
    result = classify_italic(token, make_env())
    assert (result.kind, result.rule) == ("variable", "3")


@pytest.mark.parametrize("token", ["not", "one", "two", "twice", "into", "on", "out of"])
def test_rule_4_closed_words_are_italic_text(token: str) -> None:
    result = classify_italic(token, make_env())
    assert result.kind == "italic"


@pytest.mark.parametrize(
    "token", ["one eighth", "Allow ECF from (b).", "see Fig. 2", "± 2.3.", "twice as large"]
)
def test_rule_4_phrases_with_space_or_punctuation_are_italic_text(token: str) -> None:
    assert classify_italic(token, make_env()).kind == "italic"


@pytest.mark.parametrize("token", ["zebra", "qwerty", "ab", "x²", "a/b"])
def test_an_unknown_token_is_an_error_that_names_file_question_and_line(token: str) -> None:
    with pytest.raises(ConversionError) as caught:
        classify_italic(token, make_env())
    error = caught.value
    assert (error.file, error.question, error.line) == (
        "docs/pilot/a1-test-pilot-questions.md",
        3,
        7,
    )
    assert repr(token) in error.message
    assert "question 3, line 7" in str(error)


# --- Greek letters and ASCII LaTeX (section 4.3) -----------------------------------------------


@pytest.mark.parametrize(
    ("source", "latex"),
    [
        ("γ", r"\gamma"),
        ("Δ", r"\Delta"),
        ("ω", r"\omega"),
        ("Iω", r"I\omega"),
        ("ωt", r"\omega t"),
        ("αt", r"\alpha t"),
        ("ωR", r"\omega R"),
        ("λ", r"\lambda"),
        ("µ", r"\mu"),
        ("Ω", r"\Omega"),
        ("max", "max"),
        ("2/3", "2/3"),
    ],
)
def test_variables_become_ascii_latex(source: str, latex: str) -> None:
    assert to_latex(source, make_env()) == latex


def test_a_command_followed_by_a_digit_or_end_needs_no_space() -> None:
    assert to_latex("ω0", make_env()) == r"\omega0"
    assert greek_command("ω") == "omega"
    assert greek_command("a") is None


@pytest.mark.parametrize("source", ["x′", "v−u", "é", "_", "a{b"])
def test_characters_math_cannot_carry_are_an_error(source: str) -> None:
    with pytest.raises(ConversionError, match="cannot be written in math"):
        to_latex(source, make_env())


def test_unit_superscripts_become_ascii() -> None:
    assert ascii_unit("m s⁻¹") == "m s^-1"
    assert ascii_unit("kg m² s⁻²") == "kg m^2 s^-2"
    assert ascii_unit("N C⁻¹") == "N C^-1"
    assert ascii_unit("°C") == "°C"


# --- Inline tokenizer (section 4.1) ------------------------------------------------------------


def test_emphasis_pairs_left_to_right_around_text() -> None:
    result = spans("*v*Δ*x*/*c*²")
    assert shape(result) == [
        ("math", "v", frozenset()),
        ("text", "Δ", frozenset()),
        ("math", "x", frozenset()),
        ("text", "/", frozenset()),
        ("math", "c", frozenset()),
        ("text", "²", frozenset()),
    ]


def test_bold_is_read_before_italic_and_can_hold_a_variable() -> None:
    result = spans("a **not** b **very *g* large**")
    assert shape(result) == [
        ("text", "a ", frozenset()),
        ("text", "not", frozenset({MarkType.BOLD})),
        ("text", " b ", frozenset()),
        ("text", "very ", frozenset({MarkType.BOLD})),
        ("math", "g", frozenset({MarkType.BOLD})),
        ("text", " large", frozenset({MarkType.BOLD})),
    ]


def test_italic_text_gets_the_italic_mark_and_keeps_its_words() -> None:
    result = spans("rises *twice* as fast")
    assert shape(result)[1] == ("text", "twice", frozenset({MarkType.ITALIC}))
    assert plain_text(result) == "rises twice as fast"


def test_subscript_directly_after_a_variable_is_one_math_node() -> None:
    result = spans("*v*<sub>y</sub> and *E*<sup>2</sup>")
    assert shape(result) == [
        ("math", "v_{y}", frozenset()),
        ("text", " and ", frozenset()),
        ("math", "E^{2}", frozenset()),
    ]
    assert result[0].plain == "vy"


def test_subscript_and_superscript_can_follow_each_other() -> None:
    assert [s.value for s in spans("*x*<sub>a</sub><sup>2</sup>")] == ["x_{a}^{2}"]


def test_greek_letters_inside_a_subscript_become_commands() -> None:
    assert [s.value for s in spans("*E*<sub>γ</sub>")] == [r"E_{\gamma}"]


def test_subscript_that_does_not_follow_a_variable_is_marked_text() -> None:
    result = spans("10<sup>8</sup> and *v* <sub>y</sub>")
    assert shape(result) == [
        ("text", "10", frozenset()),
        ("text", "8", frozenset({MarkType.SUP})),
        ("text", " and ", frozenset()),
        ("math", "v", frozenset()),
        ("text", " ", frozenset()),
        ("text", "y", frozenset({MarkType.SUB})),
    ]


def test_two_subscripts_on_one_variable_are_an_error() -> None:
    with pytest.raises(ConversionError, match="two <sub>"):
        spans("*x*<sub>a</sub><sub>b</sub>")


def test_guillemets_mark_optional_text_and_are_not_kept() -> None:
    result = spans("t = 3.0 «s» and «= 29 m s⁻¹»")
    assert shape(result) == [
        ("text", "t = 3.0 ", frozenset()),
        ("text", "s", frozenset({MarkType.OPTIONAL})),
        ("text", " and ", frozenset()),
        ("text", "= 29 m s⁻¹", frozenset({MarkType.OPTIONAL})),
    ]


def test_optional_text_can_contain_variables() -> None:
    result = spans("«with *nR* = 2»")
    assert [(s.kind, s.marks) for s in result] == [
        ("text", frozenset({MarkType.OPTIONAL})),
        ("math", frozenset({MarkType.OPTIONAL})),
        ("text", frozenset({MarkType.OPTIONAL})),
    ]


def test_br_outside_a_cell_separator_is_a_hard_break() -> None:
    result = spans("first<br>second")
    assert [s.kind for s in result] == ["text", "break", "text"]


def test_spaces_collapse_and_edges_are_trimmed() -> None:
    result = spans("  a   b  ")
    assert shape(result) == [("text", "a b", frozenset())]


def test_adjacent_text_with_equal_marks_is_one_node() -> None:
    result = spans("m<sup>2</sup><sup>3</sup>")
    assert shape(result) == [
        ("text", "m", frozenset()),
        ("text", "23", frozenset({MarkType.SUP})),
    ]


@pytest.mark.parametrize(
    "text",
    [
        "a * b",  # cannot pair
        "*x* and *y",  # last star unpaired
        "*x *",  # span ends with a space
        "* x*",  # span starts with a space
        "**bold",  # unclosed bold
        "«open",  # unclosed optional
        "close»",  # close without open
        "`code`",  # backtick outside a formula chain
        "<sub>x</sub> *q*<sub>open",  # no closing tag
        "*zzzz*",  # unknown token
        "✓ stray",  # tick outside a mark-scheme cell
    ],
)
def test_malformed_markup_is_an_error_not_literal_text(text: str) -> None:
    with pytest.raises(ConversionError):
        spans(text)


def test_math_the_closed_command_list_refuses_is_an_error() -> None:
    from qlab.content.pilot import markdown

    env = make_env()
    with pytest.raises(ConversionError, match="not allowed"):
        markdown._math_span(r"\unknowncommand", "x", frozenset(), env)


# --- Table rows ---------------------------------------------------------------------------------


def test_row_cells_are_split_at_pipes_and_trimmed() -> None:
    cells = split_row(Line(5, "| 4. | a |  | 18 «m» ✓<br>x ✓ | *OWTTE* | 1 |"), make_env())
    assert cells == ["4.", "a", "", "18 «m» ✓<br>x ✓", "*OWTTE*", "1"]


def test_an_escaped_pipe_stops_the_conversion() -> None:
    with pytest.raises(ConversionError, match="escaped pipe"):
        split_row(Line(5, r"| a \| b | c |"), make_env())


# --- Headings -----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "section", "marks", "hl"),
    [
        ("## Soru 3 — Paper 1A", "1A", None, False),
        ("## Soru 4 — Paper 1A (HL)", "1A", None, True),
        ("## Soru 5 — Paper 2 (9 puan)", "2", 9, False),
        ("## Soru 6 — Paper 2 (HL, 9 puan)", "2", 9, True),
        ("## Soru 7 — Paper 1B (10 puan)", "1B", 10, False),
    ],
)
def test_question_headings(text: str, section: str, marks: int | None, hl: bool) -> None:
    heading = parse_heading(Line(10, text), make_env())
    assert (heading.section, heading.marks, heading.hl) == (section, marks, hl)


@pytest.mark.parametrize(
    "text", ["## Soru 3 - Paper 1A", "## Soru 3 — Paper 2", "## Soru 3 — Paper 1A (1 puan)"]
)
def test_unrecognised_headings_are_errors(text: str) -> None:
    with pytest.raises(ConversionError):
        parse_heading(Line(10, text), make_env())


# --- Mark-scheme cells (section 3.2) ------------------------------------------------------------


def test_answers_split_into_points_with_ids_and_ticks_removed() -> None:
    points, capped = convert_answers("first ✓<br>second «x» ✓", "d.ii", 2, make_env())
    assert [p.id for p in points] == ["d.ii-m1", "d.ii-m2"]
    assert [p.route for p in points] == [None, None]
    assert not capped
    assert plain_text(parse_inline("second «x»", make_env())) == "second x"


def test_alternative_lines_set_routes_and_are_not_points() -> None:
    cell = "shared ✓<br>**ALTERNATIVE 1**<br>a1 ✓<br>**ALTERNATIVE 2**<br>b1 ✓"
    points, capped = convert_answers(cell, "b", 2, make_env())
    assert [(p.id, p.route) for p in points] == [
        ("b-m1", None),
        ("b-m2", "alt1"),
        ("b-m3", "alt2"),
    ]
    assert not capped


def test_more_points_than_marks_caps_the_part() -> None:
    _, capped = convert_answers("a ✓<br>b ✓<br>c ✓", "a", 2, make_env())
    assert capped


def test_fewer_points_than_marks_is_an_error() -> None:
    with pytest.raises(ConversionError, match="1 awardable mark points for 2 marks"):
        convert_answers("a ✓", "a", 2, make_env())


def test_a_single_route_is_an_error() -> None:
    with pytest.raises(ConversionError, match="single ALTERNATIVE"):
        convert_answers("**ALTERNATIVE 1**<br>a ✓<br>b ✓", "a", 2, make_env())


def test_or_and_and_inside_a_point_do_not_split_it() -> None:
    points, _ = convert_answers("x **OR** y **AND** z ✓", "a", 1, make_env())
    assert len(points) == 1


@pytest.mark.parametrize("cell", ["no tick here", "a ✓<br>**OR**<br>b ✓", "a ✓ b ✓"])
def test_lines_without_a_final_tick_or_with_a_middle_tick_are_errors(cell: str) -> None:
    with pytest.raises(ConversionError):
        convert_answers(cell, "a", 1, make_env())


# --- Notes --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("plain", "kind"),
    [
        ("OWTTE", NoteKind.OWTTE),
        ("Allow ECF from (b).", NoteKind.ECF),
        ("Accept 4 %.", NoteKind.ACCEPT),
        ("Accept", NoteKind.ACCEPT),
        ("Do not accept repeat readings.", NoteKind.DO_NOT_ACCEPT),
        ("Award [1 max] for 7.5 W.", NoteKind.CAP),
        ("Award [1] max for 3.3.", NoteKind.CAP),
        ("Award [0] for a bare answer.", NoteKind.GENERAL),
        ("The third mark needs a conclusion.", NoteKind.GENERAL),
    ],
)
def test_note_kinds(plain: str, kind: NoteKind) -> None:
    assert note_kind(plain) is kind


def test_notes_drop_the_surrounding_italics_and_set_ecf_from() -> None:
    cell = "*Allow ECF from (b)(i).*<br>*OWTTE*<br>*Accept* Δ*U* = 3 *for the mark.*"
    notes, ecf = convert_notes(cell, "d", ["b.i", "b.ii", "c"], make_env())
    assert [n.kind for n in notes] == [NoteKind.ECF, NoteKind.OWTTE, NoteKind.ACCEPT]
    assert ecf == ("b.i",)
    for note in notes:
        paragraph = note.content.content[0]
        assert paragraph.type == "paragraph"
        assert all(
            all(m.type is not MarkType.ITALIC for m in node.marks)
            for node in paragraph.content
            if node.type == "text"
        )


def test_an_ecf_note_may_name_several_parts_and_ticks_in_notes_stay_text() -> None:
    cell = "*Allow ECF from (a) and (b).*<br>**OR** *alternative ✓ route ✓*"
    notes, ecf = convert_notes(cell, "c", ["a", "b"], make_env())
    assert ecf == ("a", "b")
    assert notes[1].kind is NoteKind.GENERAL
    paragraph = notes[1].content.content[0]
    assert paragraph.type == "paragraph"
    texts = [n.text for n in paragraph.content if n.type == "text"]
    assert "".join(texts) == "OR alternative ✓ route ✓"


def test_an_ecf_note_that_names_a_later_or_missing_part_is_an_error() -> None:
    with pytest.raises(ConversionError, match="not an earlier part"):
        convert_notes("*Allow ECF from (c).*", "b", ["a"], make_env())


# --- Fields filled by rule (section 5) ----------------------------------------------------------


def numbers_spans(*texts: str) -> list[list[Span]]:
    return [spans(t) for t in texts]


def test_option_kind_numeric_with_unit() -> None:
    options = numbers_spans("5.0 m s⁻¹", "7.0 m s⁻¹", "1.5 × 10³ m s⁻¹", "27°")
    assert option_kind(options) is OptionKind.NUMERIC_WITH_UNIT


def test_option_kind_ratio_for_plain_numbers_and_fractions() -> None:
    assert option_kind(numbers_spans("1/3", "1", "3", "9")) is OptionKind.RATIO
    assert option_kind(numbers_spans("0.18", "0.30", "0.43", "0.70")) is OptionKind.RATIO


def test_option_kind_algebraic_when_any_option_has_a_variable() -> None:
    assert option_kind(numbers_spans("zero", "less than *g*", "*g*", "more")) is (
        OptionKind.ALGEBRAIC_EXPRESSION
    )
    assert option_kind(numbers_spans("1.3*c*", "0.92*c*", "0.5*c*", "*c*")) is (
        OptionKind.ALGEBRAIC_EXPRESSION
    )


def test_option_kind_word_phrase_up_to_four_words() -> None:
    options = numbers_spans("to the left", "to the right", "upwards", "downwards")
    assert option_kind(options) is OptionKind.WORD_PHRASE


def test_option_kind_statement_for_longer_options() -> None:
    options = numbers_spans(
        "The gas does work on the surroundings",
        "The gas is compressed slowly",
        "No energy is transferred",
        "The pressure stays the same",
    )
    assert option_kind(options) is OptionKind.STATEMENT


def test_option_kind_one_option_without_a_unit_breaks_numeric_with_unit() -> None:
    options = numbers_spans("−2.0 J K⁻¹", "0", "+0.50 J K⁻¹", "+2.0 J K⁻¹")
    assert option_kind(options) is OptionKind.WORD_PHRASE


@pytest.mark.parametrize(
    ("body", "term", "show_that"),
    [
        ("Calculate the time taken.", "calculate", False),
        ("Show that the factor is about 1.7.", "show", True),
        ("Show how the factor arises.", "show", False),
        ("*Explain* why.", "explain", False),
        ("The accepted value is 9.8. Comment on the result.", None, False),
        ("Comment on whether the result is consistent.", None, False),
    ],
)
def test_command_term_is_the_first_word_if_it_is_in_the_vocabulary(
    body: str, term: str | None, show_that: bool
) -> None:
    assert command_term_of(body, VOCABULARY) == (term, show_that)


@pytest.mark.parametrize(
    ("term", "answer_type"),
    [
        ("calculate", AnswerType.NUMERIC_WITH_UNIT),
        ("determine", AnswerType.NUMERIC_WITH_UNIT),
        ("estimate", AnswerType.NUMERIC_WITH_UNIT),
        ("state", AnswerType.WORD_PHRASE),
        ("identify", AnswerType.WORD_PHRASE),
        ("show", AnswerType.DERIVATION_NUMERIC),
        ("explain", AnswerType.EXPLANATION),
        ("outline", AnswerType.EXPLANATION),
        ("describe", AnswerType.EXPLANATION),
        ("suggest", AnswerType.EXPLANATION),
        ("predict", AnswerType.EXPLANATION),
        ("deduce", AnswerType.EXPLANATION),
        ("discuss", AnswerType.EXTENDED_EVALUATION),
        ("analyse", AnswerType.EXTENDED_EVALUATION),
        ("draw", AnswerType.DRAWING_ON_DIAGRAM),
        ("annotate", AnswerType.DRAWING_ON_DIAGRAM),
        ("complete", AnswerType.DRAWING_ON_DIAGRAM),
        ("sketch", AnswerType.GRAPH_SKETCH),
        (None, AnswerType.EXPLANATION),
    ],
)
def test_answer_type_follows_the_command_term(term: str | None, answer_type: AnswerType) -> None:
    assert answer_type_of(term) is answer_type


def test_every_vocabulary_command_term_has_an_answer_type() -> None:
    for term in COMMAND_TERMS:
        assert answer_type_of(term) is not None


@pytest.mark.parametrize(
    ("description", "kind"),
    [
        ("Tek gözlü seri devre çizilmiş.", StimulusKind.CIRCUIT_DIAGRAM),
        ("Üç Direnç seri bağlı.", StimulusKind.CIRCUIT_DIAGRAM),
        ("Bir batarya ve bir lamba.", StimulusKind.CIRCUIT_DIAGRAM),
        ("İdeal voltmetre ölçer.", StimulusKind.CIRCUIT_DIAGRAM),
        ("Ampermetre seri.", StimulusKind.CIRCUIT_DIAGRAM),
        ("Bir P–V diyagramı.", StimulusKind.GRAPH),
        ("Yatay eksen zaman, grafik doğrusal.", StimulusKind.GRAPH),
        ("Elektrik alan çizgileri.", StimulusKind.FIELD_DIAGRAM),
        ("Işın diyagramı.", StimulusKind.RAY_WAVEFRONT_DIAGRAM),
        ("Dalga cepheleri düzlem.", StimulusKind.RAY_WAVEFRONT_DIAGRAM),
        ("Enerji düzeyleri gösterilir.", StimulusKind.ENERGY_LEVEL_DIAGRAM),
        ("Uzay-zaman diyagramı.", StimulusKind.SPACETIME_DIAGRAM),
        ("Veri tablosu.", StimulusKind.DATA_TABLE),
        ("Bir platform ve bir mekik.", StimulusKind.SCHEMATIC_DIAGRAM),
    ],
)
def test_stimulus_kind_from_the_first_keyword(description: str, kind: StimulusKind) -> None:
    assert stimulus_kind(description) is kind


def test_stimulus_kind_takes_the_keyword_that_comes_first_in_the_text() -> None:
    assert stimulus_kind("Bir grafik ve bir devre.") is StimulusKind.GRAPH
    assert stimulus_kind("Bir devre ve bir grafik.") is StimulusKind.CIRCUIT_DIAGRAM


def test_stimulus_keywords_match_at_a_word_start_only() -> None:
    # `ışın` inside "dışında" and `tablo` inside "stablo" are not keywords
    assert stimulus_kind("Çerçevenin dışında kalan bölge.") is StimulusKind.SCHEMATIC_DIAGRAM
    assert stimulus_kind("Bir stablo ve bir oku.") is StimulusKind.SCHEMATIC_DIAGRAM
    assert stimulus_kind("Çerçevenin dışında bir ışın.") is StimulusKind.RAY_WAVEFRONT_DIAGRAM
    assert stimulus_kind("(ışın) gelir") is StimulusKind.RAY_WAVEFRONT_DIAGRAM


def test_turkish_lower_casing_keeps_dotted_and_dotless_i_apart() -> None:
    assert turkish_lower("Işın") == "ışın"
    assert turkish_lower("İş") == "iş"
    assert turkish_lower("IŞIN") == "ışın"
    assert stimulus_kind("IŞIN demeti") is StimulusKind.RAY_WAVEFRONT_DIAGRAM
    assert stimulus_kind("Işın demeti") is StimulusKind.RAY_WAVEFRONT_DIAGRAM
    assert stimulus_kind("DEVRE şeması") is StimulusKind.CIRCUIT_DIAGRAM


# --- Solution model (section 3.4) ---------------------------------------------------------------


def chain(*rows: str) -> list[Line]:
    header = ["| Adım | İfade | Sonuç |", "|---|---|---|"]
    return [Line(no, text) for no, text in enumerate([*header, *rows], start=1)]


def test_a_conforming_chain_becomes_a_model() -> None:
    model, reason = solution_model(
        chain(
            "| Parametreler | `u = 18 m/s`, `H = 44 m`, sabit `g = 9.8 m/s^2`, `k = 3` | |",
            "| `t` | `sqrt(2*H/g)` | 3.00 s |",
            "| `v_y` | `g*t` | 29.4 m s⁻¹ |",
            "| `r` | `u/v_y` | 0.61 |",
        ),
        make_env(),
    )
    assert reason is None
    assert model is not None
    assert [(p.name, p.value, p.unit) for p in model.parameters] == [
        ("u", "18", "m/s"),
        ("H", "44", "m"),
        ("g", "9.8", "m/s^2"),
        ("k", "3", ""),
    ]
    assert [(s.id, s.name, s.expr, s.unit) for s in model.steps] == [
        ("s1", "t", "sqrt(2*H/g)", "s"),
        ("s2", "v_y", "g*t", "m s^-1"),
        ("s3", "r", "u/v_y", ""),
    ]
    assert model.constants == () and model.answers == ()


def test_the_constants_after_sabit_are_listed_in_the_tally() -> None:
    env = make_env()
    solution_model(chain("| Parametreler | `a = 1 m`, sabit `g = 9.8 m/s^2` | |"), env)
    assert env.tally.constants == [("pilot/a1-test#3", "g")]


@pytest.mark.parametrize(
    ("row", "code"),
    [
        ("| Parametreler | `a = 1 m`, b = 2 | |", "ters tırnaksız parametre metni"),
        ("| Parametreler | `a = çok` | |", "sayı biçimi"),
        ("| Parametreler | `a = 1 3 m!` | |", "birim biçimi"),
        ("| Parametreler | `a is 1` | |", "parametre biçimi"),
        ("| Kontrol | `x` | 1 |", "satır adı tanımlayıcı değil"),
        ("| `1x` | `x` | 1 |", "satır adı tanımlayıcı değil"),
        ("| `a`, `b` | `x` | 1 |", "satır adı tanımlayıcı değil"),
        ("| `a` | `x`, `y` | 1 |", "ifade sütunu tek ifade değil"),
        ("| `a` | | 1 |", "ifade sütunu tek ifade değil"),
        ("| `a` | x | 1 |", "ifade sütunu tek ifade değil"),
        ("| `a` | `x` |", "sütun sayısı"),
    ],
)
def test_a_chain_that_does_not_fit_is_omitted_with_a_reason(row: str, code: str) -> None:
    model, reason = solution_model(chain(row), make_env())
    assert model is None
    assert reason is not None and reason[0] == code


def test_duplicate_names_omit_the_model() -> None:
    model, reason = solution_model(
        chain("| Parametreler | `a = 1 m` | |", "| `a` | `2*a` | 2 m |"), make_env()
    )
    assert model is None
    assert reason is not None and reason[0] == "yinelenen ad"


def test_one_bad_row_omits_the_whole_model() -> None:
    model, _ = solution_model(
        chain("| `a` | `1` | 1 |", "| Denetim | 3 | |", "| `b` | `2` | 2 |"), make_env()
    )
    assert model is None


# --- Whole files (a short synthetic example) ----------------------------------------------------

SAMPLE = """# Pilot soru seti: A.1 Deneme

## Kapsam tablosu

| # | Bölüm | Düzey | Kazanım (A.1) | Hedef | Komut sözcüğü | Puan | Zorluk |
|---|---|---|---|---|---|---|---|
| 1 | Paper 1A | SL | Sabit hızla hareket | AO2 | — | 1 | Kolay–orta |
| 2 | Paper 2 | HL | Serbest düşme | AO1–AO3 | State, Show that | 3 | Orta–zor |

---

## Soru 1 — Paper 1A

A trolley moves at a constant speed of 2.0 m s⁻¹ for 5.0 s.

> **Şekil:** Düz bir ray üzerinde bir araba; hız oku sağa dönük.

What distance does the trolley travel?

A. 0.40 m
B. 2.5 m
C. 7.0 m
D. 10 m

**Cevap: D**

**Çözüm.** *s* = *vt* = 2.0 × 5.0 = 10 m.

| Seçenek | Dayandığı yanılgı |
|---|---|
| A | Süre hıza bölünür: 5.0 / 2.0 |
| B | Hız süreye bölünür: 5.0 / 2.0 |
| C | Hız ile süre toplanır: 2.0 + 5.0 |

Not: yalnızca bu denemede kullanılan bir ek paragraf.

---

## Soru 2 — Paper 2 (HL, 3 puan)

A stone falls from rest for *t* seconds.

**(a)** State the initial speed of the stone. [1]

The stone then lands on soft ground.

**(b)** (i) Show that the speed after 2.0 s is about 20 m s⁻¹. [1]

 (ii) Calculate the distance fallen in 2.0 s. [1]

### Markscheme

| Question | | | Answers | Notes | Total |
|---|---|---|---|---|---|
| 2. | a | | zero «m s⁻¹» ✓ | *OWTTE* | 1 |
| 2. | b | i | *v* = 9.8 × 2.0 = 20 «m s⁻¹» ✓ | *Answer must be seen to 2 s.f.* | 1 |
| 2. | b | ii | **ALTERNATIVE 1**<br>a ✓<br>**ALTERNATIVE 2**<br>b ✓ | *Allow ECF from (b)(i)* | 1 |

### Formül zinciri (çözüm modeli)

| Adım | İfade | Sonuç |
|---|---|---|
| Parametreler | `t = 2.0 s`, sabit `g = 9.8 m/s^2` | |
| `v` | `g*t` | 19.6 m s⁻¹ |
| `d` | `0.5*g*t**2` | 19.6 m |

Denetim: serbest açıklama.

---

## Biçim uyumu

Hiçbir şey.
"""


def convert_sample(text: str = SAMPLE) -> tuple[ConversionFailed | None, Tally]:
    tally = Tally()
    try:
        convert_markdown(text.encode(), "a1-test", VOCABULARY, tally)
    except ConversionFailed as failed:
        return failed, tally
    return None, tally


def test_a_short_file_converts_end_to_end() -> None:
    tally = Tally()
    pilot = convert_markdown(SAMPLE.encode(), "a1-test", VOCABULARY, tally)
    assert [q.source_ref for q in pilot.questions] == ["pilot/a1-test#1", "pilot/a1-test#2"]
    mcq, structured = (q.document for q in pilot.questions)
    assert mcq.mcq is not None
    assert mcq.mcq.correct_key == "D"
    assert mcq.mcq.option_kind is OptionKind.NUMERIC_WITH_UNIT
    assert mcq.mcq.assessment_objective == 2
    assert [s.id for s in mcq.stimuli] == ["fig1"]
    assert [b.type for b in mcq.stem.content] == ["paragraph", "figure", "paragraph"]
    assert [lv.value for lv in mcq.levels] == ["sl", "hl"]
    assert [p.id for p in structured.parts] == ["a", "b.i", "b.ii"]
    assert [lv.value for lv in structured.levels] == ["hl"]
    assert structured.parts[0].lead_in is None
    assert structured.parts[1].lead_in is not None
    assert structured.parts[1].show_that
    assert structured.parts[2].ecf_from == ("b.i",)
    assert structured.solution_model is not None
    assert tally.models_imported == ["pilot/a1-test#2"]
    # the extra paragraph after the MCQ table and the one after the formula chain
    assert sorted(tally.free_paragraphs) == [("pilot/a1-test#1", 1), ("pilot/a1-test#2", 1)]


def test_the_same_text_always_gives_the_same_json() -> None:
    first = convert_markdown(SAMPLE.encode(), "a1-test", VOCABULARY).to_json()
    second = convert_markdown(SAMPLE.encode(), "a1-test", VOCABULARY).to_json()
    assert first == second


def test_a_failing_question_is_reported_with_its_number_and_line() -> None:
    broken = SAMPLE.replace("zero «m s⁻¹» ✓", "zero «m s⁻¹»")
    failed, _ = convert_sample(broken)
    assert failed is not None
    assert len(failed.errors) == 1
    error = failed.errors[0]
    assert (error.file, error.question) == ("docs/pilot/a1-test-pilot-questions.md", 2)
    assert error.line is not None and "without ✓" in error.message


def test_a_part_without_marks_and_a_question_missing_from_the_scope_table_stop() -> None:
    failed, _ = convert_sample(
        SAMPLE.replace("State the initial speed of the stone. [1]", "State.")
    )
    assert failed is not None and "no `[n]` marks" in failed.errors[0].message
    with pytest.raises(ConversionError, match="not in the scope table"):
        convert_markdown(
            SAMPLE.replace("## Soru 2 —", "## Soru 3 —").encode(), "a1-test", VOCABULARY
        )


def test_heading_and_part_marks_must_agree() -> None:
    failed, _ = convert_sample(SAMPLE.replace("(HL, 3 puan)", "(HL, 4 puan)"))
    assert failed is not None and "the parts add up to 3" in failed.errors[0].message


def test_the_total_column_must_equal_the_part_marks() -> None:
    failed, _ = convert_sample(
        SAMPLE.replace(
            "| 2. | a | | zero «m s⁻¹» ✓ | *OWTTE* | 1 |", "| 2. | a | | zero ✓ | *OWTTE* | 2 |"
        )
    )
    assert failed is not None and "Total" in failed.errors[0].message


def test_an_option_row_for_the_correct_answer_or_a_missing_row_is_an_error() -> None:
    missing = SAMPLE.replace("| C | Hız ile süre toplanır: 2.0 + 5.0 |\n", "")
    failed, _ = convert_sample(missing)
    assert failed is not None and "no misconception row for C" in failed.errors[0].message


# --- Amended rules: figure notes, block end, robustness -----------------------------------------


def test_a_figure_note_is_not_imported_and_gets_the_fixed_description() -> None:
    text = SAMPLE.replace(
        "Denetim: serbest açıklama.\n",
        "Denetim: serbest açıklama.\n\n### Şekil notu\n\nThe gradient is exactly 42 N.\n",
    )
    tally = Tally()
    pilot = convert_markdown(text.encode(), "a1-test", VOCABULARY, tally)
    document = pilot.questions[1].document
    assert [(s.id, s.kind, s.use.value, s.description) for s in document.stimuli] == [
        ("fig1", StimulusKind.GRAPH, "read_values", FIGURE_NOTE_DESCRIPTION)
    ]
    assert "42" not in pilot.to_json()
    assert tally.figure_notes_skipped == ["pilot/a1-test#2"]
    assert [b.type for b in document.stem.content] == ["paragraph"]


def test_a_non_blank_line_between_the_rule_and_the_next_heading_is_an_error() -> None:
    text = SAMPLE.replace("---\n\n## Soru 2", "---\n\nLeftover text.\n\n## Soru 2")
    failed, _ = convert_sample(text)
    assert failed is not None
    error = failed.errors[0]
    assert error.question == 1 and error.line is not None
    assert "after the `---`" in error.message
    assert text.split("\n")[error.line - 1] == "Leftover text."


def test_a_second_rule_inside_a_question_block_is_an_error() -> None:
    text = SAMPLE.replace("**Cevap: D**", "---\n\n**Cevap: D**")
    failed, _ = convert_sample(text)
    assert failed is not None and failed.errors[0].question == 1


@pytest.mark.parametrize(
    "text",
    [
        SAMPLE.replace("## Soru 1 —", "## Soru 123456 —"),
        SAMPLE.replace("| 1 | Paper 1A", "| 12345 | Paper 1A"),
        SAMPLE.replace("(HL, 3 puan)", "(HL, " + "9" * 5000 + " puan)"),
        SAMPLE.replace(
            "| 2. | a | | zero «m s⁻¹» ✓ | *OWTTE* | 1 |", "| 2. | a | | z ✓ | *OWTTE* | ²³ |"
        ),
        SAMPLE.replace("State the initial speed of the stone. [1]", "State. [" + "1" * 5000 + "]"),
    ],
)
def test_absurd_numbers_are_conversion_errors(text: str) -> None:
    with pytest.raises(ConversionError):
        convert_markdown(text.encode(), "a1-test", VOCABULARY)


def test_a_part_line_with_a_long_run_of_spaces_is_handled_in_linear_time() -> None:
    text = SAMPLE.replace(
        "State the initial speed of the stone. [1]", "State the speed." + " " * 15000 + "[x]"
    )
    failed, _ = convert_sample(text)
    assert failed is not None and "no `[n]` marks" in failed.errors[0].message


def test_input_size_limits_are_conversion_errors() -> None:
    with pytest.raises(ConversionError, match="larger than"):
        convert_markdown(SAMPLE.encode() + b"x" * MAX_FILE_BYTES, "a1-test", VOCABULARY)
    long_line = SAMPLE.replace("A trolley", "A" * (MAX_LINE_CHARS + 1) + " trolley")
    with pytest.raises(ConversionError, match="longer than"):
        convert_markdown(long_line.encode(), "a1-test", VOCABULARY)


def test_a_table_with_only_a_separator_row_is_an_error_not_an_index_error() -> None:
    start = SAMPLE.index("| Seçenek")
    end = SAMPLE.index("Not: yalnızca")
    text = SAMPLE[:start] + "|---|---|\n\n" + SAMPLE[end:]
    failed, _ = convert_sample(text)
    assert failed is not None and "table without a header row" in failed.errors[0].message
    scope_only = SAMPLE.replace(
        SAMPLE[SAMPLE.index("| # | Bölüm") : SAMPLE.index("| 1 | Paper 1A")], "|---|---|\n"
    )
    with pytest.raises(ConversionError):
        convert_markdown(scope_only.encode(), "a1-test", VOCABULARY)


def test_a_file_without_questions_is_an_error() -> None:
    head = SAMPLE[: SAMPLE.index("## Soru 1")]
    only_scope = head.replace("| 1 | Paper 1A", "| x | Paper 1A")
    with pytest.raises(ConversionError):
        convert_markdown(only_scope.encode(), "a1-test", VOCABULARY)
    with pytest.raises(ConversionError, match="no questions|not match"):
        convert_markdown(head.encode(), "a1-test", VOCABULARY)


@pytest.mark.parametrize("text", ["x<sub>**a</sub>", "x<sup>«a</sup>", "*v*<sub>**a</sub>"])
def test_unclosed_emphasis_inside_subscripts_is_an_error(text: str) -> None:
    with pytest.raises(ConversionError, match="unclosed"):
        spans(text)


# --- Command line: symbolic links are refused ---------------------------------------------------


def make_tree(tmp_path: Path) -> Path:
    (tmp_path / "docs" / "pilot").mkdir(parents=True)
    (tmp_path / "content" / "pilot").mkdir(parents=True)
    (tmp_path / "docs" / "pilot" / "a1-test-pilot-questions.md").write_text("x", encoding="utf-8")
    (tmp_path / "content" / "pilot" / "a1-test.json").write_text("{}", encoding="utf-8")
    return tmp_path


def test_a_plain_tree_has_no_layout_problems(tmp_path: Path) -> None:
    assert _layout_problems(make_tree(tmp_path)) == []


def test_a_symlinked_source_file_is_refused(tmp_path: Path) -> None:
    root = make_tree(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("x", encoding="utf-8")
    (root / "docs" / "pilot" / "b1-link-pilot-questions.md").symlink_to(outside)
    assert _layout_problems(root) == ["docs/pilot/b1-link-pilot-questions.md is a symbolic link"]


def test_a_symlinked_output_file_or_directory_is_refused(tmp_path: Path) -> None:
    root = make_tree(tmp_path)
    (root / "content" / "pilot" / "a1-test.json").unlink()
    (root / "content" / "pilot" / "a1-test.json").symlink_to(root / "docs" / "pilot")
    assert _layout_problems(root) == ["content/pilot/a1-test.json is a symbolic link"]
    (root / "content" / "pilot" / "a1-test.json").unlink()
    (root / "content" / "pilot").rmdir()
    (root / "content" / "pilot").symlink_to(root / "docs" / "pilot")
    assert _layout_problems(root) == ["content/pilot is a symbolic link"]
