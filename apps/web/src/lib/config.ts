// Build-time configuration (NEXT_PUBLIC_* variables are inlined by Next.js, so each one must be read by its literal name).
// docs/slices/M1G-9-ACILIS.md sections 2 and 4.

export interface OidcConfig {
  issuer: string;
  clientId: string;
  projectId: string;
  staffOrgId: string;
  learnerOrgId: string;
}

export interface WebConfig {
  /** The deployment name, e.g. `local`, `staging`, `production`; empty when unset. */
  env: string;
  /** Only the explicit value `local` enables the development sign-in. */
  local: boolean;
  /** `null` when any OIDC variable is missing or malformed: sign-in is then unavailable (fail closed). */
  oidc: OidcConfig | null;
}

export interface RawEnv {
  NEXT_PUBLIC_QLAB_ENV?: string;
  NEXT_PUBLIC_OIDC_ISSUER?: string;
  NEXT_PUBLIC_OIDC_CLIENT_ID?: string;
  NEXT_PUBLIC_OIDC_PROJECT_ID?: string;
  NEXT_PUBLIC_OIDC_STAFF_ORG_ID?: string;
  NEXT_PUBLIC_OIDC_LEARNER_ORG_ID?: string;
}

const ID = /^[A-Za-z0-9_.-]+$/;

function parseIssuer(value: string | undefined): string | null {
  const v = (value ?? "").trim();
  if (!v) return null;
  try {
    const u = new URL(v);
    if (u.protocol !== "https:" && !(u.protocol === "http:" && (u.hostname === "localhost" || u.hostname === "127.0.0.1"))) return null;
    // The issuer is compared character for character by the API; keep it exactly as configured.
    return v;
  } catch {
    return null;
  }
}

function parseId(value: string | undefined): string | null {
  const v = (value ?? "").trim();
  return v && ID.test(v) ? v : null;
}

export function parseConfig(raw: RawEnv): WebConfig {
  const env = (raw.NEXT_PUBLIC_QLAB_ENV ?? "").trim();
  const issuer = parseIssuer(raw.NEXT_PUBLIC_OIDC_ISSUER);
  const clientId = parseId(raw.NEXT_PUBLIC_OIDC_CLIENT_ID);
  const projectId = parseId(raw.NEXT_PUBLIC_OIDC_PROJECT_ID);
  const staffOrgId = parseId(raw.NEXT_PUBLIC_OIDC_STAFF_ORG_ID);
  const learnerOrgId = parseId(raw.NEXT_PUBLIC_OIDC_LEARNER_ORG_ID);
  const oidc = issuer && clientId && projectId && staffOrgId && learnerOrgId ? { issuer, clientId, projectId, staffOrgId, learnerOrgId } : null;
  return { env, local: env === "local", oidc };
}

export type SignInKind = "learner" | "staff";

/** The scopes of section 2, without the organisation scope. */
export function baseScopes(projectId: string): string {
  return [
    "openid",
    "profile",
    "email",
    "offline_access",
    `urn:zitadel:iam:org:project:id:${projectId}:aud`,
    "urn:zitadel:iam:user:resourceowner",
  ].join(" ");
}

/** Base scopes plus the organisation the sign-in is made in. */
export function scopesFor(oidc: OidcConfig, kind: SignInKind): string {
  const org = kind === "staff" ? oidc.staffOrgId : oidc.learnerOrgId;
  return `${baseScopes(oidc.projectId)} urn:zitadel:iam:org:id:${org}`;
}

export const config: WebConfig = parseConfig({
  NEXT_PUBLIC_QLAB_ENV: process.env.NEXT_PUBLIC_QLAB_ENV,
  NEXT_PUBLIC_OIDC_ISSUER: process.env.NEXT_PUBLIC_OIDC_ISSUER,
  NEXT_PUBLIC_OIDC_CLIENT_ID: process.env.NEXT_PUBLIC_OIDC_CLIENT_ID,
  NEXT_PUBLIC_OIDC_PROJECT_ID: process.env.NEXT_PUBLIC_OIDC_PROJECT_ID,
  NEXT_PUBLIC_OIDC_STAFF_ORG_ID: process.env.NEXT_PUBLIC_OIDC_STAFF_ORG_ID,
  NEXT_PUBLIC_OIDC_LEARNER_ORG_ID: process.env.NEXT_PUBLIC_OIDC_LEARNER_ORG_ID,
});

/** The page that signs a user in: the development page only when local. */
export function signInHref(cfg: WebConfig = config): string {
  return cfg.local ? "/dev/sign-in" : "/sign-in";
}
