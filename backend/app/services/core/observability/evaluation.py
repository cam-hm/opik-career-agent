"""
Evaluation Engine.

Handles post-session evaluation using LLM-as-a-Judge (GEval)
and real-time basic metrics calculation.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from config.settings import get_settings

from .models import EvaluationResult, EvaluationScore

logger = logging.getLogger("observability.evaluation")


def _clean_json_response(text: str) -> str:
    """
    Clean markdown code blocks from LLM JSON response.

    Handles common formats:
    - ```json ... ```
    - ``` ... ```
    - Plain JSON
    """
    text = text.strip()
    if text.startswith("```"):
        # Remove opening fence
        text = text.split("```", 1)[1]
        if text.startswith("json"):
            text = text[4:]
        # Remove closing fence if present
        if "```" in text:
            text = text.split("```")[0]
    elif text.endswith("```"):
        text = text[:-3]
    return text.strip()


class EvaluationEngine:
    """
    Engine for computing evaluation metrics.

    Supports:
    - Real-time basic metrics (turn count, word counts, latency)
    - Post-session GEval metrics (Confidence, Clarity, Relevance)
    - LLM-as-a-Judge evaluation using Gemini
    """

    def __init__(self):
        self.settings = get_settings()

    async def compute_basic_metrics(
        self,
        transcript: List[Dict[str, str]]
    ) -> Dict[str, float]:
        """
        Compute basic metrics from transcript.

        Args:
            transcript: List of {"role": str, "content": str}

        Returns:
            Dict with metric values
        """
        if not transcript:
            return {}

        user_turns = [t for t in transcript if t.get("role") == "user"]
        assistant_turns = [t for t in transcript if t.get("role") == "assistant"]

        # Word counts
        user_words = sum(len(t.get("content", "").split()) for t in user_turns)
        assistant_words = sum(len(t.get("content", "").split()) for t in assistant_turns)

        # Average message lengths
        avg_user_length = user_words / len(user_turns) if user_turns else 0
        avg_assistant_length = assistant_words / len(assistant_turns) if assistant_turns else 0

        return {
            "total_turns": len(transcript),
            "user_turns": len(user_turns),
            "assistant_turns": len(assistant_turns),
            "user_total_words": user_words,
            "assistant_total_words": assistant_words,
            "avg_user_words_per_turn": avg_user_length,
            "avg_assistant_words_per_turn": avg_assistant_length,
            "conversation_ratio": user_words / assistant_words if assistant_words > 0 else 0
        }

    async def evaluate_session_geval(
        self,
        session_id: str,
        transcript: List[Dict[str, str]],
        metadata: Dict[str, Any] = None,
        trace_id: Optional[str] = None
    ) -> Optional[EvaluationResult]:
        """
        Run GEval evaluation on a complete interview session.

        Uses Gemini to evaluate:
        - Confidence: How confident was the candidate?
        - Clarity: How clearly did they communicate?
        - Relevance: How relevant were their answers?
        - Technical Depth: How technically sound? (for technical stages)

        Args:
            session_id: Session identifier
            transcript: Complete conversation transcript
            metadata: Additional context (stage_type, job_role, etc.)

        Returns:
            EvaluationResult with scores and summary
        """
        if not transcript or len(transcript) < 2:
            logger.warning(f"Insufficient transcript for evaluation: {len(transcript)} turns")
            return None

        try:
            from google import genai

            client = genai.Client(api_key=self.settings.GOOGLE_API_KEY)

            # Format transcript for evaluation
            transcript_text = "\n".join([
                f"{'Interviewer' if t.get('role') == 'assistant' else 'Candidate'}: {t.get('content', '')}"
                for t in transcript
            ])

            stage_type = metadata.get("stage_type", "general") if metadata else "general"
            job_role = metadata.get("job_role", "General") if metadata else "General"

            # Build evaluation prompt
            prompt = f"""You are an expert interview evaluator. Analyze this interview transcript and provide scores.

Interview Context:
- Stage: {stage_type}
- Target Role: {job_role}

Transcript:
{transcript_text}

Evaluate the CANDIDATE's performance on these criteria (score 0.0 to 1.0):

1. **Confidence** (0-1): How confident did the candidate appear?
   - 0.0 = Very hesitant, lots of filler words, uncertain
   - 0.5 = Moderate confidence, some hesitation
   - 1.0 = Very confident, clear, decisive responses

2. **Clarity** (0-1): How clearly did the candidate communicate?
   - 0.0 = Rambling, unclear, hard to follow
   - 0.5 = Reasonably clear with some confusion
   - 1.0 = Crystal clear, well-structured responses

3. **Relevance** (0-1): How relevant were the answers to the questions?
   - 0.0 = Off-topic, didn't answer questions
   - 0.5 = Partially relevant, some tangents
   - 1.0 = Directly addressed each question

4. **Depth** (0-1): How substantive were the responses?
   - 0.0 = Superficial, one-word answers
   - 0.5 = Adequate detail
   - 1.0 = Rich, detailed responses with examples

Return JSON only (no markdown):
{{
    "confidence": 0.75,
    "confidence_reason": "Brief explanation",
    "clarity": 0.80,
    "clarity_reason": "Brief explanation",
    "relevance": 0.85,
    "relevance_reason": "Brief explanation",
    "depth": 0.70,
    "depth_reason": "Brief explanation",
    "overall_summary": "2-3 sentence overall assessment",
    "overall_score": 0.77
}}
"""

            response = await client.aio.models.generate_content(
                model=self.settings.GEMINI_MODEL,
                contents=prompt
            )

            # Parse response using helper
            response_text = _clean_json_response(response.text)
            result_data = json.loads(response_text)

            # Build evaluation result
            scores = [
                EvaluationScore(
                    metric_name="confidence",
                    score=float(result_data.get("confidence", 0)),
                    reason=result_data.get("confidence_reason")
                ),
                EvaluationScore(
                    metric_name="clarity",
                    score=float(result_data.get("clarity", 0)),
                    reason=result_data.get("clarity_reason")
                ),
                EvaluationScore(
                    metric_name="relevance",
                    score=float(result_data.get("relevance", 0)),
                    reason=result_data.get("relevance_reason")
                ),
                EvaluationScore(
                    metric_name="depth",
                    score=float(result_data.get("depth", 0)),
                    reason=result_data.get("depth_reason")
                )
            ]

            evaluation = EvaluationResult(
                session_id=session_id,
                trace_id=trace_id,  # Link to Opik trace for dashboard
                evaluator="geval",
                scores=scores,
                overall_score=float(result_data.get("overall_score", 0)),
                summary=result_data.get("overall_summary"),
                metadata={
                    "stage_type": stage_type,
                    "job_role": job_role,
                    "transcript_turns": len(transcript)
                }
            )

            logger.info(f"GEval completed for {session_id}: overall={evaluation.overall_score:.2f}")
            return evaluation

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GEval response: {e}")
            return None
        except Exception as e:
            logger.error(f"GEval evaluation failed: {e}")
            return None

    async def evaluate_answer_relevance(
        self,
        question: str,
        answer: str,
        context: str = None
    ) -> Optional[EvaluationScore]:
        """
        Evaluate relevance of a single answer to its question.

        Useful for real-time per-turn evaluation.

        Args:
            question: The interviewer's question
            answer: The candidate's answer
            context: Optional context (job description, etc.)

        Returns:
            EvaluationScore for relevance
        """
        try:
            from google import genai

            client = genai.Client(api_key=self.settings.GOOGLE_API_KEY)

            prompt = f"""Rate how relevant this answer is to the question (0.0 to 1.0).

Question: {question}
Answer: {answer}
{f"Context: {context}" if context else ""}

Return JSON only:
{{"relevance": 0.85, "reason": "Brief explanation"}}
"""

            response = await client.aio.models.generate_content(
                model=self.settings.GEMINI_MODEL,
                contents=prompt
            )

            # Parse response using helper
            response_text = _clean_json_response(response.text)
            result = json.loads(response_text)

            return EvaluationScore(
                metric_name="answer_relevance",
                score=float(result.get("relevance", 0)),
                reason=result.get("reason")
            )

        except Exception as e:
            logger.error(f"Answer relevance evaluation failed: {e}")
            return None


# Singleton instance
evaluation_engine = EvaluationEngine()


async def evaluate_session_post_completion(
    session_id: str,
    transcript: List[Dict[str, str]],
    metadata: Dict[str, Any] = None,
    trace_id: Optional[str] = None
) -> Optional[EvaluationResult]:
    """
    Convenience function for post-session evaluation.

    Runs GEval and submits results to observability service.
    """
    from .service import observability_service
    from .decorators import get_current_trace_id

    # Use provided trace_id or get from context
    effective_trace_id = trace_id or get_current_trace_id()

    # Run GEval with trace_id
    result = await evaluation_engine.evaluate_session_geval(
        session_id=session_id,
        transcript=transcript,
        metadata=metadata,
        trace_id=effective_trace_id
    )

    # Submit to observability
    if result:
        await observability_service.submit_evaluation(result)

    return result
