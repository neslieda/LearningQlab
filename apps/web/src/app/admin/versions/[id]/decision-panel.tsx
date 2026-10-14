"use client";

import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { AdminVersion } from "@qlab/api-client";
import { unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import { REASON_WARNING, availableActions, type DecisionAction } from "@/lib/decisions";
import { ProblemView } from "../../problem-view";

const NEEDS_REASON: readonly DecisionAction[] = ["request_changes", "reject", "withdraw", "republish"];

export function DecisionPanel({ version, roles, hasWorkingVersion }: { version: AdminVersion; roles: readonly string[]; hasWorkingVersion: boolean }) {
  const api = useApi();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [dialog, setDialog] = useState<DecisionAction | null>(null);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<unknown>(null);

  const id = version.id;
  const sha = version.content_sha256;
  const actions = availableActions(version.status, roles, hasWorkingVersion);

  const run = useMutation({
    mutationFn: async ({ action, reason: text }: { action: DecisionAction; reason?: string }) => {
      const path = { version_id: id };
      const reasonBody = { reason: text ?? "" };
      switch (action) {
        case "submit":
          return unwrap(await api.POST("/v1/admin/question-versions/{version_id}/submit", { params: { path } }));
        case "approve":
          return unwrap(await api.POST("/v1/admin/question-versions/{version_id}/approve", { params: { path }, body: { expected_content_sha256: sha } }));
        case "request_changes":
          return unwrap(await api.POST("/v1/admin/question-versions/{version_id}/request-changes", { params: { path }, body: reasonBody }));
        case "reject":
          return unwrap(await api.POST("/v1/admin/question-versions/{version_id}/reject", { params: { path }, body: reasonBody }));
        case "publish":
          return unwrap(await api.POST("/v1/admin/question-versions/{version_id}/publish", { params: { path }, body: { expected_content_sha256: sha } }));
        case "withdraw":
          return unwrap(await api.POST("/v1/admin/question-versions/{version_id}/withdraw", { params: { path }, body: reasonBody }));
        case "republish":
          return unwrap(await api.POST("/v1/admin/question-versions/{version_id}/republish", { params: { path }, body: { expected_content_sha256: sha, reason: reasonBody.reason } }));
        case "open_revision": {
          const created = unwrap(await api.POST("/v1/admin/questions/{question_id}/revisions", { params: { path: { question_id: version.question_id } } }));
          return created;
        }
      }
    },
    onSuccess: async (result, vars) => {
      setError(null);
      setReason("");
      await queryClient.invalidateQueries({ queryKey: ["admin"] });
      if (vars.action === "open_revision" && result && "document" in result) router.push(`/admin/versions/${result.id}`);
    },
    onError: setError,
    onSettled: () => setDialog(null),
  });

  const locked = useRef(false);
  const uid = useId();
  const trimmed = reason.trim();
  const reasonValid = trimmed.length >= 1 && trimmed.length <= 500;
  const showReason = actions.some((a) => NEEDS_REASON.includes(a.id));

  function start(action: DecisionAction) {
    if (locked.current) return; // a second click before React has re-rendered the disabled button
    setError(null);
    if (NEEDS_REASON.includes(action) && !reasonValid) return;
    if (action === "reject") {
      setDialog("reject");
      return;
    }
    send(action);
  }

  function send(action: DecisionAction) {
    if (locked.current) return;
    locked.current = true;
    run.mutate(
      { action, reason: NEEDS_REASON.includes(action) ? trimmed : undefined },
      { onSettled: () => { locked.current = false; } },
    );
  }

  function reload() {
    setError(null);
    void queryClient.invalidateQueries({ queryKey: ["admin"] });
  }

  const status = version.status;
  return (
    <section aria-labelledby="decision-heading" className="space-y-3 rounded border border-[var(--page-border)] p-4">
      <h2 id="decision-heading" className="text-lg font-medium">
        Decision
      </h2>
      {status === "needs_fix" ? <p>Waiting for changes</p> : null}
      {status === "auto_checking" ? <p>Checks are running. No decision is available yet.</p> : null}
      {actions.length === 0 && status !== "needs_fix" && status !== "auto_checking" ? <p>No decision is available to you for this version.</p> : null}
      {showReason ? (
        <div>
          <label htmlFor={`${uid}-reason`} className="block font-medium">
            Reason
          </label>
          <textarea
            id={`${uid}-reason`}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            aria-describedby={`${uid}-warning ${uid}-count`}
            aria-invalid={reason.length > 0 && !reasonValid ? true : undefined}
            className="w-full rounded border border-[var(--page-border)] bg-transparent p-2"
          />
          <p id={`${uid}-count`} className="text-sm text-[var(--page-muted)]">
            {trimmed.length} of 500 characters. A reason is required for this decision.
          </p>
          <p id={`${uid}-warning`} className="text-sm">
            {REASON_WARNING}
          </p>
        </div>
      ) : null}
      {actions.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {actions.map((a) => (
            <button
              key={a.id}
              type="button"
              onClick={() => start(a.id)}
              disabled={run.isPending || (NEEDS_REASON.includes(a.id) && !reasonValid)}
              className="rounded border border-[var(--page-border)] px-3 py-1.5 disabled:opacity-50"
            >
              {a.label}
            </button>
          ))}
        </div>
      ) : null}
      <ProblemView error={error} questionId={version.question_id} onReload={reload} />
      {dialog === "reject" ? (
        <ConfirmDialog pending={run.isPending} onCancel={() => setDialog(null)} onConfirm={() => send("reject")} />
      ) : null}
    </section>
  );
}

function ConfirmDialog({ pending, onCancel, onConfirm }: { pending: boolean; onCancel: () => void; onConfirm: () => void }) {
  const uid = useId();
  const root = useRef<HTMLDivElement>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null;
    cancelRef.current?.focus();
    return () => opener?.focus?.();
  }, []);

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Escape" && !pending) {
      e.stopPropagation();
      onCancel();
    } else if (e.key === "Tab" && root.current) {
      const els = Array.from(root.current.querySelectorAll<HTMLElement>("button:not([disabled])"));
      const first = els[0];
      const last = els[els.length - 1];
      if (!first || !last) return;
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/50 p-4">
      <div
        ref={root}
        role="dialog"
        aria-modal="true"
        aria-labelledby={`${uid}-title`}
        aria-describedby={`${uid}-text`}
        onKeyDown={onKeyDown}
        className="max-h-full w-full max-w-md space-y-3 overflow-y-auto rounded border border-[var(--page-border)] bg-[var(--page-bg)] p-4"
      >
        <h2 id={`${uid}-title`} className="text-lg font-medium">
          Reject this version?
        </h2>
        <p id={`${uid}-text`}>Rejecting cannot be undone.</p>
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={onConfirm} disabled={pending} className="rounded border border-[var(--page-border)] px-3 py-1.5 disabled:opacity-50">
            Confirm reject
          </button>
          <button type="button" ref={cancelRef} onClick={onCancel} disabled={pending} className="rounded border border-[var(--page-border)] px-3 py-1.5 disabled:opacity-50">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
