import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
 
from app.schemas.analysis import AnalysisRequestSchema
from app.services.analysis_service import AnalysisService
from app.services.llm_router import LLMRouter, LLMResult, _build_prompt
from app.utils.hashing import hash_input
 
 
# =============================================================================
# Hashing
# =============================================================================
 
class TestHashInput:
    def test_same_inputs_produce_same_hash(self):
        h1 = hash_input("hello", "summary", "v1")
        h2 = hash_input("hello", "summary", "v1")
        assert h1 == h2
 
    def test_different_text_produces_different_hash(self):
        h1 = hash_input("hello", "summary", "v1")
        h2 = hash_input("world", "summary", "v1")
        assert h1 != h2
 
    def test_different_document_id_produces_different_hash(self):
        h1 = hash_input("hello", "summary", "v1", document_id="doc-a")
        h2 = hash_input("hello", "summary", "v1", document_id="doc-b")
        assert h1 != h2
 
    def test_no_document_id_and_none_are_equivalent(self):
        h1 = hash_input("hello", "summary", "v1")
        h2 = hash_input("hello", "summary", "v1", document_id=None)
        assert h1 == h2
 
 
# =============================================================================
# Schema validation
# =============================================================================
 
class TestAnalysisRequestSchema:
    def test_valid_payload(self):
        payload = AnalysisRequestSchema(text="hello world", analysis_type="summary")
        assert payload.text == "hello world"
        assert payload.prompt_version == "v1"
        assert payload.document_id is None
 
    def test_text_too_short_raises(self):
        with pytest.raises(Exception):
            AnalysisRequestSchema(text="", analysis_type="summary")
 
    def test_text_too_long_raises(self):
        with pytest.raises(Exception):
            AnalysisRequestSchema(text="x" * 10001, analysis_type="summary")
 
    def test_invalid_analysis_type_raises(self):
        with pytest.raises(Exception):
            AnalysisRequestSchema(text="hello", analysis_type="invalid_type")
 
    def test_document_id_accepted(self):
        payload = AnalysisRequestSchema(
            text="hello", analysis_type="summary", document_id="abc-123"
        )
        assert payload.document_id == "abc-123"
 
 
# =============================================================================
# Prompt builder
# =============================================================================
 
class TestBuildPrompt:
    def test_summary_instruction_present(self):
        prompt = _build_prompt("some text", "summary")
        assert "summary" in prompt.lower()
        assert "some text" in prompt
 
    def test_key_points_instruction_present(self):
        prompt = _build_prompt("some text", "key_points")
        assert "key points" in prompt.lower()
 
    def test_context_chunks_injected(self):
        chunks = ["chunk one", "chunk two"]
        prompt = _build_prompt("question", "summary", context_chunks=chunks)
        assert "chunk one" in prompt
        assert "chunk two" in prompt
 
    def test_no_context_chunks_omits_context_block(self):
        prompt = _build_prompt("question", "summary", context_chunks=None)
        assert "Relevant context" not in prompt
 
 
# =============================================================================
# LLM Router — fallback behaviour
# =============================================================================
 
class TestLLMRouter:
    @pytest.mark.asyncio
    async def test_returns_anthropic_result_when_successful(self):
        mock_result = LLMResult(
            output={"content": "test"},
            tokens_input=10,
            tokens_output=20,
            cost_usd=0.001,
            duration_ms=100,
            provider="anthropic",
        )
        with patch(
            "app.services.llm_router._call_anthropic",
            new=AsyncMock(return_value=mock_result),
        ):
            router = LLMRouter()
            result = await router.analyze("text", "summary", "v1")
            assert result.provider == "anthropic"
 
    @pytest.mark.asyncio
    async def test_falls_back_to_gemini_when_anthropic_fails(self):
        mock_result = LLMResult(
            output={"content": "gemini response"},
            tokens_input=10,
            tokens_output=20,
            cost_usd=0.0,
            duration_ms=200,
            provider="gemini",
        )
        with patch(
            "app.services.llm_router._call_anthropic",
            new=AsyncMock(side_effect=Exception("Anthropic down")),
        ), patch(
            "app.services.llm_router._call_gemini",
            new=AsyncMock(return_value=mock_result),
        ):
            router = LLMRouter()
            result = await router.analyze("text", "summary", "v1")
            assert result.provider == "gemini"
 
    @pytest.mark.asyncio
    async def test_raises_when_both_providers_fail(self):
        with patch(
            "app.services.llm_router._call_anthropic",
            new=AsyncMock(side_effect=Exception("Anthropic down")),
        ), patch(
            "app.services.llm_router._call_gemini",
            new=AsyncMock(side_effect=Exception("Gemini down")),
        ):
            router = LLMRouter()
            with pytest.raises(RuntimeError, match="Both LLM providers failed"):
                await router.analyze("text", "summary", "v1")
 
 
# =============================================================================
# Analysis Service — cache and RAG integration
# =============================================================================
 
class TestAnalysisService:
    def _make_llm_result(self, provider="anthropic"):
        return LLMResult(
            output={"content": "mocked answer"},
            tokens_input=50,
            tokens_output=100,
            cost_usd=0.002,
            duration_ms=300,
            provider=provider,
        )
 
    @pytest.mark.asyncio
    async def test_returns_cached_response_when_cache_hit(self):
        request_id = str(uuid4())
 
        with patch(
            "app.services.analysis_service.redis_client.get",
            new=AsyncMock(return_value=f"{request_id}"),
        ):
            service = AnalysisService()
            payload = AnalysisRequestSchema(text="hello", analysis_type="summary")
            mock_session = AsyncMock()
 
            response = await service.analyze(payload, mock_session)
 
            assert response.cached is True
            assert str(response.request_id) == request_id
 
    @pytest.mark.asyncio
    async def test_calls_llm_and_persists_result_on_cache_miss(self):
        mock_req = MagicMock()
        mock_req.id = uuid4()
        mock_req.status = "processing"
 
        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(return_value=None)), \
             patch("app.services.analysis_service.redis_client.set", new=AsyncMock()), \
             patch.object(LLMRouter, "analyze", new=AsyncMock(return_value=self._make_llm_result())):
 
            service = AnalysisService()
            payload = AnalysisRequestSchema(text="hello world", analysis_type="summary")
 
            mock_session = AsyncMock()
            mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", mock_req.id))
 
            response = await service.analyze(payload, mock_session)
 
            assert response.cached is False
            assert response.status == "completed"
            assert response.provider == "anthropic"
 
    @pytest.mark.asyncio
    async def test_rag_chunks_included_when_document_id_provided(self):
        mock_req = MagicMock()
        mock_req.id = uuid4()
 
        mock_chunks = [
            {"text": "chunk one", "page": "1", "source": "doc.pdf"},
            {"text": "chunk two", "page": "2", "source": "doc.pdf"},
        ]
 
        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(return_value=None)), \
             patch("app.services.analysis_service.redis_client.set", new=AsyncMock()), \
             patch("app.services.analysis_service.retrieve_chunks", new=AsyncMock(return_value=mock_chunks)), \
             patch.object(LLMRouter, "analyze", new=AsyncMock(return_value=self._make_llm_result())):
 
            service = AnalysisService()
            payload = AnalysisRequestSchema(
                text="what is this about?",
                analysis_type="summary",
                document_id="doc-123",
            )
 
            mock_session = AsyncMock()
            mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", mock_req.id))
 
            response = await service.analyze(payload, mock_session)
 
            assert response.rag_chunks_used == 2
            assert len(response.citations) == 2
            assert response.citations[0].page == "1"
            assert response.citations[1].source == "doc.pdf"


# =============================================================================
# Analysis Service — specific exception handling
# =============================================================================

class TestAnalysisServiceExceptions:
    def _make_llm_result(self, provider="anthropic"):
        return LLMResult(
            output={"content": "mocked answer"},
            tokens_input=50,
            tokens_output=100,
            cost_usd=0.002,
            duration_ms=300,
            provider=provider,
        )

    @pytest.mark.asyncio
    async def test_analysis_returns_failed_on_cache_error(self):
        mock_req = MagicMock()
        mock_req.id = uuid4()

        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(side_effect=ConnectionError("Redis down"))), \
             patch("app.services.analysis_service.redis_client.set", new=AsyncMock()), \
             patch.object(LLMRouter, "analyze", new=AsyncMock(return_value=self._make_llm_result())):

            service = AnalysisService()
            payload = AnalysisRequestSchema(text="hello", analysis_type="summary")

            mock_session = AsyncMock()
            mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", mock_req.id))

            response = await service.analyze(payload, mock_session)

            assert response.status == "completed"
            assert response.cached is False
            assert response.cached is False

    @pytest.mark.asyncio
    async def test_returns_failed_status_on_rag_retrieval_error(self):
        mock_req = MagicMock()
        mock_req.id = uuid4()

        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(return_value=None)), \
             patch("app.services.analysis_service.redis_client.set", new=AsyncMock()), \
             patch("app.services.analysis_service.retrieve_chunks", new=AsyncMock(side_effect=Exception("Pinecone down"))):

            service = AnalysisService()
            payload = AnalysisRequestSchema(
                text="what is this?",
                analysis_type="summary",
                document_id="doc-123",
            )

            mock_session = AsyncMock()
            mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", mock_req.id))

            response = await service.analyze(payload, mock_session)

            assert response.status == "failed"
            assert response.cached is False

    @pytest.mark.asyncio
    async def test_returns_failed_status_on_db_error(self, caplog):
        from sqlalchemy.exc import OperationalError
        from app.db.models import AnalysisRequest

        call_count = 0

        async def flaky_commit():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                raise OperationalError("stmt", [], Exception("DB down"))

        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(return_value=None)), \
             patch("app.services.analysis_service.redis_client.set", new=AsyncMock()), \
             patch.object(LLMRouter, "analyze", new=AsyncMock(return_value=self._make_llm_result())), \
             patch("app.services.analysis_service.AnalysisRequest", autospec=True) as MockRequest:

            MockRequest.return_value.id = uuid4()

            service = AnalysisService()
            payload = AnalysisRequestSchema(text="hello", analysis_type="summary")

            mock_session = AsyncMock()
            mock_session.commit = flaky_commit

            response = await service.analyze(payload, mock_session)

            assert response.status == "failed"
            assert response.cached is False
            assert any("Database error" in record.message for record in caplog.records)


# =============================================================================
# Analysis Service — failure paths and caching
# =============================================================================

class TestAnalysisServiceFailurePaths:
    def _make_llm_result(self, provider="anthropic"):
        return LLMResult(
            output={"content": "mocked answer"},
            tokens_input=50,
            tokens_output=100,
            cost_usd=0.002,
            duration_ms=300,
            provider=provider,
        )

    @pytest.mark.asyncio
    async def test_analysis_returns_failed_on_llm_timeout(self):
        mock_req = MagicMock()
        mock_req.id = uuid4()

        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(return_value=None)), \
             patch("app.services.analysis_service.redis_client.set", new=AsyncMock()), \
             patch("app.services.analysis_service.asyncio.wait_for", new=AsyncMock(side_effect=TimeoutError("timed out"))):

            service = AnalysisService()
            payload = AnalysisRequestSchema(text="hello", analysis_type="summary")

            mock_session = AsyncMock()
            mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", mock_req.id))

            response = await service.analyze(payload, mock_session)

            assert response.status == "failed"
            assert response.cached is False

    @pytest.mark.asyncio
    async def test_analysis_returns_failed_on_rag_failure(self):
        mock_req = MagicMock()
        mock_req.id = uuid4()

        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(return_value=None)), \
             patch("app.services.analysis_service.redis_client.set", new=AsyncMock()), \
             patch("app.services.analysis_service.retrieve_chunks", new=AsyncMock(side_effect=Exception("Pinecone error"))):

            service = AnalysisService()
            payload = AnalysisRequestSchema(
                text="what is this?",
                analysis_type="summary",
                document_id="doc-123",
            )

            mock_session = AsyncMock()
            mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", mock_req.id))

            response = await service.analyze(payload, mock_session)

            assert response.status == "failed"
            assert response.cached is False

    @pytest.mark.asyncio
    async def test_analysis_returns_failed_on_cache_error(self):
        mock_req = MagicMock()
        mock_req.id = uuid4()

        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(side_effect=ConnectionError("Redis down"))), \
             patch("app.services.analysis_service.redis_client.set", new=AsyncMock()), \
             patch.object(LLMRouter, "analyze", new=AsyncMock(return_value=self._make_llm_result())):

            service = AnalysisService()
            payload = AnalysisRequestSchema(text="hello", analysis_type="summary")

            mock_session = AsyncMock()
            mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", mock_req.id))

            response = await service.analyze(payload, mock_session)

            assert response.status == "completed"
            assert response.cached is False

    @pytest.mark.asyncio
    async def test_analysis_caches_successful_result(self):
        mock_req = MagicMock()
        mock_req.id = uuid4()

        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(return_value=None)), \
             patch("app.services.analysis_service.redis_client.set", new=AsyncMock()) as mock_set, \
             patch.object(LLMRouter, "analyze", new=AsyncMock(return_value=self._make_llm_result())):

            service = AnalysisService()
            payload = AnalysisRequestSchema(text="hello world", analysis_type="summary")

            mock_session = AsyncMock()
            mock_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, "id", mock_req.id))

            await service.analyze(payload, mock_session)

            mock_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_analysis_returns_cached_response(self):
        request_id = str(uuid4())

        with patch("app.services.analysis_service.redis_client.get", new=AsyncMock(return_value=f"{request_id}:cached")):
            service = AnalysisService()
            payload = AnalysisRequestSchema(text="hello", analysis_type="summary")
            mock_session = AsyncMock()

            response = await service.analyze(payload, mock_session)

            assert response.cached is True
            assert response.status == "completed"
