import type { Metadata } from "next";
import { NewQuestionView } from "./new-question-view";

export const metadata: Metadata = { title: "New question - Qlab" };

export default function Page() {
  return <NewQuestionView />;
}
