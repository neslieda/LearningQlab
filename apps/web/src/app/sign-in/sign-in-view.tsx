"use client";

import Link from "next/link";
import { useSyncExternalStore } from "react";
import { useSearchParams } from "next/navigation";
import { config } from "@/lib/config";
import { safeReturnPath } from "@/lib/invite-code";
import { useHasSession } from "@/lib/use-me";
import { SignInButtons } from "./sign-in-buttons";

const subscribeNever = () => () => {};

export function SignInView() {
  const params = useSearchParams();
  const returnTo = safeReturnPath(params.get("next"));
  const { hasSession, isLoading: sessionLoading } = useHasSession();
  // The session lives in the browser; render the same placeholder on the server and on the first client pass.
  const hydrated = useSyncExternalStore(subscribeNever, () => true, () => false);
  const isLoading = !hydrated || sessionLoading;

  if (config.local) {
    return (
      <div className="space-y-3">
        <h1 className="text-2xl font-semibold">Sign in</h1>
        <p>
          This is a local build. Use the{" "}
          <Link href="/dev/sign-in" className="underline">
            development sign-in
          </Link>
          .
        </p>
      </div>
    );
  }
  if (!config.oidc) {
    return (
      <div className="space-y-3">
        <h1 className="text-2xl font-semibold">Sign in</h1>
        <p role="alert">Sign-in is not available: this site is not configured for it.</p>
      </div>
    );
  }
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Sign in</h1>
      {isLoading ? <p>Checking session...</p> : null}
      {isLoading ? null : hasSession ? (
        <p>
          You are signed in.{" "}
          <Link href={returnTo} className="underline">
            Continue
          </Link>
        </p>
      ) : (
        <>
          <p>Students and teachers use Sign in. Staff accounts use Staff sign-in, which asks for two-step verification.</p>
          <SignInButtons returnTo={returnTo} />
        </>
      )}
    </div>
  );
}
