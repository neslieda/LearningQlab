import { Editor, getSchema } from "@tiptap/core";
import { Node as PMNode } from "@tiptap/pm/model";
import type { Doc } from "@qlab/api-client";
import { describe, expect, it } from "vitest";
import { fromEditorJSON, toEditorJSON, type JSONNode } from "../src/convert";
import { buildExtensions, getEditorSchema } from "../src/schema";
import { validateDoc } from "../src/validate";
import { pilotDocs, pilotQuestionCount } from "./pilot";

const text = (t: string, marks: { type: string }[] = []) => ({ marks, type: "text", text: t });
const para = (...content: unknown[]) => ({ type: "paragraph", content });
const doc = (...content: unknown[]) => ({ type: "doc", content }) as unknown as Doc;

function viaSchema(d: Doc): Doc {
  const node = PMNode.fromJSON(getEditorSchema(), toEditorJSON(d));
  node.check();
  return fromEditorJSON(node.toJSON() as JSONNode);
}

describe("round trip over the pilot content", () => {
  const docs = pilotDocs();

  it("reads all 130 questions", () => {
    expect(pilotQuestionCount()).toBe(130);
    expect(docs.length).toBeGreaterThan(1000);
  });

  it("every doc field survives load and export byte for byte", () => {
    const bad = docs.filter(({ doc: d }) => JSON.stringify(viaSchema(d as Doc)) !== JSON.stringify(d));
    expect(bad.map((b) => `${b.file}${b.path}`)).toEqual([]);
  });

  it("is also identical through a real Editor instance", () => {
    const editor = new Editor({ extensions: buildExtensions() });
    try {
      // Every 7th doc keeps the test quick; the schema test above covers all of them.
      const bad = docs
        .filter((_, i) => i % 7 === 0)
        .filter(({ doc: d }) => {
          editor.commands.setContent(toEditorJSON(d as Doc), { emitUpdate: false });
          return JSON.stringify(fromEditorJSON(editor.getJSON() as JSONNode)) !== JSON.stringify(d);
        });
      expect(bad.map((b) => `${b.file}${b.path}`)).toEqual([]);
    } finally {
      editor.destroy();
    }
  });

  it("pilot docs have no editor-side problems", () => {
    const bad = docs.filter(({ doc: d }) => validateDoc(d as Doc).length > 0);
    expect(bad.map((b) => `${b.file}${b.path}`)).toEqual([]);
  });
});

describe("conversion edge cases", () => {
  it("keeps an empty paragraph as content: []", () => {
    const d = doc(para());
    expect(JSON.stringify(viaSchema(d))).toBe(JSON.stringify(d));
  });

  it("keeps marks: [] on text and inline math, and mark order from the manifest", () => {
    const d = doc(
      para(
        text("a"),
        text("b", [{ type: "bold" }, { type: "italic" }, { type: "optional" }]),
        { marks: [], type: "math_inline", attrs: { latex: "x^2" } },
        { marks: [{ type: "bold" }], type: "math_inline", attrs: { latex: "y" } },
      ),
    );
    expect(JSON.stringify(viaSchema(d))).toBe(JSON.stringify(d));
  });

  it("round-trips quantity (server attr order), hard_break, lists, tables with spans and figures", () => {
    const cell = (type: string, t: string, colspan = 1, rowspan = 1) => ({
      type,
      attrs: { colspan, rowspan },
      content: [para(text(t))],
    });
    const d = doc(
      para(
        { marks: [{ type: "bold" }], type: "quantity", attrs: { value: "9.81", unit: "m s^-1", param: null, uncertainty: null } },
        { type: "hard_break" },
        { marks: [], type: "quantity", attrs: { value: "20.0", unit: "", param: "g", uncertainty: "0.5" } },
      ),
      { type: "bullet_list", content: [{ type: "list_item", content: [para(text("one"))] }] },
      { type: "ordered_list", content: [{ type: "list_item", content: [para(text("1"))] }, { type: "list_item", content: [para()] }] },
      { type: "math_block", attrs: { latex: "E=mc^2" } },
      {
        type: "table",
        content: [
          { type: "table_row", content: [cell("table_header", "H", 2)] },
          { type: "table_row", content: [cell("table_cell", "a"), cell("table_cell", "b")] },
        ],
      },
      { type: "figure", attrs: { stimulus_id: "s1" } },
    );
    expect(JSON.stringify(viaSchema(d))).toBe(JSON.stringify(d));
  });

  it("normalises a non-canonical input to the server's full form", () => {
    const sparse = {
      type: "doc",
      content: [{ type: "paragraph", content: [{ type: "text", text: "x" }, { type: "quantity", attrs: { value: "1" } }] }, { type: "paragraph" }],
    } as unknown as Doc;
    expect(viaSchema(sparse)).toEqual(
      doc(
        para(text("x"), { marks: [], type: "quantity", attrs: { value: "1", unit: "", param: null, uncertainty: null } }),
        para(),
      ),
    );
  });

  it("drops empty text nodes and marks on hard_break on export", () => {
    const out = fromEditorJSON({
      type: "doc",
      content: [
        {
          type: "paragraph",
          content: [{ type: "text", text: "", marks: [{ type: "bold" }] }, { type: "hard_break", marks: [{ type: "bold" }] }, { type: "text", text: "k" }],
        },
      ],
    });
    expect(out).toEqual(doc(para({ type: "hard_break" }, text("k"))));
  });

  it("removes duplicate marks on export", () => {
    const out = fromEditorJSON({
      type: "doc",
      content: [{ type: "paragraph", content: [{ type: "text", text: "k", marks: [{ type: "italic" }, { type: "bold" }, { type: "italic" }] }] }],
    });
    expect(out).toEqual(doc(para(text("k", [{ type: "bold" }, { type: "italic" }]))));
  });

  it("has a schema that rejects what the manifest forbids", () => {
    const s = getSchema(buildExtensions());
    expect(() => PMNode.fromJSON(s, { type: "heading", content: [] })).toThrow();
    // Adding sub to a run that has sup replaces it (fromJSON does not apply excludes; validateDoc reports that case).
    const added = s.marks.sub!.create().addToSet([s.marks.sup!.create()]);
    expect(added.map((m) => m.type.name)).toEqual(["sub"]);
  });
});
