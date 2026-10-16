import type { Metadata } from "next";
import { InviteView } from "./invite-view";

export const metadata: Metadata = { title: "Invite - Qlab", referrer: "no-referrer" };

// The invite code is in the URL fragment (`/invite#<code>`): it never reaches a server or a log.
export default function Page() {
  return <InviteView />;
}
