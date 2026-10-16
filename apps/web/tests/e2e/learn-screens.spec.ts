// Slice 8 web screens with the API mocked (page.route). All data is the renderer package's invented fixtures.
import { expect, test, type Page, type Route } from "@playwright/test";
import { fixtures } from "@qlab/question-renderer";
import type { components } from "@qlab/api-client";

type S = components["schemas"];

const ME = "acc_0" + "b".repeat(25);
const mcqFx = fixtures.find((f) => f.id === "mcq-single-value");
const structFx = fixtures.find((f) => f.id === "structured");
const msFx = fixtures.find((f) => f.id === "markscheme");
if (mcqFx?.kind !== "learner_question" || structFx?.kind !== "learner_question" || msFx?.kind !== "markscheme") throw new Error("fixtures missing");
const MCQ = mcqFx.data;
const STRUCT = structFx.data;
const MS = msFx.data;
const doc = (t: string): S["Doc"] => ({ type: "doc", content: [{ type: "paragraph", content: [{ type: "text", text: t }] }] }) as S["Doc"];

type Req = { method: string; path: string; query: URLSearchParams; body: unknown };
type Reply = { status?: number; json?: unknown; problem?: { status: number; code: string } };

async function mockApi(page: Page, handler: (r: Req) => Reply | undefined, signedIn = true) {
  const log: Req[] = [];
  await page.route("**/api/v1/**", async (route: Route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname.replace(/^.*\/api\/v1/, "");
    let body: unknown;
    try {
      body = request.postDataJSON();
    } catch {
      body = undefined;
    }
    const req: Req = { method: request.method(), path, query: url.searchParams, body };
    log.push(req);
    const reply: Reply =
      path === "/me" ? (signedIn ? { json: { account_id: ME, roles: ["student"] } } : { problem: { status: 401, code: "unauthenticated" } }) : (handler(req) ?? { problem: { status: 404, code: "not_found" } });
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
const alerts = (page: Page) => page.locator('[role="alert"]:not(#__next-route-announcer__)');
const noHScroll = async (page: Page) => expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);

const response = (over: Partial<S["ResponseOut"]> = {}): S["ResponseOut"] => ({
  id: "r_1", question_id: MCQ.id, version_id: MCQ.version_id, kind: "mcq", part_id: null, selected_key: "B", text: null, correct: false, created_at: "2026-10-01T09:00:00Z", ...over,
});
const summary = (q: S["LearnerQuestion"]): S["LearnerQuestionSummary"] => ({
  id: q.id, version_id: q.version_id, exam_section: q.exam_section, levels: q.levels, question_class: q.question_class, total_marks: q.total_marks,
  topic: q.topic, answered: q.id === MCQ.id,
});

test.describe("practice list", () => {
  test("filters go to the URL and the API; Answered badge; load more", async ({ page }) => {
    const log = await mockApi(page, (r) => {
      if (r.path === "/questions") {
        if (r.query.get("cursor") === "c2") return { json: { items: [summary(STRUCT)], next_cursor: null } };
        return { json: { items: [summary(MCQ)], next_cursor: "c2" } };
      }
      return undefined;
    });
    await signIn(page);
    await page.goto("/learn");
    await expect(page.getByRole("heading", { name: "Practice" })).toBeVisible();
    await expect(page.getByText("Answered", { exact: true })).toHaveCount(1);
    await page.getByRole("button", { name: "Load more" }).click();
    await expect(page.locator(`a[href="/learn/${STRUCT.id}"]`)).toHaveText(`${STRUCT.topic.code} ${STRUCT.topic.title}`);
    await expect(page.getByText("Answered", { exact: true })).toHaveCount(1);
    expect(log.some((r) => r.path === "/me/responses")).toBe(false);
    await page.getByLabel("Level").selectOption("hl");
    await expect(page).toHaveURL(/level=hl/);
    await expect.poll(() => log.some((r) => r.path === "/questions" && r.query.get("level") === "hl")).toBe(true);
    await noHScroll(page);
  });

  test("empty and error states", async ({ page }) => {
    await mockApi(page, (r) => (r.path === "/questions" ? { json: { items: [], next_cursor: null } } : r.path === "/me/responses" ? { json: { items: [], next_cursor: null } } : undefined));
    await signIn(page);
    await page.goto("/learn?question_class=mcq");
    await expect(page.getByText("No questions match these filters.")).toBeVisible();

    const page2 = await page.context().newPage();
    await mockApi(page2, (r) => (r.path === "/questions" ? { problem: { status: 500, code: "boom" } } : { json: { items: [], next_cursor: null } }));
    await signIn(page2);
    await page2.goto("/learn");
    await expect(alerts(page2)).toContainText("Something went wrong (boom)");
  });

  test("without a session the practice list sends no request and links to sign-in", async ({ page }) => {
    const log = await mockApi(page, () => undefined, false);
    await page.goto("/learn");
    await expect(page.locator('a[href="/dev/sign-in"]').first()).toBeVisible();
    await page.waitForTimeout(300);
    expect(log.filter((r) => r.path !== "/me")).toEqual([]);
  });

  test("the header offers Practice to every signed-in user", async ({ page }) => {
    await mockApi(page, () => undefined);
    await signIn(page);
    await page.goto("/");
    await expect(page.getByRole("navigation", { name: "Account" }).getByRole("link", { name: "Practice" })).toBeVisible();
  });
});

test.describe("solve: multiple choice", () => {
  const result = (correct: boolean): S["McqResult"] => ({
    kind: "mcq", response_id: "r_9", version_id: MCQ.version_id, correct, correct_key: "C", explanation: doc("EXPLAIN-TEXT"),
    rationales: [{ key: "A", content: doc("WHY-A") }, { key: "B", content: doc("WHY-B") }, { key: "D", content: doc("WHY-D") }],
  });

  test("submit shows the correct option, explanation and rationales; locks; try again resets", async ({ page }) => {
    let previous: S["ResponseOut"][] = [];
    const log = await mockApi(page, (r) => {
      if (r.path === `/questions/${MCQ.id}` && r.method === "GET") return { json: MCQ };
      if (r.path === `/questions/${MCQ.id}/answers` && r.method === "POST") {
        previous = [response({ selected_key: "B" })];
        return { status: 201, json: result(false) };
      }
      if (r.path === "/me/responses") return { json: { items: previous, next_cursor: null } };
      return undefined;
    });
    await signIn(page);
    await page.goto(`/learn/${MCQ.id}`);
    const group = page.getByRole("radiogroup", { name: "Answer options" });
    await expect(group).toBeVisible();
    await expect(page.getByRole("button", { name: "Submit answer" })).toBeDisabled();
    await group.getByRole("radio", { name: "Option B" }).check();
    await page.getByRole("button", { name: "Submit answer" }).click();
    expect(log.find((r) => r.method === "POST")?.body).toEqual({ kind: "mcq", selected_key: "B" });
    await expect(page.getByText("Not correct. The correct answer is C.")).toBeVisible();
    await expect(page.getByText("Correct answer", { exact: true })).toBeVisible();
    await expect(page.getByText("EXPLAIN-TEXT")).toBeVisible();
    await expect(page.getByRole("group", { name: "Why option B is wrong" })).toContainText("WHY-B");
    await expect(page.getByRole("group", { name: "Why option A is wrong" })).toContainText("WHY-A");
    await expect(group.getByRole("radio", { name: "Option A" })).toBeDisabled();
    await expect(page.getByRole("region").or(page.locator("section")).filter({ hasText: "Your previous answers" }).getByText(/Option B - Incorrect/)).toBeVisible();
    await noHScroll(page);

    await page.getByRole("button", { name: "Try again" }).click();
    await expect(page.getByText("EXPLAIN-TEXT")).toHaveCount(0);
    await expect(group.getByRole("radio", { name: "Option A" })).toBeEnabled();
    await expect(group.getByRole("radio", { name: "Option A" })).toBeFocused();
    await expect(page.getByRole("button", { name: "Submit answer" })).toBeDisabled();
  });

  test("keyboard: arrow keys choose an option and Enter on the button submits", async ({ page }) => {
    await mockApi(page, (r) => {
      if (r.path === `/questions/${MCQ.id}`) return { json: MCQ };
      if (r.path.endsWith("/answers")) return { status: 201, json: result(true) };
      if (r.path === "/me/responses") return { json: { items: [], next_cursor: null } };
      return undefined;
    });
    await signIn(page);
    await page.goto(`/learn/${MCQ.id}`);
    await page.getByRole("radio", { name: "Option A" }).focus();
    await page.keyboard.press("ArrowDown");
    await expect(page.getByRole("radio", { name: "Option B" })).toBeChecked();
    await page.getByRole("button", { name: "Submit answer" }).focus();
    await page.keyboard.press("Enter");
    await expect(page.getByText("Correct. The correct answer is C.")).toBeVisible();
  });

  for (const [code, status, text] of [
    ["answer_limit_reached", 429, "You have reached the limit of 5000 saved answers. Delete your answers to continue."],
    ["answer_does_not_fit", 422, "This answer does not fit the question"],
    ["too_many_answers", 429, "You have reached the limit of 200 answers for this question"],
  ] as const) {
    test(`error ${code}`, async ({ page }) => {
      await mockApi(page, (r) => {
        if (r.path === `/questions/${MCQ.id}`) return { json: MCQ };
        if (r.path.endsWith("/answers")) return { problem: { status, code } };
        if (r.path === "/me/responses") return { json: { items: [], next_cursor: null } };
        return undefined;
      });
      await signIn(page);
      await page.goto(`/learn/${MCQ.id}`);
      await page.getByRole("radio", { name: "Option A" }).check();
      await page.getByRole("button", { name: "Submit answer" }).click();
      await expect(alerts(page)).toContainText(text);
      if (code === "answer_limit_reached") await expect(alerts(page).getByRole("link", { name: "Go to your account" })).toHaveAttribute("href", "/account");
    });
  }

  test("shows the topic as context", async ({ page }) => {
    await mockApi(page, (r) => (r.path === `/questions/${MCQ.id}` ? { json: MCQ } : r.path === "/me/responses" ? { json: { items: [], next_cursor: null } } : undefined));
    await signIn(page);
    await page.goto(`/learn/${MCQ.id}`);
    await expect(page.getByTestId("topic")).toContainText(`${MCQ.topic.code} ${MCQ.topic.title}`);
  });

  test("figure-options layout with rationales: no horizontal scroll, rationale inside its option", async ({ page }) => {
    const figFx = fixtures.find((f) => f.id === "mcq-figure-options");
    if (figFx?.kind !== "learner_question") throw new Error("fixture missing");
    const FIG = figFx.data;
    await mockApi(page, (r) => {
      if (r.path === `/questions/${FIG.id}`) return { json: FIG };
      if (r.path.endsWith("/answers")) return { status: 201, json: result(false) };
      if (r.path === "/me/responses") return { json: { items: [], next_cursor: null } };
      return undefined;
    });
    await signIn(page);
    await page.goto(`/learn/${FIG.id}`);
    await page.getByRole("radio", { name: "Option B" }).check();
    await page.getByRole("button", { name: "Submit answer" }).click();
    const why = page.getByRole("group", { name: "Why option B is wrong" });
    await expect(why).toContainText("WHY-B");
    const inside = await why.evaluate((el) => {
      const li = el.closest("li")!.getBoundingClientRect();
      const r = el.getBoundingClientRect();
      return r.left >= li.left - 1 && r.right <= li.right + 1 && r.bottom <= li.bottom + 1;
    });
    expect(inside).toBe(true);
    await noHScroll(page);
  });

  test("a 401 on submit shows the sign-in link", async ({ page }) => {
    await mockApi(page, (r) => {
      if (r.path === `/questions/${MCQ.id}`) return { json: MCQ };
      if (r.path.endsWith("/answers")) return { problem: { status: 401, code: "unauthenticated" } };
      if (r.path === "/me/responses") return { json: { items: [], next_cursor: null } };
      return undefined;
    });
    await signIn(page);
    await page.goto(`/learn/${MCQ.id}`);
    await page.getByRole("radio", { name: "Option A" }).check();
    await page.getByRole("button", { name: "Submit answer" }).click();
    await expect(alerts(page).locator('a[href="/dev/sign-in"]')).toBeVisible();
  });

  test("a question that is not visible shows the not-found text", async ({ page }) => {
    await mockApi(page, () => undefined);
    await signIn(page);
    await page.goto(`/learn/${MCQ.id}`);
    await expect(alerts(page)).toContainText("Not found or not visible to you");
  });
});

test.describe("solve: structured", () => {
  test("per-part answer boxes, mark scheme, language warning, lock and try again", async ({ page }) => {
    const first = STRUCT.parts[0]!;
    const label = `(${first.label})`;
    const log = await mockApi(page, (r) => {
      if (r.path === `/questions/${STRUCT.id}`) return { json: STRUCT };
      if (r.path === `/questions/${STRUCT.id}/answers`)
        return {
          status: 201,
          json: {
            kind: "written", response_id: "r_5", version_id: STRUCT.version_id, part_id: first.id, marks: MS.marks, marks_capped: MS.marksCapped,
            mark_points: MS.markPoints, notes: MS.notes, language_warning: { code: "answer_not_english", message: "LANG-WARNING-TEXT" },
          },
        };
      if (r.path === "/me/responses") return { json: { items: [], next_cursor: null } };
      return undefined;
    });
    await signIn(page);
    await page.goto(`/learn/${STRUCT.id}`);
    const box = page.getByRole("textbox", { name: `Answer for ${label}` });
    await expect(page.getByRole("button", { name: `Submit answer for ${label}` })).toBeDisabled();
    await box.fill("my working");
    await page.getByRole("button", { name: `Submit answer for ${label}` }).click();
    expect(log.find((r) => r.method === "POST")?.body).toEqual({ kind: "written", part_id: first.id, text: "my working" });
    await expect(page.getByRole("group", { name: "Mark scheme" })).toBeVisible();
    await expect(page.getByText("LANG-WARNING-TEXT")).toBeVisible();
    await expect(box).toHaveAttribute("readonly", "");
    await expect(box).toHaveValue("my working");
    await noHScroll(page);
    await page.getByRole("button", { name: "Try again" }).click();
    await expect(page.getByRole("group", { name: "Mark scheme" })).toHaveCount(0);
    await expect(box).toBeEditable();
    await expect(box).toBeFocused();
  });
});

test.describe("history and account", () => {
  test("history lists answers newest first with a link to the question and paginates", async ({ page }) => {
    await mockApi(page, (r) => {
      if (r.path !== "/me/responses") return undefined;
      if (r.query.get("cursor") === "c2") return { json: { items: [response({ id: "r_old", selected_key: "A", correct: true })], next_cursor: null } };
      return { json: { items: [response(), response({ id: "r_w", kind: "written", part_id: "p", selected_key: null, text: "a written answer", correct: null })], next_cursor: "c2" } };
    });
    await signIn(page);
    await page.goto("/learn/history");
    await expect(page.getByRole("heading", { name: "My answers" })).toBeVisible();
    await expect(page.getByText("a written answer")).toBeVisible();
    await expect(page.getByRole("link", { name: "Open question" }).first()).toHaveAttribute("href", `/learn/${MCQ.id}`);
    await page.getByRole("button", { name: "Load more" }).click();
    await expect(page.getByText("Option A")).toBeVisible();
    await noHScroll(page);
  });

  test("history empty state", async ({ page }) => {
    await mockApi(page, (r) => (r.path === "/me/responses" ? { json: { items: [], next_cursor: null } } : undefined));
    await signIn(page);
    await page.goto("/learn/history");
    await expect(page.getByText("You have not answered any question yet.")).toBeVisible();
  });

  test("account: count, confirm dialog with the exact warning, delete", async ({ page }) => {
    let deleted = false;
    const log = await mockApi(page, (r) => {
      if (r.path === "/me/responses" && r.method === "GET") return { json: { items: deleted ? [] : [response(), response({ id: "r_2" })], next_cursor: deleted ? null : "more" } };
      if (r.path === "/me/responses" && r.method === "DELETE") {
        deleted = true;
        return { json: { deleted: 2 } };
      }
      return undefined;
    });
    await signIn(page);
    await page.goto("/account");
    await expect(page.getByRole("heading", { name: "My answers" })).toBeVisible();
    await expect(page.getByText("You have 2+ saved answers.")).toBeVisible();
    await expect(page.getByText("We store your account ID", { exact: false }).first()).toBeVisible();
    await page.getByRole("button", { name: "Delete all my answers" }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog.getByText("This deletes every answer you have saved. It cannot be undone.")).toBeVisible();
    await dialog.getByRole("button", { name: "Cancel" }).click();
    expect(log.some((r) => r.method === "DELETE")).toBe(false);
    await expect(page.getByRole("button", { name: "Delete all my answers" })).toBeFocused();
    await page.getByRole("button", { name: "Delete all my answers" }).click();
    await page.getByRole("dialog").getByRole("button", { name: /delete all my answers/i }).click();
    await expect(page.getByText("Deleted 2 answers.")).toBeVisible();
    await expect(page.getByText("You have no saved answers.")).toBeVisible();
    await noHScroll(page);
  });

  test("privacy page", async ({ page }) => {
    await mockApi(page, () => undefined);
    await page.goto("/privacy");
    await expect(page.getByRole("heading", { name: "Privacy", level: 1 })).toBeVisible();
    await expect(page.getByRole("link", { name: "account page" })).toBeVisible();
    await expect(page.getByText(/platform owner and the database host can technically access the database/)).toBeVisible();
    await expect(page.getByText(/kept for 14 days on GitHub \(United States\)/)).toBeVisible();
    await expect(page.getByText(/we record your account ID and how many answers were deleted/)).toBeVisible();
  });
});
