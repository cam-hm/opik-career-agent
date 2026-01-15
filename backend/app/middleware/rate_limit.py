"""
Rate Limiting Middleware for FastAPI

Uses slowapi to implement rate limiting on API endpoints.
"""
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure rate limiter
# Default: 100 requests per minute per IP
# Can be overridden via RATE_LIMIT env var (e.g., "200/minute")
DEFAULT_RATE_LIMIT = os.getenv("RATE_LIMIT", "100/minute")

limiter = Limiter(key_func=get_remote_address, default_limits=[DEFAULT_RATE_LIMIT])


def setup_rate_limiting(app):
    """
    Set up rate limiting middleware on FastAPI app.
    
    Usage:
        from app.middleware.rate_limit import setup_rate_limiting, limiter
        
        setup_rate_limiting(app)
        
        @router.get("/endpoint")
        @limiter.limit("10/minute")  # Custom rate for specific endpoint
        async def endpoint(request: Request):
            pass
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
