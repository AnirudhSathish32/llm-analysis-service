# Branch Changes: critical

> Branch: `critical`
> Base: `main` (commit e2e3bda)
> Total commits: 4
> Test count: 36 passed (up from 19 original)

---

## Overview

This branch addresses **critical-severity security issues** identified during the codebase recon pass. Three slices were executed, covering hardcoded credentials, file upload security, and error response sanitization.

---

## Slice 1: Remove Hardcoded DB Credentials

**Commit:** `ea61558` — `fix(security): remove hardcoded DB credentials from config defaults`

### Changes
- **`app/core/config.py`**
  - Replaced hardcoded `llm_user:llm_password` default with empty string `""`
  - Added `@field_validator("database_url")` that raises `ValueError` if default credentials detected
  - Removed `print()` debug statements
  - Replaced `os.getenv()` with `Field(default=...)` for pydantic-settings loading

- **`docker-compose.yaml`**
  - Changed DB credentials from `llm_user:llm_password` to `dev_user:dev_password`

- **`.github/workflows/ci.yml`**
  - Changed CI DB credentials from `llm_user:llm_password` to `ci_user:ci_password`

- **`.env`**
  - Updated to use `dev_user:dev_password` instead of default credentials
  - Added placeholder API keys for local development

- **`.env.example`** (new)
  - Documents all required environment variables with placeholder values
  - Includes DATABASE_URL, REDIS_URL, API keys, and optional tuning params

### Tests Added
- **`tests/test_hardcoded_creds.py`** (6 tests)
  - `test_default_database_url_is_empty` — verifies no hardcoded creds in default
  - `test_settings_raises_if_default_creds_used` — verifies validator rejects default creds
  - `test_settings_accepts_valid_database_url` — verifies real URL passes validation
  - `test_settings_accepts_env_var_override` — verifies env var overrides default
  - `test_default_redis_url_has_no_password` — verifies Redis default has no password
  - `test_env_example_documents_database_url` — verifies `.env.example` has placeholder

---

## Slice 2: File Upload Security

**Commit:** `b581978` — `fix(security): add file size limit and path sanitization to document upload`

### Changes
- **`app/api/routes/documents.py`**
  - Added filename existence check (400 if missing)
  - Added `os.path.basename()` sanitization to prevent path traversal
  - Added file size validation against `settings.max_upload_bytes` (413 if exceeded)
  - Reads entire file into memory before saving (enables size check)
  - Error response uses generic message instead of leaking exception details
  - Uses `logger.exception()` instead of `traceback.format_exc()`

- **`app/core/config.py`**
  - Added `max_upload_bytes: int = 10_485_760` (10 MB)

### Tests Added
- **`tests/test_upload_security.py`** (6 tests)
  - `test_upload_rejects_oversized_file` — verifies 413 for files over limit
  - `test_upload_accepts_valid_file` — verifies 201 for normal file
  - `test_upload_sanitizes_path_traversal_filename` — verifies `../../etc/passwd.pdf` becomes `passwd.pdf`
  - `test_upload_rejects_empty_filename` — verifies 400 for missing filename
  - `test_upload_rejects_unsupported_extension` — verifies 400 for `.exe`
  - `test_upload_returns_correct_error_shape` — verifies generic error body on failure

---

## Slice 3: Error Response Sanitization

**Commit:** `c15cbf2` — `fix(security): sanitize error responses — stop leaking internal exception details`

### Changes
- **`app/api/routes/documents.py`**
  - Replaced `detail=f"Ingestion failed: {str(e)}"` with `detail="Document ingestion failed"`
  - Replaced `traceback.format_exc()` with `logger.exception()`

- **`app/api/routes/metrics.py`**
  - Added try/except around both `/usage` and `/usage/by_type` endpoints
  - DB failures return generic `"Failed to retrieve usage metrics"` message
  - Full exception logged internally via `logger.exception()`

### Tests Added
- **`tests/test_error_sanitization.py`** (5 tests)
  - `test_upload_error_does_not_leak_internal_details` — verifies connection strings not in response
  - `test_upload_error_returns_generic_message` — verifies generic error body
  - `test_metrics_error_returns_generic_message` — verifies DB failure gives generic error
  - `test_metrics_error_does_not_expose_stack_trace` — verifies no SQL details in response
  - `test_analysis_error_returns_failed_status_not_exception` — verifies service returns status field

---

## Files Modified Summary

| File | Change Type | Description |
|---|---|---|
| `app/core/config.py` | Modified | Added validator, max_upload_bytes, removed hardcoded creds/print |
| `app/api/routes/documents.py` | Modified | Added size limit, path sanitization, generic error messages |
| `app/api/routes/metrics.py` | Modified | Added try/except with generic error responses |
| `docker-compose.yaml` | Modified | Changed DB credentials to non-default values |
| `.github/workflows/ci.yml` | Modified | Changed CI DB credentials to non-default values |
| `.env` | Modified | Updated to use non-default credentials |
| `.env.example` | New | Documents all required environment variables |
| `tests/test_hardcoded_creds.py` | New | 6 tests for credential validation |
| `tests/test_upload_security.py` | New | 6 tests for file upload security |
| `tests/test_error_sanitization.py` | New | 5 tests for error sanitization |

---

## Test Results

```
36 passed, 0 failed, 11 warnings
```

| Test File | Tests | Status |
|---|---|---|
| `test_analysis_service.py` | 12 | ✅ All pass |
| `test_hardcoded_creds.py` | 6 | ✅ All pass |
| `test_upload_security.py` | 6 | ✅ All pass |
| `test_error_sanitization.py` | 5 | ✅ All pass |
| `test_config.py` | 7 | ✅ All pass |
| `test_logging.py` | 9 | ✅ All pass |

---

## Anti-Patterns Addressed

| Anti-Pattern | Fix Applied |
|---|---|
| Hardcoded `llm_user:llm_password` in config defaults | Empty default + validator rejects known creds |
| No file size limit on uploads | 10MB limit via `settings.max_upload_bytes` |
| Path traversal via filename | `os.path.basename()` sanitization |
| Exception details leaked in HTTP responses | Generic messages, `logger.exception()` internally |
| `str(e)` in error detail | Replaced with static error messages |
| `traceback.format_exc()` in production | Replaced with `logger.exception()` |
| Metrics endpoints with no error handling | try/except with generic 500 responses |
| No `.env.example` file | Created with all required keys documented |
