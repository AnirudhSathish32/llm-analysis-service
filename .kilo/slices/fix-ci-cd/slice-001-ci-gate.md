---
slice: 1
task: fix-ci-cd
status: pending
dependencies: none
severity: medium
---

# Slice 1: Add CI gate to CD pipeline

## Goal
CD pipeline should only deploy if CI tests pass. Add `needs: [lint, test]` to deploy job.

## Files to Create/Modify
- `.github/workflows/cd.yml` — add `needs` dependency chain to deploy job

## What It Builds
A deployment pipeline that only runs after lint and test jobs succeed.

## Tests
N/A (CI/CD change — verify via workflow syntax validation)

## Dependencies
none

## Commit Message
fix(ci-cd): add CI gate to CD pipeline with needs dependency

## Acceptance Criteria
- [ ] Deploy job has `needs: [lint, test]` or equivalent
- [ ] CD workflow only deploys when lint and test pass
- [ ] Workflow YAML is valid (verified via `act` or GitHub Actions UI)
