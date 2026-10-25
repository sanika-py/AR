# AwazRakshak frontend

Vite + React + TypeScript three-column mock officer dashboard with Tailwind CSS,
Zustand, and Vitest. The queue, waveform, transcript, and urgency values are synthetic
demo data when mock mode is enabled. Live audio uses the local backend when mock mode is disabled.

## Live microphone mode

Start the local FastAPI service from the repository root, with
`AWAZRAKSHAK_MODEL_PATH` pointing to the verified local model, using
`python -m backend.app`. Then, in this directory, set `VITE_USE_MOCK=false` and run
`npm run dev`. The Vite
development server proxies `/ws` and `/health` to `http://127.0.0.1:8000` by default.
Set `VITE_API_PROXY_TARGET` to proxy to another local API address, or set
`VITE_API_BASE_URL` when the API is served from a different origin. The browser
requires a secure context (localhost is allowed) and microphone permission. Recording
does not start until the consent checkbox is checked. The AudioWorklet sends mono
PCM16 chunks at 16 kHz, 100 ms per message; only short in-memory audio buffers are used.
Stop recording to close the microphone and both sockets.

Copy `.env.example` to `.env.local` to configure these values. `VITE_USE_MOCK=true`
keeps the synthetic dashboard enabled by default. The backend never downloads model
files at runtime; without the verified local model, the UI reports that analysis is
unavailable.

```powershell
npm install
npm run dev
```

`npm run build`, `npm run lint`, and `npm test` run the production build/type check, ESLint, and Vitest suite. `npm run test:e2e` runs the Playwright test with Chromium's fake microphone and a local WebSocket test server. All emotion outputs are advisory. Escalate, Flag for Review, and Transfer controls remain demo interactions only.
