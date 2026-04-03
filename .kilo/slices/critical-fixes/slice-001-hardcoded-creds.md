---
slice: 1
task: critical-fixes
status: completed
dependencies: none
severity: high
---

# Slice 1: Remove hardcoded DB credentials from config defaults

## Goal
Replace hardcoded `llm_user:llm_password` in `database_url` default with empty string, forcing the env var to be set. Add validation that raises on startup if the credential is still the default.

## Files to Create/Modify
- `app/core/config.py` — change default to empty string, add validator that rejects default creds
- `.env` — ensure real credentials are present
- `.env.example` — document `DATABASE_URL` with placeholder values

## What It Builds
A config that fails fast on startup if `DATABASE_URL` is not explicitly set, preventing accidental use of default credentials.

## Tests
(severity: high — 6 tests)
- `test_default_database_url_is_empty` — verify no hardcoded creds in default
- `test_settings_raises_if_default_creds_used` — verify validator rejects `llm_user:llm_password`
- `test_settings_accepts_valid_database_url` — verify real URL passes validation
- `test_settings_accepts_env_var_override` — verify env var overrides default
- `test_default_redis_url_has_no_password` — verify Redis default has no password
- `test_env_example_documents_database_url` — verify `.env.example` has placeholder

## Dependencies
none

## Commit Message
fix(security): remove hardcoded DB credentials from config defaults

## Acceptance Criteria
- [ ] `database_url` default contains no username or password
- [ ] Validator raises `ValueError` if default creds detected
- [ ] `.env.example` documents `DATABASE_URL` with placeholder
- [ ] All existing tests still pass
