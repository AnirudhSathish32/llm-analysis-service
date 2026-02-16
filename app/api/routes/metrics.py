from fastapi import APIRouter

router = APIRouter(prefix="/v1/metrics", tags=["metrics"])

@router.get("/usage")
async def usage():
    return {
        "message": "Usage aggregation would live here"
    }
