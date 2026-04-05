# Slice: ui-analyze-tab

**Parent task:** add-simple-ui
**Estimated effort:** 1 slice
**Dependencies:** ui-project-scaffold

## Purpose
Build the Analyze tab — the primary workflow for submitting text to the LLM.

## What to create
In `frontend/js/tabs/analyze.js`:
- Textarea for input text (character counter, max 10,000)
- Dropdown for `analysis_type`: `summary` or `key_points`
- Optional `document_id` input field (with link to Documents tab)
- Submit button with loading state
- Result panel showing:
  - `status` badge (completed/failed)
  - `result.content` rendered as text
  - `cached` indicator
  - `provider` badge (anthropic/gemini)
  - `rag_chunks_used` count
  - Citations table (chunk_index, page, source)
- Error toast for 429 rate limit and 500 errors
- POST to `/v1/analysis` with proper error handling

## Acceptance criteria
- User can type text, select type, submit and see result
- Character counter updates live, disables submit at 10,000
- Loading spinner shown during request
- Cached results show a "cached" badge
- Citations render as a table when present
- Rate limit (429) shows friendly message
- Failed analysis shows error state
