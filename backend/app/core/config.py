
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "NutriDecode API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    frontend_origins: str = (
        "http://localhost:3000,http://localhost:5173"
    )

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
    tesseract_cmd: str | None = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


@lru_cache
def get_settings() -> Settings:
    """Create and cache one settings instance."""
    return Settings()
