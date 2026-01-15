"""
Common/shared Pydantic schemas.
"""
from typing import Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    message: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    """Standard success response format."""
    success: bool = True
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: Optional[str] = None
    version: str = "1.0.0"


class ResumeAnalysisResponse(BaseModel):
    """Response from resume analysis."""
    summary: str
    strengths: list[str] = []
    weaknesses: list[str] = []
    suggested_questions: list[str] = []
    overall_score: int
