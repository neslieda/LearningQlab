"use client";

import type { LearnerQuestion, McqCheckResult } from "@qlab/api-client";
import { toLayout } from "./LearnerQuestionView";
import { McqBlock } from "./QuestionLayout";
import { StimuliContext } from "./context";
import { useMemo } from "react";

export interface McqResultViewProps {
  result: McqCheckResult;
  question: LearnerQuestion;
}

/** The question's options with the correct one marked (by text, not by colour alone). */
export function McqResultView({ result, question }: McqResultViewProps) {
  const layout = useMemo(() => toLayout(question), [question]);
  const context = useMemo(
    () => ({ stimuli: new Map(layout.stimuli.map((s) => [s.id, s])), showDescription: false }),
    [layout],
  );
  if (!layout.mcq) return null;
  return (
    <StimuliContext.Provider value={context}>
      <div className="qr qr-mcq-result">
        <McqBlock mcq={layout.mcq} correctKey={result.correct_key} />
      </div>
    </StimuliContext.Provider>
  );
}
