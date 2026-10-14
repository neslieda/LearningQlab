// Synthetic builders for the renderer tests. All physics here is invented.
import type { Doc } from "@qlab/api-client";

export type Mark = "bold" | "italic" | "sub" | "sup" | "optional" | "essential";

export const text = (t: string, marks: Mark[] = []) => ({
  type: "text" as const,
  text: t,
  marks: marks.map((type) => ({ type })),
});
export const mathInline = (latex: string, marks: Mark[] = []) => ({
  type: "math_inline" as const,
  attrs: { latex },
  marks: marks.map((type) => ({ type })),
});
export const quantity = (
  value: string,
  unit: string,
  uncertainty?: string | null,
  marks: Mark[] = [],
) => ({
  type: "quantity" as const,
  attrs: { value, unit, uncertainty: uncertainty ?? null },
  marks: marks.map((type) => ({ type })),
});
export const hardBreak = () => ({ type: "hard_break" as const });

type Inline =
  | ReturnType<typeof text>
  | ReturnType<typeof mathInline>
  | ReturnType<typeof quantity>
  | ReturnType<typeof hardBreak>;

export const para = (...content: Inline[]) => ({ type: "paragraph" as const, content });
export const mathBlock = (latex: string) => ({ type: "math_block" as const, attrs: { latex } });
export const figure = (stimulus_id: string) => ({ type: "figure" as const, attrs: { stimulus_id } });
export const bulletList = (...items: ReturnType<typeof para>[]) => ({
  type: "bullet_list" as const,
  content: items.map((p) => ({ type: "list_item" as const, content: [p] })),
});
export const orderedList = (...items: ReturnType<typeof para>[]) => ({
  type: "ordered_list" as const,
  content: items.map((p) => ({ type: "list_item" as const, content: [p] })),
});
export const cell = (p: ReturnType<typeof para>, colspan = 1, rowspan = 1) => ({
  type: "table_cell" as const,
  attrs: { colspan, rowspan },
  content: [p],
});
export const header = (p: ReturnType<typeof para>, colspan = 1, rowspan = 1) => ({
  type: "table_header" as const,
  attrs: { colspan, rowspan },
  content: [p],
});
export const row = (...content: (ReturnType<typeof cell> | ReturnType<typeof header>)[]) => ({
  type: "table_row" as const,
  content,
});
export const table = (...content: ReturnType<typeof row>[]) => ({ type: "table" as const, content });

export const doc = (...content: Doc["content"]): Doc => ({ type: "doc", content });
/** A document holding one paragraph of plain text. */
export const d = (s: string): Doc => doc(para(text(s)));

import type { LearnerQuestion, McqCheckResult, QuestionDocument } from "@qlab/api-client";
import type { LearnerPart } from "../src";

export const learnerPart = (
  label: string,
  body: string | Doc,
  marks: number,
  extra: Partial<LearnerPart> = {},
): LearnerPart => ({
  id: `p-${label}`,
  label,
  marks,
  body: typeof body === "string" ? d(body) : body,
  lead_in: null,
  command_term: null,
  stimulus_refs: [],
  ...extra,
});

export const learnerQuestion = (extra: Partial<LearnerQuestion> = {}): LearnerQuestion => ({
  id: "q1",
  version_id: "v1",
  exam_section: "paper_2",
  levels: ["sl", "hl"],
  question_class: "short_structured",
  total_marks: 5,
  stem: d("A trolley of invented mass rolls down a ramp."),
  stimuli: [],
  mcq: null,
  parts: [],
  ...extra,
});

export const KEYS = ["A", "B", "C", "D"] as const;

export const mcqQuestion = (
  layout: "single_value" | "two_column_table" | "roman_statements" | "figure_options",
  extra: Partial<LearnerQuestion> = {},
): LearnerQuestion => {
  const options = KEYS.map((key) => ({
    key,
    cells:
      layout === "two_column_table"
        ? [d(`left-${key}`), d(`right-${key}`)]
        : layout === "figure_options"
          ? [doc(figure(`fig-${key}`))]
          : [d(`cell-${key}`)],
  }));
  return learnerQuestion({
    question_class: "mcq",
    total_marks: 1,
    parts: [],
    stimuli:
      layout === "figure_options"
        ? KEYS.map((k) => ({ id: `fig-${k}`, kind: "circuit_diagram" as const }))
        : [],
    mcq: {
      option_layout: layout,
      column_headers: layout === "two_column_table" ? [d("Speed"), d("Direction")] : [],
      statements: layout === "roman_statements" ? [d("stmt-one"), d("stmt-two"), d("stmt-three")] : [],
      options,
    },
    ...extra,
  });
};

export const mcqResult = (correct_key: "A" | "B" | "C" | "D", correct = true): McqCheckResult => ({
  kind: "mcq",
  correct,
  correct_key,
  version_id: "v1",
});

export type { Doc, LearnerQuestion, McqCheckResult, QuestionDocument };
