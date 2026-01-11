from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings."""

    hf_token: Optional[str] = None
    hf_model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    use_inference_api: bool = True

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    database_url: str = "sqlite+aiosqlite:////data/phone_assistant.db"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    rate_limit_per_minute: int = 30

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
