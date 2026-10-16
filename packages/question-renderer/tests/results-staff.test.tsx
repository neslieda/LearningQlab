import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { QuestionDocument } from "@qlab/api-client";
import { McqResultView, QuestionDocumentView } from "../src";
import { KEYS, d, doc, figure, mcqQuestion, mcqResult, para, text } from "./helpers";

describe("McqResultView (3.2)", () => {
  it.each(KEYS)("identifies option %s as correct by text, and only that one", (key) => {
    const { container } = render(<McqResultView result={mcqResult(key)} question={mcqQuestion("single_value")} />);
    const items = within(container.querySelector("ol") as HTMLElement).getAllByRole("listitem");
    expect(items).toHaveLength(4);
    items.forEach((li, i) => {
      const isCorrect = KEYS[i] === key;
      expect(/correct/i.test(li.textContent!)).toBe(isCorrect);
    });
  });

  it("identifies the correct option even when the learner was wrong", () => {
    const { container } = render(
      <McqResultView result={mcqResult("B", false)} question={mcqQuestion("single_value")} />,
    );
    const items = within(container.querySelector("ol") as HTMLElement).getAllByRole("listitem");
    expect(items[1]!.textContent).toMatch(/correct/i);
    expect(items[0]!.textContent).not.toMatch(/correct/i);
  });

  it("works with the two_column_table layout", () => {
    const { container } = render(
      <McqResultView result={mcqResult("D")} question={mcqQuestion("two_column_table")} />,
    );
    const rows = Array.from(container.querySelectorAll("tr")).slice(1);
    expect(rows).toHaveLength(4);
    rows.forEach((tr, i) => expect(/correct/i.test(tr.textContent!)).toBe(i === 3));
  });

  it("still shows all option content", () => {
    const { container } = render(<McqResultView result={mcqResult("A")} question={mcqQuestion("single_value")} />);
    for (const k of KEYS) expect(container.textContent).toContain(`cell-${k}`);
  });
});

// A staff document with distinctive strings for everything that must be hidden without answers.
const staffStructured = (): QuestionDocument => ({
  schema_version: "1.0",
  question_class: "short_structured",
  exam_section: "paper_2",
  levels: ["sl"],
  language: "en",
  calculator: true,
  primary_syllabus_node: "node-x",
  secondary_syllabus_nodes: [],
  total_marks: 2,
  stem: doc(para(text("STEM-TEXT")), figure("st1")),
  stimuli: [{ id: "st1", kind: "graph", use: "read_values", description: "STIMULUS-DESCRIPTION-XYZ" }],
  parts: [
    {
      id: "p1",
      label: "a",
      marks: 2,
      marks_capped: false,
      answer_type: "short_text" as never,
      level_content: "sl_core",
      depends_on: [],
      ecf_from: [],
      stimulus_refs: [],
      body: d("PART-BODY"),
      mark_points: [
        { id: "mp1", content: d("MARKPOINT-ONE"), kind: "method" },
        { id: "mp2", content: d("MARKPOINT-TWO"), kind: "answer" },
      ],
      notes: [{ kind: "owtte", content: d("NOTE-TEXT"), mark_point_id: null }],
    },
  ] as unknown as QuestionDocument["parts"],
});

const staffMcq = (): QuestionDocument => ({
  schema_version: "1.0",
  question_class: "mcq",
  exam_section: "paper_1a",
  levels: ["sl"],
  language: "en",
  calculator: false,
  primary_syllabus_node: "node-x",
  secondary_syllabus_nodes: [],
  total_marks: 1,
  stem: d("MCQ-STEM"),
  stimuli: [],
  parts: [],
  mcq: {
    option_kind: "word_phrase",
    option_layout: "single_value",
    column_headers: [],
    statements: [],
    correct_key: "C",
    level_content: "sl_core",
    explanation: d("EXPLANATION-TEXT"),
    options: [
      { key: "A", cells: [d("opt-A")], rationale: d("RATIONALE-A") },
      { key: "B", cells: [d("opt-B")], rationale: d("RATIONALE-B") },
      { key: "C", cells: [d("opt-C")], rationale: null },
      { key: "D", cells: [d("opt-D")], rationale: d("RATIONALE-D") },
    ],
  },
});

describe("QuestionDocumentView, structured (3.1, staff view)", () => {
  it("showAnswers=false: question content visible, no mark point or note", () => {
    const { container } = render(<QuestionDocumentView document={staffStructured()} showAnswers={false} />);
    const t = container.textContent!;
    expect(t).toContain("STEM-TEXT");
    expect(t).toContain("PART-BODY");
    expect(t).not.toContain("MARKPOINT-ONE");
    expect(t).not.toContain("MARKPOINT-TWO");
    expect(t).not.toContain("NOTE-TEXT");
    expect(t).not.toContain("OWTTE");
    expect(t).not.toContain("✓");
  });

  it("showAnswers=true: mark points and notes are shown", () => {
    const { container } = render(<QuestionDocumentView document={staffStructured()} showAnswers />);
    const t = container.textContent!;
    expect(t).toContain("MARKPOINT-ONE");
    expect(t).toContain("MARKPOINT-TWO");
    expect(t).toContain("NOTE-TEXT");
    expect(t).toContain("OWTTE");
    expect(t).toContain("[2]");
  });

  it.each([true, false])("showAnswers=%s: the stimulus description is inside the placeholder under 'Description (staff only)'", (showAnswers) => {
    render(<QuestionDocumentView document={staffStructured()} showAnswers={showAnswers} />);
    const img = screen.getByRole("img");
    expect(img.textContent).toContain("Description (staff only)");
    expect(img.textContent).toContain("STIMULUS-DESCRIPTION-XYZ");
    expect(img.textContent!.indexOf("Description (staff only)")).toBeLessThan(
      img.textContent!.indexOf("STIMULUS-DESCRIPTION-XYZ"),
    );
    expect(img.getAttribute("aria-label")).toBeTruthy();
  });

  it("showAnswers=false never shows the correct-answer marker for a structured question", () => {
    const { container } = render(<QuestionDocumentView document={staffStructured()} showAnswers={false} />);
    expect(container.textContent).not.toMatch(/correct answer/i);
  });
});

describe("QuestionDocumentView, MCQ (3.1, staff view)", () => {
  it("showAnswers=false: options visible; no correct key, explanation or rationale", () => {
    const { container } = render(<QuestionDocumentView document={staffMcq()} showAnswers={false} />);
    const t = container.textContent!;
    for (const k of KEYS) expect(t).toContain(`opt-${k}`);
    expect(t).not.toContain("EXPLANATION-TEXT");
    expect(t).not.toContain("RATIONALE");
    expect(t).not.toMatch(/correct/i);
  });

  it("showAnswers=true: the correct option is marked by text; explanation and rationales appear", () => {
    const { container } = render(<QuestionDocumentView document={staffMcq()} showAnswers />);
    const t = container.textContent!;
    expect(t).toContain("EXPLANATION-TEXT");
    for (const k of ["A", "B", "D"]) expect(t).toContain(`RATIONALE-${k}`);
    const items = within(container.querySelector("ol") as HTMLElement).getAllByRole("listitem");
    expect(items).toHaveLength(4);
    expect(items[2]!.textContent).toMatch(/correct/i);
    expect(items[0]!.textContent).not.toMatch(/(?<!in)correct/i);
  });

  it("showAnswers=true: rationales appear in option order (A, B, D)", () => {
    const { container } = render(<QuestionDocumentView document={staffMcq()} showAnswers />);
    const t = container.textContent!;
    const pos = ["RATIONALE-A", "RATIONALE-B", "RATIONALE-D"].map((n) => t.indexOf(n));
    expect(pos.every((p, i) => p >= 0 && (i === 0 || p > pos[i - 1]!))).toBe(true);
  });
});

describe("learner answer presentation (slice 8)", () => {
  const rationales = [
    { key: "A" as const, content: d("WHY-A") },
    { key: "B" as const, content: d("WHY-B") },
    { key: "D" as const, content: d("WHY-D") },
  ];

  it.each(["single_value", "two_column_table"] as const)("McqResultView shows explanation and per-option rationales (%s)", (layout) => {
    const result = { ...mcqResult("C", false), explanation: d("EXPLAIN"), rationales };
    render(<McqResultView result={result} question={mcqQuestion(layout)} />);
    expect(screen.getByRole("region", { name: "Explanation" }).textContent).toContain("EXPLAIN");
    for (const k of ["A", "B", "D"]) {
      expect(screen.getByRole("group", { name: `Why option ${k} is wrong` }).textContent).toContain(`WHY-${k}`);
    }
    expect(screen.queryByRole("group", { name: "Why option C is wrong" })).toBeNull();
  });

  it("renders no explanation block when there is none", () => {
    render(<McqResultView result={mcqResult("A")} question={mcqQuestion("single_value")} />);
    expect(screen.queryByRole("region", { name: "Explanation" })).toBeNull();
  });
});
