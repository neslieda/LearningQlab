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

/** How many notes point at the mark point (they apply to the whole part after it is removed). */
export function notesPointingAt(doc: QuestionDocument, partIndex: number, pointIndex: number): number {
  const part = doc.parts[partIndex];
  const point = part?.mark_points[pointIndex];
  if (!part || !point || part.mark_points.length <= 1) return 0;
  return part.notes.filter((n) => n.mark_point_id === point.id).length;
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

// ---------------------------------------------------------------------------------------------- parts

/** The answer type a new part starts with: a short worded answer, valid for any command term. The author changes it. */
export const NEW_PART_ANSWER_TYPE: Part["answer_type"] = "word_phrase";

const LETTERS = "abcdefghijklmnopqrstuvwxyz";
const letterOf = (label: string) => label.split(".")[0] ?? label;

/** Index of the first part of the lettered group (a part and its sub-parts) that `partIndex` belongs to, and the group's length. */
function groupAt(doc: QuestionDocument, partIndex: number): { start: number; end: number } | null {
  const part = doc.parts[partIndex];
  if (!part) return null;
  const letter = letterOf(part.label);
  let start = partIndex;
  while (start > 0 && letterOf(doc.parts[start - 1]!.label) === letter) start--;
  let end = partIndex + 1;
  while (end < doc.parts.length && letterOf(doc.parts[end]!.label) === letter) end++;
  return { start, end };
}

/** Number of lettered groups (top-level parts). */
export function topLevelPartCount(doc: QuestionDocument): number {
  return doc.parts.filter((p, i) => i === 0 || letterOf(doc.parts[i - 1]!.label) !== letterOf(p.label)).length;
}

/** Gives the parts the letters a, b, c ... in order; sub-parts keep their roman numeral and move with their letter. */
function relabel(parts: readonly Part[]): Part[] {
  let group = -1;
  let previous = "";
  return parts.map((p) => {
    const old = letterOf(p.label);
    if (old !== previous) group++;
    previous = old;
    const [, roman] = p.label.split(".");
    const letter = LETTERS[group] ?? "z";
    const label = roman ? `${letter}.${roman}` : letter;
    return label === p.label ? p : { ...p, label };
  });
}

/** Drops depends_on / ecf_from entries that do not name a part before the one that holds them. Returns the count dropped. */
function pruneReferences(parts: readonly Part[]): { parts: Part[]; dropped: number } {
  let dropped = 0;
  const next = parts.map((p, i) => {
    const earlier = new Set(parts.slice(0, i).map((x) => x.id));
    const keep = (ids: readonly string[]) => ids.filter((id) => earlier.has(id));
    const depends = keep(p.depends_on);
    const ecf = keep(p.ecf_from);
    const removed = p.depends_on.length - depends.length + (p.ecf_from.length - ecf.length);
    if (removed === 0) return p;
    dropped += removed;
    return { ...p, depends_on: depends, ecf_from: ecf };
  });
  return { parts: next, dropped };
}

export interface PartChange {
  doc: QuestionDocument;
  /** References to an earlier part that no longer pointed at one and were removed. */
  dropped: number;
}

function rebuild(doc: QuestionDocument, parts: readonly Part[]): PartChange {
  const pruned = pruneReferences(relabel(parts));
  return { doc: withTotal({ ...doc, parts: pruned.parts }), dropped: pruned.dropped };
}

function newPartId(doc: QuestionDocument, label: string): string {
  const taken = new Set(doc.parts.map((p) => p.id));
  const pointIds = allPointIds(doc);
  let id = label;
  for (let n = 2; taken.has(id) || pointIds.has(id); n++) id = `${label}-${n}`;
  return id;
}

/** Adds a part after the last one: 1 mark, one empty mark point, an empty body (the author must fill it before saving). */
export function addPart(doc: QuestionDocument): QuestionDocument {
  const label = LETTERS[topLevelPartCount(doc)];
  if (!label || doc.question_class === "mcq") return doc;
  const id = newPartId(doc, label);
  const part: Part = {
    id,
    label,
    body: emptyDoc(),
    marks: MIN_PART_MARKS,
    marks_capped: false,
    show_that: false,
    command_term: null,
    answer_type: NEW_PART_ANSWER_TYPE,
    assessment_objective: null,
    level_content: "sl_core",
    syllabus_node: doc.primary_syllabus_node,
    stimulus_refs: [],
    depends_on: [],
    ecf_from: [],
    mark_points: [{ id: `${id}-m1`, content: emptyDoc(), kind: "statement" }],
    notes: [],
  };
  return rebuild(doc, [...doc.parts, part]).doc;
}

/** Removes the lettered part at `partIndex` with its sub-parts; at least one part stays. */
export function removePart(doc: QuestionDocument, partIndex: number): PartChange {
  const group = groupAt(doc, partIndex);
  if (!group || (group.start === 0 && group.end === doc.parts.length)) return { doc, dropped: 0 };
  return rebuild(doc, [...doc.parts.slice(0, group.start), ...doc.parts.slice(group.end)]);
}

/** Moves the lettered part at `partIndex` (with its sub-parts) one place up or down among the lettered parts. */
export function movePart(doc: QuestionDocument, partIndex: number, delta: -1 | 1): PartChange {
  const group = groupAt(doc, partIndex);
  const neighbour = group ? groupAt(doc, delta < 0 ? group.start - 1 : group.end) : null;
  if (!group || !neighbour) return { doc, dropped: 0 };
  const [first, second] = delta < 0 ? [neighbour, group] : [group, neighbour];
  const swapped = [...doc.parts.slice(second.start, second.end), ...doc.parts.slice(first.start, first.end)];
  return rebuild(doc, [...doc.parts.slice(0, first.start), ...swapped, ...doc.parts.slice(second.end)]);
}

/** Text of the notice after a removal or move; empty when no reference changed. */
export function referenceNotice(action: "Moving" | "Removing", tag: string, dropped: number): string {
  if (dropped === 0) return "";
  return `${action} part ${tag} removed ${dropped} ${dropped === 1 ? "reference" : "references"} to an earlier part.`;
}

// ---------------------------------------------------------------------------------------------- new question

export type QuestionClass = QuestionDocument["question_class"];
export type OptionKind = Mcq["option_kind"];
export type OptionLayout = Mcq["option_layout"];

/** Kinds and layouts offered when a question is created. The figure ones need figures, which this editor cannot add. */
export const CREATE_OPTION_KINDS: OptionKind[] = ["numeric_with_unit", "ratio", "algebraic_expression", "word_phrase", "statement"];
export const CREATE_OPTION_LAYOUTS: OptionLayout[] = ["single_value", "two_column_table", "roman_statements"];

const ROMAN_STATEMENT_COUNT = 3;

/** The empty multiple-choice block for a layout; `previous` supplies the first cell of each option so a change loses little. */
function mcqTemplate(kind: OptionKind, layout: OptionLayout, previous?: Mcq): Mcq {
  const columns = layout === "two_column_table" ? 2 : 1;
  const cells = (key: number) => Array.from({ length: columns }, (_, c) => previous?.options[key]?.cells[c] ?? emptyDoc());
  return {
    option_kind: kind,
    option_layout: layout,
    level_content: previous?.level_content ?? "sl_core",
    column_headers: columns === 2 ? [previous?.column_headers[0] ?? emptyDoc(), previous?.column_headers[1] ?? emptyDoc()] : [],
    statements: layout === "roman_statements" ? Array.from({ length: ROMAN_STATEMENT_COUNT }, (_, i) => previous?.statements[i] ?? emptyDoc()) : [],
    options: OPTION_KEYS.map((key, i) => ({ key, cells: cells(i), rationale: previous?.options[i]?.rationale ?? null })),
    correct_key: previous?.correct_key ?? "A",
    assessment_objective: previous?.assessment_objective ?? null,
    explanation: previous?.explanation ?? null,
    solution_step: null,
  } as Mcq;
}

/** An empty document of the class: four options for multiple choice, one part (a) with one mark point otherwise. */
export function newDocument(cls: QuestionClass, header: { exam_section?: string; primary_syllabus_node?: string } = {}): QuestionDocument {
  const base = {
    schema_version: "1.0",
    question_class: cls,
    exam_section: header.exam_section ?? "",
    levels: [],
    language: "en",
    calculator: true,
    difficulty: null,
    primary_syllabus_node: header.primary_syllabus_node ?? "",
    secondary_syllabus_nodes: [],
    outcome: null,
    stem: emptyDoc(),
    stimuli: [],
    mcq: cls === "mcq" ? mcqTemplate("word_phrase", "single_value") : null,
    parts: [],
    total_marks: cls === "mcq" ? 1 : 0,
    solution_model: null,
  } as QuestionDocument;
  return cls === "mcq" ? base : addPart(base);
}

/** Switches the class, keeping the header and stem and starting the rest from the empty template. */
export function setQuestionClass(doc: QuestionDocument, cls: QuestionClass): QuestionDocument {
  if (cls === doc.question_class) return doc;
  const fresh = newDocument(cls, doc);
  return { ...fresh, levels: doc.levels, calculator: doc.calculator, difficulty: doc.difficulty, outcome: doc.outcome, stem: doc.stem };
}

/** Changes the option kind and layout of a new multiple-choice question; the options are rebuilt for the layout. */
export function setMcqShape(doc: QuestionDocument, kind: OptionKind, layout: OptionLayout): QuestionDocument {
  if (!doc.mcq) return doc;
  return { ...doc, mcq: mcqTemplate(kind, layout, doc.mcq) };
}

/** Sets the main syllabus node; every part follows it (a new question has no other source for it). */
export function setPrimaryNode(doc: QuestionDocument, code: string): QuestionDocument {
  return { ...doc, primary_syllabus_node: code, parts: doc.parts.map((p) => ({ ...p, syllabus_node: code })) };
}

export interface SyllabusChoices {
  sections: readonly string[];
  leaves: readonly string[];
}

/** Checks done only for a new question: the header values must come from the syllabus that was chosen. */
export function createProblems(doc: QuestionDocument, choices: SyllabusChoices): EditProblem[] {
  const out: EditProblem[] = [];
  if (!choices.sections.includes(doc.exam_section)) out.push({ field: "exam_section", label: "Exam section", message: "Choose an exam section" });
  if (!choices.leaves.includes(doc.primary_syllabus_node)) out.push({ field: "primary_syllabus_node", label: "Syllabus node", message: "Choose a syllabus node from the list" });
  return out;
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

type FieldPattern = [RegExp, (m: RegExpMatchArray, doc: QuestionDocument) => string];

const FIELD_PATTERNS: FieldPattern[] = [
  [/^stem/, () => "Stem"],
  [/^outcome/, () => "Outcome"],
  [/^levels/, () => "Levels"],
  [/^difficulty/, () => "Difficulty"],
  [/^calculator/, () => "Calculator"],
  [/^total_marks/, () => "Total marks"],
  [/^exam_section/, () => "Exam section"],
  [/^(primary|secondary)_syllabus_nodes?/, () => "Syllabus node"],
  [/^mcq\.explanation/, () => "Explanation"],
  [/^mcq\.correct_key/, () => "Correct option"],
  [/^mcq\.column_headers\[(\d+)\]/, (m) => `Column header ${Number(m[1]) + 1}`],
  [/^mcq\.statements\[(\d+)\]/, (m) => `Statement ${Number(m[1]) + 1}`],
  [/^mcq\.options\[(\d+)\]\.rationale/, (m) => `Rationale for ${OPTION_KEYS[Number(m[1])] ?? "?"}`],
  [/^mcq\.options\[(\d+)\]\.cells\[(\d+)\]/, (m, d) => optionCellLabel(Number(m[1]), Number(m[2]), d.mcq?.options[Number(m[1])]?.cells.length ?? 1)],
  [/^parts\[(\d+)\]\.lead_in/, (m, d) => `Part ${tagAt(d, m[1])} lead-in`],
  [/^parts\[(\d+)\]\.body/, (m, d) => `Part ${tagAt(d, m[1])} body`],
  [/^parts\[(\d+)\]\.mark_points\[(\d+)\]\.(content|kind|alternative_group|route)/, (m, d) => `Part ${tagAt(d, m[1])}, ${pointField(m[3] ?? "content", Number(m[2]))}`],
  [/^parts\[(\d+)\]\.notes\[(\d+)\]\.(content|kind|mark_point_id)/, (m, d) => `Part ${tagAt(d, m[1])}, ${noteField(m[3] ?? "content", Number(m[2]))}`],
  [/^parts\[(\d+)\]\.(marks_capped|show_that|command_term|answer_type|assessment_objective|ecf_from|marks)/, (m, d) => `Part ${tagAt(d, m[1])} ${PART_FIELDS[m[2] ?? ""] ?? (m[2] ?? "").replace(/_/g, " ")}`],
];

/** Paths inside an item that has no editor of its own are shown at the item's text field (the nearest editable one). */
const NEAREST: Array<[RegExp, string]> = [
  [/^(parts\[\d+\]\.mark_points\[\d+\])(?:\.|$)/, "$1.content"],
  [/^(parts\[\d+\]\.notes\[\d+\])(?:\.|$)/, "$1.content"],
  [/^(parts\[\d+\])\.depends_on/, "$1.ecf_from"],
  [/^mcq\.options\[(\d+)\]\.(?:key|cells)(?:\.|$)/, "mcq.options[$1].cells[0]"],
];

/** The field a path belongs to, or null when no editable field holds it. */
export function matchField(path: string, doc: QuestionDocument): FieldRef | null {
  const normal = normalizePath(path);
  if (normal === "") return null;
  const find = (p: string): FieldRef | null => {
    for (const [pattern, label] of FIELD_PATTERNS) {
      const m = p.match(pattern);
      if (m) return { field: m[0], label: label(m, doc) };
    }
    return null;
  };
  const direct = find(normal);
  if (direct) return direct;
  for (const [pattern, to] of NEAREST) {
    if (pattern.test(normal)) return find(normal.replace(pattern, to));
  }
  return null;
}

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
  return matchField(path, doc) ?? { field: normalizePath(path), label: normalizePath(path) || "Document" };
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
    o.cells.forEach((c, j) => {
      if (isBlankDoc(c)) add(`mcq.options[${i}].cells[${j}]`, "This field cannot be empty");
    });
  });
  doc.mcq?.statements.forEach((d, i) => {
    if (isBlankDoc(d)) add(`mcq.statements[${i}]`, "This field cannot be empty");
  });
  doc.mcq?.column_headers.forEach((d, i) => {
    if (isBlankDoc(d)) add(`mcq.column_headers[${i}]`, "This field cannot be empty");
  });
  doc.parts.forEach((p, i) => {
    p.mark_points.forEach((m, j) => {
      if (isBlankDoc(m.content)) add(`parts[${i}].mark_points[${j}].content`, "This field cannot be empty");
    });
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

const NON_ENGLISH = /non-English|written in English/i;
const NON_ENGLISH_AT = /found non-English letters at (.+)$/;
const PART_PREFIX = /^(?:Value error, )?part ([a-z](?:\.[ivx]+)?)(?:\s|:)/;

/**
 * Maps what the server returned for a rejected document onto fields. A problem with a `location` (a dotted path into the
 * document, from `document.` on) goes to the nearest editable field; the message shapes are read only for problems that
 * have no location.
 */
export function serverProblems(items: readonly ServerItem[], doc: QuestionDocument): EditProblem[] {
  const out: EditProblem[] = [];
  const seen = new Set<string>();
  const push = (problem: EditProblem) => {
    const key = `${problem.field ?? ""}|${problem.message}`;
    if (seen.has(key)) return;
    seen.add(key);
    out.push(problem);
  };
  for (const item of items) {
    const message = item.message.replace(/^Value error, /, "");
    const english = NON_ENGLISH.test(message);
    if (item.location) {
      const ref = matchField(item.location, doc);
      if (ref) {
        push({ field: ref.field, label: ref.label, message: english ? ENGLISH_MESSAGE : message });
        continue;
      }
      if (normalizePath(item.location) !== "") {
        // A location that no field holds: shown in the summary only, with where it is.
        push({ field: null, label: null, message: english ? ENGLISH_MESSAGE : message });
        continue;
      }
    }
    const found = message.match(NON_ENGLISH_AT);
    if (found) {
      const fields = new Set<string>();
      for (const raw of (found[1] ?? "").split(",")) {
        const path = raw.trim();
        if (!path || path === "...") continue;
        const ref = matchField(path, doc);
        if (!ref || fields.has(ref.field)) continue;
        fields.add(ref.field);
        push({ field: ref.field, label: ref.label, message: ENGLISH_MESSAGE });
      }
      if (fields.size === 0) push({ field: null, label: null, message: ENGLISH_MESSAGE });
      continue;
    }
    const part = item.message.match(PART_PREFIX);
    if (part) {
      const index = doc.parts.findIndex((p) => p.label === part[1]);
      if (index >= 0) {
        const command = /command term/.test(message);
        const ref = matchField(`parts[${index}].${command ? "command_term" : "marks"}`, doc);
        if (ref) {
          push({ field: ref.field, label: ref.label, message });
          continue;
        }
      }
    }
    push({ field: null, label: null, message });
  }
  return out;
}
