"use client";

import { useMemo } from "react";
import { createApiClient, type ApiClient } from "@qlab/api-client";
import { getAccessToken } from "./token-source";

/** The typed API client. The browser calls the same-origin `/api` proxy (next.config.ts). */
export function useApi(): ApiClient {
  return useMemo(() => createApiClient({ baseUrl: "/api", getToken: getAccessToken }), []);
}
