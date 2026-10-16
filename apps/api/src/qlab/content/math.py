r"""Save-time check of every math node (CLAUDE.md rule 6, docs/DATA_ARCHITECTURE.md section 3.4).

Two layers. First a closed list, checked here: the source is printable ASCII, every command,
environment and escape is on the list, and a few size limits hold; anything else is refused
before it reaches a renderer. One symbol therefore has one spelling (`\times`, never the character).
Then the pinned KaTeX itself, run as a short-lived Node process (`apps/api/katex/render.mjs`),
so the server accepts exactly what the web renderer can show.

LaTeX is untrusted input (authors now, model output later). It travels as JSON on stdin, never
on a command line. The Node process gets no inherited environment, a memory and a time limit,
no code generation from strings, and Node's permission model with read access to the KaTeX
package only: no file writes, child processes or workers. Network access is denied by that
model from Node 25 on; on Node 24 it is not, so deployments block the renderer's egress at
the container level (docs/SECURITY.md section 7). If the renderer cannot be run, nothing is
saved: `RendererUnavailable`.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from qlab.content.schema import MathBlock, MathInline, QuestionDocument, iter_inlines

KATEX_VERSION = "0.19.0"
MAX_LATEX_LENGTH = 2000
MAX_MATH_NODES = 2000
# Bounds on what one node may ask a browser to lay out.
MAX_GROUP_DEPTH = 40
MAX_ALIGNMENT_TABS = 200
MAX_LINE_BREAKS = 100
RENDER_TIMEOUT_SECONDS = 10
RENDERER_MEMORY_MB = 256

KATEX_DIR_ENV = "QLAB_KATEX_DIR"
NODE_BIN_ENV = "QLAB_NODE_BIN"
_DEFAULT_KATEX_DIR = Path(__file__).resolve().parents[3] / "katex"

# Each allowed command with the smallest expression that uses it; the examples are rendered in
# the tests, so the list cannot name a command the pinned KaTeX does not know.
ALLOWED_COMMANDS: dict[str, str] = {
    # Greek letters
    **{
        name: rf"\{name}"
        for name in [
            "alpha",
            "beta",
            "gamma",
            "delta",
            "epsilon",
            "varepsilon",
            "zeta",
            "eta",
            "theta",
            "vartheta",
            "iota",
            "kappa",
            "lambda",
            "mu",
            "nu",
            "xi",
            "pi",
            "rho",
            "sigma",
            "tau",
            "upsilon",
            "phi",
            "varphi",
            "chi",
            "psi",
            "omega",
            "Gamma",
            "Delta",
            "Theta",
            "Lambda",
            "Xi",
            "Pi",
            "Sigma",
            "Phi",
            "Psi",
            "Omega",
        ]
    },
    # Symbols, operators and relations
    **{
        name: rf"a \{name} b"
        for name in [
            "times",
            "cdot",
            "div",
            "pm",
            "mp",
            "le",
            "leq",
            "ge",
            "geq",
            "ne",
            "neq",
            "approx",
            "equiv",
            "propto",
            "sim",
            "simeq",
            "ll",
            "gg",
            "to",
            "rightarrow",
            "leftarrow",
            "Rightarrow",
            "Leftrightarrow",
            "leftrightarrow",
            "rightleftharpoons",
            "uparrow",
            "downarrow",
            "mapsto",
            "circ",
            "perp",
            "parallel",
            "mid",
            "in",
        ]
    },
    **{
        name: rf"\{name}"
        for name in [
            "infty",
            "partial",
            "nabla",
            "hbar",
            "ell",
            "degree",
            "angle",
            "prime",
            "cdots",
            "ldots",
            "dots",
            "langle",
            "rangle",
            "lvert",
            "rvert",
            "lVert",
            "rVert",
            "quad",
            "qquad",
        ]
    },
    # Named functions
    **{
        name: rf"\{name} x"
        for name in [
            "sin",
            "cos",
            "tan",
            "arcsin",
            "arccos",
            "arctan",
            "sinh",
            "cosh",
            "tanh",
            "ln",
            "log",
            "exp",
            "lim",
            "max",
            "min",
        ]
    },
    **{
        name: rf"a \{name} b"
        for name in [
            "odot",
            "otimes",
            "bullet",
            "leqslant",
            "geqslant",
            "lesssim",
            "gtrsim",
            "cong",
            "Leftarrow",
            "implies",
            "longrightarrow",
            "updownarrow",
        ]
    },
    **{
        name: rf"\{name}"
        for name in ["therefore", "because", "Upsilon", "vdots", "ddots", "vert", "oint"]
    },
    **{name: rf"\{name} x" for name in ["cot", "sec", "csc", "lg"]},
    # Structures taking arguments
    "mathcal": r"\mathcal{E}",
    "textrm": r"\textrm{m}",
    "phantom": r"a \phantom{b} c",
    "cancel": r"\cancel{x}",
    "not": r"a \not\propto b",
    "overset": r"\overset{a}{=}",
    "underset": r"\underset{a}{=}",
    "stackrel": r"\stackrel{a}{=}",
    "middle": r"\left( a \middle| b \right)",
    "bigg": r"\bigg( x \bigg)",
    "Bigg": r"\Bigg( x \Bigg)",
    "biggl": r"\biggl( x \biggr)",
    "biggr": r"\biggl[ x \biggr]",
    "Biggl": r"\Biggl( x \Biggr)",
    "Biggr": r"\Biggl[ x \Biggr]",
    "hline": r"\begin{array}{c} a \\ \hline b \end{array}",
    "frac": r"\frac{a}{b}",
    "tfrac": r"\tfrac{a}{b}",
    "dfrac": r"\dfrac{a}{b}",
    "binom": r"\binom{n}{k}",
    "sqrt": r"\sqrt[3]{x}",
    "sum": r"\sum_{i=1}^{n} x_i",
    "prod": r"\prod_{i=1}^{n} x_i",
    "int": r"\int_a^b f",
    "left": r"\left( x \right)",
    "right": r"\left[ x \right]",
    "big": r"\big( x \big)",
    "Big": r"\Big( x \Big)",
    "bigl": r"\bigl( x \bigr)",
    "bigr": r"\bigl[ x \bigr]",
    "Bigl": r"\Bigl( x \Bigr)",
    "Bigr": r"\Bigl[ x \Bigr]",
    "vec": r"\vec{v}",
    "hat": r"\hat{x}",
    "bar": r"\bar{x}",
    "dot": r"\dot{x}",
    "ddot": r"\ddot{x}",
    "tilde": r"\tilde{x}",
    "overline": r"\overline{AB}",
    "underline": r"\underline{x}",
    "overrightarrow": r"\overrightarrow{AB}",
    "overbrace": r"\overbrace{a+b}^{n}",
    "underbrace": r"\underbrace{a+b}_{n}",
    "xrightarrow": r"A \xrightarrow{k} B",
    "text": r"\text{m s}",
    "mathrm": r"\mathrm{d}x",
    "mathbf": r"\mathbf{F}",
    "mathit": r"\mathit{ab}",
    "mathsf": r"\mathsf{A}",
    "boldsymbol": r"\boldsymbol{\omega}",
    "textbf": r"\textbf{all}",
    "textit": r"\textit{not}",
    "operatorname": r"\operatorname{sgn} x",
    "displaystyle": r"\displaystyle \frac{a}{b}",
    "textstyle": r"\textstyle \frac{a}{b}",
    "begin": r"\begin{aligned} a &= b \end{aligned}",
    "end": r"\begin{cases} a \\ b \end{cases}",
}
ALLOWED_ENVIRONMENTS: dict[str, str] = {
    "aligned": r"\begin{aligned} a &= b \\ c &= d \end{aligned}",
    "cases": r"\begin{cases} a & x > 0 \\ b & x \le 0 \end{cases}",
    "array": r"\begin{array}{cc} a & b \\ c & d \end{array}",
    "matrix": r"\begin{matrix} a & b \\ c & d \end{matrix}",
    "pmatrix": r"\begin{pmatrix} a \\ b \end{pmatrix}",
    "bmatrix": r"\begin{bmatrix} a \\ b \end{bmatrix}",
}
# A backslash followed by one of these is spacing or an escaped character.
ALLOWED_ESCAPES = frozenset(",;:! \\{}%&#_$|")

# Mirrors KaTeX's own lexer, where "@" is a letter: \name@ is a different, internal command.
_COMMAND = re.compile(r"\\([A-Za-z@]+|.|$)", re.DOTALL)
_ENVIRONMENT = re.compile(r"\\(begin|end)(\{([A-Za-z*]*)\})?")
_LINE_BREAK_OPTION = re.compile(r"\\\\\s*\[")


class RendererUnavailable(Exception):
    """KaTeX could not be run or answered unexpectedly. Nothing may be saved."""


@dataclass(frozen=True)
class MathNode:
    latex: str
    display: bool


def math_nodes(document: QuestionDocument) -> Iterator[MathNode]:
    """Every math node of the question. Rich-text documents come in reading order; within one
    of them, block formulas come before inline ones."""
    for doc in document.docs():
        for block in doc.content:
            if isinstance(block, MathBlock):
                yield MathNode(block.attrs.latex, display=True)
        for inline in iter_inlines(doc):
            if isinstance(inline, MathInline):
                yield MathNode(inline.attrs.latex, display=False)


def _depth(latex: str) -> int:
    depth = deepest = 0
    for char in re.sub(r"\\.", "", latex, flags=re.DOTALL):
        if char == "{":
            depth += 1
            deepest = max(deepest, depth)
        elif char == "}":
            depth -= 1
    return deepest


def disallowed(latex: str) -> list[str]:
    r"""What the closed list refuses in one LaTeX source, as readable items; empty if nothing.

    Refused: more than MAX_LATEX_LENGTH characters; any character that is not printable ASCII,
    tab or newline; an unescaped `%` (comments); a command, escape or environment that is not
    on the lists (a `\begin` or `\end` must be followed directly by `{name}`); a length option
    after a line break (`\\[...]`); groups nested deeper than MAX_GROUP_DEPTH; more than
    MAX_ALIGNMENT_TABS `&` or MAX_LINE_BREAKS `\\`.
    """
    problems: list[str] = []
    if len(latex) > MAX_LATEX_LENGTH:
        problems.append(f"longer than {MAX_LATEX_LENGTH} characters")
    if any(not (32 <= ord(c) < 127 or c in "\t\n") for c in latex):
        problems.append("character outside printable ASCII")
    without_escapes = re.sub(r"\\.", "", latex, flags=re.DOTALL)
    if "%" in without_escapes:
        problems.append("comment (%)")
    for match in _COMMAND.finditer(latex):
        name = match.group(1)
        if name == "":
            problems.append("trailing backslash")
        elif name[0].isalpha() or name[0] == "@":
            if name not in ALLOWED_COMMANDS:
                problems.append(f"command \\{name}")
        elif name not in ALLOWED_ESCAPES:
            problems.append(f"escape \\{name}")
    for match in _ENVIRONMENT.finditer(latex):
        if match.start() > 0 and latex[match.start() - 1] == "\\" and _is_escaped(latex, match):
            continue
        environment = match.group(3)
        if match.group(2) is None:
            problems.append(f"\\{match.group(1)} without an environment name")
        elif environment not in ALLOWED_ENVIRONMENTS:
            problems.append(f"environment {environment or '(empty)'}")
    if _LINE_BREAK_OPTION.search(latex):
        problems.append("length option after a line break")
    if _depth(latex) > MAX_GROUP_DEPTH:
        problems.append(f"groups nested deeper than {MAX_GROUP_DEPTH}")
    if without_escapes.count("&") > MAX_ALIGNMENT_TABS:
        problems.append(f"more than {MAX_ALIGNMENT_TABS} alignment tabs")
    if latex.count("\\\\") > MAX_LINE_BREAKS:
        problems.append(f"more than {MAX_LINE_BREAKS} line breaks")
    return list(dict.fromkeys(problems))


def _is_escaped(latex: str, match: re.Match[str]) -> bool:
    r"""True when the backslash that starts `match` is itself escaped (`\\begin` is a line
    break followed by the word "begin")."""
    backslashes = 0
    index = match.start() - 1
    while index >= 0 and latex[index] == "\\":
        backslashes += 1
        index -= 1
    return backslashes % 2 == 1


def _katex_dir() -> Path:
    return Path(os.environ.get(KATEX_DIR_ENV) or _DEFAULT_KATEX_DIR).resolve()


# Whether a node renders depends only on the node and the pinned KaTeX, so answers are kept
# for the life of the process. Failures to run the renderer are never kept.
_CACHE: dict[MathNode, str | None] = {}
_CACHE_LIMIT = 20_000
_CACHE_LOCK = threading.Lock()


def render_errors(nodes: Sequence[MathNode]) -> list[str | None]:
    """Ask KaTeX to render each node; one entry per node, None when it rendered.

    A node also fails when its rendered markup is larger than the renderer's output cap.
    Raises RendererUnavailable when Node or the KaTeX package is missing, the process fails or
    times out, the answer is malformed, or the KaTeX version is not the pinned one. Nodes
    answered earlier in this process are not rendered again.
    """
    with _CACHE_LOCK:
        answers = {node: _CACHE[node] for node in nodes if node in _CACHE}
    unknown = [node for node in dict.fromkeys(nodes) if node not in answers]
    if unknown:
        fresh = dict(zip(unknown, _run_katex(unknown), strict=True))
        answers.update(fresh)
        with _CACHE_LOCK:
            if len(_CACHE) + len(fresh) > _CACHE_LIMIT:
                _CACHE.clear()
            _CACHE.update(fresh)
    return [answers[node] for node in nodes]


def ensure_renderer() -> None:
    """Render one formula with nothing cached; raise RendererUnavailable if that fails.

    For process start-up: a deployment without Node, without `npm ci` in the KaTeX directory
    or with another KaTeX version should fail before it accepts work.
    """
    if _run_katex([MathNode("x", display=False)]) != [None]:
        raise RendererUnavailable("the KaTeX renderer could not render a trivial formula")


def _run_katex(nodes: Sequence[MathNode]) -> list[str | None]:
    directory = _katex_dir()
    script = directory / "render.mjs"
    node = shutil.which(os.environ.get(NODE_BIN_ENV) or "node")
    if node is None or not script.is_file():
        raise RendererUnavailable(
            f"node or {script.name} was not found; set {NODE_BIN_ENV} / {KATEX_DIR_ENV}"
        )
    payload = json.dumps({"items": [{"latex": n.latex, "display": n.display} for n in nodes]})
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, input on stdin, no shell
            [
                str(Path(node).resolve()),
                "--permission",
                f"--allow-fs-read={directory}",
                "--disallow-code-generation-from-strings",
                f"--max-old-space-size={RENDERER_MEMORY_MB}",
                str(script),
            ],
            input=payload,
            capture_output=True,
            text=True,
            timeout=RENDER_TIMEOUT_SECONDS,
            cwd=directory,
            env={"NODE_ENV": "production"},
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RendererUnavailable(
            f"the KaTeX renderer did not run: {type(error).__name__}"
        ) from None
    if completed.returncode != 0:
        # stderr is not quoted: it can echo the input.
        raise RendererUnavailable(
            f"the KaTeX renderer exited with status {completed.returncode}; check that "
            f"`npm ci` was run in {directory} and that Node is version 24 or later"
        )
    try:
        answer = json.loads(completed.stdout)
        version, results = answer["version"], answer["results"]
        errors = [None if r["ok"] is True else str(r["error"]) for r in results]
    except ValueError, KeyError, TypeError:
        raise RendererUnavailable("the KaTeX renderer gave a malformed answer") from None
    if version != KATEX_VERSION:
        raise RendererUnavailable(f"KaTeX {version} is installed; {KATEX_VERSION} is pinned")
    if len(errors) != len(nodes):
        raise RendererUnavailable("the KaTeX renderer answered for a different number of nodes")
    return errors


def _quote(latex: str) -> str:
    return latex if len(latex) <= 60 else latex[:57] + "..."


def _located(value: object, path: str, found: dict[MathNode, list[str]]) -> None:
    """Dotted path of every math node in the JSON form of a document, by node."""
    if isinstance(value, dict):
        kind = value.get("type")
        attrs = value.get("attrs")
        if kind in ("math_block", "math_inline") and isinstance(attrs, dict):
            latex = attrs.get("latex")
            if isinstance(latex, str):
                node = MathNode(latex, display=kind == "math_block")
                found.setdefault(node, []).append(f"{path}.attrs.latex" if path else "attrs.latex")
        for key, item in value.items():
            _located(item, f"{path}.{key}" if path else str(key), found)
    elif isinstance(value, list | tuple):
        for index, item in enumerate(value):
            _located(item, f"{path}.{index}" if path else str(index), found)


@dataclass(frozen=True)
class MathProblem:
    message: str
    # Dotted path of the node's `latex` inside the document (list indices as numbers), e.g.
    # `parts.0.mark_points.1.content.content.0.content.2.attrs.latex`; None for a problem
    # about the document as a whole.
    location: str | None


def _problems(document: QuestionDocument) -> list[tuple[MathNode | None, str]]:
    nodes = list(dict.fromkeys(math_nodes(document)))
    if len(nodes) > MAX_MATH_NODES:
        return [(None, f"more than {MAX_MATH_NODES} distinct math nodes")]
    problems: list[tuple[MathNode | None, str]] = []
    renderable: list[MathNode] = []
    for node in nodes:
        refused = disallowed(node.latex)
        if refused:
            problems.append(
                (node, f"math `{_quote(node.latex)}`: not allowed: {', '.join(refused)}")
            )
        else:
            renderable.append(node)
    for node, error in zip(renderable, render_errors(renderable), strict=True):
        if error is not None:
            problems.append((node, f"math `{_quote(node.latex)}`: does not render: {error}"))
    return problems


def check(document: QuestionDocument) -> tuple[str, ...]:
    """Problems with the question's math, for the author; empty when every node renders.

    A node refused by the closed list is not sent to the renderer. Raises
    RendererUnavailable when the renderer is needed and cannot be run.
    """
    return tuple(message for _, message in _problems(document))


MAX_PLACES_PER_NODE = 5


def check_located(document: QuestionDocument) -> tuple[MathProblem, ...]:
    """The same problems as `check`, one per place the offending node occurs (the same node
    used twice is reported at both places). A problem about the whole document, or a node whose
    place cannot be found, has location None."""
    problems = _problems(document)
    if not problems:
        return ()
    found: dict[MathNode, list[str]] = {}
    _located(document.model_dump(mode="json"), "", found)
    located: list[MathProblem] = []
    for node, message in problems:
        places = found.get(node) if node is not None else None
        if not places:
            located.append(MathProblem(message, None))
        else:
            located.extend(MathProblem(message, place) for place in places[:MAX_PLACES_PER_NODE])
    return tuple(located)
