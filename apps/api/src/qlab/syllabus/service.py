"""Syllabus service: loads reference data and answers vocabulary questions for other modules."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from qlab.syllabus.reference import SyllabusReference


class ReferenceConflict(Exception):
    """A reference file would remove something that already exists in the database."""


@dataclass(frozen=True)
class Vocabulary:
    """The labels a question may use under one syllabus version."""

    exam_sections: frozenset[str]
    command_terms: frozenset[str]
    node_codes: frozenset[str]
    # Nodes without children: the ones a question is normally tagged with.
    leaf_node_codes: frozenset[str]


def load_reference(session: Session, reference: SyllabusReference) -> uuid.UUID:
    """Create or update one syllabus version from a reference file; return its id.

    Runs inside the caller's transaction and is idempotent: loading the same file twice leaves
    the same rows with the same ids. Programme, subject, version, nodes and exam format are
    matched by code; titles, names, positions (list order, from 0), parents, attributes and the
    exam format definition are updated to match the file; new nodes are inserted.

    Nothing is ever deleted. If the database holds a node of this version that the file no
    longer lists, or an exam section or command term that the file drops, ReferenceConflict is
    raised and nothing is changed, because questions may refer to them.
    """
    raise NotImplementedError


def find_syllabus_version(
    session: Session, *, program: str, subject: str, version: str
) -> uuid.UUID | None:
    """Id of the syllabus version with these three codes, or None."""
    raise NotImplementedError


def get_vocabulary(session: Session, syllabus_version_id: uuid.UUID) -> Vocabulary:
    """Vocabulary of one syllabus version. Unknown id, or no exam format: LookupError."""
    raise NotImplementedError


def node_ids(
    session: Session, syllabus_version_id: uuid.UUID, codes: frozenset[str]
) -> dict[str, uuid.UUID]:
    """Map node codes to ids within one version. Any unknown code: LookupError."""
    raise NotImplementedError
