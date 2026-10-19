"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { unwrap } from "@/lib/admin";
import { useApi } from "@/lib/api";
import { DELETE_WARNING, countLabel } from "@/lib/learn";
import { RESPONSES_KEY } from "@/lib/responses";
import { SessionGate } from "../admin/staff-gate";
import { AnswerProblem } from "../learn/answer-problem";
import { PrivacyNotice } from "../learn/privacy-notice";

export function AccountView() {
  return (
    <SessionGate allowed={() => true} denied="">
      {(me) => <Inner accountId={me.account_id} roles={me.roles} />}
    </SessionGate>
  );
}

function Inner({ accountId, roles }: { accountId: string; roles: readonly string[] }) {
  const [copied, setCopied] = useState<"yes" | "no" | null>(null);

  async function copy() {
    try {
      await navigator.clipboard.writeText(accountId);
      setCopied("yes");
    } catch {
      setCopied("no");
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Account</h1>
      <section aria-labelledby="account-id" className="space-y-2">
        <h2 id="account-id" className="text-lg font-medium">
          Your account ID
        </h2>
        <p>
          <code className="break-all">{accountId}</code>
        </p>
        <div className="flex flex-wrap items-center gap-3">
          <button type="button" onClick={() => void copy()} className="rounded border border-[var(--page-border)] px-3 py-1.5">
            Copy account ID
          </button>
          <span role="status">{copied === "yes" ? "Account ID copied." : copied === "no" ? "Copying failed. Select the ID and copy it by hand." : ""}</span>
        </div>
      </section>
      <section aria-labelledby="account-roles" className="space-y-1">
        <h2 id="account-roles" className="text-lg font-medium">
          Roles
        </h2>
        <p>{roles.length > 0 ? roles.join(", ") : "No roles yet."}</p>
      </section>
      <MyAnswers />
      <PrivacyNotice />
    </div>
  );
}

function MyAnswers() {
  const api = useApi();
  const queryClient = useQueryClient();
  const dialog = useRef<HTMLDialogElement>(null);
  const [open, setOpen] = useState(false);
  const [deleted, setDeleted] = useState<number | null>(null);

  const count = useQuery({
    queryKey: [...RESPONSES_KEY, "count"],
    queryFn: async () => {
      const page = unwrap(await api.GET("/v1/me/responses", { params: { query: { limit: 100 } } }));
      return { n: page.items.length, more: page.next_cursor !== null };
    },
  });
  const remove = useMutation({
    mutationFn: async () => unwrap(await api.DELETE("/v1/me/responses")),
    onSuccess: (r) => {
      setDeleted(r.deleted);
      close();
      void queryClient.invalidateQueries({ queryKey: RESPONSES_KEY });
    },
  });

  useEffect(() => {
    const el = dialog.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    if (!open && el.open) el.close();
  }, [open]);

  function close() {
    setOpen(false);
  }

  return (
    <section aria-labelledby="my-answers" className="space-y-2">
      <h2 id="my-answers" className="text-lg font-medium">
        My answers
      </h2>
      {count.isPending ? <p>Loading...</p> : null}
      {count.isError ? <AnswerProblem error={count.error} onReload={() => void count.refetch()} /> : null}
      {count.data ? (
        <p>
          {count.data.n === 0 ? "You have no saved answers." : `You have ${countLabel(count.data.n, count.data.more)} saved answers.`}
        </p>
      ) : null}
      <div role="status">{deleted !== null ? `Deleted ${deleted} ${deleted === 1 ? "answer" : "answers"}.` : ""}</div>
      <div className="flex flex-wrap items-center gap-3">
        <Link href="/learn/history" className="underline">
          View my answers
        </Link>
        <button
          type="button"
          onClick={() => {
            setDeleted(null);
            remove.reset();
            setOpen(true);
          }}
          className="rounded border border-red-700 px-3 py-1.5"
        >
          Delete all my answers
        </button>
      </div>
      <dialog
        ref={dialog}
        aria-labelledby="delete-title"
        onClose={() => setOpen(false)}
        className="m-auto w-[min(28rem,calc(100vw-2rem))] rounded border border-[var(--page-border)] bg-[var(--page-bg)] p-4 text-[var(--page-fg)]"
      >
        <div className="space-y-3">
          <h3 id="delete-title" className="text-lg font-medium">
            Delete all my answers?
          </h3>
          <p>{DELETE_WARNING}</p>
          <AnswerProblem error={remove.error} />
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => remove.mutate()}
              disabled={remove.isPending}
              className="rounded border border-red-700 px-3 py-1.5"
            >
              Yes, delete all my answers
            </button>
            <button type="button" autoFocus onClick={close} className="rounded border border-[var(--page-border)] px-3 py-1.5">
              Cancel
            </button>
          </div>
        </div>
      </dialog>
    </section>
  );
}
