"""Register a trained local checkpoint and write a separate v1 hash manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from config import EXPECTED_ID2LABEL, MODEL_ID, MODEL_REVISION


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()


def register(source: Path, repo_root: Path) -> Path:
    source = source.resolve(strict=True)
    destination = repo_root / "models" / "awazrakshak-v1"
    manifest_path = repo_root / "MODEL_VERIFICATION.v1.json"
    existing_pin = (repo_root / "Models").resolve()
    if destination.resolve() == existing_pin or existing_pin in destination.resolve().parents:
        raise ValueError("Refusing to write into the existing pinned model directory")
    if destination.exists(): raise FileExistsError(f"Refusing to overwrite registered model: {destination}")
    if manifest_path.exists(): raise FileExistsError(f"Refusing to overwrite {manifest_path}")
    required = ("config.json", "preprocessor_config.json", "model.safetensors")
    if any(not (source / name).is_file() for name in required):
        raise ValueError("Source must contain config.json, preprocessor_config.json, and model.safetensors")
    metadata = json.loads((source / "config.json").read_text(encoding="utf-8"))
    labels = {int(k): v for k, v in metadata.get("id2label", {}).items()}
    expected = dict(EXPECTED_ID2LABEL)
    if labels != expected: raise ValueError(f"Checkpoint labels do not match configured labels: {labels}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    files = {p.relative_to(destination).as_posix(): sha256(p) for p in sorted(destination.rglob("*")) if p.is_file()}
    manifest = {
        "schema_version": "1.0", "registered_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "registered_unvalidated", "model_id": "awazrakshak-v1",
        "base_model_id": MODEL_ID, "base_model_revision": MODEL_REVISION,
        "labels": {str(k): v for k, v in expected.items()}, "artifact_sha256": files,
        "metrics": {}, "metrics_status": "Not evaluated; no performance claims are made.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trained_checkpoint", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(f"Registered checkpoint at {register(args.trained_checkpoint, args.repo_root.resolve())}")


if __name__ == "__main__": main()
