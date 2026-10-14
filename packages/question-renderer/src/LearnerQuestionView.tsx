import type { ReactNode } from "react";
import type { LearnerQuestion } from "@qlab/api-client";
import { QuestionLayout, type LayoutQuestion } from "./QuestionLayout";
import type { LearnerPart } from "./types";

export interface LearnerQuestionViewProps {
  question: LearnerQuestion;
  /** Slice 8's answer fields go here. */
  renderPartFooter?: (part: LearnerPart) => ReactNode;
  renderMcqFooter?: () => ReactNode;
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
export function LearnerQuestionView({ question, renderPartFooter, renderMcqFooter }: LearnerQuestionViewProps) {
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
    />
  );
}
