# AwazRakshak Repository Audit

**Scope:** This report began as a legacy UI framework-only audit and is retained as a historical baseline. The current-state addendum below supersedes its time-sensitive claims. See `BRAIN.md`, `TASKS.md`, and `docs/TEST_PLAN.md` for maintained state.

## Current-state addendum (2026-10-25)

The React/Tailwind UI in `frontend/` is now the only UI. `server/main.py` serves its production build and reuses the FastAPI health, audio/event WebSocket, and REST APIs. SQLAlchemy/Alembic persistence, JWT roles, optional in-memory ASR, offline ML utilities, Docker Compose, GitHub Actions, and pre-commit remain. WebSockets are unauthenticated and globally broadcast; frontend officer actions are demo-only.

Live-call audio is not written to application files or the database: it is buffered in memory and cleared on stop/disconnect. Separate offline ML augmentation can write WAV derivatives from operator-supplied datasets to the chosen output path. Do not treat that explicit dataset workflow as the live-call persistence path.

The original `17 passed` result below is historical. After UI cleanup, a fresh Python 3.12 environment installed `requirements.txt` successfully and `python -m pytest -v` passed 62 tests. `npm install`, `npm run build`, and `npm test` passed (10 frontend tests). Uvicorn `/health` and `/` returned HTTP 200 on port 8017; port 8000 was occupied during the runtime check. Playwright, k6, Docker execution, Ruff, and Mypy remain unverified.

## What works today

- The React page defaults to mock data and can capture microphone audio after consent when `VITE_USE_MOCK=false`; its worklet sends PCM16 frames through `/ws/audio` and reads session-matched analysis events from `/ws/events`.
- `LiveAudioBuffer` downmixes multichannel input, converts integer PCM to float, incrementally resamples to 16 kHz, and retains at most 30 seconds in a circular in-memory buffer. `LiveCallPipeline` runs inference on a worker thread over the latest 3-second window at a 1.5-second stride. Digital-silence windows are skipped.
- `engine.py` checks a full model revision pin, local file hashes from `MODEL_VERIFICATION.json`, exact label mappings, expected feature-extractor rate, CPU placement, and a synthetic forward pass. It requests `local_files_only=True`, disallows remote code, and requires safetensors. Missing or mismatched artifacts fail closed.
- Score validation checks the seven expected labels, uniqueness, finite values in `[0, 1]`, output dimension, and probability sum tolerance. Acoustic screening emits RMS, clipping, tonal, stationary-noise, VAD, and related flags without blocking non-silent scoring.
- `signals.py` implements the configured distress/nervousness formulas, bounded EMA smoothing, threshold bands, and two-consecutive-window category hysteresis. The UI labels raw scores uncalibrated, indicators derived, and the attention category indicative.
- Disconnecting clears the backend ring buffer. Authenticated REST routes accept audio-free summaries and store them in SQL; the current React UI does not yet invoke the save-summary route.

## Test results

Command run from the repository root:

```text
..\.venv\Scripts\python.exe -m pytest -v --basetemp=.pytest-tmp
```

**Current result after cleanup: 62 passed in 3.80 seconds in a fresh environment.** The earlier baseline had 17 tests. Coverage includes API/REST contracts, score validation, local model-path fail-closed checks, indicator formulas/smoothing/hysteresis, ring-buffer behavior, fake-model inference, and quality handling.

The suite does not load the real pinned model, exercise a physical microphone/browser, benchmark CPU latency, or cover concurrent users and hosted deployment. The `real_model` marker is declared in `pytest.ini`, but there is no real-model integration test among the tracked tests.

## File-by-file responsibilities

### Application and model

| File | Responsibility |
| --- | --- |
| `server/main.py` | Production ASGI entry point serving the API and built frontend assets. |
| `live.py` | In-memory 30-second audio ring buffer, channel/dtype conversion and streaming resampling, worker-thread inference, quality aggregation, indicators/category history, and thread-safe snapshots. |
| `engine.py` | Model bundle and inference, label and score validation, audio quality metrics/VAD, local snapshot selection, manifest/hash verification, offline model loading, and synthetic forward pass. |
| `signals.py` | Indicator formulas, threshold classification, EMA smoothing, and attention-category hysteresis. |
| `config.py` | Model pin and labels, sampling/window/buffer/update settings, quality thresholds, indicator weights, provisional attention thresholds, and formula text. |
| `MODEL_VERIFICATION.json` | Recorded verification evidence and SHA-256 values for the required model artifacts; records `human_approved: false`. It is integrity metadata, not a substitute for runtime verification or human validation. |
| `Models/config.json` | Checked-in model configuration and label metadata. |
| `Models/preprocessor_config.json` | Checked-in feature-extractor configuration, including the 16 kHz input rate. |

The manifest records a 378,307,508-byte `model.safetensors`, but that weight file is not present in the tracked repository. `.gitignore` excludes `*.safetensors`; a local model path/cache must supply it for analysis to run.

### Project guidance and operator docs

| File | Responsibility |
| --- | --- |
| `README.md` | Python 3.12 setup, local run instructions, model-path requirements, and a short statement of limitations. |
| `AGENTS.md` | Repository task rules: read the source-of-truth docs, one task per branch, run tests, protect model/audio data, and keep emotion output advisory. |
| `BRAIN.md` | Current architecture, model pin, labels, live settings, privacy stance, and known limitations. |
| `TASKS.md` | Ten-phase migration/delivery checklist. |
| `docs/AUDIT.md` | This repository audit: behavior, test coverage, responsibilities, migration coupling, and ranked risks. |
| `LICENSES.md` | Review of model/base-model and training-dataset licensing, with unresolved derivative-weight and redistribution questions. |
| `.gitignore` | Excludes environments, caches, secrets, local data, and model weight formats including safetensors. |
| `.streamlit/config.toml` | Removed legacy server/theme configuration; retained here as historical inventory only. |
| `requirements.txt` | FastAPI/Uvicorn, model/runtime, storage, and test dependencies; old UI packages have been removed. |
| `pytest.ini` | Declares the `real_model` marker; it does not itself configure a real-model test. |

Current components include `server/main.py` (production API/static UI entry point), `backend/app.py` (FastAPI/WebSockets), `backend/routes.py` (REST actions), `backend/auth.py` (JWT/role checks), `backend/models.py` and `backend/database.py` (audio-free persistence), `migrations/` (Alembic schema), `backend/core/asr.py` (optional ephemeral ASR), `frontend/src/` (React dashboard/audio client), `ml/` (offline data/training utilities), and `Dockerfile.*`, `docker-compose.yml`, `.github/workflows/ci.yml`, and `.pre-commit-config.yaml` (local/demo operations and CI).

### Tests

| File | Responsibility |
| --- | --- |
| `tests/test_engine_synthetic.py` | Accepts a valid seven-label score distribution and rejects invalid totals. |
| `tests/test_model_path.py` | Tests Hugging Face cache-root resolution and fail-closed behavior for missing/mismatched local snapshots. |
| `tests/test_signals.py` | Tests indicator math, invalid input handling, threshold mapping, smoothing, and hysteresis. |
| `tests/test_live.py` | Tests ring-buffer retention, integer stereo conversion/resampling, fake-model background inference, buffer clearing, and low-quality flags. |

## Coupling between the core modules

```text
config.py ──► engine.py ──► live.py ──► backend/app.py ──► WebSocket events
    │             ▲            ▲              ▲
    └──► signals.py ────────────┘              │
server/main.py ─────────────────────────► backend/app.py ◄── frontend/
```

- `config.py` is shared global policy: `engine.py`, `live.py`, and `signals.py` import its model, timing, quality, smoothing, indicator, and category constants. The web UI consumes the API event contract rather than importing Python display helpers.
- `engine.py` owns the `ModelBundle` contract. `live.py` expects the injected model factory to return an object with `labels`, `output_dimension`, and `predict_scores`; it also calls `screen_window()` and validates the returned vector itself.
- `live.py` calls `derive_indicators()`, `smooth_indicator()`, and `categorize_call()` from `signals.py`, and exposes a snapshot schema (`latest`, `insights`, `events`, `error`, `recording`, `started_at`, `duration_seconds`) that `backend/app.py` converts to validated events.
- `backend/app.py` injects the cached verified-model factory into the pipeline and accepts browser PCM16 frames. `frontend/src/types.ts` validates resulting JSON events independently of the internal snapshot.
- The design has useful seams—pure score checks and a model-factory injection—but there is no versioned service DTO/interface between the UI and live pipeline. Changing snapshot or indicator fields requires coordinated edits in `live.py` and `backend/app.py`.

## Historical blockers to FastAPI reuse (resolved by removing the old UI entry point)

- The old `app.py` executed UI code at import time and has been removed. The FastAPI entry point now imports only reusable pipeline, model, and signal modules.
- The API owns a pipeline per audio WebSocket and clears it on disconnect; WebSocket authentication and event-session isolation remain open.
- The backend uses a cached model factory and continues to rely on fail-closed model verification.
- React rendering and WebSocket/Pydantic contracts are separate from the Python inference pipeline.
- Browser capture uses the retained AudioWorklet and existing PCM16 WebSocket API.
- `LiveCallPipeline` uses Python `threading.Event`, `threading.Lock`, and a daemon thread. An async server needs a deliberate bridge between worker execution and event-loop clients, bounded queues, cancellation, and per-call resource limits.
- The API summary endpoint writes audio-free records to SQL; retention/deletion, backups, and call-level read isolation remain incomplete.

## Top 10 risks, ranked

1. **Emotion validity and interpretation.** The model outputs are explicitly uncalibrated; derived weights and attention thresholds are provisional engineering values. They must not be treated as validated indicators of a caller's internal state or as operational decisions. The verification manifest's synthetic zero-audio pass produced a `sad` score of about `0.960`; this pass checks finite logits and output shape, not emotion validity. The live pipeline does skip digital silence. Tests establish code behavior, not real-world validity.
2. **Audio confidentiality in hosted deployments.** Browser microphone frames are sent to the processing host through the FastAPI audio WebSocket. Exposing/proxying either stack transmits audio to that host; the default local setup is not an assurance for remote use.
3. **WebSocket identity and session isolation are absent.** REST calls/actions use JWT roles and audit records, but audio/events WebSockets are unauthenticated and event subscribers receive global broadcasts. The consent checkbox is a self-attestation, not identity or legal-consent proof.
4. **Model cannot be reproduced from the tracked checkout alone.** The 378 MB safetensors file is absent and ignored. Analysis correctly fails closed without a local copy, so a fresh clone or cloud deployment cannot analyze until a verified model is provisioned out of band. The manifest also says `human_approved: false`, but runtime verification does not require that field to be true before loading the model.
5. **Sensitive summaries persist without lifecycle controls or complete long-call coverage.** Audio-free summaries are persisted to SQL; retention, deletion, encryption-at-rest, access control, and backup policy are incomplete. Summaries retain timing and model-derived values. In-memory insight/event history is capped at 2,000 entries, so calls longer than roughly 50 minutes can have a duration that covers the full call while window counts and peaks are calculated from only the retained tail.
6. **Unresolved model/dataset licensing.** `LICENSES.md` flags unresolved rights around TESS, CREMA-D, SAVEE, RAVDESS, and derivative weights. The checkpoint's MIT metadata does not resolve these upstream terms; public or commercial release may be constrained.
7. **Audio clearing is not guaranteed to erase every in-flight copy immediately.** `stop()` clears the ring buffer after a thread join limited to two seconds. A worker already performing inference can still hold its local window array until it exits; deterministic memory erasure is not tested.
8. **CPU latency and overload behavior are unmeasured.** Inference is scheduled every 1.5 seconds on 3-second windows, but no test/benchmark demonstrates it keeps up on target CPUs. Slow inference can delay updates; there is no explicit queue/backpressure or latency alarm.
9. **Important runtime paths remain unverified.** Synthetic/fake-model tests cover core contracts; the Playwright and k6 assets have not been validated in this environment, and tests do not load the real pinned weights, exercise physical microphones, hosted TLS/proxy behavior, or representative concurrent inference. `VAD_UNAVAILABLE` alone does not set the existing low-confidence flag.
10. **Frontend storage actions are not connected.** React action controls remain demo-only, while the existing REST operations require JWTs and call IDs; the UI needs explicit authenticated integration before operational use.
