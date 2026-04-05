# Slice: ui-analyze-tab

**Parent task:** add-simple-ui
**Estimated effort:** 1 slice
**Dependencies:** slice-001-scaffold

## Purpose
Build the Analyze tab — the primary workflow for submitting text to the LLM.

## What to create
In `frontend/src/tabs/analyze.ts`:
- `<textarea>` with Tailwind classes for input text (character counter, max 10,000)
- `<select>` dropdown for `analysis_type`: `summary` or `key_points`
- Optional `document_id` `<input>` field (with link to Documents tab)
- Submit `<button>` with loading state (`disabled` + spinner)
- Result panel showing:
  - `status` badge (`<span>` with `bg-success` / `bg-error` pill)
  - `result.content` rendered as text
  - `cached` indicator (small badge)
  - `provider` badge (anthropic/gemini)
  - `rag_chunks_used` count
  - Citations table (`<table>` with `chunk_index`, `page`, `source` columns)
- Error toast for 429 rate limit and 500 errors
- POST to `/v1/analysis` via typed `apiClient.analyze()` call
- Use `AnalysisRequestSchema` and `AnalysisResponseSchema` from `api/types.ts`

### Component usage
- `Button` component with `variant="primary"` + `loading` prop
- `Badge` component for status/provider/cached indicators
- `Card` component for result panel
- `Toast` component for error messages

## Acceptance criteria
- User can type text, select type, submit and see result
- Character counter updates live, disables submit at 10,000
- Loading spinner shown during request (skeleton if >300ms)
- Cached results show a "cached" badge
- Citations render as a table when present
- Rate limit (429) shows friendly message with retry option
- Failed analysis shows error state with recovery path
- Submit button disabled during async request (disabled semantics, reduced opacity)
- Error messages appear below relevant fields (not at top of page)
- All inputs have visible labels (not placeholder-only)
- First invalid field auto-focused on validation error
- Toast uses aria-live="polite" for screen reader announcement
- Submit button min 44x44px touch target
- All types are strict — no `any` in analyze tab code
