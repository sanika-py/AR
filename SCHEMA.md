# Data Schemas

Source of truth: [BRAIN.md](BRAIN.md). Current shapes below are observed in the Streamlit pipeline and summary builder; they are not versioned contracts.

## Current live insight shape

```json
{
  "elapsed": 3.2,
  "scores": [
    {"label": "angry", "score": 0.1},
    {"label": "calm", "score": 0.2},
    {"label": "disgust", "score": 0.1},
    {"label": "fearful", "score": 0.2},
    {"label": "happy", "score": 0.1},
    {"label": "sad", "score": 0.2},
    {"label": "surprised", "score": 0.1}
  ],
  "indicators": {
    "distress_indicator": 0.0,
    "nervousness_indicator": 0.0
  },
  "quality_flags": [],
  "low_confidence": false,
  "category": "Routine"
}
```

The numerical values above only illustrate field shape; they are not measurements, examples of expected model behavior, or thresholds.

## Current saved summary shape

```json
{
  "application": "AwazRakshak",
  "created_at": "2000-01-01T00:00:00+00:00",
  "started_at": "2000-01-01T00:00:00+00:00",
  "duration_seconds": 0.0,
  "analyzed_windows": 0,
  "final_attention_category": "No analysis available",
  "peak_distress_indicator": 0.0,
  "peak_nervousness_indicator": 0.0,
  "quality_flags": [],
  "model": {
    "id": "Dpngtm/wav2vec2-emotion-recognition",
    "revision": "033a5751a5bbe5b0b67c2c71e6102c38de35a346"
  }
}
```

The timestamp values and numeric values are illustrative examples of valid field shapes, not actual call data or measured results. Summary numeric fields are rounded by the current builder. No raw audio or full live history is included.

## Planned schema evolution

**Planned:** Add an explicit schema version and validated API DTOs before a FastAPI service is introduced. Compatibility, required/optional fields, error envelope, session identifiers, and any persistence schema remain to be designed. Do not treat the current Python dictionaries as a stable public API.
