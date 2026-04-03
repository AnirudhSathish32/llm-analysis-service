import io
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


# =============================================================================
# File upload security
# =============================================================================

class TestUploadSecurity:
    def _make_upload(self, filename="test.pdf", content=b"test content"):
        from fastapi import UploadFile
        from starlette.datastructures import Headers
        upload = UploadFile(
            filename=filename,
            file=io.BytesIO(content),
            headers=Headers({"content-type": "application/pdf"}),
        )
        return upload

    @pytest.mark.asyncio
    async def test_upload_rejects_oversized_file(self):
        from app.api.routes.documents import upload_document
        from fastapi import HTTPException

        with patch("app.api.routes.documents.settings") as mock_settings:
            mock_settings.max_upload_bytes = 10

            with pytest.raises(HTTPException) as exc_info:
                await upload_document(
                    file=self._make_upload(content=b"x" * 100),
                    session=AsyncMock(),
                )

            assert exc_info.value.status_code == 413

    @pytest.mark.asyncio
    async def test_upload_accepts_valid_file(self):
        from app.api.routes.documents import upload_document
        import uuid

        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.api.routes.documents.settings") as mock_settings, \
             patch("app.api.routes.documents.ingest_document", new=AsyncMock(return_value=5)):
            mock_settings.max_upload_bytes = 10_485_760

            response = await upload_document(
                file=self._make_upload(content=b"valid content"),
                session=mock_session,
            )

            assert response["status"] == "ready"
            assert response["chunk_count"] == 5

    @pytest.mark.asyncio
    async def test_upload_sanitizes_path_traversal_filename(self):
        from app.api.routes.documents import upload_document
        import uuid

        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.api.routes.documents.settings") as mock_settings, \
             patch("app.api.routes.documents.ingest_document", new=AsyncMock(return_value=1)):
            mock_settings.max_upload_bytes = 10_485_760

            response = await upload_document(
                file=self._make_upload(filename="../../etc/passwd.pdf", content=b"test"),
                session=mock_session,
            )

            assert response["filename"] == "passwd.pdf"

    @pytest.mark.asyncio
    async def test_upload_rejects_empty_filename(self):
        from app.api.routes.documents import upload_document
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await upload_document(
                file=self._make_upload(filename=None, content=b"test"),
                session=AsyncMock(),
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_rejects_unsupported_extension(self):
        from app.api.routes.documents import upload_document
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await upload_document(
                file=self._make_upload(filename="malware.exe", content=b"test"),
                session=AsyncMock(),
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_returns_correct_error_shape(self):
        from app.api.routes.documents import upload_document
        from fastapi import HTTPException
        import uuid

        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.api.routes.documents.settings") as mock_settings, \
             patch("app.api.routes.documents.ingest_document", new=AsyncMock(side_effect=RuntimeError("DB down"))):
            mock_settings.max_upload_bytes = 10_485_760

            with pytest.raises(HTTPException) as exc_info:
                await upload_document(
                    file=self._make_upload(content=b"test"),
                    session=mock_session,
                )

            assert exc_info.value.status_code == 500
            assert "DB down" not in exc_info.value.detail
