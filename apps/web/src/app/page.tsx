"use client";

import Link from "next/link";
import { config, signInHref } from "@/lib/config";
import { isStaff } from "@/lib/decisions";
import { useMe } from "@/lib/use-me";

export default function HomePage() {
  const { me, enabled } = useMe();
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Qlab</h1>
      <p>
        {me ? (
          <>Signed in with role: {me.roles.join(", ") || "none"}.</>
        ) : enabled ? (
          <>
            You are not signed in.{" "}
            <Link href={signInHref()} className="underline">
              {config.local ? "Sign in with a development token" : "Sign in"}
            </Link>
            .
          </>
        ) : (
          <>You are not signed in.</>
        )}
      </p>
      <section aria-labelledby="staff-heading" className="rounded border border-[var(--page-border)] p-4">
        <h2 id="staff-heading" className="text-lg font-medium">Staff area</h2>
        {me && isStaff(me.roles) ? (
          <p>
            <Link href="/admin/questions" className="underline">
              Review questions
            </Link>
          </p>
        ) : (
          <p className="text-[var(--page-muted)]">Question review is available to staff accounts.</p>
        )}
      </section>
      <section aria-labelledby="learner-heading" className="rounded border border-[var(--page-border)] p-4">
        <h2 id="learner-heading" className="text-lg font-medium">Practice</h2>
        {me ? (
          <p>
            <Link href="/learn" className="underline">
              Solve questions
            </Link>
          </p>
        ) : (
          <p className="text-[var(--page-muted)]">Sign in to practise questions and keep your answers.</p>
        )}
      </section>
    </div>
  );
}
