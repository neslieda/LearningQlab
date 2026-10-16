import { describe, expect, it } from "vitest";
import { baseScopes, parseConfig, scopesFor, signInHref } from "@/lib/config";
import { selectTokenSource } from "@/lib/token-source";

const FULL = {
  NEXT_PUBLIC_QLAB_ENV: "staging",
  NEXT_PUBLIC_OIDC_ISSUER: "https://issuer.example.test",
  NEXT_PUBLIC_OIDC_CLIENT_ID: "client-1",
  NEXT_PUBLIC_OIDC_PROJECT_ID: "project-1",
  NEXT_PUBLIC_OIDC_STAFF_ORG_ID: "org-staff",
  NEXT_PUBLIC_OIDC_LEARNER_ORG_ID: "org-learn",
};

describe("parseConfig", () => {
  it("parses a complete environment", () => {
    const c = parseConfig(FULL);
    expect(c.local).toBe(false);
    expect(c.env).toBe("staging");
    expect(c.oidc).toEqual({
      issuer: "https://issuer.example.test",
      clientId: "client-1",
      projectId: "project-1",
      staffOrgId: "org-staff",
      learnerOrgId: "org-learn",
    });
  });

  it("is local only for the exact value local", () => {
    expect(parseConfig({ NEXT_PUBLIC_QLAB_ENV: "local" }).local).toBe(true);
    expect(parseConfig({ NEXT_PUBLIC_QLAB_ENV: " local " }).local).toBe(true);
    expect(parseConfig({ NEXT_PUBLIC_QLAB_ENV: "Local" }).local).toBe(false);
    expect(parseConfig({}).local).toBe(false);
    expect(parseConfig({ NEXT_PUBLIC_QLAB_ENV: "production" }).local).toBe(false);
  });

  it("has no OIDC settings when any variable is missing", () => {
    for (const key of Object.keys(FULL).filter((k) => k !== "NEXT_PUBLIC_QLAB_ENV")) {
      expect(parseConfig({ ...FULL, [key]: "" }).oidc).toBeNull();
      expect(parseConfig({ ...FULL, [key]: undefined }).oidc).toBeNull();
    }
  });

  it("rejects a non-https issuer except on localhost, and malformed ids", () => {
    expect(parseConfig({ ...FULL, NEXT_PUBLIC_OIDC_ISSUER: "http://issuer.example.test" }).oidc).toBeNull();
    expect(parseConfig({ ...FULL, NEXT_PUBLIC_OIDC_ISSUER: "not a url" }).oidc).toBeNull();
    expect(parseConfig({ ...FULL, NEXT_PUBLIC_OIDC_ISSUER: "http://localhost:8080" }).oidc).not.toBeNull();
    expect(parseConfig({ ...FULL, NEXT_PUBLIC_OIDC_PROJECT_ID: "a b" }).oidc).toBeNull();
  });
});

describe("scopes", () => {
  const oidc = parseConfig(FULL).oidc!;
  it("base scopes are exactly those of the slice", () => {
    expect(baseScopes("p1").split(" ")).toEqual([
      "openid",
      "profile",
      "email",
      "offline_access",
      "urn:zitadel:iam:org:project:id:p1:aud",
      "urn:zitadel:iam:user:resourceowner",
    ]);
  });
  it("adds the organisation scope per sign-in kind", () => {
    expect(scopesFor(oidc, "learner").endsWith(" urn:zitadel:iam:org:id:org-learn")).toBe(true);
    expect(scopesFor(oidc, "staff").endsWith(" urn:zitadel:iam:org:id:org-staff")).toBe(true);
    expect(scopesFor(oidc, "staff")).not.toContain("org-learn");
  });
});

describe("token source", () => {
  const oidc = parseConfig(FULL).oidc;
  it("uses the development token only when local", () => {
    expect(selectTokenSource({ local: true, oidc })).toBe("dev");
    expect(selectTokenSource({ local: true, oidc: null })).toBe("dev");
  });
  it("uses the OIDC access token otherwise", () => {
    expect(selectTokenSource({ local: false, oidc })).toBe("oidc");
  });
  it("has no source when not local and not configured", () => {
    expect(selectTokenSource({ local: false, oidc: null })).toBe("none");
  });
  it("the sign-in page depends on the environment", () => {
    expect(signInHref(parseConfig({ NEXT_PUBLIC_QLAB_ENV: "local" }))).toBe("/dev/sign-in");
    expect(signInHref(parseConfig(FULL))).toBe("/sign-in");
  });
});
