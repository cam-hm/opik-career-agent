"""
Application Service.

Business logic for interview applications.
Uses Repository pattern for data access.
"""
import uuid
from typing import Optional

from app.repositories.application_repo import ApplicationRepository
from config.stages import get_stage_type
from app.services.core.exceptions import ApplicationNotFoundError, ApplicationNotInProgressError
from app.models.interview import InterviewApplication


class ApplicationService:
    """
    Service class for application business logic.
    
    Uses ApplicationRepository for data access.
    """
    
    def __init__(self, repo: ApplicationRepository):
        self.repo = repo
    
    async def create_application(
        self,
        user_id: str,
        job_role: str,
        job_description: Optional[str] = None,
        type: str = "standard",
        resume_text: Optional[str] = None,
        resume_analysis: Optional[dict] = None
    ) -> InterviewApplication:
        """
        Create a new interview application.
        """
        application_id = str(uuid.uuid4())
        return await self.repo.create(
            application_id=application_id,
            user_id=user_id,
            job_role=job_role,
            job_description=job_description,
            type=type,
            resume_text=resume_text,
            resume_analysis=resume_analysis
        )
    
    async def get_application(
        self,
        application_id: str,
        user_id: str,
        include_sessions: bool = False
    ) -> InterviewApplication:
        """
        Get an application by ID, verified by user ownership.
        
        Raises:
            ApplicationNotFoundError: If application not found
        """
        application = await self.repo.get_by_id_and_user(
            application_id, user_id, include_sessions
        )
        if not application:
            raise ApplicationNotFoundError(application_id)
        return application
    
    async def get_user_applications(
        self,
        user_id: str,
        include_sessions: bool = False
    ) -> list[InterviewApplication]:
        """Get all applications for a user."""
        return await self.repo.get_user_applications(user_id, include_sessions)
    
    async def start_stage(
        self,
        application_id: str,
        user_id: str
    ) -> tuple[InterviewApplication, str]:
        """
        Start the current stage of an application.
        
        Returns:
            Tuple of (application, stage_type)
            
        Raises:
            ApplicationNotFoundError: If application not found
            ApplicationNotInProgressError: If application is not in progress
        """
        application = await self.repo.get_by_id_and_user(application_id, user_id)
        
        if not application:
            raise ApplicationNotFoundError(application_id)
        
        if application.status != "in_progress":
            raise ApplicationNotInProgressError(application_id, application.status)
        
        stage_type = get_stage_type(application.current_stage)
        return application, stage_type
    
    async def advance_stage(
        self,
        application_id: str
    ) -> InterviewApplication:
        """
        Advance the application to the next stage.
        
        If on stage 3, marks application as completed.
        
        Raises:
            ApplicationNotFoundError: If application not found
        """
        application = await self.repo.get_by_id(application_id)
        
        if not application:
            raise ApplicationNotFoundError(application_id)
        
        if application.current_stage < 3:
            new_stage = application.current_stage + 1
            return await self.repo.update_stage(application, new_stage)
        else:
            return await self.repo.update_stage(application, 3, status="completed")


# ===== Backward compatibility functions =====
# These wrap the class methods for existing code that uses function calls

async def create_application(
    db, 
    user_id: str, 
    job_role: str, 
    job_description: str = None,
    type: str = "standard",
    resume_text: str = None,
    resume_analysis: dict = None
):
    """Backward compatible function wrapper."""
    repo = ApplicationRepository(db)
    service = ApplicationService(repo)
    return await service.create_application(
        user_id, 
        job_role, 
        job_description,
        type=type,
        resume_text=resume_text,
        resume_analysis=resume_analysis
    )


async def start_stage(db, application_id: str, user_id: str):
    """Backward compatible function wrapper."""
    repo = ApplicationRepository(db)
    service = ApplicationService(repo)
    return await service.start_stage(application_id, user_id)


async def advance_stage(db, application_id: str):
    """Backward compatible function wrapper."""
    repo = ApplicationRepository(db)
    service = ApplicationService(repo)
    return await service.advance_stage(application_id)
