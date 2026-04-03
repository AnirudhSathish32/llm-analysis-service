import pytest
from unittest.mock import patch, MagicMock, AsyncMock


# =============================================================================
# Redis connection lifecycle
# =============================================================================

class TestRedisConnect:
    @pytest.mark.asyncio
    async def test_connect_succeeds(self):
        from app.cache import redis as redis_cache

        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)

        with patch.object(redis_cache, "redis_client", mock_client):
            await redis_cache.connect()

        mock_client.ping.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_connect_raises_on_connection_error(self):
        from app.cache import redis as redis_cache
        import redis.asyncio as redis

        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(side_effect=redis.ConnectionError("refused"))

        with patch.object(redis_cache, "redis_client", mock_client):
            with pytest.raises(redis.ConnectionError):
                await redis_cache.connect()


class TestRedisClose:
    @pytest.mark.asyncio
    async def test_close_succeeds(self):
        from app.cache import redis as redis_cache

        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()

        with patch.object(redis_cache, "redis_client", mock_client):
            await redis_cache.close()

        mock_client.aclose.assert_awaited_once()


# =============================================================================
# Lifespan Redis lifecycle
# =============================================================================

class TestLifespanRedisLifecycle:
    @pytest.mark.asyncio
    async def test_redis_close_on_app_shutdown(self):
        from app.main import lifespan
        from app.cache import redis as redis_cache
        from fastapi import FastAPI

        with patch("app.main.create_all_tables", new=AsyncMock()):
            with patch.object(redis_cache, "connect", new=AsyncMock()) as mock_connect, \
                 patch.object(redis_cache, "close", new=AsyncMock()) as mock_close:
                app = FastAPI()
                async with lifespan(app):
                    pass

                mock_connect.assert_awaited_once()
                mock_close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_redis_connect_on_startup(self):
        from app.main import lifespan
        from app.cache import redis as redis_cache
        from fastapi import FastAPI

        with patch("app.main.create_all_tables", new=AsyncMock()):
            with patch.object(redis_cache, "connect", new=AsyncMock()) as mock_connect:
                app = FastAPI()
                async with lifespan(app):
                    pass

                mock_connect.assert_awaited_once()
