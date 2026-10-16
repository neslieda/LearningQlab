"""Command line of the pilot question sets: `python -m qlab.content.pilot <command>`.

`convert` turns docs/pilot/*-pilot-questions.md into content/pilot/*.json and the conversion
report (docs/pilot/IMPORT_RULES.md); `convert --check` verifies that the committed files equal a
fresh conversion. Every command is a `run_<name>(args)` function registered in `build_parser`.
"""

from __future__ import annotations

import argparse
import sys
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
from qlab.content.schema import non_english_message, non_english_paths

REPORT_NAME = "CONVERSION_REPORT.md"


def default_root() -> Path:
    """The repository root, found from this file (apps/api/src/qlab/content/pilot/__main__.py)."""
    return Path(__file__).resolve().parents[6]


def _unsafe(path: Path, base: Path, root: Path) -> str | None:
    """Why `path` may be neither read nor written: a symbolic link, or not inside `base`."""
    shown = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
    if path.is_symlink():
        return f"{shown} is a symbolic link"
    if not path.resolve().is_relative_to(base.resolve()):
        return f"{shown} resolves outside {base.relative_to(root).as_posix()}"
    return None


def _layout_problems(root: Path) -> list[str]:
    """Symbolic links and escapes in docs/pilot, content/pilot and the files in them."""
    problems: list[str] = []
    docs = root / "docs" / "pilot"
    target = root / "content" / "pilot"
    for directory, base in ((docs, root / "docs"), (target, root / "content")):
        if directory.exists() or directory.is_symlink():
            problem = _unsafe(directory, base, root)
            if problem:
                problems.append(problem)
    if problems:
        return problems
    for directory in (docs, target):
        if directory.is_dir():
            for entry in sorted(directory.iterdir()):
                problem = _unsafe(entry, directory, root)
                if problem:
                    problems.append(problem)
    return problems


def _convert_all(root: Path) -> tuple[dict[str, str], list[str]]:
    """Generated file name -> text, and the problems found (empty when everything converted)."""
    sources = sorted((root / "docs" / "pilot").glob(f"*{SOURCE_SUFFIX}"))
    if not sources:
        return {}, [f"no *{SOURCE_SUFFIX} files under {root / 'docs' / 'pilot'}"]
    vocabulary = load_vocabulary(root / "content" / "reference" / "dp-physics-2025-syllabus.json")
    stems = [source.name.removesuffix(SOURCE_SUFFIX) for source in sources]
    tally = Tally()
    outputs: dict[str, str] = {}
    problems: list[str] = []
    for source, stem in zip(sources, stems, strict=True):
        if not source.is_file():
            problems.append(f"{source.name} is not a regular file")
            continue
        try:
            pilot = convert_markdown(source.read_bytes(), stem, vocabulary, tally)
        except ConversionFailed as failed:
            problems.extend(str(error) for error in failed.errors)
            continue
        except ConversionError as error:
            problems.append(str(error))
            continue
        for question in pilot.questions:
            foreign = non_english_paths(question.document)
            if foreign:
                problems.append(
                    f"{pilot.source_file}, {question.source_ref}: {non_english_message(foreign)}"
                )
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
    refused = _layout_problems(root)
    if refused:
        print("Refused; nothing was read, written or compared:", file=sys.stderr)
        for problem in refused:
            print(f"  {problem}", file=sys.stderr)
        return 2
    try:
        outputs, problems = _convert_all(root)
    except qmath.RendererUnavailable as error:
        print(f"math check could not run: {error}", file=sys.stderr)
        return 2
    if problems:
        print("Conversion stopped; no file was written or compared:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    target = root / "content" / "pilot"
    strays = []
    if target.is_dir():
        for path in sorted(target.iterdir()):
            if path.name in outputs:
                continue
            if path.suffix == ".json" and path.is_file():
                strays.append(f"content/pilot/{path.name} has no source file")
            else:
                strays.append(f"content/pilot/{path.name} is not a generated file")
    if args.check:
        differences = []
        for name, text in sorted(outputs.items()):
            path = target / name
            if not path.is_file():
                differences.append(f"content/pilot/{name} is missing")
            elif path.read_bytes() != text.encode("utf-8"):
                differences.append(f"content/pilot/{name} differs from a fresh conversion")
        differences.extend(strays)
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
    for path in sorted(target.glob("*.json")):
        if path.name not in outputs:
            path.unlink()
    for name, text in outputs.items():
        (target / name).write_bytes(text.encode("utf-8"))
    for stray in strays:
        if "not a generated file" in stray:
            print(f"warning: {stray}", file=sys.stderr)
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
    engine = make_engine()
    print(f"database: {engine.url.host}/{engine.url.database}")
    try:
        with Session(engine) as session, session.begin():
            report = loader.load_pilot_directory(
                session,
                root,
                holder=args.holder,
                operator=args.operator,
                create_rights=args.create_rights,
            )
            if args.dry_run:
                session.rollback()
    except (loader.OwnContentRightsError, loader.SourceMismatch, LookupError) as error:
        # Expected refusals: nothing was written. Other errors keep their traceback.
        print(f"import refused: {error}", file=sys.stderr)
        return 2
    for ref, reason in report.skipped.items():
        print(f"skipped {ref}: {reason}")
    for ref in report.blocked:
        print(f"blocked {ref}: its rights record does not permit display")
    print(("dry run: " if args.dry_run else "") + report.summary())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m qlab.content.pilot", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    convert = commands.add_parser("convert", help="Markdown -> content/pilot/*.json and report")
    convert.add_argument("--check", action="store_true", help="compare, do not write")
    convert.add_argument("--root", type=Path, default=None, help="repository root")
    convert.set_defaults(run=run_convert)

    load = commands.add_parser("load", help="import content/pilot/*.json as draft questions")
    load.add_argument("--root", type=Path, default=None, help="repository root")
    load.add_argument("--holder", default="LearningQlab", help="holder of the own-content rights")
    load.add_argument(
        "--operator", required=True, help="opaque account id of the person running the import"
    )
    load.add_argument(
        "--create-rights",
        action="store_true",
        help="open the platform's own-content rights record if none exists (D-58)",
    )
    load.add_argument("--dry-run", action="store_true", help="do everything, then roll back")
    load.set_defaults(run=run_load)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.run(args))


if __name__ == "__main__":
    sys.exit(main())
