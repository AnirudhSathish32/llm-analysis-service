---
slice: 2
task: fix-anti-patterns
status: pending
dependencies: slice-001
---

# Slice 2: Replace bare except Exception with specific exception handling

## Goal
Replace the bare `except Exception` in `analysis_service.py` with specific exception types and proper error logging.

## Files to Create/Modify
- `app/services/analysis_service.py` — catch specific exceptions, log errors with context
- `app/core/logging.py` — add shared logging configuration (if not done in slice 1)

## What It Builds
Proper error handling that logs failure context and catches specific exception types instead of swallowing everything.

## Tests
- `test_analysis_service_logs_error_on_llm_failure` — verify error is logged when LLM fails
- `test_analysis_service_returns_failed_status_on_db_error` — verify DB errors are handled specifically
- `test_analysis_service_logs_exception_details` — verify exception context is captured in logs

## Dependencies
slice-001 (logging infrastructure must exist first)

## Commit Message
fix(error-handling): replace bare except Exception with specific exception handling in analysis service

## Acceptance Criteria
- [ ] `except Exception` replaced with specific exception types (ScoringError, DBError, etc.)
- [ ] Error is logged with request context before returning failed response
- [ ] No exception details leaked to external response
- [ ] All existing tests still pass
