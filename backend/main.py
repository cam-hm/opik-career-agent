"""
FastAPI application entry point.

Uses centralized config from config package.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controllers import upload, interviews, utils, applications, test_tts, practice, gamification
from app.middleware.rate_limit import setup_rate_limiting
from config.settings import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AI Mock Interviewer API",
    version="1.0.0",
)

# Configure CORS from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
setup_rate_limiting(app)


# Custom exception handler for AppException
from app.services.core.exceptions import AppException

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions with structured response."""
    origin = request.headers.get("origin", "")
    allowed_origins = settings.cors_origins_list
    
    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "detail": exc.detail
        }
    )
    
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response


# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with consistent format and CORS headers."""
    logger.exception(f"Unhandled error on {request.url.path}: {exc}")
    
    origin = request.headers.get("origin", "")
    allowed_origins = settings.cors_origins_list
    
    response = JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )
    
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response


# Include routers
from routes.api import api_router
app.include_router(api_router, prefix="/api/v1")


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint with version info."""
    return {"message": "AI Mock Interviewer API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Basic liveness probe."""
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness_check():
    """
    Readiness probe - checks database connectivity.
    """
    from app.services.core.database import AsyncSessionLocal
    from sqlalchemy import text
    
    checks = {
        "database": "unknown",
        "status": "ok"
    }
    
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
            checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        checks["status"] = "degraded"
        logger.error(f"Readiness check failed - DB: {e}")
    
    return checks
