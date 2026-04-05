# Slice: ui-documents-tab

**Parent task:** add-simple-ui
**Estimated effort:** 1 slice
**Dependencies:** ui-project-scaffold

## Purpose
Build the Documents tab — upload files for RAG ingestion and check their status.

## What to create
In `frontend/js/tabs/documents.js`:
- File upload area (drag-and-drop + click to browse)
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

## Acceptance criteria
- User can drag-drop or browse to select a file
- Invalid file types rejected with message
- Upload shows result with copyable document_id
- Status checker polls or fetches document state
- Recent uploads persist in localStorage
- Copy-to-clipboard copies document_id
