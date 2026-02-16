from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "LLM Analysis Service"
    environment: str = "development"

    database_url: str
    redis_url: str

    llm_timeout_seconds: int = 5
    llm_max_retries: int = 2
    cache_ttl_seconds: int = 86400

    class Config:
        env_file = ".env"

settings = Settings()
