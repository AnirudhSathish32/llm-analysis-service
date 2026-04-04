---
slice: 1
task: add-missing-tests
status: pending
dependencies: none
severity: high
---

# Slice 1: Test documents.py `get_document` endpoint

## Goal
Add test coverage for the `get_document` endpoint in `documents.py` — success, 404, invalid UUID, and processing status paths.

## Files to Create/Modify
- `tests/test_documents.py` — create new test file with `TestGetDocument` class

## What It Builds
Test coverage for the document retrieval endpoint, ensuring correct HTTP status codes and response shapes.

## Tests
(severity: high — 4 tests)
- `test_get_document_success` — verify 200 with valid document
- `test_get_document_returns_404` — verify 404 for missing document
- `test_get_document_rejects_invalid_uuid` — verify 400 for malformed UUID
- `test_get_document_returns_processing_status` — verify processing status returned

## Dependencies
none

## Commit Message
test(documents): add test coverage for get_document endpoint

## Acceptance Criteria
- [ ] `test_get_document_success` passes with mock DB returning valid document
- [ ] `test_get_document_returns_404` passes when document not found
- [ ] `test_get_document_rejects_invalid_uuid` returns 400 for non-UUID input
- [ ] `test_get_document_returns_processing_status` verifies status field in response
- [ ] All existing tests still pass
