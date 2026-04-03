from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    app_name: str = "LLM Analysis Service"
    environment: str = "development"

    database_url: str = Field(default="")
    redis_url: str = Field(default="redis://redis:6379/0")

    llm_timeout_seconds: int = 120
    llm_max_retries: int = 2
    cache_ttl_seconds: int = 86400

    # DB connection pooling
    db_pool_size: int = 5
    db_pool_max_overflow: int = 10
    db_pool_timeout: int = 30

    # RAG tuning
    chunk_size: int = 500
    chunk_overlap: int = 50
    rag_top_k: int = 4

    # Upload limits
    max_upload_bytes: int = 10_485_760  # 10 MB

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url")
    @classmethod
    def reject_default_credentials(cls, v: str) -> str:
        if "llm_user:llm_password" in v:
            raise ValueError(
                "DATABASE_URL contains default credentials. "
                "Set a real DATABASE_URL environment variable."
            )
        return v

settings = Settings()
