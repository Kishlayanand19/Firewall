import asyncio
import time
import uuid
from typing import Any, AsyncGenerator, Type

import structlog

from app.agents.preprocess import preprocess_content
from app.agents.specialists import (
    DEPENDENT_AGENT_CLASSES,
    INDEPENDENT_AGENT_CLASSES,
    BehavioralReasoningAgent,
    SafetyAdvisorAgent,
)
from app.agents.base import BaseAgent
from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class AgentOrchestrator:
    """
    Stable multi-phase pipeline:
      1. Independent agents (Content + Emotional) — limited parallel
      2. Dependent agents (Persuasion, Misinformation, Social Engineering) — sequential
      3. Synthesis (Behavioral Reasoning, Safety Advisor) — sequential
    """

    def __init__(self):
        self.agent_outputs: dict[str, dict] = {}
        self.findings: list[dict] = []
        self.communication_graph: list[dict] = []
        self._preprocess: dict[str, Any] = {}
        self._phase_timings: dict[str, int] = {}

    def _record_communication(self, from_agent: str, to_agent: str, data_type: str):
        self.communication_graph.append({"from": from_agent, "to": to_agent, "type": data_type})

    def _build_threat_report(
        self, content: str, scores: dict, agent_outputs: dict, safety: dict
    ) -> dict[str, Any]:
        persuasion = agent_outputs.get("persuasion_manipulation", {})
        emotional = agent_outputs.get("emotional_influence", {})
        misinfo = agent_outputs.get("misinformation", {})

        techniques = persuasion.get("techniques", [])
        persuasive_phrases = [
            t.get("evidence", "") for t in techniques if isinstance(t, dict) and t.get("evidence")
        ]
        emotional_triggers = emotional.get("triggers", [])
        if isinstance(emotional_triggers, dict):
            emotional_triggers = list(emotional.get("emotions_detected", {}).keys())

        return {
            "summary": safety.get("summary", scores.get("verdict", "")),
            "persuasive_phrases": persuasive_phrases[:10],
            "emotional_triggers": emotional_triggers[:10] if isinstance(emotional_triggers, list) else [],
            "misinformation_signals": misinfo.get("fact_check_flags", []),
            "persuasion_techniques": [
                t.get("name", "") for t in techniques if isinstance(t, dict)
            ],
            "explainability": {
                "why_flagged": scores.get("verdict", ""),
                "key_signals": persuasive_phrases[:5]
                + (emotional_triggers[:5] if isinstance(emotional_triggers, list) else []),
                "confidence": scores.get("confidence", 0.75),
            },
            "risk_timeline": self._build_risk_timeline(scores),
            "agent_graph": {
                "nodes": [
                    {"id": f["agent_id"], "name": f["agent_name"], "confidence": f["confidence"]}
                    for f in self.findings
                ],
                "edges": self.communication_graph,
            },
        }

    def _build_risk_timeline(self, scores: dict) -> list[dict]:
        stages = [
            ("content_framing", scores.get("manipulation_score", 0) * 0.3),
            ("emotional_escalation", scores.get("emotional_pressure_score", 0)),
            ("persuasion_peak", scores.get("propaganda_risk", 0)),
            ("misinformation_risk", scores.get("misinformation_probability", 0)),
            ("social_engineering", scores.get("social_engineering_risk", 0)),
        ]
        cumulative = 0
        timeline = []
        for i, (stage, value) in enumerate(stages):
            cumulative = min(100, cumulative + value * 0.4)
            timeline.append({
                "stage": stage,
                "risk_value": round(value, 1),
                "cumulative_risk": round(cumulative, 1),
                "order": i + 1,
            })
        return timeline

    def _reset(self):
        self.agent_outputs = {}
        self.findings = []
        self.communication_graph = []
        self._preprocess = {}
        self._phase_timings = {}

    def _context(self) -> dict[str, Any]:
        return {
            "preprocess": self._preprocess,
            "agent_outputs": self.agent_outputs,
        }

    async def _run_agent(self, AgentClass: Type[BaseAgent], content: str) -> dict[str, Any]:
        agent = AgentClass()
        try:
            return await agent.analyze(content, self._context())
        except Exception as exc:
            logger.warning(
                "agent_failed",
                agent_id=agent.agent_id,
                error_type=type(exc).__name__,
            )
            if agent.heuristic_fn:
                return {
                    "agent_id": agent.agent_id,
                    "agent_name": agent.agent_name,
                    "confidence": 0.6,
                    "reasoning": "Heuristic fallback after agent error",
                    "findings": agent.heuristic_fn(content),
                    "status": "completed",
                    "duration_ms": 0,
                }
            raise

    def _store_finding(self, finding: dict[str, Any], upstream: str = "preprocess"):
        self.findings.append(finding)
        self.agent_outputs[finding["agent_id"]] = finding["findings"]
        self._record_communication(upstream, finding["agent_id"], "agent_output")

    async def _run_independent_phase(self, content: str) -> list[dict[str, Any]]:
        """Step 1: Content + Emotional in limited parallel (max 2)."""
        t0 = time.perf_counter()
        tasks = [
            asyncio.create_task(self._run_agent(cls, content))
            for cls in INDEPENDENT_AGENT_CLASSES
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        findings: list[dict[str, Any]] = []
        for cls, result in zip(INDEPENDENT_AGENT_CLASSES, results):
            if isinstance(result, Exception):
                agent = cls()
                finding = {
                    "agent_id": agent.agent_id,
                    "agent_name": agent.agent_name,
                    "confidence": 0.6,
                    "reasoning": "Heuristic fallback after parallel error",
                    "findings": agent.heuristic_fn(content) if agent.heuristic_fn else {},
                    "status": "completed",
                    "duration_ms": 0,
                }
            else:
                finding = result
            findings.append(finding)
            self._store_finding(finding)

        self._phase_timings["independent_ms"] = int((time.perf_counter() - t0) * 1000)
        logger.info(
            "phase_complete",
            phase="independent",
            elapsed_ms=self._phase_timings["independent_ms"],
            agents=[f["agent_id"] for f in findings],
        )
        return findings

    async def _run_dependent_phase(self, content: str) -> list[dict[str, Any]]:
        """Step 2: Persuasion → Misinformation → Social Engineering (sequential)."""
        t0 = time.perf_counter()
        findings: list[dict[str, Any]] = []
        prev = "independent_agents"

        for cls in DEPENDENT_AGENT_CLASSES:
            finding = await self._run_agent(cls, content)
            findings.append(finding)
            self._store_finding(finding, upstream=prev)
            prev = finding["agent_id"]

        self._phase_timings["dependent_ms"] = int((time.perf_counter() - t0) * 1000)
        logger.info(
            "phase_complete",
            phase="dependent",
            elapsed_ms=self._phase_timings["dependent_ms"],
            agents=[f["agent_id"] for f in findings],
        )
        return findings

    async def _synthesize_phase(self, content: str) -> tuple[dict, dict[str, Any], dict[str, Any]]:
        """Step 3: Behavioral Reasoning → Safety Advisor (sequential)."""
        t0 = time.perf_counter()

        behavioral = BehavioralReasoningAgent()
        behavioral_finding = await behavioral.analyze(content, self._context())
        scores = behavioral_finding["findings"]
        self.findings.append(behavioral_finding)
        self._record_communication("analysis_agents", "behavioral_reasoning", "synthesis")

        safety = SafetyAdvisorAgent()
        safety_ctx = {
            **self._context(),
            "scores": scores,
        }
        safety_finding = await safety.analyze(content, safety_ctx)
        self.findings.append(safety_finding)
        self._record_communication("behavioral_reasoning", "safety_advisor", "guidance")

        self._phase_timings["synthesis_ms"] = int((time.perf_counter() - t0) * 1000)
        logger.info(
            "phase_complete",
            phase="synthesis",
            elapsed_ms=self._phase_timings["synthesis_ms"],
        )
        return scores, behavioral_finding, safety_finding

    async def run_analysis(self, content: str) -> dict[str, Any]:
        t0 = time.perf_counter()
        self._reset()
        self._preprocess = preprocess_content(content)

        logger.info("analysis_start", content_length=len(content))

        await self._run_independent_phase(content)
        await self._run_dependent_phase(content)
        scores, behavioral_finding, safety_finding = await self._synthesize_phase(content)

        safety_data = safety_finding["findings"]
        threat_report = self._build_threat_report(content, scores, self.agent_outputs, safety_data)

        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        logger.info(
            "analysis_complete",
            elapsed_ms=elapsed_ms,
            phase_timings=self._phase_timings,
            mode="stable_phased",
        )

        return {
            "id": str(uuid.uuid4()),
            "content": content,
            "scores": scores,
            "agent_findings": self.findings,
            "threat_report": threat_report,
            "reframed_interpretation": safety_data.get(
                "reframed_content", safety_data.get("safe_interpretation", "")
            ),
            "full_report": {
                "agent_outputs": self.agent_outputs,
                "scores": scores,
                "threat_report": threat_report,
                "safety": safety_data,
                "communication_graph": self.communication_graph,
                "metrics": {
                    "total_ms": elapsed_ms,
                    **self._phase_timings,
                },
            },
        }

    async def stream_analysis(self, content: str) -> AsyncGenerator[dict[str, Any], None]:
        t0 = time.perf_counter()
        self._reset()
        self._preprocess = preprocess_content(content)

        yield {
            "event": "pipeline_start",
            "message": "Stable phased pipeline initiated",
            "phases": ["independent", "dependent", "synthesis"],
        }

        # Phase 1: limited parallel (Content + Emotional)
        yield {"event": "phase_start", "phase": "independent", "message": "Running content and emotional analysis"}
        t_phase = time.perf_counter()
        for cls in INDEPENDENT_AGENT_CLASSES:
            agent = cls()
            yield {
                "event": "agent_start",
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "phase": "independent",
            }

        independent_findings = await self._run_independent_phase(content)
        for finding in independent_findings:
            yield {"event": "agent_complete", **finding}

        independent_ms = int((time.perf_counter() - t_phase) * 1000)
        yield {
            "event": "phase_complete",
            "phase": "independent",
            "elapsed_ms": independent_ms,
            "agents_done": len(independent_findings),
        }

        # Phase 2: sequential dependent agents
        yield {"event": "phase_start", "phase": "dependent", "message": "Running persuasion, misinformation, and social engineering checks"}
        t_phase = time.perf_counter()

        for cls in DEPENDENT_AGENT_CLASSES:
            agent = cls()
            yield {
                "event": "agent_start",
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "phase": "dependent",
            }
            finding = await self._run_agent(cls, content)
            self._store_finding(
                finding,
                upstream=self.findings[-1]["agent_id"] if self.findings else "independent_agents",
            )
            yield {"event": "agent_complete", **finding}

        dependent_ms = int((time.perf_counter() - t_phase) * 1000)
        self._phase_timings["dependent_ms"] = dependent_ms
        yield {
            "event": "phase_complete",
            "phase": "dependent",
            "elapsed_ms": dependent_ms,
            "agents_done": len(DEPENDENT_AGENT_CLASSES),
        }

        # Phase 3: synthesis (no premature heuristic scores)
        yield {"event": "synthesis_start", "message": "Synthesizing threat assessment"}
        t_phase = time.perf_counter()

        behavioral = BehavioralReasoningAgent()
        yield {
            "event": "agent_start",
            "agent_id": behavioral.agent_id,
            "agent_name": behavioral.agent_name,
            "phase": "synthesis",
        }
        behavioral_finding = await behavioral.analyze(content, self._context())
        self.findings.append(behavioral_finding)
        self._record_communication("analysis_agents", "behavioral_reasoning", "synthesis")
        yield {"event": "agent_complete", **behavioral_finding}

        scores = behavioral_finding["findings"]

        safety = SafetyAdvisorAgent()
        yield {
            "event": "agent_start",
            "agent_id": safety.agent_id,
            "agent_name": safety.agent_name,
            "phase": "synthesis",
        }
        safety_ctx = {**self._context(), "scores": scores}
        safety_finding = await safety.analyze(content, safety_ctx)
        self.findings.append(safety_finding)
        self._record_communication("behavioral_reasoning", "safety_advisor", "guidance")
        yield {"event": "agent_complete", **safety_finding}

        self._phase_timings["synthesis_ms"] = int((time.perf_counter() - t_phase) * 1000)

        threat_report = self._build_threat_report(
            content, scores, self.agent_outputs, safety_finding["findings"]
        )

        total_ms = int((time.perf_counter() - t0) * 1000)
        logger.info(
            "stream_analysis_complete",
            total_ms=total_ms,
            phase_timings=self._phase_timings,
        )

        yield {
            "event": "analysis_complete",
            "id": str(uuid.uuid4()),
            "scores": scores,
            "agent_findings": self.findings,
            "threat_report": threat_report,
            "reframed_interpretation": safety_finding["findings"].get(
                "reframed_content",
                safety_finding["findings"].get("safe_interpretation", ""),
            ),
            "full_report": {
                "agent_outputs": self.agent_outputs,
                "scores": scores,
                "threat_report": threat_report,
                "metrics": {"total_ms": total_ms, **self._phase_timings},
            },
        }
