import type { Role, VersionStatus } from "@qlab/api-client";

export type DecisionAction =
  | "submit"
  | "approve"
  | "request_changes"
  | "reject"
  | "publish"
  | "withdraw"
  | "republish"
  | "open_revision";

export const ACTION_LABEL: Record<DecisionAction, string> = {
  submit: "Submit for review",
  approve: "Approve",
  request_changes: "Request changes",
  reject: "Reject",
  publish: "Publish",
  withdraw: "Withdraw",
  republish: "Republish",
  open_revision: "Open revision",
};

export const REASON_WARNING =
  "Describe the content, not a person. Do not paste question text. Reasons are kept permanently.";

const STAFF: readonly string[] = ["reviewer", "content_admin", "platform_admin"];
const PUBLISHERS: readonly string[] = ["content_admin", "platform_admin"];

export function isStaff(roles: readonly Role[] | readonly string[]): boolean {
  return roles.some((r) => STAFF.includes(r));
}

const INVITERS: readonly string[] = ["teacher", "platform_admin"];

/** Who may open the invite screen (the API enforces it too). */
export function canInvite(roles: readonly Role[] | readonly string[]): boolean {
  return roles.some((r) => INVITERS.includes(r));
}

export type InviteRole = "student" | "teacher" | "reviewer" | "content_admin" | "platform_admin";

/** The roles the caller may put on an invite: a teacher only students, a platform admin any role. */
export function invitableRoles(roles: readonly Role[] | readonly string[]): InviteRole[] {
  if (roles.includes("platform_admin")) return ["student", "teacher", "reviewer", "content_admin", "platform_admin"];
  if (roles.includes("teacher")) return ["student"];
  return [];
}

export function canPublish(roles: readonly Role[] | readonly string[]): boolean {
  return roles.some((r) => PUBLISHERS.includes(r));
}

export interface ActionItem {
  id: DecisionAction;
  label: string;
}

/** The decisions the panel offers, in table order (docs/slices/M1G-7A-INCELEME.md section 3). The API enforces the rules. */
export function availableActions(
  status: VersionStatus | string,
  roles: readonly Role[] | readonly string[],
  hasWorkingVersion: boolean,
): ActionItem[] {
  if (!isStaff(roles)) return [];
  const publisher = canPublish(roles);
  const out: DecisionAction[] = [];
  switch (status) {
    case "draft":
      out.push("submit");
      break;
    case "in_review":
      out.push("approve", "request_changes", "reject");
      break;
    case "approved":
      out.push("request_changes");
      if (publisher) out.push("publish");
      break;
    case "published":
      if (publisher) out.push("withdraw");
      break;
    case "withdrawn":
      if (publisher) out.push("republish");
      break;
  }
  if ((status === "published" || status === "withdrawn" || status === "rejected") && !hasWorkingVersion) {
    out.push("open_revision");
  }
  return out.map((id) => ({ id, label: ACTION_LABEL[id] }));
}

/** Statuses in which the content can be edited in the browser (docs/slices/M1G-7B-EDITOR.md section 4). */
export function isEditableStatus(status: VersionStatus | string): boolean {
  return status === "draft" || status === "needs_fix";
}

/** Staff may edit a `draft` or `needs_fix` version. The API enforces this too. */
export function canEdit(status: VersionStatus | string, roles: readonly Role[] | readonly string[]): boolean {
  return isStaff(roles) && isEditableStatus(status);
}

/** Version statuses that count as "being worked on" (not published, withdrawn or rejected). */
export function isWorkingStatus(status: VersionStatus | string): boolean {
  return ["draft", "auto_checking", "needs_fix", "in_review", "approved"].includes(status);
}

export interface ProblemLike {
  status?: number;
  code?: string;
  errors?: ReadonlyArray<{ code: string; message?: string; location?: string | null }>;
}

export type FollowUp = "reload" | "sign-in" | "question" | null;

export interface ProblemMessage {
  message: string;
  /** Reasons, for `not_publishable`. */
  reasons: string[];
  followUp: FollowUp;
}

export const MFA_MESSAGE = "Staff access needs two-step verification. Sign out and use Staff sign-in.";
export const INVITE_INVALID_MESSAGE = "This invite link is not valid. Ask for a new one.";

const REASONS: Record<string, string> = {
  critical_checks_failed: "A required check has not passed",
  unverified_visuals: "Figures are not verified yet",
  rights_denied: "Rights do not permit display",
};

export function problemMessage(problem: ProblemLike): ProblemMessage {
  const code = problem.code ?? "";
  if (problem.status === 401 || code === "unauthenticated") {
    return { message: "Your session has ended. Sign in again.", reasons: [], followUp: "sign-in" };
  }
  switch (code) {
    case "not_publishable":
      return {
        message: "This version cannot be published",
        reasons: (problem.errors ?? []).map((e) => REASONS[e.code] ?? `Something went wrong (${e.code})`),
        followUp: null,
      };
    case "self_approval_forbidden":
      return { message: "You edited this version last, so someone else must approve it", reasons: [], followUp: null };
    case "invalid_transition":
      return { message: "This action is not possible in the current state", reasons: [], followUp: "reload" };
    case "stale_content":
      return {
        message: "This version changed since you opened it. Reload to see the current content.",
        reasons: [],
        followUp: "reload",
      };
    case "working_version_exists":
      return { message: "A version is already being worked on", reasons: [], followUp: "question" };
    case "own_content_rights_unavailable":
      return {
        message: "New questions cannot be created right now: the platform's content rights record is missing. Ask a platform admin.",
        reasons: [],
        followUp: null,
      };
    case "mfa_required":
      return { message: MFA_MESSAGE, reasons: [], followUp: null };
    case "invite_role_forbidden":
      return { message: "You cannot invite someone to this role.", reasons: [], followUp: null };
    case "invite_not_found":
      return { message: INVITE_INVALID_MESSAGE, reasons: [], followUp: null };
    case "not_found":
      return { message: "Not found or not visible to you", reasons: [], followUp: null };
    default:
      return { message: `Something went wrong${code ? ` (${code})` : ""}`, reasons: [], followUp: null };
  }
}
