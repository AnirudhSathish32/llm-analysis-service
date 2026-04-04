---
slice: 3
task: fix-rate-limiting
status: completed
dependencies: none
severity: high
---

# Slice 3: Add UUID validation for document_id parameter

## Goal
Validate `document_id` is a valid UUID before DB query. Return 400 for invalid UUID instead of 500.

## Files to Create/Modify
- `app/api/routes/documents.py` — add UUID validation before DB lookup
- `tests/test_rate_limit.py` — add validation tests

## What It Builds
Proper input validation at the API boundary, preventing 500 errors on malformed UUIDs.

## Tests
(severity: high — 5 tests)
- `test_get_document_returns_400_for_invalid_uuid` — non-UUID string returns 400
- `test_get_document_rejects_malformed_uuid` — malformed UUID returns 400
- `test_get_document_returns_404_for_valid_uuid_not_found` — valid but missing UUID returns 404
- `test_get_document_success_with_valid_uuid` — happy path returns 200
- `test_get_document_returns_processing_status` — processing status returned correctly

## Dependencies
none

## Commit Message
fix(documents): validate document_id UUID before DB query

## Acceptance Criteria
- [x] Invalid UUID returns 400 with descriptive error message
- [x] Valid but non-existent UUID returns 404
- [x] All five new tests pass
- [x] All existing tests still pass (96/96)
