"use client";

import { useQuery } from "@tanstack/react-query";
import type { Me } from "@qlab/api-client";
import { useApi } from "./api";
import { readToken } from "./token";

export const ME_KEY = ["me"] as const;

/** The signed-in account (development token only until slice 9). Never calls the API without a token. */
export function useMe(): { me: Me | null; enabled: boolean; isLoading: boolean; error: string | null } {
  const api = useApi();
  const query = useQuery({
    queryKey: ME_KEY,
    enabled: process.env.NODE_ENV !== "production",
    queryFn: async (): Promise<Me | null> => {
      if (process.env.NODE_ENV === "production" || !readToken()) return null;
      const { data, response } = await api.GET("/v1/me");
      if (!data) throw new Error(`Sign-in check failed (HTTP ${response.status})`);
      return data;
    },
  });
  return {
    me: query.data ?? null,
    enabled: process.env.NODE_ENV !== "production",
    isLoading: query.isLoading,
    error: query.error ? query.error.message : null,
  };
}
