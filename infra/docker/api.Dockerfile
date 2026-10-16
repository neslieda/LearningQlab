# syntax=docker/dockerfile:1
# API image (D-61). Build from the repository root:
#   docker build -f infra/docker/api.Dockerfile -t qlab-api .
# Pins: python 3.14.8 (digest checked 2026-10-16), uv 0.12.24, Node 24.22.0.

FROM ghcr.io/astral-sh/uv:0.12.24@sha256:3af4716e991d6956a41e573eab705d0ee08500cd829ed30293eb8472f372c65a AS uv

FROM node:24.22.0-slim@sha256:a5f4366e834695d5f363b920c104953a535d3a9864d1bdf74566a0ebe01daee5 AS katex
WORKDIR /katex
COPY apps/api/katex/package.json apps/api/katex/package-lock.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY apps/api/katex/render.mjs ./

FROM python:3.14.8-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170 AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=never
WORKDIR /app/apps/api
COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY apps/api/alembic.ini ./
COPY apps/api/migrations ./migrations
COPY apps/api/src ./src
RUN uv sync --locked --no-dev

FROM python:3.14.8-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170 AS runtime
RUN groupadd --system --gid 10001 qlab \
 && useradd --system --uid 10001 --gid qlab --no-create-home --shell /usr/sbin/nologin qlab
# Node is only used by the math renderer (qlab.content.math); copy the binary, not npm.
COPY --from=katex /usr/local/bin/node /usr/local/bin/node
COPY --from=build --chown=qlab:qlab /app/apps/api /app/apps/api
COPY --from=katex --chown=qlab:qlab /katex /app/apps/api/katex
COPY --chmod=0755 infra/docker/api-start.sh /usr/local/bin/api-start.sh
WORKDIR /app/apps/api
ENV PATH="/app/apps/api/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    QLAB_NODE_BIN=/usr/local/bin/node \
    QLAB_KATEX_DIR=/app/apps/api/katex \
    PORT=8000
USER qlab
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
  CMD ["python", "-c", "import os,sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:%s/healthz' % os.environ.get('PORT','8000'), timeout=4).status == 200 else 1)"]
CMD ["/usr/local/bin/api-start.sh"]
