"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import type { LearnerQuestionPage } from "@qlab/api-client";
import { unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import {
  CLASSES,
  LEVELS,
  classLabel,
  filtersFromParams,
  filtersToSearch,
  isValidSection,
  type LearnFilters,
} from "@/lib/learn";
import { useAnsweredIds } from "@/lib/responses";
import { ScrollBox } from "../admin/status-badge";
import { SessionGate } from "../admin/staff-gate";
import { AnswerProblem } from "./answer-problem";
import { PrivacyNotice } from "./privacy-notice";

export function LearnList() {
  return <SessionGate allowed={() => true} denied="">{() => <Inner />}</SessionGate>;
}

function Inner() {
  const api = useApi();
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const filters = filtersFromParams(params);
  const answered = useAnsweredIds(true);

  // null: the field follows the URL; a string: the user is typing.
  const [typed, setTyped] = useState<string | null>(null);
  const sectionDraft = typed ?? filters.examSection;
  const sectionInvalid = sectionDraft.trim() !== "" && !isValidSection(sectionDraft.trim());

  function go(next: LearnFilters) {
    const qs = filtersToSearch(next);
    router.push(qs ? `${pathname}?${qs}` : pathname);
  }
  function commitSection() {
    const v = sectionDraft.trim();
    if (v !== "" && !isValidSection(v)) return;
    setTyped(null);
    if (v !== filters.examSection) go({ ...filters, examSection: v });
  }

  const query = useInfiniteQuery({
    queryKey: ["learn", "questions", filters],
    initialPageParam: null as string | null,
    queryFn: async ({ pageParam }): Promise<LearnerQuestionPage> =>
      unwrap(
        await api.GET("/v1/questions", {
          params: {
            query: {
              exam_section: filters.examSection || undefined,
              question_class: filters.questionClass,
              level: filters.level,
              cursor: pageParam ?? undefined,
              limit: 20,
            },
          },
        }),
      ),
    getNextPageParam: (last) => last.next_cursor,
  });
  const items = query.data?.pages.flatMap((p) => p.items) ?? [];
  const field = "rounded border border-[var(--page-border)] bg-transparent p-1.5";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Practice</h1>
        <Link href="/learn/history" className="underline">
          My answers
        </Link>
      </div>
      <PrivacyNotice />
      <form
        aria-label="Filters"
        className="flex flex-wrap items-end gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          commitSection();
        }}
      >
        <label className="block text-sm">
          <span className="block font-medium">Exam section</span>
          <input
            type="text"
            value={sectionDraft}
            onChange={(e) => setTyped(e.target.value)}
            onBlur={commitSection}
            maxLength={120}
            aria-invalid={sectionInvalid ? true : undefined}
            aria-describedby={sectionInvalid ? "section-error" : undefined}
            className={`w-40 ${field}`}
          />
          {sectionInvalid ? (
            <span id="section-error" role="alert" className="block text-red-700 dark:text-red-300">
              Use letters, digits, dots and underscores, starting with a letter or digit.
            </span>
          ) : null}
        </label>
        <label className="block text-sm">
          <span className="block font-medium">Question class</span>
          <select
            value={filters.questionClass ?? ""}
            onChange={(e) => go({ ...filters, questionClass: CLASSES.find((c) => c === e.target.value) })}
            className={field}
          >
            <option value="">Any</option>
            {CLASSES.map((c) => (
              <option key={c} value={c}>
                {classLabel(c)}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="block font-medium">Level</span>
          <select value={filters.level ?? ""} onChange={(e) => go({ ...filters, level: LEVELS.find((l) => l === e.target.value) })} className={field}>
            <option value="">Any</option>
            {LEVELS.map((l) => (
              <option key={l} value={l}>
                {l.toUpperCase()}
              </option>
            ))}
          </select>
        </label>
      </form>

      {query.isPending ? <p>Loading...</p> : null}
      {query.isError ? <AnswerProblem error={query.error} onReload={() => void query.refetch()} /> : null}
      {query.isSuccess && items.length === 0 ? <p>No questions match these filters.</p> : null}
      {items.length > 0 ? (
        <ScrollBox label="Questions table">
          <table className="w-full border-collapse text-left text-sm">
            <caption className="sr-only">Practice questions</caption>
            <thead>
              <tr className="border-b border-[var(--page-border)]">
                <th scope="col" className="p-2">Question</th>
                <th scope="col" className="p-2">Class</th>
                <th scope="col" className="p-2">Section</th>
                <th scope="col" className="p-2">Level</th>
                <th scope="col" className="p-2">Marks</th>
                <th scope="col" className="p-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {items.map((q, index) => (
                <tr key={q.id} className="border-b border-[var(--page-border)] align-top">
                  <th scope="row" className="p-2 font-normal">
                    <Link href={`/learn/${q.id}`} className="underline">
                      {`Question ${index + 1}`}
                    </Link>
                  </th>
                  <td className="p-2">{classLabel(q.question_class)}</td>
                  <td className="p-2">{q.exam_section}</td>
                  <td className="p-2">{q.levels.map((l) => l.toUpperCase()).join(", ")}</td>
                  <td className="p-2">{q.total_marks}</td>
                  <td className="p-2">
                    {answered.has(q.id) ? (
                      <span className="inline-block whitespace-nowrap rounded border border-green-700 px-1.5 py-0.5">Answered</span>
                    ) : null}
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
