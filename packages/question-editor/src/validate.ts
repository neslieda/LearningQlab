import type { Doc } from "@qlab/api-client";
import type { JSONNode } from "./convert";
import { renderLatex } from "@qlab/question-renderer";
import { manifest } from "./manifest";

export interface DocProblem {
  /** Same path style as the server: `content[0].content[1].text`. */
  path: string;
  code:
    | "empty_text"
    | "duplicate_mark"
    | "exclusive_marks"
    | "ragged_table"
    | "empty_latex"
    | "math_does_not_render"
    | "bad_attr"
    | "unknown_node"
    | "unknown_mark";
  message: string;
}

const join = (path: string, key: string | number): string =>
  typeof key === "number" ? `${path}[${key}]` : path ? `${path}.${key}` : key;

function checkAttrs(node: JSONNode, path: string, problems: DocProblem[]): void {
  const spec = manifest.nodes[node.type];
  if (!spec) return;
  for (const [name, a] of Object.entries(spec.attrs)) {
    const value = node.attrs?.[name];
    const at = join(join(path, "attrs"), name);
    if (value === undefined || value === null) {
      if (a.required) {
        problems.push({
          path: at,
          code: name === "latex" ? "empty_latex" : "bad_attr",
          message: name === "latex" ? "LaTeX cannot be empty" : `${name} is required`,
        });
      }
      continue;
    }
    if (typeof value === "string") {
      if (a.minLength !== undefined && value.length < a.minLength) {
        problems.push({ path: at, code: name === "latex" ? "empty_latex" : "bad_attr", message: name === "latex" ? "LaTeX cannot be empty" : `${name} is too short` });
      } else if (a.pattern && !new RegExp(a.pattern).test(value)) {
        problems.push({ path: at, code: "bad_attr", message: `${name} has an invalid format` });
      }
    } else if (typeof value === "number") {
      if ((a.minimum !== undefined && value < a.minimum) || (a.maximum !== undefined && value > a.maximum)) {
        problems.push({ path: at, code: "bad_attr", message: `${name} must be between ${a.minimum} and ${a.maximum}` });
      }
    }
  }
}

function checkTable(table: JSONNode, path: string, problems: DocProblem[]): void {
  const rows = table.content ?? [];
  const cellsOf = (r: JSONNode) => r.content ?? [];
  const spanOf = (c: JSONNode, k: "colspan" | "rowspan") => Number(c.attrs?.[k] ?? 1);
  if (rows.some((r) => cellsOf(r).some((c) => spanOf(c, "rowspan") > 1))) return;
  const widths = new Set(rows.map((r) => cellsOf(r).reduce((n, c) => n + spanOf(c, "colspan"), 0)));
  if (widths.size > 1) problems.push({ path, code: "ragged_table", message: "Table rows have different widths" });
}

function walk(node: JSONNode, path: string, problems: DocProblem[]): void {
  const spec = manifest.nodes[node.type];
  if (!spec) {
    problems.push({ path, code: "unknown_node", message: `Unknown node type ${node.type}` });
    return;
  }
  if (node.type === "text" && !node.text) {
    problems.push({ path: join(path, "text"), code: "empty_text", message: "Text nodes cannot be empty" });
  }
  if (node.marks && node.marks.length > 0) {
    const types = node.marks.map((m) => m.type);
    types.forEach((t, i) => {
      if (!manifest.marks.some((m) => m.name === t)) {
        problems.push({ path: join(join(path, "marks"), i), code: "unknown_mark", message: `Unknown mark ${t}` });
      }
    });
    if (new Set(types).size !== types.length) {
      problems.push({ path: join(path, "marks"), code: "duplicate_mark", message: "A mark appears twice on one node" });
    }
    for (const pair of manifest.mark_exclusions) {
      if (pair.every((m) => types.includes(m))) {
        problems.push({
          path: join(path, "marks"),
          code: "exclusive_marks",
          message: `${pair.join(" and ")} cannot be combined`,
        });
      }
    }
  }
  checkAttrs(node, path, problems);
  if ((node.type === "math_inline" || node.type === "math_block") && typeof node.attrs?.latex === "string" && node.attrs.latex !== "") {
    // Same KaTeX options and untrusted-command rule as the renderer.
    if (renderLatex(node.attrs.latex, node.type === "math_block") === null) {
      problems.push({ path: join(join(path, "attrs"), "latex"), code: "math_does_not_render", message: "KaTeX cannot render this formula" });
    }
  }
  if (node.type === "table") checkTable(node, path, problems);
  node.content?.forEach((child, i) => walk(child, join(join(path, "content"), i), problems));
}

/** What the manifest cannot say on its own. Returns every problem found, with its path; never throws. */
export function validateDoc(doc: Doc | JSONNode): DocProblem[] {
  const problems: DocProblem[] = [];
  walk(doc as unknown as JSONNode, "", problems);
  return problems;
}
