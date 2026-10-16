# syntax=docker/dockerfile:1
# Web image (D-61): Next.js standalone output of the npm workspace (apps/web + packages/*).
# Build from the repository root:
#   docker build -f infra/docker/web.Dockerfile -t qlab-web \
#     --build-arg NEXT_PUBLIC_OIDC_ISSUER=... .
# Requires `output: "standalone"` in apps/web/next.config.ts.
# NEXT_PUBLIC_* values are inlined into the browser bundle at build time; they are public identifiers, not secrets.
# QLAB_API_URL is read when the server starts (rewrites are evaluated at build time by `next build` and
# stored in the routes manifest, so it is ALSO needed as a build argument; see below).

FROM node:24.22.0-slim@sha256:a5f4366e834695d5f363b920c104953a535d3a9864d1bdf74566a0ebe01daee5 AS build
WORKDIR /repo
COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/
COPY packages/api-client/package.json packages/api-client/
COPY packages/question-editor/package.json packages/question-editor/
COPY packages/question-renderer/package.json packages/question-renderer/
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY apps/web apps/web
COPY packages packages

ARG NEXT_PUBLIC_QLAB_ENV
ARG NEXT_PUBLIC_OIDC_ISSUER
ARG NEXT_PUBLIC_OIDC_CLIENT_ID
ARG NEXT_PUBLIC_OIDC_PROJECT_ID
ARG NEXT_PUBLIC_OIDC_STAFF_ORG_ID
ARG NEXT_PUBLIC_OIDC_LEARNER_ORG_ID
ARG QLAB_API_URL
ENV NEXT_PUBLIC_QLAB_ENV=$NEXT_PUBLIC_QLAB_ENV \
    NEXT_PUBLIC_OIDC_ISSUER=$NEXT_PUBLIC_OIDC_ISSUER \
    NEXT_PUBLIC_OIDC_CLIENT_ID=$NEXT_PUBLIC_OIDC_CLIENT_ID \
    NEXT_PUBLIC_OIDC_PROJECT_ID=$NEXT_PUBLIC_OIDC_PROJECT_ID \
    NEXT_PUBLIC_OIDC_STAFF_ORG_ID=$NEXT_PUBLIC_OIDC_STAFF_ORG_ID \
    NEXT_PUBLIC_OIDC_LEARNER_ORG_ID=$NEXT_PUBLIC_OIDC_LEARNER_ORG_ID \
    QLAB_API_URL=$QLAB_API_URL \
    NEXT_TELEMETRY_DISABLED=1
WORKDIR /repo/apps/web
RUN npx next build

FROM node:24.22.0-slim@sha256:a5f4366e834695d5f363b920c104953a535d3a9864d1bdf74566a0ebe01daee5 AS runtime
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
WORKDIR /app
# The "node" user (uid 1000) ships with the image; it is not root.
COPY --from=build --chown=node:node /repo/apps/web/.next/standalone ./
COPY --from=build --chown=node:node /repo/apps/web/.next/static ./apps/web/.next/static
RUN mkdir -p apps/web/public
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:'+(process.env.PORT||3000)+'/').then(r=>process.exit(r.status<500?0:1)).catch(()=>process.exit(1))"]
CMD ["node", "apps/web/server.js"]
