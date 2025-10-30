"""
Application configuration management
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Paper Digest"
    PROJECT_VERSION: str = "1.0.0"

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./ai_paper_digest.db"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 86400  # 24 hours

    # AI Service Configuration
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: Optional[str] = None

    # Rate Limiting
    MAX_PAPERS_PER_BATCH: int = 20
    GEMINI_RATE_LIMIT_BATCH_SIZE: int = 5
    GEMINI_RATE_LIMIT_DELAY: float = 2.0

    # arXiv API Configuration
    ARXIV_API_BASE_URL: str = "http://export.arxiv.org/api/query"
    ARXIV_MAX_RESULTS: int = 10

    # GitHub API Configuration (Optional - for code detection)
    GITHUB_TOKEN: Optional[str] = None  # Get from https://github.com/settings/tokens

    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse ALLOWED_ORIGINS string into list"""
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Validate required settings at runtime (not import time)
def validate_settings():
    """Validate required settings - call this at application startup"""
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY environment variable is required. "
            "Get your API key from: https://makersuite.google.com/app/apikey"
        )
