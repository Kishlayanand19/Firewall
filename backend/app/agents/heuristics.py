"""Rule-based analysis fallback when OpenAI is unavailable."""
import re
from typing import Any


URGENCY_PATTERNS = [
    r"\b(urgent|immediately|act now|limited time|expires|hurry|don't wait|last chance)\b",
    r"\b(must|have to|need to)\b.*\b(now|today|right away)\b",
    r"\b(breaking|alert|warning)\b",
]

FEAR_PATTERNS = [
    r"\b(danger|threat|attack|destroy|kill|die|disaster|catastrophe|emergency)\b",
    r"\b(they're coming|before it's too late|you'll regret|lose everything)\b",
]

OUTRAGE_PATTERNS = [
    r"\b(outrageous|disgusting|evil|corrupt|traitor|enemy|destroy them)\b",
    r"\b(they hate|they want to|wake up|sheeple)\b",
]

SCARCITY_PATTERNS = [
    r"\b(only \d+ left|limited supply|exclusive|sold out|running out)\b",
    r"\b(once in a lifetime|never again)\b",
]

AUTHORITY_PATTERNS = [
    r"\b(experts say|doctors agree|scientists prove|official|government)\b",
    r"\b(studies show|research confirms)\b",
]

PHISHING_PATTERNS = [
    r"\b(verify your account|click here|confirm password|suspended|unusual activity)\b",
    r"\b(wire transfer|bitcoin|gift card|social security)\b",
    r"\b(dear customer|dear user|account holder)\b",
]

MISINFO_PATTERNS = [
    r"\b(they don't want you to know|mainstream media won't tell|secret cure)\b",
    r"\b(100% guaranteed|miracle|big pharma|cover.?up)\b",
    r"\b(shocking truth|hidden truth|what really happened)\b",
]

CLICKBAIT_PATTERNS = [
    r"you won't believe",
    r"shocking",
    r"this one trick",
    r"what happened next",
    r"\d+ reasons",
    r"gone wrong",
]


def _count_patterns(text: str, patterns: list[str]) -> tuple[int, list[str]]:
    text_lower = text.lower()
    matches = []
    for p in patterns:
        for m in re.finditer(p, text_lower, re.I):
            matches.append(m.group())
    return len(matches), list(set(matches))[:10]


def analyze_content_heuristic(content: str) -> dict[str, Any]:
    urgency_count, urgency_matches = _count_patterns(content, URGENCY_PATTERNS)
    clickbait_count, _ = _count_patterns(content, CLICKBAIT_PATTERNS)
    words = len(content.split())
    caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
    exclamation = content.count("!")

    urgency = min(100, urgency_count * 25 + exclamation * 5 + (30 if caps_ratio > 0.15 else 0))
    clickbait = min(100, clickbait_count * 30 + (20 if "!!!" in content else 0))

    return {
        "framing": "alarmist" if urgency > 50 else "neutral",
        "urgency_level": urgency,
        "clickbait_score": clickbait,
        "suspicious_phrases": urgency_matches,
        "entities": [],
        "topics": [],
        "structure_notes": f"~{words} words, {exclamation} exclamations",
        "confidence": 0.72,
    }


def analyze_emotional_heuristic(content: str) -> dict[str, Any]:
    fear_c, fear_m = _count_patterns(content, FEAR_PATTERNS)
    outrage_c, outrage_m = _count_patterns(content, OUTRAGE_PATTERNS)

    emotions = {
        "fear": min(100, fear_c * 30),
        "outrage": min(100, outrage_c * 30),
        "anger": min(100, outrage_c * 20),
        "anxiety": min(100, fear_c * 25),
        "shame": 15 if "embarrass" in content.lower() or "ashamed" in content.lower() else 0,
        "tribalism": 40 if any(w in content.lower() for w in ["us vs them", "our people", "real americans"]) else 10,
        "dopamine_hooks": 35 if "viral" in content.lower() or "share this" in content.lower() else 5,
    }
    intensity = min(100, sum(emotions.values()) / max(len(emotions), 1))

    triggers = fear_m + outrage_m
    return {
        "emotions_detected": emotions,
        "emotional_intensity": intensity,
        "triggers": triggers[:8],
        "confidence": 0.7,
        "reasoning": f"Detected {len(triggers)} emotional trigger patterns.",
    }


def analyze_persuasion_heuristic(content: str) -> dict[str, Any]:
    scarcity_c, scarcity_m = _count_patterns(content, SCARCITY_PATTERNS)
    authority_c, authority_m = _count_patterns(content, AUTHORITY_PATTERNS)

    techniques = []
    if scarcity_c:
        techniques.append({"name": "scarcity", "evidence": scarcity_m[0] if scarcity_m else "scarcity language", "severity": min(100, scarcity_c * 35)})
    if authority_c:
        techniques.append({"name": "authority_bias", "evidence": authority_m[0] if authority_m else "appeal to authority", "severity": min(100, authority_c * 30)})
    if "everyone is" in content.lower() or "millions of" in content.lower():
        techniques.append({"name": "social_proof", "evidence": "bandwagon language", "severity": 45})
    if "you're crazy" in content.lower() or "that never happened" in content.lower():
        techniques.append({"name": "gaslighting", "evidence": "gaslighting phrase", "severity": 70})

    return {
        "techniques": techniques,
        "manipulation_patterns": [t["name"] for t in techniques],
        "propaganda_indicators": ["loaded_language"] if any(w in content.lower() for w in ["enemy", "traitor", "infiltrat"]) else [],
        "confidence": 0.68,
        "reasoning": f"Identified {len(techniques)} persuasion techniques.",
    }


def analyze_misinformation_heuristic(content: str) -> dict[str, Any]:
    misinfo_c, misinfo_m = _count_patterns(content, MISINFO_PATTERNS)
    prob = min(100, misinfo_c * 28)
    return {
        "misinformation_probability": prob,
        "credibility_issues": misinfo_m,
        "fact_check_flags": misinfo_m[:5],
        "coordinated_signals": ["amplification_language"] if "share before deleted" in content.lower() else [],
        "confidence": 0.65,
        "reasoning": f"Misinformation pattern score based on {misinfo_c} signals.",
    }


def analyze_social_engineering_heuristic(content: str) -> dict[str, Any]:
    phish_c, phish_m = _count_patterns(content, PHISHING_PATTERNS)
    risk = min(100, phish_c * 32)
    return {
        "social_engineering_risk": risk,
        "indicators": phish_m,
        "phishing_signals": phish_m,
        "impersonation_risk": 60 if "irs" in content.lower() or "microsoft support" in content.lower() else 10,
        "confidence": 0.75,
        "reasoning": f"Social engineering risk from {phish_c} indicator patterns.",
    }


def synthesize_scores(agent_outputs: dict[str, dict]) -> dict[str, Any]:
    content = agent_outputs.get("content_analysis", {})
    emotional = agent_outputs.get("emotional_influence", {})
    persuasion = agent_outputs.get("persuasion_manipulation", {})
    misinfo = agent_outputs.get("misinformation", {})
    social = agent_outputs.get("social_engineering", {})

    manipulation = min(100, (
        content.get("urgency_level", 0) * 0.2 +
        content.get("clickbait_score", 0) * 0.15 +
        emotional.get("emotional_intensity", 0) * 0.25 +
        len(persuasion.get("techniques", [])) * 12 +
        misinfo.get("misinformation_probability", 0) * 0.2 +
        social.get("social_engineering_risk", 0) * 0.2
    ))

    emotional_pressure = emotional.get("emotional_intensity", 0)
    misinformation_prob = misinfo.get("misinformation_probability", 0)
    propaganda = min(100, len(persuasion.get("propaganda_indicators", [])) * 25 + emotional_pressure * 0.3)
    se_risk = social.get("social_engineering_risk", 0)
    trust = max(0, 100 - manipulation * 0.6 - misinformation_prob * 0.4)
    cognitive = min(100, manipulation * 0.4 + emotional_pressure * 0.2 + misinformation_prob * 0.2 + se_risk * 0.2)

    if cognitive >= 80:
        level = "coordinated_attack"
    elif cognitive >= 60:
        level = "dangerous"
    elif cognitive >= 40:
        level = "manipulative"
    elif cognitive >= 20:
        level = "mild_influence"
    else:
        level = "safe"

    return {
        "manipulation_score": round(manipulation, 1),
        "emotional_pressure_score": round(emotional_pressure, 1),
        "misinformation_probability": round(misinformation_prob, 1),
        "propaganda_risk": round(propaganda, 1),
        "social_engineering_risk": round(se_risk, 1),
        "trustworthiness_index": round(trust, 1),
        "cognitive_threat_level": round(cognitive, 1),
        "threat_level": level,
        "verdict": f"Content classified as {level.replace('_', ' ')} with cognitive threat {cognitive:.0f}/100.",
        "confidence": 0.78,
        "reasoning": "Synthesized from multi-agent heuristic and NLP signals.",
    }


def safety_reframe(content: str, scores: dict, agent_outputs: dict) -> dict[str, Any]:
    techniques = agent_outputs.get("persuasion_manipulation", {}).get("techniques", [])
    tech_names = [t.get("name", "") for t in techniques] if techniques else []
    triggers = agent_outputs.get("emotional_influence", {}).get("triggers", [])

    reframe_parts = []
    if scores.get("manipulation_score", 0) > 40:
        reframe_parts.append("This message uses persuasive pressure tactics")
    if tech_names:
        reframe_parts.append(f"including {', '.join(tech_names[:3])}")
    if triggers:
        reframe_parts.append(f"and targets emotions via: {', '.join(triggers[:3])}")
    if not reframe_parts:
        reframe_parts.append("This content appears relatively neutral with low detected manipulation.")

    return {
        "summary": scores.get("verdict", "Analysis complete."),
        "safe_interpretation": " ".join(reframe_parts) + ". Consider verifying claims independently before acting.",
        "reframed_content": " ".join(reframe_parts) + ".",
        "critical_thinking_tips": [
            "Pause before sharing emotionally charged content.",
            "Verify claims with independent, reputable sources.",
            "Ask who benefits if you believe and act on this message.",
            "Notice urgency and fear — common manipulation levers.",
        ],
        "confidence": 0.8,
    }
