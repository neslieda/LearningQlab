"use client";

import Link from "next/link";
import { useInfiniteQuery } from "@tanstack/react-query";
import type { ResponsePage } from "@qlab/api-client";
import { formatTime, unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import { excerpt, toAnswerRows } from "@/lib/learn";
import { RESPONSES_KEY } from "@/lib/responses";
import { ScrollBox } from "../../admin/status-badge";
import { SessionGate } from "../../admin/staff-gate";
import { AnswerProblem } from "../answer-problem";

export function History() {
  return <SessionGate allowed={() => true} denied="">{() => <Inner />}</SessionGate>;
}

function Inner() {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: [...RESPONSES_KEY, "history"],
    initialPageParam: null as string | null,
    queryFn: async ({ pageParam }): Promise<ResponsePage> =>
      unwrap(await api.GET("/v1/me/responses", { params: { query: { cursor: pageParam ?? undefined, limit: 20 } } })),
    getNextPageParam: (last) => last.next_cursor,
  });
  const rows = toAnswerRows(query.data?.pages.flatMap((p) => p.items) ?? []);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">My answers</h1>
        <Link href="/learn" className="underline">
          Back to questions
        </Link>
      </div>
      {query.isPending ? <p>Loading...</p> : null}
      {query.isError ? <AnswerProblem error={query.error} onReload={() => void query.refetch()} /> : null}
      {query.isSuccess && rows.length === 0 ? (
        <p>
          You have not answered any question yet.{" "}
          <Link href="/learn" className="underline">
            Start practising
          </Link>
        </p>
      ) : null}
      {rows.length > 0 ? (
        <ScrollBox label="My answers table">
          <table className="w-full border-collapse text-left text-sm">
            <caption className="sr-only">My answers, newest first</caption>
            <thead>
              <tr className="border-b border-[var(--page-border)]">
                <th scope="col" className="p-2">When</th>
                <th scope="col" className="p-2">Answer</th>
                <th scope="col" className="p-2">Result</th>
                <th scope="col" className="p-2">Question</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-b border-[var(--page-border)] align-top">
                  <th scope="row" className="p-2 font-normal">{formatTime(r.createdAt)}</th>
                  <td className="min-w-40 break-words p-2">{r.kind === "mcq" ? r.what : excerpt(r.answer)}</td>
                  <td className="p-2">{r.outcome ?? (r.kind === "written" ? "Written answer" : "")}</td>
                  <td className="p-2">
                    <Link href={`/learn/${r.questionId}`} className="underline">
                      Open question
                    </Link>
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
