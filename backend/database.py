"""Database configuration and request-scoped SQLAlchemy sessions."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker


def normalize_database_url(url: str) -> str:
    """Select psycopg 3 for ordinary PostgreSQL URLs when installed."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = normalize_database_url(
    os.environ.get("DATABASE_URL", "sqlite:///./.awazrakshak-data/awazrakshak.db")
)


def _make_engine(url: str = DATABASE_URL):
    connect_args = {}
    if url.startswith("sqlite:"):
        connect_args["check_same_thread"] = False
        database_file = make_url(url).database
        if database_file and database_file != ":memory:":
            Path(database_file).parent.mkdir(parents=True, exist_ok=True)
    configured_engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    if url.startswith("sqlite:"):
        @event.listens_for(configured_engine, "connect")
        def _enable_sqlite_foreign_keys(connection, _record) -> None:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return configured_engine


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield and close one database session for an HTTP request."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
