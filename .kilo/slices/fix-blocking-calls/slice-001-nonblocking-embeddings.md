---
slice: 1
task: fix-blocking-calls
status: completed
dependencies: none
severity: medium
---

# Slice 1: Make RAG embedding calls non-blocking

## Goal
Wrap synchronous `genai.embed_content()` calls in `asyncio.to_thread()` to prevent event loop blocking.

## Files to Create/Modify
- `app/services/rag_pipeline.py` — wrap `_embed_texts` and `_embed_query_text` calls in `asyncio.to_thread()`

## What It Builds
Non-blocking RAG pipeline that doesn't starve the event loop during embedding.

## Tests
(severity: medium — 4 tests)
- `test_embed_texts_runs_in_separate_thread` — verify embedding doesn't block event loop
- `test_embed_query_text_runs_in_separate_thread` — verify query embedding doesn't block
- `test_ingest_document_is_fully_async` — verify ingest_document doesn't block
- `test_retrieve_chunks_is_fully_async` — verify retrieve_chunks doesn't block

## Dependencies
none

## Commit Message
perf(rag): make embedding calls non-blocking with asyncio.to_thread

## Acceptance Criteria
- [ ] `_embed_texts` runs in a separate thread
- [ ] `_embed_query_text` runs in a separate thread
- [ ] All existing tests still pass
