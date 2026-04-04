---
slice: 1
task: fix-ci-cd
status: implemented
dependencies: none
severity: medium
---

# Slice 1: Add CI gate to CD pipeline

## Goal
Make the CD deploy job depend on CI test and lint jobs passing, so deployment only happens when CI succeeds.

## Files to Modify
- `.github/workflows/cd.yml` — use `workflow_run` trigger to gate on CI completion
- `.github/workflows/ci.yml` — already split into `lint` and `test` jobs

## What It Builds
A proper CI→CD dependency chain: lint and test must pass before deploy runs.

## Changes
- CD workflow uses `workflow_run` trigger with `workflows: ["CI"]` and `types: [completed]`
- Deploy job has `if: ${{ github.event.workflow_run.conclusion == 'success' }}` guard
- CI workflow already has separate `lint` and `test` jobs with security scanning

## Dependencies
none

## Commit Message
chore(ci-cd): add CI gate to CD pipeline so deploy requires passing tests and lint

## Acceptance Criteria
- [x] CD workflow triggers only after CI workflow completes
- [x] Deploy does not run if CI fails (guarded by `conclusion == 'success'`)
- [x] Workflow YAML is valid (no syntax errors)
