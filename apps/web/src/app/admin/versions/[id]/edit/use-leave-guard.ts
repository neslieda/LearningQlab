"use client";

import { useEffect } from "react";

const MARKER = "__qlabLeaveGuard";

export const LEAVE_MESSAGE = "You have changes that are not stored. Leave this page and lose them?";

const marked = (state: unknown) => !!(state && typeof state === "object" && (state as Record<string, unknown>)[MARKER]);

/**
 * While `active`, leaving the page asks first: closing or reloading the tab (beforeunload), following any link inside
 * the app (a capture-phase click listener, ahead of the router), and the browser's back button.
 */
export function useLeaveGuard(active: boolean): void {
  useEffect(() => {
    if (!active) return;

    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = "";
    };

    const onClick = (e: MouseEvent) => {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      const anchor = (e.target as Element | null)?.closest?.("a[href]") as HTMLAnchorElement | null;
      if (!anchor || (anchor.target && anchor.target !== "_self") || anchor.hasAttribute("download")) return;
      const url = new URL(anchor.href, window.location.href);
      if (url.origin === window.location.origin && url.pathname === window.location.pathname && url.search === window.location.search) return;
      if (!window.confirm(LEAVE_MESSAGE)) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
      }
    };

    // The back button: a marker entry with the same URL sits on top of the history while the guard is on. Going back
    // lands on the real entry (the page itself); only then do we ask, and either leave for real or put the marker back.
    const pushMarker = () => {
      const state = (window.history.state ?? {}) as Record<string, unknown>;
      window.history.pushState({ ...state, [MARKER]: true }, "", window.location.href);
    };
    if (!marked(window.history.state)) pushMarker();
    let leaving = false;
    const onPopState = (e: PopStateEvent) => {
      if (leaving || marked(e.state)) return; // going forward onto the marker, or already confirmed
      e.stopImmediatePropagation();
      if (window.confirm(LEAVE_MESSAGE)) {
        leaving = true;
        window.history.back();
      } else {
        pushMarker();
      }
    };

    window.addEventListener("beforeunload", onBeforeUnload);
    document.addEventListener("click", onClick, true);
    window.addEventListener("popstate", onPopState, true);
    return () => {
      window.removeEventListener("beforeunload", onBeforeUnload);
      document.removeEventListener("click", onClick, true);
      window.removeEventListener("popstate", onPopState, true);
    };
  }, [active]);
}
