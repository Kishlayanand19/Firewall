"""Analysis result cache — in-memory with TTL cap and optional Redis."""
import hashlib
import json
import time
from typing import Any

from app.config import get_settings

_memory: dict[str, tuple[float, dict[str, Any]]] = {}
_redis = None
_MAX_MEMORY_ENTRIES = 256


def _content_hash(content: str) -> str:
    normalized = " ".join(content.strip().lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def _evict_expired_and_trim() -> None:
    now = time.time()
    expired = [k for k, (exp, _) in _memory.items() if exp <= now]
    for k in expired:
        del _memory[k]
    if len(_memory) <= _MAX_MEMORY_ENTRIES:
        return
    # Drop oldest entries by expiry time
    sorted_keys = sorted(_memory.keys(), key=lambda k: _memory[k][0])
    for k in sorted_keys[: len(_memory) - _MAX_MEMORY_ENTRIES]:
        del _memory[k]


async def _get_redis():
    global _redis
    settings = get_settings()
    if not settings.use_redis or not settings.redis_url:
        return None
    if _redis is None:
        try:
            import redis.asyncio as aioredis

            _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        except Exception:
            return None
    return _redis


async def get_cached_analysis(content: str) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.enable_analysis_cache:
        return None

    key = f"tf:analysis:{_content_hash(content)}"
    now = time.time()
    _evict_expired_and_trim()

    if key in _memory:
        expires, payload = _memory[key]
        if expires > now:
            return payload
        del _memory[key]

    r = await _get_redis()
    if r:
        try:
            raw = await r.get(key)
            if raw:
                return json.loads(raw)
        except Exception:
            pass
    return None


async def set_cached_analysis(content: str, result: dict[str, Any]) -> None:
    settings = get_settings()
    if not settings.enable_analysis_cache:
        return

    key = f"tf:analysis:{_content_hash(content)}"
    ttl = settings.cache_ttl_seconds
    _evict_expired_and_trim()
    _memory[key] = (time.time() + ttl, result)

    r = await _get_redis()
    if r:
        try:
            await r.setex(key, ttl, json.dumps(result, default=str))
        except Exception:
            pass
