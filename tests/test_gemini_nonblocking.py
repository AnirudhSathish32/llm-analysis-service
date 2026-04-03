import asyncio
import threading
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


# =============================================================================
# Gemini non-blocking call
# =============================================================================

class TestGeminiNonBlocking:
    def test_gemini_call_returns_valid_result(self):
        from app.services.llm_router import _call_gemini

        mock_response = MagicMock()
        mock_response.text = "test content"
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 20

        with patch("app.services.llm_router._generate_content", return_value=mock_response):
            result = asyncio.get_event_loop().run_until_complete(_call_gemini("test"))

        assert result.output["content"] == "test content"
        assert result.tokens_input == 10
        assert result.tokens_output == 20
        assert result.provider == "gemini"

    def test_gemini_call_runs_in_separate_thread(self):
        from app.services.llm_router import _call_gemini

        captured_thread_ids = {}

        def fake_generate(prompt):
            captured_thread_ids["main"] = threading.current_thread() is threading.main_thread()
            captured_thread_ids["thread"] = threading.current_thread().name
            mock_response = MagicMock()
            mock_response.text = "ok"
            mock_response.usage_metadata.prompt_token_count = 1
            mock_response.usage_metadata.candidates_token_count = 1
            return mock_response

        with patch("app.services.llm_router._generate_content", side_effect=fake_generate):
            asyncio.get_event_loop().run_until_complete(_call_gemini("test"))

        assert captured_thread_ids["main"] is False

    def test_gemini_call_propagates_api_error(self):
        from app.services.llm_router import _call_gemini

        with patch("app.services.llm_router._generate_content", side_effect=RuntimeError("API error")):
            with pytest.raises(RuntimeError, match="API error"):
                asyncio.get_event_loop().run_until_complete(_call_gemini("test"))

    def test_gemini_call_respects_timeout(self):
        from app.services.llm_router import _call_gemini

        def slow_generate(prompt):
            import time
            time.sleep(10)
            mock_response = MagicMock()
            mock_response.text = "ok"
            mock_response.usage_metadata.prompt_token_count = 1
            mock_response.usage_metadata.candidates_token_count = 1
            return mock_response

        with patch("app.services.llm_router._generate_content", side_effect=slow_generate):
            with pytest.raises(asyncio.TimeoutError):
                asyncio.get_event_loop().run_until_complete(
                    asyncio.wait_for(_call_gemini("test"), timeout=0.1)
                )
