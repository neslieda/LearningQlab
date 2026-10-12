"""Syllabus service: loads reference data and answers vocabulary questions for other modules."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from qlab.syllabus.models import ExamFormat, Program, Subject, SyllabusNode, SyllabusVersion
from qlab.syllabus.reference import ExamFormatDefinition, SyllabusReference


class ReferenceConflict(Exception):
    """A reference file would remove something that already exists in the database."""


@dataclass(frozen=True)
class Vocabulary:
    """The labels (codes, not titles) a question may use under one syllabus version."""

    exam_sections: frozenset[str]
    command_terms: frozenset[str]
    node_codes: frozenset[str]
    # Nodes without children: the ones a question is normally tagged with.
    leaf_node_codes: frozenset[str]


def _find_version(
    session: Session, *, program: str, subject: str, version: str
) -> SyllabusVersion | None:
    return session.scalars(
        select(SyllabusVersion)
        .join(Subject, Subject.id == SyllabusVersion.subject_id)
        .join(Program, Program.id == Subject.program_id)
        .where(Program.code == program, Subject.code == subject, SyllabusVersion.code == version)
    ).one_or_none()


def _nodes(session: Session, syllabus_version_id: uuid.UUID) -> list[SyllabusNode]:
    return list(
        session.scalars(
            select(SyllabusNode)
            .where(SyllabusNode.syllabus_version_id == syllabus_version_id)
            .order_by(SyllabusNode.position)
        )
    )


def _exam_formats(session: Session, syllabus_version_id: uuid.UUID) -> list[ExamFormat]:
    return list(
        session.scalars(
            select(ExamFormat).where(ExamFormat.syllabus_version_id == syllabus_version_id)
        )
    )


def _check_nothing_dropped(
    reference: SyllabusReference, nodes: list[SyllabusNode], exam_format: ExamFormat | None
) -> None:
    dropped = {n.code for n in nodes} - {n.code for n in reference.nodes}
    if dropped:
        raise ReferenceConflict(f"reference file drops existing nodes: {sorted(dropped)}")
    if exam_format is None:
        return
    current = ExamFormatDefinition.model_validate(exam_format.definition)
    sections = {s.code for s in current.sections} - {s.code for s in reference.exam_format.sections}
    if sections:
        raise ReferenceConflict(f"reference file drops exam sections: {sorted(sections)}")
    terms = set(current.command_terms) - set(reference.exam_format.command_terms)
    if terms:
        raise ReferenceConflict(f"reference file drops command terms: {sorted(terms)}")


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
    codes = {
        "program": reference.program.code,
        "subject": reference.subject.code,
        "version": reference.syllabus_version.code,
    }
    version = _find_version(session, **codes)
    nodes = _nodes(session, version.id) if version is not None else []
    formats = _exam_formats(session, version.id) if version is not None else []
    exam_format = next((f for f in formats if f.code == reference.exam_format.code), None)
    _check_nothing_dropped(reference, nodes, exam_format)

    program = session.scalars(select(Program).where(Program.code == codes["program"])).one_or_none()
    if program is None:
        program = Program(code=codes["program"], name=reference.program.name)
        session.add(program)
        session.flush()
    program.name = reference.program.name
    subject = session.scalars(
        select(Subject).where(Subject.program_id == program.id, Subject.code == codes["subject"])
    ).one_or_none()
    if subject is None:
        subject = Subject(program_id=program.id, code=codes["subject"], name=reference.subject.name)
        session.add(subject)
        session.flush()
    subject.name = reference.subject.name
    if version is None:
        version = SyllabusVersion(
            subject_id=subject.id, code=codes["version"], title=reference.syllabus_version.title
        )
        session.add(version)
        session.flush()
    version.title = reference.syllabus_version.title

    by_code = {n.code: n for n in nodes}
    for position, entry in enumerate(reference.nodes):
        # The reference guarantees a parent is listed, and so stored, before its children.
        parent_id = by_code[entry.parent].id if entry.parent is not None else None
        node = by_code.get(entry.code)
        if node is None:
            node = SyllabusNode(syllabus_version_id=version.id, code=entry.code)
            by_code[entry.code] = node
            session.add(node)
        node.parent_id = parent_id
        node.title = entry.title
        node.position = position
        node.attributes = dict(entry.attributes)
        session.flush()

    definition = ExamFormatDefinition(
        sections=reference.exam_format.sections, command_terms=reference.exam_format.command_terms
    ).model_dump(mode="json")
    if exam_format is None:
        exam_format = ExamFormat(
            syllabus_version_id=version.id, code=reference.exam_format.code, definition=definition
        )
        session.add(exam_format)
    exam_format.definition = definition
    session.flush()
    return version.id


def find_syllabus_version(
    session: Session, *, program: str, subject: str, version: str
) -> uuid.UUID | None:
    """Id of the syllabus version with these three codes, or None."""
    row = _find_version(session, program=program, subject=subject, version=version)
    return None if row is None else row.id


def get_vocabulary(session: Session, syllabus_version_id: uuid.UUID) -> Vocabulary:
    """Vocabulary of one syllabus version. Unknown id, or no exam format: LookupError.

    If a version has several exam formats, their sections and command terms are combined.
    """
    formats = _exam_formats(session, syllabus_version_id)
    if not formats:
        raise LookupError(f"no exam format for syllabus version {syllabus_version_id}")
    definitions = [ExamFormatDefinition.model_validate(f.definition) for f in formats]
    nodes = _nodes(session, syllabus_version_id)
    parents = {n.parent_id for n in nodes}
    return Vocabulary(
        exam_sections=frozenset(s.code for d in definitions for s in d.sections),
        command_terms=frozenset(t for d in definitions for t in d.command_terms),
        node_codes=frozenset(n.code for n in nodes),
        leaf_node_codes=frozenset(n.code for n in nodes if n.id not in parents),
    )


def node_ids(
    session: Session, syllabus_version_id: uuid.UUID, codes: frozenset[str]
) -> dict[str, uuid.UUID]:
    """Map node codes to ids within one version. Any unknown code: LookupError."""
    found = {n.code: n.id for n in _nodes(session, syllabus_version_id) if n.code in codes}
    missing = codes - found.keys()
    if missing:
        raise LookupError(f"unknown syllabus nodes: {sorted(missing)}")
    return found
