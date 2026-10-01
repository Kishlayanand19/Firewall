from app.agents.base import BaseAgent
from app.agents.prompts import AGENT_PROMPTS
from app.agents import heuristics


class ContentAnalysisAgent(BaseAgent):
    agent_id = "content_analysis"
    agent_name = "Content Analysis Agent"
    heuristic_fn = staticmethod(heuristics.analyze_content_heuristic)

    def get_system_prompt(self) -> str:
        return AGENT_PROMPTS["content_analysis"]


class EmotionalInfluenceAgent(BaseAgent):
    agent_id = "emotional_influence"
    agent_name = "Emotional Influence Agent"
    heuristic_fn = staticmethod(heuristics.analyze_emotional_heuristic)

    def get_system_prompt(self) -> str:
        return AGENT_PROMPTS["emotional_influence"]


class PersuasionManipulationAgent(BaseAgent):
    agent_id = "persuasion_manipulation"
    agent_name = "Persuasion & Manipulation Agent"
    heuristic_fn = staticmethod(heuristics.analyze_persuasion_heuristic)

    def get_system_prompt(self) -> str:
        return AGENT_PROMPTS["persuasion_manipulation"]


class MisinformationAgent(BaseAgent):
    agent_id = "misinformation"
    agent_name = "Misinformation Detection Agent"
    heuristic_fn = staticmethod(heuristics.analyze_misinformation_heuristic)

    def get_system_prompt(self) -> str:
        return AGENT_PROMPTS["misinformation"]


class SocialEngineeringAgent(BaseAgent):
    agent_id = "social_engineering"
    agent_name = "Social Engineering Agent"
    heuristic_fn = staticmethod(heuristics.analyze_social_engineering_heuristic)

    def get_system_prompt(self) -> str:
        return AGENT_PROMPTS["social_engineering"]


# Step 1: lightweight independent agents (limited parallel)
INDEPENDENT_AGENT_CLASSES = [
    ContentAnalysisAgent,
    EmotionalInfluenceAgent,
]

# Step 2: dependent specialists (sequential — use prior agent context)
DEPENDENT_AGENT_CLASSES = [
    PersuasionManipulationAgent,
    MisinformationAgent,
    SocialEngineeringAgent,
]

# All analysis specialists (for registry / docs)
ANALYSIS_AGENT_CLASSES = INDEPENDENT_AGENT_CLASSES + DEPENDENT_AGENT_CLASSES


class BehavioralReasoningAgent(BaseAgent):
    agent_id = "behavioral_reasoning"
    agent_name = "Behavioral Reasoning Agent"

    def get_system_prompt(self) -> str:
        return AGENT_PROMPTS["behavioral_reasoning"]

    async def analyze(self, content: str, context: dict | None = None) -> dict:
        import time

        from app.config import get_settings

        start = time.perf_counter()
        agent_outputs = (context or {}).get("agent_outputs", {}) or {}
        cfg = get_settings()

        if cfg.prefer_heuristic_synthesis and not cfg.force_llm_synthesis:
            result = heuristics.synthesize_scores(agent_outputs)
        elif settings_has_openai() and context:
            try:
                result = await self._call_openai(content, context)
            except Exception:
                result = heuristics.synthesize_scores(agent_outputs)
        else:
            result = heuristics.synthesize_scores(agent_outputs)

        duration_ms = int((time.perf_counter() - start) * 1000)
        finding = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "confidence": float(result.get("confidence", 0.78)),
            "reasoning": result.get("reasoning", result.get("verdict", "")),
            "findings": result,
            "status": "completed",
            "duration_ms": duration_ms,
        }
        self.memory.append(finding)
        return finding


class SafetyAdvisorAgent(BaseAgent):
    agent_id = "safety_advisor"
    agent_name = "User Safety Advisor Agent"

    def get_system_prompt(self) -> str:
        return AGENT_PROMPTS["safety_advisor"]

    async def analyze(self, content: str, context: dict | None = None) -> dict:
        import time

        start = time.perf_counter()
        ctx = context or {}
        scores = ctx.get("scores", {})
        agent_outputs = ctx.get("agent_outputs", {})

        if settings_has_openai():
            try:
                result = await self._call_openai(content, ctx)
            except Exception:
                result = heuristics.safety_reframe(content, scores, agent_outputs)
        else:
            result = heuristics.safety_reframe(content, scores, agent_outputs)

        duration_ms = int((time.perf_counter() - start) * 1000)
        finding = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "confidence": float(result.get("confidence", 0.8)),
            "reasoning": result.get("summary", ""),
            "findings": result,
            "status": "completed",
            "duration_ms": duration_ms,
        }
        self.memory.append(finding)
        return finding


def settings_has_openai() -> bool:
    from app.config import get_settings

    return get_settings().has_openai
