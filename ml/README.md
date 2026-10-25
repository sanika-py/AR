# Offline ML workflow

This package contains optional, offline-only dataset preparation, training, calibration, evaluation, export, and registration tools. Model outputs are advisory and are not validated operational judgments. No raw audio is used by the live application from these scripts; dataset audio is read only when an operator explicitly runs these local commands. Keep datasets and generated audio out of public repositories.

Use Python 3.12 in the repository environment. Install the core requirements plus the optional `soundfile` and `soxr` packages (already in the project requirements), and install `onnx`, `onnxruntime`, and any training dependencies needed by the selected Transformers/PyTorch versions for export. Commands run on CPU. Set the Hugging Face cache location for every command that uses Transformers:

```powershell
$env:HF_HOME = "./.cache/hf"
```

No command downloads a model. Supply a local checkpoint directory. `train.py` expects a local compatible audio classifier; it saves a new fine-tuned checkpoint. It does not alter the checked-in `Models/` pinned artifact. Run all commands from the repository root.

## 1. Prepare speaker-independent splits

Create an input CSV with `audio_path,label,speaker_id`; audio paths are relative to that CSV. Labels must be the seven configured labels: angry, calm, disgust, fearful, happy, sad, surprised. At least three distinct speakers are required. A speaker appears in exactly one split. Approximate 70/15/15 speaker group proportions are deterministic for a given seed; class balance can vary because speakers are indivisible.

```powershell
python -m ml.prepare_data data/labels.csv data/manifest.csv --seed 42
```

The output `manifest.csv` contains absolute audio path, label, speaker ID, and `train`, `validation`, or `test` split.

## 2. Create telephony augmentation copies

The augment step converts each input to mono, simulates 8 kHz telephone bandwidth, applies mu-law encode/decode, adds seeded Gaussian noise at the selected SNR, then writes 16 kHz WAV copies and a new manifest. It leaves original files unchanged. Run augmentation on training rows only if augmented samples should not enter evaluation splits.

```powershell
python -m ml.augment data/train_manifest.csv data/augmented --seed 42 --snr-db 25
```

## 3. Fine-tune in two stages

Stage 1 freezes the Wav2Vec2 encoder and trains the classifier head. Stage 2 unfreezes the configured top encoder layers and trains them with a learning rate of `1e-5`. Both stages use the manifest's training and validation speakers and save to the requested output directory.

```powershell
$env:HF_HOME = "./.cache/hf"
python -m ml.train data/manifest.csv /local/model/checkpoint ./artifacts/awazrakshak-train --top-layers 2
```

## 4. Calibrate confidence scores

First produce logits on the held-out validation set in a CSV with `label` and one `logit_<label>` column for each configured label. Temperature fitting uses only this supplied set; expected calibration error is reported with 15 bins by default.

```powershell
$env:HF_HOME = "./.cache/hf"
python -m ml.calibrate artifacts/validation_logits.csv artifacts/calibration.json --bins 15
```

## 5. Evaluate held-out scores

Use logits from speakers assigned to the `test` split. The output contains macro-F1, per-class recall and support, and a labelled confusion matrix. An optional temperature can be applied before selecting the predicted class.

```powershell
$env:HF_HOME = "./.cache/hf"
python -m ml.evaluate artifacts/test_logits.csv artifacts/evaluation --temperature 1.0
```

## 6. Export ONNX

Export from a local trained checkpoint. Add `--int8` to run ONNX Runtime dynamic weight quantization. Exported models require separate compatibility and parity evaluation before use.

```powershell
$env:HF_HOME = "./.cache/hf"
python -m ml.export_onnx ./artifacts/awazrakshak-train ./artifacts/awazrakshak.onnx --int8
```

## 7. Register a separate v1 artifact

Registration copies a local checkpoint to `models/awazrakshak-v1/` and creates `MODEL_VERIFICATION.v1.json` with SHA-256 hashes for the copied files. It refuses to overwrite either destination. The manifest is explicitly `registered_unvalidated`; it does not replace `MODEL_VERIFICATION.json`, change the pinned `Models/` artifact, or establish that the trained model is approved for live use.

```powershell
python -m ml.register ./artifacts/awazrakshak-train
```

## Results template

No training, calibration, evaluation, or export results have been produced for this repository task. Record measured values only after running the workflow on a documented, speaker-independent dataset.

```text
Dataset/version:
Split manifest and seed:
Training checkpoint/source:
Calibration set and temperature:
Test macro-F1:
Per-class recall:
ECE and bin count:
Confusion matrix path:
ONNX/int8 parity check:
Operator review/status:
```
