# Fix Rate Limiting — Changes Summary

**Date:** 2026-04-04
**Branch:** wheat-bamboo
**Slices:** 3 (all completed)
**Tests:** 16 new, 96 total passing

---

## Overview

This work addresses three gaps in the rate limiting and input validation layer:

1. Rate limiting was only wired to the analysis endpoint — documents and metrics endpoints were unprotected
2. IP detection used `request.client.host` directly, which returns the load balancer IP in production
3. `document_id` parameter accepted any string, causing 500 errors on malformed UUIDs

---

## Changes

### `app/core/rate_limit.py`

**Before:** 15 lines — simple incr/expire with no error handling, no IP abstraction.

**After:** 27 lines with:
- `get_client_ip(request)` — checks `X-Forwarded-For` header first, falls back to `request.client.host`
- Handles comma-separated `X-Forwarded-For` (takes first IP, strips whitespace)
- `rate_limiter()` now catches `HTTPException` (re-raises) and generic `Exception` (logs, allows request — fail open)

### `app/api/routes/documents.py`

- Added `from app.core.rate_limit import rate_limiter` import
- Added `dependencies=[Depends(rate_limiter)]` to `upload_document` and `get_document` routes
- `get_document` now validates `document_id` with `uuid.UUID()` before DB query
  - Returns `400` with `"Invalid document ID format. Must be a valid UUID."` for malformed input
  - Returns `404` for valid UUID not found (unchanged behavior)

### `app/api/routes/metrics.py`

- Added `from app.core.rate_limit import rate_limiter` import
- Added `dependencies=[Depends(rate_limiter)]` to `usage` and `usage_by_type` routes

### `tests/test_rate_limit.py` (new file — 16 tests)

| Class | Tests | Coverage |
|-------|-------|----------|
| `TestRateLimiterUnit` | 9 | IP detection (4), rate limit behavior (3), expiry (1), Redis failure (1) |
| `TestEndpointRateLimiting` | 2 | Router dependency wiring for documents and metrics |
| `TestDocumentUUIDValidation` | 5 | Invalid UUID (2), missing document (1), success (1), processing status (1) |

---

## Test Results

```
96 passed, 0 failed, 0 errors
```

All existing tests continue to pass. No regressions introduced.

---

## Security Impact

| Risk | Before | After |
|------|--------|-------|
| Unprotected endpoints | documents and metrics had no rate limiting | All endpoints rate limited at 20 req/min |
| Load balancer bypass | Single IP (LB) consumed entire rate limit | Per-client IP via `X-Forwarded-For` |
| Malformed UUID DoS | Any string caused 500 error | 400 returned before DB query |
| Redis failure | Unhandled exception | Logged, request allowed (fail open) |
