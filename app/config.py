from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CreatorFlow AI Backend"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"

    # Keep env-driven for all deployment environments.
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/creatorflow_ai",
        alias="DATABASE_URL",
    )
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="openai/gpt-oss-120b", alias="GROQ_MODEL")
    auto_create_tables: bool = Field(default=True, alias="AUTO_CREATE_TABLES")

    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    # Temporary demo user until auth is introduced.
    demo_user_id: int = 1
    demo_user_email: str = "demo@creatorflow.local"
    demo_user_display_name: str = "CreatorFlow Demo User"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
