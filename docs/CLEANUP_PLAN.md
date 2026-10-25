# Streamlit cleanup plan

Classification is based on tracked-file inventory, repository-wide `streamlit` searches, and Python import references. The frontend's existing `/health`, `/ws/audio`, and `/ws/events` contracts are implemented by `backend/app.py`; therefore a separate inference backend is not needed. `server/main.py` now provides the requested production command and serves `frontend/dist/` while reusing that API unchanged.

## KEEP

Each tracked file is listed individually; directories are listed separately below.

| File | One-line reason |
|---|---|
| `.dockerignore` | Keeps local data, caches, and generated assets out of container contexts. |
| `.env.example` | Protected reference for environment configuration. |
| `.github/workflows/ci.yml` | Runs backend and frontend CI checks. |
| `.gitignore` | Protects secrets, models, local data, and build artifacts from Git. |
| `.pre-commit-config.yaml` | Configures repository formatting and lint hooks. |
| `AGENTS.md` | Defines safety and contributor rules. |
| `alembic.ini` | Configures the kept database migrations. |
| `API.md` | Documents the contracts consumed by the frontend. |
| `ARCHITECTURE.md` | Documents the system structure; update its stale UI description. |
| `BRAIN.md` | Maintains the project source of truth; update its stale UI description. |
| `CHANGELOG.md` | Retains history and may document removed UI files. |
| `CONTRIBUTING.md` | Documents development and review practices. |
| `DATA.md` | Documents the API's audio-free persistence and transient audio flow. |
| `DATA_DICTIONARY.md` | Documents persisted records and payloads. |
| `DECISIONS.md` | Retains architecture decisions; supersede the old dual-UI decision. |
| `DEMO_GUIDE.md` | Documents the current React demo. |
| `DEPLOYMENT.md` | Documents deployment; update its old launch commands. |
| `Dockerfile.backend` | Packages the kept API. |
| `Dockerfile.frontend` | Packages the React static UI. |
| `EVALUATION.md` | Documents model evaluation and CPU limitations. |
| `LICENSES.md` | Protected third-party license notices. |
| `LIMITATIONS.md` | Documents model and runtime limitations. |
| `MODEL_CARD.md` | Documents the pinned model and advisory use. |
| `MODEL_VERIFICATION.json` | Protected model integrity evidence; never edit or remove. |
| `PROMPTS.md` | Documents approved advisory guidance templates. |
| `README.md` | Main operator setup and run guide; rewrite for the React/FastAPI app. |
| `RUNBOOK.md` | Operations guide; update its old UI launch instructions. |
| `SCHEMA.md` | Documents kept SQL tables. |
| `SECURITY.md` | Documents current local processing and API security. |
| `TASKS.md` | Tracks planned and completed migration work. |
| `TODO.md` | Tracks remaining work. |
| `backend/__init__.py` | Makes the existing API an importable Python package. |
| `backend/app.py` | Implements the frontend's health and WebSocket API plus storage routes. |
| `backend/auth.py` | Implements authentication used by the REST API. |
| `backend/cli.py` | Provisions local API operators. |
| `backend/core/__init__.py` | Makes reusable inference logic importable. |
| `backend/core/asr.py` | Provides optional local transcription logic. |
| `backend/core/engine.py` | Implements pinned model loading and inference validation. |
| `backend/core/keywords.py` | Implements local transcript keyword matching. |
| `backend/core/keywords.yaml` | Supplies the configured keyword phrases. |
| `backend/core/priority.py` | Calculates provisional advisory priority. |
| `backend/core/signals.py` | Implements indicators, smoothing, and category logic. |
| `backend/database.py` | Connects the kept REST API to local SQL persistence. |
| `backend/events.py` | Broadcasts analysis events to WebSocket subscribers. |
| `backend/models.py` | Defines the kept audio-free SQL records. |
| `backend/routes.py` | Implements protected summary and officer-action endpoints. |
| `backend/schemas.py` | Defines API and WebSocket payload validation. |
| `backend/startup_check.py` | Fails startup checks when the pinned model is unavailable or invalid. |
| `config.py` | Protected model, timing, and indicator constants. |
| `docker-compose.yml` | Defines the local/demo service topology. |
| `docker/nginx.conf` | Configures the existing optional reverse proxy. |
| `docs/AUDIT.md` | Retains the repository audit; mark old UI observations historical. |
| `docs/CLEANUP_PLAN.md` | Records this file-by-file decision and import evidence. |
| `docs/RELEASE_CHECKLIST.md` | Retains security/product release evidence. |
| `docs/REMOVAL_MAP.md` | Retains the earlier discovery artifact; reduce to a link to this final plan. |
| `docs/TEST_PLAN.md` | Documents kept automated and manual test coverage. |
| `docs/ui/UI_SPEC.md` | Retains the design tokens used by the React UI. |
| `engine.py` | Compatibility exports used by the API and protected tests. |
| `frontend/.env.example` | Documents frontend API/mock settings. |
| `frontend/.prettierignore` | Configures frontend formatter exclusions. |
| `frontend/.prettierrc.json` | Configures frontend formatting. |
| `frontend/README.md` | Documents frontend setup and live mode. |
| `frontend/e2e/dashboard.spec.ts` | Tests dashboard interactions. |
| `frontend/e2e/fakeBackend.mjs` | Supplies the local fake WebSocket service for E2E tests. |
| `frontend/e2e/microphone.spec.ts` | Tests browser microphone streaming. |
| `frontend/eslint.config.js` | Configures frontend linting. |
| `frontend/index.html` | Vite HTML entry point. |
| `frontend/package-lock.json` | Locks frontend dependencies. |
| `frontend/package.json` | Defines frontend runtime and scripts. |
| `frontend/playwright.config.ts` | Configures browser tests. |
| `frontend/public/pcm16-worklet.js` | Captures and encodes microphone audio in-browser. |
| `frontend/src/App.test.tsx` | Tests key dashboard behavior. |
| `frontend/src/App.tsx` | Renders the React interface. |
| `frontend/src/Charts.tsx` | Renders live chart components. |
| `frontend/src/env.d.ts` | Types frontend environment values. |
| `frontend/src/liveAudio.ts` | Manages microphone worklet capture. |
| `frontend/src/main.tsx` | Boots the React application. |
| `frontend/src/mockData.ts` | Provides the frontend's demo-mode data. |
| `frontend/src/store.test.ts` | Tests the frontend event store. |
| `frontend/src/store.ts` | Holds frontend event state. |
| `frontend/src/styles.css` | Defines the calm UI styles and tokens. |
| `frontend/src/types.test.ts` | Tests the typed backend event contract. |
| `frontend/src/types.ts` | Defines frontend API event types and validation. |
| `frontend/src/useLiveAudio.ts` | Connects microphone capture to backend WebSockets. |
| `frontend/tsconfig.json` | Configures TypeScript compilation. |
| `frontend/vite.config.ts` | Configures Vite, Tailwind, tests, and backend proxies. |
| `live.py` | The API and `tests/test_live.py` import its bounded in-memory pipeline. |
| `load/audio_streams.js` | Implements the retained k6 audio-stream load scenario. |
| `migrations/env.py` | Loads the kept SQLAlchemy metadata for Alembic. |
| `migrations/script.py.mako` | Templates kept Alembic revisions. |
| `migrations/versions/0001_initial_storage.py` | Creates the kept audio-free database schema. |
| `ml/README.md` | Documents offline ML tools. |
| `ml/__init__.py` | Defines the offline ML package. |
| `ml/augment.py` | Implements explicit offline dataset augmentation. |
| `ml/calibrate.py` | Implements offline calibration. |
| `ml/evaluate.py` | Implements offline evaluation. |
| `ml/export_onnx.py` | Implements offline model export. |
| `ml/prepare_data.py` | Implements explicit offline dataset preparation. |
| `ml/register.py` | Implements separate offline model registration. |
| `ml/train.py` | Implements offline training. |
| `pyproject.toml` | Configures Python tooling. |
| `pytest.ini` | Configures the kept pytest suite. |
| `requirements-asr.txt` | Holds optional local ASR dependencies. |
| `signals.py` | Compatibility exports imported by the live pipeline and protected tests. |
| `server/__init__.py` | Makes the production ASGI entry point package importable. |
| `server/main.py` | Serves the existing FastAPI API and built React assets without changing inference logic. |
| `tests/test_api_contract.py` | Tests the existing API event contract. |
| `tests/test_backend_api.py` | Tests backend endpoints and WebSocket behavior. |
| `tests/test_engine_synthetic.py` | Tests score validation with synthetic data. |
| `tests/test_live.py` | Tests live in-memory buffering and pipeline behavior. |
| `tests/test_model_path.py` | Tests local model-path and integrity behavior. |
| `tests/test_priority.py` | Tests the provisional priority calculations. |
| `tests/test_qa_unit.py` | Tests signals and priority helpers. |
| `tests/test_signals.py` | Tests indicator, smoothing, and category behavior. |
| `tests/test_startup_check.py` | Tests fail-closed model startup verification. |
| `tests/test_storage_api.py` | Tests protected audio-free storage endpoints. |

## SPLIT

| File | One-line reason and action |
|---|---|
| `requirements.txt` | Mixes UI-only packages with API/model/test dependencies; remove only the two UI packages and pin the required FastAPI server packages. |

## REMOVE

| File/folder | One-line reason |
|---|---|
| `app.py` | The sole old UI entry point; reusable model, live-buffer, and signal logic already exists in kept modules. |
| `.streamlit/config.toml` | Legacy UI theme and server configuration; no kept code imports it. |

## Directories

| Directory | Group | One-line evidence |
|---|---|---|
| `.github/` | KEEP | Contains the active CI workflow. |
| `.streamlit/` | REMOVE | Contains only configuration for the retired interface. |
| `backend/` | KEEP | Contains the FastAPI and core packages used by the frontend/tests. |
| `backend/core/` | KEEP | Contains model-independent and model-backed reusable analysis logic. |
| `docker/` | KEEP | Contains the current optional proxy configuration. |
| `docs/` | KEEP | Contains project and migration documentation. |
| `docs/ui/` | KEEP | Contains the source design specification for React. |
| `frontend/` | KEEP | Contains the replacement application and its tests. |
| `frontend/e2e/` | KEEP | Contains browser E2E tests. |
| `frontend/public/` | KEEP | Contains the microphone AudioWorklet. |
| `frontend/src/` | KEEP | Contains the React application and unit tests. |
| `load/` | KEEP | Contains the load-test script. |
| `migrations/` | KEEP | Contains the database migration environment and templates. |
| `migrations/versions/` | KEEP | Contains the current schema migration. |
| `ml/` | KEEP | Contains manually invoked offline model tools. |
| `Models/` | KEEP | Contains protected local model metadata; model weights are never changed. |
| `server/` | KEEP | Contains the production ASGI entry point for the API and built React assets. |
| `tests/` | KEEP | Contains required model, signal, API, and storage tests. |

## Protected local/ignored directories

`.venv/`, `frontend/node_modules/`, `frontend/dist/`, `__pycache__/`, `.pytest_cache/`, and `.awazrakshak-data/` are not tracked source files. Keep the environment and frontend dependencies for verification, the existing build output until rebuilt, test cache as local tooling, and operator summary data. None is a Streamlit-only source directory.

## SPLIT

| Path | Change after this inventory |
|---|---|
| `requirements.txt` | Remove only `streamlit` and `streamlit-webrtc`; retain the libraries imported by the FastAPI runtime and tests. |
| `README.md` | Replace the legacy UI setup with the FastAPI and Vite dev commands and the single-process production command. |
| `backend/app.py` | No behavior extraction is needed: it already imports `engine.py` and `live.py` reusable logic and serves the frontend's current HTTP/WebSocket API contract. Add only production static serving in the new ASGI entry point. |
| `app.py` | Contains Streamlit rendering and WebRTC adapter code. Its reusable model/inference/windowing/signals are already in `engine.py`, `live.py`, and `signals.py`, all imported by the backend or kept tests, so none need to be extracted from this UI file. |
| Documentation listed under KEEP | Replace current-operation instructions and architecture descriptions with the React/FastAPI-only state; retain the Streamlit removal history only in `CHANGELOG.md` and this plan. |

## REMOVE

| Path | Evidence / reason |
|---|---|
| `app.py` | Only file importing Streamlit and `streamlit_webrtc`; no KEEP runtime or test imports it. |
| `.streamlit/` (`config.toml`) | Server/theme configuration used only by the deleted Streamlit UI. |

## Search constraint

The requested whole-tree `grep -ri streamlit .` allowance conflicts with explicit protection rules: `.env.example` contains a comment mentioning Streamlit, and `MODEL_VERIFICATION.json` records the package version in its verification environment. Neither can be edited. The requested tag/branch and Git history also contain the term; the retained `.venv/` has installed package metadata. These are not tracked UI source files, and changing them would violate the keep/history requirements. PowerShell has no `grep` executable in this environment; the available `rg -n -i --hidden 'streamlit' .` search reported `CHANGELOG.md`, this plan, the two protected files, and `.git` metadata (including the requested branch). A source/docs-only scan excluding protected examples, verification evidence, and generated/environment/history directories reported only `CHANGELOG.md` and this plan.

## Execution and verification

- Created `pre-cleanup` at the starting commit and switched to `cleanup-streamlit` before changes.
- Classified all tracked source files and folders above before deletion. The reusable pipeline remained in `live.py`; no code extraction was necessary. `requirements.txt` was split to remove the two UI-only packages.
- Removed `app.py` and `.streamlit/config.toml` using `git rm`.
- Existing `backend/app.py` already implements the exact `/health`, `/ws/audio`, and `/ws/events` paths expected by the frontend and has an authenticated audio-free summary endpoint. Added `server/main.py` as the production entry point to serve the React build and reuse that API.
- Fresh Python 3.12 `pip install -r requirements.txt`: completed successfully.
- `python -m pytest -v`: 62 passed.
- `npm install`: completed; npm emitted an install-script approval warning for esbuild.
- `npm run build`: passed; `npm test`: 10 passed.
- Uvicorn `/health` and `/` returned HTTP 200 on port 8017. Port 8000 was occupied during the runtime verification attempt.
- `MODEL_VERIFICATION.json` is unchanged from `pre-cleanup`; model metadata/weights and `config.py` constants were not edited.

## Existing ignored local directories

`.venv/`, `frontend/node_modules/`, `frontend/dist/`, `__pycache__/`, `.pytest_cache/`, and `.awazrakshak-data/` are local environment, build/cache, or operator data directories, not tracked application sources. They are retained: deleting them is unnecessary for Streamlit removal, and `.awazrakshak-data/` may contain saved audio-free records. The app does not persist live-call audio.
