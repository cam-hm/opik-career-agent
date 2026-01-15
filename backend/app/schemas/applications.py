"""
Pydantic schemas for Application endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ===== Request Models =====

class CreateApplicationRequest(BaseModel):
    """Request model for creating a new application."""
    job_role: str = Field(..., min_length=2, max_length=100, examples=["Senior Python Developer"])
    job_description: Optional[str] = Field(default=None, max_length=10000)


# ===== Response Models =====

class ApplicationBase(BaseModel):
    """Base application fields."""
    id: str
    job_role: str
    status: str
    current_stage: int


class SessionSummary(BaseModel):
    """Summary of an interview session."""
    id: int
    session_id: str
    stage_type: Optional[str] = None
    status: str
    overall_score: Optional[int] = None
    
    class Config:
        from_attributes = True


class ApplicationResponse(ApplicationBase):
    """Full application response with sessions."""
    sessions: list[SessionSummary] = []
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreateApplicationResponse(BaseModel):
    """Response after creating an application."""
    application_id: str
    session_id: str
    stage_type: str
    current_stage: int


class StartStageResponse(BaseModel):
    """Response after starting a stage."""
    application_id: str
    session_id: str
    stage_type: str


class CompleteStageResponse(BaseModel):
    """Response after completing a stage."""
    success: bool
    application_id: str
    current_stage: int
    status: str
    message: str


class ProceedToNextStageResponse(BaseModel):
    """Response after proceeding to next stage."""
    completed: bool
    application_id: str
    session_id: Optional[str] = None
    stage_type: Optional[str] = None
    current_stage: Optional[int] = None
    message: Optional[str] = None
