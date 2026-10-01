"""Shared async LLM client — single stable model for predictable behavior."""
from functools import lru_cache
from typing import Any

from openai import AsyncOpenAI

from app.config import get_settings


@lru_cache
def get_llm_client() -> AsyncOpenAI:
    settings = get_settings()
    kwargs: dict[str, Any] = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return AsyncOpenAI(**kwargs)


def resolve_model(tier: str | None = None) -> str:
    """Use one primary model; optional synthesis override when explicitly configured."""
    settings = get_settings()
    if tier == "synthesis" and settings.openai_model_synthesis:
        return settings.openai_model_synthesis
    return settings.openai_model
