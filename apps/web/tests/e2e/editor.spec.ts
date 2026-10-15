// Slice 7b section 5, items 3-9: the edit page end to end with the API mocked (page.route).
// Written from docs/slices/M1G-7B-EDITOR.md (sections 4 and 5) and the frozen contract
// (PUT /v1/admin/question-versions/{version_id}: {document, expected_content_sha256}). All data is synthetic.
//
// Accessible names agreed with the implementer: fields "Stem", "Part (a) body", "Mark point N", "Explanation";
// buttons "Save", "Preview", "Edit", "Add mark point", "Remove mark point N", "Move mark point N up".
import { expect, test, type Locator, type Page, type Route } from "@playwright/test";

type Json = Record<string, unknown>;
type Role = "student" | "teacher" | "reviewer" | "content_admin" | "platform_admin";

const ME = "acc_0" + "b".repeat(25);
const OTHER = "acc_0" + "c".repeat(25);
const QID = "q_0" + "a".repeat(25);
const VID = "qv_0" + "a".repeat(25);
const SHA = "ab".repeat(32);
const SHA2 = "cd".repeat(32);
const SHA3 = "ef".repeat(32);

// ---------------------------------------------------------------- synthetic question document
const text = (t: string) => ({ marks: [], type: "text", text: t });
const math = (latex: string) => ({ marks: [], type: "math_inline", attrs: { latex } });
const doc = (...inline: unknown[]) => ({ type: "doc", content: [{ type: "paragraph", content: inline }] });

function mark(id: string, t: string): Json {
  return { id, content: doc(text(t)), kind: "statement", alternative_group: null, route: null, accept_range: null, solution_step: null };
}

function part(id: string, bodyText: string, marks: number, points: Json[]): Json {
  return {
    id,
    label: id,
    lead_in: null,
    body: doc(text(bodyText), math("x^2")),
    marks,
    marks_capped: false,
    show_that: false,
    command_term: "state",
    answer_type: "word_phrase",
    assessment_objective: null,
    level_content: "sl_core",
    syllabus_node: "A.1",
    stimulus_refs: [],
    depends_on: [],
    ecf_from: [],
    mark_points: points,
    notes: [],
  };
}

function makeDocument(): Json {
  return {
    schema_version: "1.0",
    question_class: "short_structured",
    exam_section: "paper_2",
    levels: ["sl", "hl"],
    language: "en",
    calculator: true,
    difficulty: "medium",
    primary_syllabus_node: "A.1",
    secondary_syllabus_nodes: [],
    outcome: "Invented outcome for the editor tests",
    stem: doc(text("A synthetic trolley moves along a track.")),
    stimuli: [],
    mcq: null,
    parts: [
      part("a", "State the quantity ", 2, [mark("a-m1", "alpha point"), mark("a-m2", "beta point"), mark("a-m3", "gamma point")]),
      part("b", "Explain the quantity ", 1, [mark("b-m1", "omega point")]),
    ],
    total_marks: 3,
    solution_model: null,
  };
}

const clone = <T,>(v: T): T => JSON.parse(JSON.stringify(v)) as T;

// All text nodes of a node, concatenated.
function plain(node: unknown): string {
  if (!node || typeof node !== "object") return "";
  const o = node as Json;
  if (typeof o.text === "string") return o.text;
  return Object.values(o).map(plain).join("");
}
const partsOf = (d: Json) => d.parts as Json[];
const pointTexts = (d: Json, partIndex: number) => (partsOf(d)[partIndex]!.mark_points as Json[]).map((m) => plain(m.content));

// ---------------------------------------------------------------- API mock (same approach as admin.spec.ts)
type Req = { method: string; path: string; body: unknown };
type Reply = { status?: number; json?: unknown; problem?: { status: number; code: string; detail?: string | null; errors?: { code: string; message: string; location?: string | null }[] }; delayMs?: number };

async function mockApi(page: Page, roles: Role[] | null, handler: (r: Req) => Reply | undefined) {
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
    const req: Req = { method: request.method(), path, body };
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
        body: JSON.stringify({ type: `about:blank#${p.code}`, title: p.code, status: p.status, code: p.code, detail: p.detail ?? null, errors: p.errors ?? [] }),
      });
    } else {
      await route.fulfill({ status: reply.status ?? 200, contentType: "application/json", body: JSON.stringify(reply.json ?? {}) });
    }
  });
  return log;
}

async function signIn(page: Page) {
  await page.addInitScript(() => sessionStorage.setItem("qlab.dev.token", "fake.dev.token"));
}

function adminVersion(over: Json = {}): Json {
  const document = (over.document as Json | undefined) ?? makeDocument();
  return {
    id: VID,
    question_id: QID,
    version_no: 1,
    status: "draft",
    content_sha256: SHA,
    question_class: document.question_class,
    exam_section: document.exam_section,
    levels: document.levels,
    total_marks: document.total_marks,
    has_unverified_visuals: false,
    created_by: OTHER,
    created_at: "2026-10-01T09:00:00Z",
    updated_at: "2026-10-02T09:00:00Z",
    checks: [],
    ...over,
    document,
  };
}

function summaryOf(v: Json): Json {
  const { document: _d, checks: _c, ...rest } = v;
  void _d;
  void _c;
  return rest;
}

type PutReaction = (body: { document: Json; expected_content_sha256: string }, state: { v: Json }, n: number) => Reply;

// A stateful one-version server. By default a PUT stores the document under a fresh digest (SHA2, SHA3, ...).
function versionServer(initial: Json, onPut?: PutReaction) {
  const state = { v: initial, puts: 0 };
  const digests = [SHA2, SHA3, "12".repeat(32), "34".repeat(32)];
  const handler = (r: Req): Reply | undefined => {
    const base = `/admin/question-versions/${VID}`;
    if (r.method === "GET" && r.path === base) return { json: state.v };
    if (r.method === "GET" && r.path === `${base}/history`) return { json: { items: [] } };
    if (r.method === "GET" && r.path === `/admin/questions/${QID}`)
      return { json: { id: QID, origin: "authored", source_ref: "syn-001", created_by: OTHER, created_at: "2026-10-01T09:00:00Z", versions: [summaryOf(state.v)] } };
    if (r.method === "PUT" && r.path === base) {
      const body = r.body as { document: Json; expected_content_sha256: string };
      const n = state.puts++;
      if (onPut) return onPut(body, state, n);
      const doc2 = body.document;
      state.v = { ...state.v, status: "draft", content_sha256: digests[n] ?? SHA3, document: doc2, total_marks: doc2.total_marks };
      return { json: state.v };
    }
    return undefined;
  };
  return { state, handler };
}

const puts = (log: Req[]) => log.filter((r) => r.method === "PUT");
const putBody = (r: Req | undefined) => r?.body as { document: Json; expected_content_sha256: string };

// ---------------------------------------------------------------- locators
const field = (page: Page, name: string): Locator => page.getByRole("textbox", { name, exact: true }).first();
const save = (page: Page) => page.getByRole("button", { name: "Save", exact: true });

async function typeAtEnd(page: Page, name: string, value: string) {
  const box = field(page, name);
  await box.click();
  await page.keyboard.press("ControlOrMeta+End");
  await page.keyboard.type(value);
}

async function openEditor(page: Page, v: Json, roles: Role[] = ["reviewer"], onPut?: PutReaction) {
  const server = versionServer(v, onPut);
  const log = await mockApi(page, roles, server.handler);
  await signIn(page);
  await page.goto(`/admin/versions/${VID}/edit`);
  await expect(field(page, "Stem")).toBeVisible();
  return { server, log };
}

// ================================================================ item 3: the hash the page loaded with, re-pinned after a save
test.describe("save", () => {
  test("a text change is sent with the document and the digest the page loaded with; Saved is announced", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    await typeAtEnd(page, "Stem", " Edited.");
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(1);

    const req = puts(log)[0]!;
    expect(req.path).toBe(`/admin/question-versions/${VID}`);
    const body = putBody(req);
    expect(Object.keys(body).sort()).toEqual(["document", "expected_content_sha256"]);
    expect(body.expected_content_sha256).toBe(SHA);

    // exactly the stem changed (round-trip rule: untouched content is byte-identical)
    const expected = makeDocument();
    expected.stem = doc(text("A synthetic trolley moves along a track. Edited."));
    expect(body.document).toEqual(expected);

    await expect(page.locator("[aria-live]", { hasText: "Saved" }).first()).toBeAttached();
    await expect(page.getByText("Saved").first()).toBeVisible();
  });

  test("a second save sends the digest returned by the first", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    await typeAtEnd(page, "Stem", " One.");
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(1);
    await expect(page.getByText("Saved").first()).toBeVisible();

    await typeAtEnd(page, "Stem", " Two.");
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(2);
    expect(putBody(puts(log)[0]).expected_content_sha256).toBe(SHA);
    expect(putBody(puts(log)[1]).expected_content_sha256).toBe(SHA2);
    expect(plain(putBody(puts(log)[1]).document.stem)).toBe("A synthetic trolley moves along a track. One. Two.");
  });

  test("the Save button is locked while the request is in flight (one request only)", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion(), ["reviewer"], (body, state) => {
      state.v = { ...state.v, content_sha256: SHA2, document: body.document };
      return { json: state.v, delayMs: 600 };
    });
    await typeAtEnd(page, "Stem", " Slow.");
    await save(page).dblclick();
    await expect(save(page)).toBeDisabled();
    await expect.poll(() => puts(log).length).toBe(1);
    await page.waitForTimeout(800);
    expect(puts(log)).toHaveLength(1);
  });

  test("Preview shows the current, unsaved document in the exam layout", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    await typeAtEnd(page, "Stem", " Preview marker.");
    await page.getByRole("tab", { name: "Preview" }).or(page.getByRole("button", { name: "Preview", exact: true })).first().click();
    // the editor may stay in the DOM (hidden) behind the tab, so look only at visible nodes
    await expect(page.getByText("A synthetic trolley moves along a track. Preview marker.").locator("visible=true").first()).toBeVisible();
    await expect(page.locator(".katex").locator("visible=true").first()).toBeVisible();
    expect(puts(log)).toHaveLength(0); // previewing never saves
  });
});

// ================================================================ item 4: 409 stale_content
test.describe("stale content", () => {
  const MESSAGE = "Someone else saved this version while you were editing. Your changes are still here; copy what you need, then reload.";

  test("keeps the user's edits on screen, shows the message and the Reload button; Reload discards them", async ({ page }) => {
    const { server, log } = await openEditor(page, adminVersion(), ["reviewer"], () => ({ problem: { status: 409, code: "stale_content" } }));
    await typeAtEnd(page, "Stem", " My unsaved words.");
    await save(page).click();

    await expect(page.getByText(MESSAGE)).toBeVisible();
    const reload = page.getByRole("button", { name: "Reload (discards your changes)" });
    await expect(reload).toBeVisible();
    // nothing the user typed is lost
    await expect(field(page, "Stem")).toContainText("A synthetic trolley moves along a track. My unsaved words.");

    // the stored content changed meanwhile; Reload refetches it and drops the local edits
    const newer = makeDocument();
    newer.stem = doc(text("Stem written by somebody else."));
    server.state.v = adminVersion({ content_sha256: SHA2, document: newer });
    const before = log.filter((r) => r.method === "GET" && r.path === `/admin/question-versions/${VID}`).length;
    await reload.click();
    await expect.poll(() => log.filter((r) => r.method === "GET" && r.path === `/admin/question-versions/${VID}`).length).toBeGreaterThan(before);
    await expect(field(page, "Stem")).toContainText("Stem written by somebody else.");
    await expect(field(page, "Stem")).not.toContainText("My unsaved words.");
    await expect(page.getByText(MESSAGE)).toHaveCount(0);

    // the next save carries the reloaded digest
    server.state.v = adminVersion({ content_sha256: SHA2, document: newer });
    await typeAtEnd(page, "Stem", " After reload.");
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(2);
    expect(putBody(puts(log)[1]).expected_content_sha256).toBe(SHA2);
  });
});

// ================================================================ item 5: 422 invalid_document
test.describe("invalid document", () => {
  const PROBLEMS = [
    { code: "math_not_renderable", message: "This formula does not render: \\frac{1}{", location: "parts.0.mark_points.1.content" },
    { code: "unknown_label", message: "This label is not in the dictionary: zzqx", location: "stem" },
  ];

  test("every server problem is listed in a summary and next to a field; nothing the user typed is lost", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion(), ["reviewer"], () => ({
      problem: { status: 422, code: "invalid_document", detail: PROBLEMS.map((p) => p.location).join("\n"), errors: PROBLEMS },
    }));
    await typeAtEnd(page, "Stem", " Keep me.");
    await typeAtEnd(page, "Mark point 2", " and me");
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(1);

    for (const p of PROBLEMS) {
      // once in the summary and at least once beside its field
      await expect(page.getByText(p.message, { exact: false }).first()).toBeVisible();
      expect(await page.getByText(p.message, { exact: false }).count()).toBeGreaterThanOrEqual(2);
    }
    // the summary is an alert/region that takes focus
    const summary = page.locator('[role="alert"]:not(#__next-route-announcer__)').filter({ hasText: PROBLEMS[0]!.message });
    await expect(summary.first()).toBeVisible();
    await expect.poll(() => summary.first().evaluate((el) => el.contains(document.activeElement))).toBe(true);

    await expect(field(page, "Stem")).toContainText("Keep me.");
    await expect(field(page, "Mark point 2")).toContainText("beta point and me");
  });

  test("invalid_transition says the version can no longer be edited and links to the version", async ({ page }) => {
    await openEditor(page, adminVersion(), ["reviewer"], () => ({ problem: { status: 409, code: "invalid_transition" } }));
    await typeAtEnd(page, "Stem", " x");
    await save(page).click();
    await expect(page.getByText("This version can no longer be edited")).toBeVisible();
    await expect(page.locator(`a[href="/admin/versions/${VID}"]`).first()).toBeVisible();
  });
});

// ================================================================ item 6: Turkish letters block the request
test.describe("English-only content", () => {
  test("a Turkish-only letter stops the save before any request and names the problem", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    await typeAtEnd(page, "Stem", " ış");
    await save(page).click();
    await expect(page.getByText("Content must be written in English").first()).toBeVisible();
    await page.waitForTimeout(600);
    expect(puts(log)).toHaveLength(0);
    // the text is still there so the user can fix it
    await expect(field(page, "Stem")).toContainText("ış");
  });

  test("fixing the text lets the save through", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    await typeAtEnd(page, "Stem", "ğ");
    await save(page).click();
    await expect(page.getByText("Content must be written in English").first()).toBeVisible();
    expect(puts(log)).toHaveLength(0);
    await field(page, "Stem").click(); // focus moved to the Save button; return to the text
    await page.keyboard.press("ControlOrMeta+End");
    await page.keyboard.press("Backspace");
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(1);
  });
});

// ================================================================ item 7: mark points and part marks
test.describe("mark points and part marks", () => {
  // Everything except part (a)'s mark points and marks must reach the server untouched.
  function expectOnlyPartAChanged(sent: Json) {
    const orig = makeDocument();
    expect(sent.stem).toEqual(orig.stem);
    expect(partsOf(sent)[1]).toEqual(partsOf(orig)[1]);
    expect({ ...partsOf(sent)[0], mark_points: null, marks: null }).toEqual({ ...partsOf(orig)[0], mark_points: null, marks: null });
  }

  async function saveAndGet(page: Page, log: Req[]) {
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(1);
    return putBody(puts(log)[0]);
  }

  test("removing mark point 2 drops exactly that point", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    await page.getByRole("button", { name: "Remove mark point 2" }).first().click();
    const body = await saveAndGet(page, log);
    expect(pointTexts(body.document, 0)).toEqual(["alpha point", "gamma point"]);
    expect(pointTexts(body.document, 1)).toEqual(["omega point"]);
    expectOnlyPartAChanged(body.document);
    expect(body.document.total_marks).toBe(3);
  });

  test("moving mark point 2 up swaps it with point 1", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    await page.getByRole("button", { name: "Move mark point 2 up" }).first().click();
    const body = await saveAndGet(page, log);
    expect(pointTexts(body.document, 0)).toEqual(["beta point", "alpha point", "gamma point"]);
    expectOnlyPartAChanged(body.document);
  });

  test("adding a mark point appends a new, filled point with its own unique id", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    await page.getByRole("button", { name: "Add mark point" }).first().click();
    const added = field(page, "Mark point 4");
    await added.click();
    await page.keyboard.type("delta point");
    const body = await saveAndGet(page, log);
    expect(pointTexts(body.document, 0)).toEqual(["alpha point", "beta point", "gamma point", "delta point"]);
    expectOnlyPartAChanged(body.document);
    const ids = partsOf(body.document).flatMap((p) => (p.mark_points as Json[]).map((m) => m.id));
    expect(ids.every((i) => typeof i === "string" && i.length > 0)).toBe(true);
    expect(new Set(ids).size).toBe(ids.length);
    const fresh = (partsOf(body.document)[0]!.mark_points as Json[])[3]!;
    expect(fresh.kind).toBe("statement");
  });

  test("changing a part's marks recomputes total_marks from the parts", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    // Control name is not part of the agreed list; "Part (a) marks" is assumed (number input or select).
    const marks = page.getByLabel("Part (a) marks", { exact: true });
    const tag = await marks.evaluate((el) => el.tagName);
    if (tag === "SELECT") await marks.selectOption("3");
    else await marks.fill("3");
    const body = await saveAndGet(page, log);
    expect(partsOf(body.document)[0]!.marks).toBe(3);
    expect(partsOf(body.document)[1]!.marks).toBe(1);
    expect(body.document.total_marks).toBe(4);
    expect(pointTexts(body.document, 0)).toEqual(["alpha point", "beta point", "gamma point"]);
  });
});

// ================================================================ items 8 and 9: who may edit what
test.describe("access and status", () => {
  test("a published version shows no Edit control; opening /edit says it can no longer be edited and sends no PUT", async ({ page }) => {
    const v = adminVersion({ status: "published" });
    const server = versionServer(v);
    const log = await mockApi(page, ["content_admin"], server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${VID}`);
    await expect(page.getByText("published").first()).toBeVisible();
    await expect(page.getByRole("button", { name: "Edit", exact: true })).toHaveCount(0);
    await expect(page.getByRole("link", { name: "Edit", exact: true })).toHaveCount(0);

    await page.goto(`/admin/versions/${VID}/edit`);
    await expect(page.getByText("This version can no longer be edited")).toBeVisible();
    await expect(save(page)).toHaveCount(0);
    expect(puts(log)).toHaveLength(0);
  });

  test("a draft shows Edit to staff and it leads to the edit page", async ({ page }) => {
    const server = versionServer(adminVersion({ status: "draft" }));
    await mockApi(page, ["reviewer"], server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${VID}`);
    await page.getByRole("button", { name: "Edit", exact: true }).or(page.getByRole("link", { name: "Edit", exact: true })).first().click();
    await expect(page).toHaveURL(new RegExp(`/admin/versions/${VID}/edit$`));
    await expect(field(page, "Stem")).toBeVisible();
  });

  test("a needs_fix version offers Edit to fix instead of Waiting for changes", async ({ page }) => {
    const server = versionServer(adminVersion({ status: "needs_fix" }));
    await mockApi(page, ["reviewer"], server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${VID}`);
    await expect(page.getByRole("link", { name: "Edit to fix" }).first()).toBeVisible();
    await expect(page.getByText("Waiting for changes")).toHaveCount(0);
  });

  test("a learner role sees the staff notice on the edit page and no admin request is sent", async ({ page }) => {
    const server = versionServer(adminVersion());
    const log = await mockApi(page, ["student"], server.handler);
    await signIn(page);
    await page.goto(`/admin/versions/${VID}/edit`);
    await expect(page.getByText("This area is for staff")).toBeVisible();
    await expect(page.getByRole("textbox", { name: "Stem" })).toHaveCount(0);
    await page.waitForTimeout(500);
    expect(log.filter((r) => r.path.startsWith("/admin/"))).toEqual([]);
  });

  test("an unauthenticated visitor gets a sign-in link and no admin request", async ({ page }) => {
    const log = await mockApi(page, null, () => undefined);
    await page.goto(`/admin/versions/${VID}/edit`);
    await expect(page.locator('a[href="/dev/sign-in"]').first()).toBeVisible();
    await page.waitForTimeout(500);
    expect(log.filter((r) => r.path.startsWith("/admin/"))).toEqual([]);
  });
});

// keep the unused-helper linter quiet when a case above is removed
void clone;
