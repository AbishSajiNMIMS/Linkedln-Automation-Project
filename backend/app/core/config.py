from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InSync Thought Leadership Engine"
    environment: str = "development"
    database_url: str = "sqlite:///./insync.db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    clerk_jwks_url: str | None = None
    n8n_webhook_secret: str | None = None
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
