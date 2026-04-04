---
slice: 2
task: fix-rate-limiting
status: completed
dependencies: fix-rate-limiting/slice-001
severity: high
---

# Slice 2: Fix rate limiter IP detection for production

## Goal
Use `X-Forwarded-For` header when behind a load balancer, fallback to `request.client.host` for local development.

## Files to Create/Modify
- `app/core/rate_limit.py` — update IP extraction logic to check `X-Forwarded-For` first, add Redis error handling
- `tests/test_rate_limit.py` — add IP detection tests

## What It Builds
Correct rate limiting in production environments behind load balancers/proxies.

## Tests
(severity: high — 7 tests)
- `test_get_client_ip_uses_x_forwarded_for` — uses header value
- `test_get_client_ip_uses_first_ip_in_forwarded_for` — uses first IP in comma-separated list
- `test_get_client_ip_falls_back_to_client_host` — uses client.host when no header
- `test_get_client_ip_strips_whitespace_in_forwarded_for` — trims whitespace
- `test_rate_limiter_uses_x_forwarded_for_for_key` — Redis key uses forwarded IP
- `test_rate_limiter_fails_open_on_redis_error` — Redis down = allow request
- `test_rate_limiter_blocks_over_limit` — 429 on 21st request

## Dependencies
none (implemented alongside slice 1)

## Commit Message
fix(rate-limit): use X-Forwarded-For header for IP detection behind load balancers

## Acceptance Criteria
- [x] Rate limiter checks `X-Forwarded-For` header first
- [x] Falls back to `request.client.host` when header absent
- [x] Handles multiple IPs in `X-Forwarded-For` (uses first)
- [x] Redis errors are caught and logged — request allowed (fail open)
- [x] All seven new tests pass
- [x] All existing tests still pass (96/96)
