import type { Metadata } from "next";
import { Suspense } from "react";
import { QuestionList } from "./question-list";

export const metadata: Metadata = { title: "Questions - Qlab" };

export default function Page() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <QuestionList />
    </Suspense>
  );
}
