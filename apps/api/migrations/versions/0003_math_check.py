"""Math render check becomes a required check; the required list moves into one function.

Revision ID: 0003
Revises: 0002
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The lifecycle guard of migration 0002, unchanged except for how it finds the required checks.
_GUARD = """
        CREATE OR REPLACE FUNCTION question_version_update_guard() RETURNS trigger
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
                -- critical check failed (CLAUDE.md rule 8). The required codes come
                -- from content_required_checks() (qlab.content.service.REQUIRED_CHECKS).
                IF NEW.status IN ('in_review', 'published') THEN
                    IF EXISTS (
                        SELECT 1 FROM public.question_version_check c
                        WHERE c.question_version_id = NEW.id
                          AND c.severity = 'critical' AND c.outcome = 'failed'
                    ) THEN
                        RAISE EXCEPTION 'cannot move to %: a critical check failed', NEW.status
                            USING ERRCODE = 'restrict_violation';
                    END IF;
{required_clause}
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

_REQUIRED_FROM_FUNCTION = """\
                    IF (
                        SELECT count(*) FROM public.question_version_check c
                        WHERE c.question_version_id = NEW.id
                          AND c.check_code = ANY (public.content_required_checks())
                          AND c.severity = 'critical' AND c.outcome = 'passed'
                    ) <> cardinality(public.content_required_checks()) THEN"""

_REQUIRED_IN_0002 = """\
                    IF (
                        SELECT count(*) FROM public.question_version_check c
                        WHERE c.question_version_id = NEW.id
                          AND c.check_code IN ('schema_valid', 'vocabulary_valid')
                          AND c.severity = 'critical' AND c.outcome = 'passed'
                    ) <> 2 THEN"""


def upgrade() -> None:
    # The codes a version needs as critical and passed before review and before publishing
    # (CLAUDE.md rules 6 and 8). A later required check replaces only this function.
    op.execute(
        """
        CREATE FUNCTION content_required_checks() RETURNS text[]
        LANGUAGE sql IMMUTABLE SET search_path = pg_catalog, public, pg_temp
        AS $$ SELECT ARRAY['schema_valid', 'vocabulary_valid', 'math_renders'] $$
        """
    )
    op.execute(_GUARD.format(required_clause=_REQUIRED_FROM_FUNCTION))


def downgrade() -> None:
    op.execute(_GUARD.format(required_clause=_REQUIRED_IN_0002))
    op.execute("DROP FUNCTION content_required_checks()")
