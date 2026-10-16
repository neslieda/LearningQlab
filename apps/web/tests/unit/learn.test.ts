import { describe, expect, it } from "vitest";
import type { ResponseOut } from "@qlab/api-client";
import {
  answerProblemMessage,
  answeredIds,
  countLabel,
  excerpt,
  filtersFromParams,
  filtersToSearch,
  partLabeller,
  toAnswerRows,
} from "../../src/lib/learn";

const mcq = (over: Partial<ResponseOut> = {}): ResponseOut => ({
  id: "r1", question_id: "q1", version_id: "v1", kind: "mcq", part_id: null, selected_key: "B", text: null,
  correct: false, created_at: "2026-10-01T09:00:00Z", ...over,
});
const written = (over: Partial<ResponseOut> = {}): ResponseOut => ({
  ...mcq(), id: "r2", kind: "written", part_id: "p1", selected_key: null, text: "my text", correct: null, ...over,
});

describe("answerProblemMessage", () => {
  it("maps the slice 8 codes", () => {
    expect(answerProblemMessage({ status: 422, code: "answer_does_not_fit" }).message).toBe("This answer does not fit the question");
    expect(answerProblemMessage({ status: 429, code: "too_many_answers" }).message).toBe(
      "You have reached the limit of 200 answers for this question",
    );
  });
  it("sends a 401 to sign-in", () => {
    expect(answerProblemMessage({ status: 401 }).followUp).toBe("sign-in");
  });
  it("falls back to the shared mapping", () => {
    expect(answerProblemMessage({ status: 404, code: "not_found" }).message).toBe("Not found or not visible to you");
    expect(answerProblemMessage({ status: 500, code: "x" }).message).toBe("Something went wrong (x)");
  });
});

describe("filters", () => {
  it("round-trips valid filters", () => {
    const f = filtersFromParams(new URLSearchParams("exam_section=paper_1a&question_class=mcq&level=hl"));
    expect(f).toEqual({ examSection: "paper_1a", questionClass: "mcq", level: "hl" });
    expect(filtersToSearch(f)).toBe("exam_section=paper_1a&question_class=mcq&level=hl");
  });
  it("drops unknown values", () => {
    const f = filtersFromParams(new URLSearchParams("exam_section=%3Cb%3E&question_class=x&level=zz"));
    expect(f).toEqual({ examSection: "", questionClass: undefined, level: undefined });
    expect(filtersToSearch(f)).toBe("");
  });
});

describe("answer view model", () => {
  it("describes mcq and written answers", () => {
    const rows = toAnswerRows([mcq(), mcq({ id: "r3", correct: true }), written()], () => "a");
    expect(rows.map((r) => [r.what, r.outcome])).toEqual([
      ["Option B", "Incorrect"],
      ["Option B", "Correct"],
      ["Part (a)", null],
    ]);
  });
  it("labels parts from the question", () => {
    const label = partLabeller({ parts: [{ id: "p1", label: "b.i" }] as never });
    expect(label(written())).toBe("b.i");
    expect(label(mcq())).toBeUndefined();
  });
  it("collects answered question ids", () => {
    expect([...answeredIds([mcq(), written({ question_id: "q2" })])].sort()).toEqual(["q1", "q2"]);
  });
  it("labels counts", () => {
    expect(countLabel(3, false)).toBe("3");
    expect(countLabel(20, true)).toBe("20+");
    expect(excerpt("a  b\n c", 100)).toBe("a b c");
    expect(excerpt("x".repeat(300), 10)).toHaveLength(10);
  });
});
