---
slice: 3
task: fix-medium-issues
status: completed
dependencies: none
---

# Slice 3: Add Redis connection lifecycle management

## Goal
`redis_client` is created at module import with no explicit connection, no health check, and no close on shutdown. Add connection initialization and graceful shutdown.

## Files to Modify
- `app/cache/redis.py` — add `connect()` and `close()` methods, add `ping()` health check
- `app/main.py` — call `redis_client.close()` in lifespan shutdown

## Tests
- `test_redis_client_connect_on_first_use` — verify connection is established
- `test_redis_client_close_on_shutdown` — verify close is called during app shutdown

## Commit Message
perf(redis): add connection lifecycle management with connect and close

## Acceptance Criteria
- [ ] Redis client has explicit `connect()` method
- [ ] Redis client has explicit `close()` method
- [ ] Lifespan shutdown calls `redis_client.close()`
- [ ] All existing tests still pass
