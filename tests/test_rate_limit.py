import io
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from starlette.datastructures import Headers


# =============================================================================
# Rate limiter unit tests
# =============================================================================

class TestRateLimiterUnit:
    def test_get_client_ip_uses_x_forwarded_for(self):
        from app.core.rate_limit import get_client_ip

        mock_request = MagicMock()
        mock_request.headers = {"x-forwarded-for": "203.0.113.50"}
        mock_request.client.host = "127.0.0.1"

        assert get_client_ip(mock_request) == "203.0.113.50"

    def test_get_client_ip_uses_first_ip_in_forwarded_for(self):
        from app.core.rate_limit import get_client_ip

        mock_request = MagicMock()
        mock_request.headers = {"x-forwarded-for": "203.0.113.50, 70.41.3.18, 150.172.238.17"}
        mock_request.client.host = "127.0.0.1"

        assert get_client_ip(mock_request) == "203.0.113.50"

    def test_get_client_ip_falls_back_to_client_host(self):
        from app.core.rate_limit import get_client_ip

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.100"

        assert get_client_ip(mock_request) == "192.168.1.100"

    def test_get_client_ip_strips_whitespace_in_forwarded_for(self):
        from app.core.rate_limit import get_client_ip

        mock_request = MagicMock()
        mock_request.headers = {"x-forwarded-for": "  203.0.113.50  ,  70.41.3.18  "}
        mock_request.client.host = "127.0.0.1"

        assert get_client_ip(mock_request) == "203.0.113.50"

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_under_limit(self):
        from app.core.rate_limit import rate_limiter

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "127.0.0.1"

        with patch("app.core.rate_limit.redis_client.incr", new=AsyncMock(return_value=5)), \
             patch("app.core.rate_limit.redis_client.expire", new=AsyncMock()):
            await rate_limiter(mock_request)

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_over_limit(self):
        from app.core.rate_limit import rate_limiter

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "127.0.0.1"

        with patch("app.core.rate_limit.redis_client.incr", new=AsyncMock(return_value=21)), \
             patch("app.core.rate_limit.redis_client.expire", new=AsyncMock()):
            with pytest.raises(HTTPException) as exc_info:
                await rate_limiter(mock_request)

            assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_rate_limiter_sets_expiry_on_first_request(self):
        from app.core.rate_limit import rate_limiter, WINDOW_SECONDS

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "10.0.0.1"

        mock_incr = AsyncMock(return_value=1)
        mock_expire = AsyncMock()

        with patch("app.core.rate_limit.redis_client.incr", new=mock_incr), \
             patch("app.core.rate_limit.redis_client.expire", new=mock_expire):
            await rate_limiter(mock_request)

            mock_expire.assert_called_once_with("rate:10.0.0.1", WINDOW_SECONDS)

    @pytest.mark.asyncio
    async def test_rate_limiter_fails_open_on_redis_error(self, caplog):
        from app.core.rate_limit import rate_limiter

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "127.0.0.1"

        with patch("app.core.rate_limit.redis_client.incr", new=AsyncMock(side_effect=ConnectionError("Redis down"))):
            await rate_limiter(mock_request)

            assert any("Rate limiter Redis error" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_rate_limiter_uses_x_forwarded_for_for_key(self):
        from app.core.rate_limit import rate_limiter

        mock_request = MagicMock()
        mock_request.headers = {"x-forwarded-for": "203.0.113.50"}
        mock_request.client.host = "127.0.0.1"

        mock_incr = AsyncMock(return_value=5)

        with patch("app.core.rate_limit.redis_client.incr", new=mock_incr), \
             patch("app.core.rate_limit.redis_client.expire", new=AsyncMock()):
            await rate_limiter(mock_request)

            mock_incr.assert_called_once_with("rate:203.0.113.50")


# =============================================================================
# Endpoint rate limiting dependency wiring tests
# =============================================================================

class TestEndpointRateLimiting:
    def test_documents_routes_have_rate_limit_dependency(self):
        from app.api.routes.documents import router
        from app.core.rate_limit import rate_limiter

        for route in router.routes:
            if hasattr(route, "dependencies") and route.dependencies:
                dep_names = [
                    dep.dependency.__name__
                    for dep in route.dependencies
                    if hasattr(dep, "dependency") and hasattr(dep.dependency, "__name__")
                ]
                assert "rate_limiter" in dep_names, f"Route {route.path} missing rate_limiter"

    def test_metrics_routes_have_rate_limit_dependency(self):
        from app.api.routes.metrics import router
        from app.core.rate_limit import rate_limiter

        for route in router.routes:
            if hasattr(route, "dependencies") and route.dependencies:
                dep_names = [
                    dep.dependency.__name__
                    for dep in route.dependencies
                    if hasattr(dep, "dependency") and hasattr(dep.dependency, "__name__")
                ]
                assert "rate_limiter" in dep_names, f"Route {route.path} missing rate_limiter"


# =============================================================================
# UUID validation tests
# =============================================================================

class TestDocumentUUIDValidation:
    @pytest.mark.asyncio
    async def test_get_document_returns_400_for_invalid_uuid(self):
        from app.api.routes.documents import get_document

        mock_session = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_document(
                document_id="not-a-uuid",
                session=mock_session,
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_get_document_returns_404_for_valid_uuid_not_found(self):
        import uuid
        from app.api.routes.documents import get_document

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        valid_uuid = str(uuid.uuid4())

        with pytest.raises(HTTPException) as exc_info:
            await get_document(
                document_id=valid_uuid,
                session=mock_session,
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_document_success_with_valid_uuid(self):
        import uuid
        from datetime import datetime
        from app.api.routes.documents import get_document

        doc_uuid = uuid.uuid4()
        mock_doc = MagicMock()
        mock_doc.id = doc_uuid
        mock_doc.filename = "test.pdf"
        mock_doc.status = "ready"
        mock_doc.chunk_count = 5
        mock_doc.created_at = datetime.now()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_doc

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = await get_document(
            document_id=str(doc_uuid),
            session=mock_session,
        )

        assert response["document_id"] == str(doc_uuid)
        assert response["filename"] == "test.pdf"
        assert response["status"] == "ready"

    @pytest.mark.asyncio
    async def test_get_document_rejects_malformed_uuid(self):
        from app.api.routes.documents import get_document

        mock_session = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_document(
                document_id="abc-123-def",
                session=mock_session,
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_get_document_returns_processing_status(self):
        import uuid
        from datetime import datetime
        from app.api.routes.documents import get_document

        doc_uuid = uuid.uuid4()
        mock_doc = MagicMock()
        mock_doc.id = doc_uuid
        mock_doc.filename = "report.csv"
        mock_doc.status = "processing"
        mock_doc.chunk_count = None
        mock_doc.created_at = datetime.now()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_doc

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = await get_document(
            document_id=str(doc_uuid),
            session=mock_session,
        )

        assert response["status"] == "processing"
