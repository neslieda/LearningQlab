"use client";

import type { QuestionDocument } from "@qlab/api-client";
import { OPTION_KEYS, optionCellLabel, updateMcq, updateOption, updateOptionCell, type EditProblem } from "@/lib/edit-document";
import { DocField, ReadOnly, SelectControl, TABLE_BLOCKS } from "./controls";

export interface SectionProps {
  doc: QuestionDocument;
  update: (fn: (d: QuestionDocument) => QuestionDocument) => void;
  problems: readonly EditProblem[];
  /** A new question chooses the option kind and layout above; they are shown as text only when editing. */
  hideShape?: boolean;
}

const AO_OPTIONS = [
  { value: "" as const, text: "Not set" },
  { value: 1 as const, text: "1" },
  { value: 2 as const, text: "2" },
  { value: 3 as const, text: "3" },
];

export function McqSection({ doc, update, problems, hideShape }: SectionProps) {
  const mcq = doc.mcq;
  if (!mcq) return null;
  return (
    <section aria-labelledby="options-heading" className="space-y-4">
      <h2 id="options-heading" className="text-lg font-medium">
        Options
      </h2>
      <div className="space-y-1" hidden={hideShape}>
        <ReadOnly label="Option kind" value={mcq.option_kind.replace(/_/g, " ")} />
        <ReadOnly label="Option layout" value={mcq.option_layout.replace(/_/g, " ")} />
      </div>
      {mcq.column_headers.map((header, i) => (
        <DocField
          key={`h${i}`}
          path={`mcq.column_headers[${i}]`}
          label={`Column header ${i + 1}`}
          value={header}
          problems={problems}
          onChange={(d) => d && update((x) => updateMcq(x, { column_headers: (x.mcq?.column_headers ?? []).map((h, j) => (j === i ? d : h)) }))}
        />
      ))}
      {mcq.statements.map((statement, i) => (
        <DocField
          key={`s${i}`}
          path={`mcq.statements[${i}]`}
          label={`Statement ${i + 1}`}
          value={statement}
          problems={problems}
          onChange={(d) => d && update((x) => updateMcq(x, { statements: (x.mcq?.statements ?? []).map((s, j) => (j === i ? d : s)) }))}
        />
      ))}
      {mcq.options.map((option, i) => (
        <div key={option.key} className="space-y-3 rounded border border-[var(--page-border)] p-3">
          {option.cells.map((cell, j) => (
            <DocField
              key={j}
              path={`mcq.options[${i}].cells[${j}]`}
              label={optionCellLabel(i, j, option.cells.length)}
              value={cell}
              problems={problems}
              onChange={(d) => d && update((x) => updateOptionCell(x, i, j, d))}
            />
          ))}
          <DocField
            path={`mcq.options[${i}].rationale`}
            label={`Rationale for ${OPTION_KEYS[i] ?? option.key}`}
            optional
            value={option.rationale}
            problems={problems}
            onChange={(d) => update((x) => updateOption(x, i, { rationale: d }))}
          />
        </div>
      ))}
      <SelectControl
        path="mcq.correct_key"
        label="Correct option"
        value={mcq.correct_key}
        options={OPTION_KEYS.map((k) => ({ value: k, text: k }))}
        problems={problems}
        onChange={(k) => k && update((x) => updateMcq(x, { correct_key: k }))}
      />
      <SelectControl
        path="mcq.assessment_objective"
        label="Assessment objective"
        value={mcq.assessment_objective ?? ""}
        options={AO_OPTIONS}
        problems={problems}
        onChange={(v) => update((x) => updateMcq(x, { assessment_objective: v === "" ? null : v }))}
      />
      <DocField
        path="mcq.explanation"
        label="Explanation"
        optional
        value={mcq.explanation}
        blocks={TABLE_BLOCKS}
        problems={problems}
        onChange={(d) => update((x) => updateMcq(x, { explanation: d }))}
      />
    </section>
  );
}
