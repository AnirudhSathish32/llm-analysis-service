# Slice: ui-metrics-tab

**Parent task:** add-simple-ui
**Estimated effort:** 1 slice
**Dependencies:** slice-001-scaffold

## Purpose
Build the Metrics tab — display usage statistics, cost per token, and cost per query.

## What to create
In `frontend/src/tabs/metrics.ts`:
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
- GET `/v1/metrics/usage` and `/v1/metrics/usage/by_type` via typed `apiClient` calls
- Empty state when no data exists
- Typed response interfaces: `UsageResponse`, `UsageByTypeResponse` from `api/types.ts`

### Component usage
- `Card` component for summary stat cards (4-column grid on desktop, 2-col on tablet, 1-col on mobile)
- `Table` component for breakdown table
- `Button` component for refresh
- `Toggle` component for auto-refresh switch
- Skeleton placeholder components for loading state

## Acceptance criteria
- Summary cards display aggregated metrics
- Breakdown table shows per-type stats
- Cost per token and cost per query calculated and displayed
- Refresh button re-fetches data
- Auto-refresh works when toggled on
- Empty state shows "No data yet" message with guidance
- Numbers formatted with commas and 2 decimal places for currency
- Tabular nums for all data columns (no layout shift) — `font-mono` or `tabular-nums`
- Skeleton shimmer shown while data loads (not blank cards)
- Data table has accessible headers (`scope="col"`)
- Auto-refresh toggle shows current interval ("Refreshing every 30s")
- Error state shows "Failed to load metrics" with retry button
- Color not used alone to convey meaning (icons + text for status)
- Table is keyboard-navigable with visible focus ring
- Summary cards use responsive grid: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`
- All types are strict — no `any` in metrics tab code
