import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.exc import OperationalError


# =============================================================================
# Error sanitization
# =============================================================================

class TestErrorSanitization:
    @pytest.mark.asyncio
    async def test_upload_error_does_not_leak_internal_details(self):
        from app.api.routes.documents import upload_document
        from fastapi import HTTPException
        from io import BytesIO
        from fastapi import UploadFile
        from starlette.datastructures import Headers

        with patch("app.api.routes.documents.settings") as mock_settings, \
             patch("app.api.routes.documents.ingest_document", new=AsyncMock(side_effect=RuntimeError("Connection refused to postgres:5432"))):
            mock_settings.max_upload_bytes = 10_485_760

            mock_session = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            upload = UploadFile(
                filename="test.pdf",
                file=BytesIO(b"test"),
                headers=Headers({"content-type": "application/pdf"}),
            )

            with pytest.raises(HTTPException) as exc_info:
                await upload_document(file=upload, session=mock_session)

            assert "postgres:5432" not in exc_info.value.detail
            assert "Connection refused" not in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_upload_error_returns_generic_message(self):
        from app.api.routes.documents import upload_document
        from fastapi import HTTPException
        from io import BytesIO
        from fastapi import UploadFile
        from starlette.datastructures import Headers

        with patch("app.api.routes.documents.settings") as mock_settings, \
             patch("app.api.routes.documents.ingest_document", new=AsyncMock(side_effect=RuntimeError("some internal error"))):
            mock_settings.max_upload_bytes = 10_485_760

            mock_session = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            upload = UploadFile(
                filename="test.pdf",
                file=BytesIO(b"test"),
                headers=Headers({"content-type": "application/pdf"}),
            )

            with pytest.raises(HTTPException) as exc_info:
                await upload_document(file=upload, session=mock_session)

            assert exc_info.value.status_code == 500
            assert "ingestion failed" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_metrics_error_returns_generic_message(self):
        from app.api.routes.metrics import usage
        from fastapi import HTTPException

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=OperationalError("stmt", [], Exception("DB down")))

        with pytest.raises(HTTPException) as exc_info:
            await usage(session=mock_session)

        assert exc_info.value.status_code == 500
        assert "DB down" not in exc_info.value.detail
        assert "Failed to retrieve usage metrics" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_metrics_error_does_not_expose_stack_trace(self):
        from app.api.routes.metrics import usage_by_type
        from fastapi import HTTPException

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=OperationalError("stmt", [], Exception("SQL syntax error")))

        with pytest.raises(HTTPException) as exc_info:
            await usage_by_type(session=mock_session)

        assert exc_info.value.status_code == 500
        assert "SQL syntax error" not in exc_info.value.detail
        assert "stmt" not in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_analysis_error_returns_failed_status_not_exception(self):
        from app.services.analysis_service import AnalysisService
        from app.schemas.analysis import AnalysisRequestSchema
        from unittest.mock import patch, MagicMock, AsyncMock
        import uuid

        mock_req = MagicMock()
        mock_req.id = uuid.uuid4()

        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(return_value=None)), \
             patch("app.services.analysis_service.redis_client.set", new=AsyncMock()), \
             patch("app.services.analysis_service.LLMRouter.analyze", new=AsyncMock(side_effect=RuntimeError("LLM provider crashed"))):

            service = AnalysisService()
            payload = AnalysisRequestSchema(text="hello", analysis_type="summary")

            mock_session = AsyncMock()
            mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", mock_req.id))

            response = await service.analyze(payload, mock_session)

            assert response.status == "failed"
            assert response.result is None
