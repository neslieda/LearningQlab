"""Invites: the only way an account comes to exist and get a role (M1-G slice 9, D-63).

Revision ID: 0006
Revises: 0005
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ROLES = ("student", "teacher", "org_admin", "reviewer", "content_admin", "platform_admin")
_ACTOR = r"~ '^[A-Za-z0-9_.:|-]{1,200}$'"


def upgrade() -> None:
    # Only the SHA-256 of the code is stored; the code itself is shown once, to its creator.
    op.create_table(
        "invite",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code_sha256", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("max_uses", sa.Integer(), nullable=False),
        sa.Column("uses", sa.Integer(), server_default="0", nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_by", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_invite")),
        sa.UniqueConstraint("code_sha256", name=op.f("uq_invite_code_sha256")),
        sa.CheckConstraint("code_sha256 ~ '^[0-9a-f]{64}$'", name=op.f("ck_invite_code_sha256")),
        sa.CheckConstraint(
            f"role IN ({', '.join(repr(r) for r in _ROLES)})", name=op.f("ck_invite_role")
        ),
        sa.CheckConstraint(f"created_by {_ACTOR}", name=op.f("ck_invite_created_by")),
        sa.CheckConstraint("expires_at > created_at", name=op.f("ck_invite_expires_at")),
        sa.CheckConstraint("max_uses BETWEEN 1 AND 200", name=op.f("ck_invite_max_uses")),
        sa.CheckConstraint("uses BETWEEN 0 AND max_uses", name=op.f("ck_invite_uses")),
        sa.CheckConstraint(
            f"(revoked_at IS NULL) = (revoked_by IS NULL) "
            f"AND (revoked_by IS NULL OR revoked_by {_ACTOR})",
            name=op.f("ck_invite_revoked"),
        ),
    )
    # One row per person who used an invite: the same person using it twice counts once.
    op.create_table(
        "invite_redemption",
        sa.Column("invite_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column(
            "redeemed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("invite_id", "account_id", name=op.f("pk_invite_redemption")),
        sa.ForeignKeyConstraint(
            ["invite_id"], ["invite.id"], name=op.f("fk_invite_redemption_invite_id_invite")
        ),
        sa.ForeignKeyConstraint(
            ["account_id"], ["account.id"], name=op.f("fk_invite_redemption_account_id_account")
        ),
    )


def downgrade() -> None:
    if op.get_bind().exec_driver_sql("SELECT 1 FROM invite LIMIT 1").first():
        raise RuntimeError("refusing to downgrade: invites exist")
    op.drop_table("invite_redemption")
    op.drop_table("invite")
