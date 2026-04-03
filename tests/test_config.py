import pytest
from unittest.mock import patch


# =============================================================================
# Settings defaults
# =============================================================================

class TestSettingsDefaults:
    def test_database_url_has_default(self):
        from app.core.config import settings
        assert "postgresql+asyncpg://" in settings.database_url

    def test_redis_url_has_default(self):
        from app.core.config import settings
        assert "redis://" in settings.redis_url

    def test_llm_timeout_has_default(self):
        from app.core.config import settings
        assert settings.llm_timeout_seconds == 120

    def test_cache_ttl_has_default(self):
        from app.core.config import settings
        assert settings.cache_ttl_seconds > 0


# =============================================================================
# No os.getenv in config.py
# =============================================================================

class TestNoManualEnvCalls:
    def test_config_does_not_use_os_getenv(self):
        with open("app/core/config.py") as f:
            content = f.read()
        assert "os.getenv" not in content
        assert "os.environ" not in content


# =============================================================================
# .env.example completeness
# =============================================================================

class TestEnvExample:
    def test_env_example_exists(self):
        import os
        assert os.path.exists(".env.example")

    def test_env_example_has_required_keys(self):
        with open(".env.example") as f:
            content = f.read()
        required_keys = [
            "DATABASE_URL",
            "REDIS_URL",
            "ANTHROPIC_API_KEY",
            "GEMINI_API_KEY",
            "PINECONE_API_KEY",
            "PINECONE_INDEX",
        ]
        for key in required_keys:
            assert key in content, f"Missing {key} in .env.example"
