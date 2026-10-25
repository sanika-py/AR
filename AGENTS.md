# Repository working rules

Before starting every task, read `BRAIN.md` and `TASKS.md`.

- Keep one task per branch.
- Run `pytest` before finishing a task and report the result.
- Never edit `MODEL_VERIFICATION.json` or model weights.
- Never store raw audio. Raw audio may exist only in the live in-memory buffer and must be discarded when recording stops.
- Never download models at runtime. Load only a locally available, pinned model that passes the existing verification checks.
- Emotion scores, derived indicators, and priority/attention outputs are advisory. Label them as advisory in the UI and documentation; do not present them as diagnoses or determinations.
