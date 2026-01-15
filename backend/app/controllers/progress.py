"""
Progress Controller - Personal Growth & Learning APIs.

Endpoints for:
- Resolution tracking (2026 career goals)
- Skill gap analysis
- Weekly insights
- Progress history
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from uuid import UUID

from app.services.core.database import get_db
from app.middleware.auth import verify_clerk_token
from app.services.progress_service import ProgressService

router = APIRouter()


# ==================== SCHEMAS ====================

class CreateResolutionRequest(BaseModel):
    """Request to create a new resolution."""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    target_role: Optional[str] = None
    target_skills: Optional[Dict[str, int]] = None
    target_date: Optional[datetime] = None


class UpdateResolutionRequest(BaseModel):
    """Request to update a resolution."""
    title: Optional[str] = None
    description: Optional[str] = None
    target_role: Optional[str] = None
    target_skills: Optional[Dict[str, int]] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = None


class ResolutionResponse(BaseModel):
    """Resolution response model."""
    id: UUID
    user_id: str
    title: str
    description: Optional[str]
    target_role: Optional[str]
    target_skills: Dict[str, int]
    baseline_skills: Dict[str, int]
    target_date: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== RESOLUTION ENDPOINTS ====================

@router.post("/progress/resolutions", response_model=ResolutionResponse)
async def create_resolution(
    request: CreateResolutionRequest,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new 2026 career resolution.
    Automatically captures current skill levels as baseline.
    """
    service = ProgressService(db)

    resolution = await service.create_resolution(
        user_id=auth_user_id,
        title=request.title,
        description=request.description,
        target_role=request.target_role,
        target_skills=request.target_skills,
        target_date=request.target_date
    )

    return resolution


@router.get("/progress/resolutions")
async def list_resolutions(
    status: Optional[str] = Query(None, description="Filter by status: active, completed, abandoned"),
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """Get all resolutions for the authenticated user."""
    service = ProgressService(db)
    resolutions = await service.get_user_resolutions(auth_user_id, status=status)

    return {
        "resolutions": [
            {
                "id": str(r.id),
                "title": r.title,
                "description": r.description,
                "target_role": r.target_role,
                "target_skills": r.target_skills,
                "baseline_skills": r.baseline_skills,
                "target_date": r.target_date.isoformat() if r.target_date else None,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in resolutions
        ],
        "count": len(resolutions)
    }


@router.get("/progress/resolutions/{resolution_id}")
async def get_resolution(
    resolution_id: UUID,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific resolution with progress calculation."""
    service = ProgressService(db)

    resolution = await service.get_resolution(resolution_id, auth_user_id)
    if not resolution:
        raise HTTPException(status_code=404, detail="Resolution not found")

    progress = await service.get_resolution_progress(resolution_id, auth_user_id)

    return {
        "resolution": {
            "id": str(resolution.id),
            "title": resolution.title,
            "description": resolution.description,
            "target_role": resolution.target_role,
            "target_skills": resolution.target_skills,
            "baseline_skills": resolution.baseline_skills,
            "target_date": resolution.target_date.isoformat() if resolution.target_date else None,
            "status": resolution.status,
            "created_at": resolution.created_at.isoformat() if resolution.created_at else None
        },
        "progress": progress
    }


@router.patch("/progress/resolutions/{resolution_id}")
async def update_resolution(
    resolution_id: UUID,
    request: UpdateResolutionRequest,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """Update a resolution."""
    service = ProgressService(db)

    updates = request.model_dump(exclude_unset=True)
    resolution = await service.update_resolution(resolution_id, auth_user_id, **updates)

    if not resolution:
        raise HTTPException(status_code=404, detail="Resolution not found")

    return {
        "id": str(resolution.id),
        "title": resolution.title,
        "status": resolution.status,
        "message": "Resolution updated successfully"
    }


@router.post("/progress/resolutions/{resolution_id}/complete")
async def complete_resolution(
    resolution_id: UUID,
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """Mark a resolution as completed."""
    service = ProgressService(db)

    resolution = await service.complete_resolution(resolution_id, auth_user_id)

    if not resolution:
        raise HTTPException(status_code=404, detail="Resolution not found")

    return {
        "id": str(resolution.id),
        "title": resolution.title,
        "status": resolution.status,
        "completed_at": resolution.completed_at.isoformat(),
        "message": "Congratulations! Resolution completed!"
    }


# ==================== SKILL GAP ANALYSIS ====================

@router.get("/progress/skill-gap")
async def get_skill_gap_analysis(
    target_role: Optional[str] = Query(None, description="Target role for comparison"),
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze skill gaps between current levels and target requirements.
    Uses data from interview sessions and competency scores.
    """
    service = ProgressService(db)

    analysis = await service.get_skill_gap_analysis(auth_user_id, target_role)

    return analysis


# ==================== WEEKLY INSIGHTS ====================

@router.get("/progress/insights/weekly")
async def get_weekly_insights(
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI-powered weekly insights based on recent interview performance.
    Includes recommendations, strengths, and areas to improve.
    """
    service = ProgressService(db)

    insights = await service.generate_weekly_insights(auth_user_id)

    return insights


# ==================== PROGRESS HISTORY ====================

@router.get("/progress/history")
async def get_progress_history(
    weeks: int = Query(12, ge=1, le=52, description="Number of weeks of history"),
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical skill snapshots for trend visualization.
    Returns weekly snapshots showing skill progression over time.
    """
    service = ProgressService(db)

    history = await service.get_skill_history(auth_user_id, weeks=weeks)

    return {
        "user_id": auth_user_id,
        "weeks_requested": weeks,
        "snapshots": history,
        "count": len(history)
    }


# ==================== COMPREHENSIVE DASHBOARD ====================

@router.get("/progress/dashboard")
async def get_progress_dashboard(
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive progress dashboard data.
    Combines resolutions, skill gaps, and weekly insights.
    """
    service = ProgressService(db)

    # Get all data in parallel concept (sequential for now)
    resolutions = await service.get_user_resolutions(auth_user_id, status="active")
    skill_gap = await service.get_skill_gap_analysis(auth_user_id)
    weekly_insights = await service.generate_weekly_insights(auth_user_id)
    history = await service.get_skill_history(auth_user_id, weeks=8)

    # Get resolution progress for active resolutions
    resolution_progress = []
    for r in resolutions[:3]:  # Limit to top 3
        progress = await service.get_resolution_progress(r.id, auth_user_id)
        if progress:
            resolution_progress.append(progress)

    return {
        "user_id": auth_user_id,
        "active_resolutions": resolution_progress,
        "skill_gap_summary": {
            "gaps_count": len(skill_gap.get("gaps", [])),
            "top_gaps": skill_gap.get("gaps", [])[:3],
            "strengths_count": len(skill_gap.get("strengths", [])),
            "recommendations": skill_gap.get("recommendations", [])[:3]
        },
        "weekly_summary": {
            "sessions_count": weekly_insights.get("sessions_count", 0),
            "average_score": weekly_insights.get("average_score"),
            "trend_direction": weekly_insights.get("trend_direction"),
            "highlights": weekly_insights.get("highlights", [])
        },
        "skill_history": history[-8:],  # Last 8 weeks
        "generated_at": datetime.utcnow().isoformat()
    }
