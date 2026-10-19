"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AnswerRequest, LearnerQuestion, McqResult, ResponsePage, WrittenResult } from "@qlab/api-client";
import {
  LearnerQuestionView,
  MarkSchemeView,
  McqExplanation,
  type LearnerPart,
} from "@qlab/question-renderer";
import { formatTime, unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import { excerpt, partLabel, partLabeller, toAnswerRows } from "@/lib/learn";
import { QUESTIONS_KEY, RESPONSES_KEY } from "@/lib/responses";
import { SessionGate } from "../../admin/staff-gate";
import { AnswerProblem } from "../answer-problem";
import { PrivacyNotice } from "../privacy-notice";

type Key = "A" | "B" | "C" | "D";

export function Solve({ id }: { id: string }) {
  return <SessionGate allowed={() => true} denied="">{() => <Inner id={id} />}</SessionGate>;
}

function useSubmit(questionId: string) {
  const api = useApi();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: AnswerRequest) =>
      unwrap(await api.POST("/v1/questions/{question_id}/answers", { params: { path: { question_id: questionId } }, body })),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: RESPONSES_KEY });
      void queryClient.invalidateQueries({ queryKey: QUESTIONS_KEY });
    },
  });
}

function Inner({ id }: { id: string }) {
  const api = useApi();
  const query = useQuery({
    queryKey: ["learn", "question", id],
    queryFn: async (): Promise<LearnerQuestion> =>
      unwrap(await api.GET("/v1/questions/{question_id}", { params: { path: { question_id: id } } })),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Practice question</h1>
        <Link href="/learn" className="underline">
          Back to questions
        </Link>
      </div>
      {query.isPending ? <p>Loading...</p> : null}
      {query.isError ? <AnswerProblem error={query.error} onReload={() => void query.refetch()} /> : null}
      {query.data ? (
        <>
          <p data-testid="topic">
            <span className="font-medium">Topic:</span> {query.data.topic.code} {query.data.topic.title}
          </p>
          <Question question={query.data} />
          <PreviousAnswers question={query.data} />
          <PrivacyNotice />
        </>
      ) : null}
    </div>
  );
}

function Question({ question }: { question: LearnerQuestion }) {
  return question.mcq ? <McqSolve question={question} /> : <StructuredSolve question={question} />;
}

function McqSolve({ question }: { question: LearnerQuestion }) {
  const submit = useSubmit(question.id);
  const [selected, setSelected] = useState<Key | null>(null);
  const [result, setResult] = useState<McqResult | null>(null);
  const box = useRef<HTMLDivElement>(null);

  function onSubmit() {
    if (!selected) return;
    submit.mutate(
      { kind: "mcq", selected_key: selected },
      { onSuccess: (r) => setResult(r.kind === "mcq" ? r : null) },
    );
  }
  function tryAgain() {
    setResult(null);
    setSelected(null);
    submit.reset();
    window.setTimeout(() => box.current?.querySelector<HTMLInputElement>('input[type="radio"]')?.focus(), 0);
  }

  const locked = result !== null;
  return (
    <div ref={box}>
      <LearnerQuestionView
        question={question}
        mcqAnswer={{
          value: selected,
          onChange: setSelected,
          disabled: locked || submit.isPending,
          correctKey: result?.correct_key,
          rationales: result?.rationales,
        }}
        renderMcqFooter={() => (
          <div className="space-y-3">
            {!locked ? (
              <button
                type="button"
                onClick={onSubmit}
                disabled={!selected || submit.isPending}
                className="rounded border border-[var(--page-border)] px-3 py-1.5 disabled:opacity-60"
              >
                Submit answer
              </button>
            ) : (
              <button type="button" onClick={tryAgain} className="rounded border border-[var(--page-border)] px-3 py-1.5">
                Try again
              </button>
            )}
            <div role="status" aria-live="polite" data-testid="mcq-result">
              {result ? (
                <p className="font-medium">
                  {result.correct ? "Correct." : "Not correct."} The correct answer is {result.correct_key}.
                </p>
              ) : null}
            </div>
            {result ? <McqExplanation explanation={result.explanation} /> : null}
            <AnswerProblem error={submit.error} />
          </div>
        )}
      />
    </div>
  );
}

function StructuredSolve({ question }: { question: LearnerQuestion }) {
  return <LearnerQuestionView question={question} renderPartFooter={(part) => <PartAnswer questionId={question.id} part={part} />} />;
}

function PartAnswer({ questionId, part }: { questionId: string; part: LearnerPart }) {
  const submit = useSubmit(questionId);
  const [text, setText] = useState("");
  const [result, setResult] = useState<WrittenResult | null>(null);
  const area = useRef<HTMLTextAreaElement>(null);
  const label = partLabel(part.label);
  const locked = result !== null;

  function onSubmit() {
    submit.mutate(
      { kind: "written", part_id: part.id, text },
      { onSuccess: (r) => setResult(r.kind === "written" ? r : null) },
    );
  }
  function tryAgain() {
    setResult(null);
    setText("");
    submit.reset();
    window.setTimeout(() => area.current?.focus(), 0);
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm">
        <span className="block font-medium">{`Answer for ${label}`}</span>
        <textarea
          ref={area}
          value={text}
          onChange={(e) => setText(e.target.value)}
          readOnly={locked || submit.isPending}
          aria-readonly={locked || undefined}
          rows={5}
          className="w-full max-w-full rounded border border-[var(--page-border)] bg-transparent p-2 read-only:opacity-80"
        />
      </label>
      {!locked ? (
        <button
          type="button"
          onClick={onSubmit}
          disabled={text.trim() === "" || submit.isPending}
          className="rounded border border-[var(--page-border)] px-3 py-1.5 disabled:opacity-60"
        >
          {`Submit answer for ${label}`}
        </button>
      ) : (
        <button type="button" onClick={tryAgain} className="rounded border border-[var(--page-border)] px-3 py-1.5">
          {`Try again for ${label}`}
        </button>
      )}
      <div role="status" aria-live="polite">
        {result ? <p className="font-medium">{`Your answer for ${label} was saved. Compare it with the mark scheme below.`}</p> : null}
      </div>
      {result?.language_warning ? (
        <p role="note" className="rounded border border-amber-600 p-2 text-sm">
          {result.language_warning.message}
        </p>
      ) : null}
      {result ? (
        <MarkSchemeView markPoints={result.mark_points} notes={result.notes} marks={result.marks} marksCapped={result.marks_capped} />
      ) : null}
      <AnswerProblem error={submit.error} />
    </div>
  );
}

function PreviousAnswers({ question }: { question: LearnerQuestion }) {
  const api = useApi();
  const query = useInfiniteQuery({
    queryKey: [...RESPONSES_KEY, "question", question.id],
    initialPageParam: null as string | null,
    queryFn: async ({ pageParam }): Promise<ResponsePage> =>
      unwrap(
        await api.GET("/v1/me/responses", {
          params: { query: { question_id: question.id, cursor: pageParam ?? undefined, limit: 20 } },
        }),
      ),
    getNextPageParam: (last) => last.next_cursor,
  });
  const rows = toAnswerRows(query.data?.pages.flatMap((p) => p.items) ?? [], partLabeller(question));

  return (
    <section aria-labelledby="previous-answers" className="space-y-2">
      <h2 id="previous-answers" className="text-lg font-medium">
        Your previous answers
      </h2>
      {query.isPending ? <p>Loading...</p> : null}
      {query.isError ? <AnswerProblem error={query.error} onReload={() => void query.refetch()} /> : null}
      {query.isSuccess && rows.length === 0 ? <p>You have not answered this question yet.</p> : null}
      {rows.length > 0 ? (
        <ul className="space-y-2">
          {rows.map((r) => (
            <li key={r.id} className="rounded border border-[var(--page-border)] p-2 text-sm">
              <p>
                <span className="font-medium">{r.what}</span>
                {r.outcome ? <span>{` - ${r.outcome}`}</span> : null}
                <span className="text-[var(--page-muted)]">{` - ${formatTime(r.createdAt)}`}</span>
              </p>
              {r.kind === "written" ? <p className="break-words">{excerpt(r.answer)}</p> : null}
            </li>
          ))}
        </ul>
      ) : null}
      {query.hasNextPage ? (
        <button
          type="button"
          onClick={() => void query.fetchNextPage()}
          disabled={query.isFetchingNextPage}
          className="rounded border border-[var(--page-border)] px-3 py-1.5"
        >
          Load more
        </button>
      ) : null}
    </section>
  );
}
