import pytest
from unittest.mock import patch, MagicMock, AsyncMock


# =============================================================================
# Request correlation ID middleware
# =============================================================================

class TestCorrelationIdMiddleware:
    @pytest.mark.asyncio
    async def test_middleware_generates_request_id(self):
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    @pytest.mark.asyncio
    async def test_middleware_uses_client_provided_request_id(self):
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        custom_id = "my-custom-id-123"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health", headers={"X-Request-ID": custom_id})

        assert response.headers["X-Request-ID"] == custom_id

    @pytest.mark.asyncio
    async def test_request_id_is_valid_uuid(self):
        import uuid
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        request_id = response.headers["X-Request-ID"]
        uuid.UUID(request_id)  # raises ValueError if not valid UUID

    @pytest.mark.asyncio
    async def test_request_id_included_in_error_responses(self):
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/nonexistent")

        assert response.status_code == 404
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_request_id_not_duplicated(self):
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp1 = await client.get("/health")
            resp2 = await client.get("/health")

        id1 = resp1.headers["X-Request-ID"]
        id2 = resp2.headers["X-Request-ID"]
        assert id1 != id2
