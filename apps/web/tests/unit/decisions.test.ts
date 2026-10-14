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
  const msg = problemMessage as unknown as (p: unknown) => unknown;
  const problem = (code: string, status: number, errors: { code: string; message: string }[] = []) => ({
    type: `https://example.test/problems/${code}`,
    title: code,
    status,
    code,
    detail: null,
    errors,
  });
  const text = (p: unknown) => collectStrings(msg(p)).join("\n");

  it("not_publishable lists each reason in words", () => {
    const t = text(
      problem("not_publishable", 409, [
        { code: "critical_checks_failed", message: "x" },
        { code: "unverified_visuals", message: "x" },
        { code: "rights_denied", message: "x" },
      ]),
    );
    expect(t).toContain("A required check has not passed");
    expect(t).toContain("Figures are not verified yet");
    expect(t).toContain("Rights do not permit display");
  });

  it("not_publishable lists only the reasons present", () => {
    const t = text(problem("not_publishable", 409, [{ code: "unverified_visuals", message: "x" }]));
    expect(t).toContain("Figures are not verified yet");
    expect(t).not.toContain("A required check has not passed");
    expect(t).not.toContain("Rights do not permit display");
  });

  it.each([
    ["self_approval_forbidden", 403, "You edited this version last, so someone else must approve it"],
    ["invalid_transition", 409, "This action is not possible in the current state"],
    ["working_version_exists", 409, "A version is already being worked on"],
    ["not_found", 404, "Not found or not visible to you"],
    ["stale_content", 409, "This version changed since you opened it. Reload to see the current content."],
  ])("%s", (code, status, expectedText) => {
    expect(text(problem(code, status))).toContain(expectedText);
  });

  it.each([
    ["unknown_thing", 500],
    ["invalid_cursor", 422],
    ["", 500],
  ])("unknown code %j falls back to 'Something went wrong' plus the code", (code, status) => {
    const t = text(problem(code, status));
    expect(t).toContain("Something went wrong");
    if (code) expect(t).toContain(code);
  });
});
