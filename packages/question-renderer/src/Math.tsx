"use client";

import katex from "katex";
import { useMemo } from "react";

/** The server's KaTeX settings (apps/api/katex/render.mjs). They are part of the rendering contract.
 * `trust` is replaced below by a function that always refuses and records that it did. */
export const KATEX_OPTIONS = {
  throwOnError: true,
  strict: "error",
  trust: false,
  maxExpand: 1000,
  maxSize: 20,
  output: "htmlAndMathml",
} as const;

/** Same ceiling as the server: markup larger than this would stall a browser. */
const MAX_OUTPUT_CHARS = 100_000;

export interface MathProps {
  latex: string;
  display: boolean;
}

export function renderLatex(latex: string, display: boolean): string | null {
  // With trust off, KaTeX does not throw for \href, \url or \includegraphics: it prints the
  // command in red. Asking through a trust function lets us notice and show the fallback instead.
  let untrusted = false;
  const trust = () => {
    untrusted = true;
    return false;
  };
  try {
    const html = katex.renderToString(latex, { ...KATEX_OPTIONS, trust, displayMode: display });
    return untrusted || html.length > MAX_OUTPUT_CHARS ? null : html;
  } catch {
    return null;
  }
}

/** One math node. The only place in the package that sets inner HTML, and only with KaTeX output. */
export function Math({ latex, display }: MathProps) {
  const html = useMemo(() => renderLatex(latex, display), [latex, display]);

  if (html === null) {
    const fallback = (
      <>
        <code className="qr-math-source">{latex}</code>{" "}
        <span className="qr-math-error-note">(math could not be displayed)</span>
      </>
    );
    return display ? (
      <div className="qr-math-block qr-math-error" tabIndex={0} role="group" aria-label="Equation (could not be displayed)">
        {fallback}
      </div>
    ) : (
      <span className="qr-math qr-math-error">{fallback}</span>
    );
  }

  return display ? (
    <div
      className="qr-math-block qr-scroll"
      tabIndex={0}
      role="group"
      aria-label="Equation"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  ) : (
    <span className="qr-math" dangerouslySetInnerHTML={{ __html: html }} />
  );
}
