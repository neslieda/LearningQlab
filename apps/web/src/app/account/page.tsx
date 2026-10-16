import type { Metadata } from "next";
import { AccountView } from "./account-view";

export const metadata: Metadata = { title: "Account - Qlab" };

export default function Page() {
  return <AccountView />;
}
