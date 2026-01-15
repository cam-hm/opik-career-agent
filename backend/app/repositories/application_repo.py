"""
Application Repository.

Data access layer for InterviewApplication model.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.interview import InterviewApplication


class ApplicationRepository:
    """
    Repository for InterviewApplication data access.
    
    Abstracts database queries from business logic.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(
        self, 
        application_id: str,
        include_sessions: bool = False
    ) -> Optional[InterviewApplication]:
        """
        Get an application by ID.
        
        Args:
            application_id: Application UUID
            include_sessions: Whether to eager-load sessions
            
        Returns:
            InterviewApplication or None
        """
        stmt = select(InterviewApplication).where(
            InterviewApplication.id == application_id
        )
        
        if include_sessions:
            stmt = stmt.options(selectinload(InterviewApplication.sessions))
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id_and_user(
        self,
        application_id: str,
        user_id: str,
        include_sessions: bool = False
    ) -> Optional[InterviewApplication]:
        """
        Get an application by ID, verified by user ownership.
        
        Args:
            application_id: Application UUID
            user_id: Clerk user ID
            include_sessions: Whether to eager-load sessions
            
        Returns:
            InterviewApplication or None
        """
        stmt = select(InterviewApplication).where(
            InterviewApplication.id == application_id,
            InterviewApplication.user_id == user_id
        )
        
        if include_sessions:
            stmt = stmt.options(selectinload(InterviewApplication.sessions))
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_applications(
        self, 
        user_id: str,
        include_sessions: bool = False
    ) -> list[InterviewApplication]:
        """
        Get all applications for a user.
        
        Args:
            user_id: Clerk user ID
            include_sessions: Whether to eager-load sessions
            
        Returns:
            List of InterviewApplication
        """
        stmt = select(InterviewApplication).where(
            InterviewApplication.user_id == user_id
        ).order_by(InterviewApplication.created_at.desc())
        
        if include_sessions:
            stmt = stmt.options(selectinload(InterviewApplication.sessions))
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def create(
        self,
        application_id: str,
        user_id: str,
        job_role: str,
        status: str = "in_progress",
        current_stage: int = 1,
        type: str = "standard",
        resume_text: Optional[str] = None,
        resume_analysis: Optional[dict] = None,
        job_description: Optional[str] = None
    ) -> InterviewApplication:
        """
        Create a new application.
        """
        application = InterviewApplication(
            id=application_id,
            user_id=user_id,
            job_role=job_role,
            status=status,
            current_stage=current_stage,
            type=type,
            resume_text=resume_text,
            resume_analysis=resume_analysis,
            job_description=job_description
        )
        
        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)
        
        return application
    
    async def update_stage(
        self,
        application: InterviewApplication,
        new_stage: int,
        status: Optional[str] = None
    ) -> InterviewApplication:
        """
        Update application stage and optionally status.
        
        Args:
            application: Application to update
            new_stage: New stage number
            status: Optional new status
            
        Returns:
            Updated InterviewApplication
        """
        application.current_stage = new_stage
        if status:
            application.status = status
        
        await self.db.commit()
        await self.db.refresh(application)
        
        return application
