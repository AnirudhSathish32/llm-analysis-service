import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import OperationalError


# =============================================================================
# Metrics endpoints
# =============================================================================

class TestMetricsEndpoints:
    @pytest.mark.asyncio
    async def test_usage_returns_aggregated_counts(self):
        from app.api.routes.metrics import usage

        mock_row = MagicMock()
        mock_row.total_requests = 42
        mock_row.total_tokens = 10000
        mock_row.total_cost_usd = 0.50
        mock_row.avg_duration_ms = 250.0

        mock_result = MagicMock()
        mock_result.one = MagicMock(return_value=mock_row)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = await usage(session=mock_session)

        assert response["total_requests"] == 42
        assert response["total_tokens"] == 10000
        assert response["total_cost_usd"] == 0.50
        assert response["avg_duration_ms"] == 250.0

    @pytest.mark.asyncio
    async def test_usage_returns_zero_for_empty_db(self):
        from app.api.routes.metrics import usage

        mock_row = MagicMock()
        mock_row.total_requests = None
        mock_row.total_tokens = None
        mock_row.total_cost_usd = None
        mock_row.avg_duration_ms = None

        mock_result = MagicMock()
        mock_result.one = MagicMock(return_value=mock_row)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = await usage(session=mock_session)

        assert response["total_requests"] == 0
        assert response["total_tokens"] == 0
        assert response["total_cost_usd"] == 0.0
        assert response["avg_duration_ms"] == 0.0

    @pytest.mark.asyncio
    async def test_usage_by_type_returns_breakdown(self):
        from app.api.routes.metrics import usage_by_type

        row1 = MagicMock()
        row1.analysis_type = "summary"
        row1.total_requests = 30
        row1.total_tokens = 6000
        row1.total_cost_usd = 0.30

        row2 = MagicMock()
        row2.analysis_type = "key_points"
        row2.total_requests = 12
        row2.total_tokens = 4000
        row2.total_cost_usd = 0.20

        mock_result = MagicMock()
        mock_result.all = MagicMock(return_value=[row1, row2])

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = await usage_by_type(session=mock_session)

        assert len(response) == 2
        summary = next(r for r in response if r["analysis_type"] == "summary")
        assert summary["total_requests"] == 30
        assert summary["total_cost_usd"] == 0.30

    @pytest.mark.asyncio
    async def test_usage_by_type_returns_empty_for_no_data(self):
        from app.api.routes.metrics import usage_by_type

        mock_result = MagicMock()
        mock_result.all = MagicMock(return_value=[])

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = await usage_by_type(session=mock_session)

        assert response == []

    @pytest.mark.asyncio
    async def test_usage_handles_db_error_gracefully(self):
        from app.api.routes.metrics import usage
        from fastapi import HTTPException

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(
            side_effect=OperationalError("stmt", [], Exception("DB down"))
        )

        with pytest.raises(HTTPException) as exc_info:
            await usage(session=mock_session)

        assert exc_info.value.status_code == 500
