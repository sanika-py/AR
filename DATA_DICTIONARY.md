# Data dictionary

Source of truth: [BRAIN.md](BRAIN.md). REST and WebSocket models are defined in `backend/schemas.py` and described in [API.md](API.md).

The API persists officer accounts, call records, audio-free summaries, flags, notes, and audit log entries as defined in [SCHEMA.md](SCHEMA.md). Live PCM16 audio is accepted only by `/ws/audio`, buffered in memory, and discarded on disconnect; no audio field exists in the summary schema. Event payloads contain model scores, derived indicators, quality flags, provisional category/priority guidance, and optional transcript snapshots. All model-derived values are advisory.
