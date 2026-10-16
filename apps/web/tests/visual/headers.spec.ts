// Slice 9 section 4: the production build sends the security headers and the CSP does not break KaTeX.
import { expect, test } from "@playwright/test";

test("a production response carries HSTS and a CSP without unsafe-eval", async ({ request }) => {
  const h = (await request.get("/dev/gallery")).headers();
  expect(h["strict-transport-security"]).toContain("max-age=");
  expect(h["referrer-policy"]).toBe("no-referrer");
  expect(h["x-content-type-options"]).toBe("nosniff");
  const csp = h["content-security-policy"] ?? "";
  expect(csp).toContain("frame-ancestors 'none'");
  expect(csp).not.toContain("unsafe-eval");
});

test("the gallery renders math without CSP violations", async ({ page }) => {
  const problems: string[] = [];
  page.on("console", (m) => {
    if (/content security policy/i.test(m.text())) problems.push(m.text());
  });
  await page.goto("/dev/gallery");
  await expect(page.locator(".katex").first()).toBeVisible();
  await page.evaluate(() => document.fonts.ready);
  expect(problems).toEqual([]);
});
