import json
import time
from abc import ABC, abstractmethod
from typing import Any

from app.agents.llm import get_llm_client, resolve_model
from app.config import get_settings

settings = get_settings()

CONTENT_MAX_CHARS = 12_000
AGENT_OUTPUT_SNIPPET_CHARS = 600
AGENT_OUTPUT_TOTAL_CHARS = 4_000


def settings_has_openai() -> bool:
    return settings.has_openai


def compact_agent_outputs(outputs: dict[str, dict], limit: int = AGENT_OUTPUT_TOTAL_CHARS) -> str:
    """Structured context for synthesis agents — preserves more detail than compressed mode."""
    parts: list[str] = []
    for agent_id, data in outputs.items():
        if not isinstance(data, dict):
            continue
        snippet = json.dumps(data, default=str)[:AGENT_OUTPUT_SNIPPET_CHARS]
        parts.append(f"{agent_id}:\n{snippet}")
    blob = "\n\n".join(parts)
    return blob[:limit]


class BaseAgent(ABC):
    agent_id: str = "base"
    agent_name: str = "Base Agent"
    heuristic_fn = None

    def __init__(self):
        self.memory: list[dict] = []

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    def _build_user_message(self, content: str, context: dict | None) -> str:
        ctx = context or {}
        parts = [f"Content to analyze:\n{content[:CONTENT_MAX_CHARS]}"]

        if preprocess := ctx.get("preprocess"):
            parts.append(f"Preprocess signals:\n{json.dumps(preprocess, indent=2, default=str)}")

        if agent_outputs := ctx.get("agent_outputs"):
            parts.append(
                f"Prior agent findings:\n{compact_agent_outputs(agent_outputs)}"
            )

        if scores := ctx.get("scores"):
            parts.append(f"Synthesized scores:\n{json.dumps(scores, indent=2, default=str)}")

        return "\n\n".join(parts)

    async def _call_openai(self, content: str, context: dict | None = None) -> dict[str, Any]:
        client = get_llm_client()
        user_msg = self._build_user_message(content, context)

        response = await client.chat.completions.create(
            model=resolve_model(),
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
        )
        raw = response.choices[0].message.content or "{}"
        return json.loads(raw)

    async def analyze(self, content: str, context: dict | None = None) -> dict[str, Any]:
        start = time.perf_counter()
        try:
            if settings.has_openai:
                result = await self._call_openai(content, context)
                confidence = float(result.get("confidence", 0.85))
            elif self.heuristic_fn:
                result = self.heuristic_fn(content)
                confidence = float(result.get("confidence", 0.7))
            else:
                result = {"error": "No analysis method"}
                confidence = 0.0

            duration_ms = int((time.perf_counter() - start) * 1000)
            finding = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "confidence": confidence,
                "reasoning": result.get("reasoning", json.dumps(result)[:500]),
                "findings": result,
                "status": "completed",
                "duration_ms": duration_ms,
            }
            self.memory.append(finding)
            return finding
        except Exception as e:
            if self.heuristic_fn:
                result = self.heuristic_fn(content)
                fallback_note = (
                    "Heuristic fallback used."
                    if settings.is_production
                    else f"Fallback after error: {type(e).__name__}"
                )
                return {
                    "agent_id": self.agent_id,
                    "agent_name": self.agent_name,
                    "confidence": float(result.get("confidence", 0.65)),
                    "reasoning": fallback_note,
                    "findings": result,
                    "status": "completed",
                    "duration_ms": int((time.perf_counter() - start) * 1000),
                }
            raise
