# Limitations

Source of truth: [BRAIN.md](BRAIN.md).

- Emotion scores and derived indicators are uncalibrated advisory signals, not reliable measurements of internal state.
- Audio quality screening is heuristic; provisional attention and priority thresholds are not scientifically validated.
- A remote API host receives the browser microphone stream. The documented setup is for local/demo use.
- The audio and event WebSockets are unauthenticated and event subscribers are not isolated by session.
- Per-call read isolation, database retention/deletion, hosted TLS/secrets, monitoring, and backups are not configured.
- The React dashboard's action controls remain demo interactions and are not wired to authenticated REST routes.
- Optional ASR requires separately provisioned local model files and can add substantial CPU use; it is disabled by default.
- There is no governed training dataset, completed training run, or approved replacement model.
