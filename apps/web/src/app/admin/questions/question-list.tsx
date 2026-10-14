"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import type { AdminQuestionPage } from "@qlab/api-client";
import { ApiError, shortId, unwrap } from "@/lib/admin";
import { problemMessage } from "@/lib/decisions";
import { useApi } from "@/lib/api";
import { ScrollBox, StatusBadge } from "../status-badge";
import { StaffGate } from "../staff-gate";

const STATUSES = ["draft", "auto_checking", "needs_fix", "in_review", "approved", "published", "withdrawn", "rejected"] as const;
const CLASSES = ["mcq", "data_based", "short_structured", "long_structured"] as const;
const LEVELS = ["sl", "hl"] as const;
type Status = (typeof STATUSES)[number];
type QClass = (typeof CLASSES)[number];
type Level = (typeof LEVELS)[number];

function pick<T extends string>(value: string | null, allowed: readonly T[]): T | undefined {
  return allowed.find((a) => a === value);
}

export function QuestionList() {
  return <StaffGate>{() => <Inner />}</StaffGate>;
}

function Inner() {
  const api = useApi();
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const status = pick(params.get("status"), STATUSES);
  const questionClass = pick(params.get("question_class"), CLASSES);
  const level = pick(params.get("level"), LEVELS);
  const examSection = params.get("exam_section") ?? "";
  const awaitingVisuals = params.get("has_unverified_visuals") === "true";

  // null: the field follows the URL (so the back button updates it); a string: the user is typing.
  const [typed, setTyped] = useState<string | null>(null);
  const sectionDraft = typed ?? examSection;

  function setParam(key: string, value: string | null) {
    const next = new URLSearchParams(params.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    const qs = next.toString();
    router.push(qs ? `${pathname}?${qs}` : pathname);
  }
  function commitSection() {
    const v = sectionDraft.trim();
    setTyped(null);
    if (v !== examSection) setParam("exam_section", v || null);
  }

  const query = useInfiniteQuery({
    queryKey: ["admin", "questions", { status, questionClass, level, examSection, awaitingVisuals }],
    initialPageParam: null as string | null,
    queryFn: async ({ pageParam }): Promise<AdminQuestionPage> =>
      unwrap(
        await api.GET("/v1/admin/questions", {
          params: {
            query: {
              status: status as Status | undefined,
              question_class: questionClass as QClass | undefined,
              level: level as Level | undefined,
              exam_section: examSection || undefined,
              has_unverified_visuals: awaitingVisuals ? true : undefined,
              cursor: pageParam ?? undefined,
              limit: 50,
            },
          },
        }),
      ),
    getNextPageParam: (last) => last.next_cursor,
  });

  const items = query.data?.pages.flatMap((p) => p.items) ?? [];

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Questions</h1>
      <form
        aria-label="Filters"
        className="flex flex-wrap items-end gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          commitSection();
        }}
      >
        <label className="block text-sm">
          <span className="block font-medium">Status</span>
          <select value={status ?? ""} onChange={(e) => setParam("status", e.target.value || null)} className="rounded border border-[var(--page-border)] bg-transparent p-1.5">
            <option value="">Any</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="block font-medium">Exam section</span>
          <input
            type="text"
            value={sectionDraft}
            onChange={(e) => setTyped(e.target.value)}
            onBlur={commitSection}
            maxLength={120}
            className="w-40 rounded border border-[var(--page-border)] bg-transparent p-1.5"
          />
        </label>
        <label className="block text-sm">
          <span className="block font-medium">Question class</span>
          <select value={questionClass ?? ""} onChange={(e) => setParam("question_class", e.target.value || null)} className="rounded border border-[var(--page-border)] bg-transparent p-1.5">
            <option value="">Any</option>
            {CLASSES.map((s) => (
              <option key={s} value={s}>
                {s.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="block font-medium">Level</span>
          <select value={level ?? ""} onChange={(e) => setParam("level", e.target.value || null)} className="rounded border border-[var(--page-border)] bg-transparent p-1.5">
            <option value="">Any</option>
            {LEVELS.map((s) => (
              <option key={s} value={s}>
                {s.toUpperCase()}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2 pb-2 text-sm">
          <input type="checkbox" checked={awaitingVisuals} onChange={(e) => setParam("has_unverified_visuals", e.target.checked ? "true" : null)} />
          <span className="font-medium">Awaiting figures</span>
        </label>
      </form>

      {query.isPending ? <p>Loading...</p> : null}
      {query.isError ? (
        <p role="alert">
          {query.error instanceof ApiError ? problemMessage(query.error.problem).message : "Something went wrong"}
        </p>
      ) : null}
      {query.isSuccess && items.length === 0 ? <p>No questions match these filters.</p> : null}
      {items.length > 0 ? (
        <ScrollBox label="Questions table">
          <table className="w-full min-w-[40rem] border-collapse text-left text-sm">
            <caption className="sr-only">Questions</caption>
            <thead>
              <tr className="border-b border-[var(--page-border)]">
                <th scope="col" className="p-2">Question</th>
                <th scope="col" className="p-2">Class</th>
                <th scope="col" className="p-2">Section</th>
                <th scope="col" className="p-2">Levels</th>
                <th scope="col" className="p-2">Marks</th>
                <th scope="col" className="p-2">Latest version</th>
                <th scope="col" className="p-2">Flags</th>
              </tr>
            </thead>
            <tbody>
              {items.map((q) => (
                <tr key={q.id} className="border-b border-[var(--page-border)] align-top">
                  <th scope="row" className="p-2 font-normal">
                    <Link href={`/admin/questions/${q.id}`} className="underline">
                      {q.source_ref ?? shortId(q.id)}
                    </Link>
                  </th>
                  <td className="p-2">{q.latest_version.question_class.replace(/_/g, " ")}</td>
                  <td className="p-2">{q.latest_version.exam_section}</td>
                  <td className="p-2">{q.latest_version.levels.map((l) => l.toUpperCase()).join(", ")}</td>
                  <td className="p-2">{q.latest_version.total_marks}</td>
                  <td className="p-2">
                    v{q.latest_version.version_no} <StatusBadge status={q.latest_version.status} />
                  </td>
                  <td className="p-2">
                    {q.published_version_id ? <span className="mr-1 inline-block whitespace-nowrap rounded border border-green-700 px-1.5 py-0.5">Published</span> : null}
                    {q.working_version_id ? <span className="inline-block whitespace-nowrap rounded border border-blue-600 px-1.5 py-0.5">In progress</span> : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </ScrollBox>
      ) : null}
      {query.hasNextPage ? (
        <button
          type="button"
          onClick={() => void query.fetchNextPage()}
          disabled={query.isFetchingNextPage}
          className="rounded border border-[var(--page-border)] px-3 py-1.5"
        >
          Load more
        </button>
      ) : null}
    </div>
  );
}
