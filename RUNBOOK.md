# Runbook

Source of truth: [BRAIN.md](BRAIN.md).

## Start the local application

1. Install Python dependencies with `python -m pip install -r requirements.txt`.
2. Set `AWAZRAKSHAK_MODEL_PATH` to an existing verified local model cache or snapshot. No runtime model download occurs.
3. For development, start `python -m uvicorn server.main:app --port 8000` from the repository root, then in a second terminal run `cd frontend`, `npm install`, and `npm run dev`. Set `VITE_USE_MOCK=false` for microphone mode.
4. For one-process local service, build with `npm run build` inside `frontend/`, return to root, then start the same Uvicorn command. It serves `frontend/dist/` at `/`.

## Common issues

- **Analysis disabled:** verify that the local path contains the pinned snapshot and all required files pass integrity verification.
- **No microphone:** use localhost or another secure browser context, grant microphone permission, and check the consent box.
- **No live events:** confirm that the API is running on port 8000 and Vite proxies `/ws` and `/health` to it.
- **Database routes fail:** apply `alembic upgrade head`, set a valid `JWT_SECRET_KEY`, and provision an operator account.

Raw call audio is held in memory only and discarded when the WebSocket disconnects. Emotion and priority values are advisory and uncalibrated.
