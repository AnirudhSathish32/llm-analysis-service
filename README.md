# LLM Analysis Service

## Overview
This service is a backend-first FastAPI application that integrates an LLM as a
third-party dependency to analyze text documents. The system prioritizes
reliability, observability, and clean architecture over AI experimentation.

## Architecture
- FastAPI for REST APIs
- PostgreSQL for persistent storage
- Redis for caching and rate limiting
- Async service layer with graceful degradation

## Design Philosophy
The LLM is treated as an unreliable external dependency similar to a payment
provider or search service. All calls are time-bound, retried conservatively,
and failures are persisted without crashing the system.

## Features
- Document analysis with structured persistence
- Redis-backed caching for deterministic requests
- Cost and token usage tracking
- Rate limiting
- Environment-based configuration

## Running Locally

```bash
docker compose up --build
http://localhost:8000/docs
