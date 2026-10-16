"use client";

import { useState, type FormEvent } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useApi } from "@/lib/api";
import { ME_KEY, useMe } from "@/lib/use-me";
import { clearToken, writeToken } from "@/lib/token";

export function SignIn() {
  const api = useApi();
  const queryClient = useQueryClient();
  const { me, isLoading } = useMe();
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const token = value.trim();
    if (!token) {
      setError("Paste a token first.");
      return;
    }
    setBusy(true);
    setError(null);
    writeToken(token);
    try {
      const { data, response } = await api.GET("/v1/me");
      if (!data) {
        clearToken();
        setError(`The token was rejected (HTTP ${response.status}).`);
        return;
      }
      setValue("");
      await queryClient.invalidateQueries({ queryKey: ME_KEY });
    } catch {
      clearToken();
      setError("The API could not be reached. Is it running?");
    } finally {
      setBusy(false);
    }
  }

  async function onSignOut() {
    clearToken();
    await queryClient.invalidateQueries({ queryKey: ME_KEY });
  }

  if (isLoading) return <p>Checking session...</p>;

  if (me) {
    return (
      <div className="space-y-3">
        <dl className="space-y-1">
          <div>
            <dt className="font-medium">Account id</dt>
            <dd className="break-all font-mono text-sm">{me.account_id}</dd>
          </div>
          <div>
            <dt className="font-medium">Roles</dt>
            <dd>{me.roles.join(", ") || "none"}</dd>
          </div>
        </dl>
        <button type="button" onClick={onSignOut} className="rounded border border-[var(--page-border)] px-3 py-1.5">
          Sign out
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="space-y-3">
      <p className="text-[var(--page-muted)]">
        Paste the output of <code>python -m qlab.api.dev token &lt;role&gt;</code>. The token stays in this tab&apos;s session storage.
      </p>
      <div>
        <label htmlFor="token" className="block font-medium">
          Token
        </label>
        <textarea
          id="token"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          rows={4}
          autoComplete="off"
          spellCheck={false}
          aria-describedby={error ? "token-error" : undefined}
          aria-invalid={error ? true : undefined}
          className="w-full rounded border border-[var(--page-border)] bg-transparent p-2 font-mono text-sm"
        />
      </div>
      {error ? (
        <p id="token-error" role="alert" className="text-red-700 dark:text-red-300">
          {error}
        </p>
      ) : null}
      <button type="submit" disabled={busy} className="rounded border border-[var(--page-border)] px-3 py-1.5">
        {busy ? "Checking..." : "Sign in"}
      </button>
    </form>
  );
}
