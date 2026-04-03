---
slice: 5
task: fix-medium-issues
status: completed
dependencies: none
---

# Slice 5: Add request correlation IDs via middleware

## Goal
No middleware adds a `X-Request-ID` header. When something fails, there is no way to correlate logs across the request lifecycle.

## Files to Create/Modify
- `app/core/middleware.py` (new) — FastAPI middleware that generates/propagates `X-Request-ID`
- `app/main.py` — register the middleware
- All log messages should include the request ID via context

## Tests
- `test_middleware_generates_request_id` — verify X-Request-ID is added to response
- `test_middleware_propagates_existing_request_id` — verify client-provided X-Request-ID is used
- `test_log_contains_request_id` — verify logs include the request ID

## Commit Message
feat(middleware): add request correlation ID middleware for tracing

## Acceptance Criteria
- [ ] Every response includes `X-Request-ID` header
- [ ] Client-provided `X-Request-ID` is respected
- [ ] Log messages include the request ID
- [ ] All existing tests still pass
