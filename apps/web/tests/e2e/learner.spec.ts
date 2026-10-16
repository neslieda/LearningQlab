// Slice 8 learner screens, written from docs/slices/M1G-8-OGRENCI.md section 4 / 5 item 7 and the frozen OpenAPI contract.
// The API is mocked (page.route). All content is invented.
import { expect, test, type Page, type Route } from "@playwright/test";

const ME = "acc_0" + "b".repeat(25);
const QID_MCQ = "q_0" + "a".repeat(25);
const QID_STR = "q_0" + "c".repeat(25);
const QID_3 = "q_0" + "d".repeat(25);
const VID = "qv_0" + "a".repeat(25);
const VID_STR = "qv_0" + "c".repeat(25);

type Json = Record<string, unknown>;
const doc = (t: string): Json => ({ type: "doc", content: [{ type: "paragraph", content: [{ type: "text", text: t }] }] });

const mcqQuestion = (): Json => ({
  id: QID_MCQ, version_id: VID, question_class: "mcq", exam_section: "section_a", levels: ["sl", "hl"], total_marks: 1,
  stem: doc("An invented stem about a trolley on a ramp."), stimuli: [], parts: [],
  mcq: {
    option_layout: "single_value", column_headers: [], statements: [],
    options: ["A", "B", "C", "D"].map((key) => ({ key, cells: [doc(`Invented value ${key}`)] })),
  },
});
const structQuestion = (): Json => ({
  id: QID_STR, version_id: VID_STR, question_class: "short_structured", exam_section: "section_b", levels: ["hl"], total_marks: 3,
  stem: doc("An invented scenario about a cart."), stimuli: [], mcq: null,
  parts: [
    { id: "p_a", label: "a", lead_in: null, body: doc("State the invented quantity."), marks: 1, command_term: "State", stimulus_refs: [] },
    { id: "p_b", label: "b", lead_in: null, body: doc("Explain the invented effect."), marks: 2, command_term: "Explain", stimulus_refs: [] },
  ],
});
const summary = (id: string, vid: string, cls = "mcq", section = "section_a"): Json => ({
  id, version_id: vid, question_class: cls, exam_section: section, levels: ["sl"], total_marks: 1,
});
const stored = (over: Json = {}): Json => ({
  id: "rsp_0" + "1".repeat(25), question_id: QID_MCQ, version_id: VID, kind: "mcq", part_id: null,
  selected_key: "B", text: null, correct: false, created_at: "2026-10-01T09:00:00Z", ...over,
});
const page_ = (items: Json[], next: string | null = null) => ({ items, next_cursor: next });
const mcqResult = (correct: boolean): Json => ({
  kind: "mcq", response_id: "rsp_0" + "9".repeat(25), version_id: VID, correct, correct_key: "C",
  explanation: doc("EXPLANATION-SENTINEL"),
  rationales: [
    { key: "A", content: doc("RATIONALE-A-SENTINEL") },
    { key: "B", content: doc("RATIONALE-B-SENTINEL") },
    { key: "D", content: doc("RATIONALE-D-SENTINEL") },
  ],
});

type Req = { method: string; path: string; query: URLSearchParams; body: unknown };
type Reply = { status?: number; json?: unknown; problem?: { status: number; code: string } } | undefined;

async function mockApi(page: Page, handler: (r: Req) => Reply, signedIn = true) {
  const log: Req[] = [];
  await page.route("**/api/v1/**", async (route: Route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname.replace(/^.*\/api\/v1/, "");
    let body: unknown;
    try { body = request.postDataJSON(); } catch { body = undefined; }
    const req: Req = { method: request.method(), path, query: url.searchParams, body };
    log.push(req);
    const reply: NonNullable<Reply> =
      path === "/me"
        ? signedIn ? { json: { account_id: ME, roles: ["student"] } } : { problem: { status: 401, code: "unauthenticated" } }
        : (handler(req) ?? { problem: { status: 404, code: "not_found" } });
    if (reply.problem) {
      const p = reply.problem;
      await route.fulfill({ status: p.status, contentType: "application/problem+json", body: JSON.stringify({ type: "about:blank", title: p.code, status: p.status, code: p.code, detail: null, errors: [] }) });
    } else {
      await route.fulfill({ status: reply.status ?? 200, contentType: "application/json", body: JSON.stringify(reply.json ?? {}) });
    }
  });
  return log;
}
const signIn = (page: Page) => page.addInitScript(() => sessionStorage.setItem("qlab.dev.token", "fake.dev.token"));
const noHScroll = async (page: Page) =>
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);

test.describe("Practice entry and list", () => {
  test("a signed-in student sees the Practice link", async ({ page }) => {
    await mockApi(page, () => undefined);
    await signIn(page);
    await page.goto("/");
    await expect(page.getByRole("link", { name: "Practice" }).first()).toBeVisible();
  });

  test("filters in the URL are sent to GET /v1/questions", async ({ page }) => {
    const log = await mockApi(page, (r) => {
      if (r.path === "/questions") return { json: page_([summary(QID_MCQ, VID)]) };
      if (r.path === "/me/responses") return { json: page_([]) };
      return undefined;
    });
    await signIn(page);
    await page.goto("/learn?exam_section=section_a&question_class=mcq&level=sl");
    await expect.poll(() =>
      log.some((r) => r.path === "/questions" && r.method === "GET" && r.query.get("exam_section") === "section_a" && r.query.get("question_class") === "mcq" && r.query.get("level") === "sl"),
    ).toBe(true);
    await expect(page).toHaveURL(/exam_section=section_a/);
    await expect(page).toHaveURL(/question_class=mcq/);
    await expect(page).toHaveURL(/level=sl/);
  });

  test("Load more fetches the next page with the cursor; Answered badge marks answered questions only", async ({ page }) => {
    const log = await mockApi(page, (r) => {
      if (r.path === "/questions") {
        if (r.query.get("cursor") === "cur2") return { json: page_([summary(QID_3, "qv_0" + "d".repeat(25))]) };
        return { json: page_([summary(QID_MCQ, VID), summary(QID_STR, VID_STR, "short_structured", "section_b")], "cur2") };
      }
      if (r.path === "/me/responses") return { json: page_([stored()]) };
      return undefined;
    });
    await signIn(page);
    await page.goto("/learn");
    await expect(page.getByRole("button", { name: "Load more" })).toBeVisible();
    await expect(page.getByText("Answered", { exact: true })).toHaveCount(1);
    await page.getByRole("button", { name: "Load more" }).click();
    await expect.poll(() => log.some((r) => r.path === "/questions" && r.query.get("cursor") === "cur2")).toBe(true);
    await expect(page.getByRole("button", { name: "Load more" })).toHaveCount(0);
    await expect(page.locator(`a[href="/learn/${QID_3}"]`).first()).toBeVisible();
    await expect(page.getByText("Answered", { exact: true })).toHaveCount(1);
  });

  test("privacy notice with a link to /privacy; no horizontal scroll", async ({ page }) => {
    await mockApi(page, (r) => (r.path === "/questions" ? { json: page_([summary(QID_MCQ, VID)]) } : r.path === "/me/responses" ? { json: page_([]) } : undefined));
    await signIn(page);
    await page.goto("/learn");
    await expect(page.locator('a[href="/privacy"]').first()).toBeVisible();
    await noHScroll(page);
  });

  test("without a session a sign-in link is offered", async ({ page }) => {
    await mockApi(page, () => undefined, false);
    await page.goto("/learn");
    await expect(page.locator('a[href="/dev/sign-in"]').first()).toBeVisible();
  });
});

test.describe("solve: multiple choice", () => {
  const setup = async (page: Page, onAnswer: () => Reply, prior: () => Json[] = () => []) =>
    mockApi(page, (r) => {
      if (r.path === `/questions/${QID_MCQ}` && r.method === "GET") return { json: mcqQuestion() };
      if (r.path === `/questions/${QID_MCQ}/answers` && r.method === "POST") return onAnswer();
      if (r.path === "/me/responses") return { json: page_(prior()) };
      return undefined;
    });

  test("submit sends the selected key; result, explanation, rationales; answer locked; privacy notice", async ({ page }) => {
    let prior: Json[] = [];
    const log = await setup(page, () => { prior = [stored({ selected_key: "B" })]; return { status: 201, json: mcqResult(false) }; }, () => prior);
    await signIn(page);
    await page.goto(`/learn/${QID_MCQ}`);
    const group = page.getByRole("radiogroup", { name: "Answer options" });
    await expect(group).toBeVisible();
    await expect(group.getByRole("radio")).toHaveCount(4);
    await expect(page.getByText("EXPLANATION-SENTINEL")).toHaveCount(0);
    await group.getByRole("radio").nth(1).check();
    await page.getByRole("button", { name: "Submit answer" }).click();
    const post = log.find((r) => r.method === "POST");
    expect(post?.path).toBe(`/questions/${QID_MCQ}/answers`);
    expect(post?.body).toEqual({ kind: "mcq", selected_key: "B" });
    await expect(page.getByText("EXPLANATION-SENTINEL")).toBeVisible();
    for (const k of ["A", "B", "D"]) await expect(page.getByText(`RATIONALE-${k}-SENTINEL`)).toBeVisible();
    await expect(page.getByText(/incorrect|not correct|wrong/i).first()).toBeVisible();
    // locked
    for (let i = 0; i < 4; i++) await expect(group.getByRole("radio").nth(i)).toBeDisabled();
    await expect(page.getByText("Your previous answers")).toBeVisible();
    await noHScroll(page);
  });

  test("a correct answer is reported as correct", async ({ page }) => {
    await setup(page, () => ({ status: 201, json: mcqResult(true) }));
    await signIn(page);
    await page.goto(`/learn/${QID_MCQ}`);
    await page.getByRole("radiogroup", { name: "Answer options" }).getByRole("radio").nth(2).check();
    await page.getByRole("button", { name: "Submit answer" }).click();
    await expect(page.getByText("EXPLANATION-SENTINEL")).toBeVisible();
    await expect(page.getByText(/correct/i).first()).toBeVisible();
    await expect(page.getByRole("status")).not.toContainText(/incorrect|not correct/i);
  });

  test("Try again allows a new submission", async ({ page }) => {
    const log = await setup(page, () => ({ status: 201, json: mcqResult(false) }));
    await signIn(page);
    await page.goto(`/learn/${QID_MCQ}`);
    const group = page.getByRole("radiogroup", { name: "Answer options" });
    await group.getByRole("radio").nth(0).check();
    await page.getByRole("button", { name: "Submit answer" }).click();
    await expect(page.getByText("EXPLANATION-SENTINEL")).toBeVisible();
    await page.getByRole("button", { name: "Try again" }).click();
    await expect(page.getByText("EXPLANATION-SENTINEL")).toHaveCount(0);
    await expect(group.getByRole("radio").nth(0)).toBeEnabled();
    await group.getByRole("radio").nth(3).check();
    await page.getByRole("button", { name: "Submit answer" }).click();
    await expect.poll(() => log.filter((r) => r.method === "POST").length).toBe(2);
    expect(log.filter((r) => r.method === "POST")[1]?.body).toEqual({ kind: "mcq", selected_key: "D" });
    await expect(page.getByText("EXPLANATION-SENTINEL")).toBeVisible();
  });

  test("previous answers for this question are listed and requested by question_id", async ({ page }) => {
    const log = await setup(page, () => undefined, () => [stored({ selected_key: "D", correct: false })]);
    await signIn(page);
    await page.goto(`/learn/${QID_MCQ}`);
    await expect(page.getByText("Your previous answers")).toBeVisible();
    await expect.poll(() => log.some((r) => r.path === "/me/responses" && r.query.get("question_id") === QID_MCQ)).toBe(true);
  });

  for (const [code, status, text] of [
    ["answer_does_not_fit", 422, "This answer does not fit the question"],
    ["too_many_answers", 429, "You have reached the limit of 200 answers for this question"],
  ] as const) {
    test(`error ${code} shows its text`, async ({ page }) => {
      await setup(page, () => ({ problem: { status, code } }));
      await signIn(page);
      await page.goto(`/learn/${QID_MCQ}`);
      await page.getByRole("radiogroup", { name: "Answer options" }).getByRole("radio").nth(0).check();
      await page.getByRole("button", { name: "Submit answer" }).click();
      await expect(page.getByText(text)).toBeVisible();
      await expect(page.getByText("EXPLANATION-SENTINEL")).toHaveCount(0);
    });
  }

  test("401 on submit offers a sign-in link", async ({ page }) => {
    await setup(page, () => ({ problem: { status: 401, code: "unauthenticated" } }));
    await signIn(page);
    await page.goto(`/learn/${QID_MCQ}`);
    await page.getByRole("radiogroup", { name: "Answer options" }).getByRole("radio").nth(0).check();
    await page.getByRole("button", { name: "Submit answer" }).click();
    await expect(page.locator('a[href="/dev/sign-in"]').first()).toBeVisible();
  });
});

test.describe("solve: structured", () => {
  test("per-part answer box sends a written answer; mark scheme, notes, language warning; locked; try again", async ({ page }) => {
    const log = await mockApi(page, (r) => {
      if (r.path === `/questions/${QID_STR}` && r.method === "GET") return { json: structQuestion() };
      if (r.path === `/questions/${QID_STR}/answers` && r.method === "POST")
        return {
          status: 201,
          json: {
            kind: "written", response_id: "rsp_0" + "8".repeat(25), version_id: VID_STR, part_id: "p_a", marks: 1, marks_capped: false,
            mark_points: [{ id: "m1", content: doc("MARKPOINT-SENTINEL"), kind: "answer", alternative_group: null, route: null, accept_range: null }],
            notes: [{ kind: "general", content: doc("NOTE-SENTINEL"), mark_point_id: null }],
            language_warning: { code: "answer_not_english", message: "LANGUAGE-WARNING-SENTINEL" },
          },
        };
      if (r.path === "/me/responses") return { json: page_([]) };
      return undefined;
    });
    await signIn(page);
    await page.goto(`/learn/${QID_STR}`);
    const box = page.getByRole("textbox", { name: "Answer for (a)" });
    await expect(box).toBeVisible();
    await expect(page.getByRole("textbox", { name: "Answer for (b)" })).toBeVisible();
    await box.fill("my invented working");
    await page.getByRole("button", { name: "Submit answer for (a)" }).click();
    expect(log.find((r) => r.method === "POST")?.body).toEqual({ kind: "written", part_id: "p_a", text: "my invented working" });
    await expect(page.getByText("MARKPOINT-SENTINEL")).toBeVisible();
    await expect(page.getByText("NOTE-SENTINEL")).toBeVisible();
    await expect(page.getByText("LANGUAGE-WARNING-SENTINEL")).toBeVisible();
    await expect(box).toHaveValue("my invented working");
    await expect(box).not.toBeEditable();
    await noHScroll(page);
    await page.getByRole("button", { name: "Try again" }).click();
    await expect(page.getByText("MARKPOINT-SENTINEL")).toHaveCount(0);
    await expect(box).toBeEditable();
  });

  test("no language warning text when the response has none", async ({ page }) => {
    await mockApi(page, (r) => {
      if (r.path === `/questions/${QID_STR}` && r.method === "GET") return { json: structQuestion() };
      if (r.path.endsWith("/answers"))
        return { status: 201, json: { kind: "written", response_id: "rsp_0" + "8".repeat(25), version_id: VID_STR, part_id: "p_b", marks: 2, marks_capped: false, mark_points: [{ id: "m1", content: doc("MARKPOINT-SENTINEL"), kind: "answer", alternative_group: null, route: null, accept_range: null }], notes: [], language_warning: null } };
      if (r.path === "/me/responses") return { json: page_([]) };
      return undefined;
    });
    await signIn(page);
    await page.goto(`/learn/${QID_STR}`);
    await page.getByRole("textbox", { name: "Answer for (b)" }).fill("text");
    await page.getByRole("button", { name: "Submit answer for (b)" }).click();
    await expect(page.getByText("MARKPOINT-SENTINEL")).toBeVisible();
    await expect(page.getByText("LANGUAGE-WARNING-SENTINEL")).toHaveCount(0);
  });

  test("answer_does_not_fit on a written answer", async ({ page }) => {
    await mockApi(page, (r) => {
      if (r.path === `/questions/${QID_STR}` && r.method === "GET") return { json: structQuestion() };
      if (r.path.endsWith("/answers")) return { problem: { status: 422, code: "answer_does_not_fit" } };
      if (r.path === "/me/responses") return { json: page_([]) };
      return undefined;
    });
    await signIn(page);
    await page.goto(`/learn/${QID_STR}`);
    await page.getByRole("textbox", { name: "Answer for (a)" }).fill("x");
    await page.getByRole("button", { name: "Submit answer for (a)" }).click();
    await expect(page.getByText("This answer does not fit the question")).toBeVisible();
  });
});

test.describe("history and account", () => {
  test("history lists answers with question links and paginates", async ({ page }) => {
    const log = await mockApi(page, (r) => {
      if (r.path !== "/me/responses") return undefined;
      if (r.query.get("cursor") === "cur2") return { json: page_([stored({ id: "rsp_0" + "3".repeat(25), question_id: QID_3, selected_key: "A", correct: true })]) };
      return { json: page_([stored(), stored({ id: "rsp_0" + "2".repeat(25), question_id: QID_STR, kind: "written", part_id: "p_a", selected_key: null, text: "INVENTED-WRITTEN-ANSWER", correct: null })], "cur2") };
    });
    await signIn(page);
    await page.goto("/learn/history");
    await expect(page.getByRole("heading", { name: "My answers" })).toBeVisible();
    await expect(page.getByText("INVENTED-WRITTEN-ANSWER")).toBeVisible();
    await expect(page.locator(`a[href="/learn/${QID_MCQ}"]`).first()).toBeVisible();
    await expect(page.locator(`a[href="/learn/${QID_STR}"]`).first()).toBeVisible();
    await page.getByRole("button", { name: "Load more" }).click();
    await expect.poll(() => log.some((r) => r.path === "/me/responses" && r.query.get("cursor") === "cur2")).toBe(true);
    await expect(page.locator(`a[href="/learn/${QID_3}"]`).first()).toBeVisible();
    await noHScroll(page);
  });

  test("account: My answers, history link, privacy notice, confirm dialog, cancel sends nothing, confirm deletes", async ({ page }) => {
    const log = await mockApi(page, (r) => {
      if (r.path === "/me/responses" && r.method === "GET") return { json: page_([stored(), stored({ id: "rsp_0" + "2".repeat(25) })]) };
      if (r.path === "/me/responses" && r.method === "DELETE") return { json: { deleted: 2 } };
      return undefined;
    });
    await signIn(page);
    await page.goto("/account");
    await expect(page.getByRole("heading", { name: "My answers" })).toBeVisible();
    await expect(page.locator('a[href="/learn/history"]').first()).toBeVisible();
    await expect(page.locator('a[href="/privacy"]').first()).toBeVisible();
    await page.getByRole("button", { name: "Delete all my answers" }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog.getByText("This deletes every answer you have saved. It cannot be undone.")).toBeVisible();
    await dialog.getByRole("button", { name: /cancel/i }).click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
    expect(log.some((r) => r.method === "DELETE")).toBe(false);
    await page.getByRole("button", { name: "Delete all my answers" }).click();
    await page.getByRole("dialog").getByRole("button", { name: /delete/i }).click();
    await expect.poll(() => log.filter((r) => r.method === "DELETE").map((r) => r.path)).toEqual(["/me/responses"]);
    await noHScroll(page);
  });
});
