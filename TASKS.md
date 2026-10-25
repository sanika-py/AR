# Migration and delivery phases

Complete one task per branch and update this checklist as phases are finished.

- [ ] **1. Audit** — map the existing Streamlit behavior, data flow, model verification, and deployment constraints against `BRAIN.md`.
- [ ] **2. Docs** — document the target architecture, local model setup, privacy boundaries, advisory output language, and operator workflow.
- [ ] **3. Backend** — implement the FastAPI service layer while preserving pinned local inference, input validation, and fail-closed model verification.
- [ ] **4. Frontend** — build the React + Tailwind interface with consent, status, accessible live indicators, and advisory labels.
- [ ] **5. Live audio** — connect browser microphone streaming to bounded in-memory buffering and background windowed inference; never persist raw audio.
- [ ] **6. Priority bands** — implement provisional attention/priority bands, smoothing, hysteresis, and explicit non-decision language.
- [ ] **7. Storage/actions/auth** — define audio-free summary storage, operator actions, access controls, and retention behavior.
- [ ] **8. Training** — determine whether training/labeling is in scope; isolate any approved dataset and training work from runtime inference.
- [ ] **9. QA** — cover score validation, indicators, smoothing, hysteresis, buffering, API/UI behavior, privacy properties, and deployment checks.
- [ ] **10. DevOps** — establish reproducible local setup, CI, pinned dependencies, secrets handling, and deployment that respects the local-model and audio-privacy requirements.
