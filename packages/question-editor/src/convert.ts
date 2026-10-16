import type { Doc } from "@qlab/api-client";
import { MARK_NAMES, manifest } from "./manifest";

/** One node in ProseMirror JSON shape; used for both the API document and the editor document. */
export interface JSONNode {
  type: string;
  attrs?: Record<string, unknown>;
  content?: JSONNode[];
  marks?: { type: string }[];
  text?: string;
}

/**
 * The server writes a document in the field order of its Pydantic models, with every field present
 * (default attrs, `marks: []`, `content: []`). Manifest attrs are alphabetical, so the one node whose
 * model order differs is listed here; a test checks the list covers exactly the manifest's attrs.
 */
export const ATTR_ORDER: Record<string, readonly string[]> = {
  quantity: ["value", "unit", "param", "uncertainty"],
};

function attrNames(name: string): string[] {
  const names = Object.keys(manifest.nodes[name]?.attrs ?? {});
  const order = ATTR_ORDER[name];
  return order ? [...order] : names;
}

function markRank(type: string): number {
  const i = MARK_NAMES.indexOf(type);
  return i === -1 ? MARK_NAMES.length : i;
}

function withDefaults(name: string, attrs: Record<string, unknown> | undefined): Record<string, unknown> {
  const spec = manifest.nodes[name];
  const out: Record<string, unknown> = {};
  for (const key of attrNames(name)) {
    const given = attrs?.[key];
    out[key] = given === undefined ? (spec?.attrs[key]?.default ?? null) : given;
  }
  return out;
}

function canonicalMarks(marks: { type: string }[] | undefined): { type: string }[] {
  const seen = new Set<string>();
  const out: { type: string }[] = [];
  for (const m of marks ?? []) {
    if (!seen.has(m.type)) {
      seen.add(m.type);
      out.push({ type: m.type });
    }
  }
  return out.sort((a, b) => markRank(a.type) - markRank(b.type));
}

/** Server shape to the shape the editor loads: every attr present, marks in manifest order. */
function toEditorNode(node: JSONNode): JSONNode {
  const spec = manifest.nodes[node.type];
  const out: JSONNode = { type: node.type };
  if (node.type === "text") {
    out.text = node.text ?? "";
  }
  if (spec && Object.keys(spec.attrs).length > 0) out.attrs = withDefaults(node.type, node.attrs);
  if (node.content && node.content.length > 0) out.content = node.content.map(toEditorNode);
  if (spec?.marks && node.marks && node.marks.length > 0) out.marks = canonicalMarks(node.marks);
  return out;
}

export function toEditorJSON(doc: Doc): JSONNode {
  return toEditorNode(doc as unknown as JSONNode);
}

/**
 * Editor JSON to the exact shape the server stores: marks first on nodes that take marks, then `type`,
 * `attrs`, `content`, `text`; optional attrs and empty `marks`/`content` always present. Empty text
 * nodes are dropped.
 */
function fromEditorNode(node: JSONNode): JSONNode {
  const spec = manifest.nodes[node.type];
  const out: Record<string, unknown> = {};
  if (spec?.marks) out.marks = canonicalMarks(node.marks);
  out.type = node.type;
  if (spec && Object.keys(spec.attrs).length > 0) out.attrs = withDefaults(node.type, node.attrs);
  if (spec && spec.content !== null && !spec.atom) {
    out.content = (node.content ?? []).filter((c) => !(c.type === "text" && !c.text)).map(fromEditorNode);
  }
  if (node.type === "text") out.text = node.text ?? "";
  return out as unknown as JSONNode;
}

export function fromEditorJSON(json: JSONNode): Doc {
  return fromEditorNode(json) as unknown as Doc;
}
