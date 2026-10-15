"use client";

import katex from "katex";
import { KATEX_OPTIONS, renderLatex } from "@qlab/question-renderer";
import { useId, useMemo, useState, type KeyboardEvent } from "react";

/** Why KaTeX refused a formula, in words for the person editing it. */
export function latexProblem(latex: string, display: boolean): string | null {
  if (latex.trim() === "") return "LaTeX cannot be empty.";
  if (renderLatex(latex, display) !== null) return null;
  try {
    katex.renderToString(latex, { ...KATEX_OPTIONS, trust: false, displayMode: display });
    return "This formula cannot be displayed (it uses a command that is not allowed, or is too large).";
  } catch (e) {
    const raw = e instanceof Error ? e.message : String(e);
    return `KaTeX cannot render this formula: ${raw.replace(/^KaTeX parse error:\s*/, "")}`;
  }
}

export interface LatexFormProps {
  initial: string;
  display: boolean;
  applyLabel?: string;
  onApply: (latex: string) => void;
  onCancel: () => void;
  onDelete?: () => void;
}

/** LaTeX field with a live KaTeX preview; the value is only accepted when KaTeX can render it. */
export function LatexForm({ initial, display, applyLabel = "Apply", onApply, onCancel, onDelete }: LatexFormProps) {
  const id = useId();
  const [latex, setLatex] = useState(initial);
  const problem = useMemo(() => latexProblem(latex, display), [latex, display]);
  const html = useMemo(() => (problem ? null : renderLatex(latex, display)), [latex, display, problem]);

  const apply = () => {
    if (!problem) onApply(latex);
  };
  const onKey = (e: KeyboardEvent) => {
    e.stopPropagation();
    if (e.key === "Escape") {
      e.preventDefault();
      onCancel();
    } else if (e.key === "Enter" && (!display || e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      apply();
    }
  };

  return (
    <div className="qe-popover" role="group" aria-label={display ? "Edit block equation" : "Edit inline equation"} onKeyDown={onKey}>
      <label htmlFor={`${id}-latex`}>LaTeX</label>
      {display ? (
        <textarea
          id={`${id}-latex`}
          value={latex}
          rows={3}
          autoFocus
          spellCheck={false}
          aria-invalid={problem !== null}
          aria-describedby={`${id}-msg`}
          onChange={(e) => setLatex(e.target.value)}
        />
      ) : (
        <input
          id={`${id}-latex`}
          type="text"
          value={latex}
          autoFocus
          spellCheck={false}
          aria-invalid={problem !== null}
          aria-describedby={`${id}-msg`}
          onChange={(e) => setLatex(e.target.value)}
        />
      )}
      <div id={`${id}-msg`} className="qe-error" role="alert">
        {problem}
      </div>
      <div className="qe-preview" aria-label="Preview">
        {html ? <span dangerouslySetInnerHTML={{ __html: html }} /> : <span className="qe-muted">No preview</span>}
      </div>
      <div className="qe-actions">
        <button type="button" onClick={apply} disabled={problem !== null}>
          {applyLabel}
        </button>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
        {onDelete ? (
          <button type="button" onClick={onDelete}>
            Delete
          </button>
        ) : null}
      </div>
    </div>
  );
}
