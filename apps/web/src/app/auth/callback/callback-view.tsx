"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { completeSignIn } from "@/lib/oidc";
import { ME_KEY, SESSION_KEY } from "@/lib/use-me";

export function CallbackView() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let alive = true;
    completeSignIn().then(
      async (next) => {
        await queryClient.invalidateQueries({ queryKey: ME_KEY });
        await queryClient.invalidateQueries({ queryKey: SESSION_KEY });
        if (alive) router.replace(next);
      },
      () => {
        if (alive) setFailed(true);
      },
    );
    return () => {
      alive = false;
    };
  }, [router, queryClient]);

  if (failed) {
    return (
      <div className="space-y-2">
        <p role="alert">Sign-in did not complete.</p>
        <Link href="/sign-in" className="underline">
          Try again
        </Link>
      </div>
    );
  }
  return <p role="status">Signing you in...</p>;
}
