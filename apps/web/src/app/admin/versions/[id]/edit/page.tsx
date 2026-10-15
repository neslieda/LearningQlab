import type { Metadata } from "next";
import { EditView } from "./edit-view";

export const metadata: Metadata = { title: "Edit version - Qlab" };

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <EditView id={id} />;
}
