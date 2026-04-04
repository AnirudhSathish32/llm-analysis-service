# Remaining Tasks Plan

> Generated: 2026-04-04
> Completed: fix-code-quality, fix-documentation, fix-config-consistency, fix-blocking-calls, fix-anti-patterns, fix-medium-issues, critical-fixes

---

## Task 1: add-missing-tests

**Severity:** High
**Estimated slices:** 4
**Estimated tests:** ~24

### Slice 1: Test documents.py `get_document` endpoint
- `test_get_document_success` — verify 200 with valid document
- `test_get_document_returns_404` — verify 404 for missing document
- `test_get_document_rejects_invalid_uuid` — verify 400 for malformed UUID
- `test_get_document_returns_processing_status` — verify processing status returned

### Slice 2: Test metrics.py endpoints
- `test_usage_returns_aggregated_counts` — happy path
- `test_usage_returns_zero_for_empty_db` — empty database
- `test_usage_by_type_returns_breakdown` — per-type counts
- `test_usage_by_type_returns_empty_for_no_data` — no analysis results yet
- `test_usage_handles_db_error_gracefully` — DB down returns 500

### Slice 3: Test rate_limit.py middleware
- `test_rate_limit_allows_within_limit` — requests under 20/min pass
- `test_rate_limit_blocks_over_limit` — 21st request gets 429
- `test_rate_limit_resets_after_window` — requests pass after 60s
- `test_rate_limit_uses_client_ip` — different IPs get separate limits
- `test_rate_limit_fails_open_on_redis_error` — Redis down = allow (or deny based on config)

### Slice 4: Test analysis_service.py failure paths
- `test_analysis_returns_failed_on_llm_timeout` — timeout returns failed status
- `test_analysis_returns_failed_on_rag_failure` — RAG retrieval failure returns failed
- `test_analysis_returns_failed_on_cache_error` — Redis cache miss + set failure still works
- `test_analysis_caches_successful_result` — verify cache is set after success
- `test_analysis_returns_cached_response` — second identical request returns cached

---

## Task 2: fix-rate-limiting

**Severity:** High
**Estimated slices:** 3
**Estimated tests:** ~12

### Slice 1: Apply rate limiting to all endpoints
- Add `rate_limiter` dependency to `documents.py` routes
- Add `rate_limiter` dependency to `metrics.py` routes
- Test: `test_documents_endpoint_is_rate_limited`
- Test: `test_metrics_endpoint_is_rate_limited`

### Slice 2: Fix rate limiter IP detection for production
- Use `X-Forwarded-For` header when behind load balancer
- Fallback to `request.client.host` for local development
- Test: `test_rate_limit_uses_x_forwarded_for_header`
- Test: `test_rate_limit_falls_back_to_client_host`
- Test: `test_rate_limit_handles_multiple_ips_in_forwarded_for`

### Slice 3: Add UUID validation for document_id parameter
- Validate `document_id` is valid UUID before DB query
- Return 400 for invalid UUID instead of 500
- Test: `test_get_document_returns_400_for_invalid_uuid`
- Test: `test_get_document_returns_404_for_valid_uuid_not_found`

---

## Task 3: fix-ci-cd

**Severity:** Medium
**Estimated slices:** 3
**Estimated tests:** N/A (CI/CD changes)

### Slice 1: Add CI gate to CD pipeline
- CD pipeline should only deploy if CI tests pass
- Add `needs: [lint, test]` to deploy job
- Verify: CD workflow has proper dependency chain

### Slice 2: Fix CD rollback condition
- Current rollback condition `steps.deploy.outcome != 'success'` is invalid
- Use `if: failure()` on a separate rollback step
- Add explicit rollback job that reverts to previous task definition
- Verify: Rollback triggers on deploy failure

### Slice 3: Add security scanning to CI
- Add `pip-audit` step to check for vulnerable dependencies
- Add Docker image vulnerability scan (trivy or similar)
- Add step to check for hardcoded secrets (gitleaks or similar)
- Verify: CI fails on known CVEs or secrets

---

## Execution Order

1. **add-missing-tests** (highest value, blocks confidence in other changes)
2. **fix-rate-limiting** (security improvement, depends on test coverage)
3. **fix-ci-cd** (pipeline improvements, lowest risk)

## Notes

- All test slices should follow the existing test conventions from `project-rules.md`
- Use `pytest.mark.asyncio` for async tests
- Mock external dependencies (Redis, LLM, RAG, Pinecone)
- Tests run in Docker: `docker compose run --rm api pytest`
- Each slice should be on its own `task/[task-name]` branch
- Use the slice-maker workflow to create slice files
- Use the slice-builder workflow to implement each slice
