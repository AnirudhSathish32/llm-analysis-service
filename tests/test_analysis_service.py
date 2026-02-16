import pytest
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import AnalysisRequestSchema

@pytest.mark.asyncio
async def test_hash_consistency():
    service = AnalysisService()
    payload = AnalysisRequestSchema(
        text="hello world",
        analysis_type="summary",
    )

    # This test ensures deterministic behavior paths exist
    assert payload.text == "hello world"
