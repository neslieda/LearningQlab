"use client";

import type { ReactNode } from "react";
import type { Doc, LearnerQuestion } from "@qlab/api-client";
import { QuestionLayout, type LayoutQuestion, type McqSelect } from "./QuestionLayout";
import type { LearnerPart, OptionKey } from "./types";

export type McqChoice = McqSelect;

/** What the solve screen adds to a multiple-choice question: a selection, and after submitting the result. */
export interface McqAnswerState extends McqChoice {
  correctKey?: OptionKey | null;
  rationales?: { key: OptionKey; content: Doc }[];
}

export interface LearnerQuestionViewProps {
  question: LearnerQuestion;
  /** Slice 8's answer fields go here. */
  renderPartFooter?: (part: LearnerPart) => ReactNode;
  renderMcqFooter?: () => ReactNode;
  /** Makes the options selectable (radiogroup); after a submit, marks the correct option and shows the rationales. */
  mcqAnswer?: McqAnswerState;
}

export function toLayout(question: LearnerQuestion): LayoutQuestion {
  return {
    examSection: question.exam_section,
    levels: question.levels,
    totalMarks: question.total_marks,
    stem: question.stem,
    // Learner stimuli carry no description.
    stimuli: question.stimuli.map((s) => ({ id: s.id, kind: s.kind })),
    parts: question.parts.map((p) => ({
      id: p.id,
      label: p.label,
      marks: p.marks,
      leadIn: p.lead_in,
      body: p.body,
    })),
    mcq: question.mcq
      ? {
          layout: question.mcq.option_layout,
          columnHeaders: question.mcq.column_headers,
          statements: question.mcq.statements,
          options: question.mcq.options.map((o) => ({ key: o.key, cells: o.cells })),
        }
      : null,
  };
}

/** The question as a learner sees it, in exam layout. */
export function LearnerQuestionView({ question, renderPartFooter, renderMcqFooter, mcqAnswer }: LearnerQuestionViewProps) {
  const partsById = new Map(question.parts.map((p) => [p.id, p]));
  return (
    <QuestionLayout
      question={toLayout(question)}
      showDescriptions={false}
      renderPartFooter={
        renderPartFooter
          ? (id) => {
              const part = partsById.get(id);
              return part ? renderPartFooter(part) : null;
            }
          : undefined
      }
      mcqFooter={renderMcqFooter?.()}
      correctKey={mcqAnswer?.correctKey}
      mcqSelect={mcqAnswer}
      rationales={mcqAnswer?.rationales ? rationaleMap(mcqAnswer.rationales) : undefined}
    />
  );
}

export function rationaleMap(rationales: { key: OptionKey; content: Doc }[]): Partial<Record<OptionKey, Doc>> {
  const map: Partial<Record<OptionKey, Doc>> = {};
  for (const r of rationales) map[r.key] = r.content;
  return map;
}
