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


@dataclass(frozen=True)
class TreeNode:
    code: str
    title: str
    # Code of the parent node; None for a top-level node.
    parent: str | None
    is_leaf: bool
    attributes: dict[str, str]


@dataclass(frozen=True)
class SyllabusTree:
    """One syllabus version, by codes. `nodes` are in syllabus order (position), so a parent
    comes before its children."""

    program: str
    subject: str
    version: str
    title: str
    status: str
    nodes: tuple[TreeNode, ...]
    # (code, title) of each exam section, in the order of the exam format.
    exam_sections: tuple[tuple[str, str], ...]
    command_terms: tuple[str, ...]


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


def _exam_format(session: Session, syllabus_version_id: uuid.UUID) -> ExamFormat | None:
    return session.scalars(
        select(ExamFormat).where(ExamFormat.syllabus_version_id == syllabus_version_id)
    ).one_or_none()


def _check_nothing_dropped(
    reference: SyllabusReference, nodes: list[SyllabusNode], exam_format: ExamFormat | None
) -> None:
    dropped = {n.code for n in nodes} - {n.code for n in reference.nodes}
    if dropped:
        raise ReferenceConflict(f"reference file drops existing nodes: {sorted(dropped)}")
    if exam_format is None:
        return
    if exam_format.code != reference.exam_format.code:
        raise ReferenceConflict(
            f"reference file renames the exam format {exam_format.code!r}; a version has one"
        )
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
    longer lists, or an exam section or command term that the file drops, or an exam format
    under a different code (a version has exactly one), ReferenceConflict is raised and nothing
    is changed, because questions may refer to them.
    """
    codes = {
        "program": reference.program.code,
        "subject": reference.subject.code,
        "version": reference.syllabus_version.code,
    }
    version = _find_version(session, **codes)
    nodes = _nodes(session, version.id) if version is not None else []
    exam_format = _exam_format(session, version.id) if version is not None else None
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
            subject_id=subject.id,
            code=codes["version"],
            title=reference.syllabus_version.title,
            status=reference.status,
        )
        session.add(version)
        session.flush()
    version.title = reference.syllabus_version.title
    version.status = reference.status

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
    """Vocabulary of one syllabus version. Unknown id, or no exam format: LookupError."""
    exam_format = _exam_format(session, syllabus_version_id)
    if exam_format is None:
        raise LookupError(f"no exam format for syllabus version {syllabus_version_id}")
    definition = ExamFormatDefinition.model_validate(exam_format.definition)
    nodes = _nodes(session, syllabus_version_id)
    parents = {n.parent_id for n in nodes}
    return Vocabulary(
        exam_sections=frozenset(s.code for s in definition.sections),
        command_terms=frozenset(definition.command_terms),
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


def get_tree(
    session: Session, *, program: str, subject: str, version: str | None = None
) -> SyllabusTree | None:
    """The syllabus version with these codes, or None when the programme, the subject or the
    version does not exist or the version has no exam format.

    Without `version`: the subject's newest version, which is the one with the greatest id
    (identifiers are time-ordered).
    """
    query = (
        select(SyllabusVersion)
        .join(Subject, Subject.id == SyllabusVersion.subject_id)
        .join(Program, Program.id == Subject.program_id)
        .where(Program.code == program, Subject.code == subject)
    )
    if version is not None:
        query = query.where(SyllabusVersion.code == version)
    row = session.scalars(query.order_by(SyllabusVersion.id.desc()).limit(1)).first()
    if row is None:
        return None
    exam_format = _exam_format(session, row.id)
    if exam_format is None:
        return None
    definition = ExamFormatDefinition.model_validate(exam_format.definition)
    nodes = _nodes(session, row.id)
    codes = {n.id: n.code for n in nodes}
    parents = {n.parent_id for n in nodes}
    return SyllabusTree(
        program=program,
        subject=subject,
        version=row.code,
        title=row.title,
        status=row.status,
        nodes=tuple(
            TreeNode(
                code=n.code,
                title=n.title,
                parent=codes[n.parent_id] if n.parent_id is not None else None,
                is_leaf=n.id not in parents,
                attributes=dict(n.attributes),
            )
            for n in nodes
        ),
        exam_sections=tuple((s.code, s.title) for s in definition.sections),
        command_terms=tuple(definition.command_terms),
    )
