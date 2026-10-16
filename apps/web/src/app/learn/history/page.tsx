import type { Metadata } from "next";
import { History } from "./history";

export const metadata: Metadata = { title: "My answers - Qlab" };

export default function Page() {
  return <History />;
}
