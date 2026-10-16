"use client";

import { useState } from "react";
import { startSignIn } from "@/lib/oidc";
import type { SignInKind } from "@/lib/config";

/** "Sign in" (learners organisation) and "Staff sign-in" (staff organisation, two-step verification). */
export function SignInButtons({ returnTo }: { returnTo?: string }) {
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function go(kind: SignInKind) {
    setBusy(true);
    setError(null);
    try {
      await startSignIn(kind, returnTo);
    } catch {
      setBusy(false);
      setError("Sign-in could not be started. Try again later.");
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-3">
        <button type="button" disabled={busy} onClick={() => void go("learner")} className="rounded border border-[var(--page-border)] px-3 py-1.5">
          Sign in
        </button>
        <button type="button" disabled={busy} onClick={() => void go("staff")} className="rounded border border-[var(--page-border)] px-3 py-1.5">
          Staff sign-in
        </button>
      </div>
      {error ? (
        <p role="alert" className="text-red-700 dark:text-red-300">
          {error}
        </p>
      ) : null}
    </div>
  );
}
