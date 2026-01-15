"""Schemas package initialization."""
from app.schemas.applications import (
    CreateApplicationRequest,
    CreateApplicationResponse,
    ApplicationResponse,
    SessionSummary,
    StartStageResponse,
    CompleteStageResponse,
    ProceedToNextStageResponse,
)
from app.schemas.interviews import (
    UpdateInterviewRequest,
    FeedbackResponse,
    InterviewSessionResponse,
    LiveKitTokenRequest,
    LiveKitTokenResponse,
)
from app.schemas.common import (
    ErrorResponse,
    SuccessResponse,
    HealthResponse,
    ResumeAnalysisResponse,
)

__all__ = [
    # Applications
    "CreateApplicationRequest",
    "CreateApplicationResponse",
    "ApplicationResponse",
    "SessionSummary",
    "StartStageResponse",
    "CompleteStageResponse",
    "ProceedToNextStageResponse",
    # Interviews
    "UpdateInterviewRequest",
    "FeedbackResponse",
    "InterviewSessionResponse",
    "LiveKitTokenRequest",
    "LiveKitTokenResponse",
    # Common
    "ErrorResponse",
    "SuccessResponse",
    "HealthResponse",
    "ResumeAnalysisResponse",
]
