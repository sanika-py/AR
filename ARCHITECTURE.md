# Architecture

Source of truth: [BRAIN.md](BRAIN.md). Repository findings: [docs/AUDIT.md](docs/AUDIT.md).

## Current system

The only user interface is the React + TypeScript + Tailwind application in `frontend/`, built by Vite. It defaults to synthetic demo data; `VITE_USE_MOCK=false` enables consent-gated browser microphone capture. `server/main.py` exposes the existing FastAPI application and serves the built `frontend/dist/` when present. `backend/app.py` provides `/health`, `/ws/audio`, and `/ws/events`, and includes the protected REST router. `backend/routes.py`, `backend/models.py`, `backend/database.py`, and Alembic migrations implement audio-free records and audited officer actions.

```text
Browser UI (frontend/)
  ├── GET /health
  ├── WS /ws/audio ── PCM16 mono, 16 kHz ──┐
  └── WS /ws/events ◀── advisory events     │
                                            ▼
server/main.py ── backend/app.py ── LiveCallPipeline (memory only)
                                      ├── engine.py ── pinned local model
                                      └── signals.py ── indicators and bands
```

The React client uses an AudioWorklet to produce approximately 100 ms PCM16 chunks. `live.py` keeps at most 30 seconds in a bounded in-memory buffer and runs a 3-second window every 1.5 seconds. Digital silence is skipped. Other screened windows can be scored with quality flags. No live audio is written to disk.

`engine.py` and `signals.py` provide compatibility exports from `backend/core/`. `config.py` remains the source of model identity, ordered labels, timing, indicator weights, and provisional thresholds. Optional ASR and the `ml/` training scripts are separate local or offline paths; model downloads are disabled at runtime.

## Runtime and trust boundaries

The browser sends audio to the host running FastAPI. A remote deployment therefore transmits microphone audio to that host. WebSocket audio and events are currently unauthenticated and event clients are not session-filtered. REST actions require JWT roles. SQL storage accepts summary fields, notes, flags, and audit records, never raw audio. The live buffer is cleared when its socket disconnects. Explicit offline ML augmentation can write dataset-derived audio files to its operator-selected output directory; it is not called by live inference.

## Limitations

Model scores and derived indicators are uncalibrated advisory signals. Priority thresholds are provisional. The frontend's action controls remain demo-only and are not connected to authenticated REST actions. Per-call read isolation, WebSocket authentication, database retention/deletion, hosted TLS/secrets, and production operations remain incomplete.
