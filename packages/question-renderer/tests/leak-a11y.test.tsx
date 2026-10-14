import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { LearnerQuestion } from "@qlab/api-client";
import { LearnerQuestionView, fixtures } from "../src";

const learnerFixtures = fixtures.filter((f) => f.kind === "learner_question");

const FORBIDDEN = [
  /Description \(staff only\)/i,
  /staff only/i,
  /Correct answer/i,
  /correct key/i,
  /rationale/i,
  /explanation/i,
  /mark point/i,
  /✓/,
  /OWTTE/,
  /\bECF\b/,
];

describe("learner view never leaks staff content (rules 13, 14)", () => {
  it("the exported fixtures contain learner questions", () => {
    expect(learnerFixtures.length).toBeGreaterThanOrEqual(6);
  });

  it.each(learnerFixtures.map((f) => [f.id, f]))("%s", (_id, f) => {
    const question = (f as unknown as { data: LearnerQuestion }).data;
    const { container } = render(<LearnerQuestionView question={question} />);
    const t = container.textContent ?? "";
    for (const re of FORBIDDEN) expect(t).not.toMatch(re);
    expect(container.querySelector("script, img, iframe, a")).toBeNull();
    expect(container.querySelectorAll("article")).toHaveLength(1);
  });

  it("the learner payload has no field a staff-only string could come from (type-level guard)", () => {
    for (const f of learnerFixtures) {
      const q = (f as unknown as { data: Record<string, unknown> }).data;
      expect(q).not.toHaveProperty("solution_model");
      expect(JSON.stringify(q)).not.toMatch(/correct_key|rationale|description/);
    }
  });
});

describe("accessibility smoke check (3.1, 6)", () => {
  const named = (el: Element) => {
    if (el.getAttribute("aria-label")?.trim()) return true;
    const by = el.getAttribute("aria-labelledby");
    if (by) {
      return by.split(/\s+/).some((id) => (document.getElementById(id)?.textContent ?? "").trim().length > 0);
    }
    return false;
  };

  it.each(learnerFixtures.map((f) => [f.id, f]))("%s: scroll containers and images are named", (_id, f) => {
    const question = (f as unknown as { data: LearnerQuestion }).data;
    const { container } = render(<LearnerQuestionView question={question} />);
    for (const el of container.querySelectorAll('[tabindex="0"]')) {
      expect(named(el)).toBe(true);
    }
    for (const el of container.querySelectorAll('[role="img"]')) {
      expect(named(el)).toBe(true);
    }
    // No positive tabindex anywhere.
    for (const el of container.querySelectorAll("[tabindex]")) {
      expect(Number(el.getAttribute("tabindex"))).toBeLessThanOrEqual(0);
    }
  });

  it("every role=img found by Testing Library has an accessible name", () => {
    const q = learnerFixtures.map((f) => (f as unknown as { data: LearnerQuestion }).data).find((x) => x.stimuli.length > 0);
    expect(q).toBeDefined();
    render(<LearnerQuestionView question={q!} />);
    for (const img of screen.getAllByRole("img")) {
      expect(img).toHaveAccessibleName();
    }
  });

  it("the fixtures with wide tables or long math have at least one focusable scroll container", () => {
    const hit = learnerFixtures.filter((f) => {
      const q = (f as unknown as { data: LearnerQuestion }).data;
      return /"type":"table"|"type":"math_block"/.test(JSON.stringify(q));
    });
    expect(hit.length).toBeGreaterThanOrEqual(1);
    for (const f of hit) {
      const { container, unmount } = render(
        <LearnerQuestionView question={(f as unknown as { data: LearnerQuestion }).data} />,
      );
      expect(container.querySelectorAll('[tabindex="0"]').length).toBeGreaterThanOrEqual(1);
      unmount();
    }
  });
});
