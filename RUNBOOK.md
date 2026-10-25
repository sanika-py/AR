# Local Runbook

Source of truth: [BRAIN.md](BRAIN.md). This runbook applies to the current Streamlit application.

## Start the application

Use Python 3.12 and install the pinned project dependencies in a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Provide a locally available Hugging Face cache root or snapshot directory containing the pinned files `config.json`, `preprocessor_config.json`, and `model.safetensors`. The existing pin and integrity checks must pass. The checked-in `Models` directory alone is incomplete because the weights are not tracked. No model download occurs at runtime.

Run from the repository root:

```powershell
python -m streamlit run app.py
```

The UI's Local model path field accepts the cache root or snapshot folder. `AWAZRAKSHAK_MODEL_PATH` can provide the initial path through the process environment. `.env.example` is documentation only; the application does not load dotenv files itself.

## Operator flow

1. Confirm the model is shown as verified and analysis is available.
2. Check “I am authorised to record this call.”
3. Start recording and grant the browser microphone permission.
4. Observe the live raw label, derived indicators, attention category, quality flags, and trend. Treat all emotion outputs as advisory.
5. Stop recording to view and download the audio-free summary.

## Troubleshooting

- **Analysis disabled:** Check the selected local path, required files, pinned revision, configured labels, and expected hashes. A missing or mismatched artifact correctly keeps analysis disabled.
- **Microphone unavailable:** Check that `streamlit-webrtc` installed, browser microphone permission is granted, and the browser can access the host.
- **Low audio confidence:** Check microphone level and background conditions. Quality flags are heuristic; they do not certify the recording.
- **Summary not saved:** The app reports a save error when the summary directory is not writable. The in-page download may still be offered.
- **Stop takes time:** Inference runs in a worker; the current stop path waits up to two seconds for it before clearing the buffer. There is no measured stop-latency guarantee.

**Planned:** Add operational health checks, structured logs without audio, supported deployment procedures, and incident/backup guidance when a service backend is introduced.
