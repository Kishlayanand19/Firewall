import structlog
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import api_router
from app.config import get_settings
from app.database import init_db
from app.limiter import limiter
from app.middleware.security import RequestSizeLimitMiddleware, SecurityHeadersMiddleware
from app.security.logging import safe_log_exception

structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        safe_log_exception("database_init_skipped", e)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Cognitive Cybersecurity Layer for Human Decision-Making",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.enable_docs and not settings.is_production else None,
    redoc_url="/redoc" if settings.enable_docs and not settings.is_production else None,
    openapi_url="/openapi.json" if settings.enable_docs and not settings.is_production else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

app.include_router(api_router, prefix=settings.api_prefix)


def _generic_error_detail() -> str:
    return "An internal error occurred. Please try again later."


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if settings.debug:
        return JSONResponse(status_code=422, content={"detail": exc.errors()})
    return JSONResponse(status_code=422, content={"detail": "Invalid request"})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    safe_log_exception("unhandled_exception", exc, path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": _generic_error_detail()})


@app.get("/")
async def root():
    payload = {
        "name": "Thought Firewall API",
        "tagline": "A Cognitive Cybersecurity Layer for Human Decision-Making",
        "version": "1.0.0",
    }
    if settings.enable_docs and not settings.is_production:
        payload["docs"] = "/docs"
    return payload
