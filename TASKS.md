# Migration and delivery phases

Complete one task per branch and update this checklist as phases are finished.

- [x] **1. Audit** — map legacy UI framework/FastAPI/React behavior, data flows, model verification, and deployment/privacy constraints in `docs/AUDIT.md` and `docs/TEST_PLAN.md`.
- [x] **2. Docs** — document current architecture, local model setup, privacy boundaries, advisory language, and operator workflow. Ongoing doc/code alignment remains required.
- [x] **3. Backend (initial)** — FastAPI service, Pydantic contracts, local pinned-model inference, SQLAlchemy/Alembic schema, JWT roles, and audited REST actions implemented. WebSocket auth/session isolation remain open.
- [x] **4. Frontend (initial)** — React + Tailwind dashboard and consent-gated microphone flow implemented with advisory labels. REST action integration remains open.
- [x] **5. Live audio (initial)** — browser PCM16 streaming reaches bounded in-memory background inference; no live-call audio persistence. WebSocket identity/isolation and real-device verification remain open.
- [x] **6. Priority bands (provisional)** — configured indicator/keyword mappings, reasons, guidance, and advisory language implemented; thresholds are not validated.
- [ ] **7. Storage/actions/auth (partial)** — audio-free tables, roles, and audit actions exist. Retention/deletion, per-call read isolation, and hosted security controls remain open.
- [ ] **8. Training (offline utilities only)** — scripts exist, but no governed dataset, approved training, completed evaluation, or provenance/right review is complete.
- [ ] **9. QA (partial)** — synthetic unit/API/browser/load tests are present. Full dependency-complete pytest, browser E2E, k6, security assessment, real-model evaluation, and coverage measurement remain unverified; see `docs/TEST_PLAN.md` and `docs/RELEASE_CHECKLIST.md`.
- [ ] **10. DevOps (local/demo only)** — Dockerfiles, Compose model mount/startup hash check, CI, and pre-commit are configured. Container execution and production deployment, backups, monitoring, and rollback remain unverified/planned.
