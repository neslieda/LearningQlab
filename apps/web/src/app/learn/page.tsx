import type { Metadata } from "next";
import { Suspense } from "react";
import { LearnList } from "./learn-list";

export const metadata: Metadata = { title: "Practice - Qlab" };

export default function Page() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <LearnList />
    </Suspense>
  );
}
