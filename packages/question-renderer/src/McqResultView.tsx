"use client";

import type { LearnerQuestion, McqResult } from "@qlab/api-client";
import { rationaleMap, toLayout } from "./LearnerQuestionView";
import { McqBlock } from "./QuestionLayout";
import { DocView } from "./DocView";
import { StimuliContext } from "./context";
import { useMemo } from "react";

export interface McqResultViewProps {
  result: McqResult;
  question: LearnerQuestion;
}

/** The explanation block. Renders nothing when the question has none. */
export function McqExplanation({ explanation }: { explanation: McqResult["explanation"] }) {
  if (!explanation) return null;
  return (
    <section className="qr-explanation" aria-label="Explanation">
      <p className="qr-explanation-title">Explanation</p>
      <DocView doc={explanation} />
    </section>
  );
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
        <McqBlock mcq={layout.mcq} correctKey={result.correct_key} rationales={rationaleMap(result.rationales)} />
        <McqExplanation explanation={result.explanation} />
      </div>
    </StimuliContext.Provider>
  );
}
