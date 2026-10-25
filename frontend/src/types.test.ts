import { describe, expect, it } from "vitest";

import { isServerEvent } from "./types";

const analysis = {
  type: "analysis",
  session_id: "00000000-0000-4000-8000-000000000001",
  elapsed: 3,
  scores: [
    { label: "angry", score: 0.05 },
    { label: "calm", score: 0.1 },
    { label: "disgust", score: 0.05 },
    { label: "fearful", score: 0.5 },
    { label: "happy", score: 0.05 },
    { label: "sad", score: 0.15 },
    { label: "surprised", score: 0.1 },
  ],
  indicators: {
    distress_indicator: 0.4,
    nervousness_indicator: 0.3,
    fear: 0.5,
    anger: 0.05,
  },
  quality_flags: [],
  low_confidence: false,
  category: "Elevated",
  priority: "P3",
  urgency_score: 5,
  priority_reasons: ["Distress indicator meets provisional P3 threshold."],
  priority_guidance: "Advisory: Consider reviewing the conversation context and following standard intake steps.",
};

describe("server event contract", () => {
  it("accepts a complete analysis event in model label order", () => {
    expect(isServerEvent(analysis)).toBe(true);
  });

  it("rejects a partial or misordered model score vector", () => {
    expect(isServerEvent({ ...analysis, scores: analysis.scores.slice(1) })).toBe(
      false,
    );
    expect(
      isServerEvent({
        ...analysis,
        scores: [analysis.scores[1], analysis.scores[0], ...analysis.scores.slice(2)],
      }),
    ).toBe(false);
  });

  it("accepts attention transitions and analysis errors", () => {
    expect(
      isServerEvent({
        type: "attention_transition",
        session_id: analysis.session_id,
        time: 12,
        from: "Routine",
        to: "Elevated",
      }),
    ).toBe(true);
    expect(
      isServerEvent({
        type: "analysis_error",
        session_id: analysis.session_id,
        message: "Analysis disabled: model unavailable",
      }),
    ).toBe(true);
  });

  it("accepts ephemeral partial transcript events", () => {
    expect(
      isServerEvent({
        type: "transcript_partial",
        session_id: analysis.session_id,
        text: "Caller says they were threatened.",
        language: "en",
        keyword_hits: ["threatened"],
        status: "partial",
        message: null,
      }),
    ).toBe(true);
  });
});
