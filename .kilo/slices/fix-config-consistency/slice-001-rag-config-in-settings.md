---
slice: 1
task: fix-config-consistency
status: completed
dependencies: none
severity: low
---

# Slice 1: Move RAG and upload config to Settings class

## Goal
Move `rag_pipeline.py` config constants from `os.getenv()` to `Settings` class. Add `upload_dir` to Settings.

## Files to Create/Modify
- `app/core/config.py` — add `upload_dir` field
- `app/services/rag_pipeline.py` — use `settings` instead of `os.getenv()` for CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, PINECONE_INDEX
- `app/api/routes/documents.py` — use `settings.upload_dir` instead of `os.getenv()`

## What It Builds
Centralized configuration through pydantic-settings.

## Tests
(severity: low — 2 tests)
- `test_settings_has_rag_config_fields` — verify chunk_size, chunk_overlap, rag_top_k exist on Settings
- `test_settings_has_upload_dir` — verify upload_dir field exists with default

## Dependencies
none

## Commit Message
fix(config): move RAG and upload config to Settings class

## Acceptance Criteria
- [ ] No `os.getenv()` calls in `rag_pipeline.py`
- [ ] No `os.getenv()` calls in `documents.py` for UPLOAD_DIR
- [ ] `Settings` has `upload_dir` field
- [ ] All existing tests still pass
