"""Optional local faster-whisper transcription with ephemeral audio/text state."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

from backend.core.keywords import detect_keyword_hits, load_keyword_phrases
from config import (
    MODEL_SAMPLE_RATE,
    ASR_COMPUTE_TYPE,
    ASR_ENABLED,
    ASR_LANGUAGE,
    ASR_MODEL_PATH,
    ASR_MODEL_SIZE,
    ASR_UPDATE_INTERVAL_SECONDS,
    ASR_WINDOW_SECONDS,
    PROVISIONAL_ASR_MIN_AUDIO_SECONDS,
)


class LiveTranscriber:
    """Transcribe recent 16 kHz audio on a worker thread; clear it on stop."""

    def __init__(
        self,
        *,
        enabled: bool = ASR_ENABLED,
        model_path: str = ASR_MODEL_PATH,
        model_factory: Callable[[str], Any] | None = None,
        interval: float = ASR_UPDATE_INTERVAL_SECONDS,
    ) -> None:
        self.enabled = enabled
        self.model_path = model_path
        self.model_factory = model_factory or _load_whisper_model
        self.interval = interval
        self._capacity = int(ASR_WINDOW_SECONDS * MODEL_SAMPLE_RATE)
        self._audio = np.empty(0, dtype=np.float32)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._latest: dict[str, Any] | None = None
        self._error: str | None = None
        self._revision = 0
        self._last_processed = 0
        self._total_samples = 0

    def start(self) -> None:
        if not self.enabled:
            return
        self.stop()
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._worker, name="awazrakshak-local-asr", daemon=True
        )
        self._thread.start()

    def add_audio(self, samples: np.ndarray) -> None:
        if not self.enabled or self._stop.is_set():
            return
        source = np.asarray(samples)
        audio = source.astype(np.float32, copy=False)
        if audio.ndim != 1 or not audio.size or not np.isfinite(audio).all():
            raise ValueError("ASR audio must be a finite mono sample vector")
        # PCM16 chunks are normalized only for ASR. Keep at most the configured window.
        if np.issubdtype(source.dtype, np.integer):
            audio = audio / 32768.0
        with self._lock:
            self._audio = np.concatenate((self._audio, audio))[-self._capacity :]
            self._total_samples += len(audio)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "latest": self._latest.copy() if self._latest else None,
                "error": self._error,
                "revision": self._revision,
            }

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join()
        self._thread = None
        with self._lock:
            self._audio = np.empty(0, dtype=np.float32)
            self._latest = None
            self._error = None
            self._revision = 0
            self._total_samples = 0
            self._last_processed = 0

    def _worker(self) -> None:
        try:
            if not self.model_path or not Path(self.model_path).is_dir():
                raise RuntimeError(
                    f"ASR_MODEL_PATH must point to a locally available faster-whisper {ASR_MODEL_SIZE} model folder"
                )
            model = self.model_factory(self.model_path)
            phrases = load_keyword_phrases()
        except Exception as exc:
            with self._lock:
                self._error = f"ASR unavailable: {exc}"
            return

        minimum_samples = int(PROVISIONAL_ASR_MIN_AUDIO_SECONDS * MODEL_SAMPLE_RATE)
        next_run = time.monotonic() + self.interval
        while not self._stop.is_set():
            self._stop.wait(timeout=max(0.0, next_run - time.monotonic()))
            if self._stop.is_set():
                break
            next_run = time.monotonic() + self.interval
            with self._lock:
                total = self._total_samples
                if total == self._last_processed or len(self._audio) < minimum_samples:
                    continue
                audio = self._audio.copy()
                self._last_processed = total
            try:
                segments, info = model.transcribe(
                    audio,
                    language=ASR_LANGUAGE,
                    beam_size=1,
                    vad_filter=True,
                )
                text = " ".join(
                    segment.text.strip()
                    for segment in segments
                    if segment.text.strip()
                ).strip()
                if not text:
                    continue
                result = {
                    "text": text,
                    "language": getattr(info, "language", None),
                    "keyword_hits": detect_keyword_hits(text, phrases),
                }
                with self._lock:
                    if self._stop.is_set():
                        break
                    if result != self._latest:
                        self._latest = result
                        self._error = None
                        self._revision += 1
            except Exception as exc:
                with self._lock:
                    self._error = f"ASR transcription error: {exc}"


def _load_whisper_model(path: str) -> Any:
    """Load only the local small model; a model identifier is never accepted."""
    from faster_whisper import WhisperModel

    return WhisperModel(path, device="cpu", compute_type=ASR_COMPUTE_TYPE, cpu_threads=2)
