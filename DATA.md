# Data Handling

Source of truth: [BRAIN.md](BRAIN.md). Current implementation details are summarized in [docs/AUDIT.md](docs/AUDIT.md).

## Data types and path

| Data | Current handling |
|---|---|
| Browser microphone frames | Received by the Streamlit host through WebRTC during an authorized recording. |
| Rolling audio | Downmixed and resampled by `live.py`; at most 30 seconds retained in process memory. |
| Analysis window | Latest 3 seconds at 16 kHz mono; considered every 1.5 seconds. Digital silence is skipped. |
| Model scores and quality flags | Held in the live pipeline's in-memory insight history while the call is active. |
| Call summary | Audio-free JSON written under `.awazrakshak-data/summaries/` and offered as a browser download. |
| Model files | Read from a user-provided local Hugging Face cache or snapshot; not downloaded at runtime. |

## Retention and access

The ring buffer is cleared when the pipeline stops. Summary JSON remains on local disk until the operator removes it; the application has no configured summary retention or deletion schedule. Summaries are not encrypted by the application and contain call timing, category/indicator peaks, quality flags, and model identity. Do not include caller names or identifiers in the current summary format.

The current local-processing posture assumes a trusted local host. If the app is hosted, browser audio crosses the network to that host. Hosted use is not equivalent to local-only processing and needs a documented access, transport, storage, and deletion policy before use.

## Planned data work

**Planned:** Define a versioned schema, retention/deletion controls, access controls, storage threat model, and consent/audit requirements before introducing a database or multi-user service. Any training corpus or feedback collection is also Planned and must not be inferred from the current application.
