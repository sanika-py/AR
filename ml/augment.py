"""Create offline telephony-augmented WAV copies (never modifies source audio)."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import soundfile as sf
import soxr


def mulaw_encode_decode(samples: np.ndarray, mu: int = 255) -> np.ndarray:
    compressed = np.sign(samples) * np.log1p(mu * np.abs(samples)) / np.log1p(mu)
    quantized = np.round((compressed + 1) * 127.5) / 127.5 - 1
    return np.sign(quantized) * np.expm1(np.abs(quantized) * np.log1p(mu)) / mu


def simulate_telephony(samples: np.ndarray, sample_rate: int, rng: np.random.Generator,
                       noise_snr_db: float = 25.0) -> np.ndarray:
    mono = samples.mean(axis=1) if samples.ndim == 2 else samples
    telephone = soxr.resample(mono.astype(np.float32), sample_rate, 8000)
    telephone = soxr.resample(telephone, 8000, 16000)
    telephone = mulaw_encode_decode(telephone)
    signal_rms = float(np.sqrt(np.mean(telephone ** 2)))
    noise_rms = signal_rms / (10 ** (noise_snr_db / 20))
    noise = rng.normal(0.0, noise_rms, telephone.shape).astype(np.float32)
    return np.clip(telephone + noise, -1, 1).astype(np.float32)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--snr-db", type=float, default=25.0)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    with args.manifest.open(newline="", encoding="utf-8") as src:
        rows = list(csv.DictReader(src))
    augmented = []
    for index, row in enumerate(rows):
        signal, rate = sf.read(row["audio_path"], dtype="float32", always_2d=False)
        result = simulate_telephony(signal, rate, rng, args.snr_db)
        target = args.output_dir / f"{index:08d}_telephone.wav"
        sf.write(target, result, 16000)
        augmented.append({**row, "audio_path": str(target.resolve()), "augmentation": "8k_mulaw_noise"})
    target_manifest = args.output_dir / "augmented_manifest.csv"
    with target_manifest.open("w", newline="", encoding="utf-8") as dst:
        writer = csv.DictWriter(dst, fieldnames=[*rows[0].keys(), "augmentation"])
        writer.writeheader()
        writer.writerows(augmented)
    print(f"Wrote {len(augmented)} augmented WAV files and {target_manifest}")


if __name__ == "__main__":
    main()
