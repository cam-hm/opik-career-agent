"""
Progress Service - Personal Growth & Learning features.

Handles:
- Resolution tracking (2026 career goals)
- Skill gap analysis
- Weekly insights generation
- Progress snapshots
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.gamification import UserProgress, UserResolution, SkillSnapshot
from app.models.interview import InterviewSession, InterviewApplication
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Default skill dimensions for tracking
DEFAULT_SKILL_DIMENSIONS = [
    "technical_depth",
    "communication",
    "problem_solving",
    "system_design",
    "leadership",
    "adaptability"
]


class ProgressService:
    """Service for tracking personal growth and learning progress."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== RESOLUTION MANAGEMENT ====================

    async def create_resolution(
        self,
        user_id: str,
        title: str,
        target_role: Optional[str] = None,
        description: Optional[str] = None,
        target_skills: Optional[Dict[str, int]] = None,
        target_date: Optional[datetime] = None
    ) -> UserResolution:
        """
        Create a new 2026 resolution for the user.
        Captures current skill levels as baseline.
        """
        # Ensure user_progress exists (required for FK constraint)
        await self._ensure_user_progress_exists(user_id)

        # Get current skill levels as baseline
        baseline = await self._get_current_skill_levels(user_id)

        # Set default targets if not provided (baseline + 20%)
        if not target_skills:
            target_skills = {
                skill: min(100, int(level * 1.2))
                for skill, level in baseline.items()
            }

        resolution = UserResolution(
            user_id=user_id,
            title=title,
            description=description,
            target_role=target_role,
            target_skills=target_skills,
            baseline_skills=baseline,
            target_date=target_date or datetime(2026, 12, 31),
            status="active"
        )

        self.db.add(resolution)
        await self.db.commit()
        await self.db.refresh(resolution)

        logger.info(f"Created resolution '{title}' for user {user_id}")
        return resolution

    async def get_user_resolutions(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[UserResolution]:
        """Get all resolutions for a user, optionally filtered by status."""
        query = select(UserResolution).where(UserResolution.user_id == user_id)

        if status:
            query = query.where(UserResolution.status == status)

        query = query.order_by(UserResolution.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_resolution(
        self,
        resolution_id: UUID,
        user_id: str
    ) -> Optional[UserResolution]:
        """Get a specific resolution."""
        query = select(UserResolution).where(
            UserResolution.id == resolution_id,
            UserResolution.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_resolution(
        self,
        resolution_id: UUID,
        user_id: str,
        **updates
    ) -> Optional[UserResolution]:
        """Update a resolution."""
        resolution = await self.get_resolution(resolution_id, user_id)
        if not resolution:
            return None

        for key, value in updates.items():
            if hasattr(resolution, key) and value is not None:
                setattr(resolution, key, value)

        await self.db.commit()
        await self.db.refresh(resolution)
        return resolution

    async def complete_resolution(
        self,
        resolution_id: UUID,
        user_id: str
    ) -> Optional[UserResolution]:
        """Mark a resolution as completed."""
        resolution = await self.get_resolution(resolution_id, user_id)
        if not resolution:
            return None

        resolution.status = "completed"
        resolution.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(resolution)

        logger.info(f"Resolution {resolution_id} completed for user {user_id}")
        return resolution

    async def get_resolution_progress(
        self,
        resolution_id: UUID,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate progress towards a resolution.
        Returns progress percentage for each target skill.
        """
        resolution = await self.get_resolution(resolution_id, user_id)
        if not resolution:
            return None

        current_skills = await self._get_current_skill_levels(user_id)
        baseline = resolution.baseline_skills or {}
        targets = resolution.target_skills or {}

        progress = {}
        overall_progress = 0
        skill_count = 0

        for skill, target in targets.items():
            baseline_val = baseline.get(skill, 0)
            current_val = current_skills.get(skill, baseline_val)

            # Calculate progress: (current - baseline) / (target - baseline)
            if target > baseline_val:
                skill_progress = (current_val - baseline_val) / (target - baseline_val) * 100
                skill_progress = max(0, min(100, skill_progress))  # Clamp 0-100
            else:
                skill_progress = 100 if current_val >= target else 0

            progress[skill] = {
                "baseline": baseline_val,
                "current": current_val,
                "target": target,
                "progress_percent": round(skill_progress, 1)
            }

            overall_progress += skill_progress
            skill_count += 1

        return {
            "resolution_id": str(resolution.id),
            "title": resolution.title,
            "status": resolution.status,
            "target_date": resolution.target_date.isoformat() if resolution.target_date else None,
            "skills_progress": progress,
            "overall_progress": round(overall_progress / skill_count, 1) if skill_count > 0 else 0,
            "days_remaining": (resolution.target_date - datetime.utcnow()).days if resolution.target_date else None
        }

    # ==================== SKILL GAP ANALYSIS ====================

    async def get_skill_gap_analysis(
        self,
        user_id: str,
        target_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze skill gaps between current levels and target requirements.
        Uses data from interview sessions and competency scores.
        """
        # Get current skill levels
        current_skills = await self._get_current_skill_levels(user_id)

        # Get verified skills from recent sessions
        verified_skills = await self._get_verified_skills(user_id)

        # Get identified gaps from sessions
        identified_gaps = await self._get_identified_gaps(user_id)

        # Get target requirements (from latest resolution or default)
        target_requirements = await self._get_target_requirements(user_id, target_role)

        # Calculate gaps
        gaps = []
        strengths = []

        for skill, target in target_requirements.items():
            current = current_skills.get(skill, 0)
            gap = target - current

            skill_data = {
                "skill": skill,
                "current": current,
                "target": target,
                "gap": gap,
                "verified": skill in verified_skills,
                "evidence": verified_skills.get(skill, {}).get("evidence", None)
            }

            if gap > 15:  # Significant gap
                gaps.append(skill_data)
            elif gap < -10:  # Exceeds target
                strengths.append(skill_data)

        # Sort gaps by severity
        gaps.sort(key=lambda x: x["gap"], reverse=True)
        strengths.sort(key=lambda x: x["gap"])

        return {
            "user_id": user_id,
            "target_role": target_role,
            "current_skills": current_skills,
            "target_requirements": target_requirements,
            "verified_skills": list(verified_skills.keys()),
            "gaps": gaps,
            "strengths": strengths,
            "identified_gaps_from_interviews": identified_gaps,
            "recommendations": self._generate_gap_recommendations(gaps, identified_gaps),
            "analyzed_at": datetime.utcnow().isoformat()
        }

    def _generate_gap_recommendations(
        self,
        gaps: List[Dict],
        identified_gaps: List[str]
    ) -> List[str]:
        """Generate recommendations based on identified gaps."""
        recommendations = []

        if gaps:
            top_gap = gaps[0]
            recommendations.append(
                f"Focus on improving {top_gap['skill'].replace('_', ' ')} - "
                f"currently at {top_gap['current']}%, target is {top_gap['target']}%"
            )

        if len(gaps) > 1:
            recommendations.append(
                f"Schedule practice sessions for: {', '.join(g['skill'].replace('_', ' ') for g in gaps[:3])}"
            )

        if identified_gaps:
            recommendations.append(
                f"Interview feedback identified these areas: {', '.join(identified_gaps[:3])}"
            )

        if not gaps:
            recommendations.append(
                "You're meeting your skill targets! Consider setting more ambitious goals."
            )

        return recommendations

    # ==================== WEEKLY INSIGHTS ====================

    async def generate_weekly_insights(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate AI-powered weekly insights based on recent performance.
        """
        # Get sessions from the past week
        week_ago = datetime.utcnow() - timedelta(days=7)
        sessions = await self._get_recent_sessions(user_id, since=week_ago)

        if not sessions:
            return {
                "user_id": user_id,
                "period": "weekly",
                "period_start": week_ago.isoformat(),
                "period_end": datetime.utcnow().isoformat(),
                "sessions_count": 0,
                "message": "No interview sessions this week. Start practicing to get personalized insights!",
                "recommendations": [
                    "Schedule your first practice session of the week",
                    "Review feedback from your previous sessions",
                    "Set specific goals for your next interview"
                ]
            }

        # Calculate statistics
        scores = [s.overall_score for s in sessions if s.overall_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Aggregate competency data
        competencies = await self._aggregate_competencies(sessions)

        # Get previous week for comparison
        two_weeks_ago = week_ago - timedelta(days=7)
        prev_sessions = await self._get_recent_sessions(user_id, since=two_weeks_ago, until=week_ago)
        prev_scores = [s.overall_score for s in prev_sessions if s.overall_score is not None]
        prev_avg = sum(prev_scores) / len(prev_scores) if prev_scores else None

        # Calculate trend
        trend = None
        if prev_avg is not None:
            trend = avg_score - prev_avg

        # Generate AI insights
        insights = await self._generate_ai_insights(
            sessions=sessions,
            avg_score=avg_score,
            competencies=competencies,
            trend=trend
        )

        # Create snapshot
        await self._create_weekly_snapshot(
            user_id=user_id,
            sessions=sessions,
            competencies=competencies,
            avg_score=avg_score,
            period_start=week_ago,
            period_end=datetime.utcnow()
        )

        return {
            "user_id": user_id,
            "period": "weekly",
            "period_start": week_ago.isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "sessions_count": len(sessions),
            "average_score": round(avg_score, 1),
            "score_trend": round(trend, 1) if trend is not None else None,
            "trend_direction": "up" if trend and trend > 0 else "down" if trend and trend < 0 else "stable",
            "competencies": competencies,
            "strengths": insights.get("strengths", []),
            "areas_to_improve": insights.get("areas_to_improve", []),
            "recommendations": insights.get("recommendations", []),
            "highlights": insights.get("highlights", []),
            "generated_at": datetime.utcnow().isoformat()
        }

    async def _generate_ai_insights(
        self,
        sessions: List[InterviewSession],
        avg_score: float,
        competencies: Dict[str, float],
        trend: Optional[float]
    ) -> Dict[str, Any]:
        """Generate AI-powered insights using Gemini."""
        try:
            from google import genai

            client = genai.Client(api_key=settings.GOOGLE_API_KEY)

            # Prepare session summaries
            session_summaries = []
            for s in sessions[:5]:  # Limit to last 5
                session_summaries.append({
                    "role": s.application.job_role if s.application else "Unknown",
                    "stage": s.stage_type,
                    "score": s.overall_score,
                    "competencies": s.competency_scores or {}
                })

            prompt = f"""Analyze this user's weekly interview practice performance and provide insights.

Weekly Stats:
- Sessions completed: {len(sessions)}
- Average score: {avg_score:.1f}/100
- Score trend: {"+" if trend and trend > 0 else ""}{trend:.1f if trend else "N/A"} vs last week
- Competency averages: {competencies}

Recent sessions:
{session_summaries}

Provide a JSON response with:
{{
    "strengths": ["strength 1", "strength 2"],
    "areas_to_improve": ["area 1", "area 2"],
    "recommendations": ["specific actionable recommendation 1", "recommendation 2"],
    "highlights": ["notable achievement or observation"]
}}

Be specific, encouraging, and actionable. Focus on growth mindset."""

            response = await client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )

            # Parse JSON response
            import json
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            if text.endswith("```"):
                text = text[:-3]

            return json.loads(text.strip())

        except Exception as e:
            logger.error(f"Failed to generate AI insights: {e}")
            # Fallback to rule-based insights
            return self._generate_fallback_insights(avg_score, competencies, trend)

    def _generate_fallback_insights(
        self,
        avg_score: float,
        competencies: Dict[str, float],
        trend: Optional[float]
    ) -> Dict[str, Any]:
        """Fallback insights when AI is unavailable."""
        strengths = []
        areas_to_improve = []
        recommendations = []
        highlights = []

        # Analyze competencies
        for comp, score in competencies.items():
            if score >= 75:
                strengths.append(f"Strong {comp.replace('_', ' ')} skills ({score:.0f}%)")
            elif score < 60:
                areas_to_improve.append(f"{comp.replace('_', ' ').title()} needs attention ({score:.0f}%)")

        # Score-based insights
        if avg_score >= 80:
            highlights.append("Excellent performance this week! You're interview-ready.")
        elif avg_score >= 60:
            highlights.append("Solid progress this week. Keep practicing!")
        else:
            highlights.append("Room for growth - focus on fundamentals.")

        # Trend-based recommendations
        if trend and trend > 5:
            highlights.append(f"Great improvement! Score up {trend:.1f} points from last week.")
        elif trend and trend < -5:
            recommendations.append("Your scores dipped this week. Review recent feedback for patterns.")

        # Generic recommendations
        recommendations.append("Practice at least 2-3 sessions per week for consistent improvement.")

        return {
            "strengths": strengths[:3],
            "areas_to_improve": areas_to_improve[:3],
            "recommendations": recommendations[:3],
            "highlights": highlights[:2]
        }

    # ==================== HELPER METHODS ====================

    async def _get_current_skill_levels(self, user_id: str) -> Dict[str, int]:
        """Get user's current skill levels from UserProgress."""
        query = select(UserProgress).where(UserProgress.user_id == user_id)
        result = await self.db.execute(query)
        progress = result.scalar_one_or_none()

        if progress and progress.skill_stats:
            # Map skill_stats keys to standard dimensions
            return {
                "technical_depth": progress.skill_stats.get("tech_proficiency", 50),
                "communication": progress.skill_stats.get("communication", 50),
                "problem_solving": progress.skill_stats.get("algorithms", 50),
                "system_design": progress.skill_stats.get("system_design", 50),
                "leadership": progress.skill_stats.get("coding_standards", 50),
                "adaptability": progress.skill_stats.get("debugging", 50)
            }

        # Return defaults if no progress record
        return {skill: 50 for skill in DEFAULT_SKILL_DIMENSIONS}

    async def _get_verified_skills(self, user_id: str) -> Dict[str, Dict]:
        """Get skills verified through interview sessions."""
        # Get recent sessions with candidate profiles
        query = (
            select(InterviewSession)
            .join(InterviewApplication)
            .where(InterviewApplication.user_id == user_id)
            .where(InterviewSession.candidate_profile.isnot(None))
            .order_by(InterviewSession.created_at.desc())
            .limit(10)
        )
        result = await self.db.execute(query)
        sessions = result.scalars().all()

        verified = {}
        for session in sessions:
            profile = session.candidate_profile or {}
            for skill, data in profile.get("verified_skills", {}).items():
                if skill not in verified or data.get("depth", 0) > verified[skill].get("depth", 0):
                    verified[skill] = data

        return verified

    async def _get_identified_gaps(self, user_id: str) -> List[str]:
        """Get identified skill gaps from interview sessions."""
        query = (
            select(InterviewSession)
            .join(InterviewApplication)
            .where(InterviewApplication.user_id == user_id)
            .where(InterviewSession.candidate_profile.isnot(None))
            .order_by(InterviewSession.created_at.desc())
            .limit(5)
        )
        result = await self.db.execute(query)
        sessions = result.scalars().all()

        gaps = set()
        for session in sessions:
            profile = session.candidate_profile or {}
            for gap in profile.get("identified_gaps", []):
                gaps.add(gap)

        return list(gaps)

    async def _get_target_requirements(
        self,
        user_id: str,
        target_role: Optional[str] = None
    ) -> Dict[str, int]:
        """Get target skill requirements based on role or resolution."""
        # First, check if user has an active resolution
        resolutions = await self.get_user_resolutions(user_id, status="active")
        if resolutions:
            return resolutions[0].target_skills or {}

        # Default targets based on role
        role_targets = {
            "senior": {
                "technical_depth": 80,
                "communication": 75,
                "problem_solving": 80,
                "system_design": 75,
                "leadership": 70,
                "adaptability": 70
            },
            "mid": {
                "technical_depth": 70,
                "communication": 65,
                "problem_solving": 70,
                "system_design": 60,
                "leadership": 55,
                "adaptability": 65
            },
            "default": {
                "technical_depth": 60,
                "communication": 60,
                "problem_solving": 60,
                "system_design": 50,
                "leadership": 50,
                "adaptability": 60
            }
        }

        if target_role:
            role_lower = target_role.lower()
            if "senior" in role_lower or "lead" in role_lower:
                return role_targets["senior"]
            elif "mid" in role_lower:
                return role_targets["mid"]

        return role_targets["default"]

    async def _get_recent_sessions(
        self,
        user_id: str,
        since: datetime,
        until: Optional[datetime] = None
    ) -> List[InterviewSession]:
        """Get user's interview sessions within a date range."""
        query = (
            select(InterviewSession)
            .join(InterviewApplication)
            .options(selectinload(InterviewSession.application))
            .where(InterviewApplication.user_id == user_id)
            .where(InterviewSession.created_at >= since)
            .where(InterviewSession.status == "completed")
        )

        if until:
            query = query.where(InterviewSession.created_at < until)

        query = query.order_by(InterviewSession.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _aggregate_competencies(
        self,
        sessions: List[InterviewSession]
    ) -> Dict[str, float]:
        """Aggregate competency scores across sessions."""
        competencies = {}
        counts = {}

        for session in sessions:
            if session.competency_scores:
                for comp, data in session.competency_scores.items():
                    score = data.get("score", 0) if isinstance(data, dict) else data
                    if comp not in competencies:
                        competencies[comp] = 0
                        counts[comp] = 0
                    competencies[comp] += score
                    counts[comp] += 1

        # Calculate averages
        return {
            comp: round(total / counts[comp], 1)
            for comp, total in competencies.items()
            if counts.get(comp, 0) > 0
        }

    async def _ensure_user_progress_exists(self, user_id: str) -> UserProgress:
        """Ensure user_progress record exists for the user."""
        query = select(UserProgress).where(UserProgress.user_id == user_id)
        result = await self.db.execute(query)
        progress = result.scalar_one_or_none()

        if not progress:
            # Create default user_progress record
            progress = UserProgress(
                user_id=user_id,
                current_level=1,
                current_xp=0,
                daily_streak=0,
                skill_stats={skill: 50 for skill in DEFAULT_SKILL_DIMENSIONS}
            )
            self.db.add(progress)
            await self.db.commit()
            await self.db.refresh(progress)
            logger.info(f"Created default user_progress for user {user_id}")

        return progress

    async def _create_weekly_snapshot(
        self,
        user_id: str,
        sessions: List[InterviewSession],
        competencies: Dict[str, float],
        avg_score: float,
        period_start: datetime,
        period_end: datetime
    ) -> SkillSnapshot:
        """Create a weekly skill snapshot for historical tracking."""
        # Ensure user_progress exists (required for FK constraint)
        await self._ensure_user_progress_exists(user_id)

        skill_levels = await self._get_current_skill_levels(user_id)

        snapshot = SkillSnapshot(
            user_id=user_id,
            skill_levels=skill_levels,
            competency_averages=competencies,
            sessions_count=len(sessions),
            average_score=int(avg_score),
            snapshot_type="weekly",
            period_start=period_start,
            period_end=period_end
        )

        self.db.add(snapshot)
        await self.db.commit()

        return snapshot

    async def get_skill_history(
        self,
        user_id: str,
        weeks: int = 12
    ) -> List[Dict[str, Any]]:
        """Get historical skill snapshots for trend visualization."""
        cutoff = datetime.utcnow() - timedelta(weeks=weeks)

        query = (
            select(SkillSnapshot)
            .where(SkillSnapshot.user_id == user_id)
            .where(SkillSnapshot.period_start >= cutoff)
            .order_by(SkillSnapshot.period_start.asc())
        )
        result = await self.db.execute(query)
        snapshots = result.scalars().all()

        return [
            {
                "period_start": s.period_start.isoformat(),
                "period_end": s.period_end.isoformat(),
                "skill_levels": s.skill_levels,
                "competency_averages": s.competency_averages,
                "sessions_count": s.sessions_count,
                "average_score": s.average_score
            }
            for s in snapshots
        ]


# Dependency injection helper
async def get_progress_service(db: AsyncSession) -> ProgressService:
    """FastAPI dependency for ProgressService."""
    return ProgressService(db)
