# AwazRakshak Repository Audit

**Scope:** Read the tracked source, tests, documentation, configuration, and model metadata in this repository. No application code was changed for this audit.

## What works today

- The Streamlit page gates recording on a consent checkbox, a local pinned-model availability check, and availability of `streamlit-webrtc`. It captures browser microphone frames, submits them to `LiveCallPipeline`, and displays live scores, derived indicators, quality warnings, attention bands, and a small event history.
- `LiveAudioBuffer` downmixes multichannel input, converts integer PCM to float, incrementally resamples to 16 kHz, and retains at most 30 seconds in a circular in-memory buffer. `LiveCallPipeline` runs inference on a worker thread over the latest 3-second window at a 1.5-second stride. Digital-silence windows are skipped.
- `engine.py` checks a full model revision pin, local file hashes from `MODEL_VERIFICATION.json`, exact label mappings, expected feature-extractor rate, CPU placement, and a synthetic forward pass. It requests `local_files_only=True`, disallows remote code, and requires safetensors. Missing or mismatched artifacts fail closed.
- Score validation checks the seven expected labels, uniqueness, finite values in `[0, 1]`, output dimension, and probability sum tolerance. Acoustic screening emits RMS, clipping, tonal, stationary-noise, VAD, and related flags without blocking non-silent scoring.
- `signals.py` implements the configured distress/nervousness formulas, bounded EMA smoothing, threshold bands, and two-consecutive-window category hysteresis. The UI labels raw scores uncalibrated, indicators derived, and the attention category indicative.
- Stopping clears the ring buffer. The app builds an audio-free summary with call timing, analyzed-window count, final category, peak indicators, quality flags, and model identity; it saves that JSON locally and also offers a download.

## Test results

Command run from the repository root:

```text
..\.venv\Scripts\python.exe -m pytest -v --basetemp=.pytest-tmp
```

**Result: 17 passed in 0.32 seconds.** Coverage includes score-vector validation, local model-path discovery and fail-closed checks, indicator formulas and smoothing, category thresholds/hysteresis, ring-buffer downmix/resampling/retention, fake-model pipeline inference, and low-quality handling.

The suite does not load the real pinned model, run browser/WebRTC capture, exercise Streamlit rendering, benchmark CPU latency, or cover concurrent users and hosted deployment. The `real_model` marker is declared in `pytest.ini`, but there is no real-model integration test among the tracked tests.

## File-by-file responsibilities

### Application and model

| File | Responsibility |
| --- | --- |
| `app.py` | Streamlit page, cached model checks/loading, consent and start/stop controls, WebRTC callback, live panel, summary construction, local JSON persistence and download. |
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
| `.streamlit/config.toml` | Streamlit server binds to `127.0.0.1`, disables usage stats, and defines the calm theme. |
| `requirements.txt` | Pinned Python runtime dependencies for Streamlit, WebRTC, NumPy, PyTorch, Transformers, soxr, VAD, and pytest. |
| `pytest.ini` | Declares the `real_model` marker; it does not itself configure a real-model test. |

### Tests

| File | Responsibility |
| --- | --- |
| `tests/test_engine_synthetic.py` | Accepts a valid seven-label score distribution and rejects invalid totals. |
| `tests/test_model_path.py` | Tests Hugging Face cache-root resolution and fail-closed behavior for missing/mismatched local snapshots. |
| `tests/test_signals.py` | Tests indicator math, invalid input handling, threshold mapping, smoothing, and hysteresis. |
| `tests/test_live.py` | Tests ring-buffer retention, integer stereo conversion/resampling, fake-model background inference, buffer clearing, and low-quality flags. |

## Coupling between the core modules

```text
config.py ───────► engine.py ───────► live.py ───────► app.py
      │                 │                 │                │
      └──────────────► signals.py ◄───────┘                │
      └───────────────────────────────────────────────────►│
```

- `config.py` is shared global policy: `engine.py`, `live.py`, and `signals.py` import its model, timing, quality, smoothing, indicator, and category constants. Formula text is separately imported by `app.py` for display.
- `engine.py` owns the `ModelBundle` contract. `live.py` expects the injected model factory to return an object with `labels`, `output_dimension`, and `predict_scores`; it also calls `screen_window()` and validates the returned vector itself.
- `live.py` calls `derive_indicators()`, `smooth_indicator()`, and `categorize_call()` from `signals.py`, and exposes a snapshot schema (`latest`, `insights`, `events`, `error`, `recording`, `started_at`, `duration_seconds`) that `app.py` reads directly.
- `app.py` owns the model-path preflight/cache wrappers and passes a closure into the pipeline. Its nested WebRTC processor calls `pipeline.add_audio()`. Its Streamlit fragment polls `pipeline.snapshot()` every 1.5 seconds, and its summary builder depends on the internal insight fields.
- The design has useful seams—pure score checks and a model-factory injection—but there is no versioned service DTO/interface between the UI and live pipeline. Changing snapshot or indicator field names requires coordinated edits in `live.py`, `signals.py`, and `app.py`.

## Streamlit-specific blockers to FastAPI reuse

- `app.py` imports Streamlit at module import and executes page setup, widgets, session-state mutation, and rendering at module scope. Importing it from an ASGI app would run UI code; business logic cannot be imported cleanly as a module.
- `st.session_state` currently owns the lifetime and identity of a call pipeline, recording flag, and summary. FastAPI needs explicit per-client/session ownership, request authentication, teardown on disconnect, and concurrency isolation.
- `st.cache_data` and `st.cache_resource` wrap model availability/loading. Their keying, invalidation, and process lifetime are Streamlit behavior; a service needs explicit dependency lifecycle and model singleton/thread-safety policy.
- `st.fragment(run_every=...)`, widgets, charts, warnings, and download buttons are presentation and polling mechanisms with no FastAPI equivalent. The browser client will need an API schema and a transport such as WebSocket/SSE for live insights plus an HTTP endpoint for summaries.
- `streamlit-webrtc`'s `AudioProcessorBase.recv(frame)` is the current capture adapter. A FastAPI service cannot directly reuse that callback lifecycle; microphone signaling, frame decoding, backpressure, disconnect cleanup, and worker cancellation need a separately designed ASGI/WebRTC adapter.
- `LiveCallPipeline` uses Python `threading.Event`, `threading.Lock`, and a daemon thread. An async server needs a deliberate bridge between worker execution and event-loop clients, bounded queues, cancellation, and per-call resource limits.
- `save_summary()` writes relative to the application file into local disk storage. A service needs a configured storage interface, access control, retention/deletion policy, and deployment-specific persistent-volume behavior.

## Top 10 risks, ranked

1. **Emotion validity and interpretation.** The model outputs are explicitly uncalibrated; derived weights and attention thresholds are provisional engineering values. They must not be treated as validated indicators of a caller's internal state or as operational decisions. The verification manifest's synthetic zero-audio pass produced a `sad` score of about `0.960`; this pass checks finite logits and output shape, not emotion validity. The live pipeline does skip digital silence. Tests establish code behavior, not real-world validity.
2. **Audio confidentiality in hosted deployments.** Browser microphone frames are sent through WebRTC to the machine running Streamlit. The default config binds localhost, but exposing or proxying the app changes the privacy boundary and transmits call audio to that host. The README's local-use assumption must remain explicit.
3. **No user identity or enforced authorization.** The consent checkbox is a self-attestation only. There is no login, role check, session authorization, or audit trail to establish who recorded a call or whether they were entitled to do so.
4. **Model cannot be reproduced from the tracked checkout alone.** The 378 MB safetensors file is absent and ignored. Analysis correctly fails closed without a local copy, so a fresh clone or cloud deployment cannot analyze until a verified model is provisioned out of band. The manifest also says `human_approved: false`, but runtime verification does not require that field to be true before loading the model.
5. **Sensitive summaries persist without lifecycle controls or complete long-call coverage.** Summary JSON is written unencrypted under `.awazrakshak-data/summaries/`; no retention, deletion, access-control, or backup policy is implemented. The summaries omit audio but retain timing and model-derived values. In-memory insight/event history is capped at 2,000 entries, so calls longer than roughly 50 minutes can have a duration that covers the full call while window counts and peaks are calculated from only the retained tail.
6. **Unresolved model/dataset licensing.** `LICENSES.md` flags unresolved rights around TESS, CREMA-D, SAVEE, RAVDESS, and derivative weights. The checkpoint's MIT metadata does not resolve these upstream terms; public or commercial release may be constrained.
7. **Audio clearing is not guaranteed to erase every in-flight copy immediately.** `stop()` clears the ring buffer after a thread join limited to two seconds. A worker already performing inference can still hold its local window array until it exits; deterministic memory erasure is not tested.
8. **CPU latency and overload behavior are unmeasured.** Inference is scheduled every 1.5 seconds on 3-second windows, but no test/benchmark demonstrates it keeps up on target CPUs. Slow inference can delay updates; there is no explicit queue/backpressure or latency alarm.
9. **Important runtime paths lack integration coverage.** The tests use a fake model and temp directories. They do not load the pinned weights, test Streamlit/WebRTC with a real browser, test multiple sessions, or exercise hosted TLS/proxy behavior, model-load failure during capture, and summary-storage failure end to end. They also do not cover VAD-unavailable behavior; `VAD_UNAVAILABLE` is emitted by `engine.py` but is not in `live.py`'s `_LOW_CONFIDENCE_FLAGS`, so that condition alone does not turn on the low-confidence warning.
10. **UI and service responsibilities are intertwined.** Module-level Streamlit execution, session state, cache decorators, WebRTC callback types, and direct snapshot-schema access make `app.py` unsuitable as a FastAPI module. Reusing it directly risks import-time UI side effects and cross-request lifecycle bugs; isolate framework-independent call orchestration first.
