import type { Metadata } from "next";
import { Suspense } from "react";
import { SignInView } from "./sign-in-view";

export const metadata: Metadata = { title: "Sign in - Qlab" };

export default function Page() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <SignInView />
    </Suspense>
  );
}
