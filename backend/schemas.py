"""Pydantic v2 response schemas for the local API and event stream."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    model_id: str
    model_revision: str
    sample_rate: int


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
