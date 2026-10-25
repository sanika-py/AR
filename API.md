# API

Source of truth: [BRAIN.md](BRAIN.md). The current application has no HTTP API.

## Current interface

The supported current entry point is the Streamlit page started with `streamlit run app.py`. The browser sends microphone frames through the `streamlit-webrtc` component. Streamlit session state owns the live pipeline and summary. There are no FastAPI routes, REST endpoints, WebSocket protocol, or public client contract in this repository.

## Planned service interface

**Planned:** A FastAPI service may expose health and verified-model status, create and stop an authorized live session, accept/stream audio frames, publish live insight events, and return an audio-free summary. The route names, authentication, transport, payloads, error behavior, concurrency policy, and versioning are not yet defined. The shapes in [SCHEMA.md](SCHEMA.md) describe current internal dictionaries and should not be assumed as API specifications.

Until those contracts are implemented and reviewed, clients must use the current Streamlit application rather than relying on proposed endpoints.
