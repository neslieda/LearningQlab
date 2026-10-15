"use client";

import { ReactNodeViewRenderer, NodeViewWrapper, type NodeViewProps } from "@tiptap/react";
import { renderLatex } from "@qlab/question-renderer";
import { useId, useRef, useState } from "react";
import { LatexForm } from "./LatexForm";
import { manifest } from "./manifest";

/** Click or Enter on a math node opens the LaTeX field; Apply writes it back to the node. */
function MathView({ node, updateAttributes, deleteNode, extension }: NodeViewProps) {
  const display = extension.name === "math_block";
  const latex = String(node.attrs.latex ?? "");
  const [open, setOpen] = useState(false);
  const button = useRef<HTMLButtonElement>(null);
  const html = renderLatex(latex, display);
  const close = () => {
    setOpen(false);
    requestAnimationFrame(() => button.current?.focus());
  };

  return (
    <NodeViewWrapper as={display ? "div" : "span"} className={display ? "qe-math-block" : "qe-math-inline"} contentEditable={false}>
      <button
        ref={button}
        type="button"
        className="qe-node-button"
        aria-label={`Edit ${display ? "block" : "inline"} equation: ${latex}`}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
      >
        {html ? <span dangerouslySetInnerHTML={{ __html: html }} /> : <code>{latex}</code>}
      </button>
      {open ? (
        <LatexForm
          initial={latex}
          display={display}
          onApply={(next) => {
            updateAttributes({ latex: next });
            close();
          }}
          onCancel={close}
          onDelete={() => deleteNode()}
        />
      ) : null}
    </NodeViewWrapper>
  );
}

const QUANTITY_FIELDS = [
  { name: "value", label: "Value" },
  { name: "unit", label: "Unit" },
  { name: "param", label: "Parameter name" },
  { name: "uncertainty", label: "Uncertainty" },
] as const;

type QuantityAttr = (typeof QUANTITY_FIELDS)[number]["name"];

/** Empty text is a legal value only for optional attrs (null) and for the unit (""). */
export function quantityProblems(values: Record<QuantityAttr, string>): Partial<Record<QuantityAttr, string>> {
  const specs = manifest.nodes.quantity!.attrs;
  const out: Partial<Record<QuantityAttr, string>> = {};
  for (const { name, label } of QUANTITY_FIELDS) {
    const spec = specs[name]!;
    const v = values[name];
    if (v === "") {
      if (spec.required) out[name] = `${label} is required.`;
    } else if (spec.pattern && !new RegExp(spec.pattern).test(v)) {
      out[name] = `${label} has an invalid format.`;
    }
  }
  return out;
}

function QuantityView({ node, updateAttributes, deleteNode }: NodeViewProps) {
  const attrs = node.attrs as Record<QuantityAttr, string | null>;
  const uid = useId();
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<Record<QuantityAttr, string>>({ value: "", unit: "", param: "", uncertainty: "" });
  const button = useRef<HTMLButtonElement>(null);
  const problems = quantityProblems(draft);
  const valid = Object.keys(problems).length === 0;
  const summary = [attrs.value, attrs.uncertainty ? `± ${attrs.uncertainty}` : null, attrs.unit].filter(Boolean).join(" ");

  const openForm = () => {
    setDraft({ value: attrs.value ?? "", unit: attrs.unit ?? "", param: attrs.param ?? "", uncertainty: attrs.uncertainty ?? "" });
    setOpen(true);
  };
  const close = () => {
    setOpen(false);
    requestAnimationFrame(() => button.current?.focus());
  };
  const apply = () => {
    if (!valid) return;
    updateAttributes({
      value: draft.value,
      unit: draft.unit,
      param: draft.param === "" ? null : draft.param,
      uncertainty: draft.uncertainty === "" ? null : draft.uncertainty,
    });
    close();
  };

  return (
    <NodeViewWrapper as="span" className="qe-quantity" contentEditable={false}>
      <button
        ref={button}
        type="button"
        className="qe-node-button"
        aria-label={`Edit quantity: ${summary}`}
        aria-expanded={open}
        onClick={() => (open ? close() : openForm())}
      >
        {summary}
      </button>
      {open ? (
        <div
          className="qe-popover"
          role="group"
          aria-label="Edit quantity"
          onKeyDown={(e) => {
            e.stopPropagation();
            if (e.key === "Escape") {
              e.preventDefault();
              close();
            } else if (e.key === "Enter") {
              e.preventDefault();
              apply();
            }
          }}
        >
          {QUANTITY_FIELDS.map(({ name, label }, i) => (
            <div key={name} className="qe-field">
              <label htmlFor={`${uid}-${name}`}>{label}</label>
              <input
                id={`${uid}-${name}`}
                type="text"
                value={draft[name]}
                autoFocus={i === 0}
                aria-invalid={problems[name] !== undefined}
                aria-describedby={`${uid}-${name}-err`}
                onChange={(e) => setDraft({ ...draft, [name]: e.target.value })}
              />
              <div id={`${uid}-${name}-err`} className="qe-error" role="alert">
                {problems[name]}
              </div>
            </div>
          ))}
          <div className="qe-actions">
            <button type="button" onClick={apply} disabled={!valid}>
              Apply
            </button>
            <button type="button" onClick={close}>
              Cancel
            </button>
            <button type="button" onClick={() => deleteNode()}>
              Delete
            </button>
          </div>
        </div>
      ) : null}
    </NodeViewWrapper>
  );
}

/** A stimulus placement: movable and deletable, never created or edited here. */
function FigureView({ node }: NodeViewProps) {
  const id = String(node.attrs.stimulus_id ?? "");
  return (
    <NodeViewWrapper as="div" className="qe-figure" contentEditable={false} data-drag-handle>
      <span className="qe-chip" role="img" aria-label={`Figure ${id}`}>
        {`Figure (${id})`}
      </span>
    </NodeViewWrapper>
  );
}

export const nodeViews = {
  math_inline: () => ReactNodeViewRenderer(MathView),
  math_block: () => ReactNodeViewRenderer(MathView),
  quantity: () => ReactNodeViewRenderer(QuantityView),
  figure: () => ReactNodeViewRenderer(FigureView),
};
