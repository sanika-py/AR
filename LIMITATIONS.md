# Limitations

Source of truth: [BRAIN.md](BRAIN.md). Outputs are advisory and must be interpreted with independent human judgement.

- Raw emotion scores are uncalibrated classifier outputs, not reliable measurements of a caller's internal state.
- Distress and nervousness are derived indicators, not model classes. Their weights and the attention thresholds are provisional engineering choices and have not been scientifically validated.
- The model's accuracy, calibration, subgroup performance, robustness, and field usefulness have not been established in this repository.
- Audio quality checks are heuristic. They can flag ordinary speech or miss degraded audio; VAD availability also affects screening.
- The current flow analyzes short windows and a bounded history. It may miss context, language meaning, speaker identity, or events outside the window.
- The app has no authentication, multi-user authorization, durable call database, or configurable summary retention. Local summaries remain on disk and are not encrypted by the app.
- The pinned model weights are not included in the tracked repository. A matching local snapshot is required; the app does not fetch weights at runtime.
- The repository remains Streamlit. FastAPI and React/Tailwind migration work is Planned, not an available service.
- Browser audio sent to a hosted Streamlit server crosses the network; hosted use is not the same as local processing.
- Dataset and derivative-weight provenance/licensing questions are documented in `LICENSES.md` and remain unresolved.

**Planned:** Address the migration, evaluation, operational controls, and provenance work described in [TODO.md](TODO.md) before making broader deployment or performance claims.
