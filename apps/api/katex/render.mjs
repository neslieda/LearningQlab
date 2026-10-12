// Reads {"items": [{"latex": string, "display": boolean}]} on stdin and reports, for each item,
// whether the pinned KaTeX renders it. Started by qlab.content.math under Node's permission
// model: no file-system write, child process or worker (and, from Node 25, no network). The
// settings below are part of the rendering contract: the web renderer must use the same ones,
// with no shared macros (docs/DATA_ARCHITECTURE.md section 3.4).
import katex from "katex";

export const OPTIONS = {
  throwOnError: true,
  strict: "error", // anything LaTeX itself would not accept is an error, not a warning
  trust: false, // no \href, \url, \includegraphics, \htmlClass and the like
  maxExpand: 1000,
  maxSize: 20,
  output: "htmlAndMathml",
};

// A formula whose markup is larger than this is refused: it would stall a browser.
export const MAX_OUTPUT_CHARS = 100_000;

let input = "";
for await (const chunk of process.stdin) input += chunk;
const { items } = JSON.parse(input);
const results = items.map(({ latex, display }) => {
  try {
    const html = katex.renderToString(latex, { ...OPTIONS, displayMode: Boolean(display) });
    if (html.length > MAX_OUTPUT_CHARS) {
      return { ok: false, error: `rendered markup is larger than ${MAX_OUTPUT_CHARS} characters` };
    }
    return { ok: true };
  } catch (error) {
    return { ok: false, error: String(error?.message ?? error).slice(0, 300) };
  }
});
process.stdout.write(JSON.stringify({ version: katex.version, results }));
