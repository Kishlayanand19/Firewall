from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field
from uuid import UUID


class AnalyzeRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)
    content_type: str = Field(default="text", pattern=r"^(text|social|email|ad|news|chat|headline)$")
    source_url: str | None = Field(default=None, max_length=2048)
    user_id: str | None = Field(default=None, max_length=128)


class AgentFindingSchema(BaseModel):
    agent_id: str
    agent_name: str
    confidence: float
    reasoning: str
    findings: dict[str, Any]
    status: str
    duration_ms: int = 0


class ThreatScores(BaseModel):
    manipulation_score: float
    emotional_pressure_score: float
    misinformation_probability: float
    propaganda_risk: float
    social_engineering_risk: float
    trustworthiness_index: float
    cognitive_threat_level: float
    threat_level: str


class AnalysisResponse(BaseModel):
    id: str
    content: str
    content_type: str
    scores: ThreatScores
    agent_findings: list[AgentFindingSchema]
    threat_report: dict[str, Any]
    reframed_interpretation: str
    full_report: dict[str, Any]
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class StreamEvent(BaseModel):
    event: str
    data: dict[str, Any]


class AnalysisListItem(BaseModel):
    id: str
    content_preview: str
    threat_level: str
    manipulation_score: float
    cognitive_threat_level: float
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_analyses: int
    threats_detected: int
    avg_manipulation_score: float
    threat_distribution: dict[str, int]
    recent_threats: list[AnalysisListItem]
    agent_activity: list[dict[str, Any]]
    manipulation_trend: list[dict[str, Any]]
    emotional_heatmap: dict[str, float]
