"""
AI Analysis Service.

Handles AI-powered resume analysis and feedback generation using Google Gemini.
Uses centralized config from config package.
"""
import json
import logging
import time
from google import genai
from config.settings import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


async def generate_job_description(job_role: str, language: str = 'en') -> str:
    """Generate a job description for a given role."""
    
    lang_instruction = "Respond in English."
    if language == 'vi':
        lang_instruction = "Respond in Vietnamese. Keep technical terms in English."

    prompt = f"""
    Generate a concise but comprehensive Job Description for the role of: {job_role}.
    Include Key Responsibilities and Required Skills.
    Keep it under 300 words.
    {lang_instruction}
    """
    
    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating JD: {e}")
        return f"Standard Job Description for {job_role}"


async def analyze_resume(resume_text: str, job_description: str = None) -> dict:
    """
    Analyze a resume against a job description.
    
    Returns:
        dict with summary, strengths, weaknesses, suggested_questions, overall_score
    """
    model = "gemini-2.0-flash-exp" # Force new model or use settings.GEMINI_MODEL if updated
    # Note: genai v1.0 usually works best with models/gemini-1.5-flash or similar
    
    jd_context = ""
    if job_description:
        jd_context = f"\nTarget Job Description:\n{job_description}\n"
    
    prompt = f"""
    You are an expert professional interviewer. Analyze the following resume text.
    
    Resume Text:
    {resume_text}
    {jd_context}
    
    CRITICAL SCORING RULES:
    1. **Skill Alignment**: If core competencies do NOT match the JD, score MUST be below 50.
    2. **Experience Match**: If significantly underqualified, score MUST be below 60.
    3. **Be Strict**: Do not give high scores for "potential" if key requirements are missing.
    
    Return JSON format (no markdown):
    {{
        "summary": "Brief professional summary (max 2 sentences)",
        "strengths": ["Strength 1", "Strength 2", "Strength 3"],
        "weaknesses": ["Weakness 1", "Weakness 2"],
        "overall_score": 85,
        "suggested_questions": [
            "Question 1 (Technical)",
            "Question 2 (Experience)",
            "Question 3 (Behavioral)"
        ]
    }}
    """
    
    try:
        from app.services.core.observability import observability_service, get_current_trace_id

        start_time = time.time()

        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        latency_ms = (time.time() - start_time) * 1000

        # Log to Opik (provider handles truncation)
        await observability_service.log_llm_call(
            trace_id=get_current_trace_id(),
            model=settings.GEMINI_MODEL,
            input_prompt=prompt,  # Full prompt
            output_response=response.text,  # Full response
            metadata={
                "component": "resume_analysis",
                "has_jd": bool(job_description),
                "resume_length": len(resume_text),
                "prompt_length": len(prompt)
            },
            latency_ms=latency_ms
        )

        text = _clean_json_response(response.text)
        result = json.loads(text)

        # Log resume analysis score as metric
        overall_score = result.get("overall_score", 0)
        await observability_service.record_metric(
            metric_name="resume_analysis_score",
            value=float(overall_score) / 100.0,  # Normalize to 0-1
            trace_id=get_current_trace_id(),
            metadata={
                "raw_score": overall_score,
                "strengths_count": len(result.get("strengths", [])),
                "weaknesses_count": len(result.get("weaknesses", [])),
                "has_jd": bool(job_description)
            }
        )
        logger.info(f"📊 Resume analysis score logged: {overall_score}")

        return result
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        return {
            "summary": "Could not analyze resume.",
            "strengths": [],
            "weaknesses": [],
            "suggested_questions": [],
            "overall_score": 0
        }


async def _check_feedback_hallucination(
    feedback: dict,
    transcript_text: str,
    resume_text: str = None,
    job_description: str = None
) -> float | None:
    """
    Check if AI-generated feedback contains hallucinated information.

    Only runs when we have ground truth (resume/JD) to compare against.
    Returns score 0-1 where 1 = no hallucination, 0 = severe hallucination.
    """
    context_parts = []
    if resume_text:
        context_parts.append(f"RESUME:\n{resume_text[:2000]}")
    if job_description:
        context_parts.append(f"JOB DESCRIPTION:\n{job_description[:1000]}")

    if not context_parts:
        return None

    context = "\n\n".join(context_parts)
    feedback_text = json.dumps(feedback, ensure_ascii=False)

    prompt = f"""You are a hallucination detector. Check if the AI-generated feedback contains any claims NOT supported by the provided context.

CONTEXT (Ground Truth):
{context}

TRANSCRIPT:
{transcript_text[:2000]}

AI FEEDBACK TO CHECK:
{feedback_text}

Evaluate:
1. Does the feedback make claims about the candidate's skills/experience not mentioned in resume or transcript?
2. Does it reference specific details that don't exist in the provided context?
3. Does it attribute statements to the candidate they didn't make?

Return JSON only:
{{"hallucination_score": 0.95, "reason": "Brief explanation", "flagged_claims": ["claim1 if any"]}}

Score guide:
- 1.0 = All claims grounded in context
- 0.7-0.9 = Minor extrapolations but reasonable
- 0.4-0.6 = Some unsupported claims
- 0.0-0.3 = Significant hallucination
"""

    try:
        from app.services.core.observability import observability_service, get_current_trace_id

        start_time = time.time()

        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        latency_ms = (time.time() - start_time) * 1000

        text = _clean_json_response(response.text)
        result = json.loads(text)

        hallucination_score = float(result.get("hallucination_score", 1.0))

        # Log to Opik (provider handles truncation)
        await observability_service.log_llm_call(
            trace_id=get_current_trace_id(),
            model=settings.GEMINI_MODEL,
            input_prompt=prompt,  # Full prompt
            output_response=response.text,  # Full response
            metadata={
                "component": "hallucination_check",
                "has_resume": bool(resume_text),
                "has_jd": bool(job_description),
                "feedback_length": len(feedback_text),
                "prompt_length": len(prompt)
            },
            latency_ms=latency_ms
        )

        # Record as metric
        await observability_service.record_metric(
            metric_name="feedback_hallucination_score",
            value=hallucination_score,
            trace_id=get_current_trace_id(),
            metadata={
                "reason": result.get("reason", ""),
                "flagged_count": len(result.get("flagged_claims", []))
            }
        )

        logger.info(f"📊 Hallucination check: score={hallucination_score:.2f}")
        return hallucination_score

    except Exception as e:
        logger.error(f"Hallucination check failed: {e}")
        return None


async def generate_feedback(
    transcript: list,
    resume_text: str = None,
    job_description: str = None
) -> dict:
    """
    Generate interview feedback from transcript.

    Args:
        transcript: List of {"role": str, "content": str} messages
        resume_text: Optional resume text for hallucination checking
        job_description: Optional JD for hallucination checking

    Returns:
        dict with score, summary, pros, cons, feedback
    """
    # model = genai.GenerativeModel(settings.GEMINI_MODEL) # Removed deprecated call
    
    transcript_text = ""
    for msg in transcript:
        role = "Interviewer" if msg.get("role") == "assistant" else "Candidate"
        transcript_text += f"{role}: {msg.get('content')}\n"
    
    prompt = f"""
    You are an expert interviewer. Review this transcript and provide feedback.
    
    Transcript:
    {transcript_text}
    
    CRITICAL INSTRUCTION:
    - If candidate did not speak or responses are meaningless, return score 0.
    - Be strict with scoring. No high scores without evidence of skill.
    
    Return JSON format (no markdown):
    {{
        "score": 0,
        "summary": "Overall assessment",
        "pros": ["Good point 1", "Good point 2"],
        "cons": ["Improvement area 1", "Improvement area 2"],
        "feedback": "Detailed feedback and advice"
    }}
    """
    
    try:
        from app.services.core.observability import observability_service, get_current_trace_id

        start_time = time.time()

        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        latency_ms = (time.time() - start_time) * 1000

        # Log to Opik (provider handles truncation)
        await observability_service.log_llm_call(
            trace_id=get_current_trace_id(),
            model=settings.GEMINI_MODEL,
            input_prompt=prompt,  # Full prompt
            output_response=response.text,  # Full response
            metadata={
                "component": "feedback_generation",
                "transcript_length": len(transcript),
                "transcript_turns": len(transcript),
                "prompt_length": len(prompt)
            },
            latency_ms=latency_ms
        )

        text = _clean_json_response(response.text)
        result = json.loads(text)

        # Log feedback score as metric
        feedback_score = result.get("score", 0)
        await observability_service.record_metric(
            metric_name="interview_feedback_score",
            value=float(feedback_score) / 100.0,  # Normalize to 0-1
            trace_id=get_current_trace_id(),
            metadata={
                "raw_score": feedback_score,
                "pros_count": len(result.get("pros", [])),
                "cons_count": len(result.get("cons", [])),
                "transcript_turns": len(transcript)
            }
        )
        logger.info(f"📊 Feedback score logged: {feedback_score}")

        # Run hallucination check if we have context to compare against
        if resume_text or job_description:
            hallucination_score = await _check_feedback_hallucination(
                feedback=result,
                transcript_text=transcript_text,
                resume_text=resume_text,
                job_description=job_description
            )
            if hallucination_score is not None:
                result["hallucination_score"] = hallucination_score

        return result
    except Exception as e:
        logger.error(f"Error generating feedback: {e}")
        return {
            "score": 0,
            "summary": "Could not generate feedback.",
            "pros": [],
            "cons": [],
            "feedback": "Error analyzing transcript."
        }


def _clean_json_response(text: str) -> str:
    """Clean markdown code blocks from AI response."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()
