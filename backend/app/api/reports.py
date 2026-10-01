from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import AnalysisResponse, AnalysisListItem, DashboardStats

router = APIRouter()


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_report(analysis_id: str, db: AsyncSession = Depends(get_db)):
    service = AnalysisService(db)
    result = await service.get_by_id(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@router.get("/history/list", response_model=list[AnalysisListItem])
async def get_history(limit: int = 20, db: AsyncSession = Depends(get_db)):
    service = AnalysisService(db)
    return await service.list_history(limit)


@router.get("/dashboard/stats", response_model=DashboardStats)
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    service = AnalysisService(db)
    return await service.get_dashboard_stats()
