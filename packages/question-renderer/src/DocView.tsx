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
function applyMarks(node: ReactNode, marks: readonly Mark[] | undefined): ReactNode {
  if (!marks || marks.length === 0) return node;
  const types = new Set(marks.map((mark) => mark.type));
  let out = node;
  if (types.has("italic")) out = <em>{out}</em>;
  if (types.has("bold")) out = <strong>{out}</strong>;
  if (types.has("sub")) out = <sub>{out}</sub>;
  if (types.has("sup")) out = <sup>{out}</sup>;
  if (types.has("essential")) out = <u className="qr-essential">{out}</u>;
  if (types.has("optional")) out = <span className="qr-optional">({out})</span>;
  return out;
}

function InlineView({ node }: { node: InlineNode }) {
  switch (node.type) {
    case "text":
      // A text node is text: no HTML, no math scanning.
      return <>{applyMarks(node.text, node.marks)}</>;
    case "math_inline":
      return <>{applyMarks(<Math latex={node.attrs.latex} display={false} />, node.marks)}</>;
    case "quantity": {
      const { value, unit, uncertainty } = node.attrs;
      let text = value;
      if (uncertainty) text += ` ± ${uncertainty}`;
      if (unit) text += `${THIN_SPACE}${unit}`;
      return <>{applyMarks(<span className="qr-quantity">{text}</span>, node.marks)}</>;
    }
    case "hard_break":
      return <br />;
    default:
      return null;
  }
}

function ParagraphView({ node }: { node: Paragraph }) {
  return (
    <p>
      {node.content.map((child, index) => (
        <InlineView key={index} node={child} />
      ))}
    </p>
  );
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
              {node.content.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.content.map((cell, cellIndex) => {
                    const span = { colSpan: cell.attrs.colspan, rowSpan: cell.attrs.rowspan };
                    const children = cell.content.map((paragraph, i) => <ParagraphView key={i} node={paragraph} />);
                    return cell.type === "table_header" ? (
                      <th key={cellIndex} scope={rowIndex === 0 ? "col" : "row"} {...span}>
                        {children}
                      </th>
                    ) : (
                      <td key={cellIndex} {...span}>
                        {children}
                      </td>
                    );
                  })}
                </tr>
              ))}
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
