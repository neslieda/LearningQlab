"use client";

import Link from "next/link";
import { useState } from "react";
import type { AdminVersion } from "@qlab/api-client";
import { useQuery } from "@tanstack/react-query";
import { unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import { isEditableStatus } from "@/lib/decisions";
import { ProblemView } from "../../../problem-view";
import { StaffGate } from "../../../staff-gate";
import { EditorForm, consumeCreated } from "./editor-form";

export function EditView({ id }: { id: string }) {
  return <StaffGate>{() => <Inner id={id} />}</StaffGate>;
}

function Inner({ id }: { id: string }) {
  const api = useApi();
  // The content the editor started from, pinned: later reads never replace what the user is editing.
  const [base, setBase] = useState<AdminVersion | null>(null);
  const [epoch, setEpoch] = useState(0);
  const [reloadError, setReloadError] = useState<unknown>(null);
  // True once, when this page was opened by creating the question.
  const [created] = useState(() => consumeCreated(id));

  const version = useQuery({
    queryKey: ["admin", "version", id],
    // A copy cached by the version page may be older than the stored content: always read again before starting.
    refetchOnMount: "always",
    queryFn: async () => unwrap(await api.GET("/v1/admin/question-versions/{version_id}", { params: { path: { version_id: id } } })),
  });
  // Pin only data from a settled read, never the cached copy that was on screen while the read was running.
  if (version.data && !version.isFetching && (base === null || base.id !== version.data.id)) setBase(version.data);

  if (!base && version.isError) return <ProblemView error={version.error} onReload={() => void version.refetch()} />;
  if (!base) return <p>Loading...</p>;

  if (!isEditableStatus(base.status)) {
    return (
      <div className="space-y-2">
        <p role="alert">This version can no longer be edited</p>
        <Link href={`/admin/versions/${id}`} className="underline">
          Go to the version
        </Link>
      </div>
    );
  }

  const reload = () => {
    void version.refetch().then((result) => {
      if (result.isError || !result.data) {
        // Keep the user's edits; say why nothing changed.
        setReloadError(result.error ?? new Error("reload failed"));
        return;
      }
      setReloadError(null);
      setBase(result.data);
      setEpoch((n) => n + 1);
    });
  };

  return (
    <div className="space-y-4">
      <ProblemView error={reloadError} questionId={base.question_id} onReload={reload} />
      <EditorForm key={`${epoch}`} version={base} onReload={reload} initialAnnounce={created && epoch === 0 ? "Created" : ""} />
    </div>
  );
}
