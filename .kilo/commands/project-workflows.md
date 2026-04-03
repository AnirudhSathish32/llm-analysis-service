---
name: llm-analysis-service-workflows
description: >
  Project-specific workflows for llm-analysis-service (team codebase).
---

# Project Workflows: LLM Analysis Service

## Metadata
- Created: 2026-04-03
- Project type: team-inherited

## Team Conventions Recon Workflow
Already completed during `/inherit-init`. Findings are in:
- `.kilo/rules/project-rules.md` → "Team Conventions Discovered"
- `.kilo/skills/project-skill/SKILL.md` → "Team Patterns in Use"

To update conventions after discovering new patterns:
1. Edit the relevant section in `project-rules.md` or `SKILL.md`
2. Commit with `chore: update team conventions — [what changed]`

## New Node / Module Workflow
1. Check `.kilo/skills/project-skill/SKILL.md` for existing patterns
2. Create file in the correct layer directory (`app/services/`, `app/api/routes/`, etc.)
3. Follow naming: snake_case for modules/functions, PascalCase for classes, `*Schema` for Pydantic
4. Import ordering: stdlib → third-party → blank line → internal (`app.*`)
5. Write tests in `tests/` using `Test*` class grouping with `# ===` dividers
6. Run `pytest` to verify nothing breaks
7. Commit with Conventional Commits format

## Integration Workflow
1. Wire new service into existing router or create new route in `app/api/routes/`
2. Register router in `app/main.py` via `app.include_router()`
3. Add any new env vars to `.env` and document in README
4. Update `task-definition.json` if new secrets or env vars needed
5. Run full test suite

## Deployment Workflow
1. Push to `main` → GitHub Actions runs lint → test → build → deploy
2. Image pushed to ECR, ECS task definition updated, service deployed
3. Rollback is automatic on failure (reverts to previous task definition revision)
4. Verify at `http://<ecs-ip>:8000/docs`
