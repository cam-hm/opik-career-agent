"""
Pydantic schemas for Interview endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ===== Request Models =====

class UpdateInterviewRequest(BaseModel):
    """Request to update an interview session."""
    transcript: Optional[str] = None
    status: Optional[str] = None


class GenerateFeedbackRequest(BaseModel):
    """Request to generate feedback (empty body, uses session data)."""
    pass


# ===== Response Models =====

class InterviewSessionResponse(BaseModel):
    """Full interview session response."""
    id: int
    session_id: str
    candidate_name: Optional[str] = None
    job_role: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    application_id: Optional[str] = None
    stage_type: Optional[str] = None
    overall_score: Optional[int] = None
    opik_trace_id: Optional[str] = None

    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
    """AI-generated feedback response."""
    score: int = Field(ge=0, le=100)
    summary: str
    pros: list[str] = []
    cons: list[str] = []
    feedback: str
    opik_trace_id: Optional[str] = None


class LiveKitTokenRequest(BaseModel):
    """Request for LiveKit token."""
    session_id: str
    participant_name: Optional[str] = "Candidate"


class LiveKitTokenResponse(BaseModel):
    """Response with LiveKit token."""
    token: str
    room_name: str
