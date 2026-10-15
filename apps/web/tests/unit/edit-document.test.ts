// Slice 7b section 5 (test 7) and section 4 (error mapping): pure operations on the question document.
// All data is synthetic.
import { describe, expect, it } from "vitest";
import type { Doc, QuestionDocument } from "@qlab/api-client";
import {
  addMarkPoint,
  addNote,
  newDocument,
  setQuestionClass,
  setMcqShape,
  setPrimaryNode,
  createProblems,
  addPart,
  movePart,
  removePart,
  referenceNotice,
  matchField,
  topLevelPartCount,
  clientProblems,
  describePath,
  emptyDoc,
  isBlankDoc,
  moveMarkPoint,
  moveNote,
  newMarkPointId,
  notesPointingAt,
  partTag,
  pathLabel,
  removeMarkPoint,
  removeNote,
  serverProblems,
  setPartMarks,
  totalMarks,
  updateMarkPoint,
} from "../../src/lib/edit-document";

const text = (t: string): Doc => ({ type: "doc", content: [{ type: "paragraph", content: [{ type: "text", text: t, marks: [] }] }] }) as Doc;

function part(label: string, marks: number, ids: string[]): QuestionDocument["parts"][number] {
  return {
    id: label,
    label,
    body: text(`Body ${label}`),
    marks,
    marks_capped: false,
    show_that: false,
    command_term: "state",
    answer_type: "word_phrase",
    level_content: "sl_core",
    syllabus_node: "n1",
    stimulus_refs: [],
    depends_on: [],
    ecf_from: [],
    mark_points: ids.map((id) => ({ id, content: text(`Point ${id}`), kind: "statement" })),
    notes: [
      { kind: "general", content: text("N1") },
      { kind: "accept", content: text("N2"), mark_point_id: ids[0] ?? null },
    ],
  } as QuestionDocument["parts"][number];
}

function doc(): QuestionDocument {
  return {
    schema_version: "1.0",
    question_class: "short_structured",
    exam_section: "b",
    levels: ["sl"],
    language: "en",
    calculator: true,
    primary_syllabus_node: "n1",
    secondary_syllabus_nodes: [],
    stem: text("Stem"),
    stimuli: [],
    parts: [part("a", 2, ["a-m1", "a-m2"]), part("c.ii", 1, ["c.ii-m1"])],
    total_marks: 3,
  } as QuestionDocument;
}

describe("mark points", () => {
  it("adds a point with an id in the existing style that is unique in the question", () => {
    const d = addMarkPoint(doc(), 0);
    expect(d.parts[0]!.mark_points.map((m) => m.id)).toEqual(["a-m1", "a-m2", "a-m3"]);
    expect(d.parts[0]!.mark_points[2]).toMatchObject({ kind: "statement" });
    expect(isBlankDoc(d.parts[0]!.mark_points[2]!.content)).toBe(true);
    expect(addMarkPoint(doc(), 1).parts[1]!.mark_points.at(-1)!.id).toBe("c.ii-m2");
  });

  it("skips ids that are taken, also by another part", () => {
    const d = doc();
    d.parts[0]!.mark_points[1] = { ...d.parts[0]!.mark_points[1]!, id: "a-m3" }; // a-m2 is gone, a-m3 exists
    expect(newMarkPointId(d, 0)).toBe("a-m4");
    d.parts[1]!.mark_points[0] = { ...d.parts[1]!.mark_points[0]!, id: "a-m3" };
    expect(newMarkPointId(d, 0)).toBe("a-m4");
  });

  it("removes a point, points its notes at the whole part, and keeps at least one", () => {
    const d = removeMarkPoint(doc(), 0, 0);
    expect(d.parts[0]!.mark_points.map((m) => m.id)).toEqual(["a-m2"]);
    expect(d.parts[0]!.notes[1]!.mark_point_id).toBeNull();
    expect(removeMarkPoint(doc(), 1, 0)).toEqual(doc());
  });

  it("counts the notes that a removal rebinds to the whole part", () => {
    expect(notesPointingAt(doc(), 0, 0)).toBe(1);
    expect(notesPointingAt(doc(), 0, 1)).toBe(0);
    expect(notesPointingAt(doc(), 1, 0)).toBe(0); // the last point cannot be removed
  });

  it("moves a point up and down, and ignores moves past the ends", () => {
    const down = moveMarkPoint(doc(), 0, 0, 1);
    expect(down.parts[0]!.mark_points.map((m) => m.id)).toEqual(["a-m2", "a-m1"]);
    const up = moveMarkPoint(down, 0, 1, -1);
    expect(up.parts[0]!.mark_points.map((m) => m.id)).toEqual(["a-m1", "a-m2"]);
    const d = doc();
    expect(moveMarkPoint(d, 0, 0, -1)).toBe(d);
    expect(moveMarkPoint(d, 0, 1, 1)).toBe(d);
  });

  it("does not mutate its input", () => {
    const d = doc();
    const before = JSON.stringify(d);
    addMarkPoint(d, 0);
    removeMarkPoint(d, 0, 0);
    moveMarkPoint(d, 0, 0, 1);
    updateMarkPoint(d, 0, 0, { kind: "method" });
    setPartMarks(d, 0, 3);
    addNote(d, 0);
    removeNote(d, 0, 0);
    moveNote(d, 0, 0, 1);
    expect(JSON.stringify(d)).toBe(before);
  });
});

describe("notes", () => {
  it("adds, removes and moves notes", () => {
    const added = addNote(doc(), 0);
    expect(added.parts[0]!.notes).toHaveLength(3);
    expect(added.parts[0]!.notes[2]).toMatchObject({ kind: "general" });
    const moved = moveNote(doc(), 0, 1, -1);
    expect(moved.parts[0]!.notes.map((n) => n.kind)).toEqual(["accept", "general"]);
    expect(removeNote(doc(), 0, 0).parts[0]!.notes.map((n) => n.kind)).toEqual(["accept"]);
  });
});

describe("marks", () => {
  it("sets part marks within 1 to 3 and recomputes the total", () => {
    const d = setPartMarks(doc(), 1, 3);
    expect(d.parts[1]!.marks).toBe(3);
    expect(d.total_marks).toBe(5);
    expect(setPartMarks(doc(), 0, 9).parts[0]!.marks).toBe(3);
    expect(setPartMarks(doc(), 0, 0).parts[0]!.marks).toBe(1);
    expect(setPartMarks(doc(), 0, Number.NaN).parts[0]!.marks).toBe(1);
    expect(setPartMarks(doc(), 0, 2.4).parts[0]!.marks).toBe(2);
    expect(totalMarks(d)).toBe(5);
  });

  it("a multiple-choice question always has 1 mark", () => {
    expect(totalMarks({ ...doc(), question_class: "mcq", parts: [] })).toBe(1);
  });
});

describe("labels", () => {
  it("writes part tags", () => {
    expect(partTag("a")).toBe("(a)");
    expect(partTag("c.ii")).toBe("(c)(ii)");
  });

  it("turns paths into field names, also in the server's location style", () => {
    const d = doc();
    expect(pathLabel("stem.content[0].content[1].text", d)).toBe("Stem");
    expect(pathLabel("parts[0].body.content[0]", d)).toBe("Part (a) body");
    expect(pathLabel("parts.1.mark_points.0.content", d)).toBe("Part (c)(ii), mark point 1");
    expect(pathLabel("body.document.parts.0.notes.1.content", d)).toBe("Part (a), note 2");
    expect(pathLabel("parts[0].marks", d)).toBe("Part (a) marks");
    expect(pathLabel("mcq.options[1].rationale.content[0]", d)).toBe("Rationale for B");
    expect(pathLabel("mcq.explanation", d)).toBe("Explanation");
    expect(describePath("parts.0.ecf_from", d).field).toBe("parts[0].ecf_from");
    expect(describePath("parts[0].body.content[0].text", d).field).toBe("parts[0].body");
    expect(describePath("parts[0].mark_points[1].content.content[0]", d).field).toBe("parts[0].mark_points[1].content");
  });
});

describe("client checks", () => {
  it("finds Turkish-only letters and names the field", () => {
    const d = doc();
    d.parts[0]!.mark_points[1] = { ...d.parts[0]!.mark_points[1]!, content: text("ışık") };
    const found = clientProblems(d);
    expect(found).toEqual([{ field: "parts[0].mark_points[1].content", label: "Part (a), mark point 2", message: "Content must be written in English" }]);
  });

  it("finds empty required fields and a missing level", () => {
    const d = { ...doc(), stem: emptyDoc(), levels: [] };
    const fields = clientProblems(d).map((p) => p.field);
    expect(fields).toContain("stem");
    expect(fields).toContain("levels");
  });

  it("accepts a valid document", () => {
    expect(clientProblems(doc())).toEqual([]);
  });
});

describe("server problems", () => {
  it("maps non-English paths, part-prefixed messages and request locations", () => {
    const d = doc();
    const found = serverProblems(
      [
        { message: "Content must be written in English; found non-English letters at stem.content[0].content[0].text, parts[0].body.content[0].content[0].text" },
        { message: "part c.ii: unknown command term 'zz'" },
        { message: "Value error, part a: 3 awardable mark points for 2 marks", location: "body.document" },
        { message: "Field required", location: "body.document.parts.0.answer_type" },
        { message: "math `x`: does not render: bad" },
      ],
      d,
    );
    expect(found).toEqual([
      { field: "stem", label: "Stem", message: "Content must be written in English" },
      { field: "parts[0].body", label: "Part (a) body", message: "Content must be written in English" },
      { field: "parts[1].command_term", label: "Part (c)(ii) command term", message: "part c.ii: unknown command term 'zz'" },
      { field: "parts[0].marks", label: "Part (a) marks", message: "part a: 3 awardable mark points for 2 marks" },
      { field: "parts[0].answer_type", label: "Part (a) answer type", message: "Field required" },
      { field: null, label: null, message: "math `x`: does not render: bad" },
    ]);
  });
});

function threeParts(): QuestionDocument {
  const d = doc();
  d.parts = [part("a", 1, ["a-m1"]), { ...part("b", 2, ["b-m1"]), ecf_from: ["a"], depends_on: ["a"] }, { ...part("c", 1, ["c-m1"]), ecf_from: ["b", "a"], depends_on: ["b"] }];
  d.total_marks = 4;
  return d;
}

describe("parts", () => {
  it("adds a lettered part with defaults and a unique id, and recomputes the total", () => {
    const d = addPart(threeParts());
    const added = d.parts[3]!;
    expect(added).toMatchObject({ label: "d", marks: 1, answer_type: "word_phrase", command_term: null, ecf_from: [], depends_on: [] });
    expect(added.mark_points).toHaveLength(1);
    expect(added.mark_points[0]!.id).toBe("d-m1");
    expect(isBlankDoc(added.body)).toBe(true);
    expect(isBlankDoc(added.mark_points[0]!.content)).toBe(true);
    expect(d.total_marks).toBe(5);
  });

  it("gives a new part an id nobody else has", () => {
    const d = threeParts();
    d.parts[0] = { ...d.parts[0]!, id: "d" };
    expect(addPart(d).parts[3]!.id).toBe("d-2");
  });

  it("removes a part, relabels the rest in order and keeps ids", () => {
    const { doc: d, dropped } = removePart(threeParts(), 1);
    expect(d.parts.map((p) => [p.label, p.id])).toEqual([["a", "a"], ["b", "c"]]);
    expect(d.total_marks).toBe(2);
    // part c pointed at b (gone) and a: only the reference to a survives
    expect(d.parts[1]!.ecf_from).toEqual(["a"]);
    expect(d.parts[1]!.depends_on).toEqual([]);
    expect(dropped).toBe(2);
  });

  it("drops solution-model answers bound to a removed part and counts them", () => {
    const d = threeParts();
    d.solution_model = {
      parameters: [],
      constants: [],
      steps: [{ id: "s1", name: "s_one", expr: "1", unit: "" }],
      answers: [{ part_id: "a", step: "s1" }, { part_id: "c", step: "s1" }],
    } as QuestionDocument["solution_model"];
    const { doc: next, dropped } = removePart(d, 2);
    expect(next.solution_model!.answers).toEqual([{ part_id: "a", step: "s1" }]);
    expect(next.solution_model!.steps).toHaveLength(1);
    expect(dropped).toBe(1);
    expect(movePart(d, 0, 1).doc.solution_model!.answers).toHaveLength(2);
  });

  it("avoids an id whose first mark point id is taken", () => {
    const d = threeParts();
    d.parts[0] = { ...d.parts[0]!, mark_points: [{ ...d.parts[0]!.mark_points[0]!, id: "d-m1" }] };
    expect(addPart(d).parts[3]!.id).toBe("d-2");
  });

  it("keeps at least one part", () => {
    const d = doc();
    d.parts = [part("a", 1, ["a-m1"])];
    expect(removePart(d, 0)).toEqual({ doc: d, dropped: 0 });
  });

  it("moves a part down, relabels and removes references that no longer point to an earlier part", () => {
    const { doc: d, dropped } = movePart(threeParts(), 0, 1);
    expect(d.parts.map((p) => [p.id, p.label])).toEqual([["b", "a"], ["a", "b"], ["c", "c"]]);
    // b (now first) pointed at a (now later): 2 references. a (now second) has none. c keeps b and a, both earlier.
    expect(d.parts[0]!.ecf_from).toEqual([]);
    expect(d.parts[0]!.depends_on).toEqual([]);
    expect(d.parts[2]!.ecf_from).toEqual(["b", "a"]);
    expect(dropped).toBe(2);
    expect(referenceNotice("Moving", "(a)", dropped)).toBe("Moving part (a): 2 references to a part that no longer applies were removed.");
    expect(referenceNotice("Moving", "(a)", 1)).toBe("Moving part (a): 1 reference to a part that no longer applies was removed.");
    expect(referenceNotice("Moving", "(a)", 0)).toBe("");
  });

  it("moves a part up and ignores moves past the ends", () => {
    const base = threeParts();
    const up = movePart(base, 2, -1);
    expect(up.doc.parts.map((p) => p.id)).toEqual(["a", "c", "b"]);
    expect(up.doc.parts.map((p) => p.label)).toEqual(["a", "b", "c"]);
    expect(movePart(base, 0, -1).doc).toBe(base);
    expect(movePart(base, 2, 1).doc).toBe(base);
  });

  it("moves a lettered part together with its sub-parts and keeps the sub-part order", () => {
    const d = doc();
    d.parts = [part("a", 1, ["a-m1"]), part("b.i", 1, ["b.i-m1"]), part("b.ii", 1, ["b.ii-m1"]), part("c", 1, ["c-m1"])];
    expect(topLevelPartCount(d)).toBe(3);
    const moved = movePart(d, 1, -1).doc; // any part of group b
    expect(moved.parts.map((p) => p.id)).toEqual(["b.i", "b.ii", "a", "c"]);
    expect(moved.parts.map((p) => p.label)).toEqual(["a.i", "a.ii", "b", "c"]);
    const removed = removePart(d, 2).doc;
    expect(removed.parts.map((p) => [p.id, p.label])).toEqual([["a", "a"], ["c", "b"]]);
  });

  it("does not mutate its input", () => {
    const d = threeParts();
    const before = JSON.stringify(d);
    addPart(d);
    removePart(d, 0);
    movePart(d, 0, 1);
    expect(JSON.stringify(d)).toBe(before);
  });
});

describe("error locations", () => {
  const d = (): QuestionDocument => threeParts();

  it("maps a path inside a text field to that field", () => {
    expect(matchField("document.parts.0.mark_points.0.content.content.0.content.2.attrs.latex", d())).toEqual({
      field: "parts[0].mark_points[0].content",
      label: "Part (a), mark point 1",
    });
    expect(matchField("document.stem.content.0.content.1.text", d())).toEqual({ field: "stem", label: "Stem" });
    expect(matchField("document.mcq.options.2.rationale.content.0", { ...d(), mcq: { options: [{}, {}, {}] } } as unknown as QuestionDocument)?.field).toBe("mcq.options[2].rationale");
  });

  it("maps paths of items without an editor to the item's text field", () => {
    expect(matchField("document.parts.1.mark_points.0.solution_step", d())?.field).toBe("parts[1].mark_points[0].content");
    expect(matchField("document.parts.1.notes.0.mark_point_id", d())?.field).toBe("parts[1].notes[0].mark_point_id");
    expect(matchField("document.parts.1.depends_on", d())?.field).toBe("parts[1].ecf_from");
    expect(matchField("document.secondary_syllabus_nodes.0", d())?.field).toBe("primary_syllabus_node");
  });

  it("returns null for the whole document and for unknown paths", () => {
    expect(matchField("document", d())).toBeNull();
    expect(matchField("document.schema_version", d())).toBeNull();
    expect(matchField("document.parts.1.syllabus_node", d())).toBeNull();
  });

  it("uses the location before the message and keeps the message shapes as a fallback", () => {
    const found = serverProblems(
      [
        { code: "invalid_document", message: "math `x`: does not render: bad", location: "document.parts.2.body.content.0.content.1.attrs.latex" },
        { code: "invalid_document", message: "Content must be written in English; found non-English letters", location: "document.stem.content.0.content.0.text" },
        { code: "invalid_document", message: "document is too large", location: null },
        { code: "invalid_document", message: "part b: unknown command term 'zz'" },
        { code: "invalid_document", message: "odd", location: "document.parts.1.syllabus_node" },
      ],
      d(),
    );
    expect(found).toEqual([
      { field: "parts[2].body", label: "Part (c) body", message: "math `x`: does not render: bad" },
      { field: "stem", label: "Stem", message: "Content must be written in English" },
      { field: null, label: null, message: "document is too large" },
      { field: "parts[1].command_term", label: "Part (b) command term", message: "part b: unknown command term 'zz'" },
      { field: null, label: null, message: "odd" },
    ]);
  });

  it("lists one problem per place when a rule touches several places", () => {
    const found = serverProblems(
      [
        { code: "invalid_document", message: "bad", location: "document.parts.0.body.content.0" },
        { code: "invalid_document", message: "bad", location: "document.parts.1.body.content.0" },
        { code: "invalid_document", message: "bad", location: "document.parts.1.body.content.3" },
      ],
      d(),
    );
    expect(found.map((p) => p.field)).toEqual(["parts[0].body", "parts[1].body"]);
  });
});

describe("new question", () => {
  it("starts a multiple-choice question with four empty options and one mark", () => {
    const d = newDocument("mcq");
    expect(d.mcq!.options.map((o) => o.key)).toEqual(["A", "B", "C", "D"]);
    expect(d.parts).toEqual([]);
    expect(d.total_marks).toBe(1);
    expect(d.mcq!.option_layout).toBe("single_value");
  });

  it("starts a structured question with one part (a) and one mark point", () => {
    const d = newDocument("short_structured", { primary_syllabus_node: "N.1" });
    expect(d.mcq).toBeNull();
    expect(d.parts.map((p) => p.label)).toEqual(["a"]);
    expect(d.parts[0]!.mark_points).toHaveLength(1);
    expect(d.parts[0]!.syllabus_node).toBe("N.1");
    expect(d.total_marks).toBe(1);
  });

  it("keeps the header and stem when the class changes", () => {
    const d = { ...newDocument("mcq"), levels: ["sl" as const], stem: text("Kept"), outcome: "o" };
    const next = setQuestionClass(d, "long_structured");
    expect(next.levels).toEqual(["sl"]);
    expect(next.outcome).toBe("o");
    expect(next.stem).toEqual(text("Kept"));
    expect(next.parts).toHaveLength(1);
    expect(next.mcq).toBeNull();
  });

  it("rebuilds the options for the layout the writer picks and keeps the first cells", () => {
    const d = newDocument("mcq");
    d.mcq!.options[0]!.cells[0] = text("Kept cell");
    const table = setMcqShape(d, "word_phrase", "two_column_table");
    expect(table.mcq!.column_headers).toHaveLength(2);
    expect(table.mcq!.options.every((o) => o.cells.length === 2)).toBe(true);
    expect(table.mcq!.options[0]!.cells[0]).toEqual(text("Kept cell"));
    const roman = setMcqShape(table, "statement", "roman_statements");
    expect(roman.mcq!.statements.length).toBeGreaterThanOrEqual(2);
    expect(roman.mcq!.column_headers).toEqual([]);
    expect(roman.mcq!.option_kind).toBe("statement");
  });

  it("makes every part follow the main node and checks the header against the syllabus", () => {
    const d = setPrimaryNode(newDocument("short_structured"), "N.2");
    expect(d.parts[0]!.syllabus_node).toBe("N.2");
    expect(createProblems(d, { sections: ["s1"], leaves: ["N.2"] }).map((p) => p.field)).toEqual(["exam_section"]);
    expect(createProblems({ ...d, exam_section: "s1" }, { sections: ["s1"], leaves: ["N.1"] }).map((p) => p.field)).toEqual(["primary_syllabus_node"]);
    expect(createProblems({ ...d, exam_section: "s1" }, { sections: ["s1"], leaves: ["N.2"] })).toEqual([]);
  });
});
