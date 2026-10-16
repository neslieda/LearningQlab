"use client";

import { useCallback, useEffect, useRef } from "react";

const MARKER = "__qlabLeaveGuard";

export const LEAVE_MESSAGE = "You have changes that are not stored. Leave this page and lose them?";

const marked = (state: unknown) => !!(state && typeof state === "object" && (state as Record<string, unknown>)[MARKER]);

/**
 * While `active`, leaving the page asks first: closing or reloading the tab (beforeunload), following any link inside
 * the app (a capture-phase click listener, ahead of the router), and the browser's back button.
 *
 * The back button works through a marker history entry (same URL) that sits on top while the guard is on. The marker
 * is removed again when the guard switches off (after a save) and when the user confirms leaving through a link, so
 * Back never needs a second press and no duplicate of the edit URL is left behind.
 */
export function useLeaveGuard(active: boolean): () => Promise<void> {
  const mounted = useRef(true);
  const releaseRef = useRef<((done: () => void) => void) | null>(null);
  // Declared before the guard effect so that on unmount it has already cleared the flag when the guard cleans up.
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  useEffect(() => {
    if (!active) return;
    // True once the user has said yes: no further prompt (not even the browser's own) for this departure.
    let confirmed = false;
    let pendingLink: HTMLAnchorElement | null = null;

    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      if (confirmed) return;
      e.preventDefault();
      e.returnValue = "";
    };

    const onClick = (e: MouseEvent) => {
      if (confirmed || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      const anchor = (e.target as Element | null)?.closest?.("a[href]") as HTMLAnchorElement | null;
      if (!anchor || (anchor.target && anchor.target !== "_self") || anchor.hasAttribute("download")) return;
      const url = new URL(anchor.href, window.location.href);
      const sameOrigin = url.origin === window.location.origin;
      if (sameOrigin && url.pathname === window.location.pathname && url.search === window.location.search) return;
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      if (!window.confirm(LEAVE_MESSAGE)) return;
      confirmed = true;
      if (sameOrigin && marked(window.history.state)) {
        // Pop the marker first, then follow the link from the real entry.
        pendingLink = anchor;
        window.history.back();
      } else {
        anchor.click();
      }
    };

    const pushMarker = () => {
      const state = (window.history.state ?? {}) as Record<string, unknown>;
      window.history.pushState({ ...state, [MARKER]: true }, "", window.location.href);
    };
    if (!marked(window.history.state)) pushMarker();

    const onPopState = (e: PopStateEvent) => {
      if (pendingLink) {
        // The marker is gone; now follow the link the user confirmed.
        e.stopImmediatePropagation();
        const link = pendingLink;
        pendingLink = null;
        link.click();
        return;
      }
      if (confirmed || marked(e.state)) return; // going forward onto the marker, or already confirmed
      e.stopImmediatePropagation();
      if (window.confirm(LEAVE_MESSAGE)) {
        confirmed = true;
        window.history.back();
      } else {
        pushMarker();
      }
    };

    // Lets the page leave on its own (a navigation it starts itself): no prompt from here on, and the marker entry is
    // taken off the history first, so that the navigation that follows is not undone by the step back.
    releaseRef.current = (done) => {
      confirmed = true;
      if (marked(window.history.state)) {
        window.addEventListener("popstate", () => done(), { once: true });
        window.history.back();
      } else {
        done();
      }
    };

    window.addEventListener("beforeunload", onBeforeUnload);
    document.addEventListener("click", onClick, true);
    window.addEventListener("popstate", onPopState, true);
    return () => {
      releaseRef.current = null;
      window.removeEventListener("beforeunload", onBeforeUnload);
      document.removeEventListener("click", onClick, true);
      window.removeEventListener("popstate", onPopState, true);
      // The guard switched off while the page stays (a successful save): take the marker off the history.
      if (mounted.current && !confirmed && marked(window.history.state)) window.history.back();
    };
  }, [active]);

  /** Resolves once the guard is out of the way (immediately when it is off or has no marker on the history). */
  return useCallback(() => new Promise<void>((resolve) => (releaseRef.current ? releaseRef.current(resolve) : resolve())), []);
}
