// Slice 7a section 4: staff review screens, end to end with the API mocked (page.route).
// All data is synthetic (the question document is the renderer package's invented sample set).
import { expect, test, type Page, type Route } from "@playwright/test";
import { fixtures } from "@qlab/question-renderer";
import type { components } from "@qlab/api-client";

type S = components["schemas"];
type Status = S["VersionStatus"];

const ME = "acc_0" + "b".repeat(25);
const OTHER = "acc_0" + "c".repeat(25);
const qid = (c: string) => "q_0" + c.repeat(25);
const vid = (c: string) => "qv_0" + c.repeat(25);
const SHA = "ab".repeat(32);
const SHA2 = "cd".repeat(32);

const staffFixture = fixtures.find((f) => f.id === "staff-answers-on");
if (!staffFixture || staffFixture.kind !== "staff_question") throw new Error("fixture staff-answers-on missing");
const DOCUMENT = staffFixture.data.document;

function firstText(node: unknown): string | undefined {
  if (!node || typeof node !== "object") return undefined;
  const o = node as Record<string, unknown>;
  if (typeof o.text === "string" && o.text.trim().length >= 12 && /^[A-Za-z ,.]+$/.test(o.text.trim())) return o.text.trim();
  for (const v of Object.values(o)) {
    const r = firstText(v);
    if (r) return r;
  }
  return undefined;
}
const STEM_TEXT = firstText(DOCUMENT.stem);

function version(over: Partial<S["AdminVersion"]> = {}): S["AdminVersion"] {
  return {
    id: vid("a"),
    question_id: qid("a"),
    version_no: 1,
    status: "in_review",
    content_sha256: SHA,
    question_class: DOCUMENT.question_class,
    exam_section: DOCUMENT.exam_section,
    levels: DOCUMENT.levels,
    total_marks: DOCUMENT.total_marks,
    syllabus: { program: "prog", subject: "subj", version: "v1" },
    has_unverified_visuals: false,
    created_by: OTHER,
    created_at: "2026-10-01T09:00:00Z",
    updated_at: "2026-10-02T09:00:00Z",
    document: DOCUMENT,
    checks: [
      { code: "marks_sum", severity: "critical", outcome: "passed", detail: {} },
      { code: "figure_alt_text", severity: "warning", outcome: "failed", detail: { note: "<b>xss-marker</b>" } },
      { code: "tolerance_declared", severity: "warning", outcome: "not_applicable", detail: {} },
    ],
    ...over,
  } as S["AdminVersion"];
}

function summary(v: S["AdminVersion"]): S["AdminVersionSummary"] {
  const { document: _d, checks: _c, ...rest } = v;
  void _d;
  void _c;
  return rest as S["AdminVersionSummary"];
}

function historyEntry(over: Partial<S["HistoryEntry"]>): S["HistoryEntry"] {
  return {
    occurred_at: "2026-10-02T09:00:00Z",
    actor: OTHER,
    action: "submitted",
    status: "in_review",
    previous_status: "draft",
    content_sha256: SHA,
    previous_content_sha256: null,
    reason: null,
    failed_checks: null,
    check: null,
    severity: null,
    outcome: null,
    based_on: null,
    superseded_by: null,
    source_ref: null,
    approver_is_last_editor: null,
    ...over,
  };
}

function summaryRow(i: number, over: Partial<S["AdminQuestionSummary"]> = {}): S["AdminQuestionSummary"] {
  const c = "abcdefghjkmnpqrstvwxyz0123456789"[i % 32] ?? "a";
  const v = version({ id: vid(c), question_id: qid(c), version_no: 1, status: "in_review" });
  return {
    id: qid(c),
    origin: "authored",
    source_ref: `syn-${String(i).padStart(3, "0")}`,
    created_at: "2026-10-01T09:00:00Z",
    latest_version: summary(v),
    published_version_id: null,
    working_version_id: v.id,
    ...over,
  };
}

type Req = { method: string; path: string; query: URLSearchParams; body: unknown };
type Reply = { status?: number; json?: unknown; problem?: { status: number; code: string; errors?: { code: string; message: string }[] }; delayMs?: number };

async function mockApi(page: Page, roles: S["Role"][] | null, handler: (r: Req) => Reply | undefined) {
  const log: Req[] = [];
  await page.route("**/api/v1/**", async (route: Route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname.replace(/^.*\/api\/v1/, "");
    let body: unknown = undefined;
    try {
      body = request.postDataJSON();
    } catch {
      body = request.postData() ?? undefined;
    }
    const req: Req = { method: request.method(), path, query: url.searchParams, body };
    log.push(req);
    let reply: Reply | undefined;
    if (path === "/me" && roles) reply = { json: { account_id: ME, roles } };
    else if (path === "/me") reply = { problem: { status: 401, code: "unauthenticated" } };
    reply = reply ?? handler(req) ?? { problem: { status: 404, code: "not_found" } };
    if (reply.delayMs) await new Promise((r) => setTimeout(r, reply.delayMs));
    if (reply.problem) {
      const p = reply.problem;
      await route.fulfill({
        status: p.status,
        contentType: "application/problem+json",
        body: JSON.stringify({ type: `about:blank#${p.code}`, title: p.code, status: p.status, code: p.code, detail: null, errors: p.errors ?? [] }),
      });
    } else {
      await route.fulfill({ status: reply.status ?? 200, contentType: "application/json", body: JSON.stringify(reply.json ?? {}) });
    }
  });
  return log;
}

// Signed in = the development token is in sessionStorage (key qlab.dev.token); GET /v1/me is mocked.
async function signIn(page: Page) {
  await page.addInitScript(() => sessionStorage.setItem("qlab.dev.token", "fake.dev.token"));
}

const adminRequests = (log: Req[]) => log.filter((r) => r.path.startsWith("/admin/"));

// A stateful mock of one version: decisions move it to the status the server would report.
function versionServer(initial: S["AdminVersion"], extra?: (r: Req) => Reply | undefined) {
  const state = { v: initial, history: [historyEntry({})] };
  const handler = (r: Req): Reply | undefined => {
    const base = `/admin/question-versions/${state.v.id}`;
    if (r.method === "GET" && r.path === base) return { json: state.v };
    if (r.method === "GET" && r.path === `${base}/history`) return { json: { items: state.history } };
    if (r.method === "GET" && r.path === `/admin/questions/${state.v.question_id}`)
      return { json: { id: state.v.question_id, origin: "authored", source_ref: "syn-001", created_by: OTHER, created_at: "2026-10-01T09:00:00Z", versions: [summary(state.v)] } };
    const m = r.method === "POST" && r.path.startsWith(base + "/") ? r.path.slice(base.length + 1) : undefined;
    const override = extra?.(r);
    if (override) return override;
    const next: Record<string, Status> = { submit: "in_review", approve: "approved", "request-changes": "needs_fix", reject: "rejected", publish: "published", withdraw: "withdrawn", republish: "published" };
    if (m && next[m]) {
      state.v = { ...state.v, status: next[m] };
      return { json: { id: state.v.id, question_id: state.v.question_id, version_no: state.v.version_no, status: state.v.status, content_sha256: state.v.content_sha256 } };
    }
    return undefined;
  };
  return { state, handler };
}

const statusRe = (s: string) => new RegExp(s.replace("_", "[ _]"), "i");
const REASON_WARNING = "Describe the content, not a person. Do not paste question text. Reasons are kept permanently.";

// Next's dev server adds its own empty role="alert" route announcer; only the app's alerts count.
function alerts(page: Page) {
  return page.locator('[role="alert"]:not(#__next-route-announcer__)');
}

test.describe("access", () => {
  test("a role without a staff role sends no admin request and sees the staff notice", async ({ page }) => {
    const log = await mockApi(page, ["student", "teacher"], () => undefined);
    await signIn(page);
    for (const path of ["/admin/questions", `/admin/questions/${qid("a")}`, `/admin/versions/${vid("a")}`]) {
      await page.goto(path);
      await expect(page.getByText("This area is for staff")).toBeVisible();
    }
    await page.waitForTimeout(500);
    expect(adminRequests(log)).toEqual([]);
  });

  test("without a sign-in the page links to /dev/sign-in and sends no admin request", async ({ page }) => {
    const log = await mockApi(page, null, () => undefined);
    await page.goto("/admin/questions");
    await expect(page.locator('a[href="/dev/sign-in"]').first()).toBeVisible();
    await page.waitForTimeout(500);
    expect(adminRequests(log)).toEqual([]);
  });

  test("a 401 from the API shows a sign-in link", async ({ page }) => {
    await mockApi(page, ["reviewer"], (r) => (r.path.startsWith("/admin/") ? { problem: { status: 401, code: "unauthenticated" } } : undefined));
    await signIn(page);
    await page.goto("/admin/questions");
    await expect(alerts(page).locator('a[href="/dev/sign-in"]')).toBeVisible();
  });
});

test.describe("question list", () => {
  test("shows rows linking to the question, with source key, status text and markers", async ({ page }) => {
    const row = summaryRow(1, { published_version_id: vid("z") });
    await mockApi(page, ["reviewer"], (r) => (r.path === "/admin/questions" ? { json: { items: [row], next_cursor: null } } : undefined));
    await signIn(page);
    await page.goto("/admin/questions");
    const link = page.locator(`a[href="/admin/questions/${row.id}"]`).first();
    await expect(link).toBeVisible();
    await expect(page.getByText("syn-001").first()).toBeVisible();
    await expect(page.getByRole("table").getByText(statusRe("in_review")).first()).toBeVisible(); // text, not colour alone
    await expect(page.getByRole("button", { name: "Load more" })).toHaveCount(0);
  });

  test("a server error is visible", async ({ page }) => {
    await mockApi(page, ["reviewer"], (r) => (r.path === "/admin/questions" ? { problem: { status: 500, code: "boom_test" } } : undefined));
    await signIn(page);
    await page.goto("/admin/questions");
    await expect(page.getByText("Something went wrong")).toBeVisible();
    await expect(page.getByText(/boom_test/)).toBeVisible();
  });

  test("filter values in the URL are passed as query parameters", async ({ page }) => {
    const log = await mockApi(page, ["reviewer"], (r) => (r.path === "/admin/questions" ? { json: { items: [], next_cursor: null } } : undefined));
    await signIn(page);
    await page.goto("/admin/questions?status=in_review&question_class=mcq&level=hl");
    await expect.poll(() => log.some((r) => r.path === "/admin/questions" && r.query.get("status") === "in_review" && r.query.get("question_class") === "mcq" && r.query.get("level") === "hl")).toBe(true);
  });

  test("choosing a status filter writes it to the URL and to the request; back restores the previous list", async ({ page }) => {
    const log = await mockApi(page, ["reviewer"], (r) => (r.path === "/admin/questions" ? { json: { items: [summaryRow(2)], next_cursor: null } } : undefined));
    await signIn(page);
    await page.goto("/admin/questions");
    await page.getByLabel(/status/i).first().selectOption({ value: "in_review" });
    await expect(page).toHaveURL(/status=in_review/);
    await expect.poll(() => log.some((r) => r.path === "/admin/questions" && r.query.get("status") === "in_review")).toBe(true);
    await page.goBack();
    await expect(page).not.toHaveURL(/status=in_review/);
    await expect(page.getByLabel(/status/i).first()).toHaveValue("");
  });

  test("Load more sends the cursor and appends the next page", async ({ page }) => {
    const first = Array.from({ length: 3 }, (_, i) => summaryRow(i + 10));
    const second = [summaryRow(20)];
    const log = await mockApi(page, ["reviewer"], (r) => {
      if (r.path !== "/admin/questions") return undefined;
      return r.query.get("cursor") === "cursor-1" ? { json: { items: second, next_cursor: null } } : { json: { items: first, next_cursor: "cursor-1" } };
    });
    await signIn(page);
    await page.goto("/admin/questions");
    await expect(page.getByText("syn-010")).toBeVisible();
    const firstReq = log.find((r) => r.path === "/admin/questions");
    expect([null, "50"]).toContain(firstReq?.query.get("limit") ?? null);
    expect(firstReq?.query.get("cursor")).toBeNull();
    await page.getByRole("button", { name: "Load more" }).click();
    await expect(page.getByText("syn-020")).toBeVisible();
    await expect(page.getByText("syn-010")).toBeVisible(); // appended, not replaced
    expect(log.some((r) => r.path === "/admin/questions" && r.query.get("cursor") === "cursor-1")).toBe(true);
    await expect(page.getByRole("button", { name: "Load more" })).toHaveCount(0);
  });
});

test.describe("question page", () => {
  const published = version({ id: vid("a"), status: "published", version_no: 1 });
  const questionBody = (versions: S["AdminVersion"][]) => ({
    id: qid("a"),
    origin: "authored",
    source_ref: "syn-001",
    created_by: OTHER,
    created_at: "2026-10-01T09:00:00Z",
    versions: versions.map(summary),
  });

  test("shows header and versions linking to version pages; Open revision creates one and navigates to it", async ({ page }) => {
    const created = version({ id: vid("b"), status: "draft", version_no: 2 });
    const log = await mockApi(page, ["reviewer"], (r) => {
      if (r.method === "GET" && r.path === `/admin/questions/${qid("a")}`) return { json: questionBody([published]) };
      if (r.method === "POST" && r.path === `/admin/questions/${qid("a")}/revisions`) return { status: 201, json: created };
      if (r.method === "GET" && r.path === `/admin/question-versions/${created.id}`) return { json: created };
      if (r.method === "GET" && r.path === `/admin/question-versions/${created.id}/history`) return { json: { items: [] } };
      return undefined;
    });
    await signIn(page);
    await page.goto(`/admin/questions/${qid("a")}`);
    await expect(page.getByText("syn-001").first()).toBeVisible();
    await expect(page.locator(`a[href="/admin/versions/${published.id}"]`).first()).toBeVisible();
    await expect(page.getByText(SHA.slice(0, 8)).first()).toBeVisible();
    await page.getByRole("button", { name: "Open revision" }).click();
    await expect(page).toHaveURL(new RegExp(`/admin/versions/${created.id}$`));
    expect(log.filter((r) => r.method === "POST" && r.path.endsWith("/revisions"))).toHaveLength(1);
  });

  test("Open revision is hidden when a version is already being worked on", async ({ page }) => {
    const working = version({ id: vid("b"), status: "draft", version_no: 2 });
    await mockApi(page, ["reviewer"], (r) => (r.path === `/admin/questions/${qid("a")}` ? { json: questionBody([published, working]) } : undefined));
    await signIn(page);
    await page.goto(`/admin/questions/${qid("a")}`);
    await expect(page.locator(`a[href="/admin/versions/${working.id}"]`).first()).toBeVisible();
    await expect(page.getByRole("button", { name: "Open revision" })).toHaveCount(0);
  });

  test("working_version_exists (409) shows the message and a link to the question page", async ({ page }) => {
    await mockApi(page, ["reviewer"], (r) => {
      if (r.method === "GET" && r.path === `/admin/questions/${qid("a")}`) return { json: questionBody([published]) };
      if (r.method === "POST" && r.path.endsWith("/revisions")) return { problem: { status: 409, code: "working_version_exists" } };
      return undefined;
    });
    await signIn(page);
    await page.goto(`/admin/questions/${qid("a")}`);
    await page.getByRole("button", { name: "Open revision" }).click();
    const alert = alerts(page);
    await expect(alert).toContainText("A version is already being worked on");
    await expect(alert.locator(`a[href="/admin/questions/${qid("a")}"]`)).toBeVisible();
  });

  test("Open revision is absent while the question request is pending and when it fails", async ({ page }) => {
    const qpath = `/admin/questions/${qid("a")}`;
    await mockApi(page, ["reviewer"], (r) => (r.path === qpath ? { delayMs: 3000, json: questionBody([published]) } : undefined));
    await signIn(page);
    await page.goto(qpath);
    await page.waitForTimeout(800);
    await expect(page.getByRole("button", { name: "Open revision" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Open revision" })).toBeVisible({ timeout: 10000 });
  });

  test("Open revision is absent when the question request fails", async ({ page }) => {
    await mockApi(page, ["reviewer"], (r) => (r.path === `/admin/questions/${qid("a")}` ? { problem: { status: 500, code: "boom_test" } } : undefined));
    await signIn(page);
    await page.goto(`/admin/questions/${qid("a")}`);
    await expect(alerts(page)).toContainText("boom_test");
    await expect(page.getByRole("button", { name: "Open revision" })).toHaveCount(0);
  });
});

test.describe("version page", () => {
  test("shows content, checks and history", async ({ page }) => {
    const v = version({ has_unverified_visuals: true });
    const server = versionServer(v);
    server.state.history = [
      historyEntry({ action: "submitted", actor: OTHER, status: "in_review", previous_status: "draft" }),
      historyEntry({ action: "approved", actor: ME, status: "approved", previous_status: "in_review", occurred_at: "2026-10-03T09:00:00Z", reason: "Marks reconcile with the scheme", approver_is_last_editor: false }),
      historyEntry({ action: "publish_refused", actor: OTHER, status: "approved", previous_status: "approved", occurred_at: "2026-10-04T09:00:00Z", failed_checks: ["figure_alt_text"] }),
    ];
    await mockApi(page, ["reviewer"], server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    // header
    await expect(page.locator(`a[href="/admin/questions/${v.question_id}"]`).first()).toBeVisible();
    await expect(page.getByText(SHA.slice(0, 12)).first()).toBeVisible();
    await expect(page.getByText(statusRe("in_review")).first()).toBeVisible();
    // content comes from the rendering component
    if (STEM_TEXT) await expect(page.getByText(STEM_TEXT, { exact: false }).first()).toBeVisible();
    await expect(page.locator(".katex").first()).toBeVisible();
    // checks
    for (const code of ["marks_sum", "figure_alt_text", "tolerance_declared"]) await expect(page.getByText(code).first()).toBeVisible();
    await expect(page.getByText(/critical/i).first()).toBeVisible();
    await expect(page.getByText(/warning/i).first()).toBeVisible();
    await expect(page.getByText(/passed/i).first()).toBeVisible();
    await expect(page.getByText(/failed/i).first()).toBeVisible();
    await expect(page.getByText(/not[ _]applicable/i).first()).toBeVisible();
    // check detail is text, never HTML
    await expect(page.locator("b", { hasText: "xss-marker" })).toHaveCount(0);
    // figures note
    await expect(page.getByText("Has figures without verified images: can be approved, cannot be published (D-49)")).toBeVisible();
    // history: own entries show "you", others show the opaque id, reason and failed checks visible
    await expect(page.getByText("you", { exact: true }).first()).toBeVisible();
    await expect(page.getByText(OTHER).first()).toBeVisible();
    await expect(page.getByText("Marks reconcile with the scheme")).toBeVisible();
    await expect(page.getByText("submitted").first()).toBeVisible();
    await expect(page.getByText("approved").first()).toBeVisible();
    const entries = page.getByRole("listitem").or(page.getByRole("row")).filter({ hasText: /submitted|approved|publish.refused/i });
    const texts = await entries.allTextContents();
    // How an action name is displayed (raw or humanised) is not specified.
    const at = (w: string) => texts.findIndex((t) => new RegExp(w.replace("_", "."), "i").test(t));
    expect(at("submitted")).toBeGreaterThanOrEqual(0);
    expect(at("submitted")).toBeLessThan(at("Marks reconcile with the scheme")); // oldest first
    expect(at("Marks reconcile with the scheme")).toBeLessThan(at("publish_refused"));
  });

  test("with no checks it says so; the figures note is absent", async ({ page }) => {
    const v = version({ checks: [], has_unverified_visuals: false });
    await mockApi(page, ["reviewer"], versionServer(v).handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    await expect(page.getByText("No checks recorded for this content")).toBeVisible();
    await expect(page.getByText(/cannot be published \(D-49\)/)).toHaveCount(0);
  });

  test("Show answers is on by default and can be switched off", async ({ page }) => {
    const v = version();
    await mockApi(page, ["reviewer"], versionServer(v).handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    const toggle = page.getByLabel("Show answers");
    await expect(toggle).toBeChecked();
    await toggle.click();
    await expect(toggle).not.toBeChecked();
  });

  test("a missing version shows the not found message", async ({ page }) => {
    await mockApi(page, ["reviewer"], () => undefined);
    await signIn(page);
    await page.goto(`/admin/versions/${vid("a")}`);
    await expect(page.getByText("Not found or not visible to you")).toBeVisible();
  });
});

test.describe("decisions", () => {
  test("Approve sends exactly the displayed content digest, locks while pending, then shows the new state", async ({ page }) => {
    const v = version({ status: "in_review", content_sha256: SHA2 });
    const server = versionServer(v, (r) => (r.path.endsWith("/approve") ? undefined : undefined));
    const inner = server.handler;
    const log = await mockApi(page, ["content_admin"], (r) => (r.method === "POST" && r.path.endsWith("/approve") ? { ...inner(r), delayMs: 400 } : inner(r)));
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    const approve = page.getByRole("button", { name: "Approve" });
    await approve.dblclick();
    await expect(page.getByRole("button", { name: "Publish" })).toBeVisible(); // approved, content_admin
    const posts = log.filter((r) => r.method === "POST" && r.path.endsWith("/approve"));
    expect(posts).toHaveLength(1);
    expect(posts[0]?.body).toEqual({ expected_content_sha256: SHA2 });
    await expect(page.getByText(statusRe("approved")).first()).toBeVisible();
    // queries were invalidated: the version was fetched again after the decision
    const approveIdx = log.findIndex((r) => r.path.endsWith("/approve"));
    expect(log.slice(approveIdx).some((r) => r.method === "GET" && r.path === `/admin/question-versions/${v.id}`)).toBe(true);
    expect(log.slice(approveIdx).some((r) => r.method === "GET" && r.path === `/admin/question-versions/${v.id}/history`)).toBe(true);
  });

  test("409 stale_content shows the reload message and a Reload button that refetches", async ({ page }) => {
    const v = version({ status: "in_review" });
    const server = versionServer(v, (r) => (r.path.endsWith("/approve") ? { problem: { status: 409, code: "stale_content" } } : undefined));
    const log = await mockApi(page, ["reviewer"], server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    await page.getByRole("button", { name: "Approve" }).click();
    await expect(page.getByText("This version changed since you opened it. Reload to see the current content.")).toBeVisible();
    const before = log.filter((r) => r.method === "GET" && r.path === `/admin/question-versions/${v.id}`).length;
    // the content changed on the server meanwhile
    server.state.v = { ...server.state.v, content_sha256: SHA2 };
    await page.getByRole("button", { name: "Reload" }).click();
    await expect.poll(() => log.filter((r) => r.method === "GET" && r.path === `/admin/question-versions/${v.id}`).length).toBeGreaterThan(before);
    await expect(page.getByText("This version changed since you opened it.")).toHaveCount(0);
    // the next approval carries the new digest
    await page.getByRole("button", { name: "Approve" }).click();
    const posts = log.filter((r) => r.method === "POST" && r.path.endsWith("/approve"));
    expect(posts.at(-1)?.body).toEqual({ expected_content_sha256: SHA2 });
  });

  test("Publish 409 not_publishable lists the reasons", async ({ page }) => {
    const v = version({ status: "approved" });
    const server = versionServer(v, (r) =>
      r.path.endsWith("/publish")
        ? {
            problem: {
              status: 409,
              code: "not_publishable",
              errors: [
                { code: "critical_checks_failed", message: "m" },
                { code: "unverified_visuals", message: "m" },
                { code: "rights_denied", message: "m" },
              ],
            },
          }
        : undefined,
    );
    const log = await mockApi(page, ["content_admin"], server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    await page.getByRole("button", { name: "Publish" }).click();
    await expect(page.getByText("A required check has not passed")).toBeVisible();
    await expect(page.getByText("Figures are not verified yet")).toBeVisible();
    await expect(page.getByText("Rights do not permit display")).toBeVisible();
    expect(await page.getByRole("listitem").filter({ hasText: /A required check has not passed|Figures are not verified yet|Rights do not permit display/ }).count()).toBeGreaterThanOrEqual(3);
    expect(log.find((r) => r.path.endsWith("/publish"))?.body).toEqual({ expected_content_sha256: SHA });
  });

  test("self_approval_forbidden and invalid_transition show their messages", async ({ page }) => {
    const v = version({ status: "in_review" });
    let code = "self_approval_forbidden";
    const server = versionServer(v, (r) => (r.path.endsWith("/approve") ? { problem: { status: code === "self_approval_forbidden" ? 403 : 409, code } } : undefined));
    await mockApi(page, ["reviewer"], server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    await page.getByRole("button", { name: "Approve" }).click();
    await expect(page.getByText("You edited this version last, so someone else must approve it")).toBeVisible();
    code = "invalid_transition";
    await page.getByRole("button", { name: "Approve" }).click();
    await expect(page.getByText("This action is not possible in the current state")).toBeVisible();
  });

  test("a reviewer does not see Publish, Withdraw or Republish; a content_admin does", async ({ page }) => {
    const approved = version({ status: "approved" });
    await mockApi(page, ["reviewer"], versionServer(approved).handler);
    await signIn(page);
    await page.goto(`/admin/versions/${approved.id}`);
    await expect(page.getByRole("button", { name: "Request changes" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Publish" })).toHaveCount(0);
    for (const n of ["Withdraw", "Republish"]) await expect(page.getByRole("button", { name: n })).toHaveCount(0);
  });

  test("needs_fix shows no decision buttons and offers the Edit to fix link", async ({ page }) => {
    const v = version({ status: "needs_fix" });
    await mockApi(page, ["platform_admin"], versionServer(v).handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    await expect(page.getByText("Waiting for changes")).toHaveCount(0);
    await expect(page.getByRole("link", { name: "Edit to fix" })).toHaveAttribute("href", `/admin/versions/${v.id}/edit`);
    for (const n of ["Submit for review", "Approve", "Request changes", "Reject", "Publish", "Withdraw", "Republish", "Open revision"])
      await expect(page.getByRole("button", { name: n })).toHaveCount(0);
  });

  test("draft: Submit for review posts to /submit", async ({ page }) => {
    const v = version({ status: "draft" });
    const log = await mockApi(page, ["reviewer"], versionServer(v).handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    await page.getByRole("button", { name: "Submit for review" }).click();
    await expect.poll(() => log.some((r) => r.method === "POST" && r.path === `/admin/question-versions/${v.id}/submit`)).toBe(true);
  });

  test("published: Withdraw sends a trimmed reason; withdrawn: Republish sends digest and reason", async ({ page }) => {
    const v = version({ status: "published" });
    const server = versionServer(v);
    const log = await mockApi(page, ["content_admin"], server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    await page.getByRole("textbox", { name: /reason/i }).fill("  Units are inconsistent  ");
    await page.getByRole("button", { name: "Withdraw" }).click();
    await expect.poll(() => log.some((r) => r.path.endsWith("/withdraw"))).toBe(true);
    expect(log.find((r) => r.path.endsWith("/withdraw"))?.body).toEqual({ reason: "Units are inconsistent" });
    await expect(page.getByRole("button", { name: "Republish" })).toBeVisible();
    await page.getByRole("textbox", { name: /reason/i }).fill("Corrected the units");
    await page.getByRole("button", { name: "Republish" }).click();
    await expect.poll(() => log.some((r) => r.path.endsWith("/republish"))).toBe(true);
    expect(log.find((r) => r.path.endsWith("/republish"))?.body).toEqual({ expected_content_sha256: SHA, reason: "Corrected the units" });
  });
});

test.describe("reasons", () => {
  async function open(page: Page, status: Status = "in_review") {
    const v = version({ status });
    const log = await mockApi(page, ["reviewer"], versionServer(v).handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    return { v, log };
  }

  test("the reason warning is visible next to the reason field", async ({ page }) => {
    await open(page);
    await expect(page.getByText(REASON_WARNING)).toBeVisible();
    await expect(page.getByRole("textbox", { name: /reason/i })).toBeVisible();
  });

  test("an empty or whitespace-only reason cannot be sent", async ({ page }) => {
    const { log } = await open(page);
    const box = page.getByRole("textbox", { name: /reason/i });
    for (const text of ["", "   "]) {
      await box.fill(text);
      await page.getByRole("button", { name: "Request changes" }).click({ force: true, timeout: 2000 }).catch(() => undefined);
      await page.waitForTimeout(300);
      expect(log.filter((r) => r.method === "POST" && r.path.endsWith("/request-changes"))).toHaveLength(0);
    }
    await box.fill("Distractor B is also correct");
    await page.getByRole("button", { name: "Request changes" }).click();
    await expect.poll(() => log.some((r) => r.path.endsWith("/request-changes"))).toBe(true);
    expect(log.find((r) => r.path.endsWith("/request-changes"))?.body).toEqual({ reason: "Distractor B is also correct" });
  });

  test("a reason longer than 500 characters never reaches the API in full", async ({ page }) => {
    const { log } = await open(page);
    await page.getByRole("textbox", { name: /reason/i }).fill("x".repeat(501));
    await page.getByRole("button", { name: "Request changes" }).click({ force: true, timeout: 2000 }).catch(() => undefined);
    await page.waitForTimeout(400);
    for (const r of log.filter((q) => q.method === "POST" && q.path.endsWith("/request-changes"))) {
      expect(((r.body as { reason: string }).reason ?? "").length).toBeLessThanOrEqual(500);
    }
  });

  test("a reason of exactly 500 characters is accepted", async ({ page }) => {
    const { log } = await open(page);
    await page.getByRole("textbox", { name: /reason/i }).fill("y".repeat(500));
    await page.getByRole("button", { name: "Request changes" }).click();
    await expect.poll(() => log.some((r) => r.path.endsWith("/request-changes"))).toBe(true);
    expect((log.find((r) => r.path.endsWith("/request-changes"))?.body as { reason: string }).reason).toHaveLength(500);
  });

  test("Reject asks for confirmation in an ARIA dialog ('cannot be undone'), sends the reason after it, and focuses the status heading", async ({ page }) => {
    const { v, log } = await open(page);
    let native = 0;
    page.on("dialog", async (d) => {
      native++;
      await d.dismiss();
    });
    await page.getByRole("textbox", { name: /reason/i }).fill("Stem is ambiguous");
    await page.getByRole("button", { name: "Reject" }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await expect(dialog).toContainText("cannot be undone");
    expect(log.some((r) => r.path.endsWith("/reject"))).toBe(false);
    await dialog.getByRole("button", { name: /confirm|reject|yes/i }).last().click();
    await expect.poll(() => log.some((r) => r.path.endsWith("/reject"))).toBe(true);
    expect(log.find((r) => r.path.endsWith("/reject"))?.body).toEqual({ reason: "Stem is ambiguous" });
    expect(native).toBe(0);
    await expect(page.getByRole("dialog")).toHaveCount(0);
    // focus moves to the version's status heading
    await expect.poll(() => page.evaluate(() => document.activeElement?.tagName ?? "")).toMatch(/^H[1-6]$/);
    await expect(page.locator(":focus")).toContainText(/rejected/i);
    void v;
  });

  test("Cancelling the Reject dialog sends nothing", async ({ page }) => {
    const { log } = await open(page);
    await page.getByRole("textbox", { name: /reason/i }).fill("Stem is ambiguous");
    await page.getByRole("button", { name: "Reject" }).click();
    await page.getByRole("dialog").getByRole("button", { name: /cancel|close|no/i }).first().click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await page.waitForTimeout(300);
    expect(log.some((r) => r.path.endsWith("/reject"))).toBe(false);
  });

  test("the reason field has maxLength 500", async ({ page }) => {
    await open(page);
    await expect(page.getByRole("textbox", { name: /reason/i })).toHaveAttribute("maxlength", "500");
  });

  test("the reason field exists only where an action needs a reason", async ({ page }) => {
    const reasonBox = () => page.getByRole("textbox", { name: /reason/i });
    // draft: only Submit -> no reason field
    const draft = version({ status: "draft" });
    await mockApi(page, ["reviewer"], versionServer(draft).handler);
    await signIn(page);
    await page.goto(`/admin/versions/${draft.id}`);
    await expect(page.getByRole("button", { name: "Submit for review" })).toBeVisible();
    await expect(reasonBox()).toHaveCount(0);
    await expect(page.getByText(REASON_WARNING)).toHaveCount(0);
  });

  test("approved: a reviewer has Request changes so the field shows; published: a reviewer has no reason action so it does not", async ({ page }) => {
    const approved = version({ status: "approved" });
    await mockApi(page, ["reviewer"], versionServer(approved).handler);
    await signIn(page);
    await page.goto(`/admin/versions/${approved.id}`);
    await expect(page.getByRole("textbox", { name: /reason/i })).toBeVisible();
    await page.unrouteAll({ behavior: "ignoreErrors" });
    const published = version({ id: vid("d"), status: "published" });
    await mockApi(page, ["reviewer"], versionServer(published).handler);
    await page.goto(`/admin/versions/${published.id}`);
    await expect(page.getByRole("button", { name: "Withdraw" })).toHaveCount(0);
    await expect(page.getByRole("textbox", { name: /reason/i })).toHaveCount(0);
  });
});

test.describe("pinned content", () => {
  const DOC_B = {
    ...DOCUMENT,
    stem: { type: "doc", content: [{ type: "paragraph", content: [{ type: "text", text: "Replacement stem for the changed synthetic version." }] }] },
  } as unknown as S["QuestionDocument"];

  async function openPinned(page: Page, roles: S["Role"][] = ["reviewer"]) {
    const v = version({ status: "in_review", content_sha256: SHA });
    const server = versionServer(v);
    const log = await mockApi(page, roles, server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    await expect(page.getByRole("button", { name: "Approve" })).toBeEnabled();
    return { v, server, log };
  }
  const refetch = async (page: Page) => {
    await page.context().setOffline(true);
    await page.context().setOffline(false);
    await page.evaluate(() => window.dispatchEvent(new Event("online")));
    await page.evaluate(() => document.dispatchEvent(new Event("visibilitychange")));
  };
  const NOTICE = "This version changed since you opened it. Reload to see the current content.";

  test("a later read with another digest does not change the screen; it warns and locks decisions until Reload", async ({ page }) => {
    const { v, server, log } = await openPinned(page);
    if (STEM_TEXT) await expect(page.getByText(STEM_TEXT, { exact: false }).first()).toBeVisible();
    server.state.v = { ...v, content_sha256: SHA2, document: DOC_B };
    await refetch(page);
    await expect(page.getByText(NOTICE)).toBeVisible();
    // still content A
    if (STEM_TEXT) await expect(page.getByText(STEM_TEXT, { exact: false }).first()).toBeVisible();
    await expect(page.getByText("Replacement stem for the changed synthetic version.")).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Approve" })).toBeDisabled();
    await page.getByRole("button", { name: "Reload" }).click();
    await expect(page.getByText("Replacement stem for the changed synthetic version.")).toBeVisible();
    await expect(page.getByText(NOTICE)).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Approve" })).toBeEnabled();
    await page.getByRole("button", { name: "Approve" }).click();
    await expect.poll(() => log.some((r) => r.path.endsWith("/approve"))).toBe(true);
    expect(log.find((r) => r.path.endsWith("/approve"))?.body).toEqual({ expected_content_sha256: SHA2 });
  });

  test("no notice after the user's own successful approve or submit", async ({ page }) => {
    const { server, log } = await openPinned(page, ["content_admin"]);
    await page.getByRole("button", { name: "Approve" }).click();
    await expect(page.getByRole("button", { name: "Publish" })).toBeVisible();
    await refetch(page);
    await page.waitForTimeout(500);
    await expect(page.getByText(NOTICE)).toHaveCount(0);
    expect(log.filter((r) => r.path.endsWith("/approve"))).toHaveLength(1);
    void server;
  });

  test("no notice after the user's own successful submit", async ({ page }) => {
    const v = version({ status: "draft" });
    await mockApi(page, ["reviewer"], versionServer(v).handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    await page.getByRole("button", { name: "Submit for review" }).click();
    await expect(page.getByRole("button", { name: "Approve" })).toBeVisible();
    await refetch(page);
    await page.waitForTimeout(500);
    await expect(page.getByText(NOTICE)).toHaveCount(0);
  });
});

test.describe("filters", () => {
  test("an invalid exam section shows an inline message and sends no list request", async ({ page }) => {
    const log = await mockApi(page, ["reviewer"], (r) => (r.path === "/admin/questions" ? { json: { items: [], next_cursor: null } } : undefined));
    await signIn(page);
    await page.goto("/admin/questions");
    await expect.poll(() => log.filter((r) => r.path === "/admin/questions").length).toBeGreaterThan(0);
    const before = log.filter((r) => r.path === "/admin/questions").length;
    const box = page.getByLabel(/exam section/i);
    await box.fill("bad value!");
    await box.press("Enter");
    await page.waitForTimeout(600);
    await expect(page.getByText(/invalid|not valid|letters|only/i).first()).toBeVisible();
    expect(log.filter((r) => r.path === "/admin/questions" && (r.query.get("exam_section") ?? "").includes("bad")).length).toBe(0);
    expect(log.filter((r) => r.path === "/admin/questions").length).toBe(before);
  });
});

test.describe("narrow screens", () => {
  test.use({ viewport: { width: 375, height: 800 } });

  async function noHorizontalScroll(page: Page) {
    const [scrollWidth, width] = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
    expect(scrollWidth).toBeLessThanOrEqual(width);
  }

  test("the version page does not scroll horizontally at 375 px", async ({ page }) => {
    const v = version({ status: "approved", has_unverified_visuals: true });
    const server = versionServer(v);
    server.state.history = [historyEntry({ reason: "r".repeat(120), failed_checks: ["figure_alt_text", "marks_sum"], actor: OTHER })];
    await mockApi(page, ["content_admin"], server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${v.id}`);
    await expect(page.getByText("marks_sum").first()).toBeVisible();
    await noHorizontalScroll(page);
  });

  test("the list page does not scroll horizontally at 375 px", async ({ page }) => {
    const items = Array.from({ length: 5 }, (_, i) => summaryRow(i + 1, { published_version_id: vid("z") }));
    await mockApi(page, ["reviewer"], (r) => (r.path === "/admin/questions" ? { json: { items, next_cursor: "c" } } : undefined));
    await signIn(page);
    await page.goto("/admin/questions");
    await expect(page.getByText("syn-001")).toBeVisible();
    await noHorizontalScroll(page);
  });

  test("the question page does not scroll horizontally at 375 px", async ({ page }) => {
    const versions = [version({ id: vid("a"), status: "published" }), version({ id: vid("b"), status: "draft", version_no: 2 })];
    await mockApi(page, ["reviewer"], (r) => (r.path === `/admin/questions/${qid("a")}` ? { json: { id: qid("a"), origin: "authored", source_ref: "syn-001", created_by: OTHER, created_at: "2026-10-01T09:00:00Z", versions: versions.map(summary) } } : undefined));
    await signIn(page);
    await page.goto(`/admin/questions/${qid("a")}`);
    await expect(page.getByText("syn-001").first()).toBeVisible();
    await noHorizontalScroll(page);
  });
});
