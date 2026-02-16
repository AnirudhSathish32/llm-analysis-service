from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Annotated
from uuid import UUID
from datetime import datetime


class AnalysisRequestSchema(BaseModel):
    text: Annotated[str, Field()]
    analysis_type: Literal["summary", "key_points"]
    prompt_version: str = "v1"

    @field_validator("text")
    def text_length(cls, v):
        if not (1 <= len(v) <= 10000):
            raise ValueError("Text must be between 1 and 10,000 characters")
        return v

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
