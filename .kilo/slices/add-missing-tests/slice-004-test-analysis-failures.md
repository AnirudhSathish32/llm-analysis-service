---
slice: 4
task: add-missing-tests
status: pending
dependencies: none
severity: high
---

# Slice 4: Test analysis_service.py failure paths

## Goal
Add test coverage for analysis service failure paths — LLM timeout, RAG failure, cache errors, and cache hit behavior.

## Files to Create/Modify
- `tests/test_analysis_service.py` — add new test class `TestAnalysisServiceFailurePaths` to existing file

## What It Builds
Test coverage for error handling and caching in the analysis service.

## Tests
(severity: high — 5 tests)
- `test_analysis_returns_failed_on_llm_timeout` — timeout returns failed status
- `test_analysis_returns_failed_on_rag_failure` — RAG retrieval failure returns failed
- `test_analysis_returns_failed_on_cache_error` — Redis cache miss + set failure still works
- `test_analysis_caches_successful_result` — verify cache is set after success
- `test_analysis_returns_cached_response` — second identical request returns cached

## Dependencies
none

## Commit Message
test(analysis): add failure path and caching tests for analysis service

## Acceptance Criteria
- [ ] `test_analysis_returns_failed_on_llm_timeout` returns failed status on timeout
- [ ] `test_analysis_returns_failed_on_rag_failure` returns failed status on RAG error
- [ ] `test_analysis_returns_failed_on_cache_error` handles cache failure gracefully
- [ ] `test_analysis_caches_successful_result` verifies cache set after success
- [ ] `test_analysis_returns_cached_response` returns cached result on second request
- [ ] All existing tests still pass
