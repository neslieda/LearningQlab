import type { Doc } from "@qlab/api-client";
import { describe, expect, it } from "vitest";
import { nonEnglishPaths } from "../src/language";
import { validateDoc } from "../src/validate";

const para = (...content: unknown[]) => ({ type: "paragraph", content });
const doc = (...content: unknown[]) => ({ type: "doc", content }) as unknown as Doc;
const cell = (colspan = 1, rowspan = 1) => ({ type: "table_cell", attrs: { colspan, rowspan }, content: [para()] });
const codes = (d: Doc) => validateDoc(d).map((p) => `${p.code}@${p.path}`);

describe("validateDoc", () => {
  it("accepts a clean document", () => {
    expect(validateDoc(doc(para({ marks: [], type: "text", text: "a" })))).toEqual([]);
  });

  it("reports empty text nodes with their path", () => {
    expect(codes(doc(para({ marks: [], type: "text", text: "" })))).toEqual(["empty_text@content[0].content[0].text"]);
  });

  it("reports duplicate and exclusive marks", () => {
    const run = (marks: string[]) => doc(para({ marks: marks.map((type) => ({ type })), type: "text", text: "a" }));
    expect(codes(run(["bold", "bold"]))).toEqual(["duplicate_mark@content[0].content[0].marks"]);
    expect(codes(run(["sub", "sup"]))).toEqual(["exclusive_marks@content[0].content[0].marks"]);
    expect(codes(run(["optional", "essential"]))).toEqual(["exclusive_marks@content[0].content[0].marks"]);
    expect(codes(run(["bold", "italic", "sub"]))).toEqual([]);
  });

  it("reports ragged tables unless a rowspan makes widths differ legitimately", () => {
    const table = (...rows: unknown[][]) => doc({ type: "table", content: rows.map((content) => ({ type: "table_row", content })) });
    expect(codes(table([cell(), cell()], [cell()]))).toEqual(["ragged_table@content[0]"]);
    expect(codes(table([cell(2)], [cell(), cell()]))).toEqual([]);
    expect(codes(table([cell(1, 2), cell()], [cell()]))).toEqual([]);
  });

  it("reports empty latex and bad quantity attrs", () => {
    const d = doc(
      { type: "math_block", attrs: { latex: "" } },
      para({ marks: [], type: "quantity", attrs: { value: "abc", unit: "", param: "1x", uncertainty: "-1" } }),
    );
    expect(codes(d)).toEqual([
      "empty_latex@content[0].attrs.latex",
      "bad_attr@content[1].content[0].attrs.param",
      "bad_attr@content[1].content[0].attrs.uncertainty",
      "bad_attr@content[1].content[0].attrs.value",
    ]);
  });

  it("reports unknown nodes and never throws", () => {
    expect(codes(doc({ type: "heading" }))).toEqual(["unknown_node@content[0]"]);
  });
});

describe("nonEnglishPaths", () => {
  it("flags the server's six letters and not ç ö ü", () => {
    for (const ch of "ğĞıİşŞ") expect(nonEnglishPaths({ a: `x${ch}` })).toEqual(["a"]);
    expect(nonEnglishPaths({ a: "Schrödinger çü" })).toEqual([]);
  });

  it("uses the server's path format", () => {
    const d = doc(para({ marks: [], type: "text", text: "ok" }, { marks: [], type: "text", text: "kış" }));
    expect(nonEnglishPaths(d)).toEqual(["content[0].content[1].text"]);
    expect(nonEnglishPaths({ mcq: { options: [{ rationale: "a" }, { rationale: "ışık" }] } })).toEqual(["mcq.options[1].rationale"]);
    expect(nonEnglishPaths(d, "stem")).toEqual(["stem.content[0].content[1].text"]);
  });
});
