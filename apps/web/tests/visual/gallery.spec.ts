import { expect, test } from "@playwright/test";
import { fixtures } from "@qlab/question-renderer";

test.beforeEach(async ({ page }) => {
  await page.goto("/dev/gallery");
  await page.evaluate(() => document.fonts.ready);
  await page.addStyleTag({ content: "*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}" });
});

test("the page does not scroll horizontally", async ({ page }, info) => {
  const width = info.project.use.viewport?.width ?? 0;
  const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
  expect(scrollWidth).toBeLessThanOrEqual(width);
});

for (const fixture of fixtures) {
  test(`fixture ${fixture.id}`, async ({ page }) => {
    const locator = page.getByTestId(`fixture-${fixture.id}`);
    await expect(locator).toBeVisible();
    await expect(locator).toHaveScreenshot(`${fixture.id}.png`);
  });
}
