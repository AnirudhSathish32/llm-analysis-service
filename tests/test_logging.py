import logging
import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.core.logging import setup_logging


# =============================================================================
# Logging configuration
# =============================================================================

class TestSetupLogging:
    def test_sets_debug_level_in_development(self):
        with patch("app.core.logging._is_development", return_value=True):
            with patch("logging.basicConfig") as mock_config:
                setup_logging()
                call_kwargs = mock_config.call_args[1]
                assert call_kwargs["level"] == logging.DEBUG

    def test_sets_info_level_in_production(self):
        with patch("app.core.logging._is_development", return_value=False):
            with patch("logging.basicConfig") as mock_config:
                setup_logging()
                call_kwargs = mock_config.call_args[1]
                assert call_kwargs["level"] == logging.INFO

    def test_uses_stdout_stream(self):
        with patch("app.core.logging._is_development", return_value=True):
            with patch("logging.basicConfig") as mock_config:
                setup_logging()
                call_kwargs = mock_config.call_args[1]
                assert call_kwargs["stream"] is sys.stdout


# =============================================================================
# Environment detection
# =============================================================================

class TestIsDevelopment:
    def test_returns_true_when_environment_is_development(self):
        import app.core.config
        with patch.object(app.core.config.settings, "environment", "development"):
            from app.core.logging import _is_development
            assert _is_development() is True

    def test_returns_false_when_environment_is_production(self):
        import app.core.config
        with patch.object(app.core.config.settings, "environment", "production"):
            from app.core.logging import _is_development
            assert _is_development() is False


# =============================================================================
# Lifespan logging
# =============================================================================

class TestLifespanLogging:
    @pytest.mark.asyncio
    async def test_logs_success_on_table_creation(self, caplog):
        from app.main import lifespan
        from fastapi import FastAPI

        async def mock_create():
            pass

        with patch("app.main.create_all_tables", side_effect=mock_create):
            app = FastAPI()
            caplog.set_level(logging.INFO)
            async with lifespan(app):
                pass

        assert any("Tables created successfully" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_logs_warning_on_db_not_ready(self, caplog):
        from app.main import lifespan
        from fastapi import FastAPI

        call_count = 0

        async def flaky_create():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("DB not ready")

        with patch("app.main.create_all_tables", side_effect=flaky_create):
            with patch("asyncio.sleep", new=AsyncMock()):
                app = FastAPI()
                caplog.set_level(logging.WARNING)
                async with lifespan(app):
                    pass

        assert any("DB not ready" in record.message for record in caplog.records)
        assert any(record.levelno == logging.WARNING for record in caplog.records)


# =============================================================================
# Create tables logging
# =============================================================================

class TestCreateTablesLogging:
    @pytest.mark.asyncio
    async def test_logs_success_on_first_attempt(self, caplog):
        from app.db.create_tables import create_all_tables
        from app.db.base import Base

        class FakeConn:
            async def run_sync(self, fn):
                pass

        class FakeCM:
            async def __aenter__(self):
                return FakeConn()

            async def __aexit__(self, *args):
                pass

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock(return_value=FakeCM())

        with patch("app.db.create_tables.engine", mock_engine):
            caplog.set_level(logging.INFO)
            await create_all_tables(retries=1)

        assert any("Tables created successfully" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_logs_warning_on_operational_error(self, caplog):
        from app.db.create_tables import create_all_tables
        from sqlalchemy.exc import OperationalError

        class FakeConn:
            async def run_sync(self, fn):
                raise OperationalError("stmt", [], Exception("DB not ready"))

        class FakeCM:
            async def __aenter__(self):
                return FakeConn()

            async def __aexit__(self, *args):
                pass

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock(return_value=FakeCM())

        with patch("app.db.create_tables.engine", mock_engine):
            with patch("asyncio.sleep", new=AsyncMock()):
                caplog.set_level(logging.WARNING)
                with pytest.raises(RuntimeError, match="Failed to create tables"):
                    await create_all_tables(retries=2, delay=0)

        assert any("Database not ready" in record.message for record in caplog.records)
