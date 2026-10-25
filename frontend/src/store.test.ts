import { beforeEach, describe, expect, it } from "vitest";

import { useAnalysisStore } from "./store";

describe("analysis event store", () => {
  beforeEach(() => useAnalysisStore.getState().reset());

  it("stores analysis snapshots without changing their advisory categories", () => {
    const analysis = {
      type: "analysis" as const,
      session_id: "session-1",
      elapsed: 4.5,
      scores: [{ label: "fearful" as const, score: 0.7 }],
      indicators: { distress_indicator: 0.4, nervousness_indicator: 0.6 },
      quality_flags: ["LOW_RMS_ENERGY"],
      low_confidence: true,
      category: "Elevated" as const,
      priority: "P3" as const,
      urgency_score: 5,
      priority_reasons: ["Provisional P3 threshold met."],
      priority_guidance: "Advisory: Consider reviewing the conversation context and following standard intake steps.",
    };

    useAnalysisStore.getState().receiveEvent(analysis);

    expect(useAnalysisStore.getState().latest).toEqual(analysis);
    expect(useAnalysisStore.getState().error).toBeNull();
  });

  it("retains category transitions and clears state on reset", () => {
    const transition = {
      type: "attention_transition" as const,
      session_id: "session-1",
      time: 8,
      from: "Routine" as const,
      to: "Elevated" as const,
    };

    useAnalysisStore.getState().receiveEvent(transition);
    expect(useAnalysisStore.getState().transitions).toEqual([transition]);

    useAnalysisStore.getState().reset();
    expect(useAnalysisStore.getState().transitions).toEqual([]);
  });

  it("keeps transcript snapshots in memory and clears them with the session", () => {
    const transcript = {
      type: "transcript_partial" as const,
      session_id: "session-1",
      text: "Caller says they were threatened.",
      language: "en",
      keyword_hits: ["threatened"],
      status: "partial" as const,
      message: null,
    };
    useAnalysisStore.getState().receiveEvent(transcript);
    expect(useAnalysisStore.getState().transcript).toEqual(transcript);

    useAnalysisStore.getState().reset();
    expect(useAnalysisStore.getState().transcript).toBeNull();
  });
});
