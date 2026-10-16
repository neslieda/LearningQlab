"use client";

import { useState } from "react";
import { SessionGate } from "../admin/staff-gate";

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
    </div>
  );
}
