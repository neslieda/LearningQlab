"""Content: questions, versions, derived rows, check results and their guards.

Revision ID: 0002
Revises: 0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TIMESTAMP = sa.DateTime(timezone=True)
_STATUSES = (
    "'draft', 'auto_checking', 'needs_fix', 'in_review', "
    "'approved', 'published', 'withdrawn', 'rejected'"
)
_WORKING = "'draft', 'auto_checking', 'needs_fix', 'in_review', 'approved'"
_FOUNDATION_FUNCTIONS = (
    "audit_log_reject_change()",
    "audit_log_stamp()",
    "rights_record_guard()",
)
_GUARDED_TABLES = (
    "question",
    "question_version",
    "part",
    "mark_point",
    "question_version_syllabus",
    "question_version_check",
)


def upgrade() -> None:
    op.create_table(
        "question",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("rights_record_id", sa.Uuid(), nullable=False),
        sa.Column("syllabus_version_id", sa.Uuid(), nullable=False),
        sa.Column("syllabus_status", sa.Text(), server_default="in_syllabus", nullable=False),
        sa.Column("created_by", sa.Text(), nullable=False),
        sa.Column("created_at", _TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_question"),
        sa.ForeignKeyConstraint(
            ["rights_record_id"],
            ["rights_record.id"],
            name="fk_question_rights_record_id_rights_record",
        ),
        sa.ForeignKeyConstraint(
            ["syllabus_version_id"],
            ["syllabus_version.id"],
            name="fk_question_syllabus_version_id_syllabus_version",
        ),
        sa.CheckConstraint(
            "origin IN ('authored', 'generated', 'source_original')",
            name=op.f("ck_question_origin"),
        ),
        sa.CheckConstraint(
            "syllabus_status IN ('in_syllabus', 'out_of_syllabus')",
            name=op.f("ck_question_syllabus_status"),
        ),
    )
    op.create_table(
        "question_version",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.Text(), server_default="draft", nullable=False),
        sa.Column("schema_version", sa.Text(), nullable=False),
        sa.Column("document", postgresql.JSONB(), nullable=False),
        sa.Column("content_sha256", sa.Text(), nullable=False),
        sa.Column("question_class", sa.Text(), nullable=False),
        sa.Column("exam_section", sa.Text(), nullable=False),
        sa.Column("levels", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("total_marks", sa.Integer(), nullable=False),
        sa.Column(
            "has_unverified_visuals",
            sa.Boolean(),
            sa.Computed("jsonb_array_length(document -> 'stimuli') > 0", persisted=True),
            nullable=False,
        ),
        sa.Column("created_by", sa.Text(), nullable=False),
        sa.Column("created_at", _TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", _TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_question_version"),
        sa.ForeignKeyConstraint(
            ["question_id"], ["question.id"], name="fk_question_version_question_id_question"
        ),
        sa.UniqueConstraint(
            "question_id", "version_no", name="uq_question_version_question_id_version_no"
        ),
        sa.CheckConstraint(f"status IN ({_STATUSES})", name=op.f("ck_question_version_status")),
        sa.CheckConstraint("version_no >= 1", name=op.f("ck_question_version_version_no")),
        sa.CheckConstraint("total_marks >= 1", name=op.f("ck_question_version_total_marks")),
        sa.CheckConstraint(
            "octet_length(document::text) <= 1048576",
            name=op.f("ck_question_version_document_size"),
        ),
        sa.CheckConstraint(
            "content_sha256 ~ '^[0-9a-f]{64}$'", name=op.f("ck_question_version_content_sha256")
        ),
    )
    op.create_index(
        "uq_question_version_one_published",
        "question_version",
        ["question_id"],
        unique=True,
        postgresql_where=sa.text("status = 'published'"),
    )
    op.create_index(
        "uq_question_version_one_working",
        "question_version",
        ["question_id"],
        unique=True,
        postgresql_where=sa.text(f"status IN ({_WORKING})"),
    )
    op.create_table(
        "part",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("question_version_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("part_key", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("marks", sa.Integer(), nullable=False),
        sa.Column("answer_type", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_part"),
        sa.ForeignKeyConstraint(
            ["question_version_id"],
            ["question_version.id"],
            name="fk_part_question_version_id_question_version",
        ),
        sa.UniqueConstraint(
            "question_version_id", "part_key", name="uq_part_question_version_id_part_key"
        ),
    )
    op.create_table(
        "mark_point",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("part_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("point_key", sa.Text(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("alternative_group", sa.Text(), nullable=True),
        sa.Column("route", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_mark_point"),
        sa.ForeignKeyConstraint(["part_id"], ["part.id"], name="fk_mark_point_part_id_part"),
        sa.UniqueConstraint("part_id", "point_key", name="uq_mark_point_part_id_point_key"),
    )
    op.create_table(
        "question_version_syllabus",
        sa.Column("question_version_id", sa.Uuid(), nullable=False),
        sa.Column("syllabus_node_id", sa.Uuid(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint(
            "question_version_id", "syllabus_node_id", name="pk_question_version_syllabus"
        ),
        sa.ForeignKeyConstraint(
            ["question_version_id"],
            ["question_version.id"],
            name="fk_question_version_syllabus_version",
        ),
        sa.ForeignKeyConstraint(
            ["syllabus_node_id"],
            ["syllabus_node.id"],
            name="fk_question_version_syllabus_node",
        ),
    )
    op.create_index(
        "uq_question_version_syllabus_one_primary",
        "question_version_syllabus",
        ["question_version_id"],
        unique=True,
        postgresql_where=sa.text("is_primary"),
    )
    op.create_table(
        "question_version_check",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("question_version_id", sa.Uuid(), nullable=False),
        sa.Column("check_code", sa.Text(), nullable=False),
        sa.Column("severity", sa.Text(), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("detail", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column("created_at", _TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_question_version_check"),
        sa.ForeignKeyConstraint(
            ["question_version_id"],
            ["question_version.id"],
            name="fk_question_version_check_version",
        ),
        sa.UniqueConstraint(
            "question_version_id",
            "check_code",
            name="uq_question_version_check_question_version_id_check_code",
        ),
        sa.CheckConstraint(
            "check_code ~ '^[a-z][a-z0-9_]{0,63}$'",
            name=op.f("ck_question_version_check_check_code"),
        ),
        sa.CheckConstraint(
            "octet_length(detail::text) <= 16384", name=op.f("ck_question_version_check_detail")
        ),
        sa.CheckConstraint(
            "severity IN ('critical', 'warning')", name=op.f("ck_question_version_check_severity")
        ),
        sa.CheckConstraint(
            "outcome IN ('passed', 'failed', 'not_applicable')",
            name=op.f("ck_question_version_check_outcome"),
        ),
    )

    # Guards. They hold for every writer that is not the table owner or a superuser
    # (docs/SECURITY.md section 10) and fire in replica mode too (ENABLE ALWAYS). Every function
    # pins its search_path with pg_temp last and names tables with their schema, so a session
    # cannot make a guard read a temporary table of the same name.
    for function in _FOUNDATION_FUNCTIONS:
        op.execute(f"ALTER FUNCTION {function} SET search_path = pg_catalog, public, pg_temp")
    op.execute(
        """
        CREATE FUNCTION content_reject_change() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
        BEGIN
            RAISE EXCEPTION '% on % is not allowed', TG_OP, TG_TABLE_NAME
                USING ERRCODE = 'restrict_violation';
        END;
        $$
        """
    )
    # A question's origin, rights record and syllabus version are fixed at creation.
    op.execute(
        """
        CREATE FUNCTION question_guard() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
        BEGIN
            IF (to_jsonb(NEW) - 'syllabus_status') IS DISTINCT FROM
               (to_jsonb(OLD) - 'syllabus_status') THEN
                RAISE EXCEPTION 'question: only syllabus_status may change'
                    USING ERRCODE = 'restrict_violation';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    # Only authored content is accepted until the other origins are opened by a decision and a
    # migration (D-52; source_original stays closed, D-47).
    op.execute(
        """
        CREATE FUNCTION question_insert_guard() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
        BEGIN
            IF NEW.origin <> 'authored' THEN
                RAISE EXCEPTION 'origin % is closed', NEW.origin
                    USING ERRCODE = 'restrict_violation';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    # A question is tagged only with nodes of its own syllabus version.
    op.execute(
        """
        CREATE FUNCTION question_version_syllabus_same_version() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM public.question_version v
                JOIN public.question q ON q.id = v.question_id
                JOIN public.syllabus_node n ON n.syllabus_version_id = q.syllabus_version_id
                WHERE v.id = NEW.question_version_id AND n.id = NEW.syllabus_node_id
            ) THEN
                RAISE EXCEPTION 'syllabus node belongs to another syllabus version'
                    USING ERRCODE = 'restrict_violation';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION question_version_insert_guard() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
        BEGIN
            IF NEW.status <> 'draft' THEN
                RAISE EXCEPTION 'a question version starts as draft, not %', NEW.status
                    USING ERRCODE = 'restrict_violation';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    # Lifecycle: docs/DOMAIN_MODEL.md section 4. Content is editable in draft and needs_fix only
    # (D-55); a published version never changes (CLAUDE.md rule 7); publishing is refused while a
    # critical check has failed or a visual is unverified (CLAUDE.md rule 8, D-49).
    op.execute(
        """
        CREATE FUNCTION question_version_update_guard() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
        BEGIN
            -- has_unverified_visuals is generated and not yet computed in a BEFORE trigger.
            IF (to_jsonb(NEW) - 'status' - 'updated_at' - 'has_unverified_visuals')
               IS DISTINCT FROM
               (to_jsonb(OLD) - 'status' - 'updated_at' - 'has_unverified_visuals')
               -- jsonb equality is numeric (4 = 4.00); the stored text must not change either.
               OR NEW.document::text <> OLD.document::text THEN
                IF OLD.status NOT IN ('draft', 'needs_fix') THEN
                    RAISE EXCEPTION 'the content of a % question version cannot change', OLD.status
                        USING ERRCODE = 'restrict_violation';
                END IF;
                IF NEW.id <> OLD.id OR NEW.question_id <> OLD.question_id
                   OR NEW.version_no <> OLD.version_no OR NEW.created_by <> OLD.created_by
                   OR NEW.created_at <> OLD.created_at THEN
                    RAISE EXCEPTION 'the identity of a question version cannot change'
                        USING ERRCODE = 'restrict_violation';
                END IF;
            END IF;
            IF NEW.status <> OLD.status THEN
                IF (OLD.status, NEW.status) NOT IN (
                    ('draft', 'auto_checking'),
                    ('auto_checking', 'needs_fix'),
                    ('auto_checking', 'in_review'),
                    ('needs_fix', 'draft'),
                    ('in_review', 'approved'),
                    ('in_review', 'needs_fix'),
                    ('in_review', 'rejected'),
                    ('approved', 'needs_fix'),
                    ('approved', 'published'),
                    ('published', 'withdrawn'),
                    ('withdrawn', 'published')
                ) THEN
                    RAISE EXCEPTION 'question version cannot move from % to %',
                        OLD.status, NEW.status USING ERRCODE = 'restrict_violation';
                END IF;
                -- Review and publishing need every required check passed on this content and no
                -- critical check failed (CLAUDE.md rule 8). The required codes mirror
                -- qlab.content.service.REQUIRED_CHECKS.
                IF NEW.status IN ('in_review', 'published') THEN
                    IF EXISTS (
                        SELECT 1 FROM public.question_version_check c
                        WHERE c.question_version_id = NEW.id
                          AND c.severity = 'critical' AND c.outcome = 'failed'
                    ) THEN
                        RAISE EXCEPTION 'cannot move to %: a critical check failed', NEW.status
                            USING ERRCODE = 'restrict_violation';
                    END IF;
                    IF (
                        SELECT count(*) FROM public.question_version_check c
                        WHERE c.question_version_id = NEW.id
                          AND c.check_code IN ('schema_valid', 'vocabulary_valid')
                          AND c.severity = 'critical' AND c.outcome = 'passed'
                    ) <> 2 THEN
                        RAISE EXCEPTION 'cannot move to %: a required check has not passed',
                            NEW.status USING ERRCODE = 'restrict_violation';
                    END IF;
                END IF;
                IF OLD.status = 'withdrawn' AND EXISTS (
                    SELECT 1 FROM public.question_version v
                    WHERE v.question_id = NEW.question_id AND v.version_no > NEW.version_no
                ) THEN
                    RAISE EXCEPTION 'cannot republish: a newer version exists'
                        USING ERRCODE = 'restrict_violation';
                END IF;
                IF NEW.status = 'published' THEN
                    IF jsonb_array_length(NEW.document -> 'stimuli') > 0 THEN
                        RAISE EXCEPTION 'cannot publish: unverified visuals'
                            USING ERRCODE = 'restrict_violation';
                    END IF;
                END IF;
            END IF;
            NEW.updated_at := now();
            RETURN NEW;
        END;
        $$
        """
    )
    # Rows that hang off a version are replaced (delete and insert), never updated, and only
    # while the version is in one of the states named by the trigger argument.
    op.execute(
        """
        CREATE FUNCTION question_version_child_guard() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
        DECLARE
            version_id uuid;
            version_status text;
        BEGIN
            IF TG_OP = 'UPDATE' THEN
                RAISE EXCEPTION 'rows of % are replaced, not updated', TG_TABLE_NAME
                    USING ERRCODE = 'restrict_violation';
            END IF;
            IF TG_TABLE_NAME = 'mark_point' THEN
                IF TG_OP = 'DELETE' THEN
                    SELECT p.question_version_id INTO version_id
                    FROM public.part p WHERE p.id = OLD.part_id;
                ELSE
                    SELECT p.question_version_id INTO version_id
                    FROM public.part p WHERE p.id = NEW.part_id;
                END IF;
            ELSIF TG_OP = 'DELETE' THEN
                version_id := OLD.question_version_id;
            ELSE
                version_id := NEW.question_version_id;
            END IF;
            SELECT v.status INTO version_status FROM public.question_version v
            WHERE v.id = version_id FOR SHARE;
            IF version_status IS NULL
               OR NOT (version_status = ANY (string_to_array(TG_ARGV[0], ','))) THEN
                RAISE EXCEPTION '% rows cannot change while the version is %',
                    TG_TABLE_NAME, coalesce(version_status, 'missing')
                    USING ERRCODE = 'restrict_violation';
            END IF;
            IF TG_OP = 'DELETE' THEN
                RETURN OLD;
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    triggers = [
        ("question", "question_no_delete", "BEFORE DELETE", "ROW", "content_reject_change()"),
        ("question", "question_guard", "BEFORE UPDATE", "ROW", "question_guard()"),
        ("question", "question_insert_guard", "BEFORE INSERT", "ROW", "question_insert_guard()"),
        (
            "question_version_syllabus",
            "question_version_syllabus_same_version",
            "BEFORE INSERT",
            "ROW",
            "question_version_syllabus_same_version()",
        ),
        (
            "question_version",
            "question_version_no_delete",
            "BEFORE DELETE",
            "ROW",
            "content_reject_change()",
        ),
        (
            "question_version",
            "question_version_insert_guard",
            "BEFORE INSERT",
            "ROW",
            "question_version_insert_guard()",
        ),
        (
            "question_version",
            "question_version_update_guard",
            "BEFORE UPDATE",
            "ROW",
            "question_version_update_guard()",
        ),
    ]
    for table in ("part", "mark_point", "question_version_syllabus"):
        triggers.append(
            (
                table,
                f"{table}_guard",
                "BEFORE INSERT OR UPDATE OR DELETE",
                "ROW",
                "question_version_child_guard('draft,needs_fix')",
            )
        )
    triggers.append(
        (
            "question_version_check",
            "question_version_check_guard",
            "BEFORE INSERT OR UPDATE OR DELETE",
            "ROW",
            "question_version_child_guard('draft,needs_fix,auto_checking')",
        )
    )
    for table in _GUARDED_TABLES:
        triggers.append(
            (
                table,
                f"{table}_no_truncate",
                "BEFORE TRUNCATE",
                "STATEMENT",
                "content_reject_change()",
            )
        )
    for table, name, when, level, function in triggers:
        op.execute(
            f"CREATE TRIGGER {name} {when} ON {table} FOR EACH {level} EXECUTE FUNCTION {function}"
        )
        op.execute(f"ALTER TABLE {table} ENABLE ALWAYS TRIGGER {name}")


def downgrade() -> None:
    # Question content is never dropped by a migration; an operator has to move it away first.
    if op.get_bind().exec_driver_sql("SELECT 1 FROM question LIMIT 1").first():
        raise RuntimeError("refusing to downgrade: question is not empty")
    for table in reversed(_GUARDED_TABLES):
        op.drop_table(table)
    op.execute("DROP FUNCTION question_version_child_guard()")
    op.execute("DROP FUNCTION question_version_update_guard()")
    op.execute("DROP FUNCTION question_version_insert_guard()")
    op.execute("DROP FUNCTION question_version_syllabus_same_version()")
    op.execute("DROP FUNCTION question_insert_guard()")
    op.execute("DROP FUNCTION question_guard()")
    op.execute("DROP FUNCTION content_reject_change()")
    for function in _FOUNDATION_FUNCTIONS:
        op.execute(f"ALTER FUNCTION {function} RESET search_path")
