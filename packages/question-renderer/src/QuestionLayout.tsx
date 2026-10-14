"use client";

import { useId, useMemo, type ReactNode } from "react";
import type { Doc } from "@qlab/api-client";
import { StimuliContext } from "./context";
import { DocView } from "./DocView";
import type { DocBlock, Level, OptionKey, OptionLayout, StimulusInfo } from "./types";

/** Internal, normalised shapes: learner and staff views share one layout. Not exported from the package. */
export interface LayoutPart {
  id: string;
  label: string;
  marks: number;
  leadIn?: Doc | null;
  body: Doc;
}

export interface LayoutOption {
  key: OptionKey;
  cells: Doc[];
}

export interface LayoutMcq {
  layout: OptionLayout;
  columnHeaders: Doc[];
  statements: Doc[];
  options: LayoutOption[];
}

export interface LayoutQuestion {
  examSection: string;
  levels: Level[];
  totalMarks: number;
  stem: Doc;
  stimuli: StimulusInfo[];
  parts: LayoutPart[];
  mcq: LayoutMcq | null;
}

const ROMAN: [number, string][] = [
  [10, "X"],
  [9, "IX"],
  [5, "V"],
  [4, "IV"],
  [1, "I"],
];

export function toRoman(n: number): string {
  let rest = n;
  let out = "";
  for (const [value, symbol] of ROMAN) {
    while (rest >= value) {
      out += symbol;
      rest -= value;
    }
  }
  return out;
}

export function marksText(n: number): string {
  return n === 1 ? "[1 mark]" : `[${n} marks]`;
}

/** Visible "[2]"; a screen reader says "2 marks". */
function PartMarks({ marks }: { marks: number }) {
  return (
    <span className="qr-marks">
      <span aria-hidden="true">{`[${marks}]`}</span>
      <span className="qr-sr-only">{marks === 1 ? "1 mark" : `${marks} marks`}</span>
    </span>
  );
}

function collectFigureIds(blocks: readonly DocBlock[], into: Set<string>): void {
  for (const block of blocks) if (block.type === "figure") into.add(block.attrs.stimulus_id);
}

function docsOf(question: LayoutQuestion): Doc[] {
  const docs: Doc[] = [question.stem];
  for (const part of question.parts) {
    if (part.leadIn) docs.push(part.leadIn);
    docs.push(part.body);
  }
  if (question.mcq) {
    docs.push(...question.mcq.statements, ...question.mcq.columnHeaders);
    for (const option of question.mcq.options) docs.push(...option.cells);
  }
  return docs;
}

/** "A" ... "D" label plus the correct-answer marker. */
function OptionKeyLabel({ optionKey, correct }: { optionKey: OptionKey; correct: boolean }) {
  return (
    <>
      <span className="qr-option-key">{optionKey}</span>
      {correct && <span className="qr-correct-badge">Correct answer</span>}
    </>
  );
}

export function McqBlock({ mcq, correctKey }: { mcq: LayoutMcq; correctKey?: OptionKey | null }) {
  const statements = mcq.layout === "roman_statements" && mcq.statements.length > 0 && (
    <ol className="qr-statements" aria-label="Statements">
      {mcq.statements.map((statement, index) => (
        <li key={index} className="qr-statement">
          <span className="qr-statement-label">{`${toRoman(index + 1)}.`}</span>
          <div className="qr-statement-body">
            <DocView doc={statement} />
          </div>
        </li>
      ))}
    </ol>
  );

  if (mcq.layout === "two_column_table") {
    return (
      <div className="qr-mcq qr-mcq-table">
        <div className="qr-scroll" tabIndex={0} role="group" aria-label="Answer options">
          <table className="qr-table qr-options-table">
            <thead>
              <tr>
                <th scope="col">
                  <span className="qr-sr-only">Option</span>
                </th>
                {mcq.columnHeaders.map((header, index) => (
                  <th key={index} scope="col">
                    <DocView doc={header} />
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {mcq.options.map((option) => (
                <tr key={option.key} className={option.key === correctKey ? "qr-option-correct" : undefined}>
                  <th scope="row">
                    <OptionKeyLabel optionKey={option.key} correct={option.key === correctKey} />
                  </th>
                  {option.cells.map((cell, index) => (
                    <td key={index}>
                      <DocView doc={cell} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return (
    <div className={`qr-mcq qr-mcq-${mcq.layout.replace(/_/g, "-")}`}>
      {statements}
      <ol className="qr-options" aria-label="Answer options">
        {mcq.options.map((option) => (
          <li key={option.key} className={option.key === correctKey ? "qr-option qr-option-correct" : "qr-option"}>
            <OptionKeyLabel optionKey={option.key} correct={option.key === correctKey} />
            <div className="qr-option-body">
              {option.cells.map((cell, index) => (
                <DocView key={index} doc={cell} />
              ))}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

function PartSection({
  part,
  displayLabel,
  level,
  footer,
}: {
  part: LayoutPart;
  displayLabel: string;
  level: 3 | 4;
  footer?: ReactNode;
}) {
  const headingId = useId();
  const Heading = level === 3 ? "h3" : "h4";
  return (
    <section className={level === 3 ? "qr-part" : "qr-part qr-subpart"} aria-labelledby={headingId}>
      <div className="qr-part-head">
        <Heading id={headingId} className="qr-part-label">
          {displayLabel}
        </Heading>
        <PartMarks marks={part.marks} />
      </div>
      {part.leadIn && (
        <div className="qr-lead-in">
          <DocView doc={part.leadIn} />
        </div>
      )}
      <div className="qr-part-body">
        <DocView doc={part.body} />
      </div>
      {footer}
    </section>
  );
}

type PartEntry =
  | { kind: "single"; part: LayoutPart }
  | { kind: "group"; letter: string; showLetter: boolean; parts: { part: LayoutPart; sub: string }[] };

function groupParts(parts: LayoutPart[]): PartEntry[] {
  const ownLetters = new Set(parts.filter((p) => !p.label.includes(".")).map((p) => p.label));
  const entries: PartEntry[] = [];
  for (const part of parts) {
    const dot = part.label.indexOf(".");
    if (dot < 0) {
      entries.push({ kind: "single", part });
      continue;
    }
    const letter = part.label.slice(0, dot);
    const sub = part.label.slice(dot + 1);
    const last = entries[entries.length - 1];
    if (last && last.kind === "group" && last.letter === letter) {
      last.parts.push({ part, sub });
    } else {
      // The letter label is written once, before the first sub-part of that letter.
      entries.push({ kind: "group", letter, showLetter: !ownLetters.has(letter), parts: [{ part, sub }] });
    }
  }
  return entries;
}

function GroupLetterHeading({ letter }: { letter: string }) {
  return <h3 className="qr-part-label qr-part-group-label">{`(${letter})`}</h3>;
}

export interface QuestionLayoutProps {
  question: LayoutQuestion;
  showDescriptions: boolean;
  renderPartFooter?: (partId: string) => ReactNode;
  /** After the options, inside the question. */
  mcqFooter?: ReactNode;
  /** After everything else (staff answers). */
  after?: ReactNode;
  correctKey?: OptionKey | null;
}

export function QuestionLayout({
  question,
  showDescriptions,
  renderPartFooter,
  mcqFooter,
  after,
  correctKey,
}: QuestionLayoutProps) {
  const titleId = useId();
  const context = useMemo(
    () => ({ stimuli: new Map(question.stimuli.map((s) => [s.id, s])), showDescription: showDescriptions }),
    [question.stimuli, showDescriptions],
  );
  const unplaced = useMemo(() => {
    const placed = new Set<string>();
    for (const doc of docsOf(question)) collectFigureIds(doc.content, placed);
    return question.stimuli.filter((s) => !placed.has(s.id));
  }, [question]);

  const entries = groupParts(question.parts);

  return (
    <StimuliContext.Provider value={context}>
      <article className="qr qr-question" aria-labelledby={titleId}>
        <h2 id={titleId} className="qr-question-title">
          <span className="qr-section">{question.examSection}</span>
          {question.levels.map((level) => (
            <span key={level} className="qr-level">
              {level.toUpperCase()}
            </span>
          ))}
          <span className="qr-total">{marksText(question.totalMarks)}</span>
        </h2>

        <div className="qr-stem">
          <DocView doc={question.stem} />
        </div>

        {unplaced.length > 0 && (
          <div className="qr-stimuli">
            {unplaced.map((stimulus) => (
              <DocView
                key={stimulus.id}
                doc={{ type: "doc", content: [{ type: "figure", attrs: { stimulus_id: stimulus.id } }] }}
              />
            ))}
          </div>
        )}

        {question.mcq && (
          <>
            <McqBlock mcq={question.mcq} correctKey={correctKey} />
            {mcqFooter}
          </>
        )}

        {entries.map((entry) => {
          if (entry.kind === "single") {
            return (
              <PartSection
                key={entry.part.id}
                part={entry.part}
                displayLabel={`(${entry.part.label})`}
                level={3}
                footer={renderPartFooter?.(entry.part.id)}
              />
            );
          }
          return (
            <div key={entry.parts[0]!.part.id} className="qr-part-group">
              {entry.showLetter && <GroupLetterHeading letter={entry.letter} />}
              {entry.parts.map(({ part, sub }) => (
                <PartSection
                  key={part.id}
                  part={part}
                  displayLabel={`(${sub})`}
                  level={entry.showLetter ? 4 : 3}
                  footer={renderPartFooter?.(part.id)}
                />
              ))}
            </div>
          );
        })}
        {after}
      </article>
    </StimuliContext.Provider>
  );
}
