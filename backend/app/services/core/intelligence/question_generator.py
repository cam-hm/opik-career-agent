"""
Dynamic Question Generator.

Generates contextual interview questions based on:
- Resume and job description analysis
- Current difficulty level
- Topics already covered
- Identified gaps and weaknesses
"""
import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from google import genai
from pathlib import Path

from app.services.core.intelligence.competency_evaluator import competency_evaluator
from app.services.core.intelligence.difficulty_adapter import DifficultyLevel
from config.settings import get_settings

logger = logging.getLogger("question-generator")


@dataclass
class GeneratedQuestion:
    """A dynamically generated interview question."""
    question: str
    target_competency: str
    difficulty: str
    context_used: str  # What triggered this question
    topic: str  # Topic category
    follow_up_hints: List[str]  # Potential follow-ups

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class QuestionGenerator:
    """
    Generates contextual interview questions using AI.

    Questions are tailored to:
    - The specific candidate (resume, claimed experience)
    - Current interview stage and competency focus
    - Adaptive difficulty level
    - Topics not yet covered
    """

    QUESTION_GENERATION_TEMPLATE = """You are an expert interviewer generating highly contextual questions.

**Interview Context:**
- Role: {job_role}
- Stage: {stage_type}
- Current Difficulty: {difficulty}
- Focus Competencies: {focus_competencies}

**Candidate Information:**
{resume_excerpt}

**Job Requirements:**
{jd_excerpt}

**Already Covered Topics (DO NOT REPEAT):**
{topics_covered}

**Identified Gaps to Probe:**
{gaps}

**Recent Performance:**
{performance_summary}

Generate {num_questions} interview questions that:
1. Are SPECIFIC to THIS candidate (reference actual projects/skills from resume if available)
2. Test the focus competencies for this stage
3. Match the {difficulty} difficulty level
4. DO NOT repeat any topics already covered
5. Probe identified gaps if any exist

Difficulty Guidelines:
- foundational: Basic concepts, definitions, simple examples
- intermediate: Applied knowledge, common patterns, multi-step scenarios
- advanced: Edge cases, trade-offs, complex integrations
- expert: Architectural decisions, innovation, strategic thinking

Return JSON array:
[
  {{
    "question": "The actual question to ask",
    "target_competency": "technical_depth",
    "difficulty": "{difficulty}",
    "context_used": "What from the context inspired this question",
    "topic": "Topic category (e.g., 'system_design', 'leadership')",
    "follow_up_hints": ["Possible follow-up 1", "Possible follow-up 2"]
  }}
]

IMPORTANT: Questions must be specific and actionable, not generic. Bad: "Tell me about yourself". Good: "In your role at CompanyX, you mentioned scaling the payment system to 10K TPS. Walk me through the architecture decisions you made.\"
"""

    FOLLOW_UP_TEMPLATE = """Generate a targeted follow-up question.

**Original Question:** {original_question}

**Candidate's Answer:** {answer}

**Answer Score:** {score}/100

**Strategy:** {strategy}
{weakness_context}

Based on the strategy, generate ONE precise follow-up question that:
- Builds on what was just discussed
- Probes deeper or clarifies weakness
- Maintains conversational flow

Return JSON:
{{
    "question": "The follow-up question",
    "rationale": "Why this follow-up is appropriate"
}}"""

    def __init__(self):
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.GOOGLE_API_KEY)
        self.model = self.settings.GEMINI_MODEL  # Use main model for quality

    async def generate_questions(
        self,
        resume_text: str,
        job_description: str,
        stage_type: str,
        job_role: str,
        difficulty: DifficultyLevel,
        topics_covered: List[str],
        gaps: List[str],
        performance_summary: str = "",
        num_questions: int = 3
    ) -> List[GeneratedQuestion]:
        """
        Generate contextual interview questions.

        Args:
            resume_text: Candidate's resume
            job_description: Job requirements
            stage_type: Interview stage
            job_role: Target role
            difficulty: Current difficulty level
            topics_covered: Topics to avoid
            gaps: Identified gaps to probe
            performance_summary: Recent performance context
            num_questions: Number of questions to generate

        Returns:
            List of GeneratedQuestion objects
        """
        try:
            # Get competency focus for stage
            focus_competencies = competency_evaluator.get_stage_focus(stage_type)

            prompt = self.QUESTION_GENERATION_TEMPLATE.format(
                job_role=job_role,
                stage_type=stage_type,
                difficulty=difficulty.value,
                focus_competencies=", ".join(focus_competencies),
                resume_excerpt=resume_text[:2000] if resume_text else "Not provided",
                jd_excerpt=job_description[:1500] if job_description else "Not provided",
                topics_covered=", ".join(topics_covered) if topics_covered else "None yet",
                gaps=", ".join(gaps) if gaps else "None identified",
                performance_summary=performance_summary or "No data yet",
                num_questions=num_questions
            )

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )

            data = json.loads(response.text)

            questions = []
            for q in data:
                questions.append(GeneratedQuestion(
                    question=q.get("question", ""),
                    target_competency=q.get("target_competency", "general"),
                    difficulty=q.get("difficulty", difficulty.value),
                    context_used=q.get("context_used", ""),
                    topic=q.get("topic", "general"),
                    follow_up_hints=q.get("follow_up_hints", [])
                ))

            logger.info(f"Generated {len(questions)} questions for {stage_type} at {difficulty.value}")
            return questions

        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return []

    async def generate_follow_up(
        self,
        original_question: str,
        answer: str,
        score: float,
        weakness_identified: Optional[str] = None
    ) -> Optional[GeneratedQuestion]:
        """
        Generate a targeted follow-up question.

        Args:
            original_question: The question that was asked
            answer: Candidate's response
            score: Score for the answer
            weakness_identified: Specific weakness to probe

        Returns:
            GeneratedQuestion for follow-up, or None
        """
        try:
            # Determine follow-up strategy
            if score < 40:
                strategy = "clarification"
                strategy_desc = "The answer was weak. Ask a simpler, clarifying question to understand their baseline knowledge."
            elif score < 60 and weakness_identified:
                strategy = "gap_probe"
                strategy_desc = f"Probe specifically on the identified weakness: {weakness_identified}"
            elif score >= 80:
                strategy = "depth_increase"
                strategy_desc = "The answer was strong. Go deeper with a more challenging follow-up."
            else:
                strategy = "exploration"
                strategy_desc = "Explore a related aspect of the topic to get a fuller picture."

            weakness_context = f"\nWeakness to probe: {weakness_identified}" if weakness_identified else ""

            prompt = self.FOLLOW_UP_TEMPLATE.format(
                original_question=original_question,
                answer=answer[:1000],
                score=score,
                strategy=strategy_desc,
                weakness_context=weakness_context
            )

            response = await self.client.aio.models.generate_content(
                model=self.settings.SHADOW_MODEL,  # Fast model for follow-ups
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )

            data = json.loads(response.text)

            return GeneratedQuestion(
                question=data.get("question", ""),
                target_competency="follow_up",
                difficulty="contextual",
                context_used=f"Strategy: {strategy}",
                topic="follow_up",
                follow_up_hints=[]
            )

        except Exception as e:
            logger.error(f"Follow-up generation failed: {e}")
            return None

    async def generate_opening_question(
        self,
        stage_type: str,
        job_role: str,
        resume_text: str,
        previous_stage_summary: Optional[str] = None
    ) -> GeneratedQuestion:
        """
        Generate an appropriate opening question for a stage.

        Args:
            stage_type: Interview stage
            job_role: Target role
            resume_text: Candidate resume
            previous_stage_summary: Summary from previous stage if any

        Returns:
            Opening GeneratedQuestion
        """
        try:
            stage_openers = {
                "hr": "Focus on their motivation and career trajectory. Ask about why they're interested in this role.",
                "technical": "Start with their most recent technical project. Ask them to explain their specific contribution.",
                "behavioral": "Open with a leadership or conflict scenario. Ask about a challenging situation they handled.",
                "practice": "Jump straight into a technical topic from their resume."
            }

            context = stage_openers.get(stage_type, stage_openers["practice"])

            prompt = f"""Generate an opening interview question.

Stage: {stage_type}
Role: {job_role}
Context: {context}

Resume excerpt:
{resume_text[:1500] if resume_text else "Not provided"}

{f"Previous stage summary: {previous_stage_summary}" if previous_stage_summary else ""}

The opening question should:
1. Be warm but professional
2. Be specific to this candidate if resume available
3. Set the tone for the stage focus
4. Be a SINGLE question (not multiple bundled together)

Return JSON:
{{
    "question": "The opening question",
    "topic": "topic category"
}}"""

            response = await self.client.aio.models.generate_content(
                model=self.settings.SHADOW_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )

            data = json.loads(response.text)

            return GeneratedQuestion(
                question=data.get("question", "Let's start. Tell me about your most recent project."),
                target_competency="opening",
                difficulty="intermediate",
                context_used="Stage opening",
                topic=data.get("topic", "introduction"),
                follow_up_hints=[]
            )

        except Exception as e:
            logger.error(f"Opening question generation failed: {e}")
            # Fallback
            return GeneratedQuestion(
                question="Let's start with your most recent role. What were your key responsibilities?",
                target_competency="opening",
                difficulty="intermediate",
                context_used="Fallback opener",
                topic="introduction",
                follow_up_hints=[]
            )

    def build_question_bank_prompt(
        self,
        questions: List[GeneratedQuestion]
    ) -> str:
        """
        Build a prompt injection with pre-generated questions.

        Args:
            questions: List of generated questions

        Returns:
            Formatted prompt text for injection
        """
        if not questions:
            return ""

        sections = [
            "PREPARED QUESTIONS (use these as a starting point, adapt as needed):\n"
        ]

        for i, q in enumerate(questions, 1):
            sections.append(
                f"{i}. [{q.difficulty.upper()}] [{q.target_competency}]\n"
                f"   {q.question}\n"
                f"   Context: {q.context_used}\n"
            )
            if q.follow_up_hints:
                sections.append(f"   Follow-ups: {'; '.join(q.follow_up_hints[:2])}\n")

        return "\n".join(sections)


# Singleton instance
question_generator = QuestionGenerator()
