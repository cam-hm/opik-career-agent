"""
Database configuration and session management.

Uses centralized settings from config package.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config.settings import get_settings

# Get settings
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


async def get_db():
    """
    Dependency for FastAPI endpoints.
    
    Usage:
        @router.get("/")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session
