import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
 
from app.schemas.analysis import AnalysisRequestSchema, AnalysisResponseSchema, CitationSchema
from app.services.llm_router import LLMRouter
from app.services.rag_pipeline import retrieve_chunks
from app.utils.hashing import hash_input
from app.cache.redis import redis_client
from app.core.config import settings
from app.db.models import AnalysisRequest, AnalysisResult
 
 
class AnalysisService:
    def __init__(self):
        self.llm = LLMRouter()
 
    async def analyze(
        self,
        payload: AnalysisRequestSchema,
        session: AsyncSession,
    ) -> AnalysisResponseSchema:
 
        input_hash = hash_input(
            payload.text,
            payload.analysis_type,
            payload.prompt_version,
            document_id=payload.document_id,
        )
 
        cache_key = f"analysis:{input_hash}"
        cached = await redis_client.get(cache_key)
        if cached:
            return AnalysisResponseSchema(
                request_id=uuid.UUID(cached.split(":")[0]),
                status="completed",
                result=None,
                cached=True,
            )
 
        req = AnalysisRequest(
            input_hash=input_hash,
            analysis_type=payload.analysis_type,
            prompt_version=payload.prompt_version,
            status="processing",
        )
        session.add(req)
        await session.commit()
        await session.refresh(req)
 
        try:
            # --- RAG retrieval ---
            context_chunks = None
            citations = None
            rag_chunks_used = 0
 
            if payload.document_id:
                raw_chunks = await retrieve_chunks(
                    document_id=payload.document_id,
                    query=payload.text,
                )
                context_chunks = [chunk["text"] for chunk in raw_chunks]
                rag_chunks_used = len(context_chunks)
 
                # Build citation objects from the metadata RAG already retrieved
                citations = [
                    CitationSchema(
                        chunk_index=i,
                        page=chunk.get("page", "unknown"),
                        source=chunk.get("source", "unknown"),
                    )
                    for i, chunk in enumerate(raw_chunks)
                ]
 
            # --- LLM call ---
            result = await asyncio.wait_for(
                self.llm.analyze(
                    payload.text,
                    payload.analysis_type,
                    payload.prompt_version,
                    context_chunks=context_chunks,
                ),
                timeout=settings.llm_timeout_seconds,
            )
 
            session.add(
                AnalysisResult(
                    request_id=req.id,
                    result=result.output,
                    duration_ms=result.duration_ms,
                    token_usage=result.tokens_input + result.tokens_output,
                    cost_usd=result.cost_usd,
                )
            )
 
            req.status = "completed"
            await session.commit()
 
            await redis_client.set(
                cache_key, f"{req.id}", ex=settings.cache_ttl_seconds
            )
 
            return AnalysisResponseSchema(
                request_id=req.id,
                status="completed",
                result=result.output,
                cached=False,
                provider=result.provider,
                rag_chunks_used=rag_chunks_used,
                citations=citations,
            )
 
        except Exception:
            req.status = "failed"
            await session.commit()
            return AnalysisResponseSchema(
                request_id=req.id,
                status="failed",
                result=None,
                cached=False,
            )



