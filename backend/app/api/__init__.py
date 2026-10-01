from fastapi import APIRouter
from app.api import analyze, reports, agents, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
