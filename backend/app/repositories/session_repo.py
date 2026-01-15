"""
Session Repository.

Data access layer for InterviewSession model.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.interview import InterviewSession


class SessionRepository:
    """
    Repository for InterviewSession data access.
    
    Abstracts database queries from business logic.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_session_id(
        self, 
        session_id: str
    ) -> Optional[InterviewSession]:
        """
        Get a session by its UUID.
        
        Args:
            session_id: Session UUID (also LiveKit room name)
            
        Returns:
            InterviewSession or None
        """
        from sqlalchemy.orm import selectinload
        stmt = select(InterviewSession).options(
            selectinload(InterviewSession.application)
        ).where(
            InterviewSession.session_id == session_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_sessions(
        self, 
        user_id: str,
        limit: int = 50
    ) -> list[InterviewSession]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: Clerk user ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of InterviewSession
        """
        from app.models.interview import InterviewApplication
        from sqlalchemy.orm import selectinload
        
        stmt = (
            select(InterviewSession)
            .join(InterviewApplication)
            .options(selectinload(InterviewSession.application))
            .where(InterviewApplication.user_id == user_id)
            .order_by(InterviewSession.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_application_sessions(
        self,
        application_id: str
    ) -> list[InterviewSession]:
        """
        Get all sessions for an application.
        
        Args:
            application_id: Application UUID
            
        Returns:
            List of InterviewSession ordered by creation time
        """
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.application_id == application_id)
            .order_by(InterviewSession.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_pending_session_for_stage(
        self,
        application_id: str,
        stage_type: str
    ) -> Optional[InterviewSession]:
        """
        Get existing pending session for a stage.
        
        Args:
            application_id: Application UUID
            stage_type: hr, technical, or behavioral
            
        Returns:
            InterviewSession or None
        """
        stmt = select(InterviewSession).where(
            InterviewSession.application_id == application_id,
            InterviewSession.stage_type == stage_type,
            InterviewSession.status == "pending"
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        session_id: str,
        application_id: str,
        stage_type: str,
        user_id: Optional[str] = None,
        status: str = "pending",
        language: str = "en",
        node_id: Optional[str] = None
    ) -> InterviewSession:
        """
        Create a new interview session.
        """
        session = InterviewSession(
            session_id=session_id,
            application_id=application_id,
            stage_type=stage_type,
            # user_id is now on Application model
            status=status,
            language=language,
            node_id=node_id
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def update_transcript(
        self,
        session_id: str,
        transcript: str,
        status: str = "active"
    ) -> bool:
        """
        Update session transcript and status.
        
        Args:
            session_id: Session UUID
            transcript: JSON string of transcript
            status: New status
            
        Returns:
            True if updated, False if not found
        """
        stmt = (
            update(InterviewSession)
            .where(InterviewSession.session_id == session_id)
            .values(transcript=transcript, status=status)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def update_feedback(
        self,
        session_id: str,
        feedback_markdown: str,
        overall_score: int
    ) -> bool:
        """
        Update session with generated feedback.
        
        Args:
            session_id: Session UUID
            feedback_markdown: Markdown feedback
            overall_score: Score 0-100
            
        Returns:
            True if updated, False if not found
        """
        stmt = (
            update(InterviewSession)
            .where(InterviewSession.session_id == session_id)
            .values(
                feedback_markdown=feedback_markdown,
                overall_score=overall_score,
                status="completed"
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
