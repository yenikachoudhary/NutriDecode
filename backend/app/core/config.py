from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "NutriDecode API"
    app_version: str = "0.2.0"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    frontend_origins: str = (
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    )

    tesseract_cmd: str | None = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # AI Provider Settings
    ai_provider: str = "auto"  # "auto", "gemini", "openai", "mock", "disabled"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    openai_api_key: str | None = None
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    ai_timeout_seconds: float = 25.0
    ai_cache_ttl_seconds: float = 3600.0  # 1 hour in-memory caching

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Convert comma-separated frontend origins into a list."""
        return [
            origin.strip()
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Create and cache one settings instance."""
    return Settings()
