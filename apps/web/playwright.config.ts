import { defineConfig, devices } from "@playwright/test";

// Visual regression runs against `next build` + `next start`, inside the official Playwright Linux image
// (scripts/visual-docker.mjs). Baselines taken anywhere else are not valid.
const port = Number(process.env.VISUAL_PORT ?? 3100);

export default defineConfig({
  testDir: "./tests/visual",
  snapshotPathTemplate: "{testDir}/__screenshots__/{testFilePath}/{arg}-{projectName}{ext}",
  outputDir: process.env.PW_OUTPUT_DIR ?? "./test-results",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: [["list"]],
  expect: { toHaveScreenshot: { animations: "disabled", caret: "hide", maxDiffPixelRatio: 0 } },
  use: { baseURL: `http://127.0.0.1:${port}`, colorScheme: "light", reducedMotion: "reduce" },
  projects: [
    { name: "desktop-1280", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } } },
    { name: "mobile-375", use: { ...devices["Desktop Chrome"], viewport: { width: 375, height: 800 } } },
  ],
  webServer: {
    command: `npm run start -- -p ${port} -H 127.0.0.1`,
    url: `http://127.0.0.1:${port}/dev/gallery`,
    reuseExistingServer: false,
    timeout: 60_000,
  },
});
