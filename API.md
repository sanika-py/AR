# API

Source of truth: [BRAIN.md](BRAIN.md). This contract describes the local FastAPI backend. Health is public; REST routes for calls, notes, summaries, and operator actions require a JWT bearer token.

## `GET /health`

Returns process health and the configured model identity without loading model weights:

```json
{
  "status": "ok",
  "model_id": "Dpngtm/wav2vec2-emotion-recognition",
  "model_revision": "033a5751a5bbe5b0b67c2c71e6102c38de35a346",
  "sample_rate": 16000
}
```

## `WS /ws/audio`

On connection, sends a JSON `session_started` message containing the generated `session_id` and `asr_enabled` flag. Then accepts non-empty binary WebSocket messages, each containing little-endian signed PCM16 samples for mono audio at 16 kHz. Audio messages have no per-message header or JSON envelope. Text messages from the client, empty messages, and byte lengths not divisible by two are rejected with WebSocket close code `1003`.

Each connection has its own `LiveCallPipeline`, using the configured 3-second analysis window, 1.5-second default update interval, in-memory ring buffer, and existing pinned model verification. Disconnecting stops that pipeline and clears its audio buffer. Raw audio is not written to disk. The audio socket accepts data only; insight messages are delivered on `/ws/events`.

## `WS /ws/events`

Receives ephemeral events broadcast to all currently connected event clients. There is no authentication or server-side session subscription filter yet. Clients should compare event `session_id` values with the `session_started` message from their audio connection and discard events for other sessions. Events contain analysis values and metadata, never waveform samples.

Analysis event:

```json
{
  "type": "analysis",
  "session_id": "00000000-0000-4000-8000-000000000001",
  "elapsed": 3.2,
  "scores": [
    {"label": "angry", "score": 0.05},
    {"label": "calm", "score": 0.10},
    {"label": "disgust", "score": 0.05},
    {"label": "fearful", "score": 0.50},
    {"label": "happy", "score": 0.05},
    {"label": "sad", "score": 0.15},
    {"label": "surprised", "score": 0.10}
  ],
  "indicators": {
    "distress_indicator": 0.4,
    "nervousness_indicator": 0.3
  },
  "quality_flags": [],
  "low_confidence": false,
  "category": "Elevated",
  "priority": "P3",
  "urgency_score": 5,
  "priority_reasons": ["Distress indicator 0.40 meets provisional P3 threshold 0.35."],
  "priority_guidance": "Advisory: Consider reviewing the conversation context and following standard intake steps."
}
```

This shape is illustrative; an actual analysis event contains all seven validated labels. `category` is one of `Routine`, `Elevated`, or `High` and is advisory. `indicators` are derived indicators, not model classes. `priority`, `urgency_score`, reasons, and fixed guidance are provisional advisory outputs; they never decide dispatch or another operational action.

Attention transition event:

```json
{
  "type": "attention_transition",
  "session_id": "00000000-0000-4000-8000-000000000001",
  "time": 12.0,
  "from": "Routine",
  "to": "Elevated"
}
```

Analysis error event:

```json
{
  "type": "analysis_error",
  "session_id": "00000000-0000-4000-8000-000000000001",
  "message": "Analysis disabled: reason"
}
```

When optional ASR is enabled, the event stream also sends replace-in-place transcript snapshots. The transcript and matches exist in process/browser memory only; a UI officer must explicitly copy text into an officer note to retain it in that note.

```json
{
  "type": "transcript_partial",
  "session_id": "00000000-0000-4000-8000-000000000001",
  "text": "Caller says they were threatened.",
  "language": "en",
  "keyword_hits": ["threatened"],
  "status": "partial",
  "message": null
}
```

## Configuration and limits

`AWAZRAKSHAK_API_HOST` and `AWAZRAKSHAK_API_PORT` configure the module entry point (`python -m backend.app`); defaults are `127.0.0.1` and `8000`. `AWAZRAKSHAK_LIVE_UPDATE_INTERVAL_SECONDS` configures the update interval (default `1.5`). `AWAZRAKSHAK_MODEL_PATH` selects the local model cache/snapshot. The model sample rate and analysis window remain configured at 16 kHz and 3 seconds.

Optional ASR is off unless `ASR_ENABLED=true`. Enable it after installing `requirements-asr.txt` and set `ASR_MODEL_PATH` to an already-present faster-whisper `small` model directory. Inference uses CPU int8 and automatically detects supported languages, including English, Hindi, and Marathi. The service does not download ASR models at runtime. `backend/core/keywords.yaml` configures provisional phrase aliases, fuzzy-matched with RapidFuzz.

## JWT-protected REST API

`POST /auth/token` accepts `{"username": "...", "password": "..."}` and returns an HS256 bearer token. `JWT_SECRET_KEY` must be set to a random secret of at least 32 bytes; tokens expire after `JWT_LIFETIME_MINUTES` (default 30). Accounts have the roles `officer`, `supervisor`, or `admin`; role claims are checked against the active database account on every request. Create the initial account with `python -m backend.cli create-officer <username> --role admin` after applying migrations.

The following routes require authentication:

- `POST /calls` — create an audio-free call record. Returns `call_id`.
- `POST /calls/{call_id}/escalate` — officer, supervisor, or admin; accepts a required `reason`. Records the officer action and increments escalation state. This is an advisory workflow action, not a dispatch decision.
- `POST /calls/{call_id}/flag` (also `POST /calls/{call_id}/flags`) — officer, supervisor, or admin; accepts a required `reason` and creates an open review flag.
- `POST /calls/{call_id}/transfer` — supervisor or admin; accepts `target_team` and optional `reason`, then updates the assigned team.
- `POST /calls/{call_id}/notes` — officer, supervisor, or admin; stores explicitly submitted note text.
- `POST /calls/{call_id}/summaries` — officer, supervisor, or admin; stores only the allow-listed summary fields in `SCHEMA.md`. Unknown fields (including `audio`) are rejected.

Each successful mutation inserts its corresponding `audit_log` record in the same database transaction. A failed commit rolls back both the requested change and its audit record. Login success and CLI account provisioning are also audited. Database migrations are applied with `alembic upgrade head`; `DATABASE_URL` defaults to a local SQLite file and accepts a PostgreSQL URL (normalized to the installed psycopg 3 driver).

WebSocket audio and event routes remain unauthenticated in this iteration. Keep the service bound to a trusted local environment; do not expose these sockets to an untrusted network. All model scores, indicators, priority bands, and guidance are advisory and must not be used as determinations or automated dispatch actions.
