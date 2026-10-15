import type { Metadata } from "next";
import { VersionView } from "./version-view";

export const metadata: Metadata = { title: "Version - Qlab" };

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <VersionView id={id} />;
}
