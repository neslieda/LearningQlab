import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LearnerQuestionView } from "../src";
import {
  KEYS, d, doc, figure, learnerPart, learnerQuestion, mathInline, mcqQuestion, para, quantity, text,
} from "./helpers";

const orderOf = (container: HTMLElement, ...needles: string[]) => {
  const t = container.textContent ?? "";
  return needles.map((n) => t.indexOf(n));
};
const ascending = (xs: number[]) => xs.every((x, i) => x >= 0 && (i === 0 || x > xs[i - 1]!));

describe("header line (3.2)", () => {
  it("shows exam section, levels and total marks", () => {
    const { container } = render(<LearnerQuestionView question={learnerQuestion({ total_marks: 7 })} />);
    const t = container.textContent!;
    expect(t).toMatch(/paper_2|paper 2/i);
    expect(t).toContain("SL");
    expect(t).toContain("HL");
    expect(t).toContain("[7 marks]");
  });

  it("uses the singular for 1 mark", () => {
    const { container } = render(<LearnerQuestionView question={mcqQuestion("single_value")} />);
    expect(container.textContent).toContain("[1 mark]");
    expect(container.textContent).not.toContain("[1 marks]");
  });

  it("shows only the levels the question has", () => {
    const { container } = render(<LearnerQuestionView question={learnerQuestion({ levels: ["hl"] })} />);
    expect(container.textContent).toContain("HL");
    expect(container.textContent).not.toMatch(/\bSL\b/);
  });

  it("stem comes after the header and before the parts", () => {
    const q = learnerQuestion({ parts: [learnerPart("a", "PARTBODY", 2)], total_marks: 2 });
    const { container } = render(<LearnerQuestionView question={q} />);
    expect(ascending(orderOf(container, "[2 marks]", "invented mass", "PARTBODY"))).toBe(true);
  });
});

describe("article accessible name (3.2)", () => {
  it("contains exam section, levels and marks separated by whitespace", () => {
    render(<LearnerQuestionView question={learnerQuestion({ total_marks: 9 })} />);
    expect(screen.getByRole("article")).toHaveAccessibleName(/paper_2\s+SL\s+HL\s+9 marks/);
  });

  it("reads '1 mark' for a one-mark question and a single level separately", () => {
    render(
      <LearnerQuestionView question={mcqQuestion("single_value", { levels: ["hl"], exam_section: "paper_1a" })} />,
    );
    expect(screen.getByRole("article")).toHaveAccessibleName(/paper_1a\s+HL\s+1 mark/);
  });
});

describe("semantic structure (3.2)", () => {
  it("the question is an article", () => {
    render(<LearnerQuestionView question={learnerQuestion({ parts: [learnerPart("a", "x", 1)] })} />);
    expect(screen.getAllByRole("article")).toHaveLength(1);
  });

  it("each labelled part is a section inside the article, with a heading", () => {
    const q = learnerQuestion({
      parts: [learnerPart("a", "first", 1), learnerPart("b", "second", 2), learnerPart("c", "third", 2)],
    });
    const { container } = render(<LearnerQuestionView question={q} />);
    const article = container.querySelector("article")!;
    const sections = article.querySelectorAll("section");
    expect(sections.length).toBeGreaterThanOrEqual(3);
    expect(screen.getAllByRole("heading").length).toBeGreaterThanOrEqual(1);
  });

  it("heading levels never skip a level in document order", () => {
    const q = learnerQuestion({
      parts: [
        learnerPart("a", "x", 1),
        learnerPart("b.i", "y", 1),
        learnerPart("b.ii", "z", 1),
        learnerPart("c", "w", 2),
      ],
    });
    render(<LearnerQuestionView question={q} />);
    const levels = screen.getAllByRole("heading").map((h) => Number(h.tagName.slice(1)));
    for (let i = 1; i < levels.length; i++) {
      expect(levels[i]! - levels[i - 1]!).toBeLessThanOrEqual(1);
    }
  });
});

describe("MCQ layouts (3.2)", () => {
  it("single_value: options A-D in order, as a list, with the key as label", () => {
    const { container } = render(<LearnerQuestionView question={mcqQuestion("single_value")} />);
    const list = container.querySelector("ol");
    expect(list).not.toBeNull();
    const items = within(list as HTMLElement).getAllByRole("listitem");
    expect(items).toHaveLength(4);
    items.forEach((li, i) => {
      expect(li.textContent).toContain(KEYS[i]);
      expect(li.textContent).toContain(`cell-${KEYS[i]}`);
    });
    expect(ascending(orderOf(container, "cell-A", "cell-B", "cell-C", "cell-D"))).toBe(true);
  });

  it("single_value renders math and quantity inside options", () => {
    const q = mcqQuestion("single_value");
    q.mcq!.options[0]!.cells = [doc(para(mathInline("v^2"), text(" = "), quantity("9.0", "m/s")))];
    const { container } = render(<LearnerQuestionView question={q} />);
    expect(container.querySelector(".katex")).not.toBeNull();
    expect(container.textContent).toContain("9.0 m/s");
  });

  it("two_column_table: a table with the column headers and four A-D rows", () => {
    const { container } = render(<LearnerQuestionView question={mcqQuestion("two_column_table")} />);
    const table = container.querySelector("table")!;
    expect(table).not.toBeNull();
    const headers = Array.from(table.querySelectorAll("th")).map((th) => th.textContent);
    expect(headers).toEqual(expect.arrayContaining(["Speed", "Direction"]));
    const t = table.textContent!;
    expect(ascending(["A", "B", "C", "D"].map((k) => t.indexOf(`left-${k}`)))).toBe(true);
    for (const k of KEYS) {
      expect(t).toContain(`left-${k}`);
      expect(t).toContain(`right-${k}`);
    }
    // Four option rows plus one header row.
    expect(table.querySelectorAll("tr").length).toBe(5);
    // Each option row shows its key.
    const rows = Array.from(table.querySelectorAll("tr")).slice(1);
    rows.forEach((tr, i) => expect(tr.textContent).toContain(KEYS[i]));
  });

  it("two_column_table: the table sits in a focusable, named scroll container", () => {
    const { container } = render(<LearnerQuestionView question={mcqQuestion("two_column_table")} />);
    const holder = Array.from(container.querySelectorAll('[tabindex="0"]')).find((e) => e.querySelector("table"));
    expect(holder).toBeDefined();
    expect(holder!.getAttribute("aria-label") ?? holder!.getAttribute("aria-labelledby")).toBeTruthy();
  });

  it("roman_statements: I., II., III. come before the options", () => {
    const { container } = render(<LearnerQuestionView question={mcqQuestion("roman_statements")} />);
    const t = container.textContent!;
    expect(t).toContain("I.");
    expect(t).toContain("II.");
    expect(t).toContain("III.");
    expect(ascending([t.indexOf("I."), t.indexOf("II."), t.indexOf("III.")])).toBe(true);
    expect(ascending(["stmt-one", "stmt-two", "stmt-three", "cell-A", "cell-B", "cell-C", "cell-D"].map((n) => t.indexOf(n)))).toBe(true);
    expect(t.indexOf("III.")).toBeLessThan(t.indexOf("cell-A"));
  });

  it("figure_options: every option is a figure placeholder with role=img, name and kind", () => {
    render(<LearnerQuestionView question={mcqQuestion("figure_options")} />);
    const imgs = screen.getAllByRole("img");
    expect(imgs).toHaveLength(4);
    for (const img of imgs) {
      expect((img.getAttribute("aria-label") ?? "").length).toBeGreaterThan(0);
      expect(`${img.getAttribute("aria-label")} ${img.textContent}`).toMatch(/Circuit diagram/i);
    }
    expect(within(screen.getAllByRole("listitem")[0]!).getByRole("img")).toBeInTheDocument();
  });

  it("an MCQ has no part sections and no command term text", () => {
    const { container } = render(<LearnerQuestionView question={mcqQuestion("single_value")} />);
    expect(container.textContent).not.toContain("(a)");
  });

  it("renderMcqFooter is called and its output rendered after the options", () => {
    const footer = vi.fn(() => <div data-testid="mcq-footer">answer here</div>);
    const { container } = render(
      <LearnerQuestionView question={mcqQuestion("single_value")} renderMcqFooter={footer} />,
    );
    expect(footer).toHaveBeenCalled();
    expect(screen.getByTestId("mcq-footer")).toBeInTheDocument();
    expect(ascending(orderOf(container, "cell-D", "answer here"))).toBe(true);
  });

  it("without footers nothing extra is rendered", () => {
    const { container } = render(<LearnerQuestionView question={mcqQuestion("single_value")} />);
    expect(container.querySelector('[data-testid="mcq-footer"]')).toBeNull();
  });
});

describe("structured parts (3.2)", () => {
  const q = () =>
    learnerQuestion({
      total_marks: 7,
      parts: [
        learnerPart("a", "BODY-A", 1),
        learnerPart("b.i", "BODY-BI", 2, { lead_in: d("LEAD-B") }),
        learnerPart("b.ii", "BODY-BII", 3, { command_term: "Calculate" }),
        learnerPart("c", "BODY-C", 1),
      ],
    });

  it("writes (a), (b), (c) and (i), (ii); (b) only once, before (i)", () => {
    const { container } = render(<LearnerQuestionView question={q()} />);
    const t = container.textContent!;
    expect(t.match(/\(b\)/g)).toHaveLength(1);
    expect(t.match(/\(a\)/g)).toHaveLength(1);
    expect(t.match(/\(c\)/g)).toHaveLength(1);
    expect(t.match(/\(i\)/g)).toHaveLength(1);
    expect(t.match(/\(ii\)/g)).toHaveLength(1);
    expect(ascending(["(a)", "BODY-A", "(b)", "(i)", "BODY-BI", "(ii)", "BODY-BII", "(c)", "BODY-C"].map((n) => t.indexOf(n)))).toBe(true);
  });

  it("does not print raw labels such as b.i", () => {
    const { container } = render(<LearnerQuestionView question={q()} />);
    expect(container.textContent).not.toMatch(/\bb\.ii?\b/);
  });

  it("lead_in is shown before the body", () => {
    const { container } = render(<LearnerQuestionView question={q()} />);
    expect(ascending(orderOf(container, "LEAD-B", "BODY-BI"))).toBe(true);
  });

  it("sub-parts sit inside the (b) group: (i) and (ii) share an ancestor not shared with (c)", () => {
    const { container } = render(<LearnerQuestionView question={q()} />);
    const find = (s: string) => screen.getByText(s);
    const bi = find("BODY-BI");
    const bii = find("BODY-BII");
    const c = find("BODY-C");
    const common = (a: Element, b: Element) => {
      let n: Element | null = a;
      while (n && !n.contains(b)) n = n.parentElement;
      return n;
    };
    const biBii = common(bi, bii)!;
    expect(biBii).not.toBe(container);
    expect(biBii.contains(c)).toBe(false);
  });

  it("marks show as [n] with an accessible 'n marks' reading", () => {
    const { container } = render(<LearnerQuestionView question={q()} />);
    const t = container.textContent!;
    expect(t).toContain("[2]");
    expect(t).toContain("[3]");
    const hasName = (name: string) =>
      Array.from(container.querySelectorAll("[aria-label]")).some((e) => e.getAttribute("aria-label") === name) ||
      Array.from(container.querySelectorAll("*")).some((e) => e.children.length === 0 && e.textContent === name);
    expect(hasName("2 marks")).toBe(true);
    expect(hasName("3 marks")).toBe(true);
    expect(hasName("1 mark")).toBe(true);
  });

  it("does not show the command term separately", () => {
    const { container } = render(<LearnerQuestionView question={q()} />);
    expect(container.textContent).not.toContain("Calculate");
  });

  it("a part with a letter-only label and no sub-parts has no roman label", () => {
    const { container } = render(
      <LearnerQuestionView question={learnerQuestion({ parts: [learnerPart("a", "only", 2)] })} />,
    );
    expect(container.textContent).not.toMatch(/\(i\)/);
  });

  it("renderPartFooter is called once per part with that part, rendered inside it after its body", () => {
    const footer = vi.fn((part: { id: string }) => <div data-testid={`foot-${part.id}`}>FOOT-{part.id}</div>);
    const question = q();
    const { container } = render(<LearnerQuestionView question={question} renderPartFooter={footer} />);
    expect(footer).toHaveBeenCalledTimes(4);
    const ids = footer.mock.calls.map((c) => c[0].id).sort();
    expect(ids).toEqual(["p-a", "p-b.i", "p-b.ii", "p-c"]);
    const passed = footer.mock.calls.find((c) => c[0].id === "p-b.i")![0] as unknown as { label: string; marks: number };
    expect(passed.label).toBe("b.i");
    expect(passed.marks).toBe(2);
    for (const [id, body] of [["p-a", "BODY-A"], ["p-b.i", "BODY-BI"], ["p-b.ii", "BODY-BII"], ["p-c", "BODY-C"]]) {
      const f = screen.getByTestId(`foot-${id}`);
      const b = screen.getByText(body!);
      expect(b.compareDocumentPosition(f) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    }
    // The footer of (a) comes before the body of (b.i).
    expect(ascending(orderOf(container, "BODY-A", "FOOT-p-a", "BODY-BI"))).toBe(true);
    expect(ascending(orderOf(container, "BODY-BII", "FOOT-p-b.ii", "BODY-C"))).toBe(true);
  });

  it("renderMcqFooter output is not rendered for a structured question, nor renderPartFooter output for an MCQ", () => {
    // Spec 3.2 does not say whether the callback is invoked; what matters is that nothing is rendered.
    const a = render(
      <LearnerQuestionView question={q()} renderMcqFooter={() => <span data-testid="mcq-f">MCQFOOT</span>} />,
    );
    expect(a.container.textContent).not.toContain("MCQFOOT");
    a.unmount();
    const b = render(
      <LearnerQuestionView
        question={mcqQuestion("single_value")}
        renderPartFooter={() => <span data-testid="part-f">PARTFOOT</span>}
      />,
    );
    expect(b.container.textContent).not.toContain("PARTFOOT");
  });
});

describe("stimuli in the learner view (3.1, 3.2)", () => {
  const withFigure = () =>
    learnerQuestion({
      stem: doc(para(text("See the plot.")), figure("s1")),
      stimuli: [{ id: "s1", kind: "graph" }],
      parts: [learnerPart("a", "Read a value.", 1)],
      total_marks: 1,
    });

  it("a figure is a role=img placeholder with an accessible label and the readable kind", () => {
    render(<LearnerQuestionView question={withFigure()} />);
    const img = screen.getByRole("img");
    const label = img.getAttribute("aria-label") ?? "";
    expect(label.length).toBeGreaterThan(0);
    expect(`${label} ${img.textContent}`).toMatch(/Figure/);
    expect(`${label} ${img.textContent}`).toMatch(/Graph/);
    expect(`${label} ${img.textContent}`).not.toMatch(/\bgraph\b(?!\s)/);
  });

  it("the readable kind is humanised: snake_case never appears", () => {
    const q = learnerQuestion({
      stem: doc(figure("s1")),
      stimuli: [{ id: "s1", kind: "ray_wavefront_diagram" }],
      parts: [learnerPart("a", "x", 1)],
      total_marks: 1,
    });
    const { container } = render(<LearnerQuestionView question={q} />);
    expect(container.textContent).not.toContain("ray_wavefront_diagram");
    expect(`${screen.getByRole("img").getAttribute("aria-label")} ${container.textContent}`).toMatch(/Ray wavefront diagram/i);
  });

  it("the learner view has no description and no staff heading", () => {
    const { container } = render(<LearnerQuestionView question={withFigure()} />);
    expect(container.textContent).not.toMatch(/Description/i);
    expect(container.textContent).not.toMatch(/staff only/i);
  });

  it("a stimulus carrying an extra runtime description property still does not show it", () => {
    const question = withFigure();
    question.stimuli = [
      { id: "s1", kind: "graph", description: "LEAKED-DESCRIPTION-QQ" } as unknown as (typeof question.stimuli)[number],
    ];
    const { container } = render(<LearnerQuestionView question={question} />);
    expect(container.textContent).not.toContain("LEAKED-DESCRIPTION-QQ");
    for (const e of container.querySelectorAll("*")) {
      for (const a of Array.from(e.attributes)) expect(a.value).not.toContain("LEAKED-DESCRIPTION-QQ");
    }
  });

  it("a stimulus placed in the stem appears there, before the parts", () => {
    const { container } = render(<LearnerQuestionView question={withFigure()} />);
    const img = screen.getByRole("img");
    const body = screen.getByText("Read a value.");
    expect(img.compareDocumentPosition(body) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(container.querySelectorAll('[role="img"]')).toHaveLength(1);
  });
});
