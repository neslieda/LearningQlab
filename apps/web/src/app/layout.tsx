import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import { Providers } from "./providers";
import { SiteHeader } from "./site-header";

export const metadata: Metadata = { title: "Qlab", description: "Question bank and practice platform" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <Providers>
          <a
            href="#main"
            className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:bg-[var(--page-bg)] focus:p-2"
          >
            Skip to content
          </a>
          <SiteHeader />
          <main id="main" className="mx-auto w-full max-w-5xl px-4 py-6">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
