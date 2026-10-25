# QA and test plan

This plan describes the automated checks added for AwazRakshak. Emotion, distress, nervousness, attention, and priority outputs are advisory; tests verify implementation contracts, not the truth of those inferences.

## Test layers

### Python unit tests

Run `python -m pytest -v`. `tests/test_signals.py` and `tests/test_qa_unit.py` cover indicator formulas, invalid inputs, EMA smoothing, attention thresholds, and category hysteresis. `tests/test_priority.py` and `tests/test_qa_unit.py` cover threshold boundaries, keyword mapping, urgency range, reasons, and advisory wording.

### API and storage contract tests

`tests/test_backend_api.py` exercises health, WebSocket route registration, PCM16 decoding, synthetic audio analysis, and event publication. `tests/test_api_contract.py` checks OpenAPI paths, health and event payload contracts, audio exclusion, and event field aliases. `tests/test_storage_api.py` covers JWT role enforcement, audited actions, audio-field rejection, and migration-created tables. These tests use a synthetic model or schema checks; they do not download or load the pinned model.

### Frontend unit and browser E2E

From `frontend/`, run `npm test` for Vitest component/store/type tests and `npm run test:e2e` for Playwright. `e2e/dashboard.spec.ts` checks card selection, detail update, demo action state, and Escape dismissal of the transfer dialog. `e2e/microphone.spec.ts` uses Chromium's fake microphone and a synthetic WebSocket backend to check consent gating, PCM16 chunk transport, event rendering, and permission-denial behavior. It does not exercise a physical microphone or real inference.

### Concurrent stream load test

With k6 installed and the FastAPI service running, run `k6 run load/audio_streams.js`. The script ramps to 20 concurrent WebSocket audio sessions, keeps each session open for 30 seconds by default, sends synthetic silence in 100 ms PCM16 chunks, and checks the handshake, errors, and connection latency. Configure `WS_BASE_URL` and `STREAM_SECONDS` as needed. This is an opt-in load exercise, not a CI acceptance result. Run only against a local or explicitly authorized test service. The synthetic silence avoids collecting real caller content but does not represent realistic inference load because silence windows are skipped.

## Risks prioritized for QA

1. **WebSocket authorization and event isolation:** audio and events sockets currently do not authenticate or scope event subscribers to a session.
2. **CPU saturation:** 20 simultaneous active inference sessions may queue work or exceed the connection-latency threshold on a given machine.
3. **Model validity:** this suite uses synthetic model outputs and does not evaluate emotion validity, calibration, demographic effects, or suitability for operational use.
4. **Audio conditions:** fake device and synthetic chunks do not cover physical devices, clipping, background noise, accents, codecs, or telephony hardware.
5. **Storage transaction failures:** basic audited action paths are covered; crash recovery, concurrent updates, database corruption, and PostgreSQL behavior need separate testing.
6. **Authentication operations:** role checks are tested, but brute-force protection, token revocation, key rotation, and production secret deployment are not.
7. **Browser/platform differences:** the browser test uses Chromium only; Firefox, WebKit, mobile browsers, and OS-level permission UX are not covered.
8. **Frontend/backend deployment topology:** proxy, TLS, reverse proxy timeouts, and multi-worker event fan-out need deployment integration tests.
9. **Privacy boundary regressions:** tests reject audio in the summary API, but do not comprehensively inspect process memory, logs, crash dumps, or host backups.
10. **Accessibility:** semantic controls are exercised by role in Playwright, but automated contrast, screen-reader, and full keyboard audits are not performed.

## Not tested / known gaps

- A complete end-to-end run against the real pinned model and a human-reviewed consented dataset.
- Ground-truth validation, calibrated performance, scientific validity, fairness, language coverage, or any performance metrics.
- Real-time latency under representative non-silent audio; k6 silence skips most model work.
- WebSocket authentication, session isolation, reconnect recovery, and multi-instance event distribution.
- PostgreSQL migration/driver behavior, backups, retention, and recovery procedures.
- Physical microphones, non-Chromium browser engines, mobile, assistive technologies, and formal accessibility conformance.
- Security penetration testing, secret rotation, rate limiting, and production infrastructure.

## Coverage reporting

No coverage percentage is asserted here. `pytest-cov` and an equivalent frontend coverage provider are not configured as project dependencies, and coverage has not been measured. Test counts and command outcomes should be reported from the actual environment running the suite; passing tests do not establish model accuracy or operational readiness.
