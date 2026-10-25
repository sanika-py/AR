"""HTTP and event-schema contract tests (no model inference or audio persistence)."""

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from backend.app import create_app
from backend.schemas import AnalysisEvent, AttentionTransitionEvent, HealthResponse


def test_health_contract_is_stable_and_does_not_load_model():
    app = create_app(model_factory=lambda: pytest.fail("health must not load the model"))
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert set(response.json()) == {"status", "model_id", "model_revision", "sample_rate"}
    assert HealthResponse.model_validate(response.json()).status == "ok"


def test_openapi_exposes_action_routes_with_bearer_security():
    schema = create_app().openapi()
    paths = schema["paths"]
    for path in (
        "/auth/token",
        "/calls",
        "/calls/{call_id}/escalate",
        "/calls/{call_id}/flag",
        "/calls/{call_id}/transfer",
        "/calls/{call_id}/notes",
        "/calls/{call_id}/summaries",
    ):
        assert path in paths
    assert "security" in paths["/calls/{call_id}/escalate"]["post"]
    assert "security" in paths["/calls/{call_id}/transfer"]["post"]


def test_analysis_event_contract_is_audio_free_and_advisory():
    event = AnalysisEvent.model_validate(
        {
            "type": "analysis", "session_id": "qa", "elapsed": 3.0,
            "scores": [{"label": "angry", "score": 1.0}],
            "indicators": {"distress_indicator": 0.5}, "quality_flags": [],
            "low_confidence": False, "category": "Elevated", "priority": "P2",
            "urgency_score": 6, "priority_reasons": ["test reason"],
            "priority_guidance": "Advisory: use judgement.",
        }
    )
    assert "audio" not in event.model_dump()
    with pytest.raises(ValidationError):
        AnalysisEvent.model_validate({**event.model_dump(), "audio": "forbidden"})


def test_transition_wire_contract_keeps_from_to_aliases():
    event = AttentionTransitionEvent.model_validate(
        {"type": "attention_transition", "session_id": "qa", "time": 2,
         "from": "Routine", "to": "Elevated"}
    )
    assert event.model_dump(by_alias=True)["from"] == "Routine"
    assert event.model_dump(by_alias=True)["to"] == "Elevated"
