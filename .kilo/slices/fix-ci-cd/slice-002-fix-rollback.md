---
slice: 2
task: fix-ci-cd
status: pending
dependencies: fix-ci-cd/slice-001
severity: medium
---

# Slice 2: Fix CD rollback condition

## Goal
Fix invalid rollback condition `steps.deploy.outcome != 'success'`. Use `if: failure()` on a separate rollback step and add explicit rollback job.

## Files to Create/Modify
- `.github/workflows/cd.yml` — replace invalid rollback condition with `if: failure()`, add explicit rollback job

## What It Builds
A reliable rollback mechanism that triggers correctly on deployment failure.

## Tests
N/A (CI/CD change — verify via workflow syntax validation)

## Dependencies
`fix-ci-cd/slice-001`

## Commit Message
fix(ci-cd): fix rollback condition and add explicit rollback job

## Acceptance Criteria
- [ ] Rollback step uses `if: failure()` instead of invalid condition
- [ ] Explicit rollback job defined that reverts to previous task definition
- [ ] Rollback triggers on deploy failure
- [ ] Workflow YAML is valid
