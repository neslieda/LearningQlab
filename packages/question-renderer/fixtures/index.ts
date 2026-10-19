// Synthetic sample set for the renderer (docs/slices/M1G-6-GOSTERIM.md section 5).
// Invented, physics-flavoured content. Nothing here is taken from any exam paper (CLAUDE.md rule 14).
import type { components } from "@qlab/api-client";
import { br, bullets, doc, fig, line, m, mb, numbered, p, q, t, table, type Doc } from "./build";

type S = components["schemas"];
type LearnerQuestion = S["LearnerQuestion"];
type QuestionDocument = S["QuestionDocument"];
type MarkPointOut = S["MarkPointOut"];
type NoteOut = S["NoteOut"];

export type Fixture =
  | { id: string; title: string; kind: "learner_question"; data: LearnerQuestion }
  | { id: string; title: string; kind: "doc"; data: Doc }
  | {
      id: string;
      title: string;
      kind: "markscheme";
      data: { markPoints: MarkPointOut[]; notes: NoteOut[]; marks: number; marksCapped: boolean };
    }
  | { id: string; title: string; kind: "staff_question"; data: { document: QuestionDocument; showAnswers: boolean } }
  | { id: string; title: string; kind: "mcq_result"; data: { result: S["McqResult"]; question: LearnerQuestion } };

const fxTopic = { code: "FX.1", title: "Invented topic" };
const mcqBase = { topic: fxTopic, answered: false, exam_section: "paper_1a", levels: ["sl", "hl"] as const, parts: [], total_marks: 1 };

// 1. MCQ, single_value, inline maths and quantities in the options
const mcqSingleValue: LearnerQuestion = {
  ...mcqBase,
  id: "fx-q-mcq-single",
  version_id: "fx-v-mcq-single",
  levels: ["sl", "hl"],
  question_class: "mcq",
  stem: line(
    "A cart of mass ",
    q("0.80", "kg"),
    " moves along a level track. A constant resultant force of ",
    q("2.0", "N"),
    " acts on it for ",
    q("3.0", "s"),
    ". What is the magnitude of the impulse on the cart?",
  ),
  stimuli: [],
  mcq: {
    option_layout: "single_value",
    column_headers: [],
    statements: [],
    options: [
      { key: "A", cells: [line(m("\\frac{2.0}{3.0}"), " ", q("0.67", "N s"))] },
      { key: "B", cells: [line(q("1.5", "N s"))] },
      { key: "C", cells: [line(m("2.0 \\times 3.0"), " = ", q("6.0", "N s"))] },
      { key: "D", cells: [line(m("\\frac{2.0 \\times 3.0}{0.80}"), " ", q("7.5", "N s"))] },
    ],
  },
};

// 2. MCQ, two_column_table
const mcqTable: LearnerQuestion = {
  ...mcqBase,
  id: "fx-q-mcq-table",
  version_id: "fx-v-mcq-table",
  levels: ["sl", "hl"],
  question_class: "mcq",
  stem: line("A progressive wave travels along a stretched string. Which row describes the wave correctly?"),
  stimuli: [],
  mcq: {
    option_layout: "two_column_table",
    column_headers: [line("Particle motion"), line("Energy transfer")],
    statements: [],
    options: [
      { key: "A", cells: [line("Parallel to the wave direction"), line("Along the string")] },
      { key: "B", cells: [line("Perpendicular to the wave direction"), line("Along the string")] },
      { key: "C", cells: [line("Parallel to the wave direction"), line("None")] },
      { key: "D", cells: [line("Perpendicular to the wave direction"), line("None")] },
    ],
  },
};

// 3. MCQ, roman_statements
const mcqRoman: LearnerQuestion = {
  ...mcqBase,
  id: "fx-q-mcq-roman",
  version_id: "fx-v-mcq-roman",
  levels: ["hl"],
  question_class: "mcq",
  stem: line("Which statements about a sealed sample of an ideal gas are correct when its temperature rises at constant volume?"),
  stimuli: [],
  mcq: {
    option_layout: "roman_statements",
    column_headers: [],
    statements: [
      line("The mean kinetic energy of the molecules increases."),
      line("The pressure ", m("p"), " of the gas increases."),
      line("The number of molecules ", m("N"), " increases."),
    ],
    options: [
      { key: "A", cells: [line("I and II only")] },
      { key: "B", cells: [line("I and III only")] },
      { key: "C", cells: [line("II and III only")] },
      { key: "D", cells: [line("I, II and III")] },
    ],
  },
};

// 4. MCQ, figure_options
const mcqFigures: LearnerQuestion = {
  ...mcqBase,
  id: "fx-q-mcq-figures",
  version_id: "fx-v-mcq-figures",
  levels: ["sl", "hl"],
  question_class: "mcq",
  stem: line("A ball is released from rest and falls freely. Which graph shows how its speed varies with time?"),
  stimuli: [
    { id: "opt-a", kind: "graph" },
    { id: "opt-b", kind: "graph" },
    { id: "opt-c", kind: "graph" },
    { id: "opt-d", kind: "graph" },
  ],
  mcq: {
    option_layout: "figure_options",
    column_headers: [],
    statements: [],
    options: [
      { key: "A", cells: [doc(fig("opt-a"))] },
      { key: "B", cells: [doc(fig("opt-b"))] },
      { key: "C", cells: [doc(fig("opt-c"))] },
      { key: "D", cells: [doc(fig("opt-d"))] },
    ],
  },
};

// 5 and 9. A structured question, written as the full document; the learner view is derived from it.
const structuredDocument: QuestionDocument = {
  schema_version: "1.0",
  question_class: "long_structured",
  exam_section: "paper_2",
  levels: ["sl", "hl"],
  calculator: true,
  language: "en",
  primary_syllabus_node: "demo.mechanics",
  secondary_syllabus_nodes: [],
  total_marks: 9,
  stem: doc(
    p(
      "A student pulls a ",
      t("small", "italic"),
      " trolley of mass ",
      m("M"),
      " up a ramp using a ",
      t("light", "bold"),
      " string. The ramp makes an angle ",
      m("\\theta"),
      " with the horizontal. The text ",
      t("$not maths$"),
      " and ",
      t("<img src=x onerror=alert(1)>"),
      " are shown as written.",
    ),
    fig("s-ramp"),
    p("Data for the trolley:"),
    bullets(
      p("mass ", m("M"), " = ", q("1.2", "kg")),
      p("angle ", m("\\theta"), " = ", q("20", "°")),
      p("string tension ", m("T"), " = ", q("6.5", "N")),
    ),
    p("The ramp is rough.", br(), "Take ", m("g"), " = ", q("9.81", "m/s^2"), "."),
  ),
  stimuli: [
    {
      id: "s-ramp",
      kind: "schematic_diagram",
      use: "read_values",
      description: "A trolley on an inclined plane, pulled up the slope by a string parallel to the slope. The angle is marked at the base.",
      alt_text: null,
      asset_id: null,
    },
  ],
  parts: [
    {
      id: "pa",
      label: "a",
      lead_in: null,
      body: doc(p("State what is meant by the ", t("resultant", "bold"), " force on the trolley.")),
      marks: 2,
      marks_capped: false,
      show_that: false,
      command_term: "State",
      answer_type: "word_phrase",
      assessment_objective: 1,
      level_content: "sl_core",
      syllabus_node: "demo.mechanics",
      stimulus_refs: [],
      depends_on: [],
      ecf_from: [],
      mark_points: [
        { id: "pa-1", kind: "statement", content: line("the vector ", t("sum", "essential"), " of all forces acting on the trolley") },
        { id: "pa-2", kind: "statement", content: line("equal to the rate of change of ", t("momentum", "optional")) },
      ],
      notes: [{ kind: "owtte", content: line("any equivalent wording") }],
    },
    {
      id: "pbi",
      label: "b.i",
      lead_in: line("The trolley now moves up the ramp at a constant speed."),
      body: doc(
        p("Calculate the component of the weight of the trolley parallel to the ramp."),
        mb("W_{\\parallel} = M g \\sin \\theta"),
      ),
      marks: 2,
      marks_capped: false,
      show_that: false,
      command_term: "Calculate",
      answer_type: "numeric_with_unit",
      assessment_objective: 2,
      level_content: "sl_core",
      syllabus_node: "demo.mechanics",
      stimulus_refs: ["s-ramp"],
      depends_on: [],
      ecf_from: [],
      mark_points: [
        { id: "pbi-1", kind: "method", content: line(m("1.2 \\times 9.81 \\times \\sin 20")) },
        { id: "pbi-2", kind: "answer", content: line(q("4.0", "N")), accept_range: { minimum: "3.9", maximum: "4.1", unit: "N" } },
      ],
      notes: [],
    },
    {
      id: "pbii",
      label: "b.ii",
      lead_in: null,
      body: doc(
        p("Determine the friction force on the trolley, and state its direction."),
        numbered(p("Give your answer to ", t("two", "bold"), " significant figures."), p("Show your working.")),
      ),
      marks: 3,
      marks_capped: false,
      show_that: false,
      command_term: "Determine",
      answer_type: "numeric_with_unit",
      assessment_objective: 3,
      level_content: "sl_core",
      syllabus_node: "demo.mechanics",
      stimulus_refs: [],
      depends_on: ["pbi"],
      ecf_from: ["pbi"],
      mark_points: [
        { id: "pbii-1", kind: "method", content: line(m("T = W_{\\parallel} + F")) },
        { id: "pbii-2", kind: "answer", content: line(m("F = 6.5 - 4.0"), " = ", q("2.5", "N")) },
        { id: "pbii-3", kind: "statement", content: line("down the slope, opposing the motion") },
      ],
      notes: [{ kind: "ecf", content: line("allow the value found in (b)(i)"), mark_point_id: "pbii-2" }],
    },
    {
      id: "pc",
      label: "c",
      lead_in: null,
      body: doc(p("Explain why the speed of the trolley stays constant.")),
      marks: 2,
      marks_capped: false,
      show_that: false,
      command_term: "Explain",
      answer_type: "explanation",
      assessment_objective: 2,
      level_content: "sl_core",
      syllabus_node: "demo.mechanics",
      stimulus_refs: [],
      depends_on: [],
      ecf_from: [],
      mark_points: [
        { id: "pc-1", kind: "statement", content: line("the resultant force is zero") },
        { id: "pc-2", kind: "statement", content: line("so there is no acceleration") },
      ],
      notes: [],
    },
  ],
};

function toLearner(document: QuestionDocument, id: string): LearnerQuestion {
  return {
    id,
    topic: fxTopic,
    answered: false,
    version_id: `${id}-v1`,
    exam_section: document.exam_section,
    levels: document.levels,
    question_class: document.question_class,
    total_marks: document.total_marks,
    stem: document.stem,
    stimuli: document.stimuli.map((s) => ({ id: s.id, kind: s.kind })),
    mcq: null,
    parts: document.parts.map((part) => ({
      id: part.id,
      label: part.label,
      lead_in: part.lead_in ?? null,
      body: part.body,
      marks: part.marks,
      command_term: part.command_term ?? null,
      stimulus_refs: part.stimulus_refs,
    })),
  };
}

// 6. Data-based: a wide table (scrolls inside its box at 375 px), colspan and rowspan, a quantity with uncertainty
const dataBased: LearnerQuestion = {
  id: "fx-q-data",
  topic: fxTopic,
  answered: false,
  version_id: "fx-v-data",
  exam_section: "paper_2",
  levels: ["sl", "hl"],
  question_class: "data_based",
  total_marks: 3,
  stem: doc(
    p("A student measures the period of a pendulum for different lengths. The measurements are shown."),
    table(
      [
        { header: true, rowspan: 2, content: "Trial" },
        { header: true, colspan: 3, content: "Short pendulum" },
        { header: true, colspan: 3, content: "Long pendulum" },
        { header: true, rowspan: 2, content: "Comment on the reading" },
      ],
      [
        { header: true, content: p("Length ", m("l"), " / m") },
        { header: true, content: p("Time for 10 swings / s") },
        { header: true, content: p("Period ", m("T"), " / s") },
        { header: true, content: p("Length ", m("l"), " / m") },
        { header: true, content: p("Time for 10 swings / s") },
        { header: true, content: p("Period ", m("T"), " / s") },
      ],
      [
        { header: true, content: "1" },
        { content: "0.250" },
        { content: "10.1" },
        { content: "1.01" },
        { content: "1.000" },
        { content: "20.0" },
        { content: "2.00" },
        { content: "The long pendulum was released from a larger angle than the short one." },
      ],
      [
        { header: true, content: "2" },
        { content: "0.250" },
        { content: "10.0" },
        { content: "1.00" },
        { content: "1.000" },
        { content: "20.1" },
        { content: "2.01" },
        { content: "Consistent with trial 1." },
      ],
    ),
    p("The length of the long pendulum is ", q("1.000", "m", "0.002"), "."),
  ),
  stimuli: [],
  mcq: null,
  parts: [
    {
      id: "pd1",
      label: "a",
      lead_in: null,
      body: line("Calculate the percentage uncertainty in the length of the long pendulum."),
      marks: 1,
      command_term: "Calculate",
      stimulus_refs: [],
    },
    {
      id: "pd2",
      label: "b",
      lead_in: null,
      body: line("Determine the mean period of the long pendulum, with its uncertainty, as ", m("T = T_0 \\pm \\Delta T"), "."),
      marks: 2,
      command_term: "Determine",
      stimulus_refs: [],
    },
  ],
};

// 7. Long display maths, matrix and aligned
const longTerms = Array.from({ length: 9 }, (_, i) => `\\frac{1}{2} m_{${i + 1}} v_{${i + 1}}^2`).join(" + ");
const mathDoc: Doc = doc(
  p("A long display equation scrolls inside its own box:"),
  mb(`E_{\\mathrm{k}} = ${longTerms}`),
  p("A set of aligned equations:"),
  mb("\\begin{aligned} v &= u + a t \\\\ s &= u t + \\frac{1}{2} a t^2 \\\\ v^2 &= u^2 + 2 a s \\end{aligned}"),
  p("A matrix equation:"),
  mb("\\begin{pmatrix} 1 & 0 \\\\ 0 & 1 \\end{pmatrix} \\begin{pmatrix} x \\\\ y \\end{pmatrix} = \\begin{pmatrix} x \\\\ y \\end{pmatrix}"),
  p("Assorted symbols: ", m("\\lambda = \\frac{h}{p}"), ", ", m("\\omega = 2 \\pi f"), ", ", m("\\mu_0 \\approx 4 \\pi \\times 10^{-7}"), ", ", m("x \\le y \\ge z"), ", ", m("\\vec{F} = m \\vec{a}"), ", ", m("\\sqrt{\\frac{k}{m}}"), ", ", m("\\left( a + b \\right) \\cdot c \\to d"), "."),
  p("Text that is not maths: $x^2$ and \\frac{1}{2}."),
);

// 8. Mark scheme: alternative group, two routes, accept_range, every note kind, an attached note, a cap
const mkPoint = (
  id: string,
  content: Doc,
  extra: Partial<Pick<MarkPointOut, "alternative_group" | "route" | "accept_range" | "kind">> = {},
): MarkPointOut => ({
  id,
  content,
  kind: extra.kind ?? "statement",
  alternative_group: extra.alternative_group ?? null,
  route: extra.route ?? null,
  accept_range: extra.accept_range ?? null,
});

const markScheme: Fixture = {
  id: "markscheme",
  title: "Mark scheme",
  kind: "markscheme",
  data: {
    marks: 4,
    marksCapped: true,
    markPoints: [
      mkPoint("ms-1", line("the net force is zero"), { alternative_group: "g1" }),
      mkPoint("ms-2", line("the acceleration is zero"), { alternative_group: "g1" }),
      mkPoint("ms-3", line("use of ", m("F = k x")), { route: "r1", kind: "method" }),
      mkPoint("ms-4", line(q("12", "N")), { route: "r1", kind: "answer", accept_range: { minimum: "11.5", maximum: "12.5", unit: "N" } }),
      mkPoint("ms-5", line("use of ", m("W = \\frac{1}{2} k x^2")), { route: "r2", kind: "method" }),
      mkPoint(
        "ms-6",
        line(
          q("12", "N"),
          " ",
          t("applied to the spring at ", "optional"),
          t("extension", "optional", "bold"),
          t(" ", "optional"),
          m("x", "optional"),
          t(" ", "optional"),
          q("0.060", "m", undefined, "optional"),
        ),
        { route: "r2", kind: "answer" },
      ),
    ],
    notes: [
      { kind: "general", content: line("Award marks for the clearly labelled working."), mark_point_id: null },
      { kind: "owtte", content: line("for the first point"), mark_point_id: null },
      { kind: "accept", content: line("any consistent unit prefix"), mark_point_id: null },
      { kind: "do_not_accept", content: line("the word ", t("balanced", "italic"), " on its own"), mark_point_id: null },
      { kind: "cap", content: line("3 marks if no unit is given"), mark_point_id: null },
      { kind: "ecf", content: line("from the extension found earlier"), mark_point_id: "ms-3" },
    ],
  },
};

const staffAnswersOff: Fixture = {
  id: "staff-answers-off",
  title: "Staff view, answers hidden",
  kind: "staff_question",
  data: { document: structuredDocument, showAnswers: false },
};
const staffAnswersOn: Fixture = {
  id: "staff-answers-on",
  title: "Staff view, answers shown",
  kind: "staff_question",
  data: { document: structuredDocument, showAnswers: true },
};

export const fixtures: Fixture[] = [
  { id: "mcq-single-value", title: "MCQ, single value", kind: "learner_question", data: mcqSingleValue },
  { id: "mcq-two-column-table", title: "MCQ, two-column table", kind: "learner_question", data: mcqTable },
  { id: "mcq-roman-statements", title: "MCQ, Roman statements", kind: "learner_question", data: mcqRoman },
  { id: "mcq-figure-options", title: "MCQ, figure options", kind: "learner_question", data: mcqFigures },
  { id: "structured", title: "Structured question", kind: "learner_question", data: toLearner(structuredDocument, "fx-q-structured") },
  { id: "data-based", title: "Data-based question", kind: "learner_question", data: dataBased },
  { id: "math", title: "Long and display maths", kind: "doc", data: mathDoc },
  markScheme,
  staffAnswersOff,
  staffAnswersOn,
  {
    id: "mcq-result",
    title: "MCQ result, correct option marked",
    kind: "mcq_result",
    data: { result: { kind: "mcq", correct: true, correct_key: "C", version_id: "fx-v-mcq-single", response_id: "fx-r-1", explanation: null, rationales: [] }, question: mcqSingleValue },
  },
];
