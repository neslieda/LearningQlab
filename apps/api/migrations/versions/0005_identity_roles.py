"""Accounts and role assignments (M1-G slice 5, D-12, D-59).

Revision ID: 0005
Revises: 0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ROLES = ("student", "teacher", "org_admin", "reviewer", "content_admin", "platform_admin")
_ACTOR = r"~ '^[A-Za-z0-9_.:|-]{1,200}$'"


def upgrade() -> None:
    # An account is an identity provider subject. No name, e-mail or password is stored.
    op.create_table(
        "account",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("issuer", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account")),
        sa.UniqueConstraint("issuer", "subject", name=op.f("uq_account_issuer_subject")),
        sa.CheckConstraint(
            "issuer <> '' AND issuer = btrim(issuer) AND length(issuer) <= 200",
            name=op.f("ck_account_issuer"),
        ),
        sa.CheckConstraint(
            "subject <> '' AND subject = btrim(subject) AND length(subject) <= 200",
            name=op.f("ck_account_subject"),
        ),
    )
    # Roles are data in the application (D-12). A revoked assignment stays as a row.
    op.create_table(
        "role_assignment",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("granted_by", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_by", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role_assignment")),
        sa.ForeignKeyConstraint(
            ["account_id"], ["account.id"], name=op.f("fk_role_assignment_account_id_account")
        ),
        sa.CheckConstraint(
            f"role IN ({', '.join(repr(r) for r in _ROLES)})", name=op.f("ck_role_assignment_role")
        ),
        sa.CheckConstraint(f"granted_by {_ACTOR}", name=op.f("ck_role_assignment_granted_by")),
        sa.CheckConstraint(
            f"(revoked_at IS NULL) = (revoked_by IS NULL) "
            f"AND (revoked_by IS NULL OR revoked_by {_ACTOR})",
            name=op.f("ck_role_assignment_revoked"),
        ),
    )
    op.create_index(
        "uq_role_assignment_one_active",
        "role_assignment",
        ["account_id", "role"],
        unique=True,
        postgresql_where=sa.text("revoked_at IS NULL"),
    )
    # Assignments are history: who held which role when. They are revoked, never removed.
    op.execute(
        """
        CREATE FUNCTION role_assignment_guard() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
        BEGIN
            IF TG_OP = 'DELETE' OR TG_OP = 'TRUNCATE' THEN
                RAISE EXCEPTION 'role_assignment rows are never deleted; revoke instead';
            END IF;
            IF OLD.revoked_at IS NOT NULL THEN
                RAISE EXCEPTION 'a revoked role assignment cannot be changed';
            END IF;
            IF NEW.id IS DISTINCT FROM OLD.id
                OR NEW.account_id IS DISTINCT FROM OLD.account_id
                OR NEW.role IS DISTINCT FROM OLD.role
                OR NEW.granted_by IS DISTINCT FROM OLD.granted_by
                OR NEW.created_at IS DISTINCT FROM OLD.created_at THEN
                RAISE EXCEPTION 'a role assignment can only be revoked';
            END IF;
            RETURN NEW;
        END
        $$
        """
    )
    op.execute(
        "CREATE TRIGGER role_assignment_guard_row BEFORE UPDATE OR DELETE ON role_assignment "
        "FOR EACH ROW EXECUTE FUNCTION role_assignment_guard()"
    )
    op.execute(
        "CREATE TRIGGER role_assignment_guard_truncate BEFORE TRUNCATE ON role_assignment "
        "FOR EACH STATEMENT EXECUTE FUNCTION role_assignment_guard()"
    )
    op.execute("ALTER TABLE role_assignment ENABLE ALWAYS TRIGGER role_assignment_guard_row")
    op.execute("ALTER TABLE role_assignment ENABLE ALWAYS TRIGGER role_assignment_guard_truncate")


def downgrade() -> None:
    # Dropping the tables would erase who held which role.
    if op.get_bind().exec_driver_sql("SELECT 1 FROM role_assignment LIMIT 1").first():
        raise RuntimeError("refusing to downgrade: role assignments exist")
    op.execute("DROP TRIGGER role_assignment_guard_truncate ON role_assignment")
    op.execute("DROP TRIGGER role_assignment_guard_row ON role_assignment")
    op.drop_index("uq_role_assignment_one_active", table_name="role_assignment")
    op.drop_table("role_assignment")
    op.execute("DROP FUNCTION role_assignment_guard()")
    op.drop_table("account")
