import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, Float, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50), default="text")
    source_url: Mapped[str | None] = mapped_column(String(500))

    manipulation_score: Mapped[float] = mapped_column(Float, default=0)
    emotional_pressure_score: Mapped[float] = mapped_column(Float, default=0)
    misinformation_probability: Mapped[float] = mapped_column(Float, default=0)
    propaganda_risk: Mapped[float] = mapped_column(Float, default=0)
    social_engineering_risk: Mapped[float] = mapped_column(Float, default=0)
    trustworthiness_index: Mapped[float] = mapped_column(Float, default=100)
    cognitive_threat_level: Mapped[float] = mapped_column(Float, default=0)
    threat_level: Mapped[str] = mapped_column(String(50), default="safe")

    full_report: Mapped[dict] = mapped_column(JSON, default=dict)
    reframed_interpretation: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")
    agent_findings = relationship("AgentFinding", back_populates="analysis", cascade="all, delete-orphan")
    threat_report = relationship("ThreatReport", back_populates="analysis", uselist=False, cascade="all, delete-orphan")


class AgentFinding(Base):
    __tablename__ = "agent_findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analyses.id"))
    agent_id: Mapped[str] = mapped_column(String(100))
    agent_name: Mapped[str] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float, default=0)
    reasoning: Mapped[str] = mapped_column(Text, default="")
    findings: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="agent_findings")


class ThreatReport(Base):
    __tablename__ = "threat_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analyses.id"), unique=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    persuasive_phrases: Mapped[list] = mapped_column(JSON, default=list)
    emotional_triggers: Mapped[list] = mapped_column(JSON, default=list)
    misinformation_signals: Mapped[list] = mapped_column(JSON, default=list)
    persuasion_techniques: Mapped[list] = mapped_column(JSON, default=list)
    explainability: Mapped[dict] = mapped_column(JSON, default=dict)
    risk_timeline: Mapped[list] = mapped_column(JSON, default=list)
    agent_graph: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="threat_report")


class ContentSource(Base):
    __tablename__ = "content_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain: Mapped[str] = mapped_column(String(255), index=True)
    reputation_score: Mapped[float] = mapped_column(Float, default=50)
    category: Mapped[str] = mapped_column(String(100), default="unknown")
    flags: Mapped[list] = mapped_column(JSON, default=list)
    analysis_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RiskHistory(Base):
    __tablename__ = "risk_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    analysis_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=True)
    threat_level: Mapped[str] = mapped_column(String(50))
    cognitive_threat_level: Mapped[float] = mapped_column(Float)
    snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    token_hash: Mapped[str] = mapped_column(String(255))
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
