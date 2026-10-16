import type { components } from "@qlab/api-client";

type S = components["schemas"];

// Generated types that the api-client does not re-export as aliases.
export type LearnerPart = S["LearnerPart"];
export type Mark = S["Mark"];
export type Paragraph = S["Paragraph"];
export type DocBlock = S["Doc"]["content"][number];
export type InlineNode = Paragraph["content"][number];
export type OptionKey = "A" | "B" | "C" | "D";
export type OptionLayout = S["OptionLayout"];
export type StimulusKind = S["StimulusKind"];
export type MarkPointOut = S["MarkPointOut"];
export type NoteOut = S["NoteOut"];
export type Level = S["Level"];

/** What the figure placeholder needs to know about a stimulus. */
export interface StimulusInfo {
  id: string;
  kind: StimulusKind;
  /** Staff-only. Never set for learner content. */
  description?: string;
}
