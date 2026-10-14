import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DocView, Math as MathView } from "../src";
import {
  bulletList, cell, doc, figure, hardBreak, header, mathBlock, mathInline, orderedList,
  para, quantity, row, table, text,
} from "./helpers";

const FALLBACK = /math could not be displayed/i;

describe("text is text (3.1)", () => {
  it("renders an img tag with onerror as literal text and creates no element", () => {
    const src = '<img src=x onerror="alert(1)">';
    const { container } = render(<DocView doc={doc(para(text(src)))} />);
    expect(container.querySelector("img")).toBeNull();
    expect(container.textContent).toContain(src);
  });

  it("renders a script tag as literal text and creates no element", () => {
    const src = "<script>window.__pwned = 1</script>";
    const { container } = render(<DocView doc={doc(para(text(src)))} />);
    expect(container.querySelector("script")).toBeNull();
    expect(container.textContent).toContain(src);
    expect((window as unknown as { __pwned?: number }).__pwned).toBeUndefined();
  });

  it("does not scan text for math: $x$ stays text and no KaTeX markup appears", () => {
    const { container } = render(<DocView doc={doc(para(text("the value $x^2$ here")))} />);
    expect(container.textContent).toContain("the value $x^2$ here");
    expect(container.querySelector(".katex")).toBeNull();
  });

  it("renders HTML entities and ampersands literally", () => {
    const { container } = render(<DocView doc={doc(para(text("a &amp; b <b>c</b>")))} />);
    expect(container.textContent).toContain("a &amp; b <b>c</b>");
    expect(container.querySelector("b")).toBeNull();
  });
});

describe("marks (3.1)", () => {
  it("bold -> strong, italic -> em, sub -> sub, sup -> sup", () => {
    const { container } = render(
      <DocView
        doc={doc(
          para(text("B", ["bold"]), text("I", ["italic"]), text("S", ["sub"]), text("P", ["sup"])),
        )}
      />,
    );
    expect(container.querySelector("strong")?.textContent).toBe("B");
    expect(container.querySelector("em")?.textContent).toBe("I");
    expect(container.querySelector("sub")?.textContent).toBe("S");
    expect(container.querySelector("sup")?.textContent).toBe("P");
  });

  it.each([
    [["bold", "italic"]],
    [["italic", "bold"]],
  ] as const)("bold+italic in order %j gives the same wrapping elements", (marks) => {
    const { container } = render(<DocView doc={doc(para(text("both", [...marks])))} />);
    const strong = container.querySelector("strong");
    const em = container.querySelector("em");
    expect(strong).not.toBeNull();
    expect(em).not.toBeNull();
    expect(container.querySelector("p")?.textContent).toBe("both");
    // Both elements wrap the word, in whichever nesting.
    expect(strong!.textContent).toBe("both");
    expect(em!.textContent).toBe("both");
  });

  it("sub combined with bold and italic, either order, keeps all three elements", () => {
    for (const marks of [["sub", "bold", "italic"], ["italic", "sub", "bold"]] as const) {
      const { container, unmount } = render(<DocView doc={doc(para(text("x", [...marks])))} />);
      expect(container.querySelector("sub")?.textContent).toBe("x");
      expect(container.querySelector("strong")?.textContent).toBe("x");
      expect(container.querySelector("em")?.textContent).toBe("x");
      unmount();
    }
  });

  it("optional wraps the words in parentheses", () => {
    const { container } = render(<DocView doc={doc(para(text("the "), text("extra", ["optional"])))} />);
    expect(container.querySelector("p")?.textContent).toBe("the (extra)");
  });

  it("essential is underlined (an element, class or inline style marks it) and keeps the words", () => {
    const { container } = render(<DocView doc={doc(para(text("must", ["essential"])))} />);
    const p = container.querySelector("p")!;
    expect(p.textContent).toBe("must");
    const inner = p.firstElementChild as HTMLElement | null;
    const marked =
      inner !== null &&
      (inner.tagName === "U" ||
        inner.className !== "" ||
        /underline/.test(inner.getAttribute("style") ?? "") ||
        inner.getAttribute("data-mark") !== null);
    expect(marked).toBe(true);
  });

  it("optional + bold in either order give identical text", () => {
    const a = render(<DocView doc={doc(para(text("w", ["optional", "bold"])))} />);
    const textA = a.container.textContent;
    expect(a.container.querySelector("strong")).not.toBeNull();
    a.unmount();
    const b = render(<DocView doc={doc(para(text("w", ["bold", "optional"])))} />);
    expect(b.container.textContent).toBe(textA);
    expect(b.container.querySelector("strong")).not.toBeNull();
    expect(textA).toBe("(w)");
  });

  it("marks apply to math_inline and quantity too", () => {
    const { container } = render(
      <DocView doc={doc(para(mathInline("x", ["bold"]), quantity("3.0", "s", null, ["optional"])))} />,
    );
    expect(container.querySelector("strong")).not.toBeNull();
    expect(container.textContent).toContain("(3.0\u2009s)");
  });
});

describe("math (3.1)", () => {
  it("renders inline math with KaTeX markup and MathML", () => {
    const { container } = render(<DocView doc={doc(para(text("Take "), mathInline("x^2")))} />);
    expect(container.querySelector(".katex")).not.toBeNull();
    expect(container.querySelector("math")).not.toBeNull();
    expect(container.querySelector(".katex-display")).toBeNull();
  });

  it("renders block math in display mode", () => {
    const { container } = render(<DocView doc={doc(mathBlock("\\frac{a}{b}"))} />);
    expect(container.querySelector(".katex-display")).not.toBeNull();
    expect(container.querySelector("math")).not.toBeNull();
  });

  it("Math component honours the display flag", () => {
    const inline = render(<MathView latex="y" display={false} />);
    expect(inline.container.querySelector(".katex")).not.toBeNull();
    expect(inline.container.querySelector(".katex-display")).toBeNull();
    inline.unmount();
    const block = render(<MathView latex="y" display />);
    expect(block.container.querySelector(".katex-display")).not.toBeNull();
  });

  it("uses no CDN: no link or script elements are produced", () => {
    const { container } = render(<DocView doc={doc(mathBlock("x"))} />);
    expect(container.querySelector("link, script")).toBeNull();
  });

  // KaTeX options must equal the server's: trust false, strict error, throwOnError true.
  const failing: [string, string][] = [
    ["\\href", "\\href{https://example.invalid}{click}"],
    ["\\url", "\\url{https://example.invalid}"],
    ["\\includegraphics", "\\includegraphics{pic.png}"],
    ["\\htmlClass", "\\htmlClass{evil}{x}"],
    ["undefined command", "\\notacommand{x}"],
    ["strict violation (accented unicode in math mode)", "\u00e9"],
    ["unbalanced group", "\\frac{a}{"],
  ];

  describe.each([true, false])("display=%s", (display) => {
    it.each(failing)("%s shows the fallback, source as text, no role=alert, no exception", (_n, latex) => {
      let result: ReturnType<typeof render> | undefined;
      expect(() => {
        result = render(<MathView latex={latex} display={display} />);
      }).not.toThrow();
      const { container } = result!;
      expect(container.textContent).toMatch(FALLBACK);
      expect(container.textContent).toContain(latex);
      expect(container.querySelector('[role="alert"]')).toBeNull();
      expect(container.querySelector("a")).toBeNull();
      expect(container.querySelector("img")).toBeNull();
      expect(container.querySelector(".evil")).toBeNull();
    });
  });

  it("a failing node inside a document does not stop the rest of the document", () => {
    render(<DocView doc={doc(para(text("before "), mathInline("\\notacommand")), para(text("after")))} />);
    expect(screen.getByText("after")).toBeInTheDocument();
    expect(document.body.textContent).toMatch(FALLBACK);
  });

  it("the fallback shows the source as text even when it looks like HTML", () => {
    const { container } = render(<MathView latex={"\\notacommand <img src=x onerror=alert(1)>"} display={false} />);
    expect(container.querySelector("img")).toBeNull();
    expect(container.textContent).toContain("<img src=x onerror=alert(1)>");
  });

  it("a valid formula shows no fallback", () => {
    const { container } = render(<MathView latex="\\sqrt{2}" display={false} />);
    expect(container.textContent).not.toMatch(FALLBACK);
  });
});

describe("scroll containers (3.1)", () => {
  it("math_block sits in a focusable container with an accessible name", () => {
    const { container } = render(<DocView doc={doc(mathBlock("a+b"))} />);
    const scrollers = container.querySelectorAll('[tabindex="0"]');
    expect(scrollers.length).toBeGreaterThanOrEqual(1);
    const holder = Array.from(scrollers).find((el) => el.querySelector(".katex-display"));
    expect(holder).toBeDefined();
    const name = holder!.getAttribute("aria-label") ?? holder!.getAttribute("aria-labelledby");
    expect(name).toBeTruthy();
  });

  it("a table sits in a focusable container with an accessible name", () => {
    const { container } = render(
      <DocView doc={doc(table(row(header(para(text("h")))), row(cell(para(text("c"))))))} />,
    );
    const holder = Array.from(container.querySelectorAll('[tabindex="0"]')).find((el) =>
      el.querySelector("table"),
    );
    expect(holder).toBeDefined();
    expect(holder!.getAttribute("aria-label") ?? holder!.getAttribute("aria-labelledby")).toBeTruthy();
  });

  it("inline math alone creates no focusable container", () => {
    const { container } = render(<DocView doc={doc(para(mathInline("x")))} />);
    expect(container.querySelector('[tabindex="0"]')).toBeNull();
  });
});

describe("quantity (3.1)", () => {
  const thin = "\u2009";
  it("renders value, U+2009, unit as written", () => {
    const { container } = render(<DocView doc={doc(para(quantity("3.0", "m/s")))} />);
    expect(container.textContent).toBe(`3.0${thin}m/s`);
  });

  it("keeps significant figures: 20.0 stays 20.0, 1.50e-3 stays as written", () => {
    const { container } = render(
      <DocView doc={doc(para(quantity("20.0", "N"), text(" and "), quantity("1.50e-3", "A")))} />,
    );
    expect(container.textContent).toBe(`20.0${thin}N and 1.50e-3${thin}A`);
  });

  it("renders uncertainty as value ± uncertainty unit", () => {
    const { container } = render(<DocView doc={doc(para(quantity("4.20", "kg", "0.05")))} />);
    expect(container.textContent).toMatch(/4\.20\s*\u00b1\s*0\.05\s*kg/);
  });

  it("does not convert or rewrite units (m/s, mu, Omega, degrees stay)", () => {
    const { container } = render(
      <DocView doc={doc(para(quantity("1", "m/s"), quantity("2", "\u00b5F"), quantity("3", "\u03a9"), quantity("4", "\u00b0C")))} />,
    );
    const t = container.textContent!;
    expect(t).toContain("m/s");
    expect(t).not.toContain("m s");
    expect(t).not.toContain("\u207b");
    expect(t).toContain("\u00b5F");
    expect(t).toContain("\u03a9");
    expect(t).toContain("\u00b0C");
  });

  it("a quantity with an empty unit shows the value without trailing junk", () => {
    const { container } = render(<DocView doc={doc(para(quantity("7", "")))} />);
    expect(container.textContent!.trim()).toBe("7");
  });
});

describe("blocks and breaks (3.1)", () => {
  it("hard_break gives <br>, paragraph gives <p>", () => {
    const { container } = render(
      <DocView doc={doc(para(text("one"), hardBreak(), text("two")), para(text("next")))} />,
    );
    expect(container.querySelectorAll("p")).toHaveLength(2);
    expect(container.querySelectorAll("br")).toHaveLength(1);
  });

  it("bullet and ordered lists give ul/ol/li", () => {
    const { container } = render(
      <DocView doc={doc(bulletList(para(text("a")), para(text("b"))), orderedList(para(text("c"))))} />,
    );
    expect(container.querySelectorAll("ul > li")).toHaveLength(2);
    expect(container.querySelectorAll("ol > li")).toHaveLength(1);
    expect(container.querySelector("ul")?.textContent).toBe("ab");
  });

  it("list items keep their order", () => {
    render(<DocView doc={doc(orderedList(para(text("first")), para(text("second")), para(text("third"))))} />);
    expect(screen.getAllByRole("listitem").map((li) => li.textContent)).toEqual(["first", "second", "third"]);
  });
});

describe("tables (3.1)", () => {
  it("header in the first row gets scope=col; header in a later row gets scope=row", () => {
    const { container } = render(
      <DocView
        doc={doc(
          table(
            row(header(para(text("Quantity"))), header(para(text("Value")))),
            row(header(para(text("Mass"))), cell(para(text("2.0")))),
          ),
        )}
      />,
    );
    const ths = container.querySelectorAll("th");
    expect(ths).toHaveLength(3);
    expect(ths[0]!.getAttribute("scope")).toBe("col");
    expect(ths[1]!.getAttribute("scope")).toBe("col");
    expect(ths[2]!.getAttribute("scope")).toBe("row");
    expect(container.querySelectorAll("td")).toHaveLength(1);
  });

  it("passes colspan and rowspan through", () => {
    const { container } = render(
      <DocView
        doc={doc(
          table(
            row(header(para(text("wide")), 2, 1), header(para(text("tall")), 1, 2)),
            row(cell(para(text("a")), 1, 1), cell(para(text("b")), 1, 1)),
          ),
        )}
      />,
    );
    expect(container.querySelectorAll("th")[0]!.getAttribute("colspan")).toBe("2");
    expect(container.querySelectorAll("th")[1]!.getAttribute("rowspan")).toBe("2");
  });

  it("cell text is text, not HTML", () => {
    const { container } = render(
      <DocView doc={doc(table(row(cell(para(text("<b>x</b>"))))))} />,
    );
    expect(container.querySelector("td b")).toBeNull();
    expect(container.querySelector("td")?.textContent).toBe("<b>x</b>");
  });
});

describe("figure placeholder (3.1)", () => {
  it("DocView renders a role=img placeholder with a label naming the figure", () => {
    render(<DocView doc={doc(figure("s1"))} />);
    const img = screen.getByRole("img");
    const label = img.getAttribute("aria-label") ?? "";
    expect(label.length).toBeGreaterThan(0);
    expect(within(img).queryByText(/description/i)).toBeNull();
  });
});
