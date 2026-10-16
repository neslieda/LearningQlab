"use client";

import type { QuestionDocument } from "@qlab/api-client";
import { DocView } from "./DocView";
import { MarkSchemeView } from "./MarkSchemeView";
import { QuestionLayout, type LayoutQuestion } from "./QuestionLayout";
import type { MarkPointOut, NoteOut } from "./types";

export interface QuestionDocumentViewProps {
  document: QuestionDocument;
  showAnswers: boolean;
}

function toLayout(document: QuestionDocument): LayoutQuestion {
  return {
    examSection: document.exam_section,
    levels: document.levels,
    totalMarks: document.total_marks,
    stem: document.stem,
    stimuli: document.stimuli.map((s) => ({ id: s.id, kind: s.kind, description: s.description })),
    parts: document.parts.map((p) => ({
      id: p.id,
      label: p.label,
      marks: p.marks,
      leadIn: p.lead_in,
      body: p.body,
    })),
    mcq: document.mcq
      ? {
          layout: document.mcq.option_layout,
          columnHeaders: document.mcq.column_headers,
          statements: document.mcq.statements,
          options: document.mcq.options.map((o) => ({ key: o.key, cells: o.cells })),
        }
      : null,
  };
}

/** Staff view of a whole document. With `showAnswers`: correct option, rationales, explanation, mark points, notes. */
export function QuestionDocumentView({ document, showAnswers }: QuestionDocumentViewProps) {
  const partsById = new Map(document.parts.map((p) => [p.id, p]));
  const mcq = document.mcq;

  const answers =
    showAnswers && mcq ? (
      <div className="qr-staff-answers">
        {mcq.options.some((o) => o.rationale) && (
          <div className="qr-rationales" role="group" aria-label="Rationales">
            <p className="qr-staff-title">Rationales</p>
            <ul>
              {mcq.options.map((option) =>
                option.rationale ? (
                  <li key={option.key}>
                    <span className="qr-option-key">{option.key}</span>
                    <div className="qr-rationale-body">
                      <DocView doc={option.rationale} />
                    </div>
                  </li>
                ) : null,
              )}
            </ul>
          </div>
        )}
        {mcq.explanation && (
          <div className="qr-explanation" role="group" aria-label="Explanation">
            <p className="qr-staff-title">Explanation</p>
            <DocView doc={mcq.explanation} />
          </div>
        )}
      </div>
    ) : null;

  return (
    <QuestionLayout
      question={toLayout(document)}
      showDescriptions
      correctKey={showAnswers && mcq ? mcq.correct_key : null}
      renderPartFooter={
        showAnswers
          ? (id) => {
              const part = partsById.get(id);
              if (!part) return null;
              const markPoints: MarkPointOut[] = part.mark_points.map((m) => ({
                id: m.id,
                content: m.content,
                kind: m.kind,
                route: m.route ?? null,
                alternative_group: m.alternative_group ?? null,
                accept_range: m.accept_range ?? null,
              }));
              const notes: NoteOut[] = part.notes.map((n) => ({
                content: n.content,
                kind: n.kind,
                mark_point_id: n.mark_point_id ?? null,
              }));
              return (
                <MarkSchemeView
                  markPoints={markPoints}
                  notes={notes}
                  marks={part.marks}
                  marksCapped={part.marks_capped}
                />
              );
            }
          : undefined
      }
      after={answers}
    />
  );
}
