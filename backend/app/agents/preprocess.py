"""Single-pass content preprocessing shared across all agents."""
import re
from typing import Any

from app.agents import heuristics


def preprocess_content(content: str) -> dict[str, Any]:
    text = content.strip()
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    exclamations = text.count("!")
    caps_ratio = sum(1 for c in text if c.isupper()) / max(char_count, 1)

    urgency_n, urgency_hits = heuristics._count_patterns(text, heuristics.URGENCY_PATTERNS)
    fear_n, _ = heuristics._count_patterns(text, heuristics.FEAR_PATTERNS)
    phish_n, phish_hits = heuristics._count_patterns(text, heuristics.PHISHING_PATTERNS)

    return {
        "word_count": word_count,
        "char_count": char_count,
        "exclamations": exclamations,
        "caps_ratio": round(caps_ratio, 3),
        "urgency_signals": urgency_n,
        "fear_signals": fear_n,
        "phishing_signals": phish_n,
        "sample_phrases": list(
            dict.fromkeys(urgency_hits[:3] + phish_hits[:3])
        )[:5],
        "preview": text[:400] + ("…" if len(text) > 400 else ""),
    }
