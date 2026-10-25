# Decisions

Source of truth: [BRAIN.md](BRAIN.md).

## ADR 0001 — Keep inference local and pinned

**Status:** Accepted.

**Decision:** Load only the configured pinned model from a local cache/snapshot, verify the existing pin and artifact hashes, and fail closed when verification fails. Never download model files at runtime.

## ADR 0002 — Keep live-call audio transient

**Status:** Accepted.

**Decision:** Process microphone audio in a bounded in-memory buffer and discard it when a live session ends. Store audio-free summaries and officer records only.

## ADR 0003 — Use React as the only UI

**Status:** Accepted; supersedes the previous dual-interface transition decision.

**Context:** The repository now has a Vite/React UI and a FastAPI service implementing its health, audio, and event contracts.

**Decision:** Keep `frontend/` as the only user interface. Run it through Vite in development and serve its built `dist/` from FastAPI in production-style local use. Keep UI-independent inference, buffering, signal, and API code in normal Python modules.

**Consequences:** No UI framework-specific runtime or package is required. All emotion and priority outputs remain labelled advisory and uncalibrated. The existing REST storage/auth limitations and unauthenticated WebSockets remain open.
