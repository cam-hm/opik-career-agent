"""
Cross-Stage Memory Service.

Persists insights from each interview stage to inform subsequent stages.
Enables continuity across HR -> Technical -> Behavioral pipeline.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from google import genai
from sqlalchemy import update, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.services.core.database import AsyncSessionLocal
from app.models.interview import InterviewApplication
from app.services.core.intelligence.candidate_profile import CandidateProfile
from config.settings import get_settings

logger = logging.getLogger("cross-stage-memory")


@dataclass
class StageInsights:
    """Insights extracted from a completed interview stage."""
    stage_type: str
    summary: str
    communication_style: str
    verified_skills: List[str]
    red_flags: List[str]
    strengths: List[str]
    concerns: List[str]
    key_topics_covered: List[str]
    overall_score: float
    confidence: float
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CrossStageMemory:
    """
    Manages cross-stage memory for interview continuity.

    Saves insights at the end of each stage and retrieves them
    for subsequent stages to avoid repetition and build on findings.
    """

    INSIGHT_EXTRACTION_PROMPT = """Analyze this interview stage and extract key insights for the next interviewer.

STAGE: {stage_type}
JOB ROLE: {job_role}

CANDIDATE PROFILE:
{profile_json}

TRANSCRIPT SUMMARY (last messages):
{transcript_summary}

SCORES:
{scores_summary}

Extract insights that would be valuable for the NEXT interviewer to know:
1. What was verified about the candidate?
2. What concerns were raised?
3. What topics were already covered (don't repeat)?
4. What communication style did the candidate exhibit?
5. What should the next stage focus on?

Return JSON:
{{
    "summary": "Brief 2-3 sentence summary of the stage outcome",
    "communication_style": "e.g., 'concise and technical' or 'verbose but thoughtful'",
    "verified_skills": ["skill1", "skill2"],
    "red_flags": ["concern1"],
    "strengths": ["strength1"],
    "concerns": ["areas needing further exploration"],
    "key_topics_covered": ["topic1", "topic2"],
    "notes": "Any other important observations"
}}"""

    def __init__(self):
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.GOOGLE_API_KEY)
        self.model = self.settings.SHADOW_MODEL

    async def save_stage_insights(
        self,
        application_id: str,
        stage_type: str,
        profile: CandidateProfile,
        transcript: List[Dict[str, str]],
        scores: List[Dict[str, Any]],
        job_role: str
    ) -> StageInsights:
        """
        Extract and save insights at the end of a stage.

        Args:
            application_id: The interview application ID
            stage_type: Completed stage type (hr, technical, behavioral)
            profile: Candidate profile built during the stage
            transcript: Conversation transcript
            scores: Per-turn scores
            job_role: Target job role

        Returns:
            Extracted StageInsights
        """
        try:
            insights = await self._extract_insights(
                stage_type, profile, transcript, scores, job_role
            )

            # Save to database
            await self._persist_insights(application_id, stage_type, insights)

            logger.info(f"Saved insights for stage {stage_type} of application {application_id}")
            return insights

        except Exception as e:
            logger.error(f"Failed to save stage insights: {e}")
            # Return minimal insights on error
            return StageInsights(
                stage_type=stage_type,
                summary="Stage completed (insights extraction failed)",
                communication_style="unknown",
                verified_skills=[],
                red_flags=[],
                strengths=[],
                concerns=[],
                key_topics_covered=[],
                overall_score=profile.performance_trajectory[-1] if profile.performance_trajectory else 50,
                confidence=0.0,
                notes=""
            )

    async def _extract_insights(
        self,
        stage_type: str,
        profile: CandidateProfile,
        transcript: List[Dict[str, str]],
        scores: List[Dict[str, Any]],
        job_role: str
    ) -> StageInsights:
        """Extract insights using AI."""
        # Prepare transcript summary (last 10 exchanges)
        recent_transcript = transcript[-20:] if len(transcript) > 20 else transcript
        transcript_summary = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:200]}..."
            for msg in recent_transcript
        ])

        # Prepare scores summary
        if scores:
            avg_score = sum(s.get("score", 50) for s in scores) / len(scores)
            scores_summary = f"Average: {avg_score:.1f}/100 across {len(scores)} questions"
        else:
            scores_summary = "No detailed scores available"

        prompt = self.INSIGHT_EXTRACTION_PROMPT.format(
            stage_type=stage_type,
            job_role=job_role,
            profile_json=json.dumps(profile.to_dict(), indent=2)[:1500],
            transcript_summary=transcript_summary[:2000],
            scores_summary=scores_summary
        )

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )

        data = json.loads(response.text)

        # Compute overall score
        overall_score = (
            sum(profile.performance_trajectory) / len(profile.performance_trajectory)
            if profile.performance_trajectory else 50.0
        )

        return StageInsights(
            stage_type=stage_type,
            summary=data.get("summary", ""),
            communication_style=data.get("communication_style", ""),
            verified_skills=data.get("verified_skills", []),
            red_flags=data.get("red_flags", []),
            strengths=data.get("strengths", []),
            concerns=data.get("concerns", []),
            key_topics_covered=data.get("key_topics_covered", []),
            overall_score=overall_score,
            confidence=0.8,
            notes=data.get("notes", "")
        )

    async def _persist_insights(
        self,
        application_id: str,
        stage_type: str,
        insights: StageInsights
    ):
        """Persist insights to database."""
        async with AsyncSessionLocal() as db:
            # Get current insights
            result = await db.execute(
                select(InterviewApplication.cross_stage_insights)
                .where(InterviewApplication.id == application_id)
            )
            current = result.scalar() or {}

            # Update with new stage insights
            current[stage_type] = insights.to_dict()

            # Save back
            await db.execute(
                update(InterviewApplication)
                .where(InterviewApplication.id == application_id)
                .values(cross_stage_insights=current)
            )
            await db.commit()

    async def get_previous_insights(
        self,
        application_id: str,
        current_stage: str
    ) -> Dict[str, StageInsights]:
        """
        Get insights from previous stages.

        Args:
            application_id: The interview application ID
            current_stage: Current stage (to filter out)

        Returns:
            Dictionary of stage_type -> StageInsights for previous stages
        """
        # Define stage order
        stage_order = ["hr", "technical", "behavioral"]

        try:
            current_idx = stage_order.index(current_stage)
            previous_stages = stage_order[:current_idx]
        except ValueError:
            # Unknown stage, return all available insights
            previous_stages = stage_order

        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(InterviewApplication.cross_stage_insights)
                    .where(InterviewApplication.id == application_id)
                )
                all_insights = result.scalar() or {}

            # Filter to previous stages only
            filtered = {}
            for stage in previous_stages:
                if stage in all_insights:
                    data = all_insights[stage]
                    filtered[stage] = StageInsights(
                        stage_type=data.get("stage_type", stage),
                        summary=data.get("summary", ""),
                        communication_style=data.get("communication_style", ""),
                        verified_skills=data.get("verified_skills", []),
                        red_flags=data.get("red_flags", []),
                        strengths=data.get("strengths", []),
                        concerns=data.get("concerns", []),
                        key_topics_covered=data.get("key_topics_covered", []),
                        overall_score=data.get("overall_score", 50),
                        confidence=data.get("confidence", 0),
                        notes=data.get("notes", "")
                    )

            return filtered

        except Exception as e:
            logger.error(f"Failed to retrieve insights: {e}")
            return {}

    def build_context_prompt(self, insights: Dict[str, StageInsights]) -> str:
        """
        Build prompt section from previous stage insights.

        Args:
            insights: Dictionary of stage -> StageInsights

        Returns:
            Formatted prompt text for injection
        """
        if not insights:
            return ""

        sections = [
            "PREVIOUS STAGE INSIGHTS:",
            "DO NOT repeat topics already covered. Build on these findings.\n"
        ]

        for stage, data in insights.items():
            stage_section = f"""
[{stage.upper()} STAGE - Score: {data.overall_score:.0f}/100]
Summary: {data.summary}
Communication Style: {data.communication_style}
Verified Skills: {', '.join(data.verified_skills[:5]) if data.verified_skills else 'None verified'}
Concerns to Follow Up: {', '.join(data.concerns[:3]) if data.concerns else 'None'}
Topics Already Covered (DO NOT REPEAT): {', '.join(data.key_topics_covered[:8])}
"""
            if data.red_flags:
                stage_section += f"RED FLAGS: {', '.join(data.red_flags[:3])}\n"

            sections.append(stage_section)

        return "\n".join(sections)

    def get_handoff_summary(self, insights: Dict[str, StageInsights]) -> str:
        """
        Get a brief handoff summary for the next stage.

        Args:
            insights: Dictionary of stage -> StageInsights

        Returns:
            Brief summary text
        """
        if not insights:
            return "No previous stage data available."

        summaries = []
        for stage, data in insights.items():
            status = "PASSED" if data.overall_score >= 60 else "CONCERNS"
            summaries.append(f"{stage.upper()}: {status} ({data.overall_score:.0f}%)")

        return " | ".join(summaries)


# Singleton instance
cross_stage_memory = CrossStageMemory()
