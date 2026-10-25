"""Report macro-F1, per-class recall, and a confusion matrix from held-out logits."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from config import EXPECTED_ID2LABEL
from ml.calibrate import read_logits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("heldout_logits_csv", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--temperature", type=float, default=1.0)
    args = parser.parse_args()
    if args.temperature <= 0: raise ValueError("temperature must be positive")
    logits, targets = read_logits(args.heldout_logits_csv)
    prediction = (logits / args.temperature).argmax(axis=1)
    size = len(EXPECTED_ID2LABEL)
    matrix = np.zeros((size, size), dtype=np.int64)
    np.add.at(matrix, (targets, prediction), 1)
    recalls, f1s = [], []
    for i in range(size):
        tp, support, predicted = int(matrix[i, i]), int(matrix[i].sum()), int(matrix[:, i].sum())
        recall = tp / support if support else 0.0
        precision = tp / predicted if predicted else 0.0
        recalls.append(recall)
        f1s.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    labels = [EXPECTED_ID2LABEL[i] for i in range(size)]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = {"macro_f1": float(np.mean(f1s)), "per_class_recall": dict(zip(labels, recalls)),
              "class_support": dict(zip(labels, matrix.sum(axis=1).astype(int).tolist())),
              "temperature": args.temperature, "sample_count": int(len(targets))}
    (args.output_dir / "metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (args.output_dir / "confusion_matrix.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream); writer.writerow(["true_label", *labels])
        for label, row in zip(labels, matrix, strict=True): writer.writerow([label, *row.tolist()])
    print(f"Wrote held-out evaluation to {args.output_dir}")


if __name__ == "__main__": main()
