"use client";

import { Fragment, useContext, type ReactNode } from "react";
import type { Doc } from "@qlab/api-client";
import { StimuliContext } from "./context";
import { Math } from "./Math";
import type { DocBlock, InlineNode, Mark, Paragraph } from "./types";

const THIN_SPACE = " ";

/** "schematic_diagram" -> "Schematic diagram". */
export function readableKind(kind: string): string {
  const words = kind.replace(/_/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

/** Wraps in a fixed order, so the order of `marks` in the data never changes the output. */
function applyMarks(node: ReactNode, marks: readonly Mark[] | undefined, skipOptional = false): ReactNode {
  if (!marks || marks.length === 0) return node;
  const types = new Set(marks.map((mark) => mark.type));
  let out = node;
  if (types.has("italic")) out = <em>{out}</em>;
  if (types.has("bold")) out = <strong>{out}</strong>;
  if (types.has("sub")) out = <sub>{out}</sub>;
  if (types.has("sup")) out = <sup>{out}</sup>;
  if (types.has("essential")) {
    out = (
      <u className="qr-essential">
        {out}
        <span className="qr-sr-only"> essential</span>
      </u>
    );
  }
  // Normally ParagraphView wraps a whole run of optional nodes in one pair of guillemets.
  if (types.has("optional") && !skipOptional) {
    out = (
      <span className="qr-optional">
        {"\u00ab"}
        {out}
        {"\u00bb"}
      </span>
    );
  }
  return out;
}

function InlineView({ node, skipOptional = false }: { node: InlineNode; skipOptional?: boolean }) {
  switch (node.type) {
    case "text":
      // A text node is text: no HTML, no math scanning.
      return <>{applyMarks(node.text, node.marks, skipOptional)}</>;
    case "math_inline":
      return <>{applyMarks(<Math latex={node.attrs.latex} display={false} />, node.marks, skipOptional)}</>;
    case "quantity": {
      const { value, unit, uncertainty } = node.attrs;
      let text = value;
      if (uncertainty) text += ` ± ${uncertainty}`;
      if (unit) text += `${THIN_SPACE}${unit}`;
      return <>{applyMarks(<span className="qr-quantity">{text}</span>, node.marks, skipOptional)}</>;
    }
    case "hard_break":
      return <br />;
    default:
      return null;
  }
}

const isOptional = (node: InlineNode): boolean =>
  "marks" in node && (node.marks ?? []).some((mark) => mark.type === "optional");

function ParagraphView({ node }: { node: Paragraph }) {
  // Maximal runs of adjacent optional nodes share one pair of guillemets.
  const children: ReactNode[] = [];
  let index = 0;
  while (index < node.content.length) {
    const current = node.content[index]!;
    if (isOptional(current)) {
      let end = index;
      while (end < node.content.length && isOptional(node.content[end]!)) end += 1;
      children.push(
        <span key={index} className="qr-optional">
          {"\u00ab"}
          {node.content.slice(index, end).map((child, i) => (
            <InlineView key={i} node={child} skipOptional />
          ))}
          {"\u00bb"}
        </span>,
      );
      index = end;
    } else {
      children.push(<InlineView key={index} node={current} />);
      index += 1;
    }
  }
  return <p>{children}</p>;
}

function ScrollBox({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="qr-scroll" tabIndex={0} role="group" aria-label={label}>
      {children}
    </div>
  );
}

function FigurePlaceholder({ stimulusId }: { stimulusId: string }) {
  const { stimuli, showDescription } = useContext(StimuliContext);
  const stimulus = stimuli.get(stimulusId);
  const kind = stimulus ? readableKind(stimulus.kind) : null;
  const description = showDescription ? stimulus?.description : undefined;
  let label = kind ? `Figure: ${kind}` : "Figure";
  if (description) label += `. Description (staff only): ${description}`;
  return (
    <figure className="qr-figure" role="img" aria-label={label}>
      <span className="qr-figure-title">Figure</span>
      {kind && <span className="qr-figure-kind">{kind}</span>}
      {description && (
        <div className="qr-figure-description">
          <span className="qr-figure-description-title">Description (staff only)</span>
          <p>{description}</p>
        </div>
      )}
    </figure>
  );
}

function BlockView({ node }: { node: DocBlock }) {
  switch (node.type) {
    case "paragraph":
      return <ParagraphView node={node} />;
    case "math_block":
      return <Math latex={node.attrs.latex} display />;
    case "figure":
      return <FigurePlaceholder stimulusId={node.attrs.stimulus_id} />;
    case "bullet_list":
    case "ordered_list": {
      const items = node.content.map((item, index) => (
        <li key={index}>
          {item.content.map((paragraph, i) => (
            <ParagraphView key={i} node={paragraph} />
          ))}
        </li>
      ));
      return node.type === "bullet_list" ? <ul>{items}</ul> : <ol>{items}</ol>;
    }
    case "table":
      return (
        <ScrollBox label="Table">
          <table className="qr-table">
            <tbody>
              {node.content.map((row, rowIndex) => {
                const headerRow = row.content.every((cell) => cell.type === "table_header");
                return (
                <tr key={rowIndex}>
                  {row.content.map((cell, cellIndex) => {
                    const span = { colSpan: cell.attrs.colspan, rowSpan: cell.attrs.rowspan };
                    const children = cell.content.map((paragraph, i) => <ParagraphView key={i} node={paragraph} />);
                    return cell.type === "table_header" ? (
                      <th
                        key={cellIndex}
                        scope={headerRow ? (cell.attrs.colspan > 1 ? "colgroup" : "col") : "row"}
                        {...span}
                      >
                        {children}
                      </th>
                    ) : (
                      <td key={cellIndex} {...span}>
                        {children}
                      </td>
                    );
                  })}
                </tr>
                );
              })}
            </tbody>
          </table>
        </ScrollBox>
      );
    default:
      return null;
  }
}

export interface DocViewProps {
  doc: Doc;
}

/** A rich-text document. Figure placeholders look their stimulus up in the surrounding question view. */
export function DocView({ doc }: DocViewProps) {
  return (
    <div className="qr-doc">
      {doc.content.map((block, index) => (
        <Fragment key={index}>
          <BlockView node={block} />
        </Fragment>
      ))}
    </div>
  );
}
