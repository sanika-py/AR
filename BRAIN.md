# BRAIN — AwazRakshak source of truth

## Purpose

AwazRakshak currently is a single-page Streamlit application for live voice-emotion screening during an authorised call. It shows uncalibrated model scores and provisional derived indicators to support human judgement. It does not decide danger, deception, guilt, or dispatch. The planned destination is a FastAPI backend with a React and Tailwind frontend; that migration has not happened yet.

## Current architecture

- `app.py` provides the Streamlit interface, microphone consent, model availability check, live insight display, and audio-free summary save/download.
- `live.py` keeps a bounded rolling audio buffer in process memory and runs inference on a background thread.
- `engine.py` verifies and loads the pinned local model, screens audio windows, and validates the model score vector.
- `signals.py` calculates provisional indicators, exponential smoothing, attention categories, and two-window hysteresis.
- `config.py` is authoritative for model identity, labels, timing, weights, and provisional thresholds.

## Pinned model

- Hugging Face model ID: `Dpngtm/wav2vec2-emotion-recognition`
- Immutable revision: `033a5751a5bbe5b0b67c2c71e6102c38de35a346`
- Expected raw model labels, in configured index order: `angry`, `calm`, `disgust`, `fearful`, `happy`, `sad`, `surprised`.
- Inference is CPU-only and expects mono audio at 16 kHz. A local cache/snapshot path can be provided with `AWAZRAKSHAK_MODEL_PATH` or through the UI. Existing checks verify the pinned metadata and required model-file hashes. Missing or mismatched files disable analysis. Model files are not downloaded at runtime.

## Live audio and indicators

- The rolling in-memory buffer holds up to 30 seconds. The pipeline analyzes the latest 3-second window every 1.5 seconds.
- Digital-silence windows are skipped. Other screened windows can be scored with quality flags; the UI marks low-confidence audio.
- Derived indicators are not model classes:
  - Distress = `0.50 * fearful + 0.30 * sad + 0.20 * angry`.
  - Nervousness = `0.45 * fearful + 0.35 * surprised + 0.20 * min(rms_cv, 1)`, where `rms_cv` is the window's acoustic RMS coefficient of variation.
- Indicator smoothing uses an EMA alpha of `0.35`.
- Provisional attention bands use thresholds `0.35` (Elevated) and `0.65` (High), with two-window hysteresis. Routine is below the elevated threshold. These are engineering starting points, not validated decision thresholds.

## Privacy stance

Raw audio is processed from browser microphone frames in the app process, held only in the rolling in-memory buffer, and cleared when recording stops. The application does not write raw audio to disk or download model weights. It saves an audio-free JSON call summary under `.awazrakshak-data/summaries/` and offers that summary for download. A hosted deployment would transmit microphone audio from the browser to the host; the current local-processing stance assumes the app is run in a trusted local environment.

## Current limitations

- The product is still Streamlit; the FastAPI + React + Tailwind migration is pending.
- Model outputs are uncalibrated and provisional. Emotion labels are raw classifier outputs, not reliable measurements of a caller's internal state.
- Audio quality screening is heuristic and can flag ordinary speech or miss degraded audio. VAD availability affects its quality flags.
- The current attention bands are provisional and are not scientifically validated.
- The saved summary is intentionally compact: duration, analyzed-window count, final indicative category, peak indicators, quality flags, and model identity. It does not contain raw audio or a full per-window history.
- The current app has no authentication, durable call database, or training/fine-tuning workflow.
