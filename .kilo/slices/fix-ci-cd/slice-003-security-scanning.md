---
slice: 3
task: fix-ci-cd
status: pending
dependencies: fix-ci-cd/slice-001
severity: medium
---

# Slice 3: Add security scanning to CI

## Goal
Add `pip-audit` for dependency vulnerabilities, Docker image scan (trivy), and secrets check (gitleaks).

## Files to Create/Modify
- `.github/workflows/cd.yml` — add security scanning steps to CI workflow

## What It Builds
Automated security checks that fail CI on known CVEs, vulnerable Docker images, or hardcoded secrets.

## Tests
N/A (CI/CD change — verify via workflow syntax validation)

## Dependencies
`fix-ci-cd/slice-001`

## Commit Message
fix(ci-cd): add security scanning with pip-audit, trivy, and gitleaks

## Acceptance Criteria
- [ ] `pip-audit` step added to check for vulnerable dependencies
- [ ] Trivy step added to scan Docker image for vulnerabilities
- [ ] Gitleaks step added to check for hardcoded secrets
- [ ] CI fails on known CVEs or secrets
- [ ] Workflow YAML is valid
