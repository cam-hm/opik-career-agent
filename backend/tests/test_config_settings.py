"""
Tests for config/settings.py - Application settings.
"""
import os
import pytest
from unittest.mock import patch


class TestSettings:
    """Tests for Settings class."""
    
    def test_default_database_url(self):
        """Should have default database URL."""
        from config.settings import Settings
        settings = Settings()
        assert "postgresql" in settings.DATABASE_URL
    
    def test_default_gemini_model(self):
        """Should default to Gemini 2.5 Flash."""
        from config.settings import Settings
        settings = Settings()
        assert settings.GEMINI_MODEL == "models/gemini-2.5-flash"
    
    def test_default_rate_limit(self):
        """Should have default rate limit."""
        from config.settings import Settings
        settings = Settings()
        assert settings.RATE_LIMIT == "100/minute"
    
    def test_cors_origins_list_empty_returns_defaults(self):
        """Empty CORS_ORIGINS should return default origins."""
        from config.settings import Settings
        settings = Settings(CORS_ORIGINS="")
        origins = settings.cors_origins_list
        assert "http://localhost:3000" in origins
    
    def test_cors_origins_list_parses_comma_separated(self):
        """Should parse comma-separated CORS origins."""
        from config.settings import Settings
        settings = Settings(CORS_ORIGINS="http://a.com, http://b.com")
        origins = settings.cors_origins_list
        assert "http://a.com" in origins
        assert "http://b.com" in origins
    
    def test_clerk_jwks_url_derived_from_issuer(self):
        """Should derive JWKS URL from Clerk issuer."""
        from config.settings import Settings
        settings = Settings(CLERK_ISSUER="https://test.clerk.accounts.dev")
        assert settings.clerk_jwks_url == "https://test.clerk.accounts.dev/.well-known/jwks.json"


class TestGetSettings:
    """Tests for get_settings function."""
    
    def test_returns_settings_instance(self):
        """Should return a Settings instance."""
        from config.settings import get_settings, Settings
        settings = get_settings()
        assert isinstance(settings, Settings)
    
    def test_is_cached(self):
        """Should return same cached instance."""
        from config.settings import get_settings
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
