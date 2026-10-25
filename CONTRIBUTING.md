# Contributing

Use Python 3.12 and Node.js 20 or newer. Install Python requirements from `requirements.txt`; install frontend packages with `npm install` from `frontend/`. Keep model identity, labels, thresholds, and signal settings in `config.py`. Do not alter the pinned model behavior, download models at runtime, or persist raw live audio. All model-derived results must remain clearly labelled advisory and uncalibrated in user-facing text and docs.

Before a change, read `BRAIN.md` and `TASKS.md`. Run `python -m pytest -v` and, for frontend changes, `npm run build` and `npm test`. Do not commit secrets, model weights, or generated audio.
