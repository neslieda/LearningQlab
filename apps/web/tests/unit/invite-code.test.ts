import { beforeEach, describe, expect, it } from "vitest";
import { clearInviteCode, isValidCode, readInviteCode, safeReturnPath, storeInviteCode, takeCodeFromHash } from "@/lib/invite-code";
import { INVITE_INVALID_MESSAGE, MFA_MESSAGE, canInvite, invitableRoles, maxUsesFor, problemMessage } from "@/lib/decisions";

beforeEach(() => window.sessionStorage.clear());

describe("invite code storage", () => {
  it("stores, reads and clears the code in sessionStorage", () => {
    expect(readInviteCode()).toBeNull();
    storeInviteCode("abc_DEF-123");
    expect(window.sessionStorage.getItem("qlab.invite.code")).toBe("abc_DEF-123");
    expect(readInviteCode()).toBe("abc_DEF-123");
    clearInviteCode();
    expect(readInviteCode()).toBeNull();
  });
  it("refuses codes that are not base64url", () => {
    storeInviteCode("a b");
    storeInviteCode("../x");
    storeInviteCode("");
    expect(readInviteCode()).toBeNull();
    expect(isValidCode("a".repeat(201))).toBe(false);
  });
  it("ignores a tampered stored value", () => {
    window.sessionStorage.setItem("qlab.invite.code", "<script>");
    expect(readInviteCode()).toBeNull();
  });
  it("survives unavailable storage", () => {
    const broken = {
      getItem() {
        throw new Error("blocked");
      },
      setItem() {
        throw new Error("blocked");
      },
      removeItem() {
        throw new Error("blocked");
      },
    };
    expect(() => storeInviteCode("abc", broken)).not.toThrow();
    expect(readInviteCode(broken)).toBeNull();
    expect(() => clearInviteCode(broken)).not.toThrow();
  });
});

describe("safeReturnPath", () => {
  it("accepts same-site paths only", () => {
    expect(safeReturnPath("/invite/abc")).toBe("/invite/abc");
    expect(safeReturnPath("/admin/invites?x=1")).toBe("/admin/invites?x=1");
    for (const bad of ["https://evil.test", "//evil.test", "/\\evil.test", "javascript:alert(1)", "", null, undefined, "evil"]) {
      expect(safeReturnPath(bad)).toBe("/");
    }
  });
});

describe("invite roles and messages", () => {
  it("limits the roles by caller", () => {
    expect(invitableRoles(["teacher"])).toEqual(["student"]);
    expect(invitableRoles(["platform_admin"])).toEqual(["student", "teacher", "reviewer", "content_admin", "platform_admin"]);
    expect(invitableRoles(["student"])).toEqual([]);
    expect(canInvite(["reviewer"])).toBe(false);
    expect(canInvite(["teacher"])).toBe(true);
  });
  it("maps the new problem codes", () => {
    expect(problemMessage({ status: 403, code: "mfa_required" }).message).toBe(MFA_MESSAGE);
    expect(MFA_MESSAGE).toBe("Staff access needs two-step verification. Sign out and use Staff sign-in.");
    expect(problemMessage({ status: 403, code: "invite_role_forbidden" }).message).toBe("You cannot invite someone to this role.");
    expect(problemMessage({ status: 404, code: "invite_not_found" }).message).toBe(INVITE_INVALID_MESSAGE);
  });
});

describe("invite code in the URL fragment", () => {
  it("reads a valid code, stores it and removes the fragment", () => {
    window.history.replaceState(null, "", "/invite#abc_DEF-123");
    expect(takeCodeFromHash()).toBe("abc_DEF-123");
    expect(window.location.hash).toBe("");
    expect(window.location.pathname).toBe("/invite");
    expect(readInviteCode()).toBe("abc_DEF-123");
  });

  it("removes an invalid fragment and returns null without storing", () => {
    window.history.replaceState(null, "", "/invite#bad code!");
    expect(takeCodeFromHash()).toBeNull();
    expect(window.location.hash).toBe("");
    expect(readInviteCode()).toBeNull();
  });

  it("returns null when there is no fragment", () => {
    window.history.replaceState(null, "", "/invite");
    expect(takeCodeFromHash()).toBeNull();
  });
});

describe("staff invite limits", () => {
  it("limits staff roles to 5 uses and others to 200", () => {
    expect(maxUsesFor("reviewer")).toBe(5);
    expect(maxUsesFor("content_admin")).toBe(5);
    expect(maxUsesFor("platform_admin")).toBe(5);
    expect(maxUsesFor("student")).toBe(200);
    expect(maxUsesFor("teacher")).toBe(200);
  });

  it("maps invite_uses_too_many", () => {
    expect(problemMessage({ status: 422, code: "invite_uses_too_many" }).message).toBe("A staff invite can be used by at most 5 people.");
  });
});
