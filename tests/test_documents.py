import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime, timezone


# =============================================================================
# Get document endpoint
# =============================================================================

class TestGetDocument:
    @pytest.mark.asyncio
    async def test_get_document_success(self):
        from app.api.routes.documents import get_document
        from app.db.models import Document

        doc_id = uuid.uuid4()
        mock_doc = MagicMock(spec=Document)
        mock_doc.id = doc_id
        mock_doc.filename = "report.pdf"
        mock_doc.status = "ready"
        mock_doc.chunk_count = 15
        mock_doc.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_doc)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = await get_document(document_id=str(doc_id), session=mock_session)

        assert response["document_id"] == str(doc_id)
        assert response["filename"] == "report.pdf"
        assert response["status"] == "ready"
        assert response["chunk_count"] == 15

    @pytest.mark.asyncio
    async def test_get_document_returns_404(self):
        from app.api.routes.documents import get_document
        from fastapi import HTTPException

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await get_document(document_id=str(uuid.uuid4()), session=mock_session)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_document_rejects_invalid_uuid(self):
        from app.api.routes.documents import get_document

        mock_session = AsyncMock()

        with pytest.raises(ValueError):
            await get_document(document_id="not-a-uuid", session=mock_session)

    @pytest.mark.asyncio
    async def test_get_document_returns_processing_status(self):
        from app.api.routes.documents import get_document
        from app.db.models import Document

        doc_id = uuid.uuid4()
        mock_doc = MagicMock(spec=Document)
        mock_doc.id = doc_id
        mock_doc.filename = "uploading.csv"
        mock_doc.status = "processing"
        mock_doc.chunk_count = None
        mock_doc.created_at = datetime.now(timezone.utc)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_doc)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = await get_document(document_id=str(doc_id), session=mock_session)

        assert response["status"] == "processing"
        assert response["chunk_count"] is None
