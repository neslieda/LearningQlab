"use client";

import Link from "next/link";
import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { config, signInHref } from "@/lib/config";
import { canInvite, isStaff } from "@/lib/decisions";
import { signOut } from "@/lib/oidc";
import { useHasSession, useMe } from "@/lib/use-me";

export function SiteHeader() {
  const { me, enabled } = useMe();
  const { hasSession } = useHasSession();
  const queryClient = useQueryClient();
  const [leaving, setLeaving] = useState(false);

  async function onSignOut() {
    setLeaving(true);
    queryClient.clear();
    await signOut();
  }

  return (
    <header className="border-b border-[var(--page-border)]">
      <div className="mx-auto flex w-full max-w-5xl flex-wrap items-center justify-between gap-2 px-4 py-3">
        <Link href="/" className="text-lg font-semibold">
          Qlab
        </Link>
        <nav aria-label="Account" className="flex flex-wrap items-center gap-4 text-sm">
          {me ? (
            <Link href="/learn" className="underline">
              Practice
            </Link>
          ) : null}
          {me && isStaff(me.roles) ? (
            <Link href="/admin/questions" className="underline">
              Questions
            </Link>
          ) : null}
          {me && canInvite(me.roles) ? (
            <Link href="/admin/invites" className="underline">
              Invites
            </Link>
          ) : null}
          {hasSession || me ? (
            <Link href="/account" className="underline">
              Account
            </Link>
          ) : null}
          {me ? <span>Signed in: {me.roles.join(", ") || "no roles"}</span> : null}
          {!config.local && hasSession ? (
            <button type="button" onClick={() => void onSignOut()} disabled={leaving} className="rounded border border-[var(--page-border)] px-2 py-1">
              Sign out
            </button>
          ) : null}
          {!me && !hasSession && enabled ? (
            <Link href={signInHref()} className="underline">
              {config.local ? "Sign in (development)" : "Sign in"}
            </Link>
          ) : null}
        </nav>
      </div>
    </header>
  );
}
