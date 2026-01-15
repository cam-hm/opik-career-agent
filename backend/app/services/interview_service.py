"""
Interview Service.

Business logic for interview sessions.
Uses Repository pattern for data access.
"""
import uuid
from typing import Optional

from app.repositories.session_repo import SessionRepository
from app.models.interview import InterviewSession


class InterviewService:
    """
    Service class for interview session business logic.
    
    Uses SessionRepository for data access.
    """
    
    def __init__(self, repo: SessionRepository):
        self.repo = repo
    
    async def create_session(
        self,
        application_id: str,
        stage_type: str,
        user_id: Optional[str] = None,
        language: Optional[str] = "en",
        node_id: Optional[str] = None
    ) -> InterviewSession:
        """
        Create a new interview session.
        """
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        return await self.repo.create(
            session_id=session_id,
            application_id=application_id,
            stage_type=stage_type,
            user_id=user_id,
            language=language,
            node_id=node_id
        )
    
    async def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get session by ID."""
        return await self.repo.get_by_session_id(session_id)
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 50
    ) -> list[InterviewSession]:
        """Get all sessions for a user."""
        return await self.repo.get_user_sessions(user_id, limit)
    
    async def update_transcript(
        self,
        session_id: str,
        transcript: str
    ) -> bool:
        """Update session transcript."""
        return await self.repo.update_transcript(session_id, transcript)
    
    async def update_feedback(
        self,
        session_id: str,
        feedback_markdown: str,
        overall_score: int
    ) -> dict:
        """
        Update session with generated feedback and Trigger Gamification.
        
        Returns:
             dict with status and potential gamification rewards
        """
        # 1. Update DB (Status -> Completed)
        updated = await self.repo.update_feedback(session_id, feedback_markdown, overall_score)
        
        if not updated:
            return {"status": "error", "message": "Session not found"}
            
        # 2. Trigger Gamification
        # 2. Trigger Gamification
        rewards = None
        session = await self.repo.get_by_session_id(session_id)
        # Note: Must access user_id via linked Application
        if session and session.node_id and session.application and session.application.user_id:
            try:
                from app.services.core.gamification.gamification_service import gamification_service
                import json
                
                # Parse metrics from feedback if possible (assuming feedback_markdown is JSON string for now, based on legacy usage)
                metrics = {}
                try:
                    data = json.loads(feedback_markdown)
                    if isinstance(data, dict):
                        # Extract metrics if they exist in the feedback structure
                        # Expected: { "detailed_feedback": { "communication": 80 ... } } or similar
                        # For MVP just map overall_score to all temporarily or use default
                        pass
                except:
                    pass
                
                rewards = await gamification_service.complete_node(
                    db=self.repo.db,
                    user_id=session.application.user_id,
                    node_id=session.node_id,
                    score=overall_score,
                    metrics=metrics
                )
                
            except Exception as e:
                # Don't fail the feedback save if gamification crashes
                print(f"Gamification Error: {e}")
                
        return {"status": "success", "rewards": rewards}


# ===== Backward compatibility function =====

async def create_interview_session(
    db,
    resume_text: str = None,
    job_role: str = None,
    job_description: str = None,
    user_id: str = None,
    application_id: str = None,
    stage_type: str = None,
    language: str = "en",
    node_id: str = None
) -> InterviewSession:
    """Backward compatible function wrapper."""
    repo = SessionRepository(db)
    service = InterviewService(repo)
    # Note: resume_text and job_role are ignored by new service 
    # as they are now stored in the Application linked by application_id
    return await service.create_session(
        application_id=application_id,
        stage_type=stage_type,
        user_id=user_id,
        language=language,
        node_id=node_id
    )
