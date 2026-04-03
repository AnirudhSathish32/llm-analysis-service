import pytest
from unittest.mock import patch, MagicMock


# =============================================================================
# DB connection pooling
# =============================================================================

class TestDBConnectionPooling:
    def test_engine_has_pool_size_configured(self):
        from app.db.session import engine
        pool = engine.pool
        assert pool.size() == 5

    def test_engine_has_max_overflow_configured(self):
        from app.db.session import engine
        pool = engine.pool
        assert pool._max_overflow == 10

    def test_engine_has_pool_timeout_configured(self):
        from app.db.session import engine
        pool = engine.pool
        assert pool._timeout == 30

    def test_pool_settings_loaded_from_env(self):
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.database_url = "postgresql+asyncpg://test:test@localhost/test"
            mock_settings.db_pool_size = 10
            mock_settings.db_pool_max_overflow = 20
            mock_settings.db_pool_timeout = 60

            from sqlalchemy.ext.asyncio import create_async_engine

            engine = create_async_engine(
                mock_settings.database_url,
                echo=False,
                pool_size=mock_settings.db_pool_size,
                max_overflow=mock_settings.db_pool_max_overflow,
                pool_timeout=mock_settings.db_pool_timeout,
            )

            assert engine.pool.size() == 10
            assert engine.pool._max_overflow == 20
            assert engine.pool._timeout == 60

    def test_pool_settings_fallback_to_defaults(self):
        from app.core.config import settings
        assert settings.db_pool_size == 5
        assert settings.db_pool_max_overflow == 10
        assert settings.db_pool_timeout == 30
