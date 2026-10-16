"use client";

import Link from "next/link";
import { isStaff } from "@/lib/decisions";
import { useMe } from "@/lib/use-me";

export function SiteHeader() {
  const { me, enabled } = useMe();
  return (
    <header className="border-b border-[var(--page-border)]">
      <div className="mx-auto flex w-full max-w-5xl flex-wrap items-center justify-between gap-2 px-4 py-3">
        <Link href="/" className="text-lg font-semibold">
          Qlab
        </Link>
        <nav aria-label="Account" className="flex flex-wrap items-center gap-4 text-sm">
          {me && isStaff(me.roles) ? (
            <Link href="/admin/questions" className="underline">
              Questions
            </Link>
          ) : null}
          {me ? (
            <span>Signed in: {me.roles.join(", ") || "no roles"}</span>
          ) : enabled ? (
            <Link href="/dev/sign-in" className="underline">
              Sign in (development)
            </Link>
          ) : null}
        </nav>
      </div>
    </header>
  );
}
