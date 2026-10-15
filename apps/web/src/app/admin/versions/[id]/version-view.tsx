"use client";

import Link from "next/link";
import { useState } from "react";
import type { AdminVersion } from "@qlab/api-client";
import { useQuery } from "@tanstack/react-query";
import { QuestionDocumentView } from "@qlab/question-renderer";
import { formatTime, unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import { isWorkingStatus } from "@/lib/decisions";
import { ProblemView } from "../../problem-view";
import { StaffGate } from "../../staff-gate";
import { ScrollBox, StatusBadge } from "../../status-badge";
import { DecisionPanel } from "./decision-panel";

export function VersionView({ id }: { id: string }) {
  return <StaffGate>{(me) => <Inner id={id} roles={me.roles} accountId={me.account_id} />}</StaffGate>;
}

function Inner({ id, roles, accountId }: { id: string; roles: readonly string[]; accountId: string }) {
  const api = useApi();
  const [showAnswers, setShowAnswers] = useState(true);
  // The content the user is looking at, pinned at first display (per version id). A later read with another digest
  // never replaces it; the user must press Reload. Decisions always carry the pinned digest.
  const [pin, setPin] = useState<AdminVersion | null>(null);
  const [settling, setSettling] = useState(false);

  const version = useQuery({
    queryKey: ["admin", "version", id],
    queryFn: async () => unwrap(await api.GET("/v1/admin/question-versions/{version_id}", { params: { path: { version_id: id } } })),
  });
  const history = useQuery({
    queryKey: ["admin", "history", id],
    queryFn: async () => unwrap(await api.GET("/v1/admin/question-versions/{version_id}/history", { params: { path: { version_id: id } } })),
  });
  const questionId = version.data?.question_id;
  const question = useQuery({
    queryKey: ["admin", "question", questionId],
    enabled: !!questionId,
    queryFn: async () => unwrap(await api.GET("/v1/admin/questions/{question_id}", { params: { path: { question_id: questionId ?? "" } } })),
  });

  if (version.data && (pin === null || pin.id !== version.data.id)) setPin(version.data);

  if (version.isPending) return <p>Loading...</p>;
  if (version.isError && !version.data) {
    return <ProblemView error={version.error} onReload={() => void version.refetch()} />;
  }
  const latest = version.data;
  if (!latest || !pin) return <p>Loading...</p>;
  const stale = !settling && latest.content_sha256 !== pin.content_sha256;
  // Status and checks come from the latest read; the document and its digest stay pinned.
  const v: AdminVersion = { ...latest, content_sha256: pin.content_sha256, document: pin.document };
  const reload = () => {
    // Pin what the server returns now. Clearing the pin first would re-pin the cached, older read.
    void history.refetch();
    void version.refetch().then((result) => {
      if (result.data) setPin(result.data);
    });
  };
  const hasWorking = (question.data?.versions ?? []).some((x) => isWorkingStatus(x.status));

  return (
    <div className="space-y-6">
      <p>
        <Link href={`/admin/questions/${v.question_id}`} className="underline">
          Back to question
        </Link>
      </p>
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">Version {v.version_no}</h1>
        <h2 id="version-status-heading" tabIndex={-1} className="flex flex-wrap items-center gap-2 text-base font-normal">
          <span className="sr-only">Status</span>
          <StatusBadge status={v.status} />
          <span className="font-mono text-sm">Content {v.content_sha256.slice(0, 12)}</span>
        </h2>
      </header>

      {v.has_unverified_visuals ? (
        <p role="note" className="rounded border border-amber-600 p-3">
          Has figures without verified images: can be approved, cannot be published (D-49)
        </p>
      ) : null}

      <section aria-labelledby="content-heading" className="space-y-3">
        <h2 id="content-heading" className="text-lg font-medium">
          Content
        </h2>
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={showAnswers} onChange={(e) => setShowAnswers(e.target.checked)} />
          <span>Show answers</span>
        </label>
        <QuestionDocumentView document={v.document} showAnswers={showAnswers} />
      </section>

      <section aria-labelledby="checks-heading" className="space-y-3">
        <h2 id="checks-heading" className="text-lg font-medium">
          Checks
        </h2>
        {v.checks.length === 0 ? (
          <p>No checks recorded for this content</p>
        ) : (
          <ScrollBox label="Checks table">
            <table className="w-full min-w-[28rem] border-collapse text-left text-sm">
              <caption className="sr-only">Checks</caption>
              <thead>
                <tr className="border-b border-[var(--page-border)]">
                  <th scope="col" className="p-2">Check</th>
                  <th scope="col" className="p-2">Severity</th>
                  <th scope="col" className="p-2">Result</th>
                  <th scope="col" className="p-2">Detail</th>
                </tr>
              </thead>
              <tbody>
                {v.checks.map((c) => (
                  <tr key={c.code} className="border-b border-[var(--page-border)] align-top">
                    <th scope="row" className="p-2 font-mono font-normal">{c.code}</th>
                    <td className="p-2">{c.severity}</td>
                    <td className="p-2">{c.outcome.replace(/_/g, " ")}</td>
                    <td className="p-2">
                      <details>
                        <summary className="cursor-pointer">Show detail for {c.code}</summary>
                        <pre className="max-w-[70vw] overflow-x-auto text-xs">{JSON.stringify(c.detail, null, 2)}</pre>
                      </details>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </ScrollBox>
        )}
      </section>

      <section aria-labelledby="history-heading" className="space-y-3">
        <h2 id="history-heading" className="text-lg font-medium">
          History
        </h2>
        {history.isPending ? <p>Loading...</p> : null}
        {history.isError ? <ProblemView error={history.error} onReload={() => void history.refetch()} /> : null}
        {history.data ? (
          <ScrollBox label="History table">
            <table className="w-full min-w-[40rem] border-collapse text-left text-sm">
              <caption className="sr-only">History, oldest first</caption>
              <thead>
                <tr className="border-b border-[var(--page-border)]">
                  <th scope="col" className="p-2">When</th>
                  <th scope="col" className="p-2">Action</th>
                  <th scope="col" className="p-2">By</th>
                  <th scope="col" className="p-2">Status</th>
                  <th scope="col" className="p-2">Reason</th>
                  <th scope="col" className="p-2">Notes</th>
                </tr>
              </thead>
              <tbody>
                {history.data.items.map((h, i) => (
                  <tr key={i} className="border-b border-[var(--page-border)] align-top">
                    <td className="p-2 whitespace-nowrap">{formatTime(h.occurred_at)}</td>
                    <td className="p-2">{h.action.replace(/_/g, " ")}</td>
                    <td className="p-2 break-all font-mono">{h.actor === accountId ? "you" : h.actor}</td>
                    <td className="p-2 whitespace-nowrap">{h.previous_status ? `${h.previous_status.replace(/_/g, " ")} → ` : ""}{h.status.replace(/_/g, " ")}</td>
                    <td className="p-2">{h.reason ?? ""}</td>
                    <td className="p-2">
                      {h.failed_checks && h.failed_checks.length > 0 ? <div>Failed checks: {h.failed_checks.join(", ")}</div> : null}
                      {h.approver_is_last_editor ? <div>Approved by the last editor</div> : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </ScrollBox>
        ) : null}
      </section>

      <DecisionPanel
        version={v}
        roles={roles}
        hasWorkingVersion={hasWorking}
        questionLoaded={question.isSuccess}
        stale={stale}
        onReload={reload}
        onDecisionStart={() => setSettling(true)}
        onDecisionEnd={() => {
          setPin(null);
          setSettling(false);
        }}
      />
    </div>
  );
}
