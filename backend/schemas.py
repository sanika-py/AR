"""Pydantic v2 response schemas for the local API and event stream."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    model_id: str
    model_revision: str
    sample_rate: int


class AudioSessionStartedEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["session_started"] = "session_started"
    session_id: str
    asr_enabled: bool = False


class TranscriptPartialEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["transcript_partial"] = "transcript_partial"
    session_id: str
    text: str
    language: str | None = None
    keyword_hits: list[str] = Field(default_factory=list)
    status: Literal["partial", "error"] = "partial"
    message: str | None = None


class Score(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    score: float = Field(ge=0.0, le=1.0)


class AnalysisEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["analysis"] = "analysis"
    session_id: str
    elapsed: float = Field(ge=0.0)
    scores: list[Score]
    indicators: dict[str, float]
    quality_flags: list[str]
    low_confidence: bool
    category: Literal["Routine", "Elevated", "High"]
    priority: Literal["P1", "P2", "P3", "P4"]
    urgency_score: int = Field(ge=1, le=10)
    priority_reasons: list[str]
    priority_guidance: str


class AttentionTransitionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["attention_transition"] = "attention_transition"
    session_id: str
    time: float = Field(ge=0.0)
    from_category: str = Field(alias="from")
    to_category: str = Field(alias="to")


class AnalysisErrorEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["analysis_error"] = "analysis_error"
    session_id: str
    message: str


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=1024)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: Literal["officer", "supervisor", "admin"]


class CallCreatedResponse(BaseModel):
    call_id: str
    status: str
    audit_id: str


class EscalateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=1, max_length=2000)


class FlagRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=1, max_length=2000)


class TransferRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_team: str = Field(min_length=1, max_length=120)
    reason: str | None = Field(default=None, max_length=2000)


class NoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str = Field(min_length=1, max_length=20_000)


class SummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    duration_seconds: float = Field(ge=0)
    analyzed_windows: int = Field(ge=0)
    final_attention_category: str = Field(max_length=80)
    peak_distress_indicator: float = Field(ge=0, le=1)
    peak_nervousness_indicator: float = Field(ge=0, le=1)
    quality_flags: list[str] = Field(default_factory=list)
    model_id: str = Field(max_length=200)
    model_revision: str = Field(max_length=100)


class ActionResponse(BaseModel):
    call_id: str
    action: str
    audit_id: str
    status: str
    assigned_team: str | None = None
