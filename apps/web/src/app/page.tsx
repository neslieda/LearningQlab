"use client";

import Link from "next/link";
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
            You are not signed in. <Link href="/dev/sign-in" className="underline">Sign in with a development token</Link>.
          </>
        ) : (
          <>You are not signed in.</>
        )}
      </p>
      <section aria-labelledby="staff-heading" className="rounded border border-[var(--page-border)] p-4">
        <h2 id="staff-heading" className="text-lg font-medium">Staff area</h2>
        <p className="text-[var(--page-muted)]">Question review and editing will appear here (slice 7).</p>
      </section>
      <section aria-labelledby="learner-heading" className="rounded border border-[var(--page-border)] p-4">
        <h2 id="learner-heading" className="text-lg font-medium">Learner preview</h2>
        <p className="text-[var(--page-muted)]">Question lists and answering will appear here (slice 8).</p>
      </section>
    </div>
  );
}
