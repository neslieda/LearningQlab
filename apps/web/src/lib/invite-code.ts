// The invite link is `/invite#<code>`: the code is in the URL fragment, which no server or log sees.
// The invite code survives the sign-in round trip in sessionStorage (tab-scoped). It is cleared once used.
const KEY = "qlab.invite.code";
const CODE = /^[A-Za-z0-9_-]{1,200}$/;

export function isValidCode(code: string): boolean {
  return CODE.test(code);
}

export function storeInviteCode(code: string, storage: Pick<Storage, "setItem"> | null = safeStorage()): void {
  if (!storage || !isValidCode(code)) return;
  try {
    storage.setItem(KEY, code);
  } catch {
    /* storage full or blocked: the code is still in the invite URL */
  }
}

export function readInviteCode(storage: Pick<Storage, "getItem"> | null = safeStorage()): string | null {
  if (!storage) return null;
  try {
    const v = storage.getItem(KEY);
    return v && isValidCode(v) ? v : null;
  } catch {
    return null;
  }
}

export function clearInviteCode(storage: Pick<Storage, "removeItem"> | null = safeStorage()): void {
  if (!storage) return;
  try {
    storage.removeItem(KEY);
  } catch {
    /* nothing to clear */
  }
}

function safeStorage(): Storage | null {
  try {
    return typeof window === "undefined" ? null : window.sessionStorage;
  } catch {
    return null;
  }
}

/** A same-site path only (no scheme, no `//`), so a crafted `next` value cannot send the user elsewhere. */
export function safeReturnPath(path: string | null | undefined): string {
  if (!path || !path.startsWith("/") || path.startsWith("//") || path.includes("\\") || /[\u0000-\u001f]/.test(path)) return "/";
  return path;
}

/**
 * Reads the invite code from `location.hash` and removes the fragment from the address bar right away.
 * A valid code is also stored for the sign-in round trip. Returns null when there is no valid code in the fragment.
 */
export function takeCodeFromHash(): string | null {
  if (typeof window === "undefined") return null;
  const raw = window.location.hash.replace(/^#/, "");
  if (!raw) return null;
  try {
    window.history.replaceState(window.history.state, "", window.location.pathname + window.location.search);
  } catch {
    /* the address bar keeps the fragment; nothing else to do */
  }
  if (!isValidCode(raw)) return null;
  storeInviteCode(raw);
  return raw;
}
