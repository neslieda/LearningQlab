"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, formatTime, shortId, unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import { availableActions, isWorkingStatus, problemMessage } from "@/lib/decisions";
import { ProblemView } from "../../problem-view";
import { StaffGate } from "../../staff-gate";
import { ScrollBox, StatusBadge } from "../../status-badge";

export function QuestionView({ id }: { id: string }) {
  return <StaffGate>{(me) => <Inner id={id} roles={me.roles} />}</StaffGate>;
}

function Inner({ id, roles }: { id: string; roles: readonly string[] }) {
  const api = useApi();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [error, setError] = useState<unknown>(null);

  const query = useQuery({
    queryKey: ["admin", "question", id],
    queryFn: async () => unwrap(await api.GET("/v1/admin/questions/{question_id}", { params: { path: { question_id: id } } })),
  });

  const open = useMutation({
    mutationFn: async () => unwrap(await api.POST("/v1/admin/questions/{question_id}/revisions", { params: { path: { question_id: id } } })),
    onSuccess: async (version) => {
      await queryClient.invalidateQueries({ queryKey: ["admin"] });
      router.push(`/admin/versions/${version.id}`);
    },
    onError: setError,
  });

  if (query.isPending) return <p>Loading...</p>;
  if (query.isError) {
    return <p role="alert">{query.error instanceof ApiError ? problemMessage(query.error.problem).message : "Something went wrong"}</p>;
  }
  const q = query.data;
  const hasWorking = q.versions.some((v) => isWorkingStatus(v.status));
  const latest = q.versions[q.versions.length - 1];
  const canOpen = latest ? availableActions(latest.status, roles, hasWorking).some((a) => a.id === "open_revision") : false;

  return (
    <div className="space-y-4">
      <p>
        <Link href="/admin/questions" className="underline">
          All questions
        </Link>
      </p>
      <h1 className="text-2xl font-semibold">{q.source_ref ?? shortId(q.id)}</h1>
      <dl className="grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1 text-sm">
        <dt className="font-medium">Source key</dt>
        <dd>{q.source_ref ?? "none"}</dd>
        <dt className="font-medium">Origin</dt>
        <dd>{q.origin.replace(/_/g, " ")}</dd>
        <dt className="font-medium">Created by</dt>
        <dd className="break-all font-mono">{q.created_by}</dd>
        <dt className="font-medium">Created</dt>
        <dd>{formatTime(q.created_at)}</dd>
      </dl>

      <h2 className="text-lg font-medium">Versions</h2>
      <ScrollBox label="Versions table">
        <table className="w-full min-w-[32rem] border-collapse text-left text-sm">
          <caption className="sr-only">Versions, oldest first</caption>
          <thead>
            <tr className="border-b border-[var(--page-border)]">
              <th scope="col" className="p-2">Version</th>
              <th scope="col" className="p-2">Status</th>
              <th scope="col" className="p-2">Content</th>
              <th scope="col" className="p-2">Updated</th>
              <th scope="col" className="p-2">Figures</th>
            </tr>
          </thead>
          <tbody>
            {q.versions.map((v) => (
              <tr key={v.id} className="border-b border-[var(--page-border)]">
                <th scope="row" className="p-2 font-normal">
                  <Link href={`/admin/versions/${v.id}`} className="underline">
                    Version {v.version_no}
                  </Link>
                </th>
                <td className="p-2"><StatusBadge status={v.status} /></td>
                <td className="p-2 font-mono">{v.content_sha256.slice(0, 8)}</td>
                <td className="p-2">{formatTime(v.updated_at)}</td>
                <td className="p-2">{v.has_unverified_visuals ? "Awaiting figures" : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </ScrollBox>

      {canOpen ? (
        <button type="button" onClick={() => open.mutate()} disabled={open.isPending} className="rounded border border-[var(--page-border)] px-3 py-1.5">
          Open revision
        </button>
      ) : null}
      <ProblemView error={error} questionId={id} onReload={() => { setError(null); void query.refetch(); }} />
    </div>
  );
}
