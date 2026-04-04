---
slice: 3
task: add-missing-tests
status: pending
dependencies: none
severity: high
---

# Slice 3: Test rate_limit.py middleware

## Goal
Add test coverage for the rate limiting middleware — within limit, over limit, window reset, per-IP isolation, and Redis failure behavior.

## Files to Create/Modify
- `tests/test_rate_limit.py` — create new test file with `TestRateLimitMiddleware` class

## What It Builds
Test coverage for rate limiting behavior, ensuring correct throttling and graceful degradation.

## Tests
(severity: high — 5 tests)
- `test_rate_limit_allows_within_limit` — requests under 20/min pass
- `test_rate_limit_blocks_over_limit` — 21st request gets 429
- `test_rate_limit_resets_after_window` — requests pass after 60s
- `test_rate_limit_uses_client_ip` — different IPs get separate limits
- `test_rate_limit_fails_open_on_redis_error` — Redis down = allow (or deny based on config)

## Dependencies
none

## Commit Message
test(rate-limit): add test coverage for rate limiting middleware

## Acceptance Criteria
- [ ] `test_rate_limit_allows_within_limit` verifies requests under limit pass
- [ ] `test_rate_limit_blocks_over_limit` returns 429 on 21st request
- [ ] `test_rate_limit_resets_after_window` verifies window expiration
- [ ] `test_rate_limit_uses_client_ip` isolates limits per IP
- [ ] `test_rate_limit_fails_open_on_redis_error` handles Redis failure gracefully
- [ ] All existing tests still pass
