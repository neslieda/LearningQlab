// Small builders for the synthetic fixtures. Everything here is typed with the generated API types.
import type { components } from "@qlab/api-client";

type S = components["schemas"];
export type Doc = S["Doc"];
export type Block = Doc["content"][number];
export type Paragraph = S["Paragraph"];
export type Inline = Paragraph["content"][number];
export type MarkType = S["MarkType"];

/** A paragraph child: plain strings become text nodes. */
export type Piece = string | Inline;

const toInline = (piece: Piece): Inline => (typeof piece === "string" ? t(piece) : piece);

export const t = (text: string, ...marks: MarkType[]): Inline => ({
  type: "text",
  text,
  marks: marks.map((type) => ({ type })),
});

export const m = (latex: string, ...marks: MarkType[]): Inline => ({
  type: "math_inline",
  attrs: { latex },
  marks: marks.map((type) => ({ type })),
});

export const q = (value: string, unit: string, uncertainty?: string, ...marks: MarkType[]): Inline => ({
  type: "quantity",
  attrs: uncertainty === undefined ? { value, unit } : { value, unit, uncertainty },
  marks: marks.map((type) => ({ type })),
});

export const br = (): Inline => ({ type: "hard_break" });

export const p = (...pieces: Piece[]): Paragraph => ({ type: "paragraph", content: pieces.map(toInline) });

export const mb = (latex: string): Block => ({ type: "math_block", attrs: { latex } });

export const fig = (stimulusId: string): Block => ({ type: "figure", attrs: { stimulus_id: stimulusId } });

export const bullets = (...items: Paragraph[]): Block => ({
  type: "bullet_list",
  content: items.map((item) => ({ type: "list_item", content: [item] })),
});

export const numbered = (...items: Paragraph[]): Block => ({
  type: "ordered_list",
  content: items.map((item) => ({ type: "list_item", content: [item] })),
});

export interface Cell {
  header?: boolean;
  colspan?: number;
  rowspan?: number;
  content: Paragraph | string;
}

export const table = (...rows: Cell[][]): Block => ({
  type: "table",
  content: rows.map((row) => ({
    type: "table_row",
    content: row.map((cell) => {
      const attrs = { colspan: cell.colspan ?? 1, rowspan: cell.rowspan ?? 1 };
      const content = [typeof cell.content === "string" ? p(cell.content) : cell.content];
      return cell.header
        ? { type: "table_header" as const, attrs, content }
        : { type: "table_cell" as const, attrs, content };
    }),
  })),
});

/** Doc from blocks; bare paragraphs are accepted for brevity. */
export const doc = (...blocks: (Block | Paragraph)[]): Doc => ({ type: "doc", content: blocks });

/** A one-paragraph doc from plain pieces. */
export const line = (...pieces: Piece[]): Doc => doc(p(...pieces));
