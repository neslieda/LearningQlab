import type { Metadata } from "next";
import { InviteAdmin } from "./invite-admin";

export const metadata: Metadata = { title: "Invites - Qlab" };

export default function Page() {
  return <InviteAdmin />;
}
