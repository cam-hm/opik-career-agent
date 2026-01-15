"""
Dependency Injection Container.

Provides FastAPI dependencies for services, repositories, and other components.
"""
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.core.database import AsyncSessionLocal, get_db  # Re-export get_db for convenience
from app.repositories.application_repo import ApplicationRepository
from app.repositories.session_repo import SessionRepository


# ===== Database Session =====
# Note: get_db is imported from app.services.core.database for consistency with existing API imports.
# Use either `from app.services.core.database import get_db` or `from app.services.core.dependencies import get_db`.


# ===== Repositories =====

async def get_application_repo(
    db: AsyncSession = Depends(get_db)
) -> ApplicationRepository:
    """
    Get ApplicationRepository instance.
    
    Usage:
        @router.get("/applications")
        async def list_apps(repo: ApplicationRepository = Depends(get_application_repo)):
            return await repo.get_user_applications(user_id)
    """
    return ApplicationRepository(db)


async def get_session_repo(
    db: AsyncSession = Depends(get_db)
) -> SessionRepository:
    """
    Get SessionRepository instance.
    
    Usage:
        @router.get("/sessions/{session_id}")
        async def get_session(
            session_id: str,
            repo: SessionRepository = Depends(get_session_repo)
        ):
            return await repo.get_by_session_id(session_id)
    """
    return SessionRepository(db)


# ===== Combined Dependencies =====

class UnitOfWork:
    """
    Unit of Work pattern for managing multiple repositories.
    
    Ensures all operations use the same database session.
    """
    
    def __init__(
        self,
        db: AsyncSession,
        applications: ApplicationRepository,
        sessions: SessionRepository
    ):
        self.db = db
        self.applications = applications
        self.sessions = sessions
    
    async def commit(self):
        """Commit all pending changes."""
        await self.db.commit()
    
    async def rollback(self):
        """Rollback all pending changes."""
        await self.db.rollback()


async def get_unit_of_work(
    db: AsyncSession = Depends(get_db)
) -> UnitOfWork:
    """
    Get UnitOfWork instance with all repositories.
    
    Usage:
        @router.post("/complex-operation")
        async def complex_operation(uow: UnitOfWork = Depends(get_unit_of_work)):
            app = await uow.applications.get_by_id(app_id)
            session = await uow.sessions.create(...)
            await uow.commit()
    """
    return UnitOfWork(
        db=db,
        applications=ApplicationRepository(db),
        sessions=SessionRepository(db)
    )
