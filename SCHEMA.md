# Data Schemas

Source of truth: [BRAIN.md](BRAIN.md). The persistent API schema is created by Alembic migration `0001_initial_storage`. It uses SQLAlchemy models and works with SQLite in development and PostgreSQL through `DATABASE_URL`.

## Persistent tables

- **officers** — `id` (UUID string PK), `username` (unique), `password_hash` (salted PBKDF2 hash), `role` (`officer`, `supervisor`, `admin`), `active`, `created_at`.
- **calls** — `id` (UUID string PK), `status` (`active`, `escalated`, `transferred`, `closed`), `assigned_team`, `escalated`, `escalation_count`, `created_by` (officers FK), `created_at`, `updated_at`.
- **summaries** — `id`, `call_id` (calls FK), `duration_seconds`, `analyzed_windows`, `final_attention_category`, `peak_distress_indicator`, `peak_nervousness_indicator`, `quality_flags` (JSON string array), `model_id`, `model_revision`, `created_at`. The summary has explicit columns and cannot accept an audio/blob field.
- **flags** — `id`, `call_id`, `officer_id`, `reason`, `status` (`open` or `reviewed`), `created_at`.
- **notes** — `id`, `call_id`, `officer_id`, `content`, `created_at`. Transcript text reaches this table only when explicitly submitted as a note.
- **audit_log** — `id`, nullable `actor_id`, nullable `call_id`, `action`, JSON `details`, `created_at`. Action mutation and audit row are committed in one database transaction.

Foreign keys link records to their owning call/officer. Summary request fields are allow-listed; unknown fields such as `audio` are rejected. None of the six tables has an audio/blob field. No raw audio is persisted.

## Role permissions

`officer` and higher roles may create calls, escalate, flag for review, add notes, and save summaries. Only `supervisor` and `admin` may transfer calls. `admin` has the same current action permissions as `supervisor`; user provisioning is through the local CLI. JWT claims are checked against the active officer record on each request.

## Migration and bootstrap

Apply schema changes with `alembic upgrade head`. Create the initial administrator after migration with `python -m backend.cli create-officer admin --role admin`; the CLI prompts for a password and records account provisioning in `audit_log`. Configure a random `JWT_SECRET_KEY` of at least 32 bytes before requesting access tokens.

## Current live insight shape

```json
{
  "elapsed": 3.2,
  "scores": [
    {"label": "angry", "score": 0.1},
    {"label": "calm", "score": 0.2},
    {"label": "disgust", "score": 0.1},
    {"label": "fearful", "score": 0.2},
    {"label": "happy", "score": 0.1},
    {"label": "sad", "score": 0.2},
    {"label": "surprised", "score": 0.1}
  ],
  "indicators": {
    "distress_indicator": 0.0,
    "nervousness_indicator": 0.0
  },
  "quality_flags": [],
  "low_confidence": false,
  "category": "Routine"
}
```

The numerical values above only illustrate field shape; they are not measurements, examples of expected model behavior, or thresholds.

## Current saved summary shape

```json
{
  "application": "AwazRakshak",
  "created_at": "2000-01-01T00:00:00+00:00",
  "started_at": "2000-01-01T00:00:00+00:00",
  "duration_seconds": 0.0,
  "analyzed_windows": 0,
  "final_attention_category": "No analysis available",
  "peak_distress_indicator": 0.0,
  "peak_nervousness_indicator": 0.0,
  "quality_flags": [],
  "model": {
    "id": "Dpngtm/wav2vec2-emotion-recognition",
    "revision": "033a5751a5bbe5b0b67c2c71e6102c38de35a346"
  }
}
```

The timestamp values and numeric values are illustrative examples of valid field shapes, not actual call data or measured results. Summary numeric fields are rounded by the current builder. No raw audio or full live history is included.

## Planned schema evolution

**Planned:** Add explicit schema versioning, audit-log export/retention policy, note redaction/deletion, and broader database backup/restore procedures. Live websocket sessions are not yet bound to authenticated officer identities or persisted call records.
