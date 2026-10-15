import type { Doc } from "@qlab/api-client";
import type { Editor } from "@tiptap/core";
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import { DocEditor, type DocEditorProps } from "../src";
import { validateDoc } from "../src/validate";

const text = (t: string, marks: { type: string }[] = []) => ({ marks, type: "text", text: t });
const doc = (...content: unknown[]) => ({ type: "doc", content }) as unknown as Doc;
const para = (...c: unknown[]) => ({ type: "paragraph", content: c });

function Harness({ initial, onDoc, ...rest }: { initial: Doc; onDoc?: (d: Doc) => void } & Partial<DocEditorProps>) {
  const [value, setValue] = useState(initial);
  return (
    <DocEditor
      label="Question stem"
      value={value}
      onChange={(d) => {
        setValue(d);
        onDoc?.(d);
      }}
      {...rest}
    />
  );
}

function paste(box: HTMLElement, html: string, plain = "") {
  const data: Record<string, string> = { "text/html": html, "text/plain": plain };
  fireEvent.paste(box, { clipboardData: { getData: (t: string) => data[t] ?? "", types: Object.keys(data), files: [], items: [] } });
}

async function setup(initial: Doc, props: Partial<DocEditorProps> = {}) {
  const docs: Doc[] = [];
  render(<Harness initial={initial} onDoc={(d) => docs.push(d)} {...props} />);
  const box = await screen.findByRole("textbox", { name: "Question stem" });
  const editor = (box as unknown as { editor: Editor }).editor;
  return { box, editor, docs, last: () => docs[docs.length - 1]! };
}

describe("DocEditor", () => {
  it("is a labelled textbox with a described-by link", async () => {
    const { box } = await setup(doc(para(text("hi"))), { ariaDescribedBy: "help" });
    expect(box).toHaveAttribute("aria-multiline", "true");
    expect(box).toHaveAttribute("aria-describedby", "help");
    expect(screen.getByText("Question stem")).toBeVisible();
  });

  it("reports edits as a valid Doc in the server's shape", async () => {
    const { editor, last } = await setup(doc(para(text("hi"))));
    act(() => {
      editor.chain().focus("end").insertContent(" there").run();
    });
    expect(last()).toEqual(doc(para(text("hi there"))));
    expect(validateDoc(last())).toEqual([]);
  });

  it("does not call onChange for the initial load", async () => {
    const { docs } = await setup(doc(para(text("hi"))));
    expect(docs).toEqual([]);
  });

  it("follows an outside change of value", async () => {
    const view = render(<DocEditor label="Question stem" value={doc(para(text("one")))} onChange={() => {}} />);
    await screen.findByRole("textbox");
    view.rerender(<DocEditor label="Question stem" value={doc(para(text("two")))} onChange={() => {}} />);
    await waitFor(() => expect(screen.getByRole("textbox")).toHaveTextContent("two"));
  });

  it("toggles marks from the toolbar, with pressed state", async () => {
    const { editor, last } = await setup(doc(para(text("word"))));
    act(() => {
      editor.commands.selectAll();
    });
    const bold = screen.getByRole("button", { name: "Bold" });
    fireEvent.click(bold);
    expect(last()).toEqual(doc(para(text("word", [{ type: "bold" }]))));
    await waitFor(() => expect(bold).toHaveAttribute("aria-pressed", "true"));
    fireEvent.click(screen.getByRole("button", { name: "Subscript" }));
    fireEvent.click(screen.getByRole("button", { name: "Superscript" }));
    expect(last()).toEqual(doc(para(text("word", [{ type: "bold" }, { type: "sup" }]))));
    fireEvent.click(bold);
    expect(last()).toEqual(doc(para(text("word", [{ type: "sup" }]))));
  });

  it("offers essential and table only when enabled, and never a figure button", async () => {
    const first = await setup(doc(para()));
    const names = (await screen.findAllByRole("button")).map((b) => b.getAttribute("aria-label"));
    expect(names).not.toContain("Essential words (underline)");
    expect(names).not.toContain("Insert table");
    expect(names.join(" ")).not.toMatch(/figure/i);
    expect(first.box).toBeInTheDocument();
  });

  it("offers essential and table when the props allow them", async () => {
    await setup(doc(para()), { allowMarks: ["bold", "essential"], allowedBlocks: ["table"] });
    expect(screen.getByRole("button", { name: "Essential words (underline)" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Insert table" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Italic" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Bulleted list" })).toBeNull();
  });

  it("is a toolbar with named buttons and arrow-key navigation", async () => {
    await setup(doc(para()));
    const bar = screen.getByRole("toolbar", { name: "Question stem formatting" });
    const buttons = within(bar).getAllByRole("button");
    for (const name of ["Bold", "Italic", "Subscript", "Superscript", "Optional words (« »)", "Inline equation", "Block equation", "Bulleted list", "Numbered list"]) {
      expect(within(bar).getByRole("button", { name })).toBeInTheDocument();
    }
    expect(buttons.filter((b) => b.tabIndex === 0)).toHaveLength(1);
    buttons[0]!.focus();
    fireEvent.keyDown(buttons[0]!, { key: "ArrowRight" });
    expect(buttons[1]).toHaveFocus();
    expect(buttons[1]!.tabIndex).toBe(0);
    fireEvent.keyDown(buttons[1]!, { key: "End" });
    expect(buttons[buttons.length - 1]).toHaveFocus();
    fireEvent.keyDown(buttons[buttons.length - 1]!, { key: "ArrowRight" });
    expect(buttons[0]).toHaveFocus();
  });

  it("makes bullet and numbered lists", async () => {
    const { editor, last } = await setup(doc(para(text("a"))));
    act(() => {
      editor.commands.setTextSelection(2);
    });
    fireEvent.click(screen.getByRole("button", { name: "Bulleted list" }));
    expect(last()).toEqual(doc({ type: "bullet_list", content: [{ type: "list_item", content: [para(text("a"))] }] }));
    fireEvent.click(screen.getByRole("button", { name: "Numbered list" }));
    expect(last().content[0]!.type).toBe("ordered_list");
  });

  it("inserts a table and edits its rows", async () => {
    const { editor, last } = await setup(doc(para(text("a"))), { allowedBlocks: ["table"] });
    fireEvent.click(screen.getByRole("button", { name: "Insert table" }));
    act(() => {
      editor.commands.setTextSelection(4);
    });
    const table = last().content.find((b) => b.type === "table")!;
    expect(table.content).toHaveLength(2);
    expect(validateDoc(last())).toEqual([]);
    fireEvent.click(await screen.findByRole("button", { name: "Add row below" }));
    expect(last().content.find((b) => b.type === "table")!.content).toHaveLength(3);
    expect(validateDoc(last())).toEqual([]);
  });

  describe("math", () => {
    it("inserts inline math through a LaTeX field with live preview", async () => {
      const { last, box } = await setup(doc(para(text("a"))));
      fireEvent.click(screen.getByRole("button", { name: "Inline equation" }));
      const input = screen.getByLabelText("LaTeX");
      expect(screen.getByText("LaTeX cannot be empty.")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Insert" })).toBeDisabled();
      fireEvent.change(input, { target: { value: "x^2" } });
      expect(document.querySelector(".qe-preview .katex")).not.toBeNull();
      fireEvent.click(screen.getByRole("button", { name: "Insert" }));
      const para0 = last().content[0] as unknown as { content: { type: string; attrs?: { latex: string }; marks?: unknown[] }[] };
      expect(para0.content.find((n) => n.type === "math_inline")).toEqual({ marks: [], type: "math_inline", attrs: { latex: "x^2" } });
      await waitFor(() => expect(box.querySelector(".katex")).not.toBeNull());
    });

    it("shows the KaTeX error and does not accept an unrenderable formula", async () => {
      const { docs } = await setup(doc(para(text("a"))));
      fireEvent.click(screen.getByRole("button", { name: "Inline equation" }));
      fireEvent.change(screen.getByLabelText("LaTeX"), { target: { value: "\\frac{1}" } });
      expect(screen.getByRole("alert")).toHaveTextContent(/KaTeX cannot render/);
      expect(screen.getByRole("button", { name: "Insert" })).toBeDisabled();
      expect(docs).toEqual([]);
    });

    it("refuses commands KaTeX would leave untrusted", async () => {
      await setup(doc(para(text("a"))));
      fireEvent.click(screen.getByRole("button", { name: "Inline equation" }));
      fireEvent.change(screen.getByLabelText("LaTeX"), { target: { value: "\\href{https://x.invalid}{a}" } });
      expect(screen.getByRole("button", { name: "Insert" })).toBeDisabled();
    });

    it("edits an existing math node by clicking it", async () => {
      const { last } = await setup(doc(para({ marks: [], type: "math_inline", attrs: { latex: "a+b" } })));
      const open = await screen.findByRole("button", { name: "Edit inline equation: a+b" });
      fireEvent.click(open);
      const input = screen.getByLabelText("LaTeX");
      fireEvent.change(input, { target: { value: "" } });
      expect(screen.getByRole("button", { name: "Apply" })).toBeDisabled();
      fireEvent.change(input, { target: { value: "c-d" } });
      fireEvent.click(screen.getByRole("button", { name: "Apply" }));
      expect(last()).toEqual(doc(para({ marks: [], type: "math_inline", attrs: { latex: "c-d" } })));
    });

    it("edits a block equation and cancels with Escape", async () => {
      const { docs } = await setup(doc(para(text("a")), { type: "math_block", attrs: { latex: "E=mc^2" } }));
      fireEvent.click(await screen.findByRole("button", { name: "Edit block equation: E=mc^2" }));
      fireEvent.keyDown(screen.getByLabelText("LaTeX"), { key: "Escape" });
      expect(screen.queryByLabelText("LaTeX")).toBeNull();
      expect(docs).toEqual([]);
    });
  });

  describe("quantity", () => {
    const q = (attrs: Record<string, unknown>) => para({ marks: [], type: "quantity", attrs });

    it("shows value and unit and edits through validated fields", async () => {
      const { last } = await setup(doc(q({ value: "9.81", unit: "m s^-1", param: null, uncertainty: null })));
      const open = await screen.findByRole("button", { name: "Edit quantity: 9.81 m s^-1" });
      expect(open).toHaveTextContent("9.81 m s^-1");
      fireEvent.click(open);
      fireEvent.change(screen.getByLabelText("Value"), { target: { value: "x" } });
      expect(screen.getByText("Value has an invalid format.")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Apply" })).toBeDisabled();
      fireEvent.change(screen.getByLabelText("Value"), { target: { value: "10.0" } });
      fireEvent.change(screen.getByLabelText("Parameter name"), { target: { value: "g" } });
      fireEvent.change(screen.getByLabelText("Uncertainty"), { target: { value: "0.5" } });
      fireEvent.click(screen.getByRole("button", { name: "Apply" }));
      expect(last()).toEqual(doc(q({ value: "10.0", unit: "m s^-1", param: "g", uncertainty: "0.5" })));
    });
  });

  describe("figure", () => {
    const figure = { type: "figure", attrs: { stimulus_id: "s1" } };

    it("shows a non-editable chip and keeps the node untouched", async () => {
      const { box, docs } = await setup(doc(para(text("a")), figure));
      const chip = await screen.findByText("Figure (s1)");
      expect(chip.closest("[contenteditable=false]")).not.toBeNull();
      expect(box).toContainElement(chip);
      expect(docs).toEqual([]);
    });

    it("cannot be inserted: no button, and pasted figure markup is not in the schema", async () => {
      const { editor } = await setup(doc(para(text("a"))));
      expect(screen.queryByRole("button", { name: /figure/i })).toBeNull();
      act(() => {
        editor.commands.insertContent('<div data-node="figure" data-stimulus-id="x"></div><p>kept</p>');
      });
      expect(JSON.stringify(editor.getJSON())).not.toContain("figure");
    });
  });

  describe("paste", () => {
    it("keeps schema content and drops the rest", async () => {
      const { box, last } = await setup(doc(para()));
      paste(box, '<h1>Title</h1><p><b>bold</b> <span style="color:red">red</span> <img src="x" alt="i"><script>1</script></p>');
      const out = JSON.stringify(last());
      expect(out).toContain('"bold"');
      expect(out).toContain("Title");
      expect(out).not.toMatch(/script|img|heading|color/);
      expect(validateDoc(last())).toEqual([]);
    });

    it("unwraps a pasted table when tables are not allowed", async () => {
      const { box, last } = await setup(doc(para()));
      paste(box, "<table><tr><td>cell</td></tr></table>");
      expect(JSON.stringify(last())).not.toContain("table");
      expect(JSON.stringify(last())).toContain("cell");
    });

    it("strips marks the field does not allow", async () => {
      const { box, last } = await setup(doc(para()), { allowMarks: ["bold"] });
      paste(box, "<p><i>slanted</i> <b>strong</b></p>");
      const out = JSON.stringify(last());
      expect(out).toContain('"bold"');
      expect(out).not.toContain("italic");
    });
  });

  it("calls onChange with a fresh Doc each time (no shared mutation)", async () => {
    const spy = vi.fn();
    render(<DocEditor label="Question stem" value={doc(para(text("a")))} onChange={spy} />);
    const box = await screen.findByRole("textbox");
    const editor = (box as unknown as { editor: Editor }).editor;
    act(() => {
      editor.chain().focus("end").insertContent("b").run();
    });
    act(() => {
      editor.chain().focus("end").insertContent("c").run();
    });
    expect(spy).toHaveBeenCalledTimes(2);
    expect(spy.mock.calls[0]![0]).not.toBe(spy.mock.calls[1]![0]);
  });
});
