"""Persistent, audio-free relational models for calls and operator actions."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _id() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Officer(Base):
    __tablename__ = "officers"
    __table_args__ = (
        CheckConstraint("role IN ('officer', 'supervisor', 'admin')", name="ck_officers_role"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    notes: Mapped[list["Note"]] = relationship(back_populates="officer")
    flags: Mapped[list["Flag"]] = relationship(back_populates="officer")
    audit_entries: Mapped[list["AuditLog"]] = relationship(back_populates="actor")


class Call(Base):
    __tablename__ = "calls"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'escalated', 'transferred', 'closed')",
            name="ck_calls_status",
        ),
        CheckConstraint("escalation_count >= 0", name="ck_calls_escalation_count"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    assigned_team: Mapped[str | None] = mapped_column(String(120))
    escalated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    escalation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("officers.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    summaries: Mapped[list["Summary"]] = relationship(back_populates="call")
    flags: Mapped[list["Flag"]] = relationship(back_populates="call")
    notes: Mapped[list["Note"]] = relationship(back_populates="call")
    audit_entries: Mapped[list["AuditLog"]] = relationship(back_populates="call")


class Summary(Base):
    __tablename__ = "summaries"
    __table_args__ = (
        CheckConstraint("duration_seconds >= 0", name="ck_summaries_duration"),
        CheckConstraint("analyzed_windows >= 0", name="ck_summaries_window_count"),
        CheckConstraint(
            "peak_distress_indicator BETWEEN 0 AND 1",
            name="ck_summaries_peak_distress",
        ),
        CheckConstraint(
            "peak_nervousness_indicator BETWEEN 0 AND 1",
            name="ck_summaries_peak_nervousness",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"), index=True)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    analyzed_windows: Mapped[int] = mapped_column(Integer, nullable=False)
    final_attention_category: Mapped[str] = mapped_column(String(80), nullable=False)
    peak_distress_indicator: Mapped[float] = mapped_column(Float, nullable=False)
    peak_nervousness_indicator: Mapped[float] = mapped_column(Float, nullable=False)
    quality_flags: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    model_id: Mapped[str] = mapped_column(String(200), nullable=False)
    model_revision: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    call: Mapped[Call] = relationship(back_populates="summaries")


class Flag(Base):
    __tablename__ = "flags"
    __table_args__ = (
        CheckConstraint("status IN ('open', 'reviewed')", name="ck_flags_status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"), index=True)
    officer_id: Mapped[str] = mapped_column(ForeignKey("officers.id"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    call: Mapped[Call] = relationship(back_populates="flags")
    officer: Mapped[Officer] = relationship(back_populates="flags")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id", ondelete="CASCADE"), index=True)
    officer_id: Mapped[str] = mapped_column(ForeignKey("officers.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    call: Mapped[Call] = relationship(back_populates="notes")
    officer: Mapped[Officer] = relationship(back_populates="notes")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("officers.id"), index=True)
    call_id: Mapped[str | None] = mapped_column(ForeignKey("calls.id", ondelete="SET NULL"), index=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    actor: Mapped[Officer | None] = relationship(back_populates="audit_entries")
    call: Mapped[Call | None] = relationship(back_populates="audit_entries")
