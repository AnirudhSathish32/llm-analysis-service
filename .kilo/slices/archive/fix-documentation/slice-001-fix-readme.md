---
slice: 1
task: fix-documentation
status: completed
dependencies: none
severity: low
---

# Slice 1: Fix README issues

## Goal
Fix README inconsistencies: remove duplicate section, fix CACHE_TTL default, remove live IP.

## Files to Create/Modify
- `README.md` — remove duplicate "Running Locally" section, fix CACHE_TTL default to 86400, remove live API IP

## What It Builds
Accurate, clean documentation.

## Tests
(severity: low — 2 tests)
- `test_readme_no_duplicate_running_locally` — verify only one "Running Locally" section
- `test_readme_no_live_api_ip` — verify no hardcoded IP addresses in README

## Dependencies
none

## Commit Message
fix(docs): fix README duplicates, wrong defaults, and remove live API IP

## Acceptance Criteria
- [ ] No duplicate "Running Locally" section
- [ ] CACHE_TTL_SECONDS default says 86400
- [ ] No live API IP (18.222.255.28) in README
- [ ] All existing tests still pass
