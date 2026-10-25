# Security and Privacy

Source of truth: [BRAIN.md](BRAIN.md). The current application is intended for trusted local use; it is not an authenticated multi-user service.

## Current controls

- Model loading is local-only, pinned to a full revision, uses safetensors, disables remote code, and fails closed when required files or hashes do not match `MODEL_VERIFICATION.json`.
- Raw audio is processed in memory, held in a bounded ring buffer, and cleared when the live pipeline stops. The app does not write raw audio to disk.
- The saved summary contains no audio. It is stored as ordinary local JSON under `.awazrakshak-data/summaries/`; application-level encryption and automatic retention are not implemented.
- The Streamlit configuration binds to `127.0.0.1` by default. This is a local-host setting, not an authentication control.
- The user-facing workflow asks for authorization before enabling recording. That checkbox is not identity verification or proof of legal consent.

## Threats and limits

If exposed beyond localhost, the service can receive sensitive microphone audio from remote browsers. The current app does not implement authentication, role-based access, CSRF protections for a custom API, per-user isolation, rate limits, or remote deployment hardening. Summary files may be readable by local users with filesystem access. A worker may briefly retain a local window copy while inference is finishing after stop; the live ring buffer is cleared. Do not claim secure deletion of process memory.

Never commit model weights, secrets, caller data, or real call summaries. Do not edit `MODEL_VERIFICATION.json` or model weights as a shortcut around verification.

## Planned security work

**Planned:** Before a hosted service is enabled, threat-model audio transport and storage; define authentication and authorization; isolate sessions; set network and resource limits; specify summary retention/deletion and access; review dependency and model provenance; and document incident handling. These controls are not present today.
