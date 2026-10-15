import { Extension, Mark, Node, getSchema, mergeAttributes, type AnyExtension, type NodeViewRenderer } from "@tiptap/core";
import type { Schema } from "@tiptap/pm/model";
import { history, redo, undo } from "@tiptap/pm/history";
import { splitListItem } from "@tiptap/pm/schema-list";
import { tableEditing } from "@tiptap/pm/tables";
import { manifest, type AttrSpec, type NodeSpec } from "./manifest";

/**
 * Everything about which nodes and marks exist, their groups, content expressions, attrs, defaults,
 * atoms and mark exclusions comes from the manifest. The tables below only say how a node looks in
 * HTML (clipboard and `getHTML`), which the manifest does not carry.
 */
const HTML: Record<string, { tag: string; parse?: string[] }> = {
  paragraph: { tag: "p", parse: ["p"] },
  bullet_list: { tag: "ul", parse: ["ul"] },
  ordered_list: { tag: "ol", parse: ["ol"] },
  list_item: { tag: "li", parse: ["li"] },
  table: { tag: "table", parse: ["table"] },
  table_row: { tag: "tr", parse: ["tr"] },
  table_cell: { tag: "td", parse: ["td"] },
  table_header: { tag: "th", parse: ["th"] },
  hard_break: { tag: "br", parse: ["br"] },
};
const ATOM_TAG: Record<string, string> = {
  math_inline: "span",
  math_block: "div",
  quantity: "span",
  figure: "div",
};
/** Pasted markup never creates these; they only move inside the editor. */
const NOT_PASTABLE = new Set(["figure"]);

const TABLE_ROLE: Record<string, "table" | "row" | "cell" | "header_cell"> = {
  table: "table",
  table_row: "row",
  table_cell: "cell",
  table_header: "header_cell",
};

const MARK_HTML: Record<string, { render: [string, Record<string, string>?]; parse: ({ tag: string } | { style: string })[] }> = {
  bold: { render: ["strong"], parse: [{ tag: "strong" }, { tag: "b" }, { style: "font-weight=bold" }, { style: "font-weight=700" }] },
  italic: { render: ["em"], parse: [{ tag: "em" }, { tag: "i" }, { style: "font-style=italic" }] },
  sub: { render: ["sub"], parse: [{ tag: "sub" }] },
  sup: { render: ["sup"], parse: [{ tag: "sup" }] },
  optional: { render: ["span", { "data-mark": "optional" }], parse: [{ tag: "span[data-mark=optional]" }] },
  essential: { render: ["u"], parse: [{ tag: "u" }] },
};

type NodeViews = Partial<Record<string, () => NodeViewRenderer>>;

export interface BuildOptions {
  /** Optional React node views by node name (the schema is the same with or without them). */
  nodeViews?: NodeViews;
}

function attrDefs(spec: NodeSpec, htmlAttr: (name: string) => string): Record<string, object> {
  const out: Record<string, object> = {};
  for (const [name, a] of Object.entries(spec.attrs) as [string, AttrSpec][]) {
    out[name] = {
      default: a.default,
      parseHTML: (el: HTMLElement) => {
        const raw = el.getAttribute(htmlAttr(name));
        if (raw === null) return a.default;
        return a.type === "integer" ? Number(raw) : raw;
      },
      renderHTML: (attrs: Record<string, unknown>) => {
        const v = attrs[name];
        return v === null || v === undefined ? {} : { [htmlAttr(name)]: String(v) };
      },
    };
  }
  return out;
}

function nodeExtension(name: string, spec: NodeSpec, views: NodeViews): AnyExtension {
  const isCell = name === "table_cell" || name === "table_header";
  const atomTag = ATOM_TAG[name];
  const html = HTML[name];
  const dataName = (attr: string) => (isCell ? attr : `data-${attr.replace(/_/g, "-")}`);
  const required = Object.entries(spec.attrs).filter(([, a]) => a.required).map(([n]) => n);

  return Node.create({
    name,
    group: spec.group ?? undefined,
    content: spec.content ?? undefined,
    atom: spec.atom,
    inline: spec.group === "inline",
    selectable: true,
    draggable: spec.atom && spec.group === "block",
    isolating: isCell,
    addAttributes() {
      return attrDefs(spec, dataName);
    },
    parseHTML() {
      if (NOT_PASTABLE.has(name)) return [];
      if (atomTag) {
        return [
          {
            tag: `${atomTag}[data-node="${name}"]`,
            getAttrs: (el) => {
              const dom = el as HTMLElement;
              return required.every((n) => (dom.getAttribute(dataName(n)) ?? "") !== "") ? null : false;
            },
          },
        ];
      }
      return (html?.parse ?? []).map((tag) => ({ tag }));
    },
    renderHTML({ HTMLAttributes }) {
      if (atomTag) return [atomTag, mergeAttributes(HTMLAttributes, { "data-node": name })];
      if (name === "hard_break") return ["br"];
      return [html?.tag ?? "div", HTMLAttributes, ...(spec.content ? [0] : [])] as never;
    },
    addNodeView: views[name],
  });
}

function markExtension(name: string, excluded: string[]): AnyExtension {
  const h = MARK_HTML[name] ?? { render: ["span", { "data-mark": name }], parse: [{ tag: `span[data-mark=${name}]` }] };
  return Mark.create({
    name,
    excludes: [name, ...excluded].join(" "),
    parseHTML: () => h.parse,
    renderHTML: ({ HTMLAttributes }) => [h.render[0], mergeAttributes(HTMLAttributes, h.render[1] ?? {}), 0] as never,
  });
}

/** Behaviour only: undo/redo, lists, line breaks, table editing. Adds no node or mark. */
const tableRoles = Extension.create({
  name: "qlabTableRoles",
  extendNodeSchema: (extension) => {
    const role = TABLE_ROLE[extension.name];
    return role ? { tableRole: role } : {};
  },
});

const behaviour = Extension.create({
  name: "qlabBehaviour",
  priority: 1000,
  addProseMirrorPlugins() {
    return [history(), tableEditing()];
  },
  addKeyboardShortcuts() {
    const listItem = this.editor.schema.nodes.list_item;
    return {
      "Mod-z": () => undo(this.editor.state, this.editor.view.dispatch),
      "Mod-y": () => redo(this.editor.state, this.editor.view.dispatch),
      "Shift-Mod-z": () => redo(this.editor.state, this.editor.view.dispatch),
      Enter: () => (listItem ? splitListItem(listItem)(this.editor.state, this.editor.view.dispatch) : false),
      "Shift-Enter": () => this.editor.chain().insertContent({ type: "hard_break" }).run(),
    };
  },
});

export function buildExtensions(options: BuildOptions = {}): AnyExtension[] {
  const views = options.nodeViews ?? {};
  const nodes: AnyExtension[] = [];
  for (const [name, spec] of Object.entries(manifest.nodes)) {
    if (name === manifest.top) {
      nodes.push(Node.create({ name, topNode: true, content: spec.content ?? undefined }));
    } else if (name === "text") {
      nodes.push(Node.create({ name, group: spec.group ?? undefined }));
    } else {
      nodes.push(nodeExtension(name, spec, views));
    }
  }
  const marks = manifest.marks.map(({ name }) => {
    const partners = manifest.mark_exclusions
      .filter((pair) => pair.includes(name))
      .flatMap((pair) => pair.filter((m) => m !== name));
    return markExtension(name, partners);
  });
  return [...nodes, ...marks, tableRoles, behaviour];
}

let cached: Schema | null = null;

/** The editor's ProseMirror schema (without node views). */
export function getEditorSchema(): Schema {
  cached ??= getSchema(buildExtensions());
  return cached;
}
