"use client";

import { useMemo } from "react";
import { createApiClient, type ApiClient } from "@qlab/api-client";
import { readToken } from "./token";

/** The typed API client. The browser calls the same-origin `/api` proxy (next.config.ts). */
export function useApi(): ApiClient {
  return useMemo(
    () =>
      createApiClient({
        baseUrl: "/api",
        // NODE_ENV is inlined at build time: in a production build the token branch is dead code and is removed.
        getToken: process.env.NODE_ENV !== "production" ? () => (typeof window === "undefined" ? null : readToken()) : undefined,
      }),
    [],
  );
}
