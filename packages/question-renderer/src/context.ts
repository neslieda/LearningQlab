import { createContext } from "react";
import type { StimulusInfo } from "./types";

export interface StimuliContextValue {
  stimuli: ReadonlyMap<string, StimulusInfo>;
  showDescription: boolean;
}

export const EMPTY_STIMULI: StimuliContextValue = { stimuli: new Map(), showDescription: false };

/** Lets a `figure` node (which carries only a stimulus id) find its stimulus. */
export const StimuliContext = createContext<StimuliContextValue>(EMPTY_STIMULI);
