# Deployment

Source of truth: [BRAIN.md](BRAIN.md). The supported setup is local development or a production-style local FastAPI process serving the React build. This repository is not a hardened hosted deployment.

## Development

Install dependencies with `python -m pip install -r requirements.txt`, then start `python -m uvicorn server.main:app --port 8000` from the repository root. In a second terminal, run `cd frontend`, `npm install`, and `npm run dev`. Set `VITE_USE_MOCK=false` for microphone mode and point `AWAZRAKSHAK_MODEL_PATH` at an already-present verified model snapshot. Vite proxies `/health` and `/ws` to port 8000.

## Production-style local run

Run `npm install` and `npm run build` from `frontend/`, return to the root, then start `python -m uvicorn server.main:app --port 8000`. FastAPI serves `frontend/dist/` and the API from one origin. Model files must be provisioned locally; runtime downloads are disabled.

REST call/action routes require a JWT secret and operator accounts. Apply migrations with `alembic upgrade head` before using database routes. WebSocket routes remain unauthenticated and event subscribers are not session-isolated. Do not expose the service publicly without access controls, TLS, storage-retention policy, backups, and monitoring.
