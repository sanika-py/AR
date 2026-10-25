# Data

Source of truth: [BRAIN.md](BRAIN.md).

| Data | Runtime handling |
|---|---|
| Browser microphone audio | Captured only after consent and sent as mono PCM16 at 16 kHz to the FastAPI host. |
| Live audio buffer | Bounded to 30 seconds in process memory and cleared when the audio socket disconnects. |
| Emotion scores and indicators | Validated analysis events sent over `/ws/events`; no audio samples are included. |
| Optional transcript and keyword hits | In-memory snapshots only when local ASR is enabled; the stream is cleared on disconnect. |
| Persisted records | SQL database stores audio-free calls, summaries, flags, notes, and audit entries. |
| Offline training inputs | Explicit operator-supplied datasets; offline augmentation may write derived WAV files to the chosen destination. |

Live-call audio is never written to disk by the app. Database retention/deletion and hosted encryption are not configured. A remote deployment receives browser audio over the network; keep the service local unless that transfer is approved.
