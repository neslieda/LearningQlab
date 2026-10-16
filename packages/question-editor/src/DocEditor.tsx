"use client";

import type { Doc } from "@qlab/api-client";
import { EditorContent, useEditor } from "@tiptap/react";
import { Fragment, Slice, type Node as PMNode } from "@tiptap/pm/model";
import { useEffect, useId, useMemo, useRef, useState } from "react";
import { fromEditorJSON, toEditorJSON, type JSONNode } from "./convert";
import { LatexForm, latexProblem } from "./LatexForm";
import { nodeViews } from "./nodeViews";
import { buildExtensions } from "./schema";
import { Toolbar, type BlockName } from "./Toolbar";
import type { MarkName } from "./manifest";

const DEFAULT_BLOCKS: readonly BlockName[] = ["math_block", "bullet_list", "ordered_list"];
const DEFAULT_MARKS: readonly MarkName[] = ["bold", "italic", "sub", "sup", "optional"];
const CONTAINERS = new Set(["bullet_list", "ordered_list", "list_item", "table", "table_row", "table_cell", "table_header"]);

export interface DocEditorProps {
  value: Doc;
  onChange: (doc: Doc) => void;
  /** Visible label; also the accessible name of the text area. */
  label: string;
  /** Block kinds the toolbar offers (and paste keeps). Default: math_block, bullet_list, ordered_list. */
  allowedBlocks?: readonly BlockName[];
  /** Marks the toolbar offers (and paste keeps). Default: bold, italic, sub, sup, optional. Add "essential" for mark-scheme fields. */
  allowMarks?: readonly MarkName[];
  ariaDescribedBy?: string;
}

/** Pasted content keeps only what the field allows: figures never, other blocks and marks by prop. */
function cleanSlice(slice: Slice, blocks: readonly BlockName[], marks: readonly MarkName[]): Slice {
  const keep = (node: PMNode): Fragment => {
    const name = node.type.name;
    // Math that KaTeX rejects is kept as plain text (so nothing is lost), never as a math node.
    if ((name === "math_inline" || name === "math_block") && latexProblem(String(node.attrs.latex ?? ""), name === "math_block")) {
      const latex = String(node.attrs.latex ?? "");
      const schema = node.type.schema;
      const run = latex ? [schema.text(latex)] : [];
      return name === "math_block" ? Fragment.from(schema.nodes.paragraph!.create(null, run)) : Fragment.fromArray(run);
    }
    if (name === "figure") return Fragment.empty;
    if (name === "math_block" && !blocks.includes("math_block")) {
      return Fragment.from(node.type.schema.nodes.paragraph!.create(null, node.type.schema.nodes.math_inline!.create(node.attrs)));
    }
    if (CONTAINERS.has(name) && name !== "list_item" && name !== "table_row" && !blocks.includes(name as BlockName)) {
      // Unwrap a disallowed list or table into its paragraphs.
      const paragraphs: PMNode[] = [];
      node.descendants((n) => {
        if (n.type.name === "paragraph") {
          paragraphs.push(n);
          return false;
        }
        return true;
      });
      return mapFragment(Fragment.fromArray(paragraphs));
    }
    if (node.isText || node.isLeaf) {
      const allowed = node.marks.filter((m) => marks.includes(m.type.name as MarkName));
      return Fragment.from(node.mark(allowed));
    }
    return Fragment.from(node.copy(mapFragment(node.content)));
  };
  const mapFragment = (fragment: Fragment): Fragment => {
    const out: PMNode[] = [];
    fragment.forEach((child) => {
      keep(child).forEach((n) => out.push(n));
    });
    return Fragment.fromArray(out);
  };
  const content = mapFragment(slice.content);
  const depth = (first: boolean): number => {
    let n = 0;
    let node = first ? content.firstChild : content.lastChild;
    while (node && !node.isInline) {
      n++;
      node = first ? node.firstChild : node.lastChild;
    }
    return n;
  };
  return new Slice(content, Math.min(slice.openStart, depth(true)), Math.min(slice.openEnd, depth(false)));
}

export function DocEditor({ value, onChange, label, allowedBlocks = DEFAULT_BLOCKS, allowMarks = DEFAULT_MARKS, ariaDescribedBy }: DocEditorProps) {
  const labelId = useId();
  const onChangeRef = useRef(onChange);
  const lastSeen = useRef(JSON.stringify(value));
  const optsRef = useRef({ blocks: allowedBlocks, marks: allowMarks });
  useEffect(() => {
    onChangeRef.current = onChange;
    optsRef.current = { blocks: allowedBlocks, marks: allowMarks };
  });
  const extensions = useMemo(() => buildExtensions({ nodeViews }), []);
  const [mathForm, setMathForm] = useState<{ display: boolean } | null>(null);

  const editor = useEditor({
    extensions,
    content: toEditorJSON(value),
    immediatelyRender: false,
    editorProps: {
      attributes: {
        role: "textbox",
        "aria-multiline": "true",
        "aria-labelledby": labelId,
        ...(ariaDescribedBy ? { "aria-describedby": ariaDescribedBy } : {}),
        class: "qe-content",
      },
      transformPasted: (slice) => cleanSlice(slice, optsRef.current.blocks, optsRef.current.marks),
      handleKeyDown: (view, event) => {
        if (!(event.metaKey || event.ctrlKey) || event.shiftKey || event.altKey) return false;
        const mark = ({ b: "bold", i: "italic" } as Record<string, MarkName | undefined>)[event.key.toLowerCase()];
        if (!mark || !optsRef.current.marks.includes(mark)) return false;
        event.preventDefault();
        const type = view.state.schema.marks[mark]!;
        const { from, to, empty } = view.state.selection;
        const has = view.state.doc.rangeHasMark(from, to, type);
        view.dispatch(empty ? view.state.tr : has ? view.state.tr.removeMark(from, to, type) : view.state.tr.addMark(from, to, type.create()));
        return true;
      },
    },
    onUpdate: ({ editor: e }) => {
      const doc = fromEditorJSON(e.getJSON() as JSONNode);
      lastSeen.current = JSON.stringify(doc);
      onChangeRef.current(doc);
    },
  });

  // An outside change to `value` replaces the content; our own echo does not.
  useEffect(() => {
    if (!editor) return;
    const next = JSON.stringify(value);
    if (next !== lastSeen.current) {
      lastSeen.current = next;
      editor.commands.setContent(toEditorJSON(value), { emitUpdate: false });
    }
  }, [editor, value]);

  const insertMath = (latex: string, display: boolean) => {
    if (!editor) return;
    editor
      .chain()
      .focus()
      .insertContent(display ? { type: "math_block", attrs: { latex } } : { type: "math_inline", attrs: { latex }, marks: [] })
      .run();
    setMathForm(null);
  };

  return (
    <div className="qe-editor">
      <span id={labelId} className="qe-label">
        {label}
      </span>
      {editor ? (
        <Toolbar editor={editor} label={label} marks={allowMarks} blocks={allowedBlocks} onInsertMath={(display) => setMathForm({ display })} />
      ) : null}
      {mathForm ? (
        <LatexForm
          key={String(mathForm.display)}
          initial=""
          display={mathForm.display}
          applyLabel="Insert"
          onApply={(latex) => insertMath(latex, mathForm.display)}
          onCancel={() => {
            setMathForm(null);
            editor?.commands.focus();
          }}
        />
      ) : null}
      <EditorContent editor={editor} />
    </div>
  );
}
