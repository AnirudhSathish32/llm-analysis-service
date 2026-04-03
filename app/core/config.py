from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "LLM Analysis Service"
    environment: str = "development"

    database_url: str = Field(
        default="postgresql+asyncpg://llm_user:llm_password@db:5432/llm_service"
    )
    redis_url: str = Field(default="redis://redis:6379/0")

    llm_timeout_seconds: int = 120
    llm_max_retries: int = 2
    cache_ttl_seconds: int = 86400

    # DB connection pooling
    db_pool_size: int = 5
    db_pool_max_overflow: int = 10
    db_pool_timeout: int = 30

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # RAG tuning
    chunk_size: int = 500
    chunk_overlap: int = 50
    rag_top_k: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()