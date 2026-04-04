import pytest


# =============================================================================
# README documentation fixes
# =============================================================================

class TestReadmeFixes:
    def test_readme_no_duplicate_running_locally(self):
        with open("README.md") as f:
            content = f.read()
        count = content.count("## Running Locally")
        assert count == 1, f"Found {count} 'Running Locally' sections, expected 1"

    def test_readme_no_live_api_ip(self):
        with open("README.md") as f:
            content = f.read()
        assert "18.222.255.28" not in content

    def test_readme_cache_ttl_default_is_86400(self):
        with open("README.md") as f:
            content = f.read()
        assert "default: 86400" in content
        assert "default: 3600" not in content


# =============================================================================
# Module docstrings
# =============================================================================

class TestModuleDocstrings:
    def test_llm_router_has_module_docstring(self):
        import app.services.llm_router as llm_router
        assert llm_router.__doc__ is not None
        assert "fallback" in llm_router.__doc__.lower()

    def test_rag_pipeline_has_module_docstring(self):
        import app.services.rag_pipeline as rag_pipeline
        assert rag_pipeline.__doc__ is not None
        assert "ingestion" in rag_pipeline.__doc__.lower()
        assert "retrieval" in rag_pipeline.__doc__.lower()

    def test_health_endpoint_has_docstring(self):
        from app.main import health
        assert health.__doc__ is not None
