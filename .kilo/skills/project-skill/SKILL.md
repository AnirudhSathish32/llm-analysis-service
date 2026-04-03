---
name: llm-analysis-service-skill
description: >
  Project-specific skill for llm-analysis-service (team codebase).
  Team patterns discovered during recon pass.
version: 0.1.0
---

# LLM Analysis Service Skill

## Tech Stack
- FastAPI 0.129 + Uvicorn (async)
- SQLAlchemy 2.0 (async) + asyncpg
- Pydantic 2.x for schemas/validation
- Redis (async) for caching + rate limiting
- Anthropic Claude (primary) + Google Gemini (fallback)
- LangChain + Pinecone for RAG
- Alembic for migrations
- pytest + pytest-asyncio for testing
- AWS ECS Fargate + ECR + RDS + Secrets Manager
- GitHub Actions for CI/CD

## Architecture Overview
```
Client → FastAPI → Rate Limiter (Redis) → Cache Check (Redis)
  → RAG Retrieval (Pinecone) → LLM Router (Anthropic → Gemini)
  → PostgreSQL (logging: tokens, cost, latency)
```

Layered structure: `app/api/routes/` → `app/services/` → `app/db/`, `app/cache/`, `app/core/`

## Team Patterns in Use
- Service layer pattern: routers instantiate service, service orchestrates clients
- Singleton clients at module level (`redis_client`, `engine`, `AsyncSessionLocal`)
- Pydantic schemas with `*Schema` suffix for all request/response shapes
- UUID primary keys on all DB models
- Section dividers in test files: `# === Section Name ===`
- Test classes grouped by concern (`TestHashInput`, `TestBuildPrompt`, `TestLLMRouter`)
- Mocking external deps with `AsyncMock` + `patch`
- Conventional Commits for all commit messages

## Data Contracts
- Analysis: text (1-10000 chars), analysis_type (summary|key_points), optional document_id
- Response: UUID request_id, status, result dict, cached flag, provider, citations
- Citations: chunk_index, page, source filename

## File Boundaries
Safe to modify:
- `app/services/` — business logic
- `app/api/routes/` — endpoints
- `app/schemas/` — Pydantic models
- `tests/` — test suite

Do not touch without approval:
- `task-definition.json` — ECS config
- `.github/workflows/cd.yml` — CI/CD pipeline
- `app/db/base.py` — ORM base
- `app/db/session.py` — DB singleton

## Anti-Patterns Found
- `print()` in production code instead of `logging`
- Bare `except Exception` in analysis service
- ChromaDB in docker-compose but Pinecone in production — inconsistent
- No `.gitignore` in repo root
- `create_tables.py` used instead of Alembic in app lifespan
