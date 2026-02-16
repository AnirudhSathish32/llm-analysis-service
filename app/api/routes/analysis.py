from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.analysis import AnalysisRequestSchema, AnalysisResponseSchema
from app.services.analysis_service import AnalysisService
from app.db.session import get_session
from app.core.rate_limit import rate_limiter

router = APIRouter(prefix="/v1/analysis", tags=["analysis"])
service = AnalysisService()

@router.post("", response_model=AnalysisResponseSchema, dependencies=[Depends(rate_limiter)])
async def analyze(
    payload: AnalysisRequestSchema,
    session: AsyncSession = Depends(get_session),
):
    return await service.analyze(payload, session)
