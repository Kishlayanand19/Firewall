from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Thought Firewall API"
    environment: str = "development"
    debug: bool = False
    enable_docs: bool = True
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite+aiosqlite:///./thoughtfirewall.db"
    database_url_sync: str = "sqlite:///./thoughtfirewall.db"

    openai_api_key: str = ""
    openai_base_url: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_model_fast: str = ""
    openai_model_synthesis: str = ""
    openai_max_tokens: int = 1024
    openai_temperature: float = 0.2
    prefer_heuristic_synthesis: bool = False
    force_llm_synthesis: bool = False

    enable_analysis_cache: bool = True
    cache_ttl_seconds: int = 3600

    redis_url: str = ""
    use_redis: bool = False

    cors_origins: str = ""

    rate_limit: str = "60/minute"
    analyze_rate_limit: str = "10/minute"
    max_request_body_bytes: int = 1_048_576
    max_content_length: int = 50_000
    ai_request_timeout_seconds: int = 120

    clerk_secret_key: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def default_cors_for_dev(cls, v: str | None) -> str:
        if v is None or (isinstance(v, str) and not v.strip()):
            return "http://localhost:3000,http://127.0.0.1:3000"
        return v

    @property
    def database_url_async(self) -> str:
        url = self.database_url.strip()
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        if self.is_production:
            return [o for o in origins if not _is_local_origin(o)]
        return origins

    @property
    def has_openai(self) -> bool:
        key = self.openai_api_key.strip()
        return bool(key) and key not in ("sk-your-key-here", "sk-or-v1-replace-me")

    def validate_production(self) -> None:
        if not self.is_production:
            return
        if self.debug:
            raise ValueError("DEBUG must be false in production")
        if not self.cors_origin_list:
            raise ValueError("CORS_ORIGINS must list at least one production HTTPS origin")
        if self.database_url.startswith("sqlite"):
            raise ValueError("Use hosted PostgreSQL (DATABASE_URL) in production, not SQLite")


def _is_local_origin(origin: str) -> bool:
    lower = origin.lower()
    return "localhost" in lower or "127.0.0.1" in lower or lower.startswith("http://")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production()
    return settings
