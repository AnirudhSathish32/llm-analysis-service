---
slice: 4
task: fix-anti-patterns
status: completed
dependencies: slice-001
---

# Slice 4: Remove ChromaDB references — align with Pinecone-only architecture

## Goal
Remove ChromaDB from docker-compose.yaml and config.py since production uses Pinecone. Clean up the inconsistent vector DB references.

## Files to Create/Modify
- `docker-compose.yaml` — remove chromadb service and volume
- `app/core/config.py` — remove chroma_host and chroma_port fields
- `.env` — remove CHROMA_HOST and CHROMA_PORT entries

## What It Builds
A consistent architecture where only Pinecone is the vector database — no references to ChromaDB anywhere.

## Tests
- No new tests needed — this is a config cleanup slice
- Verify docker-compose up still works without chromadb service

## Dependencies
slice-001 (logging infrastructure)

## Commit Message
fix(config): remove ChromaDB references — align with Pinecone-only architecture

## Acceptance Criteria
- [ ] No chromadb service in docker-compose.yaml
- [ ] No chroma_host/chroma_port in config.py
- [ ] No CHROMA_HOST/CHROMA_PORT in .env
- [ ] docker-compose.yaml still valid (db, redis, api services remain)
- [ ] All existing tests still pass
