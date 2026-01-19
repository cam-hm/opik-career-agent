"""
Analytics Service - AI Observability & Performance Metrics.

Provides aggregate analytics for LLM performance, evaluation metrics,
and system health. Powers the /analytics dashboard.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.interview import InterviewSession, InterviewApplication

logger = logging.getLogger("analytics-service")


class AnalyticsService:
    """
    Service for computing analytics metrics from interview sessions.

    Aggregates data from:
    - interview_sessions table (scores, metadata)
    - JSONB fields (skill_assessments, competency_scores)
    - Opik traces (via opik_trace_id)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview_metrics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get high-level overview metrics for the analytics dashboard.

        Returns:
            - total_sessions: Total interview sessions
            - avg_score: Average overall score
            - opik_tracked_sessions: Sessions with Opik trace
            - stage_distribution: Breakdown by stage type
            - score_trend: Recent trend (up/down/stable)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Base query: user's completed sessions in date range
        query = select(InterviewSession).join(
            InterviewApplication
        ).where(
            and_(
                InterviewApplication.user_id == user_id,
                InterviewSession.status == "completed",
                InterviewSession.overall_score.isnot(None),
                InterviewSession.created_at >= cutoff_date
            )
        )

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        if not sessions:
            return {
                "total_sessions": 0,
                "avg_score": None,
                "opik_tracked_sessions": 0,
                "stage_distribution": {},
                "score_trend": "no_data",
                "date_range_days": days
            }

        # Compute metrics
        total_sessions = len(sessions)
        scores = [s.overall_score for s in sessions if s.overall_score is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else None

        opik_tracked = sum(1 for s in sessions if s.opik_trace_id)

        # Stage distribution
        stage_counts = {}
        for session in sessions:
            stage = session.stage_type or "unknown"
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

        # Score trend (compare first half vs second half)
        score_trend = "stable"
        if len(scores) >= 4:
            mid = len(scores) // 2
            first_half_avg = sum(scores[:mid]) / len(scores[:mid])
            second_half_avg = sum(scores[mid:]) / len(scores[mid:])
            diff = second_half_avg - first_half_avg
            if diff > 5:
                score_trend = "up"
            elif diff < -5:
                score_trend = "down"

        return {
            "total_sessions": total_sessions,
            "avg_score": avg_score,
            "opik_tracked_sessions": opik_tracked,
            "opik_coverage_percent": round(opik_tracked / total_sessions * 100, 1) if total_sessions > 0 else 0,
            "stage_distribution": stage_counts,
            "score_trend": score_trend,
            "date_range_days": days
        }

    async def get_evaluation_metrics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get evaluation metrics breakdown.

        Returns:
            - avg_scores_by_stage: Average score per stage type
            - competency_breakdown: Average scores per competency dimension
            - score_distribution: Histogram of scores (0-49, 50-69, 70-89, 90-100)
            - recent_sessions: List of recent sessions with scores
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = select(InterviewSession).join(
            InterviewApplication
        ).where(
            and_(
                InterviewApplication.user_id == user_id,
                InterviewSession.status == "completed",
                InterviewSession.overall_score.isnot(None),
                InterviewSession.created_at >= cutoff_date
            )
        ).order_by(InterviewSession.created_at.desc())

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        if not sessions:
            return {
                "avg_scores_by_stage": {},
                "competency_breakdown": {},
                "score_distribution": {},
                "recent_sessions": []
            }

        # Avg scores by stage
        stage_scores = {}
        for session in sessions:
            stage = session.stage_type or "unknown"
            if stage not in stage_scores:
                stage_scores[stage] = []
            if session.overall_score is not None:
                stage_scores[stage].append(session.overall_score)

        avg_scores_by_stage = {
            stage: round(sum(scores) / len(scores), 1)
            for stage, scores in stage_scores.items()
        }

        # Competency breakdown (aggregate from competency_scores JSONB)
        competency_totals = {}
        competency_counts = {}

        for session in sessions:
            if session.competency_scores:
                for comp, data in session.competency_scores.items():
                    score = data.get("score") if isinstance(data, dict) else data
                    if score is not None:
                        competency_totals[comp] = competency_totals.get(comp, 0) + score
                        competency_counts[comp] = competency_counts.get(comp, 0) + 1

        competency_breakdown = {
            comp: round(competency_totals[comp] / competency_counts[comp], 1)
            for comp in competency_totals
            if competency_counts[comp] > 0
        }

        # Score distribution (histogram)
        score_distribution = {
            "0-49": 0,
            "50-69": 0,
            "70-89": 0,
            "90-100": 0
        }
        for session in sessions:
            score = session.overall_score
            if score is None:
                continue
            if score < 50:
                score_distribution["0-49"] += 1
            elif score < 70:
                score_distribution["50-69"] += 1
            elif score < 90:
                score_distribution["70-89"] += 1
            else:
                score_distribution["90-100"] += 1

        # Recent sessions (top 20)
        recent_sessions = [
            {
                "session_id": s.session_id,
                "job_role": s.job_role,
                "stage_type": s.stage_type,
                "overall_score": s.overall_score,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "opik_trace_id": s.opik_trace_id
            }
            for s in sessions[:20]
        ]

        return {
            "avg_scores_by_stage": avg_scores_by_stage,
            "competency_breakdown": competency_breakdown,
            "score_distribution": score_distribution,
            "recent_sessions": recent_sessions
        }

    async def get_component_metrics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get per-component metrics (for troubleshooting).

        Extracts metadata from skill_assessments JSONB field.

        Returns:
            - total_llm_calls: Estimated from skill_assessments
            - avg_latency_ms: Average LLM latency (if available in metadata)
            - components_used: List of components used
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = select(InterviewSession).join(
            InterviewApplication
        ).where(
            and_(
                InterviewApplication.user_id == user_id,
                InterviewSession.status == "completed",
                InterviewSession.created_at >= cutoff_date
            )
        )

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        # Aggregate component usage from skill_assessments
        # skill_assessments structure: [{"turn": 1, "score": 75, "dimension": "...", ...}]
        total_turns = 0
        components_seen = set()

        for session in sessions:
            if session.skill_assessments:
                total_turns += len(session.skill_assessments)
                # Each turn typically involves scoring_engine
                components_seen.add("scoring_engine")

            if session.candidate_profile:
                # candidate_profile implies candidate_profile_manager was used
                components_seen.add("candidate_profile")

            if session.feedback_markdown:
                # feedback generation
                components_seen.add("feedback_generation")

        # Estimate LLM calls (rough approximation)
        # Each session: 1 greeting + N turns (scoring) + 1 feedback + profile updates
        estimated_llm_calls = len(sessions) * 2 + total_turns  # greeting + feedback + per-turn scoring

        return {
            "total_sessions_analyzed": len(sessions),
            "total_turns": total_turns,
            "estimated_llm_calls": estimated_llm_calls,
            "components_used": list(components_seen),
            "note": "Detailed LLM metrics available in Opik Cloud dashboard"
        }


# Singleton pattern for service (not strictly necessary, but follows progress_service pattern)
def get_analytics_service(db: AsyncSession) -> AnalyticsService:
    """Factory function for dependency injection."""
    return AnalyticsService(db)
