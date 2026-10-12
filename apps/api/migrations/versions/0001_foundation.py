"""Foundation: audit log, rights records, syllabus reference tables.

Revision ID: 0001
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TIMESTAMP = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("occurred_at", _TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column("actor", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.Text(), nullable=False),
        sa.Column("entity_id", sa.Text(), nullable=False),
        sa.Column("data", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_audit_log"),
    )
    op.create_index(
        "ix_audit_log_entity_type_entity_id_occurred_at",
        "audit_log",
        ["entity_type", "entity_id", "occurred_at"],
    )
    # Append-only: enforced in the database so that no code path can rewrite history.
    op.execute(
        """
        CREATE FUNCTION audit_log_reject_change() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only (% rejected)', TG_OP
                USING ERRCODE = 'restrict_violation';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER audit_log_no_update_delete
        BEFORE UPDATE OR DELETE ON audit_log
        FOR EACH ROW EXECUTE FUNCTION audit_log_reject_change()
        """
    )
    op.execute(
        """
        CREATE TRIGGER audit_log_no_truncate
        BEFORE TRUNCATE ON audit_log
        FOR EACH STATEMENT EXECUTE FUNCTION audit_log_reject_change()
        """
    )

    op.create_table(
        "rights_record",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("holder", sa.Text(), nullable=False),
        sa.Column("license_ref", sa.Text(), nullable=True),
        sa.Column("display_scope", sa.Text(), server_default="none", nullable=False),
        sa.Column("display_organization_id", sa.Uuid(), nullable=True),
        sa.Column("allows_ai_processing", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("allows_commercial_use", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("valid_from", _TIMESTAMP, nullable=False),
        sa.Column("valid_until", _TIMESTAMP, nullable=True),
        sa.Column("revoked_at", _TIMESTAMP, nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", _TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_rights_record"),
        sa.CheckConstraint(
            "display_scope IN ('none', 'organization', 'all')",
            name="ck_rights_record_display_scope",
        ),
        sa.CheckConstraint(
            "(display_scope = 'organization') = (display_organization_id IS NOT NULL)",
            name="ck_rights_record_display_organization",
        ),
        sa.CheckConstraint(
            "valid_until IS NULL OR valid_until > valid_from",
            name="ck_rights_record_validity_order",
        ),
    )

    op.create_table(
        "program",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_program"),
        sa.UniqueConstraint("code", name="uq_program_code"),
    )
    op.create_table(
        "subject",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("program_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_subject"),
        sa.ForeignKeyConstraint(
            ["program_id"], ["program.id"], name="fk_subject_program_id_program"
        ),
        sa.UniqueConstraint("program_id", "code", name="uq_subject_program_id_code"),
    )
    op.create_table(
        "syllabus_version",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_syllabus_version"),
        sa.ForeignKeyConstraint(
            ["subject_id"], ["subject.id"], name="fk_syllabus_version_subject_id_subject"
        ),
        sa.UniqueConstraint("subject_id", "code", name="uq_syllabus_version_subject_id_code"),
    )
    op.create_table(
        "syllabus_node",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("syllabus_version_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("attributes", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_syllabus_node"),
        sa.ForeignKeyConstraint(
            ["syllabus_version_id"],
            ["syllabus_version.id"],
            name="fk_syllabus_node_syllabus_version_id_syllabus_version",
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["syllabus_node.id"], name="fk_syllabus_node_parent_id_syllabus_node"
        ),
        sa.UniqueConstraint(
            "syllabus_version_id", "code", name="uq_syllabus_node_syllabus_version_id_code"
        ),
    )
    op.create_table(
        "exam_format",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("syllabus_version_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("definition", postgresql.JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_exam_format"),
        sa.ForeignKeyConstraint(
            ["syllabus_version_id"],
            ["syllabus_version.id"],
            name="fk_exam_format_syllabus_version_id_syllabus_version",
        ),
        sa.UniqueConstraint(
            "syllabus_version_id", "code", name="uq_exam_format_syllabus_version_id_code"
        ),
    )


def downgrade() -> None:
    op.drop_table("exam_format")
    op.drop_table("syllabus_node")
    op.drop_table("syllabus_version")
    op.drop_table("subject")
    op.drop_table("program")
    op.drop_table("rights_record")
    op.drop_table("audit_log")
    op.execute("DROP FUNCTION audit_log_reject_change()")
