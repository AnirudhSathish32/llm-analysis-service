import uuid
from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base

class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    input_hash = Column(String, index=True, nullable=False)
    analysis_type = Column(String, nullable=False)
    prompt_version = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    request_id = Column(UUID(as_uuid=True), ForeignKey("analysis_requests.id"), primary_key=True)
    result = Column(JSON, nullable=True)
    duration_ms = Column(Integer)
    token_usage = Column(Integer)
    cost_usd = Column(Numeric(10, 4))
