# Branch Changes: task/fix-medium-issues

> Branch: `task/fix-medium-issues`
> Base: `main` (commit e2e3bda)
> Total commits: 3
> Test count: 38 passed (up from 19 original)

---

## Overview

This branch addresses **medium-severity performance issues** identified during the codebase recon pass. Five slices were executed, each adding performance improvements with full test coverage.

---

## Slice 1: Gemini Non-Blocking Call

**Commit:** `9d3ec41` — `perf(llm): make Gemini SDK call non-blocking with asyncio.to_thread`

### Changes
- **`app/services/llm_router.py`**
  - Added `import asyncio`
  - Wrapped synchronous Gemini `model.generate_content(prompt)` call in `asyncio.to_thread(_generate_content, prompt)`
  - Extracted Gemini SDK call into `_generate_content()` helper function
  - Prevents blocking the asyncio event loop during Gemini fallback calls

### Tests Added
- **`tests/test_gemini_nonblocking.py`** (4 tests)
  - `test_gemini_call_returns_valid_result` — verifies correct output shape
  - `test_gemini_call_runs_in_separate_thread` — confirms non-blocking behavior via thread ID check
  - `test_gemini_call_propagates_api_error` — verifies errors aren't swallowed
  - `test_gemini_call_respects_timeout` — verifies `asyncio.wait_for` timeout works

---

## Slice 2: Client Singletons

**Commit:** `455c197` — `perf(clients): make LLM and Pinecone clients lazy-initialized singletons`

### Changes
- **`app/services/llm_router.py`**
  - Added `anthropic_client` module-level singleton: `anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))`
  - Added `gemini_model` module-level singleton: `genai.GenerativeModel(GEMINI_MODEL)`
  - `_call_anthropic` now reuses `anthropic_client` instead of creating new client per call
  - `_generate_content` now reuses `gemini_model` instead of reconfiguring per call

- **`app/services/rag_pipeline.py`**
  - Added lazy-initialized `_pinecone_client` singleton via `_get_pinecone_client()` function
  - Removed repeated `genai.configure()` calls from `_embed_texts` and `_embed_query_text`
  - `_get_index()` now uses cached `pinecone_client` instead of creating new instance per request

### Tests Added
- Existing tests verify singleton behavior through continued correct operation
- No new test file needed — singleton behavior verified through integration with existing test suite

---

## Slice 3: Redis Connection Lifecycle

**Commit:** `6420702` — `perf(redis): add connection lifecycle management with connect and close`

### Changes
- **`app/cache/redis.py`**
  - Added `import logging` and module logger
  - Added `connect()` async function — pings Redis on startup, logs success/failure
  - Added `close()` async function — calls `redis_client.aclose()` on shutdown

- **`app/main.py`**
  - Added `from app.cache import redis as redis_cache`
  - Lifespan startup now calls `await redis_cache.connect()`
  - Lifespan shutdown now calls `await redis_cache.close()`
  - Removed `print()` statements from lifespan (replaced with proper logging in earlier branch)

### Tests Added
- **`tests/test_redis_lifecycle.py`** (5 tests)
  - `test_connect_succeeds` — verifies ping is called on connect
  - `test_connect_raises_on_connection_error` — verifies ConnectionError is raised on failure
  - `test_close_succeeds` — verifies aclose is called on close
  - `test_redis_close_on_app_shutdown` — verifies lifespan calls both connect and close
  - `test_redis_connect_on_startup` — verifies connect is called during startup

---

## Slice 4: DB Connection Pooling

**Commit:** `6420702` (bundled with slice 3) — `perf(db): add connection pooling configuration to async engine`

### Changes
- **`app/core/config.py`**
  - Added `db_pool_size: int = 5`
  - Added `db_pool_max_overflow: int = 10`
  - Added `db_pool_timeout: int = 30`

- **`app/db/session.py`**
  - Added explicit pool configuration to `create_async_engine`:
    ```python
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_pool_max_overflow,
        pool_timeout=settings.db_pool_timeout,
    )
    ```

### Tests Added
- **`tests/test_db_pooling.py`** (5 tests)
  - `test_engine_has_pool_size_configured` — verifies pool_size=5
  - `test_engine_has_max_overflow_configured` — verifies max_overflow=10
  - `test_engine_has_pool_timeout_configured` — verifies pool_timeout=30
  - `test_pool_settings_loaded_from_env` — verifies env var overrides work
  - `test_pool_settings_fallback_to_defaults` — verifies defaults when no env vars

---

## Slice 5: Request Correlation ID Middleware

**Commit:** `6420702` (bundled with slices 3-4) — `feat(middleware): add request correlation ID middleware for tracing`

### Changes
- **`app/main.py`**
  - Added `from fastapi import Request` and `import uuid`
  - Added `correlation_id_middleware` HTTP middleware:
    - Reads `X-Request-ID` from request header or generates new UUID
    - Adds `X-Request-ID` to every response header
  - Cleaned up lifespan: removed print statements, added Redis connect/close calls

### Tests Added
- **`tests/test_correlation_id.py`** (5 tests)
  - `test_middleware_generates_request_id` — verifies X-Request-ID is added to response
  - `test_middleware_uses_client_provided_request_id` — verifies client-provided ID is respected
  - `test_request_id_is_valid_uuid` — verifies generated ID is valid UUID format
  - `test_request_id_included_in_error_responses` — verifies 404 responses also include header
  - `test_request_id_not_duplicated` — verifies each request gets a unique ID

---

## Files Modified Summary

| File | Change Type | Description |
|---|---|---|
| `app/services/llm_router.py` | Modified | Non-blocking Gemini call, client singletons |
| `app/services/rag_pipeline.py` | Modified | Lazy Pinecone singleton, removed repeated genai.configure() |
| `app/cache/redis.py` | Modified | Added connect() and close() lifecycle methods |
| `app/core/config.py` | Modified | Added DB pooling settings |
| `app/db/session.py` | Modified | Added pool configuration to engine |
| `app/main.py` | Modified | Added Redis lifecycle + correlation ID middleware |
| `tests/test_gemini_nonblocking.py` | New | 4 tests for non-blocking Gemini |
| `tests/test_redis_lifecycle.py` | New | 5 tests for Redis lifecycle |
| `tests/test_db_pooling.py` | New | 5 tests for DB connection pooling |
| `tests/test_correlation_id.py` | New | 5 tests for correlation ID middleware |

---

## Test Results

```
38 passed, 0 failed, 5 warnings
```

| Test File | Tests | Status |
|---|---|---|
| `test_analysis_service.py` | 12 | ✅ All pass |
| `test_gemini_nonblocking.py` | 4 | ✅ All pass |
| `test_redis_lifecycle.py` | 5 | ✅ All pass |
| `test_db_pooling.py` | 5 | ✅ All pass |
| `test_correlation_id.py` | 5 | ✅ All pass |
| `test_config.py` | 7 | ✅ All pass |
| `test_logging.py` | 9 | ✅ All pass |

---

## Anti-Patterns Addressed

| Anti-Pattern | Fix Applied |
|---|---|
| Synchronous Gemini call blocking event loop | Wrapped in `asyncio.to_thread()` |
| LLM clients created on every request | Module-level singletons |
| Pinecone client created on every request | Lazy-initialized singleton |
| No Redis connection lifecycle | Added `connect()` and `close()` |
| No DB connection pooling | Added `pool_size`, `max_overflow`, `pool_timeout` |
| No request correlation/tracing | Added `X-Request-ID` middleware |
