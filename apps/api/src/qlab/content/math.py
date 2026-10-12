"""Save-time check of every math node (CLAUDE.md rule 6, docs/DATA_ARCHITECTURE.md section 3.4).

Two layers. First a closed list of LaTeX commands, checked here: anything else is refused before
it reaches a renderer. Then the pinned KaTeX itself, run as a short-lived Node process
(`apps/api/katex/render.mjs`), so the server accepts exactly what the web renderer can show.

LaTeX is untrusted input (authors now, model output later). It travels as JSON on stdin, never
on a command line; the Node process runs with file-system read access to the KaTeX package
only and a time limit. If the renderer cannot be run, nothing is saved: `RendererUnavailable`.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from qlab.content.schema import MathBlock, MathInline, QuestionDocument, iter_inlines

KATEX_VERSION = "0.19.0"
MAX_LATEX_LENGTH = 2000
MAX_MATH_NODES = 2000
RENDER_TIMEOUT_SECONDS = 20

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
    # Structures taking arguments
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

_COMMAND = re.compile(r"\\([A-Za-z]+|.|$)", re.DOTALL)
_ENVIRONMENT = re.compile(r"\\(?:begin|end)\s*\{([^{}]*)\}")


class RendererUnavailable(Exception):
    """KaTeX could not be run or answered unexpectedly. Nothing may be saved."""


@dataclass(frozen=True)
class MathNode:
    latex: str
    display: bool


def math_nodes(document: QuestionDocument) -> Iterator[MathNode]:
    """Every math node of the question, in reading order."""
    for doc in document.docs():
        for block in doc.content:
            if isinstance(block, MathBlock):
                yield MathNode(block.attrs.latex, display=True)
        for inline in iter_inlines(doc):
            if isinstance(inline, MathInline):
                yield MathNode(inline.attrs.latex, display=False)


def disallowed(latex: str) -> list[str]:
    """What the closed list refuses in one LaTeX source, as readable items; empty if nothing."""
    problems: list[str] = []
    if len(latex) > MAX_LATEX_LENGTH:
        problems.append(f"longer than {MAX_LATEX_LENGTH} characters")
    if any(ord(c) < 32 and c not in "\t\n\r" for c in latex):
        problems.append("control character")
    for match in _COMMAND.finditer(latex):
        name = match.group(1)
        if name.isalpha() and name.isascii():
            if name not in ALLOWED_COMMANDS:
                problems.append(f"command \\{name}")
        elif name not in ALLOWED_ESCAPES or name == "":
            problems.append(f"escape \\{name}" if name else "trailing backslash")
    for environment in _ENVIRONMENT.findall(latex):
        if environment not in ALLOWED_ENVIRONMENTS:
            problems.append(f"environment {environment or '(empty)'}")
    return list(dict.fromkeys(problems))


def _katex_dir() -> Path:
    return Path(os.environ.get(KATEX_DIR_ENV) or _DEFAULT_KATEX_DIR)


# Whether a node renders depends only on the node and the pinned KaTeX, so answers are kept
# for the life of the process.
_CACHE: dict[MathNode, str | None] = {}
_CACHE_LIMIT = 20_000


def render_errors(nodes: Sequence[MathNode]) -> list[str | None]:
    """Ask KaTeX to render each node; one entry per node, None when it rendered.

    Raises RendererUnavailable when Node or the KaTeX package is missing, the process fails or
    times out, the answer is malformed, or the KaTeX version is not the pinned one.
    """
    unknown = [node for node in dict.fromkeys(nodes) if node not in _CACHE]
    if unknown:
        if len(_CACHE) + len(unknown) > _CACHE_LIMIT:
            _CACHE.clear()
        _CACHE.update(zip(unknown, _run_katex(unknown), strict=True))
    return [_CACHE[node] for node in nodes]


def _run_katex(nodes: Sequence[MathNode]) -> list[str | None]:
    directory = _katex_dir()
    script = directory / "render.mjs"
    node = shutil.which(os.environ.get(NODE_BIN_ENV) or "node")
    if node is None or not script.is_file():
        raise RendererUnavailable("node or the KaTeX renderer script was not found")
    payload = json.dumps({"items": [{"latex": n.latex, "display": n.display} for n in nodes]})
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, input on stdin, no shell
            [node, "--permission", f"--allow-fs-read={directory}", str(script)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=RENDER_TIMEOUT_SECONDS,
            cwd=directory,
            env={"PATH": os.environ.get("PATH", ""), "NODE_ENV": "production"},
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RendererUnavailable(
            f"the KaTeX renderer did not run: {type(error).__name__}"
        ) from None
    if completed.returncode != 0:
        raise RendererUnavailable(f"the KaTeX renderer exited with status {completed.returncode}")
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


def check(document: QuestionDocument) -> tuple[str, ...]:
    """Problems with the question's math, for the author; empty when every node renders.

    A node refused by the closed list is not sent to the renderer.
    """
    nodes = list(dict.fromkeys(math_nodes(document)))
    if len(nodes) > MAX_MATH_NODES:
        return (f"more than {MAX_MATH_NODES} distinct math nodes",)
    problems: list[str] = []
    renderable: list[MathNode] = []
    for node in nodes:
        refused = disallowed(node.latex)
        if refused:
            problems.append(f"math `{_quote(node.latex)}`: not allowed: {', '.join(refused)}")
        else:
            renderable.append(node)
    for node, error in zip(renderable, render_errors(renderable), strict=True):
        if error is not None:
            problems.append(f"math `{_quote(node.latex)}`: does not render: {error}")
    return tuple(problems)
