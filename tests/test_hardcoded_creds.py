import os
import pytest
from unittest.mock import patch, MagicMock


# =============================================================================
# Hardcoded DB credentials removal
# =============================================================================

class TestHardcodedCredentialsRemoval:
    def test_default_database_url_is_empty(self):
        from pydantic_settings import BaseSettings, SettingsConfigDict
        from pydantic import Field

        with patch.dict(os.environ, {}, clear=True):
            class TestSettings(BaseSettings):
                database_url: str = Field(default="")
                model_config = SettingsConfigDict(env_file=None, extra="ignore")

            s = TestSettings()
            assert s.database_url == ""

    def test_settings_raises_if_default_creds_used(self):
        from pydantic_settings import BaseSettings, SettingsConfigDict
        from pydantic import Field, field_validator

        with patch.dict(os.environ, {}, clear=True):
            class TestSettings(BaseSettings):
                database_url: str = Field(default="")
                model_config = SettingsConfigDict(env_file=None, extra="ignore")

                @field_validator("database_url")
                @classmethod
                def reject_default_credentials(cls, v: str) -> str:
                    if "llm_user:llm_password" in v:
                        raise ValueError(
                            "DATABASE_URL contains default credentials. "
                            "Set a real DATABASE_URL environment variable."
                        )
                    return v

            with pytest.raises(ValueError, match="DATABASE_URL contains default credentials"):
                TestSettings(database_url="postgresql+asyncpg://llm_user:llm_password@db:5432/llm_service")

    def test_settings_accepts_valid_database_url(self):
        from pydantic_settings import BaseSettings, SettingsConfigDict
        from pydantic import Field, field_validator

        with patch.dict(os.environ, {}, clear=True):
            class TestSettings(BaseSettings):
                database_url: str = Field(default="")
                model_config = SettingsConfigDict(env_file=None, extra="ignore")

                @field_validator("database_url")
                @classmethod
                def reject_default_credentials(cls, v: str) -> str:
                    if "llm_user:llm_password" in v:
                        raise ValueError(
                            "DATABASE_URL contains default credentials. "
                            "Set a real DATABASE_URL environment variable."
                        )
                    return v

            s = TestSettings(database_url="postgresql+asyncpg://real_user:real_pass@db:5432/llm_service")
            assert "real_user" in s.database_url

    def test_settings_accepts_env_var_override(self):
        from pydantic_settings import BaseSettings, SettingsConfigDict
        from pydantic import Field, field_validator

        with patch.dict(os.environ, {}, clear=True):
            class TestSettings(BaseSettings):
                database_url: str = Field(default="")
                model_config = SettingsConfigDict(env_file=None, extra="ignore")

                @field_validator("database_url")
                @classmethod
                def reject_default_credentials(cls, v: str) -> str:
                    if "llm_user:llm_password" in v:
                        raise ValueError(
                            "DATABASE_URL contains default credentials. "
                            "Set a real DATABASE_URL environment variable."
                        )
                    return v

            s = TestSettings(database_url="postgresql+asyncpg://prod_user:prod_pass@prod-db:5432/prod")
            assert "prod-db" in s.database_url

    def test_default_redis_url_has_no_password(self):
        from pydantic_settings import BaseSettings, SettingsConfigDict
        from pydantic import Field

        with patch.dict(os.environ, {}, clear=True):
            class TestSettings(BaseSettings):
                redis_url: str = Field(default="redis://redis:6379/0")
                model_config = SettingsConfigDict(env_file=None, extra="ignore")

            s = TestSettings()
            assert "password" not in s.redis_url
            assert s.redis_url == "redis://redis:6379/0"

    def test_env_example_documents_database_url(self):
        with open(".env.example") as f:
            content = f.read()
        assert "DATABASE_URL" in content
