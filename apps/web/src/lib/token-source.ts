import { config, type WebConfig } from "./config";
import { readToken } from "./token";

export type TokenSourceKind = "dev" | "oidc" | "none";

/** Which credential the API client sends: the development token only when local, otherwise the OIDC access token. */
export function selectTokenSource(cfg: Pick<WebConfig, "local" | "oidc">): TokenSourceKind {
  if (cfg.local) return "dev";
  return cfg.oidc ? "oidc" : "none";
}

/** True when some way of signing in exists in this build. */
export function signInAvailable(cfg: Pick<WebConfig, "local" | "oidc"> = config): boolean {
  return selectTokenSource(cfg) !== "none";
}

export async function getAccessToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;
  const kind = selectTokenSource(config);
  if (kind === "dev") return readToken();
  if (kind === "oidc") {
    const { currentUser } = await import("./oidc");
    return (await currentUser())?.access_token ?? null;
  }
  return null;
}
