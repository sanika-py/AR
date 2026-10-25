# Demo Guide

Source of truth: [BRAIN.md](BRAIN.md). This guide uses the current live Streamlit workflow.

## Before the demo

- Use Python 3.12 with dependencies from `requirements.txt`.
- Provision a local snapshot of the pinned model with its config, preprocessor config, and safetensors weights. Verify that the app reports the model as available. The tracked `Models` folder does not contain the weights.
- Use an authorized microphone and a quiet setting. Do not use a real call unless recording is authorized.
- Run `python -m streamlit run app.py` and open the local app.

## Demonstrate the flow

1. Point out the advisory disclaimer and “I am authorised to record this call” consent control.
2. Enter/select the local model path and confirm the pinned model verification message.
3. Check consent, start recording, and allow microphone access.
4. Speak naturally for several seconds. Show the top raw model label and seven scores, the two derived indicators, quality warnings, category, and trend as they update.
5. Stop and show the duration, analyzed-window count, peak indicators, quality flags, and model identity in the summary.
6. Download the audio-free JSON summary and confirm it contains no audio.

Do not present the scores as truth about emotion, danger, deception, guilt, or dispatch. Do not claim accuracy or sub-two-second latency: the repository contains no such measured results. Synthetic unit tests are not a live-call demo.

**Planned:** A repeatable demo environment with an approved model artifact and a synthetic/mocked interface mode. No call simulator or prepared audio fixture is currently included.
