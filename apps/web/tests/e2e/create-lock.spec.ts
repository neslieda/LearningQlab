// Slice 7c review: after Create succeeds the form is locked for good and the edit page is opened exactly once.
// All data is synthetic.
import { expect, test, type Route } from "@playwright/test";

type Json = Record<string, unknown>;
const ME = "acc_0" + "b".repeat(25);
const QID = "q_0" + "d".repeat(25);
const VID = "qv_0" + "d".repeat(25);
const SHA = "ab".repeat(32);

test("a second Create click sends no second POST, the edit page opens once and says Created", async ({ page }) => {
  let posts = 0;
  let created: Json | undefined;
  await page.addInitScript(() => sessionStorage.setItem("qlab.dev.token", "fake.dev.token"));
  await page.route("**/api/v1/**", async (route: Route) => {
    const req = route.request();
    const path = new URL(req.url()).pathname.replace(/^.*\/api\/v1/, "");
    const json = (body: unknown, status = 200) => route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
    if (path === "/me") return json({ account_id: ME, roles: ["reviewer"] });
    if (path === "/programs")
      return json({ items: [{ program: "prog_zz", program_name: "P", subject: "subj_zz", subject_name: "S", versions: [{ code: "v7", title: "v7" }] }] });
    if (path === "/programs/prog_zz/subjects/subj_zz/syllabus")
      return json({
        program: "prog_zz", subject: "subj_zz", version: "v7", title: "T", command_terms: ["alpha_term"],
        exam_sections: [{ code: "sec_two", title: "Section two" }],
        nodes: [{ code: "N.1", title: "Leaf", parent: null, is_leaf: true, attributes: {} }],
      });
    if (req.method() === "POST" && path === "/admin/questions") {
      posts++;
      const body = req.postDataJSON() as { document: Json };
      await new Promise((r) => setTimeout(r, 500));
      created = {
        id: VID, question_id: QID, version_no: 1, status: "draft", content_sha256: SHA, question_class: "short_structured",
        exam_section: "sec_two", levels: ["sl"], total_marks: 1, has_unverified_visuals: false, created_by: ME,
        created_at: "2026-10-01T09:00:00Z", updated_at: "2026-10-01T09:00:00Z", checks: [],
        syllabus: { program: "prog_zz", subject: "subj_zz", version: "v7" }, document: body.document,
      };
      return json(created, 201);
    }
    if (path === `/admin/question-versions/${VID}` && created) return json(created);
    return route.fulfill({ status: 404, contentType: "application/problem+json", body: JSON.stringify({ status: 404, code: "not_found", errors: [] }) });
  });

  await page.goto("/admin/questions/new");
  await page.getByLabel("Exam section", { exact: true }).selectOption("sec_two");
  await page.getByRole("group", { name: "Levels" }).getByLabel("SL", { exact: true }).check();
  await page.getByLabel("Syllabus node", { exact: true }).fill("N.1");
  for (const box of await page.locator('[contenteditable="true"]').all()) {
    await box.click();
    await page.keyboard.type("Synthetic words");
  }
  const create = page.getByRole("button", { name: "Create", exact: true });
  await create.click();
  await expect(create).toBeDisabled();
  await create.click({ force: true }).catch(() => undefined);
  await expect(page).toHaveURL(new RegExp(`/admin/versions/${VID}/edit$`));
  await expect(page.getByText("Created").first()).toBeVisible();
  await page.waitForTimeout(500);
  expect(posts).toBe(1);
  await expect(page).toHaveURL(new RegExp(`/admin/versions/${VID}/edit$`));
});
