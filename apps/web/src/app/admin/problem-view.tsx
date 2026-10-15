"use client";

import Link from "next/link";
import { ApiError } from "@/lib/admin";
import { problemMessage } from "@/lib/decisions";

/** Shows the text for a failed request, with the follow-up the code calls for. */
export function ProblemView({ error, questionId, onReload }: { error: unknown; questionId?: string; onReload: () => void }) {
  if (!error) return null;
  const m = error instanceof ApiError ? problemMessage(error.problem) : { message: "Something went wrong", reasons: [], followUp: null };
  return (
    <div role="alert" className="space-y-2 rounded border border-red-700 p-3">
      <p>{m.message}</p>
      {m.reasons.length > 0 ? (
        <ul className="list-disc pl-5">
          {m.reasons.map((r) => (
            <li key={r}>{r}</li>
          ))}
        </ul>
      ) : null}
      {m.followUp === "reload" ? (
        <button type="button" onClick={onReload} className="rounded border border-[var(--page-border)] px-3 py-1.5">
          Reload
        </button>
      ) : null}
      {m.followUp === "sign-in" ? (
        <Link href="/dev/sign-in" className="underline">
          Sign in
        </Link>
      ) : null}
      {m.followUp === "question" && questionId ? (
        <Link href={`/admin/questions/${questionId}`} className="underline">
          Go to the question
        </Link>
      ) : null}
    </div>
  );
}
