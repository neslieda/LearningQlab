import { describe, expect, it } from "vitest";
import { MARK_NAMES, NODE_NAMES, manifest } from "../src/manifest";
import { ATTR_ORDER } from "../src/convert";
import { getEditorSchema } from "../src/schema";

describe("editor schema from the manifest", () => {
  const schema = getEditorSchema();

  it("has exactly the manifest's nodes and marks, marks in manifest order", () => {
    expect(Object.keys(schema.nodes).sort()).toEqual([...NODE_NAMES].sort());
    expect(Object.keys(schema.marks)).toEqual([...MARK_NAMES]);
  });

  it("takes top node, groups, atoms, attrs and defaults from the manifest", () => {
    expect(schema.topNodeType.name).toBe(manifest.top);
    for (const [name, spec] of Object.entries(manifest.nodes)) {
      const type = schema.nodes[name]!;
      expect(type.isAtom, name).toBe(spec.atom || name === "text");
      expect(Object.keys(type.spec.attrs ?? {}).sort(), name).toEqual(Object.keys(spec.attrs).sort());
      for (const [attr, a] of Object.entries(spec.attrs)) {
        expect(type.spec.attrs![attr]!.default, `${name}.${attr}`).toEqual(a.default);
      }
      if (spec.group) expect(type.isInline).toBe(spec.group === "inline");
      if (spec.content) expect(type.spec.content).toBe(spec.content);
    }
  });

  it("lets paragraph content carry every mark", () => {
    const paragraph = schema.nodes.paragraph!;
    for (const mark of Object.values(schema.marks)) expect(paragraph.allowsMarkType(mark)).toBe(true);
  });

  it("enforces the exclusive mark pairs", () => {
    for (const [a, b] of manifest.mark_exclusions) {
      expect(schema.marks[a!]!.excludes(schema.marks[b!]!)).toBe(true);
      expect(schema.marks[b!]!.excludes(schema.marks[a!]!)).toBe(true);
    }
    expect(schema.marks.bold!.excludes(schema.marks.italic!)).toBe(false);
  });

  it("covers exactly the manifest's attrs in ATTR_ORDER", () => {
    for (const [name, order] of Object.entries(ATTR_ORDER)) {
      expect([...order].sort()).toEqual(Object.keys(manifest.nodes[name]!.attrs).sort());
    }
  });
});
