import os
import time
import asyncio
import logging
from dataclasses import dataclass
from typing import Literal

import anthropic
import google.generativeai as genai

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cost table (USD per 1K tokens)
# Gemini 1.5 Flash is free up to rate limits, then very cheap
# ---------------------------------------------------------------------------
COST_PER_1K_TOKENS = {
    "anthropic": {"input": 0.003, "output": 0.015},   # Claude 3.5 Sonnet
    "gemini":    {"input": 0.0,   "output": 0.0},     # Free tier = $0
}

ANTHROPIC_MODEL = "claude-sonnet-4-6"
GEMINI_MODEL = "gemini-1.5-flash-latest"


# ---------------------------------------------------------------------------
# Shared result shape — analysis_service.py only ever sees this
# ---------------------------------------------------------------------------
@dataclass
class LLMResult:
    output: dict
    tokens_input: int
    tokens_output: int
    cost_usd: float
    duration_ms: int
    provider: Literal["anthropic", "gemini"]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _estimate_cost(provider: str, tokens_input: int, tokens_output: int) -> float:
    rates = COST_PER_1K_TOKENS[provider]
    return (tokens_input / 1000 * rates["input"]) + (tokens_output / 1000 * rates["output"])


def _build_prompt(text: str, analysis_type: str, context_chunks: list[str] | None = None) -> str:
    """
    Assemble the user-facing prompt.
    context_chunks is injected here when RAG is active — None means plain analysis.
    """
    context_block = ""
    if context_chunks:
        formatted = "\n\n---\n\n".join(context_chunks)
        context_block = f"\n\nRelevant context from the document:\n{formatted}\n"

    if analysis_type == "summary":
        instruction = "Provide a concise summary of the following text."
    elif analysis_type == "key_points":
        instruction = "Extract the key points from the following text as a bullet list."
    else:
        instruction = f"Perform a '{analysis_type}' analysis of the following text."

    return f"{instruction}{context_block}\n\nText:\n{text}"


# ---------------------------------------------------------------------------
# Provider calls
# ---------------------------------------------------------------------------

async def _call_anthropic(prompt: str) -> LLMResult:
    start = time.time()
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = await client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    duration_ms = int((time.time() - start) * 1000)
    tokens_input = response.usage.input_tokens
    tokens_output = response.usage.output_tokens
    content = response.content[0].text

    return LLMResult(
        output={"content": content},
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        cost_usd=_estimate_cost("anthropic", tokens_input, tokens_output),
        duration_ms=duration_ms,
        provider="anthropic",
    )


async def _call_gemini(prompt: str) -> LLMResult:
    start = time.time()

    # Gemini's SDK is sync — run in a thread to avoid blocking the event loop
    response = await asyncio.to_thread(_generate_content, prompt)

    duration_ms = int((time.time() - start) * 1000)

    # Gemini returns token counts in usage_metadata
    tokens_input = getattr(response.usage_metadata, "prompt_token_count", 0)
    tokens_output = getattr(response.usage_metadata, "candidates_token_count", 0)
    content = response.text

    return LLMResult(
        output={"content": content},
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        cost_usd=_estimate_cost("gemini", tokens_input, tokens_output),
        duration_ms=duration_ms,
        provider="gemini",
    )


def _generate_content(prompt: str):
    """Run the synchronous Gemini SDK call in a separate thread."""
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(GEMINI_MODEL)
    return model.generate_content(prompt)


# ---------------------------------------------------------------------------
# Public interface — this is what analysis_service.py calls
# ---------------------------------------------------------------------------

class LLMRouter:
    """
    Tries Anthropic first. On any failure, falls back to Gemini.
    Raises RuntimeError only if both providers fail.
    """

    async def analyze(
        self,
        text: str,
        analysis_type: str,
        prompt_version: str,
        context_chunks: list[str] | None = None,
    ) -> LLMResult:
        prompt = _build_prompt(text, analysis_type, context_chunks)

        try:
            logger.info("Attempting Anthropic (%s)", ANTHROPIC_MODEL)
            return await _call_anthropic(prompt)
        except Exception as anthropic_err:
            logger.warning("Anthropic failed (%s), falling back to Gemini", anthropic_err)

        try:
            logger.info("Attempting Gemini (%s)", GEMINI_MODEL)
            return await _call_gemini(prompt)
        except Exception as gemini_err:
            logger.error("Gemini also failed: %s", gemini_err)
            raise RuntimeError(
                f"Both LLM providers failed. Gemini: {gemini_err}"
            )
