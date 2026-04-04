---
slice: 2
task: fix-code-quality
status: completed
dependencies: none
severity: low
---

# Slice 2: Add missing type hints

## Goal
Add return type hints to `get_session()`, `rate_limiter()`, and `health()` endpoint.

## Files to Create/Modify
- `app/db/session.py` — add `-> AsyncGenerator[AsyncSession, None]` to `get_session()`
- `app/core/rate_limit.py` — add `-> None` to `rate_limiter()`
- `app/main.py` — add `-> dict` to `health()`

## What It Builds
Consistent type hints on all public functions.

## Tests
(severity: low — 2 tests)
- `test_get_session_has_return_type_hint` — verify return type annotation present
- `test_health_endpoint_has_return_type_hint` — verify return type annotation present

## Dependencies
none

## Commit Message
fix(code-quality): add missing return type hints to public functions

## Acceptance Criteria
- [ ] `get_session()` has `-> AsyncGenerator[AsyncSession, None]`
- [ ] `rate_limiter()` has `-> None`
- [ ] `health()` has `-> dict`
- [ ] All existing tests still pass
