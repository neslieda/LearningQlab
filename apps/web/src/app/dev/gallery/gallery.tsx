"use client";

import {
  DocView,
  LearnerQuestionView,
  MarkSchemeView,
  McqResultView,
  QuestionDocumentView,
  fixtures,
  type Fixture,
} from "@qlab/question-renderer";

function Render({ fixture }: { fixture: Fixture }) {
  switch (fixture.kind) {
    case "learner_question":
      return <LearnerQuestionView question={fixture.data} />;
    case "doc":
      return <DocView doc={fixture.data} />;
    case "markscheme":
      return (
        <MarkSchemeView
          markPoints={fixture.data.markPoints}
          notes={fixture.data.notes}
          marks={fixture.data.marks}
          marksCapped={fixture.data.marksCapped}
        />
      );
    case "staff_question":
      return <QuestionDocumentView document={fixture.data.document} showAnswers={fixture.data.showAnswers} />;
    case "mcq_result":
      return <McqResultView result={fixture.data.result} question={fixture.data.question} />;
  }
}

export function Gallery() {
  return (
    <div className="space-y-10">
      <h1 className="text-2xl font-semibold">Renderer gallery</h1>
      {fixtures.map((fixture) => (
        <section key={fixture.id} data-testid={`fixture-${fixture.id}`} aria-labelledby={`h-${fixture.id}`} className="space-y-3">
          <h2 id={`h-${fixture.id}`} className="text-lg font-medium">
            {fixture.title}
          </h2>
          <Render fixture={fixture} />
        </section>
      ))}
    </div>
  );
}
