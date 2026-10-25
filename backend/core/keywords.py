"""Fuzzy matching for configured transcript keyword phrases."""

from __future__ import annotations

from pathlib import Path

from config import ASR_KEYWORD_CONFIG_PATH, PROVISIONAL_ASR_KEYWORD_MATCH_THRESHOLD


def load_keyword_phrases(
    path: Path = ASR_KEYWORD_CONFIG_PATH,
) -> dict[str, tuple[str, ...]]:
    """Load canonical keyword keys and aliases from the local YAML file."""
    import yaml

    with path.open("r", encoding="utf-8") as source:
        entries = yaml.safe_load(source)
    if not isinstance(entries, list):
        raise ValueError("Keyword YAML must contain a list")

    phrases: dict[str, tuple[str, ...]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("key"), str):
            raise ValueError("Each keyword entry must have a string key")
        aliases = entry.get("phrases")
        if not isinstance(aliases, list) or not aliases or not all(
            isinstance(alias, str) and alias.strip() for alias in aliases
        ):
            raise ValueError(f"Keyword {entry['key']!r} must have non-empty phrases")
        phrases[entry["key"]] = tuple(aliases)
    return phrases


def detect_keyword_hits(
    transcript: str,
    phrases: dict[str, tuple[str, ...]] | None = None,
    *,
    threshold: int = PROVISIONAL_ASR_KEYWORD_MATCH_THRESHOLD,
) -> list[str]:
    """Return distinct canonical keys with at least one fuzzy phrase match."""
    from rapidfuzz import fuzz

    if not isinstance(transcript, str) or not transcript.strip():
        return []
    phrase_map = phrases if phrases is not None else load_keyword_phrases()
    normalized_text = " ".join(transcript.casefold().split())
    return [
        key
        for key, aliases in phrase_map.items()
        if max(
            (
                fuzz.partial_ratio(
                    " ".join(alias.casefold().split()), normalized_text
                )
                for alias in aliases
            ),
            default=0,
        )
        >= threshold
    ]
