"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import { ProblemView } from "../../problem-view";
import { StaffGate } from "../../staff-gate";
import { EditorForm } from "../../versions/[id]/edit/editor-form";

export function NewQuestionView() {
  return <StaffGate>{() => <Inner />}</StaffGate>;
}

const SELECT = "rounded border border-[var(--page-border)] bg-transparent p-2";

function Inner() {
  const api = useApi();
  // Chosen only when the catalogue offers more than one; otherwise the single subject and newest version are used.
  const [subjectKey, setSubjectKey] = useState<string | null>(null);
  const [versionCode, setVersionCode] = useState<string | null>(null);

  const catalog = useQuery({
    queryKey: ["programs"],
    queryFn: async () => unwrap(await api.GET("/v1/programs")),
  });
  const items = catalog.data?.items ?? [];
  const key = (s: { program: string; subject: string }) => `${s.program}/${s.subject}`;
  const chosen = items.find((s) => key(s) === subjectKey) ?? items[0];
  const version = chosen?.versions.find((v) => v.code === versionCode) ?? chosen?.versions[0];
  const program = chosen?.program;
  const subject = chosen?.subject;

  const syllabus = useQuery({
    queryKey: ["syllabus", program, subject, version?.code],
    enabled: !!program && !!subject && !!version,
    queryFn: async () =>
      unwrap(
        await api.GET("/v1/programs/{program}/subjects/{subject}/syllabus", {
          params: { path: { program: program as string, subject: subject as string }, query: { version: version?.code } },
        }),
      ),
  });

  if (catalog.isError) return <ProblemView error={catalog.error} onReload={() => void catalog.refetch()} />;
  if (catalog.isPending) return <p>Loading...</p>;
  if (!chosen || !version) return <p role="alert">There is no subject to write a question for yet.</p>;

  return (
    <div className="space-y-4">
      {items.length > 1 ? (
        <div className="flex flex-col gap-1">
          <label htmlFor="new-subject" className="font-medium">
            Subject
          </label>
          <select id="new-subject" className={SELECT} value={key(chosen)} onChange={(e) => { setSubjectKey(e.target.value); setVersionCode(null); }}>
            {items.map((s) => (
              <option key={key(s)} value={key(s)}>
                {s.program_name} - {s.subject_name}
              </option>
            ))}
          </select>
        </div>
      ) : (
        <p>
          <span className="font-medium">Subject:</span> {chosen.program_name} - {chosen.subject_name}
        </p>
      )}
      {chosen.versions.length > 1 ? (
        <div className="flex flex-col gap-1">
          <label htmlFor="new-syllabus-version" className="font-medium">
            Syllabus version
          </label>
          <select id="new-syllabus-version" className={SELECT} value={version.code} onChange={(e) => setVersionCode(e.target.value)}>
            {chosen.versions.map((v) => (
              <option key={v.code} value={v.code}>
                {v.title}
              </option>
            ))}
          </select>
        </div>
      ) : null}
      {syllabus.isError ? <ProblemView error={syllabus.error} onReload={() => void syllabus.refetch()} /> : null}
      {syllabus.data ? (
        <EditorForm
          key={`${program}/${subject}/${version.code}`}
          version={null}
          create={{ program: chosen.program, subject: chosen.subject, version: version.code, syllabus: syllabus.data }}
          onReload={() => void syllabus.refetch()}
        />
      ) : syllabus.isError ? null : (
        <p>Loading...</p>
      )}
    </div>
  );
}
