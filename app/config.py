from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "pullim-api"
    database_url: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost:8443"
    upload_max_bytes: int = 20 * 1024 * 1024

    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_api_key: str = ""
    llm_model: str = "anthropic/claude-sonnet-5"
    llm_timeout_seconds: float = 90.0

    embedding_base_url: str = "https://openrouter.ai/api/v1"
    embedding_api_key: str = ""
    embedding_model: str = "voyage/voyage-4-large"
    embedding_dimension: int = 1024
    embedding_timeout_seconds: float = 60.0

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def embedding_key(self) -> str:
        return self.embedding_api_key or self.llm_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
