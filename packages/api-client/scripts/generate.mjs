// Generates src/schema.d.ts from apps/api/openapi.json.
//   node scripts/generate.mjs           write the file
//   node scripts/generate.mjs --check   fail (exit 1) if the committed file differs
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import openapiTS, { astToString, COMMENT_HEADER } from "openapi-typescript";

const spec = fileURLToPath(new URL("../../../apps/api/openapi.json", import.meta.url));
const out = fileURLToPath(new URL("../src/schema.d.ts", import.meta.url));

const HEADER = `/**
 * GENERATED FILE - DO NOT EDIT.
 * Source: apps/api/openapi.json. Regenerate with \`npm run generate\` in packages/api-client.
 */

`;

const ast = await openapiTS(pathToFileURL(spec));
const generated = HEADER + COMMENT_HEADER + astToString(ast);

if (process.argv.includes("--check")) {
  let current = null;
  try {
    current = readFileSync(out, "utf8");
  } catch {
    // missing file counts as out of sync
  }
  if (current !== generated) {
    console.error(
      "OpenAPI and API client are out of sync: packages/api-client/src/schema.d.ts does not match apps/api/openapi.json.\n" +
        "Run `npm run generate` in packages/api-client and commit the result. Never edit the file by hand.",
    );
    process.exit(1);
  }
  console.log("API client is in sync with apps/api/openapi.json.");
} else {
  writeFileSync(out, generated);
  console.log(`Wrote ${out}`);
}
