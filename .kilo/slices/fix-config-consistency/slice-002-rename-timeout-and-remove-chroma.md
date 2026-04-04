---
slice: 2
task: fix-config-consistency
status: completed
dependencies: none
severity: low
---

# Slice 2: Rename TimeoutError and remove stale task-definition env vars

## Goal
Rename `TimeoutError` to `LLMTimeoutError` to fix Python built-in shadowing. Remove stale `CHROMA_HOST`/`CHROMA_PORT` from `task-definition.json`.

## Files to Create/Modify
- `app/core/exceptions.py` — rename `TimeoutError` to `LLMTimeoutError`
- `app/services/analysis_service.py` — update import to use `LLMTimeoutError`
- `task-definition.json` — remove CHROMA_HOST and CHROMA_PORT env vars

## What It Builds
No more built-in shadowing, no dead ECS config.

## Tests
(severity: low — 2 tests)
- `test_llm_timeout_error_does_not_shadow_builtin` — verify `TimeoutError` is still the Python built-in
- `test_task_definition_has_no_chroma_vars` — verify no CHROMA_HOST/CHROMA_PORT in task-definition.json

## Dependencies
none

## Commit Message
fix(config): rename TimeoutError to LLMTimeoutError and remove stale ChromaDB env vars

## Acceptance Criteria
- [ ] `TimeoutError` class renamed to `LLMTimeoutError`
- [ ] `analysis_service.py` imports `LLMTimeoutError`
- [ ] No CHROMA_HOST/CHROMA_PORT in `task-definition.json`
- [ ] All existing tests still pass
