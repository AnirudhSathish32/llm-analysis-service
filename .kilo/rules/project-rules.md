# Project Rules: LLM Analysis Service

## Metadata
- Created: 2026-04-03
- Project type: team-inherited
- Overrides global rule: none (team conventions take precedence)

## Rule Priority (highest to lowest)
1. Security rules (from global security-baseline — non-negotiable)
2. Team conventions (discovered during recon — fill in below)
3. Personal global rules (fallback only when team has no convention)

## Team Conventions Discovered

### Naming
- Variables/functions: snake_case (`hash_input`, `rate_limiter`, `get_session`)
- Classes: PascalCase (`AnalysisService`, `LLMRouter`, `AnalysisRequestSchema`)
- Pydantic schemas: `*Schema` suffix (`AnalysisRequestSchema`, `CitationSchema`)
- Test classes: `Test*` prefix with grouped sections (`TestHashInput`, `TestBuildPrompt`)
- Test methods: `test_[scenario]_[expected]` (e.g. `test_different_text_produces_different_hash`)
- DB tables: plural snake_case (`analysis_requests`, `analysis_results`, `documents`)

### Import Ordering
1. stdlib (uuid, asyncio, time, random)
2. third-party (fastapi, sqlalchemy, pydantic, redis)
3. internal (app.*) — separated by blank line
4. Relative imports not used

### File Structure
- `app/api/routes/` — FastAPI routers with `prefix` and `tags`
- `app/core/` — config and middleware (rate limiting)
- `app/db/` — base, models, session, migrations helpers
- `app/cache/` — Redis client singleton
- `app/schemas/` — Pydantic request/response schemas
- `app/services/` — business logic (analysis_service, llm_client, llm_router, rag_pipeline)
- `app/utils/` — shared utilities (hashing)
- `tests/` — flat test files, grouped by class with section comment dividers

### Error Handling
- Bare `except Exception` used in analysis_service catch-all (anti-pattern — should be specific)
- `HTTPException` for rate limiting (429)
- `RuntimeError` for fatal startup failures
- DB retries with `OperationalError` catch in `create_tables.py`
- `print()` used for debug/logging in `config.py`, `main.py`, `test_connection.py`, `create_tables.py` (anti-pattern — should use proper logging)

### Test Structure
- `pytest` with `pytest.mark.asyncio` for async tests
- `unittest.mock.AsyncMock`, `MagicMock`, `patch` for mocking
- Tests grouped into sections with `# ===` comment dividers
- Helper methods on test classes (e.g. `_make_llm_result`)
- External deps (Redis, LLM, RAG) are mocked — no real API calls

### Test Execution
- All tests MUST be run inside the Docker environment, never directly on the host
- Command: `docker compose run --rm api pytest` (or `docker compose exec api pytest` for running container)
- Docker Compose provides the required services (PostgreSQL, Redis) that tests may depend on
- Never run `pytest` directly against host Python — dependencies and services won't be available

### Test Execution
- All tests MUST be run inside the Docker environment, never directly on the host
- Command: `docker compose run --rm api pytest` (or `docker compose exec api pytest` for running container)
- Docker Compose provides the required services (PostgreSQL, Redis) that tests may depend on
- Never run `pytest` directly against host Python — dependencies and services won't be available

### Commit Format
- Conventional Commits: `type(scope): description`
- Types observed: feat, fix, test, chore, docs, perf, refactor

## Architecture Constraints
- FastAPI async throughout
- SQLAlchemy async engine with `async_sessionmaker`
- Alembic for migrations (not `create_all_tables` in production)
- UUID primary keys everywhere
- Redis used for both caching and rate limiting
- LLM router: Anthropic primary → Gemini fallback
- RAG: LangChain + Pinecone + Google Embeddings
- AWS ECS Fargate deployment with sidecar Redis

## File Boundaries
Safe to modify:
- `app/services/` — business logic layer
- `app/api/routes/` — endpoint definitions
- `app/schemas/` — request/response schemas
- `tests/` — test suite

Do not touch without approval:
- `task-definition.json` — ECS deployment config
- `.github/workflows/cd.yml` — CI/CD pipeline
- `app/db/base.py` — ORM base declaration
- `app/db/session.py` — DB engine/session singleton

## Data Contracts
- `AnalysisRequestSchema`: text (1-10000 chars), analysis_type (summary|key_points), prompt_version (str), document_id (optional str)
- `AnalysisResponseSchema`: request_id (UUID), status (str), result (optional dict), cached (bool), provider (optional str), rag_chunks_used (optional int), citations (optional list[CitationSchema])
- `CitationSchema`: chunk_index (int), page (str), source (str)

## Error Handling Specifics
- Service layer catches all exceptions and returns `status: "failed"` — does not re-raise
- Router raises `RuntimeError` when both providers fail
- Rate limiter raises `HTTPException(429)`
- DB creation retries on `OperationalError` with exponential backoff

## Input Validation
- Pydantic `field_validator` for text length (1-10000 chars)
- `Literal` type for `analysis_type` enum constraint
- SHA-256 hashing of inputs for cache key deduplication

## Anti-Patterns Found
- `print()` statements in production code (`config.py`, `main.py`) — should use `logging` module
- Bare `except Exception` in `analysis_service.py` — swallows error details, should catch specific exceptions and log
- `config.py` uses `os.getenv()` manually instead of relying on pydantic-settings env loading
- `llm_client.py` is a simulated stub — not connected to real LLM providers (real logic in `llm_router.py`)
- `create_tables.py` used instead of Alembic for table creation in lifespan
- `docker-compose.yaml` references ChromaDB but `task-definition.json` and README reference Pinecone — inconsistent vector DB
- No `.gitignore` file detected in repo root

## Override Log
[none]
