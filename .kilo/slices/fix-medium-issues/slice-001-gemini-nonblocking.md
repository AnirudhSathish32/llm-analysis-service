---
slice: 1
task: fix-medium-issues
status: pending
dependencies: none
---

# Slice 1: Convert synchronous Gemini call to non-blocking

## Goal
Fix `llm_router.py:_call_gemini` which uses synchronous `model.generate_content(prompt)`, blocking the entire asyncio event loop.

## Files to Modify
- `app/services/llm_router.py` — wrap `_call_gemini` in `asyncio.to_thread()` or `run_in_executor`

## Tests
- `test_gemini_call_does_not_block_event_loop` — verify Gemini call runs in a separate thread
- Existing tests should still pass

## Commit Message
perf(llm): make Gemini SDK call non-blocking with asyncio.to_thread

## Acceptance Criteria
- [ ] `_call_gemini` no longer blocks the event loop
- [ ] Uses `asyncio.to_thread()` or `loop.run_in_executor()`
- [ ] All existing tests still pass
