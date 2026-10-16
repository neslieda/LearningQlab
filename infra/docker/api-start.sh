#!/bin/sh
# Container entrypoint: migrate with the owner role, then serve with the application role.
# QLAB_MIGRATION_DATABASE_URL is handed to Alembic only (migrations/env.py reads QLAB_DATABASE_URL),
# in that one process; the server never sees it as its database URL.
set -eu

: "${QLAB_DATABASE_URL:?QLAB_DATABASE_URL is not set}"
: "${QLAB_MIGRATION_DATABASE_URL:?QLAB_MIGRATION_DATABASE_URL is not set}"

QLAB_DATABASE_URL="$QLAB_MIGRATION_DATABASE_URL" alembic upgrade head

# The server does not need the owner credentials; drop them before it starts.
unset QLAB_MIGRATION_DATABASE_URL

exec uvicorn --factory qlab.api.app:app_from_env \
  --host 0.0.0.0 --port "${PORT:-8000}" \
  --proxy-headers --forwarded-allow-ips='*'
