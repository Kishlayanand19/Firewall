import uuid
from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import AgentOrchestrator
from app.cache.analysis_cache import get_cached_analysis, set_cached_analysis
from app.models.analysis import AgentFinding, Analysis, RiskHistory, ThreatReport
from app.schemas.analysis import (
    AgentFindingSchema,
    AnalysisListItem,
    AnalysisResponse,
    DashboardStats,
    ThreatScores,
)


def _scores_from_result(result: dict) -> ThreatScores:
    s = result["scores"]
    return ThreatScores(
        manipulation_score=s.get("manipulation_score", 0),
        emotional_pressure_score=s.get("emotional_pressure_score", 0),
        misinformation_probability=s.get("misinformation_probability", 0),
        propaganda_risk=s.get("propaganda_risk", 0),
        social_engineering_risk=s.get("social_engineering_risk", 0),
        trustworthiness_index=s.get("trustworthiness_index", 100),
        cognitive_threat_level=s.get("cognitive_threat_level", 0),
        threat_level=s.get("threat_level", "safe"),
    )


def _to_response(result: dict, analysis_id: str | None = None) -> AnalysisResponse:
    findings = [
        AgentFindingSchema(
            agent_id=f["agent_id"],
            agent_name=f["agent_name"],
            confidence=f["confidence"],
            reasoning=f.get("reasoning", ""),
            findings=f.get("findings", {}),
            status=f.get("status", "completed"),
            duration_ms=f.get("duration_ms", 0),
        )
        for f in result.get("agent_findings", [])
    ]
    return AnalysisResponse(
        id=analysis_id or result.get("id", str(uuid.uuid4())),
        content=result.get("content", ""),
        content_type=result.get("content_type", "text"),
        scores=_scores_from_result(result),
        agent_findings=findings,
        threat_report=result.get("threat_report", {}),
        reframed_interpretation=result.get("reframed_interpretation", ""),
        full_report=result.get("full_report", {}),
        created_at=datetime.utcnow(),
    )


class AnalysisService:
    def __init__(self, db: AsyncSession | None = None):
        self.db = db
        self.orchestrator = AgentOrchestrator()

    async def analyze(self, content: str, content_type: str = "text", user_id: str | None = None) -> AnalysisResponse:
        cached = await get_cached_analysis(content)
        if cached:
            cached["content"] = content
            cached["content_type"] = content_type
            return _to_response(cached, cached.get("id"))

        result = await self.orchestrator.run_analysis(content)
        result["content"] = content
        result["content_type"] = content_type

        await set_cached_analysis(content, result)

        if self.db:
            analysis_id = await self._persist(result, content, content_type, user_id)
            return _to_response(result, analysis_id)

        return _to_response(result)

    async def _persist(self, result: dict, content: str, content_type: str, user_id: str | None) -> str:
        scores = result["scores"]
        analysis = Analysis(
            content=content[:10000],
            content_type=content_type,
            manipulation_score=scores.get("manipulation_score", 0),
            emotional_pressure_score=scores.get("emotional_pressure_score", 0),
            misinformation_probability=scores.get("misinformation_probability", 0),
            propaganda_risk=scores.get("propaganda_risk", 0),
            social_engineering_risk=scores.get("social_engineering_risk", 0),
            trustworthiness_index=scores.get("trustworthiness_index", 100),
            cognitive_threat_level=scores.get("cognitive_threat_level", 0),
            threat_level=scores.get("threat_level", "safe"),
            full_report=result.get("full_report", {}),
            reframed_interpretation=result.get("reframed_interpretation"),
        )
        if user_id:
            try:
                analysis.user_id = uuid.UUID(user_id)
            except ValueError:
                pass

        self.db.add(analysis)
        await self.db.flush()

        for f in result.get("agent_findings", []):
            self.db.add(
                AgentFinding(
                    analysis_id=analysis.id,
                    agent_id=f["agent_id"],
                    agent_name=f["agent_name"],
                    confidence=f["confidence"],
                    reasoning=f.get("reasoning", "")[:5000],
                    findings=f.get("findings", {}),
                    status=f.get("status", "completed"),
                    duration_ms=f.get("duration_ms", 0),
                )
            )

        tr = result.get("threat_report", {})
        self.db.add(
            ThreatReport(
                analysis_id=analysis.id,
                summary=tr.get("summary", ""),
                persuasive_phrases=tr.get("persuasive_phrases", []),
                emotional_triggers=tr.get("emotional_triggers", []),
                misinformation_signals=tr.get("misinformation_signals", []),
                persuasion_techniques=tr.get("persuasion_techniques", []),
                explainability=tr.get("explainability", {}),
                risk_timeline=tr.get("risk_timeline", []),
                agent_graph=tr.get("agent_graph", {}),
            )
        )

        self.db.add(
            RiskHistory(
                analysis_id=analysis.id,
                user_id=analysis.user_id,
                threat_level=scores.get("threat_level", "safe"),
                cognitive_threat_level=scores.get("cognitive_threat_level", 0),
                snapshot={"manipulation_score": scores.get("manipulation_score")},
            )
        )

        await self.db.flush()
        return str(analysis.id)

    async def get_by_id(self, analysis_id: str) -> AnalysisResponse | None:
        if not self.db:
            return None
        result = await self.db.execute(select(Analysis).where(Analysis.id == uuid.UUID(analysis_id)))
        analysis = result.scalar_one_or_none()
        if not analysis:
            return None

        findings_result = await self.db.execute(
            select(AgentFinding).where(AgentFinding.analysis_id == analysis.id)
        )
        findings = findings_result.scalars().all()

        tr_result = await self.db.execute(
            select(ThreatReport).where(ThreatReport.analysis_id == analysis.id)
        )
        threat_report = tr_result.scalar_one_or_none()

        agent_findings = [
            AgentFindingSchema(
                agent_id=f.agent_id,
                agent_name=f.agent_name,
                confidence=f.confidence,
                reasoning=f.reasoning,
                findings=f.findings,
                status=f.status,
                duration_ms=f.duration_ms,
            )
            for f in findings
        ]

        return AnalysisResponse(
            id=str(analysis.id),
            content=analysis.content,
            content_type=analysis.content_type,
            scores=ThreatScores(
                manipulation_score=analysis.manipulation_score,
                emotional_pressure_score=analysis.emotional_pressure_score,
                misinformation_probability=analysis.misinformation_probability,
                propaganda_risk=analysis.propaganda_risk,
                social_engineering_risk=analysis.social_engineering_risk,
                trustworthiness_index=analysis.trustworthiness_index,
                cognitive_threat_level=analysis.cognitive_threat_level,
                threat_level=analysis.threat_level,
            ),
            agent_findings=agent_findings,
            threat_report={
                "summary": threat_report.summary if threat_report else "",
                "persuasive_phrases": threat_report.persuasive_phrases if threat_report else [],
                "emotional_triggers": threat_report.emotional_triggers if threat_report else [],
                "misinformation_signals": threat_report.misinformation_signals if threat_report else [],
                "persuasion_techniques": threat_report.persuasion_techniques if threat_report else [],
                "explainability": threat_report.explainability if threat_report else {},
                "risk_timeline": threat_report.risk_timeline if threat_report else [],
            },
            reframed_interpretation=analysis.reframed_interpretation or "",
            full_report=analysis.full_report,
            created_at=analysis.created_at,
        )

    async def list_history(self, limit: int = 20) -> list[AnalysisListItem]:
        if not self.db:
            return []
        result = await self.db.execute(
            select(Analysis).order_by(desc(Analysis.created_at)).limit(limit)
        )
        analyses = result.scalars().all()
        return [
            AnalysisListItem(
                id=str(a.id),
                content_preview=a.content[:120] + ("..." if len(a.content) > 120 else ""),
                threat_level=a.threat_level,
                manipulation_score=a.manipulation_score,
                cognitive_threat_level=a.cognitive_threat_level,
                created_at=a.created_at,
            )
            for a in analyses
        ]

    async def get_dashboard_stats(self) -> DashboardStats:
        if not self.db:
            return self._demo_dashboard_stats()

        total = await self.db.scalar(select(func.count(Analysis.id))) or 0
        threats = await self.db.scalar(
            select(func.count(Analysis.id)).where(Analysis.threat_level != "safe")
        ) or 0
        avg_manip = await self.db.scalar(select(func.avg(Analysis.manipulation_score))) or 0

        recent = await self.list_history(10)

        dist_result = await self.db.execute(
            select(Analysis.threat_level, func.count(Analysis.id)).group_by(Analysis.threat_level)
        )
        threat_distribution = {row[0]: row[1] for row in dist_result.all()}

        return DashboardStats(
            total_analyses=total,
            threats_detected=threats,
            avg_manipulation_score=round(float(avg_manip), 1),
            threat_distribution=threat_distribution or {"safe": 0},
            recent_threats=recent,
            agent_activity=self._demo_agent_activity(),
            manipulation_trend=self._demo_trend(),
            emotional_heatmap={"fear": 42, "outrage": 38, "anger": 25, "anxiety": 31, "shame": 12, "tribalism": 28},
        )

    def _demo_dashboard_stats(self) -> DashboardStats:
        return DashboardStats(
            total_analyses=0,
            threats_detected=0,
            avg_manipulation_score=0,
            threat_distribution={"safe": 0, "mild_influence": 0, "manipulative": 0, "dangerous": 0},
            recent_threats=[],
            agent_activity=self._demo_agent_activity(),
            manipulation_trend=self._demo_trend(),
            emotional_heatmap={"fear": 42, "outrage": 38, "anger": 25, "anxiety": 31, "shame": 12, "tribalism": 28},
        )

    def _demo_agent_activity(self) -> list[dict]:
        agents = [
            "Content Analysis",
            "Emotional Influence",
            "Persuasion & Manipulation",
            "Misinformation",
            "Social Engineering",
            "Behavioral Reasoning",
            "Safety Advisor",
        ]
        return [{"agent": a, "runs": 0, "avg_confidence": 0.75} for a in agents]

    def _demo_trend(self) -> list[dict]:
        from datetime import timedelta

        now = datetime.utcnow()
        return [
            {"date": (now - timedelta(days=i)).strftime("%Y-%m-%d"), "score": 30 + i * 5}
            for i in range(6, -1, -1)
        ]
