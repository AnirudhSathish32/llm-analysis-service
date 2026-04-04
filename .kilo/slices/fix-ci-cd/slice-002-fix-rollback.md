---
slice: 2
task: fix-ci-cd
status: implemented
dependencies: slice-001-ci-gate
severity: medium
---

# Slice 2: Fix CD rollback condition

## Goal
Fix the rollback step condition which previously used `failure() && steps.deploy.outcome == 'failure'` — redundant and fragile. Replaced with clean `if: failure()`.

## Files to Modify
- `.github/workflows/cd.yml` — rollback condition simplified

## What It Builds
A reliable rollback mechanism that triggers automatically when any prior step fails.

## Changes
- Replaced `if: failure() && steps.deploy.outcome == 'failure'` with `if: failure()`
- The `failure()` function already covers the case when the deploy step fails
- Rollback logic intact: fetches previous revision from deployments[1], updates service

## Dependencies
- slice-001-ci-gate (implemented in same changeset)

## Commit Message
fix(ci-cd): fix rollback condition to use failure() correctly

## Acceptance Criteria
- [x] Rollback step triggers when deploy fails
- [x] Rollback does not trigger on success
- [x] Rollback gracefully handles missing previous revision
