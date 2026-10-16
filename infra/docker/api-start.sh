#!/bin/sh
# Container entrypoint: migrate with the owner role, then serve with the application role.
# QLAB_MIGRATION_DATABASE_URL is handed to Alembic only (migrations/env.py reads QLAB_DATABASE_URL),
# in that one process; the server never sees it as its database URL.
set -eu

: "${QLAB_DATABASE_URL:?QLAB_DATABASE_URL is not set}"
: "${QLAB_MIGRATION_DATABASE_URL:?QLAB_MIGRATION_DATABASE_URL is not set}"

QLAB_DATABASE_URL="$QLAB_MIGRATION_DATABASE_URL" alembic upgrade head

# Tables created by the migration above carry default grants for the application role; alembic_version is the
# owner's bookkeeping, so take them away again (idempotent; skipped if the role does not exist).
QLAB_DATABASE_URL="$QLAB_MIGRATION_DATABASE_URL" python - <<'PY'
import os
import sqlalchemy as sa

role = os.environ.get("QLAB_APP_DB_ROLE", "qlab_app")
engine = sa.create_engine(os.environ["QLAB_DATABASE_URL"])
with engine.begin() as conn:
    if conn.execute(sa.text("SELECT 1 FROM pg_roles WHERE rolname = :r"), {"r": role}).first():
        quoted = conn.dialect.identifier_preparer.quote(role)
        conn.execute(sa.text(f"REVOKE ALL ON TABLE public.alembic_version FROM {quoted}"))
PY

# The server does not need the owner credentials; drop them before it starts.
unset QLAB_MIGRATION_DATABASE_URL

exec uvicorn --factory qlab.api.app:app_from_env \
  --host 0.0.0.0 --port "${PORT:-8000}" \
  --proxy-headers --forwarded-allow-ips='*'
