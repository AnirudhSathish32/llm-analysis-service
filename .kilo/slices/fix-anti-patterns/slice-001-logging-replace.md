---
slice: 1
task: fix-anti-patterns
status: completed
dependencies: none
---

# Slice 1: Replace print() with logging module

## Goal
Replace all `print()` debug statements in production code with proper `logging` module calls.

## Files to Create/Modify
- `app/core/config.py` — remove print statements, use logging
- `app/main.py` — replace print statements in lifespan with logging
- `app/db/test_connection.py` — replace print with logging
- `app/db/create_tables.py` — replace print with logging

## What It Builds
A consistent logging approach across all modules that currently use print() for debug output.

## Tests
- `test_logging_config` — verify logger is configured and emits at correct level
- `test_lifespan_logs_table_creation` — verify lifespan uses logger, not print
- `test_create_tables_logs_retries` — verify create_tables uses logger for retry messages

## Dependencies
none

## Commit Message
fix(logging): replace print() statements with logging module across codebase

## Acceptance Criteria
- [ ] No print() calls remain in app/ (except test_connection.py __main__ block)
- [ ] config.py has no print() calls
- [ ] main.py lifespan uses logger.info/logger.error
- [ ] create_tables.py uses logger for retry/failure messages
- [ ] All existing tests still pass
