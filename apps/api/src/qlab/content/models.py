"""Question tables. The JSON document on `question_version` is the source of truth (D-50);
`part`, `mark_point` and `question_version_syllabus` are derived from it in the same
transaction so that answers, marks and analytics can point at rows.

Migration 0002 adds triggers that hold whatever code writes to these tables: content changes
only in `draft` and `needs_fix`, status moves only along the lifecycle, nothing is deleted,
and a version cannot become `published` with unverified visuals or a failed critical check.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    Computed,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from qlab.database import Base, created_at_column, new_id

ORIGINS = ("authored", "generated", "source_original")
STATUSES = (
    "draft",
    "auto_checking",
    "needs_fix",
    "in_review",
    "approved",
    "published",
    "withdrawn",
    "rejected",
)
# A question has at most one version in these states at a time.
WORKING_STATUSES = ("draft", "auto_checking", "needs_fix", "in_review", "approved")


def _in(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


class Question(Base):
    __tablename__ = "question"
    __table_args__ = (
        CheckConstraint(_in("origin", ORIGINS), name="origin"),
        CheckConstraint(
            "syllabus_status IN ('in_syllabus', 'out_of_syllabus')", name="syllabus_status"
        ),
        CheckConstraint("source_ref ~ '^[a-z0-9][a-z0-9/_#.-]{0,199}$'", name="source_ref"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    origin: Mapped[str] = mapped_column(Text)
    rights_record_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rights_record.id"))
    syllabus_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("syllabus_version.id"))
    syllabus_status: Mapped[str] = mapped_column(Text, server_default="in_syllabus")
    # Stable key of an imported question (for example "pilot/a1-kinematics#1"); fixed at creation.
    source_ref: Mapped[str | None] = mapped_column(Text, unique=True)
    created_by: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()


class QuestionVersion(Base):
    __tablename__ = "question_version"
    __table_args__ = (
        UniqueConstraint("question_id", "version_no"),
        CheckConstraint(_in("status", STATUSES), name="status"),
        CheckConstraint("version_no >= 1", name="version_no"),
        CheckConstraint("total_marks >= 1", name="total_marks"),
        CheckConstraint("octet_length(document::text) <= 1048576", name="document_size"),
        CheckConstraint("content_sha256 ~ '^[0-9a-f]{64}$'", name="content_sha256"),
        Index(
            "uq_question_version_one_published",
            "question_id",
            unique=True,
            postgresql_where=text("status = 'published'"),
        ),
        Index(
            "uq_question_version_one_working",
            "question_id",
            unique=True,
            postgresql_where=text(_in("status", WORKING_STATUSES)),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question.id"))
    version_no: Mapped[int]
    status: Mapped[str] = mapped_column(Text, server_default="draft")
    schema_version: Mapped[str] = mapped_column(Text)
    document: Mapped[dict[str, Any]] = mapped_column(JSONB)
    # SHA-256 of the document's canonical JSON; written to the audit log at every transition.
    content_sha256: Mapped[str] = mapped_column(Text)
    # Copies of document fields, for filtering. Written together with the document.
    question_class: Mapped[str] = mapped_column(Text)
    exam_section: Mapped[str] = mapped_column(Text)
    levels: Mapped[list[str]] = mapped_column(ARRAY(Text))
    total_marks: Mapped[int]
    # Computed by the database from the document, so it cannot be set by a writer. Until
    # assets exist, every stimulus counts as unverified and blocks publishing (D-49).
    has_unverified_visuals: Mapped[bool] = mapped_column(
        Computed("jsonb_array_length(document -> 'stimuli') > 0", persisted=True)
    )
    created_by: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()
    # Maintained by the update guard.
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Part(Base):
    """A markable part. A multiple-choice question has one, with key "mcq" and no label."""

    __tablename__ = "part"
    __table_args__ = (UniqueConstraint("question_version_id", "part_key"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    question_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question_version.id"))
    position: Mapped[int]
    # The part's id inside the document.
    part_key: Mapped[str] = mapped_column(Text)
    label: Mapped[str | None] = mapped_column(Text)
    marks: Mapped[int]
    answer_type: Mapped[str] = mapped_column(Text)


class MarkPoint(Base):
    __tablename__ = "mark_point"
    __table_args__ = (UniqueConstraint("part_id", "point_key"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    part_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("part.id"))
    position: Mapped[int]
    # The mark point's id inside the document.
    point_key: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(Text)
    alternative_group: Mapped[str | None] = mapped_column(Text)
    route: Mapped[str | None] = mapped_column(Text)


class QuestionVersionSyllabus(Base):
    __tablename__ = "question_version_syllabus"
    __table_args__ = (
        Index(
            "uq_question_version_syllabus_one_primary",
            "question_version_id",
            unique=True,
            postgresql_where=text("is_primary"),
        ),
    )

    question_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("question_version.id", name="fk_question_version_syllabus_version"),
        primary_key=True,
    )
    syllabus_node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("syllabus_node.id", name="fk_question_version_syllabus_node"),
        primary_key=True,
    )
    is_primary: Mapped[bool]


class QuestionVersionCheck(Base):
    """Result of one verification check on a version's current content."""

    __tablename__ = "question_version_check"
    __table_args__ = (
        UniqueConstraint("question_version_id", "check_code"),
        CheckConstraint("check_code ~ '^[a-z][a-z0-9_]{0,63}$'", name="check_code"),
        CheckConstraint("octet_length(detail::text) <= 16384", name="detail"),
        CheckConstraint("severity IN ('critical', 'warning')", name="severity"),
        CheckConstraint("outcome IN ('passed', 'failed', 'not_applicable')", name="outcome"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)
    question_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("question_version.id", name="fk_question_version_check_version")
    )
    check_code: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(Text)
    outcome: Mapped[str] = mapped_column(Text)
    detail: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default="{}")
    created_at: Mapped[datetime] = created_at_column()
