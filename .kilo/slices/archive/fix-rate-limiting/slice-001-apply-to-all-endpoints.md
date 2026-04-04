---
slice: 1
task: fix-rate-limiting
status: completed
dependencies: none
severity: high
---

# Slice 1: Apply rate limiting to all endpoints

## Goal
Ensure rate limiting is applied to `documents.py` and `metrics.py` routes, not just analysis endpoints.

## Files to Create/Modify
- `app/api/routes/documents.py` — add `rate_limiter` dependency to routes
- `app/api/routes/metrics.py` — add `rate_limiter` dependency to routes
- `tests/test_rate_limit.py` — add endpoint-level rate limit tests

## What It Builds
Consistent rate limiting across all public endpoints.

## Tests
(severity: high — 2 tests)
- `test_documents_routes_have_rate_limit_dependency` — verify all document routes have rate_limiter
- `test_metrics_routes_have_rate_limit_dependency` — verify all metrics routes have rate_limiter

## Dependencies
none

## Commit Message
fix(rate-limit): apply rate limiting to documents and metrics endpoints

## Acceptance Criteria
- [x] `documents.py` routes include `rate_limiter` dependency
- [x] `metrics.py` routes include `rate_limiter` dependency
- [x] `test_documents_routes_have_rate_limit_dependency` passes
- [x] `test_metrics_routes_have_rate_limit_dependency` passes
- [x] All existing tests still pass (96/96)
