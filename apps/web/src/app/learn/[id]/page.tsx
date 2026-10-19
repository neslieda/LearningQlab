import type { Metadata } from "next";
import { Solve } from "./solve";

export const metadata: Metadata = { title: "Practice question - Qlab" };

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <Solve id={id} />;
}
