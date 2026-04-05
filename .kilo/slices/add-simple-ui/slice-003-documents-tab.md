# Slice: ui-documents-tab

**Parent task:** add-simple-ui
**Estimated effort:** 1 slice
**Dependencies:** slice-001-scaffold

## Purpose
Build the Documents tab — upload files for RAG ingestion and check their status.

## What to create
In `frontend/src/tabs/documents.ts`:
- File upload area (drag-and-drop + click to browse) — styled `div` with `border-2 border-dashed`
- File type validation: `.pdf`, `.txt`, `.csv` only
- File size indicator with configured max
- Upload button with progress indicator
- Result card showing:
  - `document_id` (with copy-to-clipboard button)
  - `filename`
  - `status` badge (processing/ready/failed)
  - `chunk_count`
- Document status checker:
  - Input field to paste a `document_id`
  - "Check Status" button → GET `/v1/documents/{id}`
  - Displays current status and chunk count
- List of recently uploaded documents (stored in localStorage)
- Typed response interface: `DocumentUploadResponse` from `api/types.ts`

### Component usage
- `Card` component for result cards
- `Badge` component for status indicators
- `Button` component with `loading` prop
- `Toast` component for success/error feedback

## Acceptance criteria
- User can drag-drop or browse to select a file
- Invalid file types rejected with message below upload area
- Upload shows result with copyable document_id
- Status checker polls or fetches document state
- Recent uploads persist in localStorage
- Copy-to-clipboard copies document_id
- Drop zone has visible border + label (not gesture-only)
- Upload button disabled during file transfer
- Success/error feedback shown within 300ms of response
- File size error includes recovery guidance ("Max file size: X MB")
- Empty state shows "No documents uploaded yet" with action hint
- Copy button shows brief "Copied!" confirmation (success feedback)
- All interactive elements >= 44x44px touch targets
- File upload uses `FormData` with correct `multipart/form-data` content type
- All types are strict — no `any` in documents tab code
