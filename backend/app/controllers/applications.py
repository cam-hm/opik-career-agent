from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.core.database import get_db
from app.services.application_service import create_application, start_stage, advance_stage
from app.services.cv_service import parse_resume
from app.services.analysis_service import generate_job_description
from app.models.interview import InterviewSession
from app.middleware.auth import verify_clerk_token
from config.stages import get_stage_type
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/applications")
async def create_new_application(
    job_role: str = Form(...),
    file: Optional[UploadFile] = File(None),  # CV is now optional
    job_description: Optional[str] = Form(None),
    language: str = Form("en"),
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new 3-stage interview application.
    """
    # 1. Parse PDF if provided
    resume_text = None
    if file and file.filename:
        try:
            resume_text = await parse_resume(file)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid PDF: {str(e)}")

    # 2. Handle JD - generate if not provided
    final_jd = job_description
    if not final_jd and job_role:
        final_jd = await generate_job_description(job_role, language)

    # 3. Resume Analysis (Once per application)
    from app.services.analysis_service import analyze_resume
    resume_analysis = None
    if resume_text:
        resume_analysis = await analyze_resume(resume_text, final_jd)

    # 4. Create Application (Context)
    application = await create_application(
        db, 
        auth_user_id, 
        job_role, 
        final_jd, 
        resume_text=resume_text, 
        resume_analysis=resume_analysis,
        type="standard"
    )

    # 5. Start Stage 1 automatically
    from app.services.interview_service import create_interview_session

    # Session no longer needs resume/JD context (it's in application)
    new_session = await create_interview_session(
        db=db,
        user_id=auth_user_id,
        application_id=application.id,
        stage_type="hr",
        language=language
    )

    return {
        "application_id": application.id,
        "current_stage": application.current_stage,
        "session_id": new_session.session_id,
        "stage_type": "hr",
        "has_resume": resume_text is not None
    }

from pydantic import BaseModel

class StartStageRequest(BaseModel):
    user_id: str

@router.post("/applications/{application_id}/start_stage")
async def start_next_stage(
    application_id: str,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    try:
        from sqlalchemy import select
        from app.models.interview import InterviewApplication
        from config.stages import get_stage_type
        
        # First, get the application
        stmt = select(InterviewApplication).where(
            InterviewApplication.id == application_id,
            InterviewApplication.user_id == auth_user_id
        )
        result = await db.execute(stmt)
        application = result.scalar_one_or_none()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
            
        if application.status != "in_progress":
            raise HTTPException(status_code=400, detail="Application is not in progress")
        
        stage_type = get_stage_type(application.current_stage)
        
        # Check if there's an existing pending session for this stage
        stmt = select(InterviewSession).where(
            InterviewSession.application_id == application_id,
            InterviewSession.stage_type == stage_type,
            InterviewSession.status == "pending"
        )
        result = await db.execute(stmt)
        existing_session = result.scalar_one_or_none()
        
        if existing_session:
            # Reuse existing pending session
            return {
                "application_id": application.id,
                "session_id": existing_session.session_id,
                "stage_type": stage_type
            }
        
        # No existing session, need to fetch context from previous session
        stmt = select(InterviewSession).where(
            InterviewSession.application_id == application_id
        ).order_by(InterviewSession.created_at.desc())
        result = await db.execute(stmt)
        last_session = result.scalars().first()
        
        if not last_session:
            raise HTTPException(status_code=404, detail="No previous session found for context")

        # Create new session
        from app.services.interview_service import create_interview_session
        
        new_session = await create_interview_session(
            db=db,
            user_id=auth_user_id,
            application_id=application.id,
            stage_type=stage_type,
            language=last_session.language or "en"
        )
        
        return {
            "application_id": application.id,
            "session_id": new_session.session_id,
            "stage_type": stage_type
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/applications/{application_id}")
async def get_application(
    application_id: str,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.interview import InterviewApplication
    
    stmt = select(InterviewApplication).options(selectinload(InterviewApplication.sessions)).where(InterviewApplication.id == application_id)
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    return application

@router.get("/applications")
async def list_applications(
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = None
):
    """
    List user's full applications (3-stage process).
    Practice sessions are excluded - use /interviews?mode=practice for those.
    
    Query params:
    - status: Filter by status ('in_progress', 'completed')
    """
    from sqlalchemy import select
    from app.models.interview import InterviewApplication
    
    # User can only see their own applications, exclude practice type
    query = select(InterviewApplication).where(
        InterviewApplication.user_id == auth_user_id,
        InterviewApplication.type != "practice"  # Exclude practice wrappers
    )
    
    # Filter by status at database level
    if status == "in_progress":
        query = query.where(InterviewApplication.status != "completed")
    elif status == "completed":
        query = query.where(InterviewApplication.status == "completed")
    
    query = query.order_by(InterviewApplication.created_at.desc())
    result = await db.execute(query)
    applications = result.scalars().all()
    
    return applications

@router.post("/applications/{application_id}/skip_stage")
async def skip_stage_endpoint(
    application_id: str,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Reuse start_stage logic but don't create a session, just advance
        # Actually, we need a specific service method for this to just increment the stage
        from app.services.application_service import advance_stage
        
        application = await advance_stage(db, application_id)
        return application
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/applications/{application_id}/complete_stage")
async def complete_stage_endpoint(
    application_id: str,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete the current stage and advance to the next one.
    Similar to skip_stage but with 'completed' semantics.
    """
    try:
        from app.services.application_service import advance_stage
        
        application = await advance_stage(db, application_id)
        return {
            "success": True,
            "application_id": application.id,
            "current_stage": application.current_stage,
            "status": application.status,
            "message": "Stage completed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/applications/{application_id}/proceed_to_next_stage")
async def proceed_to_next_stage_endpoint(
    application_id: str,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete current stage, advance to next stage, and start the interview.
    This is used from the feedback page "Proceed to Next Stage" button.
    """
    try:
        from sqlalchemy import select
        from app.models.interview import InterviewApplication
        from app.services.application_service import advance_stage
        from config.stages import get_stage_type
        from app.services.interview_service import create_interview_session
        
        # First advance to next stage
        application = await advance_stage(db, application_id)
        
        # Check if application is completed (all stages done)
        if application.status == "completed":
            return {
                "completed": True,
                "application_id": application.id,
                "message": "All stages completed!"
            }
        
        # Get the new stage type
        stage_type = get_stage_type(application.current_stage)
        
        # Fetch context from previous sessions
        stmt = select(InterviewSession).where(
            InterviewSession.application_id == application_id
        ).order_by(InterviewSession.created_at.desc())
        result = await db.execute(stmt)
        last_session = result.scalars().first()
        
        if not last_session:
            raise HTTPException(status_code=404, detail="No previous session found for context")
        
        # Create new session
        from app.services.interview_service import create_interview_session
        
        new_session = await create_interview_session(
            db=db,
            user_id=auth_user_id,
            application_id=application.id,
            stage_type=stage_type,
            # We fetch language from previous session to persist preference, or default to 'en'
            language=last_session.language or "en"
        )
        
        return {
            "completed": False,
            "application_id": application.id,
            "session_id": new_session.session_id,
            "stage_type": stage_type,
            "current_stage": application.current_stage
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

