# AwazRakshak

AwazRakshak is a local React + Tailwind call dashboard backed by FastAPI. The browser captures microphone audio only after the officer confirms consent. It streams 16 kHz mono PCM16 to the local API, which runs the pinned model and keeps raw audio in a bounded in-memory buffer only. Emotion scores, derived indicators, and attention bands are advisory and uncalibrated.

## Setup

Use Python 3.12 and Node.js 20 or newer. In PowerShell, from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The model must already exist locally and pass the repository's pin and file-integrity checks. Point `AWAZRAKSHAK_MODEL_PATH` at the Hugging Face cache root or the snapshot directory containing `config.json`, `preprocessor_config.json`, and `model.safetensors`:

```powershell
$env:AWAZRAKSHAK_MODEL_PATH = 'C:\path\to\verified\snapshot'
```

The app does not download model files at runtime.

## Development

Open two PowerShell terminals at the repository root.

Terminal 1, backend:

```powershell
.\.venv\Scripts\Activate.ps1
$env:AWAZRAKSHAK_MODEL_PATH = 'C:\path\to\verified\snapshot'
python -m uvicorn server.main:app --port 8000
```

Terminal 2, frontend:

```powershell
cd frontend
npm install
$env:VITE_USE_MOCK = 'false'
npm run dev
```

Open the Vite URL printed in the frontend terminal (normally `http://localhost:5173`). Its `/health` and WebSocket proxy targets the local API at port 8000. For mock dashboard mode, omit `VITE_USE_MOCK` or set it to `true`.

## Production-style local run

Build the frontend, return to the repository root, set the verified model path, then run one FastAPI process:

```powershell
cd frontend
npm install
npm run build
cd ..
$env:AWAZRAKSHAK_MODEL_PATH = 'C:\path\to\verified\snapshot'
python -m uvicorn server.main:app --port 8000
```

FastAPI serves `frontend/dist/` at `/` and serves the health, WebSocket, and API routes from the same origin. Open `http://127.0.0.1:8000`.

## Verification

```powershell
python -m pytest -v
cd frontend
npm install
npm run build
npm test
```

The summary REST endpoint stores only validated audio-free summary fields and requires an authenticated officer token. Current React action controls remain demo interactions. See [API.md](API.md), [SECURITY.md](SECURITY.md), and [LIMITATIONS.md](LIMITATIONS.md).
