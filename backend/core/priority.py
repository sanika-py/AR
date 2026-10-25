"""Deterministic, provisional priority guidance from advisory indicators."""

from __future__ import annotations

import math
from dataclasses import dataclass
from collections.abc import Iterable

from config import (
    PROVISIONAL_PRIORITY_INDICATOR_THRESHOLDS,
    PROVISIONAL_PRIORITY_INDICATOR_URGENCY_MAX,
    PROVISIONAL_PRIORITY_INDICATOR_URGENCY_MIN,
    PROVISIONAL_PRIORITY_KEYWORD_BANDS,
    PROVISIONAL_PRIORITY_KEYWORD_URGENCY_FLOORS,
)

PRIORITY_ORDER = ("P1", "P2", "P3", "P4")

# Exact approved wording is also listed in PROMPTS.md. These are process-oriented
# suggestions only; none makes an operational, dispatch, or safety decision.
ADVISORY_GUIDANCE_TEMPLATES = {
    "P1": "Advisory: Consider careful follow-up with calm, open-ended questions and apply established procedures.",
    "P2": "Advisory: Consider clarifying the caller's account with calm, open-ended questions.",
    "P3": "Advisory: Consider reviewing the conversation context and following standard intake steps.",
    "P4": "Advisory: Continue standard intake and use your judgement in context.",
}


@dataclass(frozen=True)
class PriorityAssessment:
    """Priority output with inspectable causes and approved advisory wording."""

    priority: str
    urgency_score: int
    reasons: tuple[str, ...]
    guidance: str


def assess_priority(
    distress: float,
    nervousness: float,
    keyword_hits: Iterable[str] = (),
) -> PriorityAssessment:
    """Map indicators and recognized keyword hits to a provisional P1-P4 band.

    Indicators must be finite values in [0, 1]. Keyword matching is exact after
    case folding and whitespace normalization so results remain reproducible.
    """
    distress = _validate_indicator("distress", distress)
    nervousness = _validate_indicator("nervousness", nervousness)
    normalized_hits = {_normalize(hit) for hit in keyword_hits if isinstance(hit, str)}
    recognized = {
        keyword: band
        for keyword, band in PROVISIONAL_PRIORITY_KEYWORD_BANDS.items()
        if _normalize(keyword) in normalized_hits
    }

    matched_bands: list[str] = []
    reasons: list[str] = []
    values = {"distress": distress, "nervousness": nervousness}
    for band in PRIORITY_ORDER[:-1]:
        threshold = PROVISIONAL_PRIORITY_INDICATOR_THRESHOLDS[band]
        for name, value in values.items():
            if value >= threshold:
                matched_bands.append(band)
                reasons.append(
                    f"{name.title()} indicator {value:.2f} meets provisional {band} threshold {threshold:.2f}."
                )
                break

    for keyword, band in sorted(recognized.items()):
        matched_bands.append(band)
        reasons.append(f"Keyword hit '{keyword}' maps to provisional {band}.")

    priority = min(matched_bands, key=PRIORITY_ORDER.index) if matched_bands else "P4"
    if not matched_bands:
        reasons.append(
            "Neither indicator meets the provisional P3 threshold and no configured priority keyword matched."
        )

    highest_indicator = max(distress, nervousness)
    urgency = PROVISIONAL_PRIORITY_INDICATOR_URGENCY_MIN + math.ceil(
        highest_indicator
        * (PROVISIONAL_PRIORITY_INDICATOR_URGENCY_MAX - PROVISIONAL_PRIORITY_INDICATOR_URGENCY_MIN)
    )
    keyword_floors = [
        PROVISIONAL_PRIORITY_KEYWORD_URGENCY_FLOORS[band]
        for band in recognized.values()
    ]
    if keyword_floors:
        urgency = max(urgency, *keyword_floors)
    urgency = min(PROVISIONAL_PRIORITY_INDICATOR_URGENCY_MAX, urgency)

    return PriorityAssessment(
        priority=priority,
        urgency_score=urgency,
        reasons=tuple(reasons),
        guidance=ADVISORY_GUIDANCE_TEMPLATES[priority],
    )


def _validate_indicator(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} indicator must be a finite number within [0, 1]")
    numeric = float(value)
    if not math.isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} indicator must be a finite number within [0, 1]")
    return numeric


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())
