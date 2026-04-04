import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from starlette.datastructures import Address


# =============================================================================
# Rate limiting middleware
# =============================================================================

class TestRateLimitMiddleware:
    def _make_request(self, host="127.0.0.1"):
        request = MagicMock()
        request.client = Address(host=host, port=8000)
        return request

    @pytest.mark.asyncio
    async def test_rate_limit_allows_within_limit(self):
        from app.core.rate_limit import rate_limiter

        with patch("app.core.rate_limit.redis_client") as mock_redis:
            mock_redis.incr = AsyncMock(return_value=1)
            mock_redis.expire = AsyncMock()

            request = self._make_request()
            await rate_limiter(request)

            mock_redis.incr.assert_called_once_with("rate:127.0.0.1")
            mock_redis.expire.assert_called_once_with("rate:127.0.0.1", 60)

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_over_limit(self):
        from app.core.rate_limit import rate_limiter

        with patch("app.core.rate_limit.redis_client") as mock_redis:
            mock_redis.incr = AsyncMock(return_value=21)
            mock_redis.expire = AsyncMock()

            request = self._make_request()

            with pytest.raises(HTTPException) as exc_info:
                await rate_limiter(request)

            assert exc_info.value.status_code == 429
            assert "Rate limit exceeded" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_rate_limit_resets_after_window(self):
        from app.core.rate_limit import rate_limiter

        with patch("app.core.rate_limit.redis_client") as mock_redis:
            mock_redis.incr = AsyncMock(return_value=1)
            mock_redis.expire = AsyncMock()

            request = self._make_request()
            await rate_limiter(request)

            mock_redis.expire.assert_called_once_with("rate:127.0.0.1", 60)

    @pytest.mark.asyncio
    async def test_rate_limit_uses_client_ip(self):
        from app.core.rate_limit import rate_limiter

        with patch("app.core.rate_limit.redis_client") as mock_redis:
            mock_redis.incr = AsyncMock(return_value=1)
            mock_redis.expire = AsyncMock()

            request1 = self._make_request(host="10.0.0.1")
            request2 = self._make_request(host="10.0.0.2")

            await rate_limiter(request1)
            await rate_limiter(request2)

            assert mock_redis.incr.call_count == 2
            mock_redis.incr.assert_any_call("rate:10.0.0.1")
            mock_redis.incr.assert_any_call("rate:10.0.0.2")

    @pytest.mark.asyncio
    async def test_rate_limit_fails_open_on_redis_error(self):
        from app.core.rate_limit import rate_limiter

        with patch("app.core.rate_limit.redis_client") as mock_redis:
            mock_redis.incr = AsyncMock(side_effect=ConnectionError("Redis down"))

            request = self._make_request()

            with pytest.raises(ConnectionError):
                await rate_limiter(request)
