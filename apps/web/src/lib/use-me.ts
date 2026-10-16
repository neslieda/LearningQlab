"use client";

import { useQuery } from "@tanstack/react-query";
import type { Me } from "@qlab/api-client";
import { ApiError } from "./admin";
import { problemMessage } from "./decisions";
import { useApi } from "./api";
import { getAccessToken, signInAvailable } from "./token-source";

export const ME_KEY = ["me"] as const;
export const SESSION_KEY = ["oidc-user"] as const;

/** The signed-in account. Never calls the API without a token. `enabled` tells whether this build can sign in at all. */
export function useMe(): { me: Me | null; enabled: boolean; isLoading: boolean; error: string | null } {
  const api = useApi();
  const enabled = signInAvailable();
  const query = useQuery({
    queryKey: ME_KEY,
    enabled,
    queryFn: async (): Promise<Me | null> => {
      if (!(await getAccessToken())) return null;
      const { data, response, error } = await api.GET("/v1/me");
      if (!data) {
        const problem = new ApiError(response.status, error).problem;
        if (problem.code === "mfa_required") throw new Error(problemMessage(problem).message);
        throw new Error(`Sign-in check failed (HTTP ${response.status})`);
      }
      return data;
    },
  });
  return { me: query.data ?? null, enabled, isLoading: query.isLoading, error: query.error ? query.error.message : null };
}

/** Whether an OIDC session exists in this tab (an account may not exist yet, e.g. before an invite is used). */
export function useHasSession(): { hasSession: boolean; isLoading: boolean } {
  const enabled = signInAvailable();
  const query = useQuery({
    queryKey: SESSION_KEY,
    enabled,
    queryFn: async () => (await getAccessToken()) !== null,
  });
  return { hasSession: query.data === true, isLoading: query.isLoading };
}
