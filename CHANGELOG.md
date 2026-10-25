# Changelog

Source of truth: [BRAIN.md](BRAIN.md). This log records the documented repository baseline; no release version is implied.

## Current baseline

- Single-page Streamlit live microphone workflow with an authorization checkbox and `streamlit-webrtc` capture.
- Local pinned model verification and CPU inference; model weights are not included in the tracked repository.
- Bounded in-memory audio buffer, 3-second windows, 1.5-second update cadence, audio screening, and silence skipping.
- Seven raw emotion labels, provisional derived indicators, EMA smoothing, and two-window attention-category hysteresis.
- Audio-free JSON call summary saved locally and offered for download.
- Automated tests use synthetic inputs and fake models; no real-model accuracy or latency results are published.

## Planned

- FastAPI backend and React/Tailwind frontend.
- Versioned API and data contracts, authentication, governed storage, and hosted deployment controls.
- Representative evaluation and verified model/data provenance.
