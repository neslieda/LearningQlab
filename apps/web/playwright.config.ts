import { defineConfig, devices } from "@playwright/test";

// Visual regression runs against `next build` + `next start`, inside the official Playwright Linux image
// (scripts/visual-docker.mjs). Baselines taken anywhere else are not valid.
const port = Number(process.env.VISUAL_PORT ?? 3100);
// The end-to-end tests need the development sign-in, which a production build does not contain, so they run
// against `next dev` on a second port with its own build directory (it must not overwrite the production build).
const devPort = Number(process.env.E2E_PORT ?? 3101);
// The sign-in tests need a non-local build (real sign-in path) with a mocked issuer: a third dev server.
const oidcPort = Number(process.env.OIDC_PORT ?? 3102);
const OIDC_ENV = {
  NEXT_PUBLIC_QLAB_ENV: "test",
  NEXT_PUBLIC_OIDC_ISSUER: "https://issuer.example.test",
  NEXT_PUBLIC_OIDC_CLIENT_ID: "client-123",
  NEXT_PUBLIC_OIDC_PROJECT_ID: "project-456",
  NEXT_PUBLIC_OIDC_STAFF_ORG_ID: "org-staff",
  NEXT_PUBLIC_OIDC_LEARNER_ORG_ID: "org-learners",
};

export default defineConfig({
  snapshotPathTemplate: "{testDir}/__screenshots__/{testFilePath}/{arg}-{projectName}{ext}",
  outputDir: process.env.PW_OUTPUT_DIR ?? "./test-results",
  fullyParallel: true,
  // The container also runs two Next servers; more workers made pages crash.
  workers: 2,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: [["list"]],
  expect: { toHaveScreenshot: { animations: "disabled", caret: "hide", maxDiffPixelRatio: 0 } },
  use: { colorScheme: "light", reducedMotion: "reduce" },
  projects: [
    // Gallery screenshots: production build. Project names are part of the baseline file names; do not rename.
    {
      name: "desktop-1280",
      testDir: "./tests/visual",
      use: { ...devices["Desktop Chrome"], baseURL: `http://127.0.0.1:${port}`, viewport: { width: 1280, height: 800 } },
    },
    {
      name: "mobile-375",
      testDir: "./tests/visual",
      use: { ...devices["Desktop Chrome"], baseURL: `http://127.0.0.1:${port}`, viewport: { width: 375, height: 800 } },
    },
    // Admin screens with a mocked API (page.route), dev server.
    {
      name: "e2e-desktop-1280",
      testDir: "./tests/e2e",
      use: { ...devices["Desktop Chrome"], baseURL: `http://127.0.0.1:${devPort}`, viewport: { width: 1280, height: 800 } },
    },
    {
      name: "e2e-mobile-375",
      testDir: "./tests/e2e",
      use: { ...devices["Desktop Chrome"], baseURL: `http://127.0.0.1:${devPort}`, viewport: { width: 375, height: 800 } },
    },
    {
      name: "oidc-desktop-1280",
      testDir: "./tests/oidc",
      use: { ...devices["Desktop Chrome"], baseURL: `http://127.0.0.1:${oidcPort}`, viewport: { width: 1280, height: 800 } },
    },
    {
      name: "oidc-mobile-375",
      testDir: "./tests/oidc",
      use: { ...devices["Desktop Chrome"], baseURL: `http://127.0.0.1:${oidcPort}`, viewport: { width: 375, height: 800 } },
    },
  ],
  webServer: [
    {
      command: `npm run start -- -p ${port} -H 127.0.0.1`,
      url: `http://127.0.0.1:${port}/dev/gallery`,
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      command: `npm run dev -- -p ${devPort}`,
      env: { QLAB_DIST_DIR: ".next-dev", NEXT_TELEMETRY_DISABLED: "1", NEXT_PUBLIC_QLAB_ENV: "local" },
      url: `http://127.0.0.1:${devPort}/dev/sign-in`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: `npm run dev -- -p ${oidcPort}`,
      env: { QLAB_DIST_DIR: ".next-oidc", NEXT_TELEMETRY_DISABLED: "1", ...OIDC_ENV },
      // Readiness waits for the heaviest route, so its first on-demand compile does not eat into a test timeout.
      url: `http://127.0.0.1:${oidcPort}/admin/invites`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
