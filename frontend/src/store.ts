import { create } from "zustand";

import type {
  AnalysisErrorEvent,
  AnalysisEvent,
  AttentionTransitionEvent,
  ServerEvent,
  TranscriptPartialEvent,
} from "./types";

interface AnalysisState {
  latest: AnalysisEvent | null;
  history: AnalysisEvent[];
  transitions: AttentionTransitionEvent[];
  error: AnalysisErrorEvent | null;
  transcript: TranscriptPartialEvent | null;
  receiveEvent: (event: ServerEvent) => void;
  reset: () => void;
}

const emptyState = {
  latest: null,
  history: [] as AnalysisEvent[],
  transitions: [] as AttentionTransitionEvent[],
  error: null,
  transcript: null as TranscriptPartialEvent | null,
};

export const useAnalysisStore = create<AnalysisState>((set) => ({
  ...emptyState,
  receiveEvent: (event) => {
    switch (event.type) {
      case "analysis":
        set((state) => ({
          latest: event,
          history: [
            ...(state.latest?.session_id === event.session_id ? state.history : []),
            event,
          ].slice(-60),
          error: null,
        }));
        break;
      case "attention_transition":
        set((state) => ({ transitions: [...state.transitions, event] }));
        break;
      case "analysis_error":
        set({ error: event });
        break;
      case "transcript_partial":
        set({ transcript: event });
        break;
    }
  },
  reset: () => set(emptyState),
}));
