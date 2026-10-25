# Architecture Decisions

Source of truth: [BRAIN.md](BRAIN.md). These records describe implemented choices or clearly mark proposed work.

## ADR 0001 — Pin and verify a local model

**Status:** Accepted; implemented.

**Context:** Results need a reproducible model identity, and runtime downloads are out of scope.

**Decision:** Use `Dpngtm/wav2vec2-emotion-recognition` at revision `033a5751a5bbe5b0b67c2c71e6102c38de35a346`. Load only local files; check expected metadata and hashes in `MODEL_VERIFICATION.json`; disable analysis if checks fail.

**Consequences:** Model availability depends on separately provisioned local weights. The repository does not contain `model.safetensors`. The provenance and licensing status of underlying datasets and derivative weights remain unresolved; see `LICENSES.md`.

## ADR 0002 — Keep raw audio transient

**Status:** Accepted; implemented in the application flow.

**Context:** Calls contain sensitive audio.

**Decision:** Keep microphone audio in a bounded process-memory ring buffer, skip digital silence, clear the buffer when recording stops, and save only an audio-free summary.

**Consequences:** The summary cannot reproduce or reanalyze a call. A hosted service would receive browser audio and would require a separate privacy and retention design.

## ADR 0003 — Use Streamlit for the current interface

**Status:** Accepted for current baseline; migration is Planned.

**Context:** The implemented product is a single-page live workflow.

**Decision:** Keep the current interface in Streamlit with `streamlit-webrtc` microphone capture and a live fragment.

**Consequences:** Streamlit session state, reruns, fragments, and WebRTC component lifecycle are coupled to `app.py`. They cannot be directly reused as FastAPI service behavior. A FastAPI backend with a React and Tailwind frontend is Planned.

## ADR 0004 — Treat indicators as advisory

**Status:** Accepted; implemented in UI language and configuration.

**Context:** A classifier score is not a validated measure of a person's internal state or danger.

**Decision:** Label emotion scores uncalibrated, derived indicators as non-model classes, and attention bands as indicative. Do not present them as a decision about danger, deception, guilt, or dispatch.

**Consequences:** Users must apply independent judgement. Thresholds and indicator weights are provisional engineering values and must not be treated as validated cutoffs.

## ADR 0005 — Keep model and data rights unresolved until verified

**Status:** Accepted constraint.

**Context:** `LICENSES.md` records unresolved licensing and provenance for source emotion datasets and derivative weights.

**Decision:** Do not claim rights that have not been verified, and do not add a project license file without an owner decision and rights review.

**Consequences:** Redistribution and deployment decisions involving model weights or data require legal/provenance review. **Planned:** record verified provenance and obtain an explicit project-license choice.

## ADR 0006 — Do not claim measured quality or latency

**Status:** Accepted; current evidence is limited to automated tests and model integrity checks.

**Context:** The tracked tests use synthetic audio and fake models and do not benchmark the pinned model or browser capture.

**Decision:** Publish no accuracy, calibration, CPU latency, or field-performance metrics until a suitable evaluation has been performed and documented.

**Consequences:** The system's real-world predictive quality and target latency remain unknown. Evaluation work is Planned.
