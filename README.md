# LLM Analysis Service
 
A production-deployed document analysis API powered by a RAG pipeline, multi-provider LLM routing, and cloud-native infrastructure on AWS ECS Fargate.
 
## Live Demo
 
The API is live and accessible at the Swagger UI:
```
http://3.129.206.59:8000/docs
```
 
---
 
## What It Does
 
Users upload documents (PDF, TXT, CSV) and ask questions about them. The system retrieves the most semantically relevant sections of the document and passes them as context to an LLM, which returns a structured answer with source citations.
 
Without a document, the API performs standalone text analysis — summarisation or key point extraction.
 
---
 
## Architecture
 
```
Client Request
      │
      ▼
FastAPI (AWS ECS Fargate)
      │
      ├── Rate Limiter (Redis)
      │
      ├── Cache Check (Redis) ──── Cache Hit → Return instantly
      │
      ├── RAG Retrieval (Pinecone) ← document_id provided
      │         │
      │    Google Embeddings (gemini-embedding-001)
      │
      ├── LLM Router
      │         ├── Primary: Anthropic Claude
      │         └── Fallback: Google Gemini
      │
      └── PostgreSQL (AWS RDS)
                └── Logs every request: tokens, cost, latency
```
 
---
 
## Tech Stack
 
| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn (async) |
| LLM Routing | Anthropic Claude (primary) → Google Gemini (fallback) |
| RAG Pipeline | LangChain + Pinecone (vector DB) + Google Embeddings |
| Caching | Redis (cache + rate limiting) |
| Database | PostgreSQL via async SQLAlchemy |
| Containerisation | Docker + Docker Compose |
| Cloud | AWS ECS Fargate + ECR + RDS + Secrets Manager |
| CI/CD | GitHub Actions (lint → test → build → deploy) |
| Observability | AWS CloudWatch |
 
---
 
## Key Features
 
**Multi-provider LLM routing with automatic fallback**
Anthropic Claude is the primary LLM. If it fails for any reason — rate limit, timeout, API error — the system automatically retries with Google Gemini. Both providers return a consistent result shape so the rest of the system never needs to know which one responded.
 
**RAG pipeline with source citations**
Documents are chunked using LangChain's `RecursiveCharacterTextSplitter` (500 character chunks, 50 character overlap), embedded using Google's `gemini-embedding-001` model (3072 dimensions), and stored in Pinecone. On each query, the top 4 semantically relevant chunks are retrieved and injected into the LLM prompt as context. The response includes citations with page numbers and source filenames.
 
**Redis caching**
Responses are cached in Redis using a SHA-256 hash of the request inputs including `document_id`. Cache TTL is configurable. Identical queries return instantly without hitting the LLM or vector database.
 
**Cost and token tracking**
Every request logs token usage (input + output) and estimated cost in USD to PostgreSQL. Aggregated metrics are available via the `/v1/metrics/usage` endpoint.
 
**Production-grade CI/CD**
GitHub Actions runs linting (flake8) and a pytest test suite on every push. On merge to main, it builds a Docker image, pushes to ECR, and deploys a new task definition to ECS with automatic rollback on failure.
 
---
 
## API Endpoints
 
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/documents` | Upload a PDF, TXT, or CSV for RAG ingestion |
| `GET` | `/v1/documents/{id}` | Check ingestion status and chunk count |
| `POST` | `/v1/analysis` | Analyse text — with or without RAG context |
| `GET` | `/v1/metrics/usage` | Aggregate token usage and cost |
| `GET` | `/v1/metrics/usage/by_type` | Usage breakdown by analysis type |
| `GET` | `/health` | Health check |
 
### Example: Upload a document
 
```bash
curl -X POST http://your-ip:8000/v1/documents \
  -F "file=@report.pdf"
```
 
```json
{
  "document_id": "3f7a1c2e-...",
  "filename": "report.pdf",
  "status": "ready",
  "chunk_count": 42
}
```
 
### Example: Query with RAG
 
```bash
curl -X POST http://your-ip:8000/v1/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What are the key findings?",
    "analysis_type": "key_points",
    "document_id": "3f7a1c2e-..."
  }'
```
 
```json
{
  "request_id": "9a2b...",
  "status": "completed",
  "result": { "content": "..." },
  "cached": false,
  "provider": "anthropic",
  "rag_chunks_used": 4,
  "citations": [
    { "chunk_index": 0, "page": "3", "source": "report.pdf" },
    { "chunk_index": 1, "page": "7", "source": "report.pdf" }
  ]
}
```
 
---
 
## Running Locally
 
**Prerequisites:** Docker Desktop, Python 3.11
 
```bash
git clone https://github.com/your-username/llm-analysis-service
cd llm-analysis-service
 
cp .env.example .env
# Fill in ANTHROPIC_API_KEY, GEMINI_API_KEY, PINECONE_API_KEY
 
docker compose up --build
```
 
API available at `http://localhost:8000/docs`
 
---
 
## Infrastructure
 
The service runs on AWS ECS Fargate with the following containers per task:
 
- `llm-analysis-service` — FastAPI application
- `redis` — Sidecar for caching and rate limiting
 
External managed services:
- **AWS RDS** — PostgreSQL for persistent storage
- **AWS Secrets Manager** — API keys and database credentials
- **Pinecone** — Serverless vector database
 
Database migrations are managed with Alembic.
 
---
 
## Environment Variables
 
See `.env.example` for the full list. Key variables:
 
```
ANTHROPIC_API_KEY      Anthropic API key
GEMINI_API_KEY         Google Gemini API key
PINECONE_API_KEY       Pinecone API key
PINECONE_INDEX         Pinecone index name
DATABASE_URL           PostgreSQL connection string
REDIS_URL              Redis connection string
CACHE_TTL_SECONDS      Cache expiry (default: 3600)
RAG_TOP_K              Number of chunks to retrieve (default: 4)
```
 
---
 
## Design Decisions
 
**Why treat the LLM as an unreliable dependency?**
LLM APIs have unpredictable latency and occasional outages. The router pattern — primary provider with automatic fallback — means the service degrades gracefully rather than failing completely. Every call is time-bounded with a configurable timeout.
 
**Why Pinecone over self-hosted ChromaDB?**
Pinecone is a managed serverless vector database — no infrastructure to maintain, predictable performance, and it's what production teams actually use at scale. Self-hosting ChromaDB adds operational complexity with no benefit at this scale.
 
**Why Redis for both caching and rate limiting?**
Both use cases share the same infrastructure. Rate limiting uses Redis atomic increment operations, caching uses key-value storage with TTL. Running Redis as a sidecar keeps the architecture simple without VPC networking complexity.

## Running Locally

```bash
docker compose up --build
http://localhost:8000/docs
