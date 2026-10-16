"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import type { AdminVersion, QuestionDocument } from "@qlab/api-client";
import { QuestionDocumentView } from "@qlab/question-renderer";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import {
  clientProblems,
  serverProblems,
  totalMarks,
  type EditProblem,
} from "@/lib/edit-document";
import { ProblemView } from "../../../problem-view";
import { ScrollBox } from "../../../status-badge";
import { BTN, CheckControl, DocField, ReadOnly, SelectControl, TABLE_BLOCKS, TextControl, focusField } from "./controls";
import { McqSection } from "./mcq-section";
import { PartSection } from "./part-section";
import { useLeaveGuard } from "./use-leave-guard";

// The only programme this slice edits. The version does not carry its programme, so the vocabulary is fetched for it.
const PROGRAM = "ib_dp";
const SUBJECT = "physics";

const DIFFICULTIES = [
  { value: "" as const, text: "Not set" },
  { value: "easy" as const, text: "easy" },
  { value: "medium" as const, text: "medium" },
  { value: "hard" as const, text: "hard" },
];

export interface EditorFormProps {
  version: AdminVersion;
  /** Throws away the form and loads the stored version again. */
  onReload: () => void;
}

type Tab = "form" | "preview";

export function EditorForm({ version, onReload }: EditorFormProps) {
  const api = useApi();
  const queryClient = useQueryClient();
  const id = version.id;

  const [doc, setDoc] = useState<QuestionDocument>(version.document);
  // What the stored content is, as far as this page knows: the document it started from (or last saved) and its digest.
  const [saved, setSaved] = useState<{ json: string; sha: string }>(() => ({ json: JSON.stringify(version.document), sha: version.content_sha256 }));
  const [tab, setTab] = useState<Tab>("form");
  const [problems, setProblems] = useState<EditProblem[]>([]);
  const [attempt, setAttempt] = useState(0);
  const [error, setError] = useState<unknown>(null);
  const [stale, setStale] = useState(false);
  const [locked, setLocked] = useState(false);
  const [announce, setAnnounce] = useState("");
  const [notice, setNotice] = useState("");
  const submitting = useRef(false);
  const summary = useRef<HTMLDivElement>(null);

  const dirty = useMemo(() => JSON.stringify(doc) !== saved.json, [doc, saved.json]);
  useLeaveGuard(dirty);

  const syllabus = useQuery({
    queryKey: ["syllabus", PROGRAM, SUBJECT],
    enabled: doc.parts.length > 0,
    queryFn: async () => unwrap(await api.GET("/v1/programs/{program}/subjects/{subject}/syllabus", { params: { path: { program: PROGRAM, subject: SUBJECT } } })),
  });
  const commandTerms = syllabus.data?.command_terms ?? [];

  const update = (fn: (d: QuestionDocument) => QuestionDocument) => {
    setDoc((prev) => fn(prev));
    setAnnounce("");
  };

  const save = useMutation({
    mutationFn: async ({ document, sha }: { document: QuestionDocument; sha: string }) =>
      unwrap(
        await api.PUT("/v1/admin/question-versions/{version_id}", {
          params: { path: { version_id: id } },
          body: { document, expected_content_sha256: sha },
        }),
      ),
    onSuccess: async (result, vars) => {
      setError(null);
      setProblems([]);
      setStale(false);
      setSaved({ json: JSON.stringify(vars.document), sha: result.content_sha256 });
      setAnnounce("Saved");
      setNotice("");
      queryClient.setQueryData(["admin", "version", id], result);
      await queryClient.invalidateQueries({ queryKey: ["admin"] });
    },
    onError: (e, vars) => {
      const problem = e instanceof ApiError ? e.problem : null;
      if (problem?.status === 409 && problem.code === "stale_content") {
        setStale(true);
        setError(null);
      } else if (problem?.status === 422 && (problem.code === "invalid_document" || problem.code === "validation_failed")) {
        setProblems(serverProblems((problem.errors ?? []).map((x) => ({ code: x.code, message: x.message ?? x.code, location: x.location })), vars.document));
        setAttempt((n) => n + 1);
        setTab("form");
        setError(null);
      } else {
        setError(e);
      }
    },
    onSettled: () => {
      submitting.current = false;
      setLocked(false);
    },
  });

  useEffect(() => {
    if (attempt > 0) summary.current?.focus();
  }, [attempt]);

  function onSave() {
    if (submitting.current) return;
    setAnnounce("");
    setError(null);
    const found = clientProblems(doc);
    if (found.length > 0) {
      setProblems(found);
      setAttempt((n) => n + 1);
      setTab("form");
      return;
    }
    setProblems([]);
    submitting.current = true;
    setLocked(true);
    save.mutate({ document: doc, sha: saved.sha });
  }

  const problem = error instanceof ApiError ? error.problem : null;
  const cannotEdit = problem?.code === "invalid_transition";

  return (
    <form
      className="space-y-6"
      // Only the Save button saves: Enter in a text input must not submit the form.
      onSubmit={(e) => e.preventDefault()}
      noValidate
    >
      <p>
        <Link href={`/admin/versions/${id}`} className="underline">
          Back to version
        </Link>
      </p>
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold">Edit version {version.version_no}</h1>
        <div className="flex flex-wrap gap-2" role="group" aria-label="View">
          <button type="button" className={BTN} aria-pressed={tab === "form"} onClick={() => setTab("form")}>
            Form
          </button>
          <button type="button" className={BTN} aria-pressed={tab === "preview"} onClick={() => setTab("preview")}>
            Preview
          </button>
        </div>
      </header>

      {problems.length > 0 ? (
        <div ref={summary} role="alert" tabIndex={-1} className="space-y-2 rounded border border-red-700 p-3">
          <p className="font-medium">These problems must be fixed before the version can be saved</p>
          <ul className="list-disc pl-5">
            {problems.map((p, i) => (
              <li key={i}>
                {p.field && p.label ? (
                  <button type="button" className="underline" onClick={() => { setTab("form"); setTimeout(() => focusField(p.field as string), 0); }}>
                    {p.label}
                  </button>
                ) : null}
                {p.field && p.label ? ": " : ""}
                {p.message}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {stale ? (
        <div role="alert" className="space-y-2 rounded border border-red-700 p-3">
          <p>Someone else saved this version while you were editing. Your changes are still here; copy what you need, then reload.</p>
          <button type="button" className={BTN} onClick={onReload}>
            Reload (discards your changes)
          </button>
        </div>
      ) : null}

      {cannotEdit ? (
        <div role="alert" className="space-y-2 rounded border border-red-700 p-3">
          <p>This version can no longer be edited</p>
          <Link href={`/admin/versions/${id}`} className="underline">
            Go to the version
          </Link>
        </div>
      ) : (
        <ProblemView error={error} questionId={version.question_id} onReload={onReload} />
      )}

      <div hidden={tab !== "form"} className="space-y-8">
        <section aria-labelledby="details-heading" className="space-y-4">
          <h2 id="details-heading" className="text-lg font-medium">
            Details
          </h2>
          <div className="space-y-1">
            <ReadOnly label="Question class" value={doc.question_class.replace(/_/g, " ")} />
            <ReadOnly label="Exam section" value={doc.exam_section} />
            <ReadOnly label="Syllabus node" value={[doc.primary_syllabus_node, ...doc.secondary_syllabus_nodes].join(", ")} />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <SelectControl
              path="difficulty"
              label="Difficulty"
              value={doc.difficulty ?? ""}
              options={DIFFICULTIES}
              problems={problems}
              onChange={(v) => update((d) => ({ ...d, difficulty: v === "" ? null : v }))}
            />
            <div className="space-y-2">
              <CheckControl path="calculator" label="Calculator allowed" checked={doc.calculator} problems={problems} onChange={(v) => update((d) => ({ ...d, calculator: v }))} />
              <fieldset className="space-y-1">
                <legend className="font-medium">Levels</legend>
                <div className="flex gap-6">
                  {(["sl", "hl"] as const).map((level) => (
                    <CheckControl
                      key={level}
                      path={level === "sl" ? "levels" : "levels.hl"}
                      label={level.toUpperCase()}
                      checked={doc.levels.includes(level)}
                      problems={problems}
                      onChange={(on) =>
                        update((d) => ({ ...d, levels: (["sl", "hl"] as const).filter((l) => (l === level ? on : d.levels.includes(l))) }))
                      }
                    />
                  ))}
                </div>
              </fieldset>
            </div>
          </div>
          <TextControl path="outcome" label="Outcome" multiline value={doc.outcome ?? ""} problems={problems} onChange={(v) => update((d) => ({ ...d, outcome: v.trim() === "" ? null : v }))} />
        </section>

        <section aria-labelledby="question-heading" className="space-y-4">
          <h2 id="question-heading" className="text-lg font-medium">
            Question
          </h2>
          <DocField path="stem" label="Stem" value={doc.stem} blocks={TABLE_BLOCKS} problems={problems} onChange={(d) => d && update((x) => ({ ...x, stem: d }))} />
        </section>

        {doc.stimuli.length > 0 ? (
          <section aria-labelledby="stimuli-heading" className="space-y-2">
            <h2 id="stimuli-heading" className="text-lg font-medium">
              Stimuli (read-only)
            </h2>
            <ul className="list-disc pl-5">
              {doc.stimuli.map((s) => (
                <li key={s.id}>
                  {s.id} ({s.kind.replace(/_/g, " ")}): {s.description}
                </li>
              ))}
            </ul>
          </section>
        ) : null}

        <McqSection doc={doc} update={update} problems={problems} />
        {doc.parts.map((p, i) => (
          <PartSection key={p.id} doc={doc} index={i} update={update} problems={problems} commandTerms={commandTerms} notify={setNotice} />
        ))}

        {doc.solution_model ? (
          <section aria-labelledby="solution-heading" className="space-y-2">
            <h2 id="solution-heading" className="text-lg font-medium">
              Solution model (read-only)
            </h2>
            <ScrollBox label="Solution model">
              <pre className="text-xs">{JSON.stringify(doc.solution_model, null, 2)}</pre>
            </ScrollBox>
          </section>
        ) : null}
      </div>

      {tab === "preview" ? (
        <section aria-labelledby="preview-heading" className="space-y-2">
          <h2 id="preview-heading" className="text-lg font-medium">
            Preview
          </h2>
          <QuestionDocumentView document={doc} showAnswers />
        </section>
      ) : null}

      <p role="status" aria-live="polite" className={notice ? "rounded border border-amber-600 p-3" : "sr-only"}>
        {notice}
      </p>

      <div className="sticky bottom-0 flex flex-wrap items-center justify-end gap-x-4 gap-y-2 border-t border-[var(--page-border)] bg-[var(--page-bg)] py-3">
        <span>Total marks: {totalMarks(doc)}</span>
        {dirty ? <span>Changes pending</span> : null}
        <span role="status" aria-live="polite">
          {announce}
        </span>
        <button type="button" onClick={onSave} className={BTN} disabled={locked} aria-busy={locked}>
          Save
        </button>
      </div>
    </form>
  );
}
