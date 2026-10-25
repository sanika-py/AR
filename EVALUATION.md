# Evaluation and Test Evidence

Source of truth: [BRAIN.md](BRAIN.md). Detailed repository evidence is in [docs/AUDIT.md](docs/AUDIT.md).

## Current automated evidence

The pytest suite covers score-vector validation, local model path discovery and fail-closed checks, indicator formulas and smoothing, category thresholds/hysteresis, ring-buffer conversion/retention, priority boundaries, startup checks, and synthetic pipeline behavior. At the 2026-10-25 local QA run, **48 Python tests passed** when API/storage modules were excluded because SQLAlchemy and Alembic were unavailable; full collection therefore did not pass in that environment. This is test-suite evidence, not a model accuracy or field validation result. CI installs project dependencies and is configured to run the full suite. No real pinned-model evaluation was performed.

`MODEL_VERIFICATION.json` records integrity checks and a synthetic forward pass. A successful synthetic forward pass confirms a model can produce a valid-shaped output under that check; it does not demonstrate emotion recognition quality. In particular, the synthetic zero input result is not an evaluation metric, and digital-silence windows are skipped by the live pipeline.

## Metrics not established

This repository contains no measured accuracy, precision, recall, calibration, subgroup performance, robustness, CPU latency, or operational outcome metrics. No estimates are supplied here. The 1.5-second update interval is a configured cadence, not a demonstrated end-to-end latency bound.

## Optional ASR CPU cost

ASR is disabled by default (`ASR_ENABLED=false`). When enabled, the backend loads an already-present faster-whisper `small` model on CPU using `int8` computation and re-transcribes a rolling 12-second mono window every 2 seconds. ASR inference runs on its own worker thread; it competes with emotion inference for CPU and memory and can increase event latency or reduce analysis cadence on slower hosts. ASR languages are auto-detected; English, Hindi, and Marathi are supported by the multilingual Whisper model when recognition quality permits. No hardware-specific CPU, memory, or latency measurements have been collected for this repository, so none are claimed. The configured model path must exist locally; the app does not download model files.

## Planned evaluation

**Planned:** Define intended-use and exclusion criteria; obtain appropriate authorization and data governance; select suitable evaluation data and labels; predefine metrics and analysis; assess calibration, subgroup and recording-condition behavior; measure real-model CPU latency and browser-to-display timing; record limitations and reproducible results. Do not turn the provisional thresholds into claims of validated risk categories.
