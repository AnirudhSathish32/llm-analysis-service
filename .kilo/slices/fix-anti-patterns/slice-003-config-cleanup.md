---
slice: 3
task: fix-anti-patterns
status: pending
dependencies: slice-001
---

# Slice 3: Clean up config.py — remove manual os.getenv() usage

## Goal
Remove manual `os.getenv()` calls in `config.py` and rely entirely on pydantic-settings env loading with proper field defaults.

## Files to Create/Modify
- `app/core/config.py` — replace os.getenv() with pydantic-settings Field(default=...)
- `.env.example` — create with all required keys documented

## What It Builds
A clean configuration module that uses pydantic-settings properly without manual env var fetching.

## Tests
- `test_settings_loads_from_env` — verify settings load from environment variables
- `test_settings_uses_defaults_when_env_missing` — verify defaults work without .env
- `test_env_example_has_all_required_keys` — verify .env.example documents all vars

## Dependencies
slice-001 (logging infrastructure)

## Commit Message
fix(config): replace manual os.getenv() with pydantic-settings Field defaults

## Acceptance Criteria
- [ ] No `os.getenv()` calls in config.py
- [ ] All settings use pydantic-settings Field(default=...) pattern
- [ ] `.env.example` created with all required keys documented
- [ ] Settings still work with existing .env file
- [ ] All existing tests still pass
