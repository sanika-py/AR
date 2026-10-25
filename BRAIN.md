# BRAIN — AwazRakshak source of truth

## Purpose

AwazRakshak is a local React dashboard backed by FastAPI for advisory voice-emotion signals. The browser requires recording consent before capturing audio. Scores are not calibrated measurements and never decide danger, deception, guilt, or dispatch.

## Current architecture

- `frontend/` contains the Vite/React/TypeScript/Tailwind UI, demo data, typed API contract, tests, and microphone AudioWorklet.
- `server/main.py` is the production ASGI entry point and serves a built `frontend/dist/` when available.
- `backend/app.py` exposes health, PCM16 audio and event WebSockets, plus the REST router.
- `live.py` is the reusable 30-second in-memory audio buffer and background inference pipeline. The backend and `tests/test_live.py` import it.
- `engine.py` and `signals.py` are compatibility exports for `backend/core/engine.py` and `backend/core/signals.py`.
- `backend/core/engine.py` verifies the pinned local model, screens audio, and validates scores. `backend/core/signals.py` derives/smooths indicators and applies two-window attention hysteresis.
- `backend/core/priority.py` returns provisional P1-P4 advisory groupings, urgency scores, reasons, and approved guidance templates.
- `backend/core/asr.py` provides optional local faster-whisper transcription, disabled by default. Transcript snapshots and keyword matches are memory-only.
- `backend/routes.py`, SQLAlchemy models, and Alembic migrations implement audio-free calls, summaries, flags, notes, and audit entries.
- `config.py` is authoritative for the model pin, labels, timing, indicator weights, and provisional thresholds.
- `ml/` contains manually invoked offline dataset/training utilities. They are not called during live inference.

## Pinned model

- Model ID: `Dpngtm/wav2vec2-emotion-recognition`
- Revision: `033a5751a5bbe5b0b67c2c71e6102c38de35a346`
- Ordered labels: `angry`, `calm`, `disgust`, `fearful`, `happy`, `sad`, `surprised`.
- Inference is CPU-only on mono 16 kHz samples. `AWAZRAKSHAK_MODEL_PATH` can point to the Hugging Face cache root or a snapshot directory. Existing pin and file-hash checks fail closed; runtime downloads are disabled.

## Live audio and indicators

- In-memory ring buffer: 30 seconds maximum.
- Analysis window: 3 seconds, updated every 1.5 seconds.
- Digital silence is skipped; other quality-flagged windows can still be scored.
- Distress = `0.50 * fearful + 0.30 * sad + 0.20 * angry`.
- Nervousness = `0.45 * fearful + 0.35 * surprised + 0.20 * min(rms_cv, 1)`.
- EMA alpha is `0.35`; provisional category thresholds are `0.35` Elevated and `0.65` High, with two-window hysteresis.

## Privacy and limitations

Raw live-call audio is processed only after consent, held in browser/process memory, and discarded when the live session ends. No database/API summary stores raw audio. Audio-free summaries and operator records may be saved locally through the REST API. Offline augmentation is a separate explicit dataset operation and may write derived WAV files. A remote API host receives the microphone stream. WebSocket authentication/session isolation and per-call read isolation are incomplete. Model signals and configured attention/priority thresholds are advisory, uncalibrated, and not scientifically validated.
