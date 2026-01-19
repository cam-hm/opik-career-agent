from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.core.database import get_db
from config.settings import get_settings
from app.models.interview import InterviewSession
from livekit import api
from app.services.analysis_service import analyze_resume
from app.middleware.auth import verify_clerk_token, optional_auth
from typing import Optional

settings = get_settings()

router = APIRouter()

@router.post("/interviews/{session_id}/token")
async def get_interview_token(
    session_id: str,
    participant_name: str,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """Generate LiveKit token for interview session. Requires auth."""
    from sqlalchemy.orm import selectinload
    from app.models.interview import InterviewApplication
    
    # Verify session exists and belongs to user
    query = select(InterviewSession).options(
        selectinload(InterviewSession.application)
    ).where(InterviewSession.session_id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.application and session.application.user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    # Create LiveKit Token
    token = api.AccessToken(
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET
    )
    
    token.with_identity(participant_name) \
         .with_name(participant_name) \
         .with_grants(api.VideoGrants(
             room_join=True,
             room=session_id,
         ))
    
    return {"token": token.to_jwt()}

from app.schemas.interviews import InterviewSessionResponse
from typing import List

@router.get("/interviews", response_model=List[InterviewSessionResponse])
async def list_interviews(
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db),
    mode: Optional[str] = Query(None, description="Filter: 'practice' or 'application'")
):
    """
    List user's interview sessions.
    
    Query params:
    - mode=practice: Only practice sessions (stage_type='practice')
    - mode=application: Only application sessions (HR/Technical/Behavioral)
    - No mode: All sessions (backward compatible)
    """
    from sqlalchemy.orm import selectinload
    from app.models.interview import InterviewApplication
    
    query = (
        select(InterviewSession)
        .join(InterviewApplication)
        .options(selectinload(InterviewSession.application))
        .where(InterviewApplication.user_id == auth_user_id)
    )
    
    # Filter by mode at database level
    if mode == "practice":
        query = query.where(InterviewSession.stage_type == "practice")
    elif mode == "application":
        query = query.where(InterviewSession.stage_type != "practice")
    
    query = query.order_by(InterviewSession.created_at.desc())
    result = await db.execute(query)
    sessions = result.scalars().all()
    return sessions

from sqlalchemy import select

@router.get("/interviews/{session_id}", response_model=InterviewSessionResponse)
async def get_interview_session(
    session_id: str,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """Get interview session details. Requires auth and ownership."""
    from sqlalchemy.orm import selectinload
    query = select(InterviewSession).options(
        selectinload(InterviewSession.application)
    ).where(InterviewSession.session_id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.application and session.application.user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
        
    return session

@router.post("/interviews/{session_id}/analyze")
async def analyze_interview_cv(
    session_id: str,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """Analyze resume for interview session. Requires auth and ownership."""
    # 1. Get session with application
    from sqlalchemy.orm import selectinload
    from app.models.interview import InterviewApplication
    
    query = select(InterviewSession).options(
        selectinload(InterviewSession.application)
    ).where(InterviewSession.session_id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session or not session.application:
        raise HTTPException(status_code=404, detail="Session or linked Application not found")
    if session.application.user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    application = session.application
    
    # 2. Check Cache
    if application.resume_analysis:
        return application.resume_analysis
        
    if not application.resume_text:
        raise HTTPException(status_code=400, detail="No resume text found for this application")

    # 3. Analyze (Fallback if not cached)
    # This might happen for old data or if analysis failed previously
    analysis = await analyze_resume(application.resume_text, application.job_description)
    
    # 4. Save to Cache
    from sqlalchemy import update
    stmt = (
        update(InterviewApplication)
        .where(InterviewApplication.id == application.id)
        .values(resume_analysis=analysis)
    )
    await db.execute(stmt)
    await db.commit()
    
    return analysis

import json
from app.services.analysis_service import generate_feedback

@router.post("/interviews/{session_id}/feedback")
async def generate_interview_feedback(
    session_id: str,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """Generate feedback for interview session. Requires auth."""
    from sqlalchemy.orm import selectinload
    
    # 1. Get session with application for ownership check
    query = select(InterviewSession).options(
        selectinload(InterviewSession.application)
    ).where(InterviewSession.session_id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.application and session.application.user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    # 2. Check if feedback already exists
    if session.feedback_markdown:
        try:
            cached_feedback = json.loads(session.feedback_markdown)
            # Attach observability data for frontend display
            if session.opik_trace_id:
                cached_feedback["opik_trace_id"] = session.opik_trace_id
            if session.competency_scores:
                cached_feedback["competency_scores"] = session.competency_scores
            if session.skill_assessments:
                cached_feedback["skill_assessments"] = session.skill_assessments
            return cached_feedback
        except json.JSONDecodeError:
            # If it's not valid JSON (maybe legacy text), regenerate
            pass

    # 3. Handle empty/no transcript gracefully
    if not session.transcript or session.transcript == "[]":
        # No transcript - return default empty feedback
        empty_feedback = {
            "score": 0,
            "summary": "Interview session ended without any conversation recorded.",
            "pros": [],
            "cons": ["No responses were recorded during the interview."],
            "detailed_feedback": "The interview session was terminated before any meaningful conversation took place. Please try again and ensure your microphone is working properly."
        }
        
        # Save to DB
        session.transcript = "[]"
        session.feedback_markdown = json.dumps(empty_feedback)
        session.status = "completed"
        session.overall_score = 0
        await db.commit()
        
        return empty_feedback

    # 4. Generate Feedback from transcript
    transcript_list = json.loads(session.transcript)
    
    # Extra check: if transcript_list is empty after parsing
    if not transcript_list:
        empty_feedback = {
            "score": 0,
            "summary": "Interview session ended without any conversation recorded.",
            "pros": [],
            "cons": ["No responses were recorded during the interview."],
            "detailed_feedback": "The interview session was terminated before any meaningful conversation took place."
        }
        session.feedback_markdown = json.dumps(empty_feedback)
        session.status = "completed"
        session.overall_score = 0
        await db.commit()
        return empty_feedback
    
    feedback = await generate_feedback(
        transcript_list,
        resume_text=session.resume_text,
        job_description=session.job_description,
        session_id=session_id
    )
    
    # 5. Save to DB
    # 5. Save to DB and Trigger Gamification
    from app.repositories.session_repo import SessionRepository
    from app.services.interview_service import InterviewService
    
    session_repo = SessionRepository(db)
    interview_service = InterviewService(session_repo)
    
    # Serialize feedback
    feedback_str = json.dumps(feedback)
    overall_score = feedback.get("score", 0) if isinstance(feedback, dict) else 0
    
    result = await interview_service.update_feedback(session.session_id, feedback_str, overall_score)
    
    # If there are rewards, we could attach them to the response or just log them
    # For now, just return feedback logic as before, but maybe inject 'rewards' key if needed?
    # The frontend expects the feedback object directly.
    # Let's attach rewards to the feedback object if it's a dict
    if result.get("rewards") and isinstance(feedback, dict):
        feedback["gamification_rewards"] = result["rewards"]

    # Attach observability data for frontend display
    if isinstance(feedback, dict):
        if session.opik_trace_id:
            feedback["opik_trace_id"] = session.opik_trace_id
        if session.competency_scores:
            feedback["competency_scores"] = session.competency_scores
        if session.skill_assessments:
            feedback["skill_assessments"] = session.skill_assessments

    return feedback
