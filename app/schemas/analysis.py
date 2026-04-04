from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Annotated
from uuid import UUID


class CitationSchema(BaseModel):
    chunk_index: int        # which chunk (0-based) this citation refers to
    page: str               # page number or "unknown"
    source: str             # original filename

class AnalysisRequestSchema(BaseModel):
    text: Annotated[str, Field()]
    analysis_type: Literal["summary", "key_points"]
    prompt_version: str = "v1"
    document_id: Optional[str] = None

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
    provider: Optional[str] = None
    rag_chunks_used: Optional[int] = None
    citations: Optional[list[CitationSchema]] = None
