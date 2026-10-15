// Slice 7b section 5 (test 7) and section 4 (error mapping): pure operations on the question document.
// All data is synthetic.
import { describe, expect, it } from "vitest";
import type { Doc, QuestionDocument } from "@qlab/api-client";
import {
  addMarkPoint,
  addNote,
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
