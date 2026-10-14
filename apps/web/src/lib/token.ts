// Local development sign-in only. Imported solely from the /dev/sign-in route and from useApi();
// in a production build that route is notFound() and useApi() carries no token path (see api.ts).
const KEY = "qlab.dev.token";

export function readToken(): string | null {
  try {
    return window.sessionStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function writeToken(token: string): void {
  window.sessionStorage.setItem(KEY, token);
}

export function clearToken(): void {
  try {
    window.sessionStorage.removeItem(KEY);
  } catch {
    /* sessionStorage unavailable: nothing to clear */
  }
}
