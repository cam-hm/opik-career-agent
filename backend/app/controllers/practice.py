from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.core.database import get_db
from app.models.interview import InterviewSession
from app.services.cv_service import parse_resume
from app.services.analysis_service import generate_job_description
from app.middleware.auth import verify_clerk_token
import uuid
from typing import Optional

router = APIRouter()

# File upload limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf"}
ALLOWED_CONTENT_TYPES = {"application/pdf"}

@router.post("/practice")
async def start_practice_session(
    job_role: str = Form(...),
    file: Optional[UploadFile] = File(None),  # CV is optional
    job_description: Optional[str] = Form(None),
    language: Optional[str] = Form("en"),  # Default to English
    node_id: Optional[str] = Form(None), # Gamification Node
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a standalone Practice Session.

    This is distinct from the full 3-stage application process.
    It creates a single session with stage_type='practice' (Technical focus).
    """
    # 1. Parse PDF if provided
    resume_text = None
    if file and file.filename:
        # Validate file extension
        import os
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Only PDF files are allowed."
            )
        
        # Validate content type
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type. Only PDF files are allowed."
            )
        
        # Validate file size (read content to check)
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is 10MB."
            )
        
        # Reset file position for parsing
        await file.seek(0)
        
        try:
            resume_text = await parse_resume(file)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid PDF: {str(e)}")

    # 2. Handle JD - generate if not provided
    # 2. Handle JD - generate if not provided
    final_jd = job_description
    if not final_jd and job_role:
        final_jd = await generate_job_description(job_role, language)

    # 3. Resume Analysis (Once per "Practice App")
    from app.services.analysis_service import analyze_resume
    resume_analysis = None
    if resume_text:
        resume_analysis = await analyze_resume(resume_text, final_jd)

    # 4. Create "Practice Application" wrapper
    from app.services.application_service import create_application
    
    # We create a hidden application wrapper for this practice session
    # This keeps our schema unified (Session always has Parent App)
    practice_app = await create_application(
        db, 
        auth_user_id, 
        job_role, 
        final_jd, 
        resume_text=resume_text, 
        resume_analysis=resume_analysis,
        type="practice" # Special type
    )

    # 5. Create Session Linked to Practice App
    from app.services.interview_service import create_interview_session

    new_session = await create_interview_session(
        db=db,
        user_id=auth_user_id,
        application_id=practice_app.id,
        stage_type="practice", # Technical Practice Persona
        language=language,
        node_id=node_id
    )

    return {
        "session_id": new_session.session_id,
        "application_id": practice_app.id,
        "has_resume": resume_text is not None,
        "mode": "practice",
        "resume_preview": (resume_text[:200] + "...") if resume_text else None,
        "job_description_preview": (final_jd[:100] + "...") if final_jd else None
    }
