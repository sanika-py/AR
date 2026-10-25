"""Build deterministic speaker-independent train/validation/test manifests.

Input CSV columns: audio_path,label,speaker_id. Paths are resolved relative to the CSV.
Splits are by speaker; an indivisible speaker group can make class balance imperfect.
"""
from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path

from config import EXPECTED_ID2LABEL


def prepare(input_csv: Path, output_csv: Path, seed: int = 42) -> int:
    rng = random.Random(seed)
    source_root = input_csv.resolve().parent
    with input_csv.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    required = {"audio_path", "label", "speaker_id"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Input CSV must have audio_path,label,speaker_id columns and rows")
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        label = row["label"].strip().lower()
        speaker = row["speaker_id"].strip()
        path = (source_root / row["audio_path"]).resolve()
        if label not in EXPECTED_ID2LABEL.values() or not speaker or not path.is_file():
            raise ValueError(f"Invalid label, speaker_id, or missing audio file in row: {row}")
        groups[speaker].append({"audio_path": str(path), "label": label, "speaker_id": speaker})
    speakers = list(groups)
    if len(speakers) < 3:
        raise ValueError("At least three distinct speakers are required to populate all splits")
    rng.shuffle(speakers)
    n = len(speakers)
    train_count = max(1, int(n * 0.70))
    validation_count = max(1, int(n * 0.15))
    if train_count + validation_count >= n:
        train_count = n - 2
        validation_count = 1
    split_for = {
        **{speaker: "train" for speaker in speakers[:train_count]},
        **{speaker: "validation" for speaker in speakers[train_count:train_count + validation_count]},
        **{speaker: "test" for speaker in speakers[train_count + validation_count:]},
    }
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["audio_path", "label", "speaker_id", "split"])
        writer.writeheader()
        for speaker in speakers:
            for row in groups[speaker]:
                writer.writerow({**row, "split": split_for[speaker]})
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(f"Wrote speaker-independent manifest with {prepare(args.input_csv, args.output_csv, args.seed)} rows")


if __name__ == "__main__":
    main()
