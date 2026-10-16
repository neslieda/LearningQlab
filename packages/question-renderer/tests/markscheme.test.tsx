import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarkSchemeView, type MarkPointOut, type NoteOut } from "../src";
import { d, doc, para, text } from "./helpers";

const mp = (id: string, s: string, extra: Partial<MarkPointOut> = {}): MarkPointOut => ({
  id,
  content: d(s),
  kind: "statement",
  alternative_group: null,
  route: null,
  accept_range: null,
  ...extra,
});
const note = (kind: NoteOut["kind"], s: string, mark_point_id: string | null = null): NoteOut => ({
  kind,
  content: d(s),
  mark_point_id,
});
const idx = (c: HTMLElement, ...needles: string[]) => needles.map((n) => (c.textContent ?? "").indexOf(n));
const ascending = (xs: number[]) => xs.every((x, i) => x >= 0 && (i === 0 || x > xs[i - 1]!));
const count = (s: string, sub: string) => s.split(sub).length - 1;

describe("mark points (3.3)", () => {
  it("shows the points in the given order, each introduced by a check mark", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[mp("m1", "FIRST"), mp("m2", "SECOND"), mp("m3", "THIRD")]}
        notes={[]}
        marks={3}
        marksCapped={false}
      />,
    );
    const t = container.textContent!;
    expect(ascending(idx(container, "FIRST", "SECOND", "THIRD"))).toBe(true);
    expect(count(t, "✓")).toBe(3);
  });

  it("the check mark is visual: hidden from assistive tech and 'mark point' is readable", () => {
    const { container } = render(
      <MarkSchemeView markPoints={[mp("m1", "ONE")]} notes={[]} marks={1} marksCapped={false} />,
    );
    const tick = Array.from(container.querySelectorAll("*")).find(
      (e) => e.children.length === 0 && e.textContent === "✓",
    );
    expect(tick).toBeDefined();
    const hidden = tick!.closest('[aria-hidden="true"]') !== null;
    expect(hidden).toBe(true);
    const named =
      Array.from(container.querySelectorAll("[aria-label]")).some((e) => /mark point/i.test(e.getAttribute("aria-label")!)) ||
      /mark point/i.test(container.textContent!);
    expect(named).toBe(true);
  });

  it("points sharing an alternative group are joined by OR and form one group", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[
          mp("m1", "ALT-ONE", { alternative_group: "g" }),
          mp("m2", "ALT-TWO", { alternative_group: "g" }),
          mp("m3", "SEPARATE"),
        ]}
        notes={[]}
        marks={2}
        marksCapped={false}
      />,
    );
    const t = container.textContent!;
    expect(ascending(idx(container, "ALT-ONE", "OR", "ALT-TWO", "SEPARATE"))).toBe(true);
    expect(count(t, "OR")).toBe(1);
  });

  it("three alternatives give two ORs", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={["x", "y", "z"].map((s, i) => mp(`m${i}`, `ALT-${s}`, { alternative_group: "g" }))}
        notes={[]}
        marks={1}
        marksCapped={false}
      />,
    );
    expect(count(container.textContent!, "OR")).toBe(2);
  });

  it("points with different alternative groups are not joined by OR", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[
          mp("m1", "AA", { alternative_group: "g1" }),
          mp("m2", "BB", { alternative_group: "g2" }),
        ]}
        notes={[]}
        marks={2}
        marksCapped={false}
      />,
    );
    expect(container.textContent).not.toContain("OR");
  });

  it("routes are grouped and labelled Method 1, Method 2, in order of appearance", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[
          mp("m1", "R1-A", { route: "first" }),
          mp("m2", "R1-B", { route: "first" }),
          mp("m3", "R2-A", { route: "second" }),
          mp("m4", "R2-B", { route: "second" }),
        ]}
        notes={[]}
        marks={2}
        marksCapped={false}
      />,
    );
    expect(ascending(idx(container, "Method 1", "R1-A", "R1-B", "Method 2", "R2-A", "R2-B"))).toBe(true);
    expect(container.textContent).not.toContain("Method 3");
  });

  it("a mark scheme without routes has no Method heading", () => {
    const { container } = render(
      <MarkSchemeView markPoints={[mp("m1", "NOROUTE")]} notes={[]} marks={1} marksCapped={false} />,
    );
    expect(container.textContent).not.toContain("Method");
  });

  it("accept_range is written as 'Accept min-max unit'", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[mp("m1", "ANS", { kind: "answer", accept_range: { minimum: "1.2", maximum: "1.4", unit: "m" } })]}
        notes={[]}
        marks={1}
        marksCapped={false}
      />,
    );
    expect(container.textContent).toMatch(/Accept\s+1\.2\s*–\s*1\.4\s+m/);
  });

  it("accept_range keeps trailing zeros as written", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[mp("m1", "ANS", { accept_range: { minimum: "2.50", maximum: "3.00", unit: "" } })]}
        notes={[]}
        marks={1}
        marksCapped={false}
      />,
    );
    expect(container.textContent).toMatch(/2\.50\s*–\s*3\.00/);
  });

  it("renders rich content in a point (math, marks)", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[mp("m1", "", { content: doc(para(text("use "), text("F = ma", ["bold"]))) })]}
        notes={[]}
        marks={1}
        marksCapped={false}
      />,
    );
    expect(container.querySelector("strong")?.textContent).toBe("F = ma");
  });
});

describe("notes (3.3)", () => {
  const kinds: [NoteOut["kind"], string | null][] = [
    ["owtte", "OWTTE"],
    ["accept", "Accept"],
    ["do_not_accept", "Do not accept"],
    ["cap", "Max"],
    ["ecf", "ECF"],
    ["general", null],
  ];

  it.each(kinds)("kind %s has prefix %s", (kind, prefix) => {
    const { container } = render(
      <MarkSchemeView markPoints={[mp("m1", "POINT")]} notes={[note(kind, "NOTE-BODY")]} marks={1} marksCapped={false} />,
    );
    const t = container.textContent!;
    expect(t).toContain("NOTE-BODY");
    const after = t.slice(t.indexOf("POINT") + 5);
    if (prefix) {
      expect(after).toMatch(new RegExp(`${prefix}[\\s:.\\u2013-]*NOTE-BODY`));
    } else {
      // general: nothing but whitespace/separators precedes the note text
      expect(after.trim().startsWith("NOTE-BODY")).toBe(true);
    }
  });

  it("general notes carry none of the prefixes", () => {
    const { container } = render(
      <MarkSchemeView markPoints={[]} notes={[note("general", "PLAIN")]} marks={1} marksCapped={false} />,
    );
    for (const p of ["OWTTE", "Accept", "Do not accept", "Max", "ECF"]) {
      expect(container.textContent).not.toContain(p);
    }
  });

  it("notes come after all points", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[mp("m1", "P-ONE"), mp("m2", "P-TWO")]}
        notes={[note("general", "N-GENERAL"), note("ecf", "N-ECF")]}
        marks={2}
        marksCapped={false}
      />,
    );
    expect(ascending(idx(container, "P-ONE", "P-TWO", "N-GENERAL", "N-ECF"))).toBe(true);
  });

  it("a note tied to a mark point appears right after that point, before the next", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[mp("m1", "P-ONE"), mp("m2", "P-TWO"), mp("m3", "P-THREE")]}
        notes={[note("general", "N-LOOSE"), note("accept", "N-TIED", "m2")]}
        marks={3}
        marksCapped={false}
      />,
    );
    expect(ascending(idx(container, "P-ONE", "P-TWO", "N-TIED", "P-THREE", "N-LOOSE"))).toBe(true);
  });

  it("two notes tied to the same point both follow it in the given order", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[mp("m1", "P-ONE"), mp("m2", "P-TWO")]}
        notes={[note("accept", "N-1", "m1"), note("do_not_accept", "N-2", "m1")]}
        marks={2}
        marksCapped={false}
      />,
    );
    expect(ascending(idx(container, "P-ONE", "N-1", "N-2", "P-TWO"))).toBe(true);
  });

  it("a tied note is indented under its point (nested in the point's element)", () => {
    const { container } = render(
      <MarkSchemeView
        markPoints={[mp("m1", "P-ONE"), mp("m2", "P-TWO")]}
        notes={[note("accept", "N-TIED", "m1")]}
        marks={2}
        marksCapped={false}
      />,
    );
    const all = Array.from(container.querySelectorAll("*"));
    // The smallest element holding both the first point and its note must not also hold the second point.
    const holders = all.filter((e) => e.textContent!.includes("P-ONE") && e.textContent!.includes("N-TIED"));
    const smallest = holders.reduce((a, b) => (b.textContent!.length < a.textContent!.length ? b : a));
    expect(smallest.textContent).not.toContain("P-TWO");
  });
});

describe("marks heading (3.3)", () => {
  it("shows [n] when not capped", () => {
    const { container } = render(
      <MarkSchemeView markPoints={[mp("m1", "x")]} notes={[]} marks={3} marksCapped={false} />,
    );
    expect(container.textContent).toContain("[3]");
    expect(container.textContent).not.toContain("max");
  });

  it("shows [max n] when capped", () => {
    const { container } = render(
      <MarkSchemeView markPoints={[mp("m1", "x")]} notes={[]} marks={2} marksCapped />,
    );
    expect(container.textContent).toContain("[max 2]");
  });
});
