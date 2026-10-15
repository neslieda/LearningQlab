// Slice 7b section 4: unsaved changes warn before leaving; the history marker never outlives the guard.
import { renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useLeaveGuard } from "../../src/app/admin/versions/[id]/edit/use-leave-guard";

const tick = () => new Promise((r) => setTimeout(r, 30));
const markerOn = () => !!(window.history.state && (window.history.state as Record<string, unknown>).__qlabLeaveGuard);

beforeEach(() => window.history.replaceState(null, "", "/"));

afterEach(() => {
  vi.restoreAllMocks();
  document.body.innerHTML = "";
});

function beforeUnload(): BeforeUnloadEvent {
  const e = new Event("beforeunload", { cancelable: true }) as BeforeUnloadEvent;
  window.dispatchEvent(e);
  return e;
}

describe("useLeaveGuard", () => {
  it("arms beforeunload only while active", () => {
    const { rerender, unmount } = renderHook(({ on }) => useLeaveGuard(on), { initialProps: { on: false } });
    expect(beforeUnload().defaultPrevented).toBe(false);
    rerender({ on: true });
    expect(beforeUnload().defaultPrevented).toBe(true);
    rerender({ on: false });
    expect(beforeUnload().defaultPrevented).toBe(false);
    unmount();
  });

  it("asks before following an in-app link, and cancels the click on no", () => {
    const confirm = vi.spyOn(window, "confirm").mockReturnValue(false);
    const { unmount } = renderHook(() => useLeaveGuard(true));
    const a = document.createElement("a");
    a.href = "/somewhere-else";
    document.body.append(a);
    const click = new MouseEvent("click", { bubbles: true, cancelable: true });
    a.dispatchEvent(click);
    expect(confirm).toHaveBeenCalledTimes(1);
    expect(click.defaultPrevented).toBe(true);
    unmount();
  });

  it("removes its history marker when the guard switches off, so one Back press is enough", async () => {
    const before = window.history.length;
    const { rerender, unmount } = renderHook(({ on }) => useLeaveGuard(on), { initialProps: { on: true } });
    expect(markerOn()).toBe(true);
    expect(window.history.length).toBe(before + 1);
    rerender({ on: false });
    await tick();
    expect(markerOn()).toBe(false);
    unmount();
  });

  it("does not touch the history when it unmounts (leaving for another page)", async () => {
    const { unmount } = renderHook(() => useLeaveGuard(true));
    expect(markerOn()).toBe(true);
    unmount();
    await tick();
    expect(markerOn()).toBe(true); // the page is leaving anyway; Back goes through the entry, not past it
  });

  it("does not prompt a second time after the user confirmed a link", async () => {
    const confirm = vi.spyOn(window, "confirm").mockReturnValue(true);
    const { unmount } = renderHook(() => useLeaveGuard(true));
    const a = document.createElement("a");
    a.href = "/elsewhere";
    a.addEventListener("click", (e) => e.preventDefault()); // jsdom cannot navigate
    document.body.append(a);
    a.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
    await tick();
    expect(confirm).toHaveBeenCalledTimes(1);
    expect(beforeUnload().defaultPrevented).toBe(false);
    unmount();
  });
});
