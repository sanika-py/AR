# Deployment

Source of truth: [BRAIN.md](BRAIN.md). The only implemented deployment target is a local Streamlit process.

## Current local operation

The Streamlit configuration binds to `127.0.0.1`. Start the app with `python -m streamlit run app.py` after installing `requirements.txt` and providing a verified local model snapshot. The large weight file is not tracked in this repository. Runtime model downloads are disabled, so deployments must provision the model separately through an approved local process and preserve the pin/hash checks.

## Hosting considerations

The current workflow captures microphone audio in a browser and sends frames to the Streamlit host. Hosting the app remotely therefore transmits call audio to that host. The current local-processing privacy assumption no longer applies. The application has no authentication, session isolation, configurable retention, or hosted-service security controls. Do not expose it as a multi-user production service on the basis of the localhost configuration.

The repository has no FastAPI application, React client, container/service manifest, deployment pipeline, or production hosting configuration.

## Planned deployment

**Planned:** Design and review a FastAPI + React/Tailwind deployment, including authentication, TLS and network boundaries, audio transport, per-session isolation, CPU/resource limits, model provisioning, summary storage and deletion, observability, and rollback. Deployment procedures and hosting claims should be updated only after those components exist and are verified.
