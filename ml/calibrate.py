"""Fit one temperature on held-out logits and report expected calibration error."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

os.environ.setdefault("HF_HOME", "./.cache/hf")

import numpy as np
import torch

from config import EXPECTED_ID2LABEL


def read_logits(path: Path) -> tuple[np.ndarray, np.ndarray]:
    labels = [EXPECTED_ID2LABEL[i] for i in range(len(EXPECTED_ID2LABEL))]
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    columns = [f"logit_{label}" for label in labels]
    if not rows or "label" not in rows[0] or not set(columns).issubset(rows[0]):
        raise ValueError("CSV must contain label and logit_<configured-label> columns")
    label_ids = {label: idx for idx, label in enumerate(labels)}
    return (np.asarray([[float(r[c]) for c in columns] for r in rows], dtype=np.float64),
            np.asarray([label_ids[r["label"].strip().lower()] for r in rows], dtype=np.int64))


def expected_calibration_error(logits: np.ndarray, targets: np.ndarray, temperature: float, bins: int = 15) -> float:
    shifted = logits / temperature
    exp = np.exp(shifted - shifted.max(axis=1, keepdims=True))
    probs = exp / exp.sum(axis=1, keepdims=True)
    confidence, prediction = probs.max(axis=1), probs.argmax(axis=1)
    ece = 0.0
    for lower in np.linspace(0, 1, bins, endpoint=False):
        upper = lower + 1 / bins
        mask = (confidence >= lower) & ((confidence < upper) if upper < 1 else (confidence <= upper))
        if mask.any(): ece += float(mask.mean()) * abs(float((prediction[mask] == targets[mask]).mean()) - float(confidence[mask].mean()))
    return ece


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("heldout_logits_csv", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--bins", type=int, default=15)
    args = parser.parse_args()
    logits, targets = read_logits(args.heldout_logits_csv)
    if args.bins < 1: raise ValueError("bins must be positive")
    tensor, y = torch.tensor(logits), torch.tensor(targets)
    log_t = torch.zeros((), dtype=torch.float64, requires_grad=True)
    optimizer = torch.optim.LBFGS([log_t], lr=0.1, max_iter=100)
    def closure():
        optimizer.zero_grad()
        loss = torch.nn.functional.cross_entropy(tensor / log_t.exp(), y)
        loss.backward()
        return loss
    optimizer.step(closure)
    temperature = float(log_t.detach().exp().clamp(0.05, 20.0))
    result = {"temperature": temperature, "ece": expected_calibration_error(logits, targets, temperature, args.bins),
              "ece_bins": args.bins, "sample_count": int(len(targets)), "results_status": "measured on supplied held-out data"}
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote calibration results to {args.output_json}")


if __name__ == "__main__": main()
