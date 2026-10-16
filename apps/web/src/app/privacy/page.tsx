import type { Metadata } from "next";
import Link from "next/link";
import { PRIVACY_NOTICE } from "@/lib/learn";

export const metadata: Metadata = { title: "Privacy - Qlab" };

export default function Page() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Privacy</h1>
      <section aria-labelledby="p-stored" className="space-y-1">
        <h2 id="p-stored" className="text-lg font-medium">What is stored</h2>
        <p>{PRIVACY_NOTICE.stored}</p>
        <p>For a multiple-choice answer we also store whether it was correct. For a written answer we store the part you answered.</p>
        <p>Each answer is tied to the exact version of the question you saw, so it stays meaningful if the question is corrected later.</p>
      </section>
      <section aria-labelledby="p-not" className="space-y-1">
        <h2 id="p-not" className="text-lg font-medium">What is not stored</h2>
        <p>{PRIVACY_NOTICE.notStored} We do not measure how long you take.</p>
        <p>Your answers are not sent to any AI service.</p>
      </section>
      <section aria-labelledby="p-who" className="space-y-1">
        <h2 id="p-who" className="text-lg font-medium">Who can see your answers</h2>
        <p>{PRIVACY_NOTICE.visibility} Teachers and staff cannot see your answers in the app.</p>
        <p>Backups of the database are kept for 14 days and then removed.</p>
      </section>
      <section aria-labelledby="p-delete" className="space-y-1">
        <h2 id="p-delete" className="text-lg font-medium">How to delete your answers</h2>
        <p>
          Open your{" "}
          <Link href="/account" className="underline">
            account page
          </Link>{" "}
          and choose &ldquo;Delete all my answers&rdquo;. Deleting your account also deletes your answers.
        </p>
      </section>
    </div>
  );
}
