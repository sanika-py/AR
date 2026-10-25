# Model Card

Source of truth: [BRAIN.md](BRAIN.md). This card describes the pinned model as used by the current repository and distinguishes repository checks from model evaluation.

## Identity and use

- **Model ID:** `Dpngtm/wav2vec2-emotion-recognition`
- **Pinned revision:** `033a5751a5bbe5b0b67c2c71e6102c38de35a346`
- **Runtime:** Transformers sequence classification on CPU, loaded from a local snapshot/cache.
- **Input:** Mono waveform resampled to 16 kHz; current live window is 3 seconds.
- **Output labels, configured index order:** `angry`, `calm`, `disgust`, `fearful`, `happy`, `sad`, `surprised`.

The application displays raw classifier scores and derives provisional distress and nervousness indicators. The intended role is advisory screening to support officer judgement. Outputs are not decisions about danger, deception, guilt, dispatch, or any person's actual internal emotional state.

## Verification and availability

`engine.py` requires local `config.json`, `preprocessor_config.json`, and `model.safetensors`, checks pinned identity/labels and expected hashes recorded in `MODEL_VERIFICATION.json`, disables remote code and network downloads, and runs a synthetic forward check when loading. The tracked repository has model configuration files but does not include the large weight file. The manifest currently records `human_approved: false`; runtime integrity checks do not convert that value into a human approval claim.

## Evaluation

The repository has synthetic/fake-model unit tests and integrity checks. It does not provide validated accuracy, calibration, demographic robustness, field effectiveness, or latency measurements for the pinned model. No such metrics are asserted here. See [EVALUATION.md](EVALUATION.md).

## Known concerns

Emotion recognition from voice is sensitive to language, culture, recording conditions, individual variation, and label definitions. The repository does not establish the model's training provenance or fitness for consequential use. `LICENSES.md` records unresolved dataset and derivative-weight rights. **Planned:** review model/data provenance, evaluate representative authorized data, document limitations and use constraints, and obtain any approvals required before deployment or redistribution.
