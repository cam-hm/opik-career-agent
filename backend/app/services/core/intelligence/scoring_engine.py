"""
Answer Scoring Engine.

Scores candidate answers in real-time using multiple dimensions.
Provides feedback, follow-up suggestions, and competency mapping.
"""
import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from google import genai
from jinja2 import Template
from pathlib import Path
from config.settings import get_settings

logger = logging.getLogger("scoring-engine")


@dataclass
class AnswerScore:
    """Detailed scoring result for a candidate answer."""
    # Overall score (0-100)
    overall: float

    # Dimension scores (0-100)
    relevance: float  # Did they answer the question?
    depth: float  # How substantive and detailed?
    technical_accuracy: float  # Are claims technically correct?
    communication: float  # Clear and structured?

    # Competency mapping
    dimension: str  # Primary competency tested (e.g., "system_design", "leadership")

    # Feedback
    feedback: str  # Brief explanation of the score
    follow_up_needed: bool  # Should we dig deeper?
    suggested_follow_up: Optional[str]  # What to ask next

    # Metadata
    confidence: float  # Model's confidence in this scoring (0-1)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ScoringEngine:
    """
    Real-time answer scoring using AI.
    Evaluates answers across multiple dimensions and maps to competencies.
    """

    SCORING_TEMPLATE = """You are an expert interview evaluator. Score this answer objectively.

**Interview Context:**
- Stage: {stage_type}
- Target Role: {job_role}

**Question Asked:**
{question}

**Candidate's Answer:**
{answer}

**Additional Context:**
{context}

Evaluate on these dimensions (0-100 scale):
1. **Relevance**: Did they directly answer the question asked?
2. **Depth**: How substantive and detailed was the response?
3. **Technical Accuracy**: Are claims and statements technically correct? (N/A if non-technical)
4. **Communication**: Was the answer clear, structured, and concise?

Determine the PRIMARY competency dimension being tested:
- technical_depth (algorithms, system_design, code_quality, architecture)
- communication (clarity, structure, articulation)
- problem_solving (analysis, methodology, edge_cases)
- leadership (influence, decision_making, conflict_resolution)
- adaptability (learning, flexibility, growth_mindset)

Return JSON:
{{
    "overall": 75,
    "relevance": 80,
    "depth": 70,
    "technical_accuracy": 75,
    "communication": 80,
    "dimension": "technical_depth",
    "feedback": "Good high-level answer but lacked specific implementation details",
    "follow_up_needed": true,
    "suggested_follow_up": "Ask how they would handle failure scenarios",
    "confidence": 0.85
}}

Be objective. A score of 50 is average. Below 40 is weak. Above 80 is strong."""

    def __init__(self):
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.GOOGLE_API_KEY)
        self.model = self.settings.SHADOW_MODEL  # Use fast model for speed

    async def score_answer(
        self,
        question: str,
        answer: str,
        stage_type: str,
        job_role: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AnswerScore:
        """
        Score a candidate's answer using AI evaluation.

        Args:
            question: The question that was asked
            answer: The candidate's response
            stage_type: Interview stage (hr, technical, behavioral)
            job_role: Target job role
            context: Additional context (profile, previous answers, etc.)

        Returns:
            AnswerScore with detailed scoring and feedback
        """
        # Handle empty or very short answers
        if not answer or len(answer.strip()) < 10:
            return AnswerScore(
                overall=20.0,
                relevance=10.0,
                depth=10.0,
                technical_accuracy=50.0,
                communication=30.0,
                dimension="communication",
                feedback="Answer was too brief or empty",
                follow_up_needed=True,
                suggested_follow_up="Could you elaborate on that?",
                confidence=0.9
            )

        try:
            # Build context string
            context_str = ""
            if context:
                if context.get("profile"):
                    context_str += f"Candidate Profile: {json.dumps(context['profile'], indent=2)[:500]}\n"
                if context.get("previous_scores"):
                    avg = sum(context["previous_scores"]) / len(context["previous_scores"])
                    context_str += f"Average score so far: {avg:.1f}/100\n"

            prompt = self.SCORING_TEMPLATE.format(
                stage_type=stage_type,
                job_role=job_role,
                question=question,
                answer=answer[:2000],
                context=context_str or "None"
            )

            start_time = time.time()

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )

            latency = (time.time() - start_time) * 1000
            logger.debug(f"Scoring completed in {latency:.0f}ms")

            data = json.loads(response.text)

            return AnswerScore(
                overall=float(data.get("overall", 50)),
                relevance=float(data.get("relevance", 50)),
                depth=float(data.get("depth", 50)),
                technical_accuracy=float(data.get("technical_accuracy", 50)),
                communication=float(data.get("communication", 50)),
                dimension=data.get("dimension", "general"),
                feedback=data.get("feedback", ""),
                follow_up_needed=data.get("follow_up_needed", False),
                suggested_follow_up=data.get("suggested_follow_up"),
                confidence=float(data.get("confidence", 0.7))
            )

        except Exception as e:
            logger.error(f"Scoring failed: {e}")
            # Return neutral score on error
            return AnswerScore(
                overall=50.0,
                relevance=50.0,
                depth=50.0,
                technical_accuracy=50.0,
                communication=50.0,
                dimension="general",
                feedback="Unable to score (system error)",
                follow_up_needed=False,
                suggested_follow_up=None,
                confidence=0.0
            )

    async def batch_score(
        self,
        qa_pairs: List[Dict[str, str]],
        stage_type: str,
        job_role: str
    ) -> List[AnswerScore]:
        """
        Score multiple Q&A pairs (for end-of-session analysis).

        Args:
            qa_pairs: List of {"question": ..., "answer": ...}
            stage_type: Interview stage
            job_role: Target job role

        Returns:
            List of AnswerScore objects
        """
        scores = []
        for pair in qa_pairs:
            score = await self.score_answer(
                question=pair.get("question", ""),
                answer=pair.get("answer", ""),
                stage_type=stage_type,
                job_role=job_role
            )
            scores.append(score)
        return scores

    def compute_aggregate_score(self, scores: List[AnswerScore]) -> Dict[str, Any]:
        """
        Compute aggregate statistics from multiple answer scores.

        Args:
            scores: List of AnswerScore objects

        Returns:
            Aggregate statistics
        """
        if not scores:
            return {"overall_avg": 0, "dimension_scores": {}}

        # Overall average
        overall_avg = sum(s.overall for s in scores) / len(scores)

        # Per-dimension averages
        dimensions = {}
        for score in scores:
            dim = score.dimension
            if dim not in dimensions:
                dimensions[dim] = []
            dimensions[dim].append(score.overall)

        dimension_scores = {
            dim: sum(vals) / len(vals)
            for dim, vals in dimensions.items()
        }

        # Communication average (always tracked)
        comm_avg = sum(s.communication for s in scores) / len(scores)

        # Trend analysis
        if len(scores) >= 3:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            first_avg = sum(s.overall for s in first_half) / len(first_half)
            second_avg = sum(s.overall for s in second_half) / len(second_half)
            trend = "improving" if second_avg > first_avg + 5 else \
                    "declining" if second_avg < first_avg - 5 else "stable"
        else:
            trend = "insufficient_data"

        return {
            "overall_avg": round(overall_avg, 1),
            "dimension_scores": {k: round(v, 1) for k, v in dimension_scores.items()},
            "communication_avg": round(comm_avg, 1),
            "trend": trend,
            "sample_size": len(scores),
            "high_scores": len([s for s in scores if s.overall >= 80]),
            "low_scores": len([s for s in scores if s.overall < 50])
        }


# Singleton instance
scoring_engine = ScoringEngine()
