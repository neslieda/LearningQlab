"use client";

import Link from "next/link";
import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { useQueryClient } from "@tanstack/react-query";
import type { Role } from "@qlab/api-client";
import { ApiError } from "@/lib/admin";
import { useApi } from "@/lib/api";
import { config, signInHref } from "@/lib/config";
import { INVITE_INVALID_MESSAGE, isStaff, problemMessage } from "@/lib/decisions";
import { clearInviteCode, readInviteCode, storeInviteCode, takeCodeFromHash } from "@/lib/invite-code";
import { ME_KEY, useHasSession } from "@/lib/use-me";
import { SignInButtons } from "../sign-in/sign-in-buttons";

type Outcome = { kind: "done"; roles: Role[]; accountId: string } | { kind: "invalid" } | { kind: "error"; message: string };

function roleSentence(roles: readonly string[]): string {
  return roles.length === 1 ? `the ${roles[0]} role` : `the ${roles.join(", ")} roles`;
}

const subscribeNever = () => () => {};

export function InviteView() {
  const api = useApi();
  const queryClient = useQueryClient();
  const { hasSession, isLoading: sessionLoading } = useHasSession();
  // The session lives in the browser; render the same placeholder on the server and on the first client pass.
  const hydrated = useSyncExternalStore(subscribeNever, () => true, () => false);
  const isLoading = !hydrated || sessionLoading;
  const started = useRef(false);
  const [result, setOutcome] = useState<Outcome | null>(null);

  useEffect(() => {
    if (started.current) return;
    // The code comes from the URL fragment (removed from the address bar at once), or from the tab's storage after sign-in.
    const code = takeCodeFromHash() ?? readInviteCode();
    if (!code) {
      clearInviteCode();
      void Promise.resolve().then(() => setOutcome({ kind: "invalid" }));
      return;
    }
    if (isLoading || config.local || !config.oidc) return;
    if (!hasSession) {
      storeInviteCode(code);
      return;
    }
    if (started.current) return;
    started.current = true;
    void (async () => {
      try {
        const { data, response, error } = await api.POST("/v1/invites/redeem", { body: { code } });
        if (data) {
          setOutcome({ kind: "done", roles: data.roles, accountId: data.account_id });
          await queryClient.invalidateQueries({ queryKey: ME_KEY });
        } else {
          const problem = new ApiError(response.status, error).problem;
          setOutcome(problem.code === "invite_not_found" ? { kind: "invalid" } : { kind: "error", message: problemMessage(problem).message });
        }
      } catch {
        setOutcome({ kind: "error", message: "The server could not be reached. Try again later." });
      } finally {
        clearInviteCode();
      }
    })();
  }, [api, hasSession, isLoading, queryClient]);

  const outcome = result;
  const heading = <h1 className="text-2xl font-semibold">Invitation</h1>;

  if (outcome?.kind === "invalid") {
    return (
      <div className="space-y-3">
        {heading}
        <p role="alert">{INVITE_INVALID_MESSAGE}</p>
      </div>
    );
  }
  if (outcome?.kind === "error") {
    return (
      <div className="space-y-3">
        {heading}
        <p role="alert">{outcome.message}</p>
        <button type="button" onClick={() => window.location.reload()} className="rounded border border-[var(--page-border)] px-3 py-1.5">
          Try again
        </button>
      </div>
    );
  }
  if (outcome?.kind === "done") {
    const staff = isStaff(outcome.roles);
    return (
      <div className="space-y-3">
        {heading}
        <p role="status">You now have {roleSentence(outcome.roles)}.</p>
        <p>
          Your account ID: <code className="break-all">{outcome.accountId}</code>
        </p>
        <Link href={staff ? "/admin/questions" : "/"} className="underline">
          {staff ? "Go to the questions" : "Go to the home page"}
        </Link>
      </div>
    );
  }
  if (config.local) {
    return (
      <div className="space-y-3">
        {heading}
        <p>
          Invites need the real sign-in, which a local build does not have. Use the{" "}
          <Link href={signInHref()} className="underline">
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
        {heading}
        <p role="alert">Sign-in is not available: this site is not configured for it.</p>
      </div>
    );
  }
  if (isLoading || hasSession) {
    return (
      <div className="space-y-3">
        {heading}
        <p role="status">Using your invitation...</p>
      </div>
    );
  }
  return (
    <div className="space-y-4">
      {heading}
      <p>Sign in to use this invitation. You will return to this page afterwards.</p>
      <SignInButtons returnTo="/invite" />
    </div>
  );
}
