// Runs the visual regression tests inside the official Playwright image, so that screenshots are
// produced by the same OS, browser build and fonts everywhere (docs/slices/M1G-6-GOSTERIM.md section 6).
// Usage: node scripts/visual-docker.mjs [--update]
import { spawnSync } from "node:child_process";
import { mkdirSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const update = process.argv.includes("--update");

const installed = JSON.parse(readFileSync(resolve(root, "node_modules/@playwright/test/package.json"), "utf8")).version;
const image = `mcr.microsoft.com/playwright:v${installed}-noble`;

// Without --update the repository is mounted read-only at /src and the only writable host mount is
// apps/web/test-results (at /out). With --update the repository is mounted read-write, because the
// regenerated baselines are copied back. The container works on a copy without host node_modules
// (macOS binaries), .git, secrets (.env*) and apps/api.
const inner = `
set -euo pipefail
mkdir -p /work
tar -C /src --exclude=node_modules --exclude=.next --exclude=.git --exclude=test-results --exclude=.venv --exclude='apps/api' --exclude='.env*' -cf - . | tar -C /work -xf -
cd /work
npm ci --ignore-scripts --no-audit --no-fund
npm run build -w @qlab/web
cd apps/web
${update ? "rm -rf tests/visual/__screenshots__" : "export PW_OUTPUT_DIR=/out/results"}
status=0
npx playwright test ${update ? "--update-snapshots" : ""} || status=$?
${update ? "if [ $status -eq 0 ]; then rm -rf /src/apps/web/tests/visual/__screenshots__ && cp -R tests/visual/__screenshots__ /src/apps/web/tests/visual/__screenshots__; fi" : ""}
exit $status
`;

const resultsDir = resolve(root, "apps/web/test-results");
const mounts = update ? ["-v", `${root}:/src`] : ["-v", `${root}:/src:ro`, "-v", `${resultsDir}:/out`];
if (!update) mkdirSync(resultsDir, { recursive: true });

const result = spawnSync(
  "docker",
  ["run", "--rm", "--platform", "linux/amd64", "--ipc=host", ...mounts, "-e", "CI=1", image, "bash", "-c", inner],
  { stdio: "inherit" },
);
process.exit(result.status ?? 1);
