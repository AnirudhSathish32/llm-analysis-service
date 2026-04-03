---
slice: 2
task: fix-medium-issues
status: completed
dependencies: none
---

# Slice 2: Make LLM and Pinecone clients singletons

## Goal
LLM clients (Anthropic, Gemini) and Pinecone client are created on every call. Convert to module-level singletons to avoid repeated network handshakes and initialization overhead.

## Files to Modify
- `app/services/llm_router.py` — create `anthropic_client` and `gemini_model` at module level
- `app/services/rag_pipeline.py` — create `pinecone_index` and embed `genai.configure()` at module init

## Tests
- `test_llm_router_reuses_anthropic_client` — verify same instance across calls
- `test_rag_pipeline_reuses_pinecone_index` — verify same instance across calls

## Commit Message
perf(clients): make LLM and Pinecone clients module-level singletons

## Acceptance Criteria
- [ ] `anthropic.AsyncAnthropic` instantiated once at module level
- [ ] `genai.configure()` called once at module level
- [ ] `Pinecone()` instantiated once at module level
- [ ] All existing tests still pass
