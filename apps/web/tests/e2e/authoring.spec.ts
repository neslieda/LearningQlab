// Slice 7c section 3, acceptance 4-7: new question, part add/remove/move, error locations, syllabus vocabulary.
// Written from docs/slices/M1G-7C-YAZIM.md (sections 2 and 3) and the frozen contract in apps/api/openapi.json
// (AdminVersion.syllabus, ProblemItem.location, POST /v1/admin/questions -> 201 AdminVersion, 409 own_content_rights_unavailable).
// The API is mocked with page.route. All data is synthetic.
//
// Accessible names taken from the specification: "New question", "Question type", "Exam section", "Levels" (SL/HL),
// "Syllabus node", "Difficulty", "Calculator", "Outcome", "Option kind", "Option layout", "Create", "Add part",
// "Remove part (b)", "Move part (b) up", "Mark point N", "Part (a) body". Anything else is located loosely and noted in the report.
import { expect, test, type Locator, type Page, type Route } from "@playwright/test";

type Json = Record<string, unknown>;
type Role = "student" | "teacher" | "reviewer" | "content_admin" | "platform_admin";

const ME = "acc_0" + "b".repeat(25);
const OTHER = "acc_0" + "c".repeat(25);
const QID = "q_0" + "a".repeat(25);
const VID = "qv_0" + "a".repeat(25);
const NEW_QID = "q_0" + "d".repeat(25);
const NEW_VID = "qv_0" + "d".repeat(25);
const SHA = "ab".repeat(32);
const SHA2 = "cd".repeat(32);

// The program, subject and syllabus version the mock serves. Deliberately unlike anything a developer would hard-code.
const PROGRAM = "prog_zz";
const SUBJECT = "subj_zz";
const SYL_VERSION = "v7";

// ---------------------------------------------------------------- synthetic question document
const text = (t: string) => ({ marks: [], type: "text", text: t });
const math = (latex: string) => ({ marks: [], type: "math_inline", attrs: { latex } });
const doc = (...inline: unknown[]) => ({ type: "doc", content: [{ type: "paragraph", content: inline }] });

function mark(id: string, t: string): Json {
  return { id, content: doc(text(t)), kind: "statement", alternative_group: null, route: null, accept_range: null, solution_step: null };
}

function part(id: string, bodyText: string, marks: number, points: Json[], over: Json = {}): Json {
  return {
    id,
    label: id,
    lead_in: null,
    body: doc(text(bodyText), math("x^2")),
    marks,
    marks_capped: false,
    show_that: false,
    command_term: "alpha_term",
    answer_type: "word_phrase",
    assessment_objective: null,
    level_content: "sl_core",
    syllabus_node: "N.1",
    stimulus_refs: [],
    depends_on: [],
    ecf_from: [],
    mark_points: points,
    notes: [],
    ...over,
  };
}

function makeDocument(parts: Json[]): Json {
  return {
    schema_version: "1.0",
    question_class: "short_structured",
    exam_section: "sec_two",
    levels: ["sl", "hl"],
    language: "en",
    calculator: true,
    difficulty: "medium",
    primary_syllabus_node: "N.1",
    secondary_syllabus_nodes: [],
    outcome: "Invented outcome for the authoring tests",
    stem: doc(text("A synthetic cart moves along a synthetic rail.")),
    stimuli: [],
    mcq: null,
    parts,
    total_marks: parts.reduce((s, p) => s + (p.marks as number), 0),
    solution_model: null,
  };
}

const twoParts = () => [
  part("a", "State the quantity ", 2, [mark("a-m1", "alpha point"), mark("a-m2", "beta point"), mark("a-m3", "gamma point")]),
  part("b", "Explain the quantity ", 1, [mark("b-m1", "omega point")]),
];

// a (2), b (1, depends on a), c (1, depends on b, ecf from a and b)
const threeParts = () => [
  part("a", "State the quantity ", 2, [mark("a-m1", "alpha point")]),
  part("b", "Explain the quantity ", 1, [mark("b-m1", "omega point")], { depends_on: ["a"] }),
  part("c", "Find the quantity ", 1, [mark("c-m1", "sigma point")], { depends_on: ["b"], ecf_from: ["a", "b"] }),
];

const partsOf = (d: Json) => d.parts as Json[];
const ids = (d: Json) => partsOf(d).map((p) => p.id);
const labels = (d: Json) => partsOf(d).map((p) => p.label);

// ---------------------------------------------------------------- syllabus mock
type SyllabusSpec = { program: string; subject: string; version: string; commandTerms: string[] };

function syllabusJson(s: SyllabusSpec): Json {
  return {
    program: s.program,
    subject: s.subject,
    version: s.version,
    title: "Synthetic syllabus",
    command_terms: s.commandTerms,
    exam_sections: [
      { code: "sec_one", title: "Section one" },
      { code: "sec_two", title: "Section two" },
    ],
    nodes: [
      { code: "N", title: "Synthetic topic", parent: null, is_leaf: false, attributes: {} },
      { code: "N.1", title: "Synthetic leaf one", parent: "N", is_leaf: true, attributes: {} },
      { code: "N.2", title: "Synthetic leaf two", parent: "N", is_leaf: true, attributes: {} },
    ],
  };
}

const DEFAULT_SYLLABUS: SyllabusSpec = { program: PROGRAM, subject: SUBJECT, version: SYL_VERSION, commandTerms: ["alpha_term", "beta_term"] };

// ---------------------------------------------------------------- API mock (same approach as editor.spec.ts)
type Req = { method: string; path: string; query: URLSearchParams; body: unknown };
type Reply = {
  status?: number;
  json?: unknown;
  problem?: { status: number; code: string; detail?: string | null; errors?: { code: string; message: string; location?: string | null }[] };
  delayMs?: number;
};

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

function adminVersion(over: Json = {}, vid = VID, qid = QID): Json {
  const document = (over.document as Json | undefined) ?? makeDocument(twoParts());
  return {
    id: vid,
    question_id: qid,
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
    syllabus: { program: PROGRAM, subject: SUBJECT, version: SYL_VERSION },
    checks: [],
    ...over,
    document,
  };
}

function summaryOf(v: Json): Json {
  const { document: _d, checks: _c, syllabus: _s, ...rest } = v;
  void _d;
  void _c;
  void _s;
  return rest;
}

type PutReaction = (body: { document: Json; expected_content_sha256: string }, state: { v: Json }, n: number) => Reply;

// A stateful one-version server for the edit page, plus the syllabus endpoint(s).
function versionServer(initial: Json, syllabi: SyllabusSpec[] = [DEFAULT_SYLLABUS], onPut?: PutReaction) {
  const state = { v: initial, puts: 0 };
  const vid = initial.id as string;
  const qid = initial.question_id as string;
  const handler = (r: Req): Reply | undefined => {
    const base = `/admin/question-versions/${vid}`;
    if (r.method === "GET" && r.path === base) return { json: state.v };
    if (r.method === "GET" && r.path === `${base}/history`) return { json: { items: [] } };
    if (r.method === "GET" && r.path === `/admin/questions/${qid}`)
      return { json: { id: qid, origin: "authored", source_ref: null, created_by: OTHER, created_at: "2026-10-01T09:00:00Z", versions: [summaryOf(state.v)] } };
    if (r.method === "PUT" && r.path === base) {
      const body = r.body as { document: Json; expected_content_sha256: string };
      const n = state.puts++;
      if (onPut) return onPut(body, state, n);
      state.v = { ...state.v, status: "draft", content_sha256: SHA2, document: body.document, total_marks: body.document.total_marks };
      return { json: state.v };
    }
    const m = /^\/programs\/([^/]+)\/subjects\/([^/]+)\/syllabus$/.exec(r.path);
    if (r.method === "GET" && m) {
      const hit = syllabi.find((s) => s.program === m[1] && s.subject === m[2] && s.version === r.query.get("version"));
      return hit ? { json: syllabusJson(hit) } : undefined;
    }
    return undefined;
  };
  return { state, handler };
}

const puts = (log: Req[]) => log.filter((r) => r.method === "PUT");
const posts = (log: Req[]) => log.filter((r) => r.method === "POST" && r.path === "/admin/questions");
const putBody = (r: Req | undefined) => r?.body as { document: Json; expected_content_sha256: string };

// ---------------------------------------------------------------- locators
const field = (page: Page, name: string): Locator => page.getByRole("textbox", { name, exact: true }).first();
const button = (page: Page, name: string): Locator => page.getByRole("button", { name, exact: true });
const save = (page: Page) => button(page, "Save");
const norm = (s: string) => s.toLowerCase().replace(/[_\s]+/g, " ").trim();

async function typeAtEnd(page: Page, name: string, value: string) {
  const box = field(page, name);
  await box.click();
  await page.keyboard.press("ControlOrMeta+End");
  await page.keyboard.type(value);
}

async function openEditor(page: Page, v: Json, roles: Role[] = ["reviewer"], syllabi?: SyllabusSpec[], onPut?: PutReaction) {
  const server = versionServer(v, syllabi, onPut);
  const log = await mockApi(page, roles, server.handler);
  await signIn(page);
  await page.goto(`/admin/versions/${v.id as string}/edit`);
  await expect(field(page, "Stem")).toBeVisible();
  return { server, log };
}

// Sets a labelled header control whatever its widget: select, checkbox, text input or searchable list.
async function setControl(page: Page, label: string, want: string) {
  const ctl = page.getByLabel(label, { exact: true }).first();
  await expect(ctl).toBeVisible();
  const tag = await ctl.evaluate((el) => el.tagName);
  const type = await ctl.evaluate((el) => (el as HTMLInputElement).type ?? "");
  if (tag === "SELECT") {
    const opts = await ctl.evaluate((el) => Array.from((el as HTMLSelectElement).options).map((o) => ({ v: o.value, t: o.text })));
    const hit = opts.find((o) => norm(o.v) === norm(want) || norm(o.t) === norm(want)) ?? opts.find((o) => norm(o.t).includes(norm(want)) || norm(o.v).includes(norm(want)));
    expect(hit, `option "${want}" in "${label}" (have ${JSON.stringify(opts)})`).toBeTruthy();
    await ctl.selectOption(hit!.v);
  } else if (type === "checkbox") {
    if (["true", "yes", "on"].includes(norm(want))) await ctl.check();
    else await ctl.uncheck();
  } else {
    await ctl.fill(want);
    const option = page.getByRole("option", { name: new RegExp(want.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")) }).first();
    if (await option.isVisible().catch(() => false)) await option.click();
  }
}

async function fillRichText(page: Page) {
  const boxes = page.locator('[contenteditable="true"]');
  const n = await boxes.count();
  for (let i = 0; i < n; i++) {
    const box = boxes.nth(i);
    if (!(await box.isVisible())) continue;
    await box.click();
    await page.keyboard.press("ControlOrMeta+End");
    await page.keyboard.type(`Synthetic words ${i}`);
  }
}

// ---------------------------------------------------------------- new-question mock
// GET /v1/programs (listPrograms): one row per program/subject, versions newest first.
let extraSubject = false;
function programItems(): Json[] {
  const row = (subject: string, name: string) => ({
    program: PROGRAM,
    program_name: "Synthetic program",
    subject,
    subject_name: name,
    versions: [
      { code: SYL_VERSION, title: "Newest synthetic syllabus" },
      { code: "v6", title: "Older synthetic syllabus" },
    ],
  });
  return extraSubject ? [row(SUBJECT, "Synthetic subject"), row("subj_yy", "Other synthetic subject")] : [row(SUBJECT, "Synthetic subject")];
}

function newQuestionServer(opts: { createReply?: (body: Json) => Reply } = {}) {
  let created: Json | undefined;
  const inner = versionServer(adminVersion({}, NEW_VID, NEW_QID));
  const handler = (r: Req): Reply | undefined => {
    if (r.method === "POST" && r.path === "/admin/questions") {
      const body = r.body as Json;
      if (opts.createReply) {
        const rep = opts.createReply(body);
        if (rep.problem || rep.status) return rep;
      }
      created = adminVersion({ document: body.document }, NEW_VID, NEW_QID);
      inner.state.v = created;
      return { status: 201, json: created };
    }
    if (r.method === "GET" && r.path === "/admin/questions") return { json: { items: [], next_cursor: null } };
    if (r.method === "GET" && r.path === "/programs") return { json: { items: programItems() } };
    if (r.method === "GET" && r.path === `/programs/${PROGRAM}/subjects/${SUBJECT}/syllabus`) return { json: syllabusJson(DEFAULT_SYLLABUS) };
    if (r.method === "GET" && r.path === `/programs/${PROGRAM}/subjects/subj_yy/syllabus`) return { json: syllabusJson({ ...DEFAULT_SYLLABUS, subject: "subj_yy" }) };
    return inner.handler(r);
  };
  return { handler, created: () => created };
}

async function openNew(page: Page, roles: Role[] = ["reviewer"], opts: Parameters<typeof newQuestionServer>[0] = {}) {
  const server = newQuestionServer(opts);
  const log = await mockApi(page, roles, server.handler);
  await signIn(page);
  await page.goto("/admin/questions/new");
  return { server, log };
}

// ================================================================ acceptance 4: new question
test.describe("new question", () => {
  test("staff sees the New question button on the list and it leads to /admin/questions/new", async ({ page }) => {
    await mockApi(page, ["reviewer"], newQuestionServer().handler);
    await signIn(page);
    await page.goto("/admin/questions");
    const entry = page.getByRole("link", { name: "New question", exact: true }).or(button(page, "New question")).first();
    await expect(entry).toBeVisible();
    await entry.click();
    await expect(page).toHaveURL(/\/admin\/questions\/new$/);
  });

  test("the header form has the agreed controls; multiple choice adds Option kind and Option layout", async ({ page }) => {
    await openNew(page);
    await expect(page.getByLabel("Question type", { exact: true }).first()).toBeVisible();
    await expect(page.getByLabel("Exam section", { exact: true }).first()).toBeVisible();
    const levels = page.getByRole("group", { name: "Levels" });
    await expect(levels.getByLabel("SL", { exact: true })).toBeVisible();
    await expect(levels.getByLabel("HL", { exact: true })).toBeVisible();
    for (const name of ["Syllabus node", "Difficulty", "Calculator", "Outcome"]) {
      await expect(page.getByLabel(name, { exact: true }).first(), name).toBeVisible();
    }
    await setControl(page, "Question type", "short structured");
    await expect(page.getByLabel("Option kind", { exact: true })).toHaveCount(0);
    await setControl(page, "Question type", "multiple choice");
    await expect(page.getByLabel("Option kind", { exact: true }).first()).toBeVisible();
    await expect(page.getByLabel("Option layout", { exact: true }).first()).toBeVisible();
  });

  test("the exam sections and syllabus nodes offered come from the syllabus the API serves", async ({ page }) => {
    await openNew(page);
    const section = page.getByLabel("Exam section", { exact: true }).first();
    await expect(section).toBeVisible();
    await expect(page.getByText("Section two").first().or(section.locator("option", { hasText: "Section two" }))).toBeAttached();
  });

  async function fillHeader(page: Page, cls: string) {
    await setControl(page, "Question type", cls);
    await setControl(page, "Exam section", "sec_two");
    const levels = page.getByRole("group", { name: "Levels" });
    await levels.getByLabel("SL", { exact: true }).check();
    await levels.getByLabel("HL", { exact: true }).check();
    await setControl(page, "Syllabus node", "N.1");
    await setControl(page, "Difficulty", "medium");
    await setControl(page, "Calculator", "yes");
    await setControl(page, "Outcome", "Invented outcome for creation");
  }

  test("creating a multiple choice question posts {program, subject, document}, then opens the edit page and announces Created", async ({ page }) => {
    const { log } = await openNew(page);
    await setControl(page, "Question type", "multiple choice");
    await setControl(page, "Exam section", "sec_two");
    const levels = page.getByRole("group", { name: "Levels" });
    await levels.getByLabel("SL", { exact: true }).check();
    await setControl(page, "Syllabus node", "N.1");
    await setControl(page, "Difficulty", "medium");
    await setControl(page, "Calculator", "yes");
    await setControl(page, "Outcome", "Invented outcome for creation");
    await setControl(page, "Option kind", "statement");
    await setControl(page, "Option layout", "single_value");
    await fillRichText(page);
    const correct = page.getByLabel(/correct/i).first();
    if (await correct.isVisible().catch(() => false)) {
      const tag = await correct.evaluate((el) => el.tagName);
      if (tag === "SELECT") await correct.selectOption({ index: 1 }).catch(() => undefined);
    }

    await button(page, "Create").click();
    await expect.poll(() => posts(log).length).toBe(1);
    const body = posts(log)[0]!.body as Json;

    expect(Object.keys(body).every((k) => ["program", "subject", "version", "document"].includes(k))).toBe(true);
    expect(body.program).toBe(PROGRAM);
    expect(body.subject).toBe(SUBJECT);
    expect(body.version).toBe(SYL_VERSION); // newest version, as served by GET /programs
    expect(JSON.stringify(body)).not.toMatch(/"origin"|"source_ref"|"rights/);
    const d = body.document as Json;
    expect(d.question_class).toBe("mcq");
    expect(d.exam_section).toBe("sec_two");
    expect(d.levels).toEqual(["sl"]);
    expect(d.primary_syllabus_node).toBe("N.1");
    expect(d.difficulty).toBe("medium");
    expect(d.calculator).toBe(true);
    expect(d.outcome).toBe("Invented outcome for creation");
    const mcq = d.mcq as Json;
    expect((mcq.options as Json[]).map((o) => o.key)).toEqual(["A", "B", "C", "D"]);
    expect(mcq.option_kind).toBe("statement");
    expect(mcq.option_layout).toBe("single_value");
    expect(["A", "B", "C", "D"]).toContain(mcq.correct_key);

    await expect(page).toHaveURL(new RegExp(`/admin/versions/${NEW_VID}/edit$`));
    await expect(page.getByText("Created").first()).toBeVisible();
    await expect(field(page, "Stem")).toBeVisible();
  });

  test("creating a short structured question starts with one part (a) with one mark point, then opens the edit page", async ({ page }) => {
    const { log } = await openNew(page);
    await fillHeader(page, "short structured");
    await expect(field(page, "Part (a) body")).toBeVisible();
    await expect(field(page, "Mark point 1")).toBeVisible();
    await expect(field(page, "Part (b) body")).toHaveCount(0);
    await fillRichText(page);

    await button(page, "Create").click();
    await expect.poll(() => posts(log).length).toBe(1);
    const body = posts(log)[0]!.body as Json;
    expect(Object.keys(body).every((k) => ["program", "subject", "version", "document"].includes(k))).toBe(true);
    expect(body.program).toBe(PROGRAM);
    expect(body.subject).toBe(SUBJECT);
    expect(body.version).toBe(SYL_VERSION); // newest version, as served by GET /programs
    expect(JSON.stringify(body)).not.toMatch(/"origin"|"source_ref"/);
    const d = body.document as Json;
    expect(d.question_class).toBe("short_structured");
    expect(d.levels).toEqual(["sl", "hl"]);
    expect(d.mcq ?? null).toBeNull();
    expect(labels(d)).toEqual(["a"]);
    expect((partsOf(d)[0]!.mark_points as Json[]).length).toBe(1);
    expect(d.total_marks).toBe(partsOf(d)[0]!.marks);

    await expect(page).toHaveURL(new RegExp(`/admin/versions/${NEW_VID}/edit$`));
    await expect(page.getByText("Created").first()).toBeVisible();
  });

  test("409 own_content_rights_unavailable shows the exact message and keeps the form and what was typed", async ({ page }) => {
    const MESSAGE = "New questions cannot be created right now: the platform's content rights record is missing. Ask a platform admin.";
    const { log } = await openNew(page, ["reviewer"], { createReply: () => ({ problem: { status: 409, code: "own_content_rights_unavailable" } }) });
    await fillHeader(page, "short structured");
    await fillRichText(page);
    await button(page, "Create").click();
    await expect.poll(() => posts(log).length).toBe(1);
    await expect(page.getByText(MESSAGE)).toBeVisible();
    await expect(page).toHaveURL(/\/admin\/questions\/new$/);
    await expect(field(page, "Stem")).toContainText("Synthetic words");
    await expect(button(page, "Create")).toBeEnabled();
  });

  test("a Turkish-only letter blocks the request and names the problem", async ({ page }) => {
    const { log } = await openNew(page);
    await fillHeader(page, "short structured");
    await fillRichText(page);
    await typeAtEnd(page, "Stem", " ış");
    await button(page, "Create").click();
    await expect(page.getByText("Content must be written in English").first()).toBeVisible();
    await page.waitForTimeout(600);
    expect(posts(log)).toHaveLength(0);
    await expect(field(page, "Stem")).toContainText("ış");
  });

  test("the program, subject and newest version come from GET /programs; no Subject select with a single subject", async ({ page }) => {
    const { log } = await openNew(page);
    await expect(page.getByLabel("Outcome", { exact: true })).toBeVisible();
    expect(log.some((r) => r.method === "GET" && r.path === "/programs")).toBe(true);
    await expect(page.getByLabel("Subject", { exact: true })).toHaveCount(0);
    const syl = log.filter((r) => r.path.endsWith("/syllabus"));
    expect(syl.length).toBeGreaterThan(0);
    for (const r of syl) {
      expect(r.path).toBe(`/programs/${PROGRAM}/subjects/${SUBJECT}/syllabus`);
      expect(r.query.get("version")).toBe(SYL_VERSION);
    }
  });

  test("with several subjects a Subject select appears and the chosen subject is posted", async ({ page }) => {
    extraSubject = true;
    try {
      const { log } = await openNew(page);
      const sel = page.getByLabel("Subject", { exact: true });
      await expect(sel).toBeVisible();
      const opts = await sel.locator("option").allTextContents();
      await sel.selectOption({ index: opts.findIndex((t) => t.includes("Other synthetic subject")) });
      await setControl(page, "Question type", "short structured");
      await setControl(page, "Exam section", "sec_two");
      await page.getByRole("group", { name: "Levels" }).getByLabel("SL", { exact: true }).check();
      await setControl(page, "Syllabus node", "N.1");
      await setControl(page, "Difficulty", "medium");
      await setControl(page, "Calculator", "yes");
      await setControl(page, "Outcome", "Invented outcome");
      await fillRichText(page);
      await button(page, "Create").click();
      await expect.poll(() => posts(log).length).toBe(1);
      const body = posts(log)[0]!.body as Json;
      expect(body.program).toBe(PROGRAM);
      expect(body.subject).toBe("subj_yy");
      expect(body.version).toBe(SYL_VERSION);
    } finally {
      extraSubject = false;
    }
  });

  test("a learner role sees the staff notice on /admin/questions/new and no admin request is sent", async ({ page }) => {
    const { log } = await openNew(page, ["student"]);
    await expect(page.getByText("This area is for staff")).toBeVisible();
    await expect(button(page, "Create")).toHaveCount(0);
    await page.waitForTimeout(500);
    expect(log.filter((r) => r.path.startsWith("/admin/"))).toEqual([]);
  });

  test("a learner role does not see the New question button on the list", async ({ page }) => {
    await mockApi(page, ["student"], newQuestionServer().handler);
    await signIn(page);
    await page.goto("/admin/questions");
    await expect(page.getByText("This area is for staff")).toBeVisible();
    await expect(page.getByText("New question", { exact: true })).toHaveCount(0);
  });
});

// ================================================================ acceptance 5: parts
test.describe("parts", () => {
  async function saveAndGet(page: Page, log: Req[]) {
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(1);
    return putBody(puts(log)[0]);
  }

  test("Add part appends part (c) after (a) and (b): marks 1, one mark point, total recomputed", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    await button(page, "Add part").click();
    await expect(field(page, "Part (c) body")).toBeVisible();
    await field(page, "Part (c) body").click();
    await page.keyboard.type("Synthetic body for the new part");
    // part (a) has three mark points, part (b) one; the new part's single point is the last "Mark point 1"
    const newPoint = page.getByRole("textbox", { name: "Mark point 1", exact: true }).last();
    await newPoint.click();
    await page.keyboard.type("new point");

    const { document: d } = await saveAndGet(page, log);
    expect(labels(d)).toEqual(["a", "b", "c"]);
    const added = partsOf(d)[2]!;
    expect(added.marks).toBe(1);
    expect((added.mark_points as Json[]).length).toBe(1);
    expect(new Set(ids(d)).size).toBe(3);
    expect(ids(d).slice(0, 2)).toEqual(["a", "b"]);
    expect(d.total_marks).toBe(2 + 1 + 1);
    const pointIds = partsOf(d).flatMap((p) => (p.mark_points as Json[]).map((m) => m.id));
    expect(new Set(pointIds).size).toBe(pointIds.length);
    // untouched parts reach the server unchanged
    expect(partsOf(d)[0]).toEqual(twoParts()[0]);
    expect(partsOf(d)[1]).toEqual(twoParts()[1]);
  });

  test("Remove part (b) relabels (c) to (b) and keeps every id; references to the removed part are dropped with a visible notice", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion({ document: makeDocument(threeParts()) }));
    await button(page, "Remove part (b)").click();

    // c is now (b)
    await expect(field(page, "Part (b) body")).toContainText("Find the quantity");
    await expect(field(page, "Part (c) body")).toHaveCount(0);
    // two references pointed at the removed part (c.depends_on and c.ecf_from); the notice says how many changed
    const notice = page.locator('[role="status"]').filter({ hasText: /2/ });
    await expect(notice.first()).toBeVisible();

    const { document: d } = await saveAndGet(page, log);
    expect(labels(d)).toEqual(["a", "b"]);
    expect(ids(d)).toEqual(["a", "c"]);
    const moved = partsOf(d)[1]!;
    expect(moved.depends_on).toEqual([]);
    expect(moved.ecf_from).toEqual(["a"]);
    expect(partsOf(d)[0]).toEqual(threeParts()[0]);
    expect((moved.mark_points as Json[]).map((m) => m.id)).toEqual(["c-m1"]);
    expect(d.total_marks).toBe(2 + 1);
  });

  test("Move part (b) up swaps the parts and relabels; a reference that now points forward is removed and reported", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion({ document: makeDocument(threeParts()) }));
    await button(page, "Move part (b) up").click();
    // the old (b) text is now first, labelled (a)
    await expect(field(page, "Part (a) body")).toContainText("Explain the quantity");
    await expect(field(page, "Part (b) body")).toContainText("State the quantity");
    await expect(page.locator('[role="status"]').filter({ hasText: /\d/ }).first()).toBeVisible();

    const { document: d } = await saveAndGet(page, log);
    expect(labels(d)).toEqual(["a", "b", "c"]);
    expect(ids(d)).toEqual(["b", "a", "c"]);
    // b depended on a; a is now later, so the reference is gone
    expect(partsOf(d)[0]!.depends_on).toEqual([]);
    // c depended on b and had ecf from a and b: both are still earlier, so they stay
    expect(partsOf(d)[2]!.depends_on).toEqual(["b"]);
    expect(partsOf(d)[2]!.ecf_from).toEqual(["a", "b"]);
    expect(d.total_marks).toBe(2 + 1 + 1);
  });

  test("moving without invalidating any reference changes no reference and shows no reference notice", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion());
    await button(page, "Move part (b) up").click();
    const { document: d } = await saveAndGet(page, log);
    expect(ids(d)).toEqual(["b", "a"]);
    expect(labels(d)).toEqual(["a", "b"]);
    expect(partsOf(d).every((p) => (p.depends_on as unknown[]).length === 0 && (p.ecf_from as unknown[]).length === 0)).toBe(true);
  });

  test("at least one part remains: Remove is not offered on the last part", async ({ page }) => {
    await openEditor(page, adminVersion());
    await button(page, "Remove part (b)").click();
    await expect(field(page, "Part (b) body")).toHaveCount(0);
    const last = button(page, "Remove part (a)");
    if ((await last.count()) > 0) await expect(last).toBeDisabled();
    else await expect(last).toHaveCount(0);
  });

  test("Move up is not offered on the first part and Move down not on the last", async ({ page }) => {
    await openEditor(page, adminVersion());
    for (const name of ["Move part (a) up", "Move part (b) down"]) {
      const b = button(page, name);
      if ((await b.count()) > 0) await expect(b, name).toBeDisabled();
    }
    await expect(button(page, "Move part (b) up")).toBeEnabled();
    await expect(button(page, "Move part (a) down")).toBeEnabled();
  });
});

// ================================================================ acceptance 6: error locations
test.describe("error locations", () => {
  const LOCATED = "This formula does not render: \\frac{1}{";
  const UNLOCATED = "The document is too large for this synthetic limit.";
  const LOC = "document.parts.0.mark_points.1.content.content.0.content.0.attrs.latex";

  function problemReply(): Reply {
    return {
      problem: {
        status: 422,
        code: "invalid_document",
        detail: "invalid",
        errors: [
          { code: "math_not_renderable", message: LOCATED, location: LOC },
          { code: "document_too_large", message: UNLOCATED, location: null },
        ],
      },
    };
  }

  test("a located problem appears next to Mark point 2 of part (a), not next to the other mark points", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion(), ["reviewer"], undefined, () => problemReply());
    await typeAtEnd(page, "Mark point 2", " and me");
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(1);

    await expect(page.getByText(LOCATED, { exact: false }).first()).toBeVisible();
    expect(await page.getByText(LOCATED, { exact: false }).count()).toBeGreaterThanOrEqual(2); // summary + field

    // The field's container: walk up from the editor until the ancestor would hold a second editable field.
    const near = async (name: string) =>
      field(page, name).evaluate((el, msg) => {
        const described = (el.getAttribute("aria-describedby") ?? "")
          .split(/\s+/)
          .map((id) => document.getElementById(id)?.textContent ?? "")
          .join(" ");
        if (described.includes(msg)) return true;
        let node: HTMLElement | null = el.parentElement;
        let best: HTMLElement | null = null;
        while (node && node !== document.body) {
          const editors = node.querySelectorAll('[contenteditable="true"],textarea,input[type="text"]').length;
          if (editors > 1) break;
          best = node;
          node = node.parentElement;
        }
        return best !== null && (best.textContent ?? "").includes(msg);
      }, LOCATED);

    expect(await near("Mark point 2")).toBe(true);
    expect(await near("Mark point 1")).toBe(false);
    expect(await near("Mark point 3")).toBe(false);
    expect(await near("Part (b) body")).toBe(false);
    await expect(field(page, "Mark point 2")).toContainText("beta point and me"); // nothing typed is lost
  });

  test("a problem without a location is listed only in the summary", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion(), ["reviewer"], undefined, () => problemReply());
    await typeAtEnd(page, "Stem", " x");
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(1);
    await expect(page.getByText(UNLOCATED, { exact: false }).first()).toBeVisible();
    expect(await page.getByText(UNLOCATED, { exact: false }).count()).toBe(1);
  });

  test("the summary link for the located problem focuses the Mark point 2 field", async ({ page }) => {
    const { log } = await openEditor(page, adminVersion(), ["reviewer"], undefined, () => problemReply());
    await typeAtEnd(page, "Stem", " x");
    await save(page).click();
    await expect.poll(() => puts(log).length).toBe(1);

    const link = page.getByRole("link", { name: LOCATED, exact: false }).or(page.getByRole("button", { name: LOCATED, exact: false })).first();
    await expect(link).toBeVisible();
    await link.click();
    await expect
      .poll(() => field(page, "Mark point 2").evaluate((el) => el === document.activeElement || el.contains(document.activeElement)))
      .toBe(true);
  });
});

// ================================================================ acceptance 7: command terms from version.syllabus
test.describe("syllabus vocabulary", () => {
  const CASES: { name: string; syl: { program: string; subject: string; version: string }; terms: string[]; other: string[] }[] = [
    { name: "first syllabus", syl: { program: "prog_one", subject: "subj_one", version: "v11" }, terms: ["alpha_term", "beta_term"], other: ["gamma_term", "delta_term"] },
    { name: "second syllabus", syl: { program: "prog_two", subject: "subj_two", version: "v22" }, terms: ["gamma_term", "delta_term"], other: ["alpha_term", "beta_term"] },
  ];

  for (const c of CASES) {
    test(`command terms come from the syllabus of version.syllabus (${c.name}), fetched with its program, subject and version`, async ({ page }) => {
      const mine: SyllabusSpec = { ...c.syl, commandTerms: c.terms };
      const others: SyllabusSpec[] = CASES.filter((x) => x !== c).map((x) => ({ ...x.syl, commandTerms: x.terms }));
      // The page may also try the default program; only the version's own syllabus is served, any other fetch is a 404.
      const v = adminVersion({ syllabus: c.syl, document: makeDocument([part("a", "State the quantity ", 1, [mark("a-m1", "alpha point")], { command_term: c.terms[0] })]) });
      const { log } = await openEditor(page, v, ["reviewer"], [mine, ...others.map((o) => ({ ...o, version: o.version + "-unserved" }))]);

      await expect
        .poll(() => log.filter((r) => r.method === "GET" && r.path === `/programs/${c.syl.program}/subjects/${c.syl.subject}/syllabus`).length)
        .toBeGreaterThan(0);
      const fetched = log.filter((r) => r.path.endsWith("/syllabus"));
      for (const r of fetched) {
        expect(r.path).toBe(`/programs/${c.syl.program}/subjects/${c.syl.subject}/syllabus`);
        expect(r.query.get("version")).toBe(c.syl.version);
      }

      const control = page.getByLabel(/command term/i).first();
      await expect(control).toBeVisible();
      const tag = await control.evaluate((el) => el.tagName);
      let offered: string[];
      if (tag === "SELECT") {
        offered = await control.evaluate((el) => Array.from((el as HTMLSelectElement).options).map((o) => `${o.value} ${o.text}`));
      } else {
        await control.click();
        offered = await page.getByRole("option").allTextContents();
      }
      const joined = norm(offered.join(" | "));
      for (const t of c.terms) expect(joined, `offers ${t}`).toContain(norm(t));
      for (const t of c.other) expect(joined, `does not offer ${t}`).not.toContain(norm(t));
    });
  }
});
