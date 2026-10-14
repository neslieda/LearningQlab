"use client";

import type { Problem } from "@qlab/api-client";
import type { ProblemLike } from "./decisions";

/** Thrown for any non-2xx answer; carries the problem body when the API sent one. */
export class ApiError extends Error {
  readonly problem: ProblemLike;
  constructor(status: number, body: unknown) {
    const p = (body && typeof body === "object" ? (body as Partial<Problem>) : {}) as Partial<Problem>;
    super(p.title ?? `HTTP ${status}`);
    this.problem = { status, code: typeof p.code === "string" ? p.code : undefined, errors: Array.isArray(p.errors) ? p.errors : [] };
  }
}

export function unwrap<T>(result: { data?: T; error?: unknown; response: Response }): T {
  if (result.data === undefined) throw new ApiError(result.response.status, result.error);
  return result.data;
}

export function shortId(id: string): string {
  return id.slice(0, 12);
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleString();
}
