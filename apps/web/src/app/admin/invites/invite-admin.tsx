"use client";

import { useState, type FormEvent } from "react";
import { useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { components } from "@qlab/api-client";
import { formatTime, unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import { invitableRoles, maxUsesFor, type InviteRole } from "@/lib/decisions";
import { InviterGate } from "../staff-gate";
import { ProblemView } from "../problem-view";
import { ScrollBox } from "../status-badge";

type Invite = components["schemas"]["InviteOut"];
type Created = components["schemas"]["InviteCreated"];

const ROLE_LABEL: Record<InviteRole, string> = {
  student: "Student",
  teacher: "Teacher",
  reviewer: "Reviewer",
  content_admin: "Content admin",
  platform_admin: "Platform admin",
};

export function InviteAdmin() {
  return <InviterGate>{(me) => <Inner roles={me.roles} />}</InviterGate>;
}

function inviteStatus(i: Invite, now: number): "Revoked" | "Expired" | "Used up" | "Active" {
  if (i.revoked_at) return "Revoked";
  if (new Date(i.expires_at).getTime() <= now) return "Expired";
  if (i.uses >= i.max_uses) return "Used up";
  return "Active";
}

function parseWhole(value: string, min: number, max: number): number | null {
  if (!/^\d+$/.test(value.trim())) return null;
  const n = Number(value);
  return n >= min && n <= max ? n : null;
}

function Inner({ roles }: { roles: readonly string[] }) {
  const api = useApi();
  const queryClient = useQueryClient();
  const allowed = invitableRoles(roles);
  const [role, setRole] = useState<InviteRole>(allowed[0] ?? "student");
  const [days, setDays] = useState("7");
  const [uses, setUses] = useState("1");
  const [invalid, setInvalid] = useState(false);
  const [created, setCreated] = useState<Created | null>(null);
  const [copied, setCopied] = useState<"yes" | "no" | null>(null);

  const daysValue = parseWhole(days, 1, 30);
  const maxUses = maxUsesFor(role);
  const usesValue = parseWhole(uses, 1, maxUses);

  const list = useInfiniteQuery({
    queryKey: ["admin", "invites"],
    initialPageParam: null as string | null,
    queryFn: async ({ pageParam }) =>
      unwrap(await api.GET("/v1/admin/invites", { params: { query: { cursor: pageParam ?? undefined, limit: 50 } } })),
    getNextPageParam: (last) => last.next_cursor,
  });
  const items = list.data?.pages.flatMap((p) => p.items) ?? [];

  const create = useMutation({
    mutationFn: async () =>
      unwrap(await api.POST("/v1/admin/invites", { body: { role, expires_in_days: daysValue ?? 7, max_uses: usesValue ?? 1 } })),
    onSuccess: async (data) => {
      setCreated(data);
      setCopied(null);
      await queryClient.invalidateQueries({ queryKey: ["admin", "invites"] });
    },
  });

  const revoke = useMutation({
    mutationFn: async (id: string) => unwrap(await api.POST("/v1/admin/invites/{invite_id}/revoke", { params: { path: { invite_id: id } } })),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "invites"] }),
  });

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (daysValue === null || usesValue === null) {
      setInvalid(true);
      return;
    }
    setInvalid(false);
    revoke.reset();
    create.mutate();
  }

  const link = created ? `${window.location.origin}/invite#${created.code}` : "";

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(link);
      setCopied("yes");
    } catch {
      setCopied("no");
    }
  }

  function onRevoke(i: Invite) {
    if (!window.confirm(`Revoke this ${ROLE_LABEL[i.role]} invite? The link will stop working.`)) return;
    create.reset();
    revoke.mutate(i.id);
  }

  const now = list.dataUpdatedAt;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Invites</h1>

      <form onSubmit={onSubmit} noValidate aria-label="Create an invite" className="flex flex-wrap items-end gap-3">
        <label className="block text-sm">
          <span className="block font-medium">Role</span>
          <select value={role} onChange={(e) => setRole(e.target.value as InviteRole)} className="rounded border border-[var(--page-border)] bg-transparent p-1.5">
            {allowed.map((r) => (
              <option key={r} value={r}>
                {ROLE_LABEL[r]}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="block font-medium">Expires in (days)</span>
          <input
            type="number"
            inputMode="numeric"
            min={1}
            max={30}
            step={1}
            value={days}
            onChange={(e) => setDays(e.target.value)}
            aria-invalid={invalid && daysValue === null ? true : undefined}
            aria-describedby={invalid && daysValue === null ? "days-error" : undefined}
            className="w-28 rounded border border-[var(--page-border)] bg-transparent p-1.5"
          />
        </label>
        <label className="block text-sm">
          <span className="block font-medium">Uses</span>
          <input
            type="number"
            inputMode="numeric"
            min={1}
            max={maxUses}
            step={1}
            value={uses}
            onChange={(e) => setUses(e.target.value)}
            aria-invalid={invalid && usesValue === null ? true : undefined}
            aria-describedby={invalid && usesValue === null ? "uses-error" : undefined}
            className="w-28 rounded border border-[var(--page-border)] bg-transparent p-1.5"
          />
        </label>
        <button type="submit" disabled={create.isPending} className="rounded border border-[var(--page-border)] px-3 py-1.5">
          {create.isPending ? "Creating..." : "Create invite"}
        </button>
        {invalid ? (
          <div role="alert" className="w-full text-red-700 dark:text-red-300">
            {daysValue === null ? <p id="days-error">Expires in must be a whole number from 1 to 30.</p> : null}
            {usesValue === null ? <p id="uses-error">Uses must be a whole number from 1 to {maxUses}.</p> : null}
          </div>
        ) : null}
      </form>

      {create.isError ? <ProblemView error={create.error} onReload={() => create.reset()} /> : null}

      {created ? (
        <section aria-labelledby="new-invite" className="space-y-2 rounded border border-[var(--page-border)] p-3">
          <h2 id="new-invite" className="text-lg font-medium">
            Invite link ({ROLE_LABEL[created.role]})
          </h2>
          <p className="font-medium">This link is shown only once. Copy it now: it will not be shown again.</p>
          <input
            type="text"
            readOnly
            aria-label="Invite link"
            value={link}
            onFocus={(e) => e.currentTarget.select()}
            className="w-full rounded border border-[var(--page-border)] bg-transparent p-1.5 font-mono text-sm"
          />
          <div className="flex flex-wrap items-center gap-3">
            <button type="button" onClick={() => void copyLink()} className="rounded border border-[var(--page-border)] px-3 py-1.5">
              Copy link
            </button>
            <span role="status">{copied === "yes" ? "Link copied." : copied === "no" ? "Copying failed. Select the link and copy it by hand." : ""}</span>
          </div>
        </section>
      ) : null}

      <section aria-labelledby="invite-list" className="space-y-3">
        <h2 id="invite-list" className="text-lg font-medium">
          Your invites
        </h2>
        {revoke.isError ? <ProblemView error={revoke.error} onReload={() => revoke.reset()} /> : null}
        {list.isPending ? <p>Loading...</p> : null}
        {list.isError ? <ProblemView error={list.error} onReload={() => void list.refetch()} /> : null}
        {list.isSuccess && items.length === 0 ? <p>No invites yet.</p> : null}
        {items.length > 0 ? (
          <ScrollBox label="Invites table">
            <table className="w-full min-w-[40rem] border-collapse text-left text-sm">
              <caption className="sr-only">Invites</caption>
              <thead>
                <tr className="border-b border-[var(--page-border)]">
                  <th scope="col" className="p-2">Role</th>
                  <th scope="col" className="p-2">Created</th>
                  <th scope="col" className="p-2">Expires</th>
                  <th scope="col" className="p-2">Uses</th>
                  <th scope="col" className="p-2">Status</th>
                  <th scope="col" className="p-2">Action</th>
                </tr>
              </thead>
              <tbody>
                {items.map((i) => {
                  const status = inviteStatus(i, now);
                  return (
                    <tr key={i.id} className="border-b border-[var(--page-border)] align-top">
                      <th scope="row" className="p-2 font-normal">{ROLE_LABEL[i.role]}</th>
                      <td className="p-2">{formatTime(i.created_at)}</td>
                      <td className="p-2">{formatTime(i.expires_at)}</td>
                      <td className="p-2">
                        {i.uses}/{i.max_uses}
                      </td>
                      <td className="p-2">{status}</td>
                      <td className="p-2">
                        {status === "Active" ? (
                          <button
                            type="button"
                            onClick={() => onRevoke(i)}
                            disabled={revoke.isPending}
                            aria-label={`Revoke ${ROLE_LABEL[i.role]} invite created ${formatTime(i.created_at)}`}
                            className="rounded border border-[var(--page-border)] px-2 py-1"
                          >
                            Revoke
                          </button>
                        ) : null}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </ScrollBox>
        ) : null}
        {list.hasNextPage ? (
          <button type="button" onClick={() => void list.fetchNextPage()} disabled={list.isFetchingNextPage} className="rounded border border-[var(--page-border)] px-3 py-1.5">
            {list.isFetchingNextPage ? "Loading..." : "Load more"}
          </button>
        ) : null}
      </section>
    </div>
  );
}
