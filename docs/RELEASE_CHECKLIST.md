# Security and product release checklist

**Review date:** 2026-10-25  
**Scope:** Local React + FastAPI application after removing the legacy UI.

## Audio persistence — PASS for live runtime

`LiveAudioBuffer` stores a bounded rolling window in process memory and `backend/app.py` stops the pipeline and transcriber in the audio socket's `finally` block. No SQL model/schema or summary request accepts raw audio. `tests/test_storage_api.py` checks summary payload validation. Offline `ml/augment.py` is separate and can write derived dataset WAV files when an operator explicitly runs it. Immediate secure erasure of all in-flight memory copies is not guaranteed.

## Secrets — source-level scan only

The tracked `.env.example` is an example, not a credential store; the JWT test fixture is a dummy test string. This review did not scan all prior Git history for secrets. The protected environment example and model-verification manifest were not modified.

## Advisory outputs — PARTIAL

The React UI labels model-derived insight content advisory and displays the non-decision disclaimer. The API still sends numeric emotion scores, indicators, category, and priority fields without a top-level machine-readable advisory marker. API consumers must follow `API.md` and treat all such values as advisory and uncalibrated. Do not use them as determinations or dispatch decisions.

## Runtime and verification — PASS with stated limits

- A fresh Python 3.12 virtual environment installed `requirements.txt` successfully.
- `python -m pytest -v`: 62 passed.
- `npm install`: completed; npm reported an install-script approval warning for esbuild, but the build succeeded.
- `npm run build`: passed.
- `npm test`: 10 passed.
- Uvicorn served `/health` and `/` with HTTP 200 on port 8017. Attempts to use port 8000 in this environment failed because it was occupied during the check.
- Model behavior was not changed. `MODEL_VERIFICATION.json` is protected and unchanged from `pre-cleanup`.

A recursive search found permitted history/report mentions and unavoidable protected `.env.example`/`MODEL_VERIFICATION.json` matches. Git metadata also records the requested branch and tag. These exceptions prevent a literal whole-tree search from matching only two documentation files while honoring the protected-file and history requirements.

## Remaining release risks

WebSocket audio/events remain unauthenticated and globally broadcast; REST calls require JWT and per-call read isolation is incomplete. Retention/deletion, backups, hosted TLS/network controls, real-model accuracy, microphone hardware, and CPU latency have not been validated. See [LIMITATIONS.md](../LIMITATIONS.md), [SECURITY.md](../SECURITY.md), and [TEST_PLAN.md](TEST_PLAN.md).
