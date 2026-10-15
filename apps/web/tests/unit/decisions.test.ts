// Slice 7a spec section 3: the decision table and the problem-to-text mapping.
// The return shape of availableActions is not fixed by the spec, so results are flattened to the
// set of action names the spec defines ("Submit for review", "Approve", ...).
import { describe, expect, it } from "vitest";
import { availableActions, problemMessage } from "../../src/lib/decisions";

const STATUSES = [
  "draft",
  "auto_checking",
  "needs_fix",
  "in_review",
  "approved",
  "published",
  "withdrawn",
  "rejected",
] as const;
type Status = (typeof STATUSES)[number];

// Only its element type is used.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const ACTION_NAMES = [
  "Submit for review",
  "Approve",
  "Request changes",
  "Reject",
  "Publish",
  "Withdraw",
  "Republish",
  "Open revision",
] as const;
type ActionName = (typeof ACTION_NAMES)[number];

const call = availableActions as unknown as (s: string, r: string[], w: boolean) => unknown;

function collectStrings(value: unknown, out: string[] = []): string[] {
  if (typeof value === "string") out.push(value);
  else if (Array.isArray(value)) value.forEach((v) => collectStrings(v, out));
  else if (value && typeof value === "object") Object.values(value).forEach((v) => collectStrings(v, out));
  return out;
}

// The spec defines action labels but not machine ids. Accept a label or its snake_case form
// ("Request changes" / "request_changes"); "Submit for review" may also be just "submit".
const CANONICAL: Record<string, ActionName> = {
  submit_for_review: "Submit for review",
  submit: "Submit for review",
  approve: "Approve",
  request_changes: "Request changes",
  reject: "Reject",
  publish: "Publish",
  withdraw: "Withdraw",
  republish: "Republish",
  open_revision: "Open revision",
};
const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");

function names(status: string, roles: string[], working: boolean): string[] {
  const found = collectStrings(call(status, roles, working));
  const mapped = found.map((f) => CANONICAL[norm(f)]).filter((x): x is ActionName => !!x);
  return [...new Set(mapped)].sort();
}

const ROLE_SETS: { label: string; roles: string[]; staff: boolean; publisher: boolean }[] = [
  { label: "no roles", roles: [], staff: false, publisher: false },
  { label: "student only", roles: ["student"], staff: false, publisher: false },
  { label: "teacher + org_admin", roles: ["teacher", "org_admin"], staff: false, publisher: false },
  { label: "reviewer", roles: ["reviewer"], staff: true, publisher: false },
  { label: "content_admin", roles: ["content_admin"], staff: true, publisher: true },
  { label: "platform_admin", roles: ["platform_admin"], staff: true, publisher: true },
  { label: "reviewer + student", roles: ["reviewer", "student"], staff: true, publisher: false },
];

function expected(status: Status, staff: boolean, publisher: boolean, working: boolean): ActionName[] {
  const out: ActionName[] = [];
  if (!staff) return out;
  switch (status) {
    case "draft":
      out.push("Submit for review");
      break;
    case "in_review":
      out.push("Approve", "Request changes", "Reject");
      break;
    case "approved":
      out.push("Request changes");
      if (publisher) out.push("Publish");
      break;
    case "published":
      if (publisher) out.push("Withdraw");
      if (!working) out.push("Open revision");
      break;
    case "withdrawn":
      if (publisher) out.push("Republish");
      if (!working) out.push("Open revision");
      break;
    case "rejected":
      if (!working) out.push("Open revision");
      break;
    default:
      break; // auto_checking, needs_fix: no decision
  }
  return out.sort();
}

describe("availableActions: every cell of the section 3 table", () => {
  for (const status of STATUSES) {
    for (const rs of ROLE_SETS) {
      for (const working of [false, true]) {
        it(`${status} | ${rs.label} | working version ${working ? "yes" : "no"}`, () => {
          expect(names(status, rs.roles, working)).toEqual(expected(status, rs.staff, rs.publisher, working));
        });
      }
    }
  }
});

describe("availableActions: invariants", () => {
  it("auto_checking and needs_fix have no decisions for any role", () => {
    for (const status of ["auto_checking", "needs_fix"]) {
      for (const rs of ROLE_SETS) {
        for (const working of [false, true]) {
          expect(names(status, rs.roles, working)).toEqual([]);
          expect(collectStrings(call(status, rs.roles, working))).toEqual([]);
        }
      }
    }
  });

  it("Publish, Withdraw and Republish are for publishers only", () => {
    for (const status of STATUSES) {
      for (const rs of ROLE_SETS.filter((r) => !r.publisher)) {
        for (const working of [false, true]) {
          const got = names(status, rs.roles, working);
          for (const n of ["Publish", "Withdraw", "Republish"]) expect(got).not.toContain(n);
        }
      }
    }
  });

  it("a user without a staff role gets nothing in any state", () => {
    for (const status of STATUSES) {
      for (const rs of ROLE_SETS.filter((r) => !r.staff)) {
        expect(names(status, rs.roles, false)).toEqual([]);
      }
    }
  });

  it("Open revision is offered only when there is no working version", () => {
    for (const status of ["published", "withdrawn", "rejected"]) {
      expect(names(status, ["reviewer"], false)).toContain("Open revision");
      expect(names(status, ["reviewer"], true)).not.toContain("Open revision");
    }
    for (const status of ["draft", "in_review", "approved", "needs_fix", "auto_checking"]) {
      expect(names(status, ["platform_admin"], false)).not.toContain("Open revision");
    }
  });

  it("does not mutate the roles argument and is deterministic", () => {
    const roles = ["reviewer", "student"];
    const first = JSON.stringify(call("in_review", roles, false));
    expect(roles).toEqual(["reviewer", "student"]);
    expect(JSON.stringify(call("in_review", roles, false))).toBe(first);
  });
});

describe("problemMessage", () => {
  // Shape (exported type ProblemMessage): { message, reasons, followUp }.
  const pm = (code: string | undefined, status: number, errors: { code: string }[] = []) =>
    problemMessage({ code, status, errors });

  it("not_publishable: message plus the reasons in words, in the order given, no follow-up", () => {
    const r = pm("not_publishable", 409, [{ code: "critical_checks_failed" }, { code: "unverified_visuals" }, { code: "rights_denied" }]);
    expect(r.reasons).toEqual(["A required check has not passed", "Figures are not verified yet", "Rights do not permit display"]);
    expect(r.message.length).toBeGreaterThan(0);
    expect(r.followUp).toBeNull();
  });

  it("not_publishable lists only the reasons present", () => {
    expect(pm("not_publishable", 409, [{ code: "unverified_visuals" }]).reasons).toEqual(["Figures are not verified yet"]);
    expect(pm("not_publishable", 409, []).reasons).toEqual([]);
  });

  it.each([
    ["self_approval_forbidden", 403, "You edited this version last, so someone else must approve it", null],
    ["invalid_transition", 409, "This action is not possible in the current state", "reload"],
    ["working_version_exists", 409, "A version is already being worked on", "question"],
    ["not_found", 404, "Not found or not visible to you", null],
    ["stale_content", 409, "This version changed since you opened it. Reload to see the current content.", "reload"],
  ])("%s", (code, status, text, followUp) => {
    const r = pm(code, status);
    expect(r.message).toBe(text);
    expect(r.reasons).toEqual([]);
    expect(r.followUp).toBe(followUp);
  });

  it("status 401 and code unauthenticated lead to sign-in", () => {
    for (const r of [pm("unauthenticated", 401), pm(undefined, 401), pm("whatever", 401), pm("unauthenticated", 500)]) {
      expect(r.followUp).toBe("sign-in");
      expect(r.message.length).toBeGreaterThan(0);
      expect(r.reasons).toEqual([]);
    }
  });

  it.each([
    ["unknown_thing", 500],
    ["invalid_cursor", 422],
  ])("unknown code %j: 'Something went wrong' plus the code, no follow-up", (code, status) => {
    const r = pm(code, status);
    expect(r.message).toContain("Something went wrong");
    expect(r.message).toContain(code);
    expect(r.followUp).toBeNull();
    expect(r.reasons).toEqual([]);
  });
});
