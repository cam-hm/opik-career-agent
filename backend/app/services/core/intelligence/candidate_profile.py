"""
Candidate Profile Manager.

Builds and maintains a real-time profile of the candidate during the interview.
Tracks verified skills, identified gaps, red flags, and performance trajectory.
"""
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set
from google import genai
from config.settings import get_settings

logger = logging.getLogger("candidate-profile")


@dataclass
class SkillAssessment:
    """Assessment of a single skill."""
    depth: int  # 1-5 scale
    evidence: str  # Quote or summary from candidate
    verified_at_turn: int
    confidence: float  # 0-1


@dataclass
class CandidateProfile:
    """Real-time candidate profile built during interview."""
    # Verified technical and soft skills with depth ratings
    verified_skills: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Gaps identified (skills in JD but weak/missing in candidate)
    identified_gaps: List[str] = field(default_factory=list)

    # Red flags (inconsistencies, concerning patterns)
    red_flags: List[Dict[str, str]] = field(default_factory=list)

    # Strengths identified
    strengths: List[str] = field(default_factory=list)

    # Topics already covered (to avoid repetition)
    topics_covered: Set[str] = field(default_factory=set)

    # Questions asked with metadata
    questions_asked: List[Dict[str, Any]] = field(default_factory=list)

    # Performance trajectory (scores over time)
    performance_trajectory: List[float] = field(default_factory=list)

    # Key facts extracted from answers
    key_facts: List[str] = field(default_factory=list)

    # Current turn number
    current_turn: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "verified_skills": self.verified_skills,
            "identified_gaps": self.identified_gaps,
            "red_flags": self.red_flags,
            "strengths": self.strengths,
            "topics_covered": list(self.topics_covered),
            "questions_asked": self.questions_asked,
            "performance_trajectory": self.performance_trajectory,
            "key_facts": self.key_facts,
            "current_turn": self.current_turn
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CandidateProfile":
        """Create from dictionary."""
        if not data:
            return cls()
        return cls(
            verified_skills=data.get("verified_skills", {}),
            identified_gaps=data.get("identified_gaps", []),
            red_flags=data.get("red_flags", []),
            strengths=data.get("strengths", []),
            topics_covered=set(data.get("topics_covered", [])),
            questions_asked=data.get("questions_asked", []),
            performance_trajectory=data.get("performance_trajectory", []),
            key_facts=data.get("key_facts", []),
            current_turn=data.get("current_turn", 0)
        )


class CandidateProfileManager:
    """
    Manages real-time candidate profiling during interviews.
    Uses AI to extract insights from resume and answers.
    """

    INITIAL_PROFILE_PROMPT = """Analyze this resume and job description to create an initial candidate profile.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Extract and return JSON:
{{
    "claimed_skills": ["skill1", "skill2"],
    "experience_years": 5,
    "education_level": "Bachelor's/Master's/PhD",
    "potential_gaps": ["skill from JD not in resume"],
    "potential_strengths": ["strong points from resume"],
    "initial_topics": ["topics to explore"]
}}

Focus on factual extraction. Do not infer or assume."""

    UPDATE_PROFILE_PROMPT = """Analyze this interview exchange and update the candidate profile.

QUESTION ASKED:
{question}

CANDIDATE'S ANSWER:
{answer}

ANSWER SCORE: {score}/100

CURRENT PROFILE:
{current_profile}

Based on this exchange, extract:
1. Any skills that were VERIFIED (candidate demonstrated knowledge)
2. Any skills that showed WEAKNESS (candidate struggled)
3. Any RED FLAGS (inconsistencies, concerning statements)
4. Any NEW STRENGTHS identified
5. KEY FACTS learned about the candidate

Return JSON:
{{
    "verified_skills": {{"skill_name": {{"depth": 1-5, "evidence": "brief quote"}}}},
    "weakness_signals": ["areas where candidate struggled"],
    "red_flags": [{{"type": "inconsistency|evasion|concern", "detail": "..."}}],
    "new_strengths": ["newly identified strengths"],
    "key_facts": ["important facts learned"],
    "topic_covered": "main topic of this exchange"
}}"""

    def __init__(self):
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.GOOGLE_API_KEY)
        self.model = self.settings.SHADOW_MODEL  # Use fast model

    async def create_initial_profile(
        self,
        resume_text: str,
        job_description: str
    ) -> CandidateProfile:
        """Build initial profile from resume and job description."""
        profile = CandidateProfile()

        if not resume_text or len(resume_text.strip()) < 50:
            logger.info("No resume provided, starting with blank profile")
            return profile

        try:
            prompt = self.INITIAL_PROFILE_PROMPT.format(
                resume_text=resume_text[:3000],
                job_description=job_description[:2000] if job_description else "Not provided"
            )

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )

            data = json.loads(response.text)

            # Initialize profile with extracted data
            for skill in data.get("claimed_skills", []):
                profile.verified_skills[skill] = {
                    "depth": 0,  # Not verified yet
                    "evidence": "From resume (unverified)",
                    "verified_at_turn": 0,
                    "confidence": 0.3
                }

            profile.identified_gaps = data.get("potential_gaps", [])
            profile.strengths = data.get("potential_strengths", [])
            profile.key_facts.append(f"Experience: ~{data.get('experience_years', 'Unknown')} years")
            profile.key_facts.append(f"Education: {data.get('education_level', 'Unknown')}")

            # Set initial topics to explore
            for topic in data.get("initial_topics", []):
                profile.topics_covered.add(f"pending:{topic}")

            logger.info(f"Initial profile created with {len(profile.verified_skills)} claimed skills")
            return profile

        except Exception as e:
            logger.error(f"Failed to create initial profile: {e}")
            return profile

    async def update_after_turn(
        self,
        profile: CandidateProfile,
        question: str,
        answer: str,
        score: float
    ) -> CandidateProfile:
        """Update profile after each Q&A turn."""
        profile.current_turn += 1
        profile.performance_trajectory.append(score)

        # Track the question
        profile.questions_asked.append({
            "turn": profile.current_turn,
            "question": question[:200],
            "score": score
        })

        if not answer or len(answer.strip()) < 20:
            logger.debug("Answer too short, skipping profile update")
            return profile

        try:
            prompt = self.UPDATE_PROFILE_PROMPT.format(
                question=question,
                answer=answer[:1500],
                score=score,
                current_profile=json.dumps({
                    "verified_skills": profile.verified_skills,
                    "strengths": profile.strengths,
                    "gaps": profile.identified_gaps
                }, indent=2)
            )

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )

            data = json.loads(response.text)

            # Update verified skills
            for skill, assessment in data.get("verified_skills", {}).items():
                existing = profile.verified_skills.get(skill, {})
                new_depth = assessment.get("depth", 3)

                # Only upgrade if new depth is higher
                if new_depth > existing.get("depth", 0):
                    profile.verified_skills[skill] = {
                        "depth": new_depth,
                        "evidence": assessment.get("evidence", ""),
                        "verified_at_turn": profile.current_turn,
                        "confidence": 0.8 if score >= 70 else 0.5
                    }

            # Add weakness signals to gaps if not already there
            for weakness in data.get("weakness_signals", []):
                if weakness not in profile.identified_gaps:
                    profile.identified_gaps.append(weakness)

            # Add red flags
            for flag in data.get("red_flags", []):
                if flag not in profile.red_flags:
                    profile.red_flags.append(flag)

            # Add new strengths
            for strength in data.get("new_strengths", []):
                if strength not in profile.strengths:
                    profile.strengths.append(strength)

            # Add key facts
            for fact in data.get("key_facts", []):
                if fact not in profile.key_facts:
                    profile.key_facts.append(fact)

            # Track topic covered
            topic = data.get("topic_covered", "")
            if topic:
                profile.topics_covered.add(topic)

            logger.debug(f"Profile updated at turn {profile.current_turn}")
            return profile

        except Exception as e:
            logger.error(f"Failed to update profile: {e}")
            return profile

    def to_context_string(self, profile: CandidateProfile) -> str:
        """Convert profile to prompt-injectable context string."""
        if not profile or not any([
            profile.verified_skills,
            profile.identified_gaps,
            profile.strengths
        ]):
            return ""

        sections = []

        # Verified skills
        if profile.verified_skills:
            verified = [
                f"{skill} (depth: {data['depth']}/5)"
                for skill, data in profile.verified_skills.items()
                if data.get("depth", 0) >= 3
            ]
            if verified:
                sections.append(f"VERIFIED SKILLS: {', '.join(verified)}")

        # Gaps to probe
        if profile.identified_gaps:
            sections.append(f"GAPS TO PROBE: {', '.join(profile.identified_gaps[:5])}")

        # Red flags
        if profile.red_flags:
            flags = [f["detail"] for f in profile.red_flags[:3]]
            sections.append(f"CONCERNS: {'; '.join(flags)}")

        # Strengths
        if profile.strengths:
            sections.append(f"STRENGTHS: {', '.join(profile.strengths[:3])}")

        # Topics covered
        if profile.topics_covered:
            sections.append(f"TOPICS COVERED (DO NOT REPEAT): {', '.join(list(profile.topics_covered)[:10])}")

        # Performance trend
        if len(profile.performance_trajectory) >= 3:
            recent = profile.performance_trajectory[-3:]
            avg = sum(recent) / len(recent)
            trend = "improving" if recent[-1] > recent[0] else "declining" if recent[-1] < recent[0] else "stable"
            sections.append(f"PERFORMANCE: {trend} (avg: {avg:.0f}/100)")

        return "\n".join(sections)

    def get_suggested_focus(self, profile: CandidateProfile) -> List[str]:
        """Get suggested areas to focus on based on profile."""
        suggestions = []

        # Unverified skills from resume
        unverified = [
            skill for skill, data in profile.verified_skills.items()
            if data.get("depth", 0) < 2
        ]
        if unverified:
            suggestions.append(f"Verify claimed skills: {', '.join(unverified[:3])}")

        # Gaps to explore
        if profile.identified_gaps:
            suggestions.append(f"Probe gaps: {', '.join(profile.identified_gaps[:2])}")

        # Low scores need follow-up
        if profile.performance_trajectory:
            low_turns = [
                i + 1 for i, score in enumerate(profile.performance_trajectory)
                if score < 50
            ]
            if low_turns:
                suggestions.append(f"Follow up on weak answers from turns: {low_turns[-3:]}")

        return suggestions


# Singleton instance
candidate_profile_manager = CandidateProfileManager()
