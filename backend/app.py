"""FastAPI entry point for health and local live-audio analysis."""

from __future__ import annotations

import asyncio
import functools
import uuid
from collections.abc import Callable

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from config import (
    API_HOST,
    API_PORT,
    LIVE_UPDATE_INTERVAL_SECONDS,
    MODEL_ID,
    MODEL_REVISION,
    MODEL_SAMPLE_RATE,
)
from engine import ModelBundle, load_model
from live import LiveCallPipeline

from backend.events import EventBroker
from backend.schemas import (
    AnalysisErrorEvent,
    AnalysisEvent,
    AttentionTransitionEvent,
    HealthResponse,
)


@functools.lru_cache(maxsize=1)
def _load_configured_model() -> ModelBundle:
    return load_model()


def create_app(
    model_factory: Callable[[], ModelBundle] | None = None,
) -> FastAPI:
    app = FastAPI(
        title="AwazRakshak local analysis API",
        description="Advisory live voice-emotion analysis; not a decision service.",
        version="0.1.0",
    )
    app.state.event_broker = EventBroker()
    app.state.model_factory = model_factory or _load_configured_model

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        """Report API process health without loading or downloading the model."""
        return HealthResponse(
            status="ok",
            model_id=MODEL_ID,
            model_revision=MODEL_REVISION,
            sample_rate=MODEL_SAMPLE_RATE,
        )

    @app.websocket("/ws/events")
    async def events_socket(websocket: WebSocket) -> None:
        """Stream ephemeral analysis events to all currently connected clients."""
        await websocket.accept()
        broker: EventBroker = websocket.app.state.event_broker
        async with broker.subscribe() as queue:
            sender = asyncio.create_task(_send_events(websocket, queue))
            receiver = asyncio.create_task(_receive_until_disconnect(websocket))
            done, pending = await asyncio.wait(
                {sender, receiver}, return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            for task in done:
                try:
                    task.result()
                except (WebSocketDisconnect, RuntimeError):
                    pass

    @app.websocket("/ws/audio")
    async def audio_socket(websocket: WebSocket) -> None:
        """Accept binary little-endian PCM16 mono frames at 16 kHz."""
        await websocket.accept()
        session_id = str(uuid.uuid4())
        pipeline = LiveCallPipeline(
            websocket.app.state.model_factory,
            update_interval=LIVE_UPDATE_INTERVAL_SECONDS,
        )
        pipeline.start()
        publisher = asyncio.create_task(
            _publish_pipeline_events(
                pipeline,
                session_id,
                websocket.app.state.event_broker,
            )
        )
        try:
            while True:
                message = await websocket.receive()
                if message["type"] == "websocket.disconnect":
                    break
                chunk = message.get("bytes")
                if chunk is None:
                    await websocket.close(
                        code=1003,
                        reason="Expected non-empty binary PCM16 audio chunks.",
                    )
                    break
                try:
                    samples = decode_pcm16_chunk(chunk)
                except ValueError:
                    await websocket.close(
                        code=1003,
                        reason="Expected non-empty binary PCM16 audio chunks.",
                    )
                    break
                pipeline.add_audio(samples, MODEL_SAMPLE_RATE)
        except WebSocketDisconnect:
            pass
        finally:
            publisher.cancel()
            await asyncio.gather(publisher, return_exceptions=True)
            pipeline.stop()

    return app


async def _publish_pipeline_events(
    pipeline: LiveCallPipeline,
    session_id: str,
    broker: EventBroker,
) -> None:
    last_elapsed: float | None = None
    seen_transitions: set[tuple[float, str, str]] = set()
    last_error: str | None = None
    while True:
        snapshot = pipeline.snapshot()
        events, last_elapsed, last_error = build_snapshot_events(
            snapshot,
            session_id,
            last_elapsed=last_elapsed,
            last_error=last_error,
            seen_transitions=seen_transitions,
        )
        for event in events:
            await broker.publish(event)
        await asyncio.sleep(0.05)


def build_snapshot_events(
    snapshot: dict,
    session_id: str,
    *,
    last_elapsed: float | None = None,
    last_error: str | None = None,
    seen_transitions: set[tuple[float, str, str]] | None = None,
) -> tuple[list[dict], float | None, str | None]:
    """Build validated, audio-free event dictionaries from a pipeline snapshot."""
    seen_transitions = seen_transitions if seen_transitions is not None else set()
    events: list[dict] = []
    latest = snapshot["latest"]
    if latest is not None and latest["elapsed"] != last_elapsed:
        event = AnalysisEvent(
            session_id=session_id,
            elapsed=latest["elapsed"],
            scores=latest["scores"],
            indicators=latest["indicators"],
            quality_flags=latest["quality_flags"],
            low_confidence=latest["low_confidence"],
            category=latest["category"],
        )
        events.append(event.model_dump(mode="json"))
        last_elapsed = latest["elapsed"]

    for transition in snapshot["events"]:
        key = (transition["time"], transition["from"], transition["to"])
        if key in seen_transitions:
            continue
        seen_transitions.add(key)
        event = AttentionTransitionEvent(
            session_id=session_id,
            time=transition["time"],
            **{"from": transition["from"], "to": transition["to"]},
        )
        events.append(event.model_dump(mode="json", by_alias=True))

    error = snapshot["error"]
    if error and error != last_error:
        event = AnalysisErrorEvent(session_id=session_id, message=error)
        events.append(event.model_dump(mode="json"))
        last_error = error
    return events, last_elapsed, last_error


async def _send_events(websocket: WebSocket, queue: asyncio.Queue) -> None:
    while True:
        await websocket.send_json(await queue.get())


async def _receive_until_disconnect(websocket: WebSocket) -> None:
    while True:
        message = await websocket.receive()
        if message["type"] == "websocket.disconnect":
            return


app = create_app()


def decode_pcm16_chunk(chunk: bytes) -> np.ndarray:
    """Decode one non-empty little-endian mono PCM16 WebSocket message."""
    if not chunk or len(chunk) % 2:
        raise ValueError("PCM16 chunks must contain a non-empty even number of bytes")
    return np.frombuffer(chunk, dtype="<i2")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=API_HOST, port=API_PORT)
