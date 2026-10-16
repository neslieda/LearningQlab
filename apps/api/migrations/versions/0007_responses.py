"""Learner answers (M1-G slice 8, D-66).

Revision ID: 0007
Revises: 0006
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Opaque account id and the answer; nothing that names a person. Rows go with the account,
    # and the learner can delete their own (docs/SECURITY.md 5.4): no delete guard.
    op.create_table(
        "response",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("question_version_id", sa.Uuid(), nullable=False),
        sa.Column("part_id", sa.Text(), nullable=True),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_response")),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["account.id"],
            name=op.f("fk_response_account_id_account"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_version_id"],
            ["question_version.id"],
            name=op.f("fk_response_question_version_id_question_version"),
        ),
        sa.CheckConstraint("kind IN ('mcq', 'written')", name=op.f("ck_response_kind")),
        sa.CheckConstraint(
            "(kind = 'mcq' AND part_id IS NULL AND correct IS NOT NULL) "
            "OR (kind = 'written' AND part_id IS NOT NULL AND correct IS NULL)",
            name=op.f("ck_response_shape"),
        ),
        sa.CheckConstraint(
            "part_id IS NULL OR (part_id <> '' AND length(part_id) <= 200)",
            name=op.f("ck_response_part_id"),
        ),
        sa.CheckConstraint(
            "pg_column_size(payload) <= 66000", name=op.f("ck_response_payload_size")
        ),
    )
    op.create_index(
        "ix_response_account_created", "response", ["account_id", "created_at", "id"], unique=False
    )
    op.create_index(
        "ix_response_account_version",
        "response",
        ["account_id", "question_version_id"],
        unique=False,
    )


def downgrade() -> None:
    # Dropping the table would erase learners' answers.
    if op.get_bind().exec_driver_sql("SELECT 1 FROM response LIMIT 1").first():
        raise RuntimeError("refusing to downgrade: learner answers exist")
    op.drop_index("ix_response_account_version", table_name="response")
    op.drop_index("ix_response_account_created", table_name="response")
    op.drop_table("response")
