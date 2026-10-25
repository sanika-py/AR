# Architecture

Source of truth: [BRAIN.md](BRAIN.md). Repository findings: [docs/AUDIT.md](docs/AUDIT.md).

## Current system

AwazRakshak is a single-page Streamlit application. `app.py` owns page rendering, consent, local model-path selection, session state, WebRTC microphone setup, live display, and audio-free summary persistence/download. `live.py` accepts microphone frames, downmixes and resamples them, retains a bounded 30-second ring buffer, and coordinates CPU inference on a background thread. `engine.py` resolves a local pinned snapshot, verifies its expected files, loads the classifier, screens 3-second windows, and validates seven scores. `signals.py` derives and smooths indicators and applies attention-band hysteresis. `config.py` contains model identity, label ordering, timing, weights, and provisional thresholds.

```text
Browser microphone
       │ WebRTC audio frames
       ▼
app.py ── consent, Streamlit session, display, summary
       │
       ▼
live.py ── bounded memory buffer ── background worker
       │                              │
       │                              ├── engine.py ── local verified model
       │                              └── signals.py ── derived indicators/bands
       ▼
audio-free summary JSON on local disk / browser download
```

The inference path uses mono 16 kHz audio. A 3-second window is considered every 1.5 seconds. Digital silence is skipped; other windows can be scored with quality flags. Model output is a raw seven-label score vector. Distress and nervousness are derived indicators, smoothed with EMA alpha 0.35. Attention bands are provisional and require two consecutive windows to change.

## Runtime and trust boundaries

The browser supplies microphone frames to the Streamlit host. In a local trusted run, that host is the user's machine. The application stores raw samples only in process memory, clears its ring buffer on stop, and writes an audio-free JSON summary under `.awazrakshak-data/summaries/`. Model files must already exist locally and match the pin/integrity checks; runtime model downloads and remote-code execution are disabled.

## Planned migration

**Planned:** Separate transport-independent inference and signal logic from the Streamlit entry point; expose a FastAPI service; implement a React and Tailwind interface; define versioned request/response schemas and session lifecycle; and design authentication, storage, and deployment boundaries before enabling those capabilities. No FastAPI routes, React client, persistent call database, or authentication layer currently exists. The audio transport, session isolation, cancellation, concurrency limits, and hosted privacy model need explicit design before a remote service is used.
