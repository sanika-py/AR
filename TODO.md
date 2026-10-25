# Planned Work

Source of truth: [BRAIN.md](BRAIN.md). Completed items are checked. Remaining unchecked items are Planned unless explicitly described as current elsewhere.

- [x] **Audit:** repository inventory and privacy/security findings are in `docs/AUDIT.md` and `docs/TEST_PLAN.md`.
- [x] **Documentation:** implementation and limitations are documented; continue updating as code changes.
- [x] **Backend:** FastAPI health, event/audio WebSockets, Pydantic contracts, SQLAlchemy/Alembic persistence, JWT roles, and audited REST actions exist.
- [x] **Frontend:** React/Tailwind dashboard exists with accessible controls and advisory labels; officer actions remain mock-only.
- [x] **Live audio:** consent-gated browser audio streams PCM16 through WebSockets into bounded in-memory analysis; per-session authorization and isolation remain Planned.
- [x] **Priority bands (implementation):** provisional attention and P1-P4 indicators, smoothing/hysteresis, inspectable reasons, and advisory copy exist. Validation and threshold review remain Planned.
- [x] **Storage, actions, and auth:** audio-free records, JWT officer/supervisor/admin roles, audited actions, SQLite migrations, PostgreSQL support, and local summary saving exist. Retention, call-level read isolation, and production controls remain Planned.
- [ ] **Planned — Training and provenance:** offline scripts exist, but no governed dataset, completed experiment, validated metrics, or dataset/model rights review is present.
- [ ] **QA (partial):** unit/API/E2E/load test assets exist. Full pytest, Playwright, k6, real-model evaluation, security review, and measured coverage remain unverified or Planned; see `docs/TEST_PLAN.md`.
- [x] **DevOps (local/demo):** Dockerfiles, Compose model mount, startup hash gate, CI, and pre-commit configuration exist. Container execution, production hosting, backups, monitoring, incident response, and rollback remain Planned.
