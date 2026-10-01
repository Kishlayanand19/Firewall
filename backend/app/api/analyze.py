import asyncio
import json
import time

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.limiter import limiter
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import AgentOrchestrator
from app.config import get_settings
from app.database import get_db
from app.schemas.analysis import AnalyzeRequest, AnalysisResponse
from app.security import safe_log_exception, sanitize_user_content
from app.services.analysis_service import AnalysisService

router = APIRouter()
settings = get_settings()


def _prepare_content(request: AnalyzeRequest) -> str:
    return sanitize_user_content(request.content, max_length=settings.max_content_length)


@router.post("", response_model=AnalysisResponse)
@limiter.limit(settings.analyze_rate_limit)
async def analyze_content(
    request: Request,
    body: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
):
    content = _prepare_content(body)
    service = AnalysisService(db)
    try:
        result = await asyncio.wait_for(
            service.analyze(
                content=content,
                content_type=body.content_type,
                user_id=body.user_id,
            ),
            timeout=settings.ai_request_timeout_seconds,
        )
        await db.commit()
        return result
    except asyncio.TimeoutError:
        await db.rollback()
        from fastapi import HTTPException

        raise HTTPException(status_code=504, detail="Analysis timed out. Try shorter content.")
    except ValueError as e:
        await db.rollback()
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        safe_log_exception("analyze_failed", e)
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail="Analysis failed. Please try again later.")


@router.post("/stream")
@limiter.limit(settings.analyze_rate_limit)
async def analyze_stream(request: Request, body: AnalyzeRequest):
    content = _prepare_content(body)
    orchestrator = AgentOrchestrator()
    timeout = settings.ai_request_timeout_seconds

    async def event_generator():
        deadline = time.monotonic() + timeout
        stream = orchestrator.stream_analysis(content).__aiter__()
        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    yield f"data: {json.dumps({'event': 'error', 'message': 'Analysis timed out'})}\n\n"
                    return
                try:
                    event = await asyncio.wait_for(stream.__anext__(), timeout=remaining)
                except StopAsyncIteration:
                    break
                yield f"data: {json.dumps(event, default=str)}\n\n"
        except asyncio.TimeoutError:
            yield f"data: {json.dumps({'event': 'error', 'message': 'Analysis timed out'})}\n\n"
        except Exception as e:
            safe_log_exception("stream_analyze_failed", e)
            yield f"data: {json.dumps({'event': 'error', 'message': 'Analysis failed. Please try again.'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
