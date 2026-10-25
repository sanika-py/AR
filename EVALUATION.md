# Evaluation and Test Evidence

Source of truth: [BRAIN.md](BRAIN.md). Detailed repository evidence is in [docs/AUDIT.md](docs/AUDIT.md).

## Current automated evidence

The tracked pytest suite covers score-vector validation, local model path discovery and fail-closed checks, indicator formulas and smoothing, category thresholds/hysteresis, ring-buffer conversion/retention, and live pipeline behavior with fake model output. At the audit baseline, `python -m pytest -v` reported **17 passed**. This is test-suite evidence, not a model accuracy or field validation result. The suite does not load the real pinned model or exercise browser/WebRTC capture and Streamlit rendering.

`MODEL_VERIFICATION.json` records integrity checks and a synthetic forward pass. A successful synthetic forward pass confirms a model can produce a valid-shaped output under that check; it does not demonstrate emotion recognition quality. In particular, the synthetic zero input result is not an evaluation metric, and digital-silence windows are skipped by the live pipeline.

## Metrics not established

This repository contains no measured accuracy, precision, recall, calibration, subgroup performance, robustness, CPU latency, or operational outcome metrics. No estimates are supplied here. The 1.5-second update interval is a configured cadence, not a demonstrated end-to-end latency bound.

## Planned evaluation

**Planned:** Define intended-use and exclusion criteria; obtain appropriate authorization and data governance; select suitable evaluation data and labels; predefine metrics and analysis; assess calibration, subgroup and recording-condition behavior; measure real-model CPU latency and browser-to-display timing; record limitations and reproducible results. Do not turn the provisional thresholds into claims of validated risk categories.
