import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_session
from app.db.models import AnalysisRequest, AnalysisResult

router = APIRouter(prefix="/v1/metrics", tags=["metrics"])

logger = logging.getLogger(__name__)


@router.get("/usage")
async def usage(session: AsyncSession = Depends(get_session)):
    """
    Aggregate token usage and cost across all completed requests.
    """
    try:
        result = await session.execute(
            select(
                func.count(AnalysisResult.request_id).label("total_requests"),
                func.sum(AnalysisResult.token_usage).label("total_tokens"),
                func.sum(AnalysisResult.cost_usd).label("total_cost_usd"),
                func.avg(AnalysisResult.duration_ms).label("avg_duration_ms"),
            )
        )
        row = result.one()

        return {
            "total_requests": row.total_requests or 0,
            "total_tokens": row.total_tokens or 0,
            "total_cost_usd": float(row.total_cost_usd or 0),
            "avg_duration_ms": float(row.avg_duration_ms or 0),
        }
    except Exception as e:
        logger.exception("Failed to fetch usage metrics")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage metrics")


@router.get("/usage/by_type")
async def usage_by_type(session: AsyncSession = Depends(get_session)):
    """
    Break down request count and cost by analysis type (summary vs key_points).
    """
    try:
        result = await session.execute(
            select(
                AnalysisRequest.analysis_type,
                func.count(AnalysisResult.request_id).label("total_requests"),
                func.sum(AnalysisResult.token_usage).label("total_tokens"),
                func.sum(AnalysisResult.cost_usd).label("total_cost_usd"),
            )
            .join(AnalysisResult, AnalysisRequest.id == AnalysisResult.request_id)
            .group_by(AnalysisRequest.analysis_type)
        )

        return [
            {
                "analysis_type": row.analysis_type,
                "total_requests": row.total_requests,
                "total_tokens": row.total_tokens or 0,
                "total_cost_usd": float(row.total_cost_usd or 0),
            }
            for row in result.all()
        ]
    except Exception as e:
        logger.exception("Failed to fetch usage-by-type metrics")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage metrics")
