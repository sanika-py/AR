# Demo guide

Source of truth: [BRAIN.md](BRAIN.md). The dashboard defaults to synthetic mock data. For a live local microphone demo, configure a verified model snapshot and use the consent-gated live mode.

1. Start FastAPI from the repository root: `python -m uvicorn server.main:app --port 8000`.
2. In another terminal: `cd frontend`, `npm install`, set `$env:VITE_USE_MOCK = 'false'`, then run `npm run dev`.
3. Open the Vite URL, review the visible advisory disclaimer, check the consent box, and allow microphone access.
4. Confirm that live status and event values update. Stop capture to close the browser audio stream and WebSockets.

Demo queue entries and action controls are synthetic/local UI state. They do not represent real calls or perform external actions. Outputs are advisory and uncalibrated. Physical-device and pinned-model behavior depend on the local environment.
