from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    if settings.is_production:
        return {"status": "healthy"}
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
        "ai_enabled": settings.has_openai,
    }
