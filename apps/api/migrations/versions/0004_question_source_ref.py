"""Stable external key for imported questions.

Revision ID: 0004
Revises: 0003
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Where a question came from when it was imported (for example "pilot/a1-kinematics#1").
    # Set at creation and never changed: the question guard of migration 0002 allows updates to
    # syllabus_status only.
    op.add_column("question", sa.Column("source_ref", sa.Text(), nullable=True))
    op.create_unique_constraint("uq_question_source_ref", "question", ["source_ref"])
    op.create_check_constraint(
        op.f("ck_question_source_ref"),
        "question",
        "source_ref ~ '^[a-z0-9][a-z0-9/_#.-]{0,199}$'",
    )


def downgrade() -> None:
    # Without the keys a re-import would create every imported question a second time.
    if (
        op.get_bind()
        .exec_driver_sql("SELECT 1 FROM question WHERE source_ref IS NOT NULL LIMIT 1")
        .first()
    ):
        raise RuntimeError("refusing to downgrade: questions with a source_ref exist")
    op.drop_constraint(op.f("ck_question_source_ref"), "question", type_="check")
    op.drop_constraint("uq_question_source_ref", "question", type_="unique")
    op.drop_column("question", "source_ref")
