import Link from "next/link";
import { PRIVACY_NOTICE } from "@/lib/learn";

/** The short notice shown where answers are given and managed (wording to be reviewed by the owner). */
export function PrivacyNotice({ withLink = true }: { withLink?: boolean }) {
  return (
    <section aria-labelledby="privacy-notice-heading" className="space-y-1 rounded border border-[var(--page-border)] p-3 text-sm">
      <h2 id="privacy-notice-heading" className="font-medium">
        Your answers and your privacy
      </h2>
      <p>{PRIVACY_NOTICE.stored}</p>
      <p>{PRIVACY_NOTICE.notStored}</p>
      <p>{PRIVACY_NOTICE.visibility}</p>
      <p>{PRIVACY_NOTICE.deletion}</p>
      {withLink ? (
        <p>
          <Link href="/privacy" className="underline">
            Privacy details
          </Link>
        </p>
      ) : null}
    </section>
  );
}
