"""
Clerk JWT Authentication Middleware for FastAPI.

Uses centralized config from config package.
"""
import jwt
import httpx
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timedelta
import logging

from config.settings import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Security scheme
security = HTTPBearer(auto_error=False)

# Cache for JWKS keys with TTL
_jwks_cache: Optional[dict] = None
_jwks_cache_time: Optional[datetime] = None
JWKS_TTL = timedelta(hours=1)  # Refresh keys every hour


async def get_jwks() -> dict:
    """Fetch JWKS from Clerk (cached with TTL)."""
    global _jwks_cache, _jwks_cache_time
    
    now = datetime.now()
    cache_expired = _jwks_cache_time is None or (now - _jwks_cache_time) > JWKS_TTL
    
    if _jwks_cache is None or cache_expired:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.clerk_jwks_url)
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_cache_time = now
            logger.debug("JWKS cache refreshed")
    
    return _jwks_cache


def get_public_key(token: str, jwks: dict) -> str:
    """Get the public key from JWKS for the given token."""
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        
        raise HTTPException(status_code=401, detail="Public key not found")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token format")


async def verify_clerk_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency to verify Clerk JWT token and return user_id.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user_id: str = Depends(verify_clerk_token)):
            return {"user_id": user_id}
    """
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    
    try:
        jwks = await get_jwks()
        public_key = get_public_key(token, jwks)
        
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER,
            options={"verify_aud": False}
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=401, detail="Invalid token issuer")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        raise HTTPException(status_code=503, detail="Authentication service unavailable")


async def optional_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[str]:
    """
    Optional authentication - returns user_id if valid token, None otherwise.
    """
    if credentials is None:
        return None
    
    try:
        return await verify_clerk_token(credentials)
    except HTTPException:
        return None
