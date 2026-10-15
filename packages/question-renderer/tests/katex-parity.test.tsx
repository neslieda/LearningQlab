import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import * as pkg from "../src";
import { Math as MathView } from "../src";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const serverDir = resolve(root, "apps/api/katex");

const serverOptions = (): Record<string, unknown> => {
  const src = readFileSync(resolve(serverDir, "render.mjs"), "utf8");
  const m = /export const OPTIONS = (\{[\s\S]*?\n\});/.exec(src);
  expect(m, "OPTIONS object not found in render.mjs").not.toBeNull();
  return new Function(`return ${m![1]}`)() as Record<string, unknown>;
};

describe("KaTeX parity with the server (3.1, DATA_ARCHITECTURE 3.4)", () => {
  it("the renderer depends on exactly the server's KaTeX version", () => {
    const server = JSON.parse(readFileSync(resolve(serverDir, "package.json"), "utf8")) as {
      dependencies: Record<string, string>;
    };
    const mine = JSON.parse(
      readFileSync(resolve(root, "packages/question-renderer/package.json"), "utf8"),
    ) as { dependencies: Record<string, string> };
    expect(mine.dependencies.katex).toBe(server.dependencies.katex);
    expect(mine.dependencies.katex).toMatch(/^\d+\.\d+\.\d+$/);
  });

  it("exports KATEX_OPTIONS equal to the server's options, with trust refusing", () => {
    const opts = (pkg as unknown as { KATEX_OPTIONS?: Record<string, unknown> }).KATEX_OPTIONS;
    expect(opts).toBeDefined();
    const server = serverOptions();
    for (const key of ["throwOnError", "strict", "maxExpand", "maxSize", "output"]) {
      expect(opts![key], key).toEqual(server[key]);
    }
    const trust = opts!.trust;
    if (typeof trust === "function") {
      expect((trust as (c: unknown) => unknown)({ command: "\\href", url: "https://example.invalid" })).toBe(false);
    } else {
      expect(trust).toBe(false);
    }
    expect(server.trust).toBe(false);
  });

  it("does not set shared macros", () => {
    const opts = (pkg as unknown as { KATEX_OPTIONS?: Record<string, unknown> }).KATEX_OPTIONS;
    expect(opts).toBeDefined();
    const macros = opts!.macros;
    expect(macros === undefined || Object.keys(macros as object).length === 0).toBe(true);
  });

  it("maxSize is enforced: a 100em rule is clamped to 20em", () => {
    const { container } = render(<MathView latex={"\\rule{100em}{1em}"} display={false} />);
    const html = container.innerHTML;
    expect(html).toContain("border-right-width:20em");
    expect(html).not.toContain("border-right-width:100em");
  });

  it("a size within maxSize is kept", () => {
    const { container } = render(<MathView latex={"\\rule{5em}{1em}"} display={false} />);
    expect(container.innerHTML).toContain("border-right-width:5em");
  });

  it("maxExpand is enforced: runaway macro expansion shows the fallback", () => {
    const { container } = render(
      <MathView latex={"\\def\\a{\\a\\a}\\a"} display={false} />,
    );
    expect(container.textContent).toMatch(/math could not be displayed/i);
  });
});
