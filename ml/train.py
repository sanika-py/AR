"""Two-stage CPU fine-tuning from a local, verified-compatible checkpoint."""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

os.environ.setdefault("HF_HOME", "./.cache/hf")

import soundfile as sf
import torch
from torch.utils.data import Dataset
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification, Trainer, TrainingArguments

from config import EXPECTED_ID2LABEL, MODEL_SAMPLE_RATE


class ManifestDataset(Dataset):
    def __init__(self, rows: list[dict[str, str]], extractor):
        self.rows, self.extractor = rows, extractor
        self.label_ids = {label: idx for idx, label in EXPECTED_ID2LABEL.items()}

    def __len__(self): return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        audio, rate = sf.read(row["audio_path"], dtype="float32", always_2d=False)
        if audio.ndim == 2: audio = audio.mean(axis=1)
        if rate != MODEL_SAMPLE_RATE:
            import soxr
            audio = soxr.resample(audio, rate, MODEL_SAMPLE_RATE)
        encoded = self.extractor(audio, sampling_rate=MODEL_SAMPLE_RATE, return_tensors="pt")
        return {"input_values": encoded.input_values.squeeze(0), "labels": torch.tensor(self.label_ids[row["label"]])}


class AudioCollator:
    def __init__(self, extractor): self.extractor = extractor

    def __call__(self, features):
        inputs = self.extractor.pad(
            [{"input_values": item["input_values"]} for item in features],
            padding=True, return_tensors="pt",
        )
        inputs["labels"] = torch.stack([item["labels"] for item in features])
        return inputs


def load_rows(path: Path, split: str) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = [r for r in csv.DictReader(stream) if r["split"] == split]
    if not rows: raise ValueError(f"Manifest has no {split} rows")
    return rows


def freeze_encoder(model) -> None:
    encoder = model.wav2vec2
    for parameter in encoder.parameters(): parameter.requires_grad = False
    for parameter in model.projector.parameters(): parameter.requires_grad = True
    for parameter in model.classifier.parameters(): parameter.requires_grad = True


def unfreeze_top_layers(model, count: int) -> None:
    layers = model.wav2vec2.encoder.layers
    if count < 1 or count > len(layers): raise ValueError(f"top layers must be between 1 and {len(layers)}")
    for layer in layers[-count:]:
        for parameter in layer.parameters(): parameter.requires_grad = True
    for parameter in model.wav2vec2.encoder.layer_norm.parameters(): parameter.requires_grad = True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("local_model", type=Path, help="Local checkpoint directory; no download is attempted")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--epochs-stage1", type=float, default=2)
    parser.add_argument("--epochs-stage2", type=float, default=2)
    parser.add_argument("--top-layers", type=int, default=2)
    args = parser.parse_args()
    if not args.local_model.is_dir(): raise FileNotFoundError("Provide a local model directory; runtime downloads are disabled")
    torch.set_num_threads(max(1, (os.cpu_count() or 2) - 1))
    extractor = AutoFeatureExtractor.from_pretrained(args.local_model, local_files_only=True)
    model = AutoModelForAudioClassification.from_pretrained(args.local_model, local_files_only=True, use_safetensors=True)
    labels = [EXPECTED_ID2LABEL[i] for i in range(len(EXPECTED_ID2LABEL))]
    model.config.id2label = dict(enumerate(labels)); model.config.label2id = {v: k for k, v in model.config.id2label.items()}
    train = ManifestDataset(load_rows(args.manifest, "train"), extractor)
    validation = ManifestDataset(load_rows(args.manifest, "validation"), extractor)
    collator = AudioCollator(extractor)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    common = dict(output_dir=str(args.output_dir), learning_rate=1e-5, per_device_train_batch_size=2,
                  per_device_eval_batch_size=2, eval_strategy="epoch", save_strategy="epoch",
                  logging_strategy="epoch", report_to=[], use_cpu=True, remove_unused_columns=False)
    freeze_encoder(model)
    Trainer(model=model, args=TrainingArguments(**common, num_train_epochs=args.epochs_stage1),
            train_dataset=train, eval_dataset=validation, data_collator=collator).train()
    unfreeze_top_layers(model, args.top_layers)
    Trainer(model=model, args=TrainingArguments(**common, num_train_epochs=args.epochs_stage2),
            train_dataset=train, eval_dataset=validation, data_collator=collator).train()
    model.save_pretrained(args.output_dir, safe_serialization=True)
    extractor.save_pretrained(args.output_dir)
    print(f"Saved fine-tuned checkpoint to {args.output_dir}; evaluate before any use")


if __name__ == "__main__": main()
