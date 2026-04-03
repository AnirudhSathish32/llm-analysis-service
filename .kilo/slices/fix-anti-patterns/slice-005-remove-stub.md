---
slice: 5
task: fix-anti-patterns
status: pending
dependencies: slice-002
---

# Slice 5: Remove simulated llm_client.py stub

## Goal
Delete `app/services/llm_client.py` — it's a simulated stub that's not used anywhere. The real LLM logic lives in `llm_router.py`.

## Files to Create/Modify
- `app/services/llm_client.py` — DELETE this file
- `app/services/__init__.py` — remove any reference if present

## What It Builds
A cleaner codebase with no dead code — the simulated LLMClient class is removed since `LLMRouter` handles all real LLM calls.

## Tests
- `test_no_import_of_llm_client` — verify no module imports llm_client
- Existing tests already import from llm_router, not llm_client

## Dependencies
slice-002 (error handling fixes — ensures we're not breaking anything)

## Commit Message
refactor(services): remove simulated llm_client.py stub — LLMRouter handles all calls

## Acceptance Criteria
- [ ] `app/services/llm_client.py` deleted
- [ ] No imports of `LLMClient` or `llm_client` remain in codebase
- [ ] All existing tests still pass
- [ ] No references in requirements.txt or imports
