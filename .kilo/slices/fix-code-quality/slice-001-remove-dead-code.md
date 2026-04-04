---
slice: 1
task: fix-code-quality
status: completed
dependencies: none
severity: low
---

# Slice 1: Remove duplicate test and dead code

## Goal
Clean up dead code, duplicate tests, and redundant imports.

## Files to Create/Modify
- `tests/test_logging.py` — remove duplicate test method `test_logs_warning_on_operational_error` (lines 130-152)
- `app/schemas/analysis.py` — delete `StoredAnalysisSchema` class and unused `datetime` import
- `app/api/dependencies.py` — delete empty file
- `tests/test_error_sanitization.py` — remove redundant imports inside `test_analysis_error_returns_failed_status_not_exception`

## What It Builds
A cleaner codebase with no dead code or duplicate tests.

## Tests
(severity: low — 2 tests)
- `test_no_stored_analysis_schema` — verify `StoredAnalysisSchema` is not importable
- `test_no_dependencies_module` — verify `app.api.dependencies` doesn't exist or is empty

## Dependencies
none

## Commit Message
fix(code-quality): remove duplicate test, dead schema, and empty module

## Acceptance Criteria
- [ ] No duplicate test methods in `test_logging.py`
- [ ] `StoredAnalysisSchema` removed from `analysis.py`
- [ ] `datetime` import removed if unused
- [ ] `app/api/dependencies.py` deleted
- [ ] Redundant imports removed from `test_error_sanitization.py`
- [ ] All existing tests still pass
