# @qlab/api-client

Typed TypeScript client for the QLab API.

- `src/schema.d.ts` is **generated** from `apps/api/openapi.json` by `openapi-typescript`. It is never edited by hand.
- `src/index.ts` is a thin wrapper: `createApiClient({ baseUrl, getToken })` (built on `openapi-fetch`) sends
  `Authorization: Bearer <token>` and exposes typed calls for every path, plus type aliases (`LearnerQuestion`, `AdminVersion`,
  `QuestionDocument`, `Doc`, `Problem`, ...) that all derive from the generated schema.

## Commands

Run in this directory (`npm ci --ignore-scripts` first; Node >= 24).

| Command | What it does |
|---|---|
| `npm run generate` | Rewrites `src/schema.d.ts` from `../../apps/api/openapi.json`. |
| `npm run check` | Regenerates in memory; exits 1 if the committed `src/schema.d.ts` differs. CI runs this. |
| `npm run typecheck` | `tsc --noEmit` (strict). |

## When the API changes

Export the new `apps/api/openapi.json`, run `npm run generate`, commit both files together. If the generated types look wrong,
fix the API's OpenAPI output, not the generated file.
