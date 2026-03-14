import hashlib

def hash_input(
    text: str,
    analysis_type: str,
    prompt_version: str,
    document_id: str | None = None,
) -> str:
    """
    Deterministic hash of all inputs that affect the LLM response.
    Including document_id means the same question against two different
    documents will never collide in the cache.
    """
    raw = f"{text}:{analysis_type}:{prompt_version}:{document_id or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()
