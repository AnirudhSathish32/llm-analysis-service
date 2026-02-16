import hashlib

def hash_input(text: str, analysis_type: str, prompt_version: str) -> str:
    raw = f"{text}:{analysis_type}:{prompt_version}"
    return hashlib.sha256(raw.encode()).hexdigest()
