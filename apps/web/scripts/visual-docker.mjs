// Runs the visual regression tests inside the official Playwright image, so that screenshots are
// produced by the same OS, browser build and fonts everywhere (docs/slices/M1G-6-GOSTERIM.md section 6).
// Usage: node scripts/visual-docker.mjs [--update]
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const update = process.argv.includes("--update");

const installed = JSON.parse(readFileSync(resolve(root, "node_modules/@playwright/test/package.json"), "utf8")).version;
const image = `mcr.microsoft.com/playwright:v${installed}-noble`;

// The repo is mounted read-write at /src; the container works on a copy without host node_modules
// (those hold macOS binaries) and writes baselines back to /src only with --update.
const inner = `
set -euo pipefail
mkdir -p /work
tar -C /src --exclude=node_modules --exclude=.next --exclude=.git --exclude=test-results --exclude=.venv --exclude='apps/api' -cf - . | tar -C /work -xf -
cd /work
npm ci --ignore-scripts --no-audit --no-fund
npm run build -w @qlab/web
cd apps/web
export PW_OUTPUT_DIR=/tmp/pw-results
status=0
npx playwright test ${update ? "--update-snapshots" : ""} || status=$?
${update ? "rm -rf /src/apps/web/tests/visual/__screenshots__ && cp -R tests/visual/__screenshots__ /src/apps/web/tests/visual/__screenshots__" : "if [ $status -ne 0 ] && [ -d /tmp/pw-results ]; then rm -rf /src/apps/web/test-results && cp -R /tmp/pw-results /src/apps/web/test-results; fi"}
exit $status
`;

const result = spawnSync(
  "docker",
  ["run", "--rm", "--platform", "linux/amd64", "--ipc=host", "-v", `${root}:/src`, "-e", "CI=1", image, "bash", "-c", inner],
  { stdio: "inherit" },
);
process.exit(result.status ?? 1);
