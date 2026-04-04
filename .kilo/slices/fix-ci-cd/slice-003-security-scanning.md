---
slice: 3
task: fix-ci-cd
status: implemented
dependencies: slice-001-ci-gate
severity: medium
---

# Slice 3: Add security scanning to CI

## Goal
Add security scanning steps to the CI pipeline to catch vulnerable dependencies, container image issues, and hardcoded secrets.

## Files to Modify
- `.github/workflows/ci.yml` — added pip-audit, gitleaks, and Trivy steps

## What It Builds
Three security gates in CI: dependency audit, container scan, and secret detection.

## Changes
- Added `pip-audit` step in lint job — fails on known CVEs in Python dependencies
- Added `gitleaks/gitleaks-action@v2` in lint job — scans for hardcoded secrets
- Added `aquasecurity/trivy-action@master` in test job — scans Docker image for CRITICAL/HIGH CVEs

## Dependencies
- slice-001-ci-gate (implemented in same changeset)

## Commit Message
chore(ci-cd): add security scanning with pip-audit, Trivy, and Gitleaks

## Acceptance Criteria
- [x] CI fails when pip-audit finds known vulnerable dependencies
- [x] CI fails when Trivy finds critical/high CVEs in Docker image
- [x] CI fails when Gitleaks detects hardcoded secrets
- [x] All existing CI steps still present
