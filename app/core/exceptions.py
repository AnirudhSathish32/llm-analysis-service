class AnalysisError(Exception):
    """Base exception for analysis service failures."""


class LLMProviderError(AnalysisError):
    """Raised when all LLM providers fail to produce a result."""


class RAGRetrievalError(AnalysisError):
    """Raised when RAG chunk retrieval fails for a given document."""


class CacheError(AnalysisError):
    """Raised when Redis cache operations fail."""


class DatabaseError(AnalysisError):
    """Raised when database operations fail."""


class TimeoutError(AnalysisError):
    """Raised when an LLM call exceeds the configured timeout."""
