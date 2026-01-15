"""
Centralized application settings.
All configuration is loaded from environment variables with sensible defaults.
"""
import os
from functools import lru_cache
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Use get_settings() to get a cached instance.
    """
    
    # ===== Database =====
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/interviewer"
    
    # ===== Authentication (Clerk) =====
    CLERK_ISSUER: str = "https://bright-unicorn-12.clerk.accounts.dev"
    
    # ===== LiveKit =====
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    LIVEKIT_URL: str = ""
    
    # ===== AI Providers =====
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "models/gemini-2.5-flash"
    SHADOW_MODEL: str = "models/gemini-2.5-flash"
    DEEPGRAM_API_KEY: str = ""
    
    # ===== Rate Limiting =====
    RATE_LIMIT: str = "100/minute"
    
    # ===== CORS =====
    CORS_ORIGINS: str = ""  # Comma-separated list
    
    # ===== Opik Observability =====
    OPIK_ENABLED: bool = False
    OPIK_API_KEY: str = ""
    OPIK_WORKSPACE: str = "default"
    OPIK_PROJECT_NAME: str = "ai-interviewer"

    # ===== Debug =====
    DEBUG: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list."""
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        # Default origins
        return [
            "http://localhost:3000",
            "https://interviewer-frontend-766703134732.asia-southeast1.run.app",
        ]
    
    @property
    def clerk_jwks_url(self) -> str:
        """Get JWKS URL from issuer."""
        return f"{self.CLERK_ISSUER}/.well-known/jwks.json"
    
    @property
    def base_path(self) -> Path:
        """
        Get the absolute path to the backend project root.
        Robustly navigates up from config/settings.py to backend/.
        """
        # config/settings.py -> config/ -> backend/
        return Path(__file__).resolve().parent.parent

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Usage:
        from config.settings import get_settings
        settings = get_settings()
        print(settings.DATABASE_URL)
    """
    return Settings()


# Convenience alias for backward compatibility
settings = get_settings()
