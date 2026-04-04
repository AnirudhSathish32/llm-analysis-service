---
slice: 2
task: add-missing-tests
status: pending
dependencies: none
severity: high
---

# Slice 2: Test metrics.py endpoints

## Goal
Add test coverage for the metrics endpoints — usage counts, empty database, per-type breakdown, and DB error handling.

## Files to Create/Modify
- `tests/test_metrics.py` — create new test file with `TestMetricsEndpoints` class

## What It Builds
Test coverage for the metrics API, ensuring correct aggregation and error handling.

## Tests
(severity: high — 5 tests)
- `test_usage_returns_aggregated_counts` — happy path
- `test_usage_returns_zero_for_empty_db` — empty database
- `test_usage_by_type_returns_breakdown` — per-type counts
- `test_usage_by_type_returns_empty_for_no_data` — no analysis results yet
- `test_usage_handles_db_error_gracefully` — DB down returns 500

## Dependencies
none

## Commit Message
test(metrics): add test coverage for metrics endpoints

## Acceptance Criteria
- [ ] `test_usage_returns_aggregated_counts` verifies correct count aggregation
- [ ] `test_usage_returns_zero_for_empty_db` returns zero counts
- [ ] `test_usage_by_type_returns_breakdown` returns per-type breakdown
- [ ] `test_usage_by_type_returns_empty_for_no_data` returns empty breakdown
- [ ] `test_usage_handles_db_error_gracefully` returns 500 on DB error
- [ ] All existing tests still pass
