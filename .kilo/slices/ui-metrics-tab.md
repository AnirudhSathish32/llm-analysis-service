# Slice: ui-metrics-tab

**Parent task:** add-simple-ui
**Estimated effort:** 1 slice
**Dependencies:** ui-project-scaffold

## Purpose
Build the Metrics tab — display usage statistics, cost per token, and cost per query.

## What to create
In `frontend/js/tabs/metrics.js`:
- Summary cards showing:
  - Total requests
  - Total tokens
  - Total cost (USD)
  - Average duration (ms)
- Breakdown table by analysis type (`summary` vs `key_points`):
  - Requests count
  - Tokens used
  - Cost (USD)
- Derived metrics:
  - Cost per token (total_cost / total_tokens)
  - Cost per query (total_cost / total_requests)
- Refresh button to re-fetch data
- Auto-refresh toggle (every 30s)
- GET `/v1/metrics/usage` and `/v1/metrics/usage/by_type`
- Empty state when no data exists

## Acceptance criteria
- Summary cards display aggregated metrics
- Breakdown table shows per-type stats
- Cost per token and cost per query calculated and displayed
- Refresh button re-fetches data
- Auto-refresh works when toggled on
- Empty state shows "No data yet" message
- Numbers formatted with commas and 2 decimal places for currency
