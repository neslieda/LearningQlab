import type { NextConfig } from "next";

const apiUrl = (process.env.QLAB_API_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");

const config: NextConfig = {
  transpilePackages: ["@qlab/api-client", "@qlab/question-renderer"],
  async rewrites() {
    // The browser never talks to the API directly (no CORS). Only these two paths are proxied.
    return [
      { source: "/api/v1/:path*", destination: `${apiUrl}/v1/:path*` },
      { source: "/api/healthz", destination: `${apiUrl}/healthz` },
    ];
  },
};

export default config;
