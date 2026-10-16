import { notFound } from "next/navigation";

// Development only: absent from production builds. The component is imported only inside the
// non-production branch so that production bundles contain neither the page nor the token storage code.
export default async function SignInPage() {
  if (process.env.NODE_ENV !== "production") {
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
