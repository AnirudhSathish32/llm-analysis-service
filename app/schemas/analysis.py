from dataclasses import Field
from pydantic import BaseModel
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

class AnalysisRequestSchema(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)
    analysis_type: Literal["summary", "key_points"]
    prompt_version: str = "v1"


class AnalysisResponseSchema(BaseModel):
    request_id: UUID
    status: str
    result: Optional[dict]
    cached: bool


class StoredAnalysisSchema(BaseModel):
    request_id: UUID
    analysis_type: str
    result: Optional[dict]
    created_at: datetime
    token_usage: int
    cost_usd: float
