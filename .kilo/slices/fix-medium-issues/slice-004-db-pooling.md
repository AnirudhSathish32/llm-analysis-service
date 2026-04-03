---
slice: 4
task: fix-medium-issues
status: pending
dependencies: none
---

# Slice 4: Add DB connection pooling configuration

## Goal
`create_async_engine` has no `pool_size`, `max_overflow`, or `pool_timeout` settings. Add sensible defaults for production.

## Files to Modify
- `app/db/session.py` — add `pool_size=5`, `max_overflow=10`, `pool_timeout=30` to `create_async_engine`
- `app/core/config.py` — add optional `db_pool_size`, `db_pool_max_overflow`, `db_pool_timeout` settings

## Tests
- `test_db_engine_uses_connection_pool` — verify pool settings are applied

## Commit Message
perf(db): add connection pooling configuration to async engine

## Acceptance Criteria
- [ ] `create_async_engine` has explicit pool settings
- [ ] Pool settings are configurable via env vars with sensible defaults
- [ ] All existing tests still pass
