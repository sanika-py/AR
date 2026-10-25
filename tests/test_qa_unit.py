"""Focused deterministic tests for indicator and priority decision helpers."""

import pytest

from backend.core.priority import assess_priority
from signals import categorize_call, derive_indicators, smooth_indicator


def test_indicator_weighting_and_clamping_are_explicit():
    scores = {"fearful": 0.4, "sad": 0.2, "angry": 0.1, "surprised": 0.6}
    values = derive_indicators(scores, {"rms_cv": 2.0})
    assert values["distress_indicator"] == pytest.approx(0.28)
    assert values["nervousness_indicator"] == pytest.approx(0.59)


@pytest.mark.parametrize("alpha", [0, -0.1, 1.1, float("nan")])
def test_ema_rejects_alpha_outside_domain(alpha):
    with pytest.raises(ValueError, match="alpha"):
        smooth_indicator([0.2, 0.8], alpha)


def test_ema_uses_latest_value_and_preserves_bounds():
    assert smooth_indicator([0.2, 0.8], 0.35) == pytest.approx(0.41)
    assert smooth_indicator([0.2, 0.8], 1.0) == pytest.approx(0.8)


@pytest.mark.parametrize(
    ("distress", "nervousness", "keywords", "expected"),
    [
        (0.0, 0.0, [], "P4"),
        (0.35, 0.0, [], "P3"),
        (0.6, 0.0, [], "P2"),
        (0.8, 0.0, [], "P1"),
        (0.0, 0.0, ["threatened"], "P1"),
        (0.1, 0.1, ["unknown"], "P4"),
    ],
)
def test_priority_boundaries_and_keyword_mapping_have_reasons(
    distress, nervousness, keywords, expected
):
    result = assess_priority(distress, nervousness, keywords)
    assert result.priority == expected
    assert 1 <= result.urgency_score <= 10
    assert result.reasons
    assert result.guidance.startswith("Advisory:")


def test_category_change_requires_two_confirming_windows():
    indicators = {"distress_indicator": 0.7, "nervousness_indicator": 0.2}
    assert categorize_call(indicators, [], previous_category="Routine") == "Routine"
    assert categorize_call(
        indicators, [], previous_category="Routine", candidate_history=["High"]
    ) == "High"
