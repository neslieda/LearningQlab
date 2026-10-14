"""The language hint `qlab.api.language.looks_non_english`, rule by rule
(docs/slices/M1G-5-SOZLESME.md section 3.4).

Pure tests: no database, no network. The two word sets of rule 4 are small and fixed but their
contents are not part of the specification, so the rule-4 tests read the module's public
`frozenset` constants and build their inputs from them instead of hard-coding words.
"""

from __future__ import annotations

from types import ModuleType

import pytest
from hypothesis import given
from hypothesis import strategies as st

from qlab.api import language
from qlab.api.language import looks_non_english

STRONG_LETTERS = "ğışİĞŞ"
ASCII_LOWER = "abcdefghijklmnopqrstuvwxyz"


def _word_sets(module: ModuleType = language) -> list[frozenset[str]]:
    return [
        value
        for value in vars(module).values()
        if isinstance(value, frozenset) and value and all(isinstance(w, str) for w in value)
    ]


def _find_set(probe: str) -> frozenset[str]:
    found = [s for s in _word_sets() if probe in s]
    assert found, f"no frozenset constant in qlab.api.language contains {probe!r}"
    return found[0]


def turkish_words() -> frozenset[str]:
    return _find_set("bir")


def english_words() -> frozenset[str]:
    return _find_set("the")


def plain_turkish(count: int) -> list[str]:
    """Distinct Turkish common words without a strong letter, so that only rule 4 can apply."""
    candidates = sorted(
        w
        for w in turkish_words()
        if w.isalpha() and len(w) >= 2 and not any(c in STRONG_LETTERS for c in w)
    )
    assert len(candidates) >= count, "the Turkish word set is too small for these tests"
    return candidates[:count]


def plain_english(count: int) -> list[str]:
    candidates = sorted(w for w in english_words() if w.isalpha() and len(w) >= 2)
    assert len(candidates) >= count, "the English word set is too small for these tests"
    return candidates[:count]


# --- the constants ----------------------------------------------------------------------------


def test_the_two_word_sets_exist_are_frozen_and_do_not_intersect() -> None:
    turkish, english = turkish_words(), english_words()
    assert isinstance(turkish, frozenset)
    assert isinstance(english, frozenset)
    assert turkish is not english
    assert turkish.isdisjoint(english)


def test_the_word_sets_hold_lower_case_words() -> None:
    for words in (turkish_words(), english_words()):
        assert all(w == w.lower() for w in words)


def test_the_turkish_set_is_small_and_fixed() -> None:
    # "küçük, sabit" (small, fixed): a hint, not a dictionary.
    assert 2 <= len(turkish_words()) <= 500


# --- rule 2: fewer than three words -----------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "\n\t",
        "ışık",  # one word with strong letters
        "ışık hızı",  # two words with strong letters
        "Çok güzel",
        "42",
        "9.8 m/s",
        "kuvvet",
    ],
)
def test_fewer_than_three_words_is_never_flagged(text: str) -> None:
    assert looks_non_english(text) is False


def test_three_words_is_enough_to_apply_the_later_rules() -> None:
    assert looks_non_english("ışık çok hızlı") is True


# --- rule 1: what a word is -------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "a b c d e f",
        "ş ı ğ ş ı ğ",  # single letters do not count, strong or not
        "x = 1 + y",
        "v = u + a t",
        "F = m a",
    ],
)
def test_single_letter_words_are_not_counted(text: str) -> None:
    assert looks_non_english(text) is False


def test_single_letter_words_do_not_make_up_the_three_words() -> None:
    # Only one word of two or more letters: fewer than three words.
    assert looks_non_english("a ışık b c") is False
    # Two such words and single letters between them: still two.
    assert looks_non_english("ışık a hızı b") is False


def test_a_third_two_letter_word_completes_the_count() -> None:
    assert looks_non_english("ışık a hızı b ve") is True


@pytest.mark.parametrize(
    "text",
    [
        "ışık,hızı;çok",
        "ışık-hızı-çok",
        "ışık\nhızı\tçok",
        "(ışık)/(hızı)/(çok)",
        "ışık1hızı2çok",
    ],
)
def test_words_are_runs_of_letters_split_by_anything_else(text: str) -> None:
    assert looks_non_english(text) is True


def test_digits_and_symbols_are_not_words() -> None:
    assert looks_non_english("3.5 * 10^8 m/s^2 = 12.0 + 7") is False


def test_words_are_compared_in_lower_case() -> None:
    plain = plain_turkish(2)
    lower = " ".join([*plain, "zzqq"])
    assert looks_non_english(lower) is True
    assert looks_non_english(lower.upper()) is True
    assert looks_non_english(lower.title()) is True


# --- rule 3: the strong Turkish letters ---------------------------------------------------------


@pytest.mark.parametrize("letter", ["ğ", "ı", "ş", "İ", "Ğ", "Ş"])
def test_each_strong_letter_alone_flags_a_text_of_three_words(letter: str) -> None:
    sentence = f"the d{letter}d value"
    assert looks_non_english(sentence) is True


@pytest.mark.parametrize("letter", ["ğ", "ı", "ş", "İ", "Ğ", "Ş"])
def test_a_strong_letter_at_the_start_or_end_of_a_word_counts(letter: str) -> None:
    assert looks_non_english(f"the {letter}ab value") is True
    assert looks_non_english(f"the ab{letter} value") is True


def test_a_capital_dotted_i_word_flags() -> None:
    assert looks_non_english("İyi ders çalışma") is True
    assert looks_non_english("the İZMİR value") is True


def test_one_strong_word_among_english_words_flags() -> None:
    assert looks_non_english("The ball moves with constant velocity and then ışık") is True


def test_a_strong_letter_flags_even_when_english_words_dominate() -> None:
    # Rule 3 is decided before the comparison of rule 4.
    english = " ".join(plain_english(6))
    assert looks_non_english(f"{english} ışık") is True


@pytest.mark.parametrize("letter", ["ç", "ö", "ü", "Ç", "Ö", "Ü"])
def test_c_cedilla_o_umlaut_u_umlaut_alone_do_not_flag(letter: str) -> None:
    assert looks_non_english(f"the x{letter}x value") is False


def test_a_proper_name_with_umlauts_does_not_flag() -> None:
    assert looks_non_english("Müller Schröder Çelik") is False
    assert looks_non_english("Dr Müller measured the speed of the cart") is False
    assert looks_non_english("ÇÖÜ ÇÖÜ ÇÖÜ") is False


# --- rule 4: common words, two distinct, more than English ---------------------------------


def test_two_distinct_turkish_common_words_flag_a_text_with_no_english_words() -> None:
    first, second = plain_turkish(2)
    assert looks_non_english(f"{first} {second} zzqq") is True


def test_the_two_words_must_be_distinct() -> None:
    (word,) = plain_turkish(1)
    assert looks_non_english(f"{word} {word} {word}") is False
    assert looks_non_english(f"{word} {word} {word} {word} zzqq") is False


def test_one_turkish_common_word_is_not_enough() -> None:
    (word,) = plain_turkish(1)
    assert looks_non_english(f"{word} zzqq yyxx") is False


def test_turkish_must_outnumber_english_distinct_words() -> None:
    first, second, third = plain_turkish(3)
    one, two, three = plain_english(3)

    assert looks_non_english(f"{first} {second} {one}") is True  # 2 against 1
    assert looks_non_english(f"{first} {second} {one} {two}") is False  # 2 against 2: not more
    assert looks_non_english(f"{first} {second} {third} {one} {two}") is True  # 3 against 2
    assert looks_non_english(f"{first} {second} {one} {two} {three}") is False  # 2 against 3


def test_repeating_an_english_word_does_not_raise_the_english_count() -> None:
    first, second = plain_turkish(2)
    (one,) = plain_english(1)
    assert looks_non_english(f"{first} {second} {one} {one} {one}") is True


def test_repeating_a_turkish_word_does_not_raise_the_turkish_count() -> None:
    first, second = plain_turkish(2)
    one, two = plain_english(2)
    assert looks_non_english(f"{first} {first} {first} {second} {one} {two}") is False


# --- English, formulas, numbers, mixed ----------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "The ball accelerates because the net force acts on it",
        "Calculate the time taken for the package to reach the ground",
        "The gradient of the graph is equal to g divided by two",
        "Energy is transferred from the chemical store to the kinetic store",
        "the velocity increases",
    ],
)
def test_english_sentences_are_not_flagged(text: str) -> None:
    assert looks_non_english(text) is False


@pytest.mark.parametrize(
    "text",
    [
        "42",
        "0.45",
        "-3.2e-4",
        "9.8 m/s^2",
        "v = u + a t",
        "E = mc^2",
        "x = 1/2 a t^2",
        "sqrt(2*H/g)",
        "0.5 * 9.8 * 3.0^2",
        "h = 1/2 g t^2 = 44 m",
        "t = 3.0 s, v = 34 m/s",
        "!!!",
        "1 + 1 = 2",
    ],
)
def test_numbers_and_formulas_are_not_flagged(text: str) -> None:
    assert looks_non_english(text) is False


@pytest.mark.parametrize(
    "text",
    [
        "Cismin hızı zamanla artar çünkü net kuvvet etki eder",
        "Topun ivmesi sabit kalır",
        "Işık bir dalga olarak yayılır",
        "hız = yol / zaman",  # strong letter in a three-word text
    ],
)
def test_turkish_sentences_with_strong_letters_are_flagged(text: str) -> None:
    assert looks_non_english(text) is True


def test_a_turkish_sentence_with_english_technical_terms_is_flagged() -> None:
    assert looks_non_english("Cismin velocity değeri artar") is True


def test_english_sentence_with_a_formula_and_a_name_is_not_flagged() -> None:
    assert looks_non_english("Using v = u + a t the speed is 34 m/s, as Müller found") is False


# --- the empty string, determinism ---------------------------------------------------------------


def test_the_empty_string_is_not_flagged() -> None:
    assert looks_non_english("") is False


def test_the_result_is_a_bool() -> None:
    for text in ("", "ışık çok hızlı", "the ball moves", "42"):
        assert type(looks_non_english(text)) is bool


def test_the_function_is_deterministic() -> None:
    samples = ["ışık çok hızlı", "the ball moves slowly", "42", "", "Müller Schröder Çelik"]
    for text in samples:
        results = {looks_non_english(text) for _ in range(50)}
        assert len(results) == 1


def test_the_function_is_pure_it_does_not_change_the_word_sets() -> None:
    before = (turkish_words(), english_words())
    for text in ("ışık çok hızlı", "the ball moves slowly"):
        looks_non_english(text)
    assert (turkish_words(), english_words()) == before


# --- properties -----------------------------------------------------------------------------------


@given(st.text())
def test_never_raises_and_always_returns_a_bool(text: str) -> None:
    assert type(looks_non_english(text)) is bool


@given(st.text())
def test_repeated_calls_agree(text: str) -> None:
    assert looks_non_english(text) == looks_non_english(text)


@given(st.text(alphabet="0123456789+-*/^=().,%[]{} \t\n"))
def test_digits_and_operators_only_are_never_flagged(text: str) -> None:
    assert looks_non_english(text) is False


@given(st.text(alphabet="0123456789+-*/^=().,%abcdefghijklmnopqrstuvwxyzşığ ", max_size=60))
def test_a_text_with_only_single_letter_words_is_never_flagged(text: str) -> None:
    # Break every run of letters into single letters separated by a symbol.
    spaced = "".join(f"{c}+" if c.isalpha() else c for c in text)
    assert looks_non_english(spaced) is False


@given(
    st.lists(st.text(alphabet=ASCII_LOWER + "çöüğışİĞŞ", min_size=2, max_size=8), max_size=2),
)
def test_fewer_than_three_words_is_never_flagged_whatever_the_letters(words: list[str]) -> None:
    assert looks_non_english(" ".join(words)) is False


@given(
    st.text(alphabet=ASCII_LOWER, min_size=1, max_size=8),
    st.text(alphabet=ASCII_LOWER, min_size=1, max_size=8),
    st.text(alphabet=ASCII_LOWER, min_size=1, max_size=8),
    st.sampled_from(list("ğışĞŞ")),
    st.integers(min_value=0, max_value=2),
)
def test_three_words_one_with_a_strong_letter_is_always_flagged(
    a: str, b: str, c: str, letter: str, which: int
) -> None:
    words = [a + "x", b + "x", c + "x"]
    words[which] = words[which] + letter
    assert looks_non_english(" ".join(words)) is True


@given(st.text(), st.text(alphabet=" .,;:!?0123456789+-*/="))
def test_appending_non_letters_does_not_change_the_answer(text: str, tail: str) -> None:
    # Letters are the only thing that makes words; a separator first keeps runs apart.
    assert looks_non_english(text + " " + tail) == looks_non_english(text)


@given(st.text(alphabet=ASCII_LOWER + " ", max_size=80))
def test_plain_ascii_without_turkish_words_is_never_flagged_by_rule_3(text: str) -> None:
    # ASCII text has no strong letter; it can only be flagged by the word-set rule, which needs
    # two distinct Turkish common words.
    turkish = turkish_words()
    distinct_turkish = {w for w in text.split() if w in turkish}
    if len(distinct_turkish) < 2:
        assert looks_non_english(text) is False
