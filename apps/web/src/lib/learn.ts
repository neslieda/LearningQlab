import type { LearnerQuestion, ResponseOut } from "@qlab/api-client";
import { problemMessage, type ProblemLike, type ProblemMessage } from "./decisions";

export const ANSWER_LIMIT = 200;
export const DELETE_WARNING = "This deletes every answer you have saved. It cannot be undone.";

export const PRIVACY_NOTICE = {
  stored: "We store your account ID, the question, your answer and the time you sent it.",
  notStored: "We do not store your name, e-mail address or device data with your answers.",
  visibility: "Only you can see your answers for now.",
  deletion: "You can delete all of them at any time from your account page.",
} as const;

/** The text for a failed answer request (docs/slices/M1G-8-OGRENCI.md section 4); other codes follow slice 7a. */
export function answerProblemMessage(problem: ProblemLike): ProblemMessage {
  switch (problem.status === 401 ? "unauthenticated" : (problem.code ?? "")) {
    case "answer_does_not_fit":
      return { message: "This answer does not fit the question", reasons: [], followUp: null };
    case "too_many_answers":
      return { message: `You have reached the limit of ${ANSWER_LIMIT} answers for this question`, reasons: [], followUp: null };
    default:
      return problemMessage(problem);
  }
}

// --- list filters in the URL ---

export const CLASSES = ["mcq", "data_based", "short_structured", "long_structured"] as const;
export const LEVELS = ["sl", "hl"] as const;
export type LearnClass = (typeof CLASSES)[number];
export type LearnLevel = (typeof LEVELS)[number];

export interface LearnFilters {
  examSection: string;
  questionClass: LearnClass | undefined;
  level: LearnLevel | undefined;
}

const SECTION_RE = /^[A-Za-z0-9][A-Za-z0-9_.]*$/;

export function isValidSection(value: string): boolean {
  return value.length <= 120 && SECTION_RE.test(value);
}

function pick<T extends string>(value: string | null, allowed: readonly T[]): T | undefined {
  return allowed.find((a) => a === value);
}

/** Reads the filters from the URL; anything unknown or malformed is ignored (never sent to the API). */
export function filtersFromParams(params: { get(name: string): string | null }): LearnFilters {
  const raw = (params.get("exam_section") ?? "").trim();
  return {
    examSection: isValidSection(raw) ? raw : "",
    questionClass: pick(params.get("question_class"), CLASSES),
    level: pick(params.get("level"), LEVELS),
  };
}

/** The query string for the filters (empty when none are set). */
export function filtersToSearch(filters: LearnFilters): string {
  const p = new URLSearchParams();
  if (filters.examSection) p.set("exam_section", filters.examSection);
  if (filters.questionClass) p.set("question_class", filters.questionClass);
  if (filters.level) p.set("level", filters.level);
  return p.toString();
}

// --- answers ---

/** "3" or "20+" when more pages exist. */
export function countLabel(count: number, hasMore: boolean): string {
  return hasMore ? `${count}+` : String(count);
}

export function partLabel(label: string): string {
  return `(${label})`;
}

export interface AnswerRow {
  id: string;
  questionId: string;
  createdAt: string;
  kind: "mcq" | "written";
  /** "Option B" or "Part (a)". */
  what: string;
  /** The answer as text. */
  answer: string;
  /** Only for multiple choice. */
  outcome: "Correct" | "Incorrect" | null;
}

/** One row per stored answer. `labelOf` turns a part id into its label when the question is known. */
export function toAnswerRows(items: readonly ResponseOut[], labelOf?: (response: ResponseOut) => string | undefined): AnswerRow[] {
  return items.map((r) => {
    if (r.kind === "mcq") {
      return {
        id: r.id,
        questionId: r.question_id,
        createdAt: r.created_at,
        kind: "mcq",
        what: `Option ${r.selected_key ?? "?"}`,
        answer: r.selected_key ?? "",
        outcome: r.correct === null ? null : r.correct ? "Correct" : "Incorrect",
      };
    }
    const label = labelOf?.(r);
    return {
      id: r.id,
      questionId: r.question_id,
      createdAt: r.created_at,
      kind: "written",
      what: label ? `Part ${partLabel(label)}` : "Written answer",
      answer: r.text ?? "",
      outcome: null,
    };
  });
}

/** Label lookup for the previous answers of one question. */
export function partLabeller(question: Pick<LearnerQuestion, "parts">): (r: ResponseOut) => string | undefined {
  const byId = new Map(question.parts.map((p) => [p.id, p.label]));
  return (r) => (r.part_id ? byId.get(r.part_id) : undefined);
}

/** Question ids that have at least one answer. */
export function answeredIds(items: readonly ResponseOut[]): Set<string> {
  return new Set(items.map((r) => r.question_id));
}

export function excerpt(text: string, max = 160): string {
  const flat = text.replace(/\s+/g, " ").trim();
  return flat.length > max ? `${flat.slice(0, max - 1)}…` : flat;
}

export function classLabel(c: string): string {
  return c.replace(/_/g, " ");
}
