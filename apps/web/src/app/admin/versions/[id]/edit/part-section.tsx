"use client";

import type { QuestionDocument } from "@qlab/api-client";
import {
  MAX_PART_MARKS,
  MIN_PART_MARKS,
  addMarkPoint,
  addNote,
  moveMarkPoint,
  moveNote,
  partTag,
  notesPointingAt,
  removeMarkPoint,
  removeNote,
  setPartMarks,
  updateMarkPoint,
  updateNote,
  updatePart,
  type EditProblem,
  type Part,
} from "@/lib/edit-document";
import { BTN, CheckControl, DocField, FieldShell, MARKSCHEME_MARKS, SelectControl, TABLE_BLOCKS, TextControl } from "./controls";

type AnswerType = Part["answer_type"];
type PointKind = Part["mark_points"][number]["kind"];
type NoteKind = Part["notes"][number]["kind"];

const ANSWER_TYPES: AnswerType[] = [
  "numeric_with_unit",
  "numeric_unitless",
  "value_from_graph",
  "unit",
  "algebraic_expression",
  "symbolic_equation",
  "word_phrase",
  "explanation",
  "judgement_justified",
  "extended_evaluation",
  "derivation_algebraic",
  "derivation_numeric",
  "drawing_on_diagram",
  "graph_sketch",
];
const POINT_KINDS: PointKind[] = ["method", "answer", "statement"];
const NOTE_KINDS: NoteKind[] = ["general", "owtte", "accept", "do_not_accept", "cap", "ecf"];
const words = (s: string) => s.replace(/_/g, " ");
const MARK_OPTIONS = Array.from({ length: MAX_PART_MARKS - MIN_PART_MARKS + 1 }, (_, i) => ({ value: MIN_PART_MARKS + i, text: String(MIN_PART_MARKS + i) }));

export interface PartSectionProps {
  doc: QuestionDocument;
  index: number;
  update: (fn: (d: QuestionDocument) => QuestionDocument) => void;
  problems: readonly EditProblem[];
  commandTerms: readonly string[];
  /** Announces something the user should know about (visible and read out). */
  notify: (message: string) => void;
}

export function PartSection({ doc, index, update, problems, commandTerms, notify }: PartSectionProps) {
  const part = doc.parts[index];
  if (!part) return null;
  const tag = partTag(part.label);
  const base = `parts[${index}]`;
  const patch = (p: Partial<Part>) => update((d) => updatePart(d, index, p));
  const terms = part.command_term && !commandTerms.includes(part.command_term) ? [part.command_term, ...commandTerms] : commandTerms;
  const earlier = doc.parts.slice(0, index);

  return (
    <section aria-labelledby={`part-${index}-heading`} className="space-y-4 rounded border border-[var(--page-border)] p-4">
      <h2 id={`part-${index}-heading`} className="text-lg font-medium">
        Part {tag}
      </h2>
      <DocField path={`${base}.lead_in`} label={`Part ${tag} lead-in`} optional value={part.lead_in} blocks={TABLE_BLOCKS} problems={problems} onChange={(d) => patch({ lead_in: d })} />
      <DocField path={`${base}.body`} label={`Part ${tag} body`} value={part.body} blocks={TABLE_BLOCKS} problems={problems} onChange={(d) => d && patch({ body: d })} />

      <div className="grid gap-4 sm:grid-cols-2">
        <SelectControl
          path={`${base}.marks`}
          label={`Part ${tag} marks`}
          value={part.marks}
          options={MARK_OPTIONS}
          problems={problems}
          onChange={(v) => v !== "" && update((d) => setPartMarks(d, index, Number(v)))}
        />
        <SelectControl
          path={`${base}.command_term`}
          label={`Part ${tag} command term`}
          value={part.command_term ?? ""}
          options={[{ value: "", text: "None" }, ...terms.map((t) => ({ value: t, text: words(t) }))]}
          problems={problems}
          onChange={(v) => patch({ command_term: v === "" ? null : String(v) })}
        />
        <SelectControl
          path={`${base}.answer_type`}
          label={`Part ${tag} answer type`}
          value={part.answer_type}
          options={ANSWER_TYPES.map((t) => ({ value: t, text: words(t) }))}
          problems={problems}
          onChange={(v) => v !== "" && patch({ answer_type: v as AnswerType })}
        />
        <SelectControl
          path={`${base}.assessment_objective`}
          label={`Part ${tag} assessment objective`}
          value={part.assessment_objective ?? ""}
          options={[{ value: "", text: "Not set" }, { value: 1, text: "1" }, { value: 2, text: "2" }, { value: 3, text: "3" }]}
          problems={problems}
          onChange={(v) => patch({ assessment_objective: v === "" ? null : (Number(v) as 1 | 2 | 3) })}
        />
      </div>
      <div className="flex flex-wrap gap-x-6 gap-y-2">
        <CheckControl path={`${base}.marks_capped`} label={`Part ${tag} marks capped`} checked={part.marks_capped} problems={problems} onChange={(v) => patch({ marks_capped: v })} />
        <CheckControl path={`${base}.show_that`} label={`Part ${tag} show that`} checked={part.show_that} problems={problems} onChange={(v) => patch({ show_that: v })} />
      </div>
      {earlier.length > 0 ? (
        <FieldShell path={`${base}.ecf_from`} problems={problems}>
          {(describedBy) => (
            <fieldset className="space-y-1" aria-describedby={describedBy}>
              <legend className="font-medium">Error carried forward into part {tag}</legend>
              <div className="flex flex-wrap gap-x-6 gap-y-1">
                {earlier.map((p) => (
                  <CheckControl
                    key={p.id}
                    path={`${base}.ecf_from.${p.id}`}
                    label={`From part ${partTag(p.label)}`}
                    checked={part.ecf_from.includes(p.id)}
                    problems={problems}
                    onChange={(on) => patch({ ecf_from: on ? [...part.ecf_from, p.id] : part.ecf_from.filter((x) => x !== p.id) })}
                  />
                ))}
              </div>
            </fieldset>
          )}
        </FieldShell>
      ) : null}

      <div className="space-y-4">
        <h3 className="font-medium">Mark scheme for part {tag}</h3>
        {part.mark_points.map((point, j) => {
          const n = j + 1;
          return (
            <div key={point.id} className="space-y-2 rounded border border-[var(--page-border)] p-3">
              <DocField
                path={`${base}.mark_points[${j}].content`}
                label={`Mark point ${n}`}
                value={point.content}
                marks={MARKSCHEME_MARKS}
                problems={problems}
                onChange={(d) => d && update((x) => updateMarkPoint(x, index, j, { content: d }))}
              />
              <div className="grid gap-3 sm:grid-cols-3">
                <SelectControl
                  path={`${base}.mark_points[${j}].kind`}
                  label={`Kind of point ${n}`}
                  value={point.kind}
                  options={POINT_KINDS.map((k) => ({ value: k, text: k }))}
                  problems={problems}
                  onChange={(v) => v !== "" && update((x) => updateMarkPoint(x, index, j, { kind: v as PointKind }))}
                />
                <TextControl
                  path={`${base}.mark_points[${j}].alternative_group`}
                  label={`Alternative group, point ${n}`}
                  value={point.alternative_group ?? ""}
                  problems={problems}
                  onChange={(v) => update((x) => updateMarkPoint(x, index, j, { alternative_group: v.trim() === "" ? null : v.trim() }))}
                />
                <TextControl
                  path={`${base}.mark_points[${j}].route`}
                  label={`Route, point ${n}`}
                  value={point.route ?? ""}
                  problems={problems}
                  onChange={(v) => update((x) => updateMarkPoint(x, index, j, { route: v.trim() === "" ? null : v.trim() }))}
                />
              </div>
              <div className="flex flex-wrap gap-2">
                <button type="button" className={BTN} disabled={j === 0} aria-label={`Move mark point ${n} up`} onClick={() => update((x) => moveMarkPoint(x, index, j, -1))}>
                  Up
                </button>
                <button type="button" className={BTN} disabled={j === part.mark_points.length - 1} aria-label={`Move mark point ${n} down`} onClick={() => update((x) => moveMarkPoint(x, index, j, 1))}>
                  Down
                </button>
                <button type="button" className={BTN} disabled={part.mark_points.length <= 1} aria-label={`Remove mark point ${n}`} onClick={() => {
                    const rebound = notesPointingAt(doc, index, j);
                    if (rebound > 0) notify(`Removing mark point ${n} changed ${rebound} ${rebound === 1 ? "note" : "notes"} to apply to the whole part.`);
                    update((x) => removeMarkPoint(x, index, j));
                  }}>
                  Remove
                </button>
              </div>
            </div>
          );
        })}
        <button type="button" className={BTN} onClick={() => update((x) => addMarkPoint(x, index))}>
          Add mark point
        </button>
      </div>

      <div className="space-y-4">
        <h3 className="font-medium">Notes for part {tag}</h3>
        {part.notes.map((note, j) => {
          const n = j + 1;
          return (
            <div key={j} className="space-y-2 rounded border border-[var(--page-border)] p-3">
              <DocField
                path={`${base}.notes[${j}].content`}
                label={`Note ${n}`}
                value={note.content}
                marks={MARKSCHEME_MARKS}
                problems={problems}
                onChange={(d) => d && update((x) => updateNote(x, index, j, { content: d }))}
              />
              <div className="grid gap-3 sm:grid-cols-2">
                <SelectControl
                  path={`${base}.notes[${j}].kind`}
                  label={`Kind of note ${n}`}
                  value={note.kind}
                  options={NOTE_KINDS.map((k) => ({ value: k, text: words(k) }))}
                  problems={problems}
                  onChange={(v) => v !== "" && update((x) => updateNote(x, index, j, { kind: v as NoteKind }))}
                />
                <SelectControl
                  path={`${base}.notes[${j}].mark_point_id`}
                  label={`Applies to, note ${n}`}
                  value={note.mark_point_id ?? ""}
                  options={[{ value: "", text: "Whole part" }, ...part.mark_points.map((m, k) => ({ value: m.id, text: `Mark point ${k + 1}` }))]}
                  problems={problems}
                  onChange={(v) => update((x) => updateNote(x, index, j, { mark_point_id: v === "" ? null : String(v) }))}
                />
              </div>
              <div className="flex flex-wrap gap-2">
                <button type="button" className={BTN} disabled={j === 0} aria-label={`Move note ${n} up`} onClick={() => update((x) => moveNote(x, index, j, -1))}>
                  Up
                </button>
                <button type="button" className={BTN} disabled={j === part.notes.length - 1} aria-label={`Move note ${n} down`} onClick={() => update((x) => moveNote(x, index, j, 1))}>
                  Down
                </button>
                <button type="button" className={BTN} aria-label={`Remove note ${n}`} onClick={() => update((x) => removeNote(x, index, j))}>
                  Remove
                </button>
              </div>
            </div>
          );
        })}
        <button type="button" className={BTN} onClick={() => update((x) => addNote(x, index))}>
          Add note
        </button>
      </div>
    </section>
  );
}
