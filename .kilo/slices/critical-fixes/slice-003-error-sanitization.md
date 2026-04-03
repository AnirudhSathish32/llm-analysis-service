---
slice: 3
task: critical-fixes
status: completed
dependencies: none
severity: high
---

# Slice 3: Sanitize error responses — stop leaking internal details

## Goal
Replace `detail=str(e)` in document upload error handler with a generic message. Never expose internal exception text to clients.

## Files to Create/Modify
- `app/api/routes/documents.py` — replace `detail=str(e)` with generic message, log full error internally
- `app/api/routes/metrics.py` — add try/except that returns generic error, not stack trace

## What It Builds
Error responses that return generic messages externally while logging full details internally.

## Tests
(severity: high — 6 tests)
- `test_upload_error_does_not_leak_internal_details` — verify exception text not in response
- `test_upload_error_returns_generic_message` — verify generic error body
- `test_upload_error_logs_full_traceback` — verify internal log has details
- `test_metrics_error_returns_generic_message` — verify DB failure gives generic error
- `test_metrics_error_does_not_expose_stack_trace` — verify no stack trace in response
- `test_analysis_error_returns_failed_status_not_exception` — verify service returns status field

## Dependencies
none

## Commit Message
fix(security): sanitize error responses — stop leaking internal exception details

## Acceptance Criteria
- [ ] No `str(e)` in any HTTP response detail
- [ ] Generic error message returned to client
- [ ] Full exception logged internally with logger.exception()
- [ ] Metrics endpoint returns JSON error, not stack trace
- [ ] All existing tests still pass
