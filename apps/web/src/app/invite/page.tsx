import type { Metadata } from "next";
import { InviteView } from "./invite-view";

export const metadata: Metadata = { title: "Invite - Qlab", referrer: "no-referrer" };

export default async function Page({ params }: { params: Promise<{ code: string }> }) {
  const { code } = await params;
  return <InviteView code={code} />;
}
