"""
Resume Probe Skill.

Analyzes resume context to generate specific verification questions.
Stage-aware: Uses different strategies based on interview stage (HR, Technical, Behavioral).
"""
from typing import Dict, Any
import random
from app.services.core.intelligence.skills import BaseSkill


class ResumeProbe(BaseSkill):
    """Stage-aware resume probing skill with separate strategy pools per stage."""

    # HR Stage: Focus on career trajectory, culture fit, soft skills
    HR_STRATEGIES = [
        """
        STRATEGY: THE CHRONOLOGIST
        - Focus on their career trajectory. Ask why they moved from one role to another.
        - Ask how their responsibilities changed over time.
        - If you see a gap > 6 months, ask about it gently.
        - DO NOT ask technical implementation questions.
        """,
        """
        STRATEGY: THE CULTURE FIT
        - Look at their volunteer work or "Interests" section if it exists.
        - Ask how they handle team conflicts based on their past roles.
        - Ask what they learned from their longest-held position.
        - Focus on communication style and team dynamics.
        """,
        """
        STRATEGY: THE RED FLAG HUNTER
        - Look for job hopping patterns (multiple jobs < 1 year).
        - Ask about unexplained gaps in employment.
        - Probe reasons for leaving previous positions.
        - Assess commitment and stability.
        """
    ]

    # Technical Stage: Focus on technical depth, implementation details, trade-offs
    TECHNICAL_STRATEGIES = [
        """
        STRATEGY: THE SKEPTIC
        - Pick 2 specific technical claims and ask: "How exactly did you implement that?"
        - Verify the depth of their most listed technical skill with edge-case questions.
        - Ask about internal workings, not just usage (e.g., "How does X handle memory?").
        - DO NOT ask about career journey or culture fit.
        """,
        """
        STRATEGY: THE PROJECT DIVER
        - Focus deeply on their MOST RECENT technical project.
        - Ask: "What was your specific technical contribution vs the team's?"
        - Ask them to explain a technical trade-off they made and WHY.
        - Probe for real experience vs tutorial knowledge.
        """,
        """
        STRATEGY: THE ARCHITECTURE ANALYST
        - Look for system design or architecture experience in their resume.
        - Ask how they would scale a system they mentioned.
        - Probe database choices, caching strategies, or API design decisions.
        - Focus on technical decision-making rationale.
        """,
        """
        STRATEGY: THE DEBUGGER
        - Ask about the most difficult bug they've solved.
        - Probe their debugging methodology and tools.
        - Ask about production incidents and how they handled them.
        - Focus on problem-solving approach under pressure.
        """
    ]

    # Behavioral Stage: Focus on leadership, conflict resolution, learning
    BEHAVIORAL_STRATEGIES = [
        """
        STRATEGY: THE FAILURE ANALYST
        - Look for leadership or team-lead roles in their history.
        - Ask about a project that did NOT go well and what they learned.
        - Probe for self-awareness and growth from mistakes.
        - DO NOT ask technical implementation details.
        """,
        """
        STRATEGY: THE INFLUENCE MAPPER
        - Focus on roles where they worked cross-functionally.
        - Ask how they influenced decisions without formal authority.
        - Explore conflict resolution patterns in their past roles.
        - Assess leadership potential and collaboration skills.
        """,
        """
        STRATEGY: THE GROWTH TRACKER
        - Compare their early career roles to recent ones.
        - Ask what skills they developed over time.
        - Probe for self-improvement initiatives and learning mindset.
        - Focus on career growth and ambition.
        """
    ]

    # Practice/Default: Mix of strategies for general practice
    PRACTICE_STRATEGIES = [
        """
        STRATEGY: THE WELL-ROUNDED PROBE
        - Ask about their strongest technical skill and verify depth.
        - Ask about a challenging team situation they navigated.
        - Cover both technical competence and soft skills.
        - Keep energy high and provide constructive feedback.
        """
    ]

    def execute(self, context: Dict[str, Any]) -> str:
        resume_text = context.get("resume_text", "")
        stage_type = context.get("stage_type", "hr")

        # If no resume, this skill is useless
        if not resume_text or len(resume_text) < 50:
            return ""

        # Select strategy pool based on stage
        if stage_type == "hr":
            strategies = self.HR_STRATEGIES
        elif stage_type == "technical":
            strategies = self.TECHNICAL_STRATEGIES
        elif stage_type == "behavioral":
            strategies = self.BEHAVIORAL_STRATEGIES
        else:  # practice or unknown
            strategies = self.PRACTICE_STRATEGIES

        selected_strategy = random.choice(strategies)

        prompt_injection = f"""
[SKILL: RESUME DEEP DIVE ACTIVE]
Mode: {self.config.get("mode", "analysis").upper()}
Stage: {stage_type.upper()}

You have reviewed the candidate's resume.
To make the interview feel natural and unique, follow this specific line of inquiry:

{selected_strategy}

IMPORTANT: Stay within your stage's focus area. Do not cross into other stages' territory.

Context from Resume:
{resume_text[:2500]}...
"""
        return prompt_injection
