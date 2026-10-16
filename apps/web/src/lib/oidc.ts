"use client";

// Browser authorization code flow with PKCE (oidc-client-ts). Tokens live in sessionStorage only.
import { UserManager, WebStorageStateStore, type User } from "oidc-client-ts";
import { config, scopesFor, type SignInKind } from "./config";
import { clearInviteCode, readInviteCode, safeReturnPath } from "./invite-code";
import { clearToken } from "./token";

let manager: UserManager | null = null;

/** `null` on the server, when running locally, or when the OIDC variables are missing. */
export function getManager(): UserManager | null {
  if (typeof window === "undefined" || config.local || !config.oidc) return null;
  if (!manager) {
    const o = config.oidc;
    manager = new UserManager({
      authority: o.issuer,
      client_id: o.clientId,
      redirect_uri: `${window.location.origin}/auth/callback`,
      post_logout_redirect_uri: `${window.location.origin}/`,
      response_type: "code",
      scope: scopesFor(o, "learner"),
      userStore: new WebStorageStateStore({ store: window.sessionStorage }),
      stateStore: new WebStorageStateStore({ store: window.sessionStorage }),
      // offline_access gives a refresh token, so renewal needs no hidden iframe.
      automaticSilentRenew: true,
      loadUserInfo: false,
    });
  }
  return manager;
}

export async function currentUser(): Promise<User | null> {
  const m = getManager();
  if (!m) return null;
  const user = await m.getUser();
  return user && !user.expired ? user : null;
}

export async function startSignIn(kind: SignInKind, returnTo?: string): Promise<void> {
  const m = getManager();
  if (!m || !config.oidc) throw new Error("Sign-in is not configured");
  await m.signinRedirect({ scope: scopesFor(config.oidc, kind), state: { returnTo: safeReturnPath(returnTo) } });
}

let pendingCallback: Promise<string> | null = null;

/** Finishes the redirect and returns the page to open next. Safe to call twice (React strict mode). */
export function completeSignIn(): Promise<string> {
  if (!pendingCallback) {
    pendingCallback = (async () => {
      const m = getManager();
      if (!m) throw new Error("Sign-in is not configured");
      const user = await m.signinCallback();
      const state = user?.state as { returnTo?: unknown } | undefined;
      if (typeof state?.returnTo === "string" && state.returnTo !== "/") return safeReturnPath(state.returnTo);
      const code = readInviteCode();
      return code ? `/invite/${code}` : "/";
    })();
    pendingCallback.catch(() => {
      pendingCallback = null;
    });
  }
  return pendingCallback;
}

/** Ends the session at the issuer and clears everything this app keeps in the tab. */
export async function signOut(): Promise<void> {
  clearToken();
  clearInviteCode();
  const m = getManager();
  if (!m) return;
  try {
    await m.signoutRedirect();
  } catch {
    // No end-session endpoint or the issuer is unreachable: at least drop the local session.
    await m.removeUser();
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination -- full reload on purpose: drop all in-memory state
    window.location.assign("/");
  }
}
