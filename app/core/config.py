from pydantic_settings import BaseSettings
import os
class Settings(BaseSettings):
    app_name: str = "LLM Analysis Service"
    environment: str = "development"

    database_url: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://llm_user:llm_password@db:5432/llm_service"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    llm_timeout_seconds: int = 5
    llm_max_retries: int = 2
    cache_ttl_seconds: int = 86400

    class Config:
        env_file = ".env"

settings = Settings()

print("Loaded DATABASE_URL:", settings.database_url)
print("Loaded REDIS_URL:", settings.redis_url)