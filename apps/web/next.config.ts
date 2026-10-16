import path from "node:path";
import type { NextConfig } from "next";

const apiUrl = (process.env.QLAB_API_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");
const isProduction = process.env.NODE_ENV === "production";

// `next dev` without an explicit environment is the local one (development sign-in). Builds never default to local.
const qlabEnv = process.env.NEXT_PUBLIC_QLAB_ENV ?? (isProduction ? "" : "local");

function origin(value: string | undefined): string | null {
  try {
    return value ? new URL(value).origin : null;
  } catch {
    return null;
  }
}
const issuerOrigin = origin(process.env.NEXT_PUBLIC_OIDC_ISSUER);

// Content-Security-Policy. Next.js emits inline bootstrap scripts and React/KaTeX use inline style attributes, so
// script-src and style-src keep 'unsafe-inline' (a per-request nonce would force every page to render dynamically).
// 'unsafe-eval' is allowed only by the development server (React refresh needs it); never in a production build.
const csp = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline'${isProduction ? "" : " 'unsafe-eval'"}`,
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  `connect-src 'self'${issuerOrigin ? ` ${issuerOrigin}` : ""}`,
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "object-src 'none'",
  `form-action 'self'${issuerOrigin ? ` ${issuerOrigin}` : ""}`,
].join("; ");

const securityHeaders = [
  { key: "Content-Security-Policy", value: csp },
  { key: "Referrer-Policy", value: "no-referrer" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  ...(isProduction ? [{ key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains" }] : []),
];

const config: NextConfig = {
  // The Playwright end-to-end run starts `next dev` next to `next start`; it needs its own build directory.
  // Self-contained server bundle for the deployment image. The trace root is the monorepo root so workspace packages are included.
  output: "standalone",
  outputFileTracingRoot: path.join(__dirname, "../.."),
  distDir: process.env.QLAB_DIST_DIR ?? ".next",
  env: { NEXT_PUBLIC_QLAB_ENV: qlabEnv },
  transpilePackages: ["@qlab/api-client", "@qlab/question-renderer", "@qlab/question-editor"],
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
  async rewrites() {
    // The browser never talks to the API directly (no CORS). Only these two paths are proxied.
    return [
      { source: "/api/v1/:path*", destination: `${apiUrl}/v1/:path*` },
      { source: "/api/healthz", destination: `${apiUrl}/healthz` },
    ];
  },
};

export default config;
