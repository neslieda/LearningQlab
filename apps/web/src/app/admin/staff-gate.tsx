"use client";

import Link from "next/link";
import { useSyncExternalStore, type ReactNode } from "react";
import type { Me } from "@qlab/api-client";
import { config, signInHref } from "@/lib/config";
import { canInvite, isStaff } from "@/lib/decisions";
import { useMe } from "@/lib/use-me";

const subscribeNever = () => () => {};

function SessionGate({
  allowed,
  denied,
  children,
}: {
  allowed: (roles: Me["roles"]) => boolean;
  denied: string;
  children: (me: Me) => ReactNode;
}) {
  const { me, enabled, isLoading, error } = useMe();
  // The server cannot know the session; render the same placeholder there and on the first client pass.
  const hydrated = useSyncExternalStore(subscribeNever, () => true, () => false);
  if (!hydrated || isLoading) return <p>Checking session...</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!me) {
    return (
      <p>
        You are not signed in.{" "}
        {enabled ? (
          <Link href={signInHref()} className="underline">
            {config.local ? "Sign in with a development token" : "Sign in"}
          </Link>
        ) : null}
      </p>
    );
  }
  if (!allowed(me.roles)) return <p>{denied}</p>;
  return <>{children(me)}</>;
}

/** Renders children only for signed-in staff; otherwise sends no admin request at all. */
export function StaffGate({ children }: { children: (me: Me) => ReactNode }) {
  return (
    <SessionGate allowed={isStaff} denied="This area is for staff.">
      {children}
    </SessionGate>
  );
}

/** Renders children only for teachers and platform admins (the invite screen). */
export function InviterGate({ children }: { children: (me: Me) => ReactNode }) {
  return (
    <SessionGate allowed={canInvite} denied="This area is for teachers and platform admins.">
      {children}
    </SessionGate>
  );
}
