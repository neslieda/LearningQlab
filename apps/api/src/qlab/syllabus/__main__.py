"""Load a syllabus reference file: `python -m qlab.syllabus content/reference/<file>.json`."""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy.orm import Session

from qlab.database import make_engine
from qlab.syllabus.reference import SyllabusReference
from qlab.syllabus.service import load_reference


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    reference = SyllabusReference.model_validate_json(Path(argv[0]).read_text(encoding="utf-8"))
    with Session(make_engine()) as session, session.begin():
        version_id = load_reference(session, reference)
    print(f"loaded {len(reference.nodes)} nodes into syllabus version {version_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
