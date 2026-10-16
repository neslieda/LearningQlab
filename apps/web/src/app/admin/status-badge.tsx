import type { VersionStatus } from "@qlab/api-client";

const TONE: Record<VersionStatus, string> = {
  draft: "border-gray-500",
  auto_checking: "border-gray-500",
  needs_fix: "border-amber-600",
  in_review: "border-blue-600",
  approved: "border-green-700",
  published: "border-green-700 font-semibold",
  withdrawn: "border-amber-600",
  rejected: "border-red-700",
};

/** Colour is never the only cue: the status is always written out. */
export function StatusBadge({ status }: { status: VersionStatus }) {
  return (
    <span className={`inline-block whitespace-nowrap rounded border px-1.5 py-0.5 text-sm ${TONE[status]}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}

export function ScrollBox({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div role="region" aria-label={label} tabIndex={0} className="overflow-x-auto">
      {children}
    </div>
  );
}
