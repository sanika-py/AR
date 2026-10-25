from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app import create_app
from backend.auth import hash_password
from backend.database import get_db
from backend.models import AuditLog, Base, Officer


@pytest.fixture
def session_factory(tmp_path: Path) -> Generator[sessionmaker[Session], None, None]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory.begin() as db:
        db.add_all(
            [
                Officer(
                    username="officer",
                    password_hash=hash_password("officer-password-123"),
                    role="officer",
                ),
                Officer(
                    username="supervisor",
                    password_hash=hash_password("supervisor-password-123"),
                    role="supervisor",
                ),
            ]
        )
    yield factory
    engine.dispose()


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    app = create_app(model_factory=lambda: pytest.fail("REST test must not load model"))

    def override_db():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client


def bearer_token(client: TestClient, monkeypatch: pytest.MonkeyPatch, username: str) -> str:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-with-at-least-32-bytes")
    response = client.post(
        "/auth/token",
        json={"username": username, "password": f"{username}-password-123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_auth_roles_and_audited_call_actions(
    client: TestClient,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
):
    officer_token = bearer_token(client, monkeypatch, "officer")
    officer_headers = {"Authorization": f"Bearer {officer_token}"}
    created = client.post("/calls", headers=officer_headers)
    assert created.status_code == 201
    call_id = created.json()["call_id"]

    escalated = client.post(
        f"/calls/{call_id}/escalate",
        headers=officer_headers,
        json={"reason": "Supervisor review requested"},
    )
    assert escalated.status_code == 200
    assert escalated.json()["status"] == "escalated"

    flagged = client.post(
        f"/calls/{call_id}/flag",
        headers=officer_headers,
        json={"reason": "Review the reported account activity"},
    )
    assert flagged.status_code == 201

    forbidden_transfer = client.post(
        f"/calls/{call_id}/transfer",
        headers=officer_headers,
        json={"target_team": "Review team"},
    )
    assert forbidden_transfer.status_code == 403

    supervisor_token = bearer_token(client, monkeypatch, "supervisor")
    transferred = client.post(
        f"/calls/{call_id}/transfer",
        headers={"Authorization": f"Bearer {supervisor_token}"},
        json={"target_team": "Review team", "reason": "Officer requested review"},
    )
    assert transferred.status_code == 200
    assert transferred.json()["assigned_team"] == "Review team"

    with session_factory() as db:
        actions = db.scalars(
            select(AuditLog.action).where(AuditLog.call_id == call_id)
        ).all()
        assert actions.count("call.created") == 1
        assert actions.count("call.escalated") == 1
        assert actions.count("call.flagged_for_review") == 1
        assert actions.count("call.transferred") == 1
        assert db.scalar(
            select(func.count(AuditLog.id)).where(
                AuditLog.id.in_(
                    [escalated.json()["audit_id"], flagged.json()["audit_id"], transferred.json()["audit_id"]]
                )
            )
        ) == 3


def test_mutating_routes_require_jwt_and_summary_cannot_accept_audio(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    token = bearer_token(client, monkeypatch, "officer")
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post("/calls", headers=headers)
    call_id = created.json()["call_id"]

    assert client.post(f"/calls/{call_id}/escalate", json={"reason": "x"}).status_code == 401
    response = client.post(
        f"/calls/{call_id}/summaries",
        headers=headers,
        json={
            "duration_seconds": 2,
            "analyzed_windows": 1,
            "final_attention_category": "Routine",
            "peak_distress_indicator": 0.2,
            "peak_nervousness_indicator": 0.3,
            "quality_flags": [],
            "model_id": "local-model",
            "model_revision": "revision",
            "audio": "must never persist",
        },
    )
    assert response.status_code == 422


def test_alembic_migration_creates_all_required_tables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    database_path = tmp_path / "migrated.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    root = Path(__file__).resolve().parents[1]
    alembic_config = Config(str(root / "alembic.ini"))
    command.upgrade(alembic_config, "head")

    migrated_engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    table_names = set(inspect(migrated_engine).get_table_names())
    migrated_engine.dispose()
    assert {"officers", "calls", "summaries", "flags", "notes", "audit_log"}.issubset(
        table_names
    )
