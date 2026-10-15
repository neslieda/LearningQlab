"use client";

import type { Editor } from "@tiptap/core";
import { useEditorState } from "@tiptap/react";
import { addColumnAfter, addRowAfter, deleteColumn, deleteRow, deleteTable } from "@tiptap/pm/tables";
import { liftListItem, wrapInList } from "@tiptap/pm/schema-list";
import { useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import type { MarkName } from "./manifest";

export type BlockName = "math_block" | "table" | "bullet_list" | "ordered_list";

interface ButtonSpec {
  key: string;
  label: string;
  content: ReactNode;
  pressed?: boolean;
  onClick: () => void;
}

export function toggleList(editor: Editor, listName: "bullet_list" | "ordered_list"): void {
  const { schema } = editor.state;
  const list = schema.nodes[listName]!;
  const item = schema.nodes.list_item!;
  editor
    .chain()
    .focus()
    .command(({ state, dispatch }) => {
      const { $from } = state.selection;
      for (let d = $from.depth; d > 0; d--) {
        const node = $from.node(d);
        if (node.type === list) return liftListItem(item)(state, dispatch);
        if (node.type.name === "bullet_list" || node.type.name === "ordered_list") {
          dispatch?.(state.tr.setNodeMarkup($from.before(d), list));
          return true;
        }
      }
      return wrapInList(list)(state, dispatch);
    })
    .run();
}

export function insertTable(editor: Editor): void {
  const { schema } = editor.state;
  const cell = (type: "table_cell" | "table_header") => schema.nodes[type]!.createAndFill()!;
  const row = (type: "table_cell" | "table_header") => schema.nodes.table_row!.create(null, [cell(type), cell(type)]);
  const table = schema.nodes.table!.create(null, [row("table_header"), row("table_cell")]);
  editor.chain().focus().insertContent(table.toJSON()).run();
}

const GLYPH: Record<string, ReactNode> = {
  bold: <strong aria-hidden="true">B</strong>,
  italic: <em aria-hidden="true">I</em>,
  sub: <span aria-hidden="true">x<sub>2</sub></span>,
  sup: <span aria-hidden="true">x<sup>2</sup></span>,
  optional: <span aria-hidden="true">«»</span>,
  essential: <u aria-hidden="true">U</u>,
};
const MARK_LABEL: Record<string, string> = {
  bold: "Bold",
  italic: "Italic",
  sub: "Subscript",
  sup: "Superscript",
  optional: "Optional words (« »)",
  essential: "Essential words (underline)",
};

export interface ToolbarProps {
  editor: Editor;
  label: string;
  marks: readonly MarkName[];
  blocks: readonly BlockName[];
  onInsertMath: (display: boolean) => void;
}

export function Toolbar({ editor, label, marks, blocks, onInsertMath }: ToolbarProps) {
  const state = useEditorState({
    editor,
    selector: ({ editor: e }) => ({
      marks: Object.fromEntries(marks.map((m) => [m, e.isActive(m)])) as Record<string, boolean>,
      bullet: e.isActive("bullet_list"),
      ordered: e.isActive("ordered_list"),
      inTable: e.isActive("table_cell") || e.isActive("table_header"),
    }),
  });
  const [active, setActive] = useState(0);
  const root = useRef<HTMLDivElement>(null);

  const run = (cmd: (s: Editor["state"], d: Editor["view"]["dispatch"]) => boolean) => () => {
    editor.chain().focus().command(({ state, dispatch }) => cmd(state, dispatch!)).run();
  };

  const buttons: ButtonSpec[] = [
    ...marks.map((m) => ({
      key: m,
      label: MARK_LABEL[m] ?? m,
      content: GLYPH[m] ?? m,
      pressed: state.marks[m],
      onClick: () => void editor.chain().focus().toggleMark(m).run(),
    })),
    { key: "math_inline", label: "Inline equation", content: <span aria-hidden="true">∑</span>, onClick: () => onInsertMath(false) },
    ...(blocks.includes("math_block")
      ? [{ key: "math_block", label: "Block equation", content: <span aria-hidden="true">∑∑</span>, onClick: () => onInsertMath(true) }]
      : []),
    ...(blocks.includes("bullet_list")
      ? [{ key: "bullet", label: "Bulleted list", content: <span aria-hidden="true">•</span>, pressed: state.bullet, onClick: () => toggleList(editor, "bullet_list") }]
      : []),
    ...(blocks.includes("ordered_list")
      ? [{ key: "ordered", label: "Numbered list", content: <span aria-hidden="true">1.</span>, pressed: state.ordered, onClick: () => toggleList(editor, "ordered_list") }]
      : []),
    ...(blocks.includes("table")
      ? [{ key: "table", label: "Insert table", content: <span aria-hidden="true">▦</span>, onClick: () => insertTable(editor) }]
      : []),
    ...(blocks.includes("table") && state.inTable
      ? [
          { key: "row", label: "Add row below", content: <span aria-hidden="true">+row</span>, onClick: run(addRowAfter) },
          { key: "col", label: "Add column right", content: <span aria-hidden="true">+col</span>, onClick: run(addColumnAfter) },
          { key: "delrow", label: "Delete row", content: <span aria-hidden="true">−row</span>, onClick: run(deleteRow) },
          { key: "delcol", label: "Delete column", content: <span aria-hidden="true">−col</span>, onClick: run(deleteColumn) },
          { key: "deltable", label: "Delete table", content: <span aria-hidden="true">✕▦</span>, onClick: run(deleteTable) },
        ]
      : []),
  ];

  const focusAt = (i: number) => {
    const n = buttons.length;
    const next = ((i % n) + n) % n;
    setActive(next);
    root.current?.querySelectorAll<HTMLButtonElement>("button")[next]?.focus();
  };
  const onKeyDown = (e: KeyboardEvent) => {
    const at = Math.min(active, buttons.length - 1);
    if (e.key === "ArrowRight") focusAt(at + 1);
    else if (e.key === "ArrowLeft") focusAt(at - 1);
    else if (e.key === "Home") focusAt(0);
    else if (e.key === "End") focusAt(buttons.length - 1);
    else return;
    e.preventDefault();
  };

  return (
    <div ref={root} role="toolbar" aria-label={`${label} formatting`} aria-orientation="horizontal" className="qe-toolbar" onKeyDown={onKeyDown}>
      {buttons.map((b, i) => (
        <button
          key={b.key}
          type="button"
          aria-label={b.label}
          title={b.label}
          aria-pressed={b.pressed}
          tabIndex={i === Math.min(active, buttons.length - 1) ? 0 : -1}
          onFocus={() => setActive(i)}
          onMouseDown={(e) => e.preventDefault()}
          onClick={b.onClick}
        >
          {b.content}
        </button>
      ))}
    </div>
  );
}
