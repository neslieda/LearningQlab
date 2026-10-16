import type { Metadata } from "next";
import { CallbackView } from "./callback-view";

export const metadata: Metadata = { title: "Signing in - Qlab" };

export default function Page() {
  return <CallbackView />;
}
