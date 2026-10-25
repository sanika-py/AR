import pytest

from backend.core.priority import ADVISORY_GUIDANCE_TEMPLATES, assess_priority


@pytest.mark.parametrize(
    ("distress", "nervousness", "keywords", "priority", "urgency"),
    [
        (0.0, 0.0, [], "P4", 1),
        (0.349, 0.2, [], "P4", 5),
        (0.35, 0.0, [], "P3", 5),
        (0.599, 0.0, [], "P3", 7),
        (0.60, 0.0, [], "P2", 7),
        (0.799, 0.0, [], "P2", 9),
        (0.80, 0.0, [], "P1", 9),
        (1.0, 0.0, [], "P1", 10),
        (0.1, 0.1, [" OTP   SHARED "], "P3", 4),
        (0.1, 0.1, ["extortion"], "P2", 7),
        (0.1, 0.1, ["threatened"], "P1", 9),
        (0.1, 0.1, ["unknown"], "P4", 2),
    ],
)
def test_priority_boundaries_and_keyword_floors(
    distress, nervousness, keywords, priority, urgency
):
    result = assess_priority(distress, nervousness, keywords)

    assert result.priority == priority
    assert result.urgency_score == urgency
    assert result.reasons
    assert result.guidance == ADVISORY_GUIDANCE_TEMPLATES[priority]
    assert "dispatch" not in result.guidance.casefold()


@pytest.mark.parametrize("value", [-0.01, 1.01, float("nan"), float("inf")])
def test_priority_rejects_invalid_indicators(value):
    with pytest.raises(ValueError, match=r"within \[0, 1\]"):
        assess_priority(value, 0.0)
