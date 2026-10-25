# Unreleased — React-only UI cleanup

- Removed `app.py`, `.streamlit/config.toml`, and the `streamlit` / `streamlit-webrtc` runtime dependencies; kept the shared live audio pipeline and FastAPI API.
- Added `server/main.py` to serve the built React frontend and existing API from one local FastAPI process.
- Updated setup and run instructions for Vite development and production-style local serving.

# Changelog

Source of truth: [BRAIN.md](BRAIN.md). This log records the documented repository baseline; no release version is implied.

## Current repository state (unreleased)

- React/Tailwind dashboard served by Vite in development and FastAPI in a built local run.
- Local pinned model verification and CPU inference; model weights are not included in the tracked repository.
- Bounded in-memory audio buffer, 3-second windows, 1.5-second update cadence, audio screening, and silence skipping.
- Seven raw emotion labels, provisional derived indicators, EMA smoothing, and two-window attention-category hysteresis.
- FastAPI health, WebSocket analysis, and JWT-protected call/action APIs with SQLAlchemy/Alembic persistence.
- React/Tailwind dashboard with mock queue and optional consent-gated local microphone streaming.
- Offline ML utilities for speaker-independent data manifests, augmentation, staged training, calibration, evaluation, ONNX export, and separate v1 artifact registration.
- Docker Compose local/demo deployment, fail-fast local model hash check, GitHub Actions CI, and pre-commit hooks.
- Automated tests use synthetic inputs and fake models; no real-model accuracy or latency results are published.

## Remaining work

- Authenticate/isolate WebSocket sessions and connect React action controls to REST.
- Add production hosting controls, retention/deletion, backups, and operations.
- Perform governed representative evaluation and verify model/data provenance before considering model replacement or redistribution.
