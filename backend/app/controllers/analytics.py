"""
Analytics Controller - AI Observability & Performance APIs.

Endpoints for:
- Overview metrics (total sessions, avg score, Opik coverage)
- Evaluation metrics (score breakdown, competency analysis)
- Component metrics (LLM performance, component usage)

Powers the /analytics dashboard for "Best Use of Opik" showcase.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.services.core.database import get_db
from app.middleware.auth import verify_clerk_token
from app.services.analytics_service import AnalyticsService

router = APIRouter()


# ==================== SCHEMAS ====================

class OverviewMetricsResponse(BaseModel):
    """Overview metrics for analytics dashboard."""
    total_sessions: int
    avg_score: Optional[float]
    opik_tracked_sessions: int
    opik_coverage_percent: float
    stage_distribution: Dict[str, int]
    score_trend: str  # "up", "down", "stable", "no_data"
    date_range_days: int


class SessionSummary(BaseModel):
    """Summary of a single session."""
    session_id: str
    job_role: Optional[str]
    stage_type: Optional[str]
    overall_score: Optional[int]
    created_at: Optional[str]
    opik_trace_id: Optional[str]


class EvaluationMetricsResponse(BaseModel):
    """Evaluation metrics breakdown."""
    avg_scores_by_stage: Dict[str, float]
    competency_breakdown: Dict[str, float]
    score_distribution: Dict[str, int]
    recent_sessions: List[SessionSummary]


class ComponentMetricsResponse(BaseModel):
    """Component-level metrics for troubleshooting."""
    total_sessions_analyzed: int
    total_turns: int
    estimated_llm_calls: int
    components_used: List[str]
    note: str


# ==================== ENDPOINTS ====================

@router.get("/analytics/overview", response_model=OverviewMetricsResponse)
async def get_overview_metrics(
    days: int = Query(30, ge=1, le=365, description="Date range in days"),
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Get high-level overview metrics for analytics dashboard.

    Returns:
    - Total sessions completed
    - Average score
    - Opik tracing coverage
    - Stage distribution
    - Score trend
    """
    service = AnalyticsService(db)
    metrics = await service.get_overview_metrics(auth_user_id, days=days)
    return metrics


@router.get("/analytics/evaluation", response_model=EvaluationMetricsResponse)
async def get_evaluation_metrics(
    days: int = Query(30, ge=1, le=365, description="Date range in days"),
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Get evaluation metrics breakdown.

    Returns:
    - Average scores by stage type
    - Competency dimension scores
    - Score distribution histogram
    - Recent sessions list
    """
    service = AnalyticsService(db)
    metrics = await service.get_evaluation_metrics(auth_user_id, days=days)
    return metrics


@router.get("/analytics/components", response_model=ComponentMetricsResponse)
async def get_component_metrics(
    days: int = Query(30, ge=1, le=365, description="Date range in days"),
    auth_user_id: str = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Get component-level metrics (for troubleshooting).

    Returns:
    - Estimated LLM calls
    - Components used
    - Session and turn counts

    Note: Detailed LLM metrics (latency, tokens) available in Opik Cloud.
    """
    service = AnalyticsService(db)
    metrics = await service.get_component_metrics(auth_user_id, days=days)
    return metrics
