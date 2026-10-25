# Data Dictionary

Source of truth: [BRAIN.md](BRAIN.md). This describes fields emitted by the current implementation; it is not a guarantee of a stable external API.

## Live insight

| Field | Meaning |
|---|---|
| `elapsed` | Seconds since the current pipeline started, measured from a monotonic clock. |
| `scores` | List of `{label, score}` objects for the seven configured raw model labels. Scores are validated finite values in `[0, 1]` whose sum is checked against the configured tolerance. |
| `indicators.distress_indicator` | Smoothed derived distress indicator; not a model class. |
| `indicators.nervousness_indicator` | Smoothed derived nervousness indicator; not a model class. |
| `quality_flags` | Screening flags for this analyzed window. |
| `low_confidence` | Whether a low-quality flag occurred in the recent quality window. |
| `category` | Current indicative attention category: `Routine`, `Elevated`, or `High`. |

## Audio screening measurements and flags

`screen_window()` returns flags plus acoustic metrics. Metrics include `rms_energy`, `peak_amplitude`, `spectral_flatness`, `dominant_peak_fraction`, `rms_cv`, and `vad_activity_ratio`. Flags include low RMS energy, clipping, low VAD activity, suspected stationary noise, suspected tonal audio, and VAD-unavailable status where applicable. These heuristics do not establish that speech is intelligible or representative.

## Pipeline snapshot

| Field | Meaning |
|---|---|
| `latest` | Most recent live insight, or null before the first analyzed window. |
| `insights` | In-memory sequence of analyzed insights, bounded by the configured maximum. |
| `events` | In-memory attention-category transitions with elapsed seconds and `from`/`to` labels. |
| `error` | Current analysis error string or null. |
| `recording` | Whether the pipeline stop event is unset. |
| `started_at` | UTC ISO-8601 start time or null. |
| `duration_seconds` | Elapsed duration measured with a monotonic clock. |

## Saved summary

The current summary contains `application`, `created_at`, `started_at`, `duration_seconds`, `analyzed_windows`, `final_attention_category`, `peak_distress_indicator`, `peak_nervousness_indicator`, `quality_flags`, and `model` (`id`, `revision`). It contains no audio and no per-window series. Indicator values and attention categories are provisional and advisory.

## Planned fields

**Planned:** A versioned, externally stable API schema, call/session identifiers, authentication principals, and durable audit records. These fields do not exist in the current summary contract.
