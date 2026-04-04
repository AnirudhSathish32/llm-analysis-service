---
slice: 3
task: fix-code-quality
status: pending
dependencies: none
severity: low
---

# Slice 3: Move import to module level and add docstring

## Goal
Move `select` import to module level in `documents.py` and add docstring to `health` endpoint.

## Files to Create/Modify
- `app/api/routes/documents.py` — move `from sqlalchemy import select` to top of file
- `app/main.py` — add docstring to `health()` endpoint

## What It Builds
Cleaner code following import conventions and proper documentation.

## Tests
(severity: low — 2 tests)
- `test_select_import_at_module_level` — verify `select` is imported at top of documents.py
- `test_health_endpoint_has_docstring` — verify `health()` has a docstring

## Dependencies
none

## Commit Message
fix(code-quality): move select import to module level and add health docstring

## Acceptance Criteria
- [ ] `select` imported at top of `documents.py`, not inside function
- [ ] `health()` has a docstring
- [ ] All existing tests still pass
