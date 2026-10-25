# Security

Source of truth: [BRAIN.md](BRAIN.md).

- Model loading is local-only and fails closed when pin or file-hash checks fail; runtime downloads are disabled.
- Live-call audio is buffered only in process memory and cleared on WebSocket disconnect. Persisted summaries and operator records exclude raw audio.
- `.env.example` is an example only. Do not commit real JWT keys, passwords, or credentials.
- REST mutations require JWT role checks and write audit records. WebSocket routes remain unauthenticated and events are not session-isolated.
- The default configuration is for local/demo use. A remote host receives microphone audio; public use requires TLS, authentication, network controls, per-call authorization, retention policy, backups, and monitoring.
- Emotion scores, derived indicators, attention bands, and priority guidance are advisory and uncalibrated; they must not be treated as determinations or dispatch decisions.
