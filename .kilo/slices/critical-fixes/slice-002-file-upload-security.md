---
slice: 2
task: critical-fixes
status: pending
dependencies: none
severity: high
---

# Slice 2: Add file size limit and path sanitization to document upload

## Goal
Add `max_file_size` check (10MB) and sanitize `file.filename` to prevent path traversal in the document upload endpoint.

## Files to Create/Modify
- `app/api/routes/documents.py` — add size limit check, sanitize filename with `os.path.basename`
- `app/core/config.py` — add `max_upload_bytes` setting

## What It Builds
A safe document upload endpoint that rejects oversized files and sanitizes filenames.

## Tests
(severity: high — 6 tests)
- `test_upload_rejects_oversized_file` — verify 413 for files over limit
- `test_upload_accepts_valid_file` — verify 201 for normal file
- `test_upload_sanitizes_path_traversal_filename` — verify `../../etc/passwd` becomes `passwd`
- `test_upload_rejects_empty_filename` — verify 400 for missing filename
- `test_upload_rejects_unsupported_extension` — verify 400 for `.exe`
- `test_upload_returns_correct_error_shape` — verify JSON error body, not stack trace

## Dependencies
none

## Commit Message
fix(security): add file size limit and path sanitization to document upload

## Acceptance Criteria
- [ ] Files over 10MB rejected with 413
- [ ] Path traversal characters stripped from filename
- [ ] Unsupported file types rejected with 400
- [ ] Error responses are JSON, not stack traces
- [ ] All existing tests still pass
