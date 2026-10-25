/** Wire contract documented in the repository's API.md. */

export const EMOTION_LABELS = [
  "angry",
  "calm",
  "disgust",
  "fearful",
  "happy",
  "sad",
  "surprised",
] as const;

export type EmotionLabel = (typeof EMOTION_LABELS)[number];
export type AttentionCategory = "Routine" | "Elevated" | "High";
export type Priority = "P1" | "P2" | "P3" | "P4";

export interface HealthResponse {
  status: "ok";
  model_id: string;
  model_revision: string;
  sample_rate: 16000;
}

export interface Score {
  label: EmotionLabel;
  score: number;
}

export interface AnalysisEvent {
  type: "analysis";
  session_id: string;
  elapsed: number;
  scores: Score[];
  indicators: {
    distress_indicator: number;
    nervousness_indicator: number;
    [key: string]: number;
  };
  quality_flags: string[];
  low_confidence: boolean;
  category: AttentionCategory;
  priority: Priority;
  urgency_score: number;
  priority_reasons: string[];
  priority_guidance: string;
}

export interface AudioSessionStartedEvent {
  type: "session_started";
  session_id: string;
  asr_enabled: boolean;
}

export interface AttentionTransitionEvent {
  type: "attention_transition";
  session_id: string;
  time: number;
  from: AttentionCategory;
  to: AttentionCategory;
}

export interface AnalysisErrorEvent {
  type: "analysis_error";
  session_id: string;
  message: string;
}

export interface TranscriptPartialEvent {
  type: "transcript_partial";
  session_id: string;
  text: string;
  language: string | null;
  keyword_hits: string[];
  status: "partial" | "error";
  message: string | null;
}

export type ServerEvent = AnalysisEvent | AttentionTransitionEvent | AnalysisErrorEvent | TranscriptPartialEvent;

/** WS /ws/audio uses binary little-endian signed PCM16 mono frames at 16 kHz. */
export type AudioWebSocketFrame = ArrayBuffer;

export function isServerEvent(value: unknown): value is ServerEvent {
  if (typeof value !== "object" || value === null || !("type" in value)) {
    return false;
  }

  const event = value as Record<string, unknown>;
  if (typeof event.session_id !== "string") return false;

  switch (event.type) {
    case "analysis": {
      const scores = event.scores;
      const indicators = event.indicators;
      return (
        isFiniteNonNegative(event.elapsed) &&
        Array.isArray(scores) &&
        scores.length === EMOTION_LABELS.length &&
        scores.every(isScore) &&
        scores.every((score, index) => score.label === EMOTION_LABELS[index]) &&
        isIndicators(indicators) &&
        Array.isArray(event.quality_flags) &&
        event.quality_flags.every((flag) => typeof flag === "string") &&
        typeof event.low_confidence === "boolean" &&
        isAttentionCategory(event.category) &&
        isPriority(event.priority) &&
        typeof event.urgency_score === "number" &&
        Number.isInteger(event.urgency_score) &&
        event.urgency_score >= 1 &&
        event.urgency_score <= 10 &&
        Array.isArray(event.priority_reasons) &&
        event.priority_reasons.every((reason) => typeof reason === "string") &&
        typeof event.priority_guidance === "string"
      );
    }
    case "attention_transition":
      return (
        isFiniteNonNegative(event.time) &&
        isAttentionCategory(event.from) &&
        isAttentionCategory(event.to)
      );
    case "analysis_error":
      return typeof event.message === "string";
    case "transcript_partial":
      return (
        typeof event.text === "string" &&
        (event.language === null || typeof event.language === "string") &&
        Array.isArray(event.keyword_hits) &&
        event.keyword_hits.every((hit) => typeof hit === "string") &&
        (event.status === "partial" || event.status === "error") &&
        (event.message === null || typeof event.message === "string")
      );
    default:
      return false;
  }
}

function isAttentionCategory(value: unknown): value is AttentionCategory {
  return value === "Routine" || value === "Elevated" || value === "High";
}

function isPriority(value: unknown): value is Priority {
  return value === "P1" || value === "P2" || value === "P3" || value === "P4";
}

function isScore(value: unknown): value is Score {
  if (typeof value !== "object" || value === null || !("label" in value)) {
    return false;
  }
  const score = value as Record<string, unknown>;
  return (
    isEmotionLabel(score.label) &&
    typeof score.score === "number" &&
    Number.isFinite(score.score) &&
    score.score >= 0 &&
    score.score <= 1
  );
}

function isEmotionLabel(value: unknown): value is EmotionLabel {
  return EMOTION_LABELS.some((label) => label === value);
}

function isIndicators(value: unknown): value is AnalysisEvent["indicators"] {
  if (typeof value !== "object" || value === null) return false;
  const indicators = value as Record<string, unknown>;
  return (
    typeof indicators.distress_indicator === "number" &&
    Number.isFinite(indicators.distress_indicator) &&
    typeof indicators.nervousness_indicator === "number" &&
    Number.isFinite(indicators.nervousness_indicator) &&
    Object.values(indicators).every(
      (indicator) => typeof indicator === "number" && Number.isFinite(indicator),
    )
  );
}

function isFiniteNonNegative(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= 0;
}
