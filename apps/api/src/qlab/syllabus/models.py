"""Programme, subject, syllabus tree and exam format.

Nothing here names a particular exam board (CLAUDE.md rule 12): codes, titles, exam sections
and command terms are rows and JSON loaded from a reference file.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from qlab.database import Base, new_id


class Program(Base):
    __tablename__ = "program"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)


class Subject(Base):
    __tablename__ = "subject"
    __table_args__ = (UniqueConstraint("program_id", "code"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("program.id"))
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)


class SyllabusVersion(Base):
    __tablename__ = "syllabus_version"
    __table_args__ = (UniqueConstraint("subject_id", "code"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subject.id"))
    code: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)


class SyllabusNode(Base):
    __tablename__ = "syllabus_node"
    __table_args__ = (UniqueConstraint("syllabus_version_id", "code"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    syllabus_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("syllabus_version.id"))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("syllabus_node.id"))
    code: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    position: Mapped[int]
    # Programme-specific properties of the node (for example which level it belongs to).
    attributes: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default="{}")


class ExamFormat(Base):
    __tablename__ = "exam_format"
    __table_args__ = (UniqueConstraint("syllabus_version_id", "code"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    syllabus_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("syllabus_version.id"))
    code: Mapped[str] = mapped_column(Text)
    # Sections and label vocabulary; shape: qlab.syllabus.reference.ExamFormatDefinition.
    definition: Mapped[dict[str, Any]] = mapped_column(JSONB)
