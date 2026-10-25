# Security and product release checklist

**Review date:** 2026-10-25  
**Overall result:** **FAIL — not release-ready for operational use.** Live-call audio and committed-secret checks pass within the scope below. Advisory marking is not explicit on every output, and local test/deployment evidence is incomplete.

## 1. Raw audio persistence — PASS for live-call runtime; offline dataset caveat

- `live.py` stores incoming samples in a bounded in-memory buffer and clears it when the pipeline stops. `backend/app.py` passes decoded PCM16 frames to the in-memory pipeline and ASR session; it has no audio file/database write path.
- `backend/models.py` has no audio/blob column. `backend/schemas.py` defines an allow-listed `SummaryRequest`; `tests/test_storage_api.py` rejects an extra `audio` field (that API test could not be collected in the current local environment because SQLAlchemy/Alembic are absent).
- Streamlit saves audio-free JSON summaries; Docker mounts the model read-only and database volume separately. The WebSocket event contract sends scores/indicators, not waveform samples.
- **Scope caveat:** `ml/augment.py` writes WAV augmentation derivatives from an operator-supplied dataset to the chosen output directory. This utility is offline and is not wired to live microphone capture. Do not treat the whole repository as a no-audio-files training workspace.
- No claim is made that process-memory samples are securely erased; a worker may retain an in-flight local window briefly after stop, as documented in `SECURITY.md`.

## 2. Committed secrets — PASS based on repository scan

- `git ls-files` contains `.env.example`, but no `.env`, private-key file, or credentials file. `.env.example` contains blank `JWT_SECRET_KEY`/`ASR_MODEL_PATH` values and non-secret local defaults.
- The tracked test code contains a fixed `test-secret-key-with-at-least-32-bytes` fixture for JWT tests; it is explicitly a test value, not a production credential.
- A repository text scan found no populated credential assignments. No scan can establish whether a secret was committed in earlier Git history; review history separately if the repository was ever public with real credentials.

## 3. Advisory labels — FAIL (inconsistent at field/output level)

- React UI labels priority, urgency, insight, chart, transcript, and relevant keyword content as **Advisory**, and displays the non-decision disclaimer (`frontend/src/App.tsx`, `frontend/src/Charts.tsx`).
- Streamlit has a page-level disclaimer and calls the raw label “uncalibrated” and attention “indicative” (`app.py`), but the individual distress/nervousness metrics and saved summary peak fields do not consistently carry an explicit Advisory label/marker.
- FastAPI `AnalysisEvent` returns scores, indicators, attention category, priority, and urgency without a top-level advisory marker or per-field descriptions that clients can rely on. `AnalysisErrorEvent` and the saved JSON/SQL summary contracts likewise have no advisory field. API docs say outputs are advisory, but client consumers can receive unlabeled values.
- **Release action:** add a machine-readable advisory designation to analysis/summary contracts and make every rendered Streamlit metric/summary explicitly advisory; add contract/UI tests that assert the designation. Do not represent priority as a determination or action instruction.

## 4. Documentation/code alignment — PASS after this review's updates, with known planned gaps

- Updated `README.md`, `ARCHITECTURE.md`, `DATA.md`, `DATA_DICTIONARY.md`, `LIMITATIONS.md`, `RUNBOOK.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `DECISIONS.md`, `EVALUATION.md`, `PROMPTS.md`, `SCHEMA.md`, `DEPLOYMENT.md`, `BRAIN.md`, `docs/AUDIT.md`, and `docs/ui/UI_SPEC.md` to describe the existing FastAPI/React/database/ML/Docker components and distinguish live-call capture from offline dataset augmentation.
- `docs/AUDIT.md` now identifies its original Streamlit-only findings and 17-test result as historical and adds current-state evidence. `docs/ui/UI_SPEC.md` identifies the implemented React demo separately from planned/unsupported operational integrations.
- Remaining limitations are identified as Planned or incomplete: unauthenticated/global WebSocket events, demo-only React actions, no automatic retention/deletion, no validated model metrics, and no production deployment hardening.

## 5. TASKS.md — PASS

`TASKS.md` now marks initial audit/docs/backend/frontend/live-audio/priority phases complete, leaves storage governance, dataset/provenance, full QA, and production DevOps open, and states the verification limits. This is consistent with the implementation and `TODO.md`.

## Verification evidence and release blockers

- Latest available focused Python run: **48 passed** with API/storage test modules excluded. Full pytest collection is blocked locally because SQLAlchemy and Alembic are missing.
- Frontend lint, Vitest (10 tests), and production build passed in the current local environment. Playwright, k6, Docker build/startup, Ruff, and Mypy were not verified locally. CI is configured for Python Ruff/Mypy/pytest and frontend lint/test/build.
- `python -m compileall`, YAML parsing, and `git diff --check` passed during the latest configuration/review checks.
- No model accuracy, fairness, privacy-erasure, or production-readiness conclusion follows from these checks.

**Decision:** Do not present this as an operational release until the advisory-label gap is closed and the dependency-complete API, browser, container, and security checks have evidence in CI or an authorized deployment environment.
