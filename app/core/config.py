from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    app_name: str = "LLM Analysis Service"
    environment: str = "development"

    database_url: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://llm_user:llm_password@db:5432/llm_service"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    llm_timeout_seconds: int = 60
    llm_max_retries: int = 2
    cache_ttl_seconds: int = 86400

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # RAG tuning
    chunk_size: int = 500
    chunk_overlap: int = 50
    rag_top_k: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

print("Loaded DATABASE_URL:", settings.database_url)
print("Loaded REDIS_URL:", settings.redis_url)