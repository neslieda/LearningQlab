"""Command line of the pilot question sets: `python -m qlab.content.pilot <command>`.

`convert` turns docs/pilot/*-pilot-questions.md into content/pilot/*.json and the conversion
report (docs/pilot/IMPORT_RULES.md); `convert --check` verifies that the committed files equal a
fresh conversion. Every command is a `run_<name>(args)` function registered in `build_parser`.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

from qlab.content import math as qmath
from qlab.content.pilot.markdown import (
    SOURCE_SUFFIX,
    ConversionError,
    ConversionFailed,
    Tally,
    convert_markdown,
    load_vocabulary,
)
from qlab.content.pilot.report import render_report

REPORT_NAME = "CONVERSION_REPORT.md"
_SKIP_REF = re.compile(r"^pilot/([a-z0-9][a-z0-9-]*)#([1-9][0-9]*)$")


def default_root() -> Path:
    """The repository root, found from this file (apps/api/src/qlab/content/pilot/__main__.py)."""
    return Path(__file__).resolve().parents[6]


def _skips(refs: Sequence[str]) -> dict[str, set[int]]:
    skips: dict[str, set[int]] = defaultdict(set)
    for ref in refs:
        found = _SKIP_REF.match(ref)
        if found is None:
            raise SystemExit(f"--skip {ref!r}: expected pilot/<file stem>#<question number>")
        skips[found.group(1)].add(int(found.group(2)))
    return skips


def _convert_all(root: Path, skip_refs: Sequence[str]) -> tuple[dict[str, str], list[str]]:
    """Generated file name -> text, and the problems found (empty when everything converted)."""
    sources = sorted((root / "docs" / "pilot").glob(f"*{SOURCE_SUFFIX}"))
    if not sources:
        return {}, [f"no *{SOURCE_SUFFIX} files under {root / 'docs' / 'pilot'}"]
    vocabulary = load_vocabulary(root / "content" / "reference" / "dp-physics-2025-syllabus.json")
    skips = _skips(skip_refs)
    stems = [source.name.removesuffix(SOURCE_SUFFIX) for source in sources]
    for stem in skips:
        if stem not in stems:
            return {}, [f"--skip names an unknown file stem {stem!r}"]
    tally = Tally()
    outputs: dict[str, str] = {}
    problems: list[str] = []
    for source, stem in zip(sources, stems, strict=True):
        try:
            pilot = convert_markdown(
                source.read_bytes(), stem, vocabulary, tally, skip=skips.get(stem, ())
            )
        except ConversionFailed as failed:
            problems.extend(str(error) for error in failed.errors)
            continue
        except ConversionError as error:
            problems.append(str(error))
            continue
        for question in pilot.questions:
            for problem in qmath.check(question.document):
                problems.append(f"{pilot.source_file}, {question.source_ref}: {problem}")
        outputs[f"{stem}.json"] = pilot.to_json()
    if problems:
        return {}, problems
    outputs[REPORT_NAME] = render_report(tally, stems)
    return outputs, []


def run_convert(args: argparse.Namespace) -> int:
    """Write content/pilot (or, with --check, compare it with a fresh conversion)."""
    root: Path = (args.root or default_root()).resolve()
    if not (root / "docs" / "pilot").is_dir():
        print(f"{root}: no docs/pilot directory; pass --root", file=sys.stderr)
        return 2
    try:
        outputs, problems = _convert_all(root, args.skip)
    except qmath.RendererUnavailable as error:
        print(f"math check could not run: {error}", file=sys.stderr)
        return 2
    if problems:
        print("Conversion stopped; no file was written or compared:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    target = root / "content" / "pilot"
    if args.check:
        differences = []
        for name, text in sorted(outputs.items()):
            path = target / name
            if not path.is_file():
                differences.append(f"content/pilot/{name} is missing")
            elif path.read_bytes() != text.encode("utf-8"):
                differences.append(f"content/pilot/{name} differs from a fresh conversion")
        if target.is_dir():
            for path in sorted(target.glob("*.json")):
                if path.name not in outputs:
                    differences.append(f"content/pilot/{path.name} has no source file")
        if differences:
            print("content/pilot is out of date:", file=sys.stderr)
            for difference in differences:
                print(f"  {difference}", file=sys.stderr)
            print(
                "Run `python -m qlab.content.pilot convert` and commit the result.",
                file=sys.stderr,
            )
            return 1
        print(f"content/pilot matches a fresh conversion ({len(outputs) - 1} files + report).")
        return 0

    target.mkdir(parents=True, exist_ok=True)
    for path in target.glob("*.json"):
        if path.name not in outputs:
            path.unlink()
    for name, text in outputs.items():
        (target / name).write_bytes(text.encode("utf-8"))
    print(f"Wrote {len(outputs) - 1} files and {REPORT_NAME} to content/pilot.")
    return 0


def run_load(args: argparse.Namespace) -> int:
    """Import the converted files (docs/pilot/IMPORT_RULES.md section 7). One transaction: either
    every question is imported or none."""
    # Imported here so that `convert` needs neither a database nor its driver.
    from sqlalchemy.orm import Session

    from qlab.content import math
    from qlab.content.pilot import loader
    from qlab.database import make_engine

    root = (args.root or default_root()).resolve()
    math.ensure_renderer()
    with Session(make_engine()) as session, session.begin():
        report = loader.load_pilot_directory(
            session, root / "content" / "pilot", holder=args.holder
        )
        for ref, status in report.skipped.items():
            print(f"skipped {ref}: latest version is {status}")
        if args.dry_run:
            session.rollback()
    print(("dry run: " if args.dry_run else "") + report.summary())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m qlab.content.pilot", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    convert = commands.add_parser("convert", help="Markdown -> content/pilot/*.json and report")
    convert.add_argument("--check", action="store_true", help="compare, do not write")
    convert.add_argument("--root", type=Path, default=None, help="repository root")
    convert.add_argument(
        "--skip",
        action="append",
        default=[],
        metavar="REF",
        help="development aid: leave out pilot/<file stem>#<number> (listed in the report)",
    )
    convert.set_defaults(run=run_convert)

    load = commands.add_parser("load", help="import content/pilot/*.json as draft questions")
    load.add_argument("--root", type=Path, default=None, help="repository root")
    load.add_argument("--holder", default="LearningQlab", help="holder of the own-content rights")
    load.add_argument("--dry-run", action="store_true", help="do everything, then roll back")
    load.set_defaults(run=run_load)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.run(args))


if __name__ == "__main__":
    sys.exit(main())
