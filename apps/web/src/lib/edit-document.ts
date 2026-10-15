// Pure operations on a question document for the edit page (docs/slices/M1G-7B-EDITOR.md section 4).
// Nothing here mutates its input: every function returns a new document (or the same object when nothing changes).
import type { Doc, QuestionDocument } from "@qlab/api-client";
import { nonEnglishPaths, validateDoc } from "@qlab/question-editor";

export type Part = QuestionDocument["parts"][number];
export type MarkPoint = Part["mark_points"][number];
export type Note = Part["notes"][number];
type Mcq = NonNullable<QuestionDocument["mcq"]>;

export const MIN_PART_MARKS = 1;
export const MAX_PART_MARKS = 3;
export const OPTION_KEYS = ["A", "B", "C", "D"] as const;
const SLUG = /^[a-z0-9][a-z0-9_.-]*$/;

export function emptyDoc(): Doc {
  return { type: "doc", content: [{ type: "paragraph", content: [] }] } as Doc;
}

/** True when the document has no visible content (only empty or whitespace-only paragraphs), like the server's rule. */
export function isBlankDoc(doc: Doc | null | undefined): boolean {
  if (!doc) return true;
  return doc.content.every(
    (block) =>
      block.type === "paragraph" &&
      (block.content ?? []).every((inline) => (inline.type === "text" && inline.text.trim() === "") || inline.type === "hard_break"),
  );
}

// ---------------------------------------------------------------------------------------------- generic updates

function replaceAt<T>(items: readonly T[], index: number, next: T): T[] {
  return items.map((item, i) => (i === index ? next : item));
}

export function updatePart(doc: QuestionDocument, partIndex: number, patch: Partial<Part>): QuestionDocument {
  const part = doc.parts[partIndex];
  if (!part) return doc;
  return withTotal({ ...doc, parts: replaceAt(doc.parts, partIndex, { ...part, ...patch }) });
}

export function updateMarkPoint(doc: QuestionDocument, partIndex: number, pointIndex: number, patch: Partial<MarkPoint>): QuestionDocument {
  const part = doc.parts[partIndex];
  const point = part?.mark_points[pointIndex];
  if (!part || !point) return doc;
  return updatePart(doc, partIndex, { mark_points: replaceAt(part.mark_points, pointIndex, { ...point, ...patch }) });
}

export function updateNote(doc: QuestionDocument, partIndex: number, noteIndex: number, patch: Partial<Note>): QuestionDocument {
  const part = doc.parts[partIndex];
  const note = part?.notes[noteIndex];
  if (!part || !note) return doc;
  return updatePart(doc, partIndex, { notes: replaceAt(part.notes, noteIndex, { ...note, ...patch }) });
}

export function updateMcq(doc: QuestionDocument, patch: Partial<Mcq>): QuestionDocument {
  if (!doc.mcq) return doc;
  return { ...doc, mcq: { ...doc.mcq, ...patch } };
}

export function updateOption(doc: QuestionDocument, optionIndex: number, patch: Partial<Mcq["options"][number]>): QuestionDocument {
  const option = doc.mcq?.options[optionIndex];
  if (!doc.mcq || !option) return doc;
  return updateMcq(doc, { options: replaceAt(doc.mcq.options, optionIndex, { ...option, ...patch }) });
}

export function updateOptionCell(doc: QuestionDocument, optionIndex: number, cellIndex: number, cell: Doc): QuestionDocument {
  const option = doc.mcq?.options[optionIndex];
  if (!option) return doc;
  return updateOption(doc, optionIndex, { cells: replaceAt(option.cells, cellIndex, cell) });
}

// ---------------------------------------------------------------------------------------------- marks

/** The total is derived: the sum of part marks for a structured question, 1 for a multiple-choice question. */
export function totalMarks(doc: QuestionDocument): number {
  return doc.question_class === "mcq" ? 1 : doc.parts.reduce((sum, p) => sum + p.marks, 0);
}

function withTotal(doc: QuestionDocument): QuestionDocument {
  const total = totalMarks(doc);
  return total === doc.total_marks ? doc : { ...doc, total_marks: total };
}

/** Sets a part's marks (clamped to 1-3, whole numbers) and recomputes the total. */
export function setPartMarks(doc: QuestionDocument, partIndex: number, marks: number): QuestionDocument {
  const n = Number.isFinite(marks) ? Math.round(marks) : MIN_PART_MARKS;
  return updatePart(doc, partIndex, { marks: Math.min(MAX_PART_MARKS, Math.max(MIN_PART_MARKS, n)) });
}

// ---------------------------------------------------------------------------------------------- mark points

function allPointIds(doc: QuestionDocument): Set<string> {
  return new Set(doc.parts.flatMap((p) => p.mark_points.map((m) => m.id)));
}

/** A new id in the existing style (`<part label>-m<N>`, e.g. `c.ii-m3`) that no mark point in the question has. */
export function newMarkPointId(doc: QuestionDocument, partIndex: number): string {
  const part = doc.parts[partIndex];
  const prefix = part ? part.label : "p";
  const taken = allPointIds(doc);
  let n = (part?.mark_points.length ?? 0) + 1;
  while (taken.has(`${prefix}-m${n}`)) n++;
  return `${prefix}-m${n}`;
}

export function addMarkPoint(doc: QuestionDocument, partIndex: number): QuestionDocument {
  const part = doc.parts[partIndex];
  if (!part) return doc;
  const point: MarkPoint = { id: newMarkPointId(doc, partIndex), content: emptyDoc(), kind: "statement" };
  return updatePart(doc, partIndex, { mark_points: [...part.mark_points, point] });
}

/** Removes a mark point. A part keeps at least one; notes that pointed at the removed point apply to the whole part. */
export function removeMarkPoint(doc: QuestionDocument, partIndex: number, pointIndex: number): QuestionDocument {
  const part = doc.parts[partIndex];
  const point = part?.mark_points[pointIndex];
  if (!part || !point || part.mark_points.length <= 1) return doc;
  return updatePart(doc, partIndex, {
    mark_points: part.mark_points.filter((_, i) => i !== pointIndex),
    notes: part.notes.map((n) => (n.mark_point_id === point.id ? { ...n, mark_point_id: null } : n)),
  });
}

function moved<T>(items: readonly T[], index: number, delta: -1 | 1): T[] | null {
  const to = index + delta;
  if (index < 0 || index >= items.length || to < 0 || to >= items.length) return null;
  const next = [...items];
  const [item] = next.splice(index, 1);
  next.splice(to, 0, item as T);
  return next;
}

export function moveMarkPoint(doc: QuestionDocument, partIndex: number, pointIndex: number, delta: -1 | 1): QuestionDocument {
  const part = doc.parts[partIndex];
  const next = part ? moved(part.mark_points, pointIndex, delta) : null;
  return part && next ? updatePart(doc, partIndex, { mark_points: next }) : doc;
}

// ---------------------------------------------------------------------------------------------- notes

export function addNote(doc: QuestionDocument, partIndex: number): QuestionDocument {
  const part = doc.parts[partIndex];
  if (!part) return doc;
  const note: Note = { kind: "general", content: emptyDoc() };
  return updatePart(doc, partIndex, { notes: [...part.notes, note] });
}

export function removeNote(doc: QuestionDocument, partIndex: number, noteIndex: number): QuestionDocument {
  const part = doc.parts[partIndex];
  if (!part || !part.notes[noteIndex]) return doc;
  return updatePart(doc, partIndex, { notes: part.notes.filter((_, i) => i !== noteIndex) });
}

export function moveNote(doc: QuestionDocument, partIndex: number, noteIndex: number, delta: -1 | 1): QuestionDocument {
  const part = doc.parts[partIndex];
  const next = part ? moved(part.notes, noteIndex, delta) : null;
  return part && next ? updatePart(doc, partIndex, { notes: next }) : doc;
}

// ---------------------------------------------------------------------------------------------- paths and labels

/** `parts.0.body` and `parts[0].body` both become `parts[0].body`; a leading `body.document.` (request location) is dropped. */
export function normalizePath(path: string): string {
  return path
    .replace(/^(body\.)?document\.?/, "")
    .replace(/\.(\d+)(?=\.|$|\[)/g, "[$1]")
    .replace(/^\.+/, "");
}

/** "a" -> "(a)", "c.ii" -> "(c)(ii)" */
export function partTag(label: string): string {
  const [letter, roman] = label.split(".");
  return roman ? `(${letter})(${roman})` : `(${letter})`;
}

export interface FieldRef {
  /** The path of the field that holds the problem (the document inside it is not part of it), normalised. */
  field: string;
  /** Human-readable name of that field. */
  label: string;
}

const FIELD_PATTERNS: Array<[RegExp, (m: RegExpMatchArray, doc: QuestionDocument) => string]> = [
  [/^stem/, () => "Stem"],
  [/^outcome/, () => "Outcome"],
  [/^levels/, () => "Levels"],
  [/^difficulty/, () => "Difficulty"],
  [/^calculator/, () => "Calculator allowed"],
  [/^total_marks/, () => "Total marks"],
  [/^exam_section/, () => "Exam section"],
  [/^(primary|secondary)_syllabus_nodes?/, () => "Syllabus node"],
  [/^mcq\.explanation/, () => "Explanation"],
  [/^mcq\.correct_key/, () => "Correct option"],
  [/^mcq\.column_headers\[(\d+)\]/, (m) => `Column header ${Number(m[1]) + 1}`],
  [/^mcq\.statements\[(\d+)\]/, (m) => `Statement ${Number(m[1]) + 1}`],
  [/^mcq\.options\[(\d+)\]\.rationale/, (m) => `Rationale for ${OPTION_KEYS[Number(m[1])] ?? "?"}`],
  [/^mcq\.options\[(\d+)\]\.cells\[(\d+)\]/, (m, d) => optionCellLabel(Number(m[1]), Number(m[2]), d.mcq?.options[Number(m[1])]?.cells.length ?? 1)],
  [/^mcq\.options\[(\d+)\]/, (m) => `Option ${OPTION_KEYS[Number(m[1])] ?? "?"}`],
  [/^parts\[(\d+)\]\.lead_in/, (m, d) => `Part ${tagAt(d, m[1])} lead-in`],
  [/^parts\[(\d+)\]\.body/, (m, d) => `Part ${tagAt(d, m[1])} body`],
  [/^parts\[(\d+)\]\.mark_points\[(\d+)\]\.(\w+)/, (m, d) => `Part ${tagAt(d, m[1])}, ${pointField(m[3] ?? "content", Number(m[2]))}`],
  [/^parts\[(\d+)\]\.notes\[(\d+)\]\.(\w+)/, (m, d) => `Part ${tagAt(d, m[1])}, ${noteField(m[3] ?? "content", Number(m[2]))}`],
  [/^parts\[(\d+)\]\.(\w+)/, (m, d) => `Part ${tagAt(d, m[1])} ${PART_FIELDS[m[2] ?? ""] ?? (m[2] ?? "").replace(/_/g, " ")}`],
];

const PART_FIELDS: Record<string, string> = {
  marks: "marks",
  marks_capped: "marks capped",
  show_that: "show that",
  command_term: "command term",
  answer_type: "answer type",
  assessment_objective: "assessment objective",
  ecf_from: "error carried forward",
  mark_points: "mark points",
  notes: "notes",
};

function tagAt(doc: QuestionDocument, index: string | undefined): string {
  const part = doc.parts[Number(index)];
  return part ? partTag(part.label) : `#${Number(index) + 1}`;
}

function pointField(name: string, index: number): string {
  return name === "content" ? `mark point ${index + 1}` : `mark point ${index + 1} ${name.replace(/_/g, " ")}`;
}

function noteField(name: string, index: number): string {
  return name === "content" ? `note ${index + 1}` : `note ${index + 1} ${name.replace(/_/g, " ")}`;
}

export function optionCellLabel(optionIndex: number, cellIndex: number, cellCount: number): string {
  const key = OPTION_KEYS[optionIndex] ?? "?";
  return cellCount > 1 ? `Option ${key} column ${cellIndex + 1}` : `Option ${key}`;
}

/** Where a path points: the field that holds it (document internals such as `.content[0].text` are cut off) and its name. */
export function describePath(path: string, doc: QuestionDocument): FieldRef {
  const normal = normalizePath(path);
  for (const [pattern, label] of FIELD_PATTERNS) {
    const m = normal.match(pattern);
    if (m) return { field: m[0], label: label(m, doc) };
  }
  return { field: normal, label: normal || "Document" };
}

/** Human-readable name of the field a path points into. */
export function pathLabel(path: string, doc: QuestionDocument): string {
  return describePath(path, doc).label;
}

// ---------------------------------------------------------------------------------------------- client checks

export interface EditProblem {
  /** Normalised path of the field, or null when the problem does not belong to one field. */
  field: string | null;
  label: string | null;
  message: string;
}

export const ENGLISH_MESSAGE = "Content must be written in English";

/** Every rich-text document with the path of the field that holds it. */
export function docFields(doc: QuestionDocument): Array<{ path: string; doc: Doc }> {
  const out: Array<{ path: string; doc: Doc }> = [{ path: "stem", doc: doc.stem }];
  const mcq = doc.mcq;
  if (mcq) {
    mcq.column_headers.forEach((d, i) => out.push({ path: `mcq.column_headers[${i}]`, doc: d }));
    mcq.statements.forEach((d, i) => out.push({ path: `mcq.statements[${i}]`, doc: d }));
    mcq.options.forEach((o, i) => {
      o.cells.forEach((d, j) => out.push({ path: `mcq.options[${i}].cells[${j}]`, doc: d }));
      if (o.rationale) out.push({ path: `mcq.options[${i}].rationale`, doc: o.rationale });
    });
    if (mcq.explanation) out.push({ path: "mcq.explanation", doc: mcq.explanation });
  }
  doc.parts.forEach((p, i) => {
    if (p.lead_in) out.push({ path: `parts[${i}].lead_in`, doc: p.lead_in });
    out.push({ path: `parts[${i}].body`, doc: p.body });
    p.mark_points.forEach((m, j) => out.push({ path: `parts[${i}].mark_points[${j}].content`, doc: m.content }));
    p.notes.forEach((n, j) => out.push({ path: `parts[${i}].notes[${j}].content`, doc: n.content }));
  });
  return out;
}

/**
 * Checks done before a save request is sent: Turkish-only letters, the structure rules of the editor schema and a few
 * simple field rules. The server still enforces everything; this only keeps obvious mistakes from costing a round trip.
 */
export function clientProblems(doc: QuestionDocument): EditProblem[] {
  const problems: EditProblem[] = [];
  const add = (path: string, message: string) => {
    const ref = describePath(path, doc);
    problems.push({ field: ref.field, label: ref.label, message });
  };
  const seen = new Set<string>();
  for (const path of nonEnglishPaths(doc)) {
    const ref = describePath(path, doc);
    if (seen.has(ref.field)) continue;
    seen.add(ref.field);
    problems.push({ field: ref.field, label: ref.label, message: ENGLISH_MESSAGE });
  }
  for (const { path, doc: d } of docFields(doc)) {
    for (const p of validateDoc(d)) add(path, p.message);
  }
  if (doc.levels.length === 0) add("levels", "Choose at least one level");
  if (isBlankDoc(doc.stem)) add("stem", "This field cannot be empty");
  doc.parts.forEach((p, i) => {
    if (isBlankDoc(p.body)) add(`parts[${i}].body`, "This field cannot be empty");
  });
  doc.mcq?.options.forEach((o, i) => {
    if (o.key !== doc.mcq?.correct_key && isBlankDoc(o.rationale)) add(`mcq.options[${i}].rationale`, "A wrong option needs a rationale");
  });
  doc.parts.forEach((p, i) => {
    p.mark_points.forEach((m, j) => {
      if (m.alternative_group && !SLUG.test(m.alternative_group)) {
        add(`parts[${i}].mark_points[${j}].alternative_group`, "Use lower-case letters, digits, dots, dashes or underscores");
      }
      if (m.route && !SLUG.test(m.route)) add(`parts[${i}].mark_points[${j}].route`, "Use lower-case letters, digits, dots, dashes or underscores");
    });
  });
  return problems;
}

// ---------------------------------------------------------------------------------------------- server problems

export interface ServerItem {
  code?: string;
  message: string;
  location?: string | null;
}

const NON_ENGLISH_AT = /found non-English letters at (.+)$/;
const PART_PREFIX = /^(?:Value error, )?part ([a-z](?:\.[ivx]+)?)(?:\s|:)/;

/** Maps what the server returned for a rejected document onto fields. The server sends text, so this reads the few shapes it uses. */
export function serverProblems(items: readonly ServerItem[], doc: QuestionDocument): EditProblem[] {
  const out: EditProblem[] = [];
  for (const item of items) {
    const message = item.message.replace(/^Value error, /, "");
    const english = message.match(NON_ENGLISH_AT);
    if (english) {
      const fields = new Set<string>();
      for (const raw of (english[1] ?? "").split(",")) {
        const path = raw.trim();
        if (!path || path === "...") continue;
        const ref = describePath(path, doc);
        if (fields.has(ref.field)) continue;
        fields.add(ref.field);
        out.push({ field: ref.field, label: ref.label, message: ENGLISH_MESSAGE });
      }
      if (fields.size === 0) out.push({ field: null, label: null, message: ENGLISH_MESSAGE });
      continue;
    }
    if (item.location) {
      const ref = describePath(item.location, doc);
      if (normalizePath(item.location) !== "") {
        out.push({ field: ref.field, label: ref.label, message });
        continue;
      }
    }
    const part = item.message.match(PART_PREFIX);
    if (part) {
      const index = doc.parts.findIndex((p) => p.label === part[1]);
      if (index >= 0) {
        const command = /command term/.test(message);
        const field = `parts[${index}].${command ? "command_term" : "marks"}`;
        const ref = describePath(field, doc);
        out.push({ field: ref.field, label: ref.label, message });
        continue;
      }
    }
    out.push({ field: null, label: null, message });
  }
  return out;
}
