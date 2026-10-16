"use client";

import { useQuery } from "@tanstack/react-query";
import type { ResponsePage } from "@qlab/api-client";
import { unwrap } from "./admin";
import { useApi } from "./api";
import { answeredIds } from "./learn";

export const RESPONSES_KEY = ["learn", "responses"] as const;
const MAX_PAGES = 10;

/** Ids of the questions the caller has answered. Reads up to 1000 answers; a failure just hides the badges. */
export function useAnsweredIds(enabled: boolean): Set<string> {
  const api = useApi();
  const query = useQuery({
    queryKey: [...RESPONSES_KEY, "answered-ids"],
    enabled,
    retry: false,
    queryFn: async (): Promise<string[]> => {
      const ids = new Set<string>();
      let cursor: string | undefined;
      for (let i = 0; i < MAX_PAGES; i += 1) {
        const page: ResponsePage = unwrap(
          await api.GET("/v1/me/responses", { params: { query: { cursor, limit: 100 } } }),
        );
        for (const id of answeredIds(page.items)) ids.add(id);
        if (!page.next_cursor) break;
        cursor = page.next_cursor;
      }
      return [...ids];
    },
  });
  return new Set(query.data ?? []);
}
