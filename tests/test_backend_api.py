import asyncio
import time

import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.app import build_snapshot_events, create_app, decode_pcm16_chunk
from backend.events import EventBroker
from config import EXPECTED_ID2LABEL, MODEL_ID, MODEL_REVISION, MODEL_SAMPLE_RATE
from live import LiveCallPipeline


class SyntheticModel:
    labels = tuple(EXPECTED_ID2LABEL[index] for index in range(7))
    output_dimension = len(labels)

    def predict_scores(self, waveform):
        assert waveform.dtype == np.float32
        assert waveform.shape == (3 * MODEL_SAMPLE_RATE,)
        scores = [0.0] * self.output_dimension
        scores[3] = 1.0
        return [
            {"label": label, "score": score}
            for label, score in zip(self.labels, scores, strict=True)
        ]


def test_health_reports_pinned_model_without_loading_it():
    app = create_app(model_factory=lambda: pytest.fail("health must not load model"))
    route = next(route for route in app.routes if getattr(route, "path", None) == "/health")
    coroutine = route.endpoint()
    with pytest.raises(StopIteration) as result:
        coroutine.send(None)
    response = result.value.value

    assert response.model_dump() == {
        "status": "ok",
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "sample_rate": MODEL_SAMPLE_RATE,
    }


def test_root_redirects_to_api_docs():
    with TestClient(create_app()) as client:
        response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_websocket_routes_are_registered():
    paths = {getattr(route, "path", None) for route in create_app().routes}
    assert "/ws/audio" in paths
    assert "/ws/events" in paths


def test_audio_socket_announces_session_id_before_audio_frames():
    app = create_app(model_factory=SyntheticModel)
    with TestClient(app) as client:
        with client.websocket_connect("/ws/audio") as websocket:
            message = websocket.receive_json()

    assert message["type"] == "session_started"
    assert message["session_id"]


def test_event_broker_fans_out_audio_free_events():
    broker = EventBroker()
    subscriber = asyncio.Queue(maxsize=1)
    broker._subscribers.add(subscriber)
    coroutine = broker.publish({"type": "analysis", "session_id": "test"})
    with pytest.raises(StopIteration):
        coroutine.send(None)

    assert subscriber.get_nowait() == {"type": "analysis", "session_id": "test"}


def test_synthetic_pcm16_audio_produces_analysis_event():
    pipeline = LiveCallPipeline(SyntheticModel, update_interval=0.01)
    samples = (
        np.sin(np.arange(3 * MODEL_SAMPLE_RATE) * 2 * np.pi * 220 / MODEL_SAMPLE_RATE)
        * 12000
    ).astype("<i2")
    pipeline.start()
    pipeline.add_audio(decode_pcm16_chunk(samples.tobytes()), MODEL_SAMPLE_RATE)
    deadline = time.monotonic() + 5.0
    while pipeline.snapshot()["latest"] is None and time.monotonic() < deadline:
        time.sleep(0.01)
    snapshot = pipeline.snapshot()
    pipeline.stop()

    events, _, _ = build_snapshot_events(snapshot, "synthetic-session")
    event = events[0]
    assert event["type"] == "analysis"
    assert event["session_id"] == "synthetic-session"
    assert len(event["scores"]) == 7
    assert event["scores"][3] == {"label": "fearful", "score": 1.0}
    assert "distress_indicator" in event["indicators"]
    assert event["category"] in {"Routine", "Elevated", "High"}
    assert "audio" not in event


def test_pcm16_decoder_rejects_empty_or_misaligned_audio():
    with pytest.raises(ValueError, match="non-empty"):
        decode_pcm16_chunk(b"")
    with pytest.raises(ValueError, match="even number"):
        decode_pcm16_chunk(b"\x00")


def test_pcm16_decoder_accepts_little_endian_int16():
    decoded = decode_pcm16_chunk(b"\x01\x00\xff\xff")
    assert decoded.dtype == np.dtype("<i2")
    assert decoded.tolist() == [1, -1]
