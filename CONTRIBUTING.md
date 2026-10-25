# Contributing

Source of truth: [BRAIN.md](BRAIN.md). See [docs/AUDIT.md](docs/AUDIT.md) for the current repository inventory and coupling.

## Before changing the project

Read `BRAIN.md` and `TASKS.md` before each task. Keep one task per branch. Preserve the current data policy: never store raw audio, never download models at runtime, and never edit `MODEL_VERIFICATION.json` or model weights to bypass checks. All emotion outputs must remain labelled advisory in the UI and documentation.

## Development

Use Python 3.12 and install dependencies from `requirements.txt` in an isolated environment. Current code is a Streamlit application; FastAPI and React/Tailwind are migration targets, not existing interfaces. Keep model identity, label map, weights, and thresholds centralized in `config.py`. Keep inference validation and fail-closed local model verification in `engine.py`.

Before finishing a change, run `python -m pytest -v` and report the result. The current tests exercise synthetic and fake-model paths; passing tests do not establish real-model quality or performance. There is no documented formatter, linter, or CI policy in the current repository.

## Review expectations

Describe what changed and its evidence. Do not claim unmeasured model quality, latency, or deployment readiness. Avoid adding caller-identifying data to summaries. Any proposed hosted audio flow, persistent storage, authentication, or model/data redistribution needs explicit design and rights review.

**Planned:** Define API compatibility, frontend contribution, security review, and release procedures when those components are implemented.
