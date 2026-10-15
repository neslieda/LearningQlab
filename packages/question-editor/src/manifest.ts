import raw from "./manifest.json";

/** Shape of src/manifest.json, generated from the backend Pydantic models. Never edit the JSON by hand. */
export interface AttrSpec {
  default: string | number | boolean | null;
  required: boolean;
  type: "string" | "integer" | string;
  pattern: string | null;
  minLength?: number;
  minimum?: number;
  maximum?: number;
}

export interface NodeSpec {
  atom: boolean;
  attrs: Record<string, AttrSpec>;
  content: string | null;
  group: "block" | "inline" | null;
  /** Whether the node accepts marks. */
  marks: boolean;
}

export interface Manifest {
  schema_version: string;
  top: string;
  marks: { name: string }[];
  mark_exclusions: string[][];
  nodes: Record<string, NodeSpec>;
}

export const manifest = raw as unknown as Manifest;

export const MARK_NAMES: readonly string[] = manifest.marks.map((m) => m.name);
export const NODE_NAMES: readonly string[] = Object.keys(manifest.nodes);

export type MarkName = "bold" | "italic" | "sub" | "sup" | "optional" | "essential";
