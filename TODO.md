# Planned Work

Source of truth: [BRAIN.md](BRAIN.md). Items below are not implemented unless explicitly described as current elsewhere.

- [ ] **Planned — Audit:** maintain an inventory of modules, dependencies, data flows, and security/privacy boundaries as the repository changes.
- [ ] **Planned — Documentation:** keep the current behavior and migration notes aligned with implementation and verified evidence.
- [ ] **Planned — Backend:** extract a transport-independent service layer and define versioned FastAPI contracts with input validation and error handling.
- [ ] **Planned — Frontend:** build the React and Tailwind interface, including accessible live status and advisory labels.
- [ ] **Planned — Live audio:** define browser-to-service audio transport, per-session isolation, cancellation, buffering limits, and privacy boundaries.
- [ ] **Planned — Priority bands:** evaluate and review provisional indicator weights and attention thresholds before retaining or changing them; do not claim they are validated.
- [ ] **Planned — Storage, actions, and auth:** decide whether summaries persist, define access and deletion controls, and implement authentication/authorization before multi-user hosting.
- [ ] **Planned — Training and provenance:** resolve model/dataset provenance and rights; define governance before any feedback collection or training work.
- [ ] **Planned — Quality assurance:** add approved real-model, browser audio, service contract, security, and performance evaluation only with suitable data and reproducible methods.
- [ ] **Planned — DevOps:** define supported deployment, model provisioning, monitoring, backup/deletion, incident response, and rollback after the service architecture exists.
