"use client";

import Link from "next/link";
import { useSyncExternalStore, type ReactNode } from "react";
import type { Me } from "@qlab/api-client";
import { isStaff } from "@/lib/decisions";
import { useMe } from "@/lib/use-me";

const subscribeNever = () => () => {};

/** Renders children only for signed-in staff; otherwise sends no admin request at all. */
export function StaffGate({ children }: { children: (me: Me) => ReactNode }) {
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
          <Link href="/dev/sign-in" className="underline">
            Sign in with a development token
          </Link>
        ) : null}
      </p>
    );
  }
  if (!isStaff(me.roles)) return <p>This area is for staff.</p>;
  return <>{children(me)}</>;
}
