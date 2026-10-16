"use client";

import Link from "next/link";
import { ApiError } from "@/lib/admin";
import { signInHref } from "@/lib/config";
import { answerProblemMessage } from "@/lib/learn";

/** The text for a failed learner request. */
export function AnswerProblem({ error, onReload }: { error: unknown; onReload?: () => void }) {
  if (!error) return null;
  const m = error instanceof ApiError ? answerProblemMessage(error.problem) : { message: "Something went wrong", reasons: [], followUp: null };
  return (
    <div role="alert" className="space-y-2 rounded border border-red-700 p-3">
      <p>{m.message}</p>
      {m.followUp === "sign-in" ? (
        <Link href={signInHref()} className="underline">
          Sign in
        </Link>
      ) : onReload ? (
        <button type="button" onClick={onReload} className="rounded border border-[var(--page-border)] px-3 py-1.5">
          Try again
        </button>
      ) : null}
    </div>
  );
}
