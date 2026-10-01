from fastapi import APIRouter
from app.agents.specialists import (
    ContentAnalysisAgent,
    EmotionalInfluenceAgent,
    PersuasionManipulationAgent,
    MisinformationAgent,
    SocialEngineeringAgent,
    BehavioralReasoningAgent,
    SafetyAdvisorAgent,
)

router = APIRouter()

AGENT_REGISTRY = [
    ContentAnalysisAgent,
    EmotionalInfluenceAgent,
    PersuasionManipulationAgent,
    MisinformationAgent,
    SocialEngineeringAgent,
    BehavioralReasoningAgent,
    SafetyAdvisorAgent,
]


@router.get("/registry")
async def agent_registry():
    return {
        "agents": [
            {
                "id": cls().agent_id,
                "name": cls().agent_name,
                "role": cls().get_system_prompt()[:200] + "...",
                "status": "ready",
            }
            for cls in AGENT_REGISTRY
        ],
        "total": len(AGENT_REGISTRY),
        "orchestration": "phased_parallel_then_sequential",
        "phases": {
            "independent_parallel": ["content_analysis", "emotional_influence"],
            "dependent_sequential": [
                "persuasion_manipulation",
                "misinformation",
                "social_engineering",
            ],
            "synthesis_sequential": ["behavioral_reasoning", "safety_advisor"],
        },
    }


@router.get("/intelligence/sources")
async def source_reputation():
    return {
        "sources": [
            {"domain": "unknown-forward.com", "reputation_score": 22, "category": "messaging", "flags": ["unverified"]},
            {"domain": "news.example.com", "reputation_score": 72, "category": "news", "flags": []},
            {"domain": "social-feed.net", "reputation_score": 45, "category": "social", "flags": ["high_amplification"]},
        ],
        "engine": "source_reputation_v1",
    }
