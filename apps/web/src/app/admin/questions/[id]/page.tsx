import type { Metadata } from "next";
import { QuestionView } from "./question-view";

export const metadata: Metadata = { title: "Question - Qlab" };

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <QuestionView id={id} />;
}
