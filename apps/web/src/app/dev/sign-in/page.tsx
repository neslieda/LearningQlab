import { notFound } from "next/navigation";
import { config } from "@/lib/config";

// Local only (NEXT_PUBLIC_QLAB_ENV=local, inlined at build time): any other build answers 404. The component is
// imported only inside the local branch so that other bundles contain no development sign-in UI.
export default async function SignInPage() {
  if (config.local) {
    const { SignIn } = await import("./sign-in");
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold">Development sign-in</h1>
        <SignIn />
      </div>
    );
  }
  notFound();
}
