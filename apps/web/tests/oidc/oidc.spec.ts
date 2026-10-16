// Slice 9 section 4: sign-in, invite and invite-admin screens against a mocked issuer and a mocked API.
// This server is a non-local build (NEXT_PUBLIC_QLAB_ENV=test), so the real sign-in path is used. All data is synthetic.
import { expect, test, type BrowserContext, type Page, type Route } from "@playwright/test";

const ISSUER = "https://issuer.example.test";
const CLIENT_ID = "client-123";
const USER_KEY = `oidc.user:${ISSUER}:${CLIENT_ID}`;
const CODE = "Zm9vYmFyYmF6cXV4MTIzNDU2Nzg5MGFiY2RlZmdoaWo";
const ACCOUNT = "acc_0" + "b".repeat(25);
const INVITE_ID = "inv_0" + "a".repeat(25);
const CORS = { "access-control-allow-origin": "*", "access-control-allow-headers": "*" };

type Role = "student" | "teacher" | "reviewer" | "content_admin" | "platform_admin";
type ApiReq = { method: string; path: string; body: unknown; auth: string | null };

function b64url(value: unknown): string {
  return Buffer.from(JSON.stringify(value)).toString("base64url");
}

function idToken(nonce: string | null): string {
  const now = Math.floor(Date.now() / 1000);
  return `${b64url({ alg: "none", typ: "JWT" })}.${b64url({ iss: ISSUER, aud: CLIENT_ID, sub: "user-1", iat: now, exp: now + 3600, nonce })}.sig`;
}

/** A signed-in user exactly as oidc-client-ts keeps it in sessionStorage. */
async function injectUser(page: Page, token = "access-token-0") {
  await page.addInitScript(
    ([key, value]) => {
      // The script runs on every navigation; inject once per tab so that a sign-out stays signed out.
      if (sessionStorage.getItem("test.injected")) return;
      sessionStorage.setItem("test.injected", "1");
      sessionStorage.setItem(key, value);
    },
    [
      USER_KEY,
      JSON.stringify({
        id_token: `${b64url({ alg: "none" })}.${b64url({ sub: "user-1" })}.sig`,
        access_token: token,
        refresh_token: "refresh-0",
        token_type: "Bearer",
        scope: "openid",
        profile: { sub: "user-1" },
        expires_at: Math.floor(Date.now() / 1000) + 3600,
      }),
    ] as const,
  );
}

interface Issuer {
  authorizeUrls: URL[];
  tokenBodies: URLSearchParams[];
  endSessions: URL[];
}

/** Discovery, authorize, token and end-session of the mocked issuer. `auto`: authorize answers with the redirect back. */
async function mockIssuer(page: Page, auto: boolean): Promise<Issuer> {
  const seen: Issuer = { authorizeUrls: [], tokenBodies: [], endSessions: [] };
  let nonce: string | null = null;
  await page.route(`${ISSUER}/**`, async (route: Route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname === "/.well-known/openid-configuration") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: CORS,
        body: JSON.stringify({
          issuer: ISSUER,
          authorization_endpoint: `${ISSUER}/oauth/v2/authorize`,
          token_endpoint: `${ISSUER}/oauth/v2/token`,
          end_session_endpoint: `${ISSUER}/oidc/v1/end_session`,
          jwks_uri: `${ISSUER}/oauth/v2/keys`,
          response_types_supported: ["code"],
          code_challenge_methods_supported: ["S256"],
        }),
      });
    }
    if (url.pathname === "/oauth/v2/authorize") {
      seen.authorizeUrls.push(url);
      nonce = url.searchParams.get("nonce");
      if (!auto) return route.fulfill({ status: 200, contentType: "text/html", body: "<p>issuer login</p>" });
      const back = new URL(url.searchParams.get("redirect_uri") ?? "");
      back.searchParams.set("code", "auth-code-1");
      back.searchParams.set("state", url.searchParams.get("state") ?? "");
      return route.fulfill({ status: 302, headers: { location: back.toString() } });
    }
    if (url.pathname === "/oauth/v2/token") {
      seen.tokenBodies.push(new URLSearchParams(request.postData() ?? ""));
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: CORS,
        body: JSON.stringify({
          access_token: "access-token-1",
          refresh_token: "refresh-1",
          id_token: idToken(nonce),
          token_type: "Bearer",
          expires_in: 3600,
          scope: "openid",
        }),
      });
    }
    if (url.pathname === "/oidc/v1/end_session") {
      seen.endSessions.push(url);
      const back = url.searchParams.get("post_logout_redirect_uri") ?? "/";
      return route.fulfill({ status: 302, headers: { location: back } });
    }
    return route.fulfill({ status: 404, body: "" });
  });
  return seen;
}

type Reply = { status?: number; json?: unknown; problem?: { status: number; code: string } };

async function mockApi(page: Page, roles: Role[] | { problem: { status: number; code: string } }, handler: (r: ApiReq) => Reply | undefined = () => undefined) {
  const log: ApiReq[] = [];
  await page.route("**/api/v1/**", async (route: Route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname.replace(/^.*\/api\/v1/, "");
    let body: unknown;
    try {
      body = request.postDataJSON();
    } catch {
      body = undefined;
    }
    const r: ApiReq = { method: request.method(), path, body, auth: request.headers()["authorization"] ?? null };
    log.push(r);
    let reply: Reply | undefined;
    if (path === "/me") reply = Array.isArray(roles) ? { json: { account_id: ACCOUNT, roles } } : roles;
    reply = reply ?? handler(r) ?? { problem: { status: 404, code: "not_found" } };
    if (reply.problem) {
      const p = reply.problem;
      return route.fulfill({
        status: p.status,
        contentType: "application/problem+json",
        body: JSON.stringify({ type: `about:blank#${p.code}`, title: p.code, status: p.status, code: p.code, detail: null, errors: [] }),
      });
    }
    return route.fulfill({ status: reply.status ?? 200, contentType: "application/json", body: JSON.stringify(reply.json ?? {}) });
  });
  return log;
}

function invite(over: Record<string, unknown> = {}) {
  return {
    id: INVITE_ID,
    role: "student",
    created_by: ACCOUNT,
    created_at: "2026-10-16T09:00:00Z",
    expires_at: "2099-10-23T09:00:00Z",
    max_uses: 1,
    uses: 0,
    revoked_at: null,
    ...over,
  };
}

function alerts(page: Page) {
  return page.locator('[role="alert"]:not(#__next-route-announcer__)');
}

async function noHorizontalScroll(page: Page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
}

test.describe("sign-in", () => {
  test("Sign in starts the code flow with PKCE, the scopes and the learners organisation", async ({ page }) => {
    const issuer = await mockIssuer(page, false);
    await mockApi(page, { problem: { status: 401, code: "unauthenticated" } });
    await page.goto("/sign-in");
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    await expect.poll(() => issuer.authorizeUrls.length).toBe(1);
    const q = issuer.authorizeUrls[0]!.searchParams;
    expect(q.get("response_type")).toBe("code");
    expect(q.get("client_id")).toBe(CLIENT_ID);
    expect(q.get("code_challenge_method")).toBe("S256");
    expect(q.get("code_challenge")).toMatch(/^[A-Za-z0-9_-]{43}$/);
    expect(q.get("state")).toBeTruthy();
    expect(q.get("redirect_uri")).toMatch(/\/auth\/callback$/);
    const scopes = (q.get("scope") ?? "").split(" ");
    expect(scopes).toEqual([
      "openid",
      "profile",
      "email",
      "offline_access",
      "urn:zitadel:iam:org:project:id:project-456:aud",
      "urn:zitadel:iam:user:resourceowner",
      "urn:zitadel:iam:org:id:org-learners",
    ]);
  });

  test("Staff sign-in uses the staff organisation scope", async ({ page }) => {
    const issuer = await mockIssuer(page, false);
    await mockApi(page, { problem: { status: 401, code: "unauthenticated" } });
    await page.goto("/sign-in");
    await page.getByRole("button", { name: "Staff sign-in" }).click();
    await expect.poll(() => issuer.authorizeUrls.length).toBe(1);
    const scopes = (issuer.authorizeUrls[0]!.searchParams.get("scope") ?? "").split(" ");
    expect(scopes).toContain("urn:zitadel:iam:org:id:org-staff");
    expect(scopes).not.toContain("urn:zitadel:iam:org:id:org-learners");
  });

  test("the callback exchanges the code, stores the user in sessionStorage and opens the home page", async ({ page }) => {
    const issuer = await mockIssuer(page, true);
    const log = await mockApi(page, ["teacher"]);
    await page.goto("/sign-in");
    // A click before hydration does nothing; retry until the handler is attached and the redirect starts.
    await expect(async () => {
      await page.getByRole("button", { name: "Sign in", exact: true }).click({ timeout: 1000 });
      await expect(page).toHaveURL(/\/$/, { timeout: 1500 });
    }).toPass({ timeout: 15_000 });
    await expect(page.getByRole("navigation", { name: "Account" }).getByText("Signed in: teacher")).toBeVisible();
    await expect(page.getByRole("button", { name: "Sign out" })).toBeVisible();
    expect(issuer.tokenBodies).toHaveLength(1);
    const t = issuer.tokenBodies[0]!;
    expect(t.get("grant_type")).toBe("authorization_code");
    expect(t.get("code")).toBe("auth-code-1");
    expect(t.get("code_verifier")).toBeTruthy();
    expect(await page.evaluate((k) => sessionStorage.getItem(k) !== null, USER_KEY)).toBe(true);
    expect(await page.evaluate((k) => localStorage.getItem(k), USER_KEY)).toBeNull();
    expect(log.some((r) => r.path === "/me" && r.auth === "Bearer access-token-1")).toBe(true);
  });

  test("Sign out ends the session at the issuer and clears the tab", async ({ page }) => {
    const issuer = await mockIssuer(page, false);
    await mockApi(page, ["teacher"]);
    await injectUser(page);
    await page.goto("/");
    await page.getByRole("button", { name: "Sign out" }).click();
    await expect.poll(() => issuer.endSessions.length).toBe(1);
    await expect(page.getByRole("navigation", { name: "Account" }).getByRole("link", { name: "Sign in", exact: true })).toBeVisible();
    expect(await page.evaluate((k) => sessionStorage.getItem(k), USER_KEY)).toBeNull();
    expect(await page.evaluate(() => sessionStorage.getItem("qlab.invite.code"))).toBeNull();
  });

  test("the development sign-in does not exist in this build", async ({ page }) => {
    const response = await page.goto("/dev/sign-in");
    expect(response?.status()).toBe(404);
    await expect(page.getByRole("heading", { name: "Development sign-in" })).toHaveCount(0);
  });
});

test.describe("invite page", () => {
  test("redeems the code and links to the home page for a student", async ({ page }) => {
    await mockIssuer(page, false);
    const log = await mockApi(page, ["student"], (r) => (r.path === "/invites/redeem" ? { json: { account_id: ACCOUNT, roles: ["student"] } } : undefined));
    await injectUser(page);
    await page.goto(`/invite/${CODE}`);
    await expect(page.getByText("You now have the student role")).toBeVisible();
    await expect(page.getByRole("link", { name: "Go to the home page" })).toHaveAttribute("href", "/");
    const redeem = log.filter((r) => r.path === "/invites/redeem");
    expect(redeem).toHaveLength(1);
    expect(redeem[0]!.body).toEqual({ code: CODE });
    expect(redeem[0]!.auth).toBe("Bearer access-token-0");
    expect(await page.evaluate(() => sessionStorage.getItem("qlab.invite.code"))).toBeNull();
  });

  test("a staff role links to the questions", async ({ page }) => {
    await mockIssuer(page, false);
    await mockApi(page, ["reviewer"], (r) => (r.path === "/invites/redeem" ? { json: { account_id: ACCOUNT, roles: ["reviewer"] } } : undefined));
    await injectUser(page);
    await page.goto(`/invite/${CODE}`);
    await expect(page.getByText("You now have the reviewer role")).toBeVisible();
    await expect(page.getByRole("link", { name: "Go to the questions" })).toHaveAttribute("href", "/admin/questions");
  });

  test("an unknown, expired, revoked or used-up code shows one message", async ({ page }) => {
    await mockIssuer(page, false);
    await mockApi(page, ["student"], (r) => (r.path === "/invites/redeem" ? { problem: { status: 404, code: "invite_not_found" } } : undefined));
    await injectUser(page);
    await page.goto(`/invite/${CODE}`);
    await expect(alerts(page)).toHaveText("This invite link is not valid. Ask for a new one.");
    expect(await page.evaluate(() => sessionStorage.getItem("qlab.invite.code"))).toBeNull();
  });

  test("without a session the code is kept, sign-in is offered and the user returns to the invite", async ({ page }) => {
    const issuer = await mockIssuer(page, true);
    const log = await mockApi(page, ["student"], (r) => (r.path === "/invites/redeem" ? { json: { account_id: ACCOUNT, roles: ["student"] } } : undefined));
    await page.goto(`/invite/${CODE}`);
    await expect(page.getByRole("button", { name: "Staff sign-in" })).toBeVisible();
    expect(await page.evaluate(() => sessionStorage.getItem("qlab.invite.code"))).toBe(CODE);
    expect(log.filter((r) => r.path === "/invites/redeem")).toHaveLength(0);
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`/invite/${CODE}$`));
    await expect(page.getByText("You now have the student role")).toBeVisible();
    expect(issuer.authorizeUrls).toHaveLength(1);
    expect(log.filter((r) => r.path === "/invites/redeem")).toHaveLength(1);
    expect(await page.evaluate(() => sessionStorage.getItem("qlab.invite.code"))).toBeNull();
  });
});

async function grantClipboard(context: BrowserContext) {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
}

test.describe("invite administration", () => {
  function adminApi(page: Page, roles: Role[], onCreate?: (body: unknown) => Reply) {
    const state = { items: [invite()] as Record<string, unknown>[] };
    const logP = mockApi(page, roles, (r) => {
      if (r.method === "GET" && r.path === "/admin/invites") return { json: { items: state.items, next_cursor: null } };
      if (r.method === "POST" && r.path === "/admin/invites") {
        if (onCreate) return onCreate(r.body);
        const b = r.body as { role: string; expires_in_days: number; max_uses: number };
        const created = invite({ id: "inv_0" + "c".repeat(25), role: b.role, max_uses: b.max_uses });
        state.items = [created, ...state.items];
        return { status: 201, json: { ...created, code: CODE } };
      }
      if (r.method === "POST" && r.path === `/admin/invites/${INVITE_ID}/revoke`) {
        state.items = state.items.map((i) => (i.id === INVITE_ID ? { ...i, revoked_at: "2026-10-16T10:00:00Z" } : i));
        return { json: state.items.find((i) => i.id === INVITE_ID) };
      }
      return undefined;
    });
    return logP;
  }

  test("a platform admin creates an invite, copies the link once, and revokes another", async ({ page, context }) => {
    await grantClipboard(context);
    await mockIssuer(page, false);
    const log = await adminApi(page, ["platform_admin"]);
    await injectUser(page);
    await page.goto("/admin/invites");
    await expect(page.getByRole("heading", { name: "Invites", exact: true, level: 1 })).toBeVisible();

    const options = await page.getByLabel("Role").locator("option").allTextContents();
    expect(options).toEqual(["Student", "Teacher", "Reviewer", "Content admin", "Platform admin"]);
    await expect(page.getByLabel("Expires in (days)")).toHaveValue("7");
    await expect(page.getByLabel("Uses")).toHaveValue("1");

    await page.getByLabel("Role").selectOption("teacher");
    await page.getByLabel("Expires in (days)").fill("3");
    await page.getByLabel("Uses").fill("5");
    await page.getByRole("button", { name: "Create invite" }).click();

    await expect.poll(() => log.some((r) => r.method === "POST" && r.path === "/admin/invites")).toBe(true);
    const post = log.find((r) => r.method === "POST" && r.path === "/admin/invites");
    expect(post?.body).toEqual({ role: "teacher", expires_in_days: 3, max_uses: 5 });
    const linkBox = page.getByRole("textbox", { name: "Invite link" });
    await expect(linkBox).toHaveValue(new RegExp(`/invite/${CODE}$`));
    await expect(page.getByText("will not be shown again")).toBeVisible();
    await page.getByRole("button", { name: "Copy link" }).click();
    await expect(page.getByText("Link copied.")).toBeVisible();
    const clip = await page.evaluate(() => navigator.clipboard.readText());
    expect(clip).toMatch(new RegExp(`/invite/${CODE}$`));

    // The list never carries a code; the new row is there.
    const table = page.getByRole("table", { name: "Invites" });
    await expect(table.getByRole("row")).toHaveCount(3);
    await expect(table.getByRole("row").nth(1)).toContainText("Teacher");
    await expect(table.getByRole("row").nth(1)).toContainText("0/5");

    // Revoke asks first.
    page.once("dialog", (d) => void d.dismiss());
    await table.getByRole("button", { name: /Revoke Student invite/ }).click();
    expect(log.filter((r) => r.path.endsWith("/revoke"))).toHaveLength(0);
    page.once("dialog", (d) => void d.accept());
    await table.getByRole("button", { name: /Revoke Student invite/ }).click();
    await expect.poll(() => log.filter((r) => r.path.endsWith("/revoke")).length).toBe(1);
    await expect(table.getByRole("row").nth(2)).toContainText("Revoked");
    await expect(table.getByRole("button", { name: /Revoke Student invite/ })).toHaveCount(0);
    await noHorizontalScroll(page);
  });

  test("a teacher can invite students only", async ({ page }) => {
    await mockIssuer(page, false);
    await adminApi(page, ["teacher"]);
    await injectUser(page);
    await page.goto("/admin/invites");
    await expect(page.getByRole("heading", { name: "Invites", exact: true, level: 1 })).toBeVisible();
    const options = await page.getByLabel("Role").locator("option").allTextContents();
    expect(options).toEqual(["Student"]);
  });

  test("a role without invite rights sees the notice and sends no invite request", async ({ page }) => {
    await mockIssuer(page, false);
    const log = await adminApi(page, ["student"]);
    await injectUser(page);
    await page.goto("/admin/invites");
    await expect(page.getByText("This area is for teachers and platform admins.")).toBeVisible();
    await page.waitForTimeout(300);
    expect(log.filter((r) => r.path.startsWith("/admin/"))).toEqual([]);
  });

  test("values outside the allowed ranges are not sent", async ({ page }) => {
    await mockIssuer(page, false);
    const log = await adminApi(page, ["teacher"]);
    await injectUser(page);
    await page.goto("/admin/invites");
    await expect(page.getByRole("heading", { name: "Invites", exact: true, level: 1 })).toBeVisible();
    await page.getByLabel("Expires in (days)").fill("31");
    await page.getByRole("button", { name: "Create invite" }).click();
    await expect(alerts(page)).toContainText("Expires in must be a whole number from 1 to 30.");
    await page.getByLabel("Expires in (days)").fill("7");
    await page.getByLabel("Uses").fill("201");
    await page.getByRole("button", { name: "Create invite" }).click();
    await expect(alerts(page)).toContainText("Uses must be a whole number from 1 to 200.");
    expect(log.filter((r) => r.method === "POST")).toHaveLength(0);
  });

  test("invite_role_forbidden shows the plain message", async ({ page }) => {
    await mockIssuer(page, false);
    await adminApi(page, ["teacher"], () => ({ problem: { status: 403, code: "invite_role_forbidden" } }));
    await injectUser(page);
    await page.goto("/admin/invites");
    await page.getByRole("button", { name: "Create invite" }).click();
    await expect(alerts(page)).toHaveText("You cannot invite someone to this role.");
  });

  test("mfa_required on a request shows the two-step message", async ({ page }) => {
    await mockIssuer(page, false);
    await adminApi(page, ["platform_admin"], () => ({ problem: { status: 403, code: "mfa_required" } }));
    await injectUser(page);
    await page.goto("/admin/invites");
    await page.getByRole("button", { name: "Create invite" }).click();
    await expect(alerts(page)).toHaveText("Staff access needs two-step verification. Sign out and use Staff sign-in.");
  });
});

test("mfa_required while checking the session shows the two-step message", async ({ page }) => {
  await mockIssuer(page, false);
  await mockApi(page, { problem: { status: 403, code: "mfa_required" } });
  await injectUser(page);
  await page.goto("/admin/questions");
  await expect(alerts(page)).toHaveText("Staff access needs two-step verification. Sign out and use Staff sign-in.");
  await expect(page.getByRole("button", { name: "Sign out" })).toBeVisible();
});

test("responses carry the security headers", async ({ request }) => {
  const response = await request.get("/sign-in");
  const h = response.headers();
  expect(h["referrer-policy"]).toBe("no-referrer");
  expect(h["x-content-type-options"]).toBe("nosniff");
  const csp = h["content-security-policy"] ?? "";
  expect(csp).toContain("default-src 'self'");
  expect(csp).toContain(`connect-src 'self' ${ISSUER}`);
  expect(csp).toContain("frame-ancestors 'none'");
  expect(csp).toContain(`form-action 'self' ${ISSUER}`);
});
