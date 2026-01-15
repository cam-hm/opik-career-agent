"""
Domain-Specific Tracers.

High-level tracing interfaces for each AI component in the system.
Provides specialized methods tailored to each component's needs.
"""
import logging
from typing import Any, Dict, List, Optional

from .decorators import (
    get_current_trace_id,
    log_turn_event,
    trace_llm_call,
    traced_session,
    traced_span,
)
from .models import SpanType, TraceMetadata

logger = logging.getLogger("observability.tracers")


class InterviewTracer:
    """
    Tracer for interview sessions.

    Handles session-level tracing and per-turn metrics.
    """

    async def start_session(
        self,
        session_id: str,
        stage_type: str,
        job_role: str,
        language: str = "en",
        **metadata
    ):
        """
        Start tracing an interview session.

        Returns a context manager for the session trace.
        """
        return traced_session(
            session_id=session_id,
            stage_type=stage_type,
            job_role=job_role,
            language=language,
            **metadata
        )

    async def log_turn(
        self,
        turn_index: int,
        role: str,
        content: str,
        response_time_ms: float = None
    ):
        """Log a conversation turn."""
        await log_turn_event(
            turn_index=turn_index,
            role=role,
            content=content,
            response_time_ms=response_time_ms
        )

    async def log_greeting(self, greeting_text: str):
        """Log the initial greeting."""
        from .service import observability_service

        await observability_service.record_metric(
            metric_name="initial_greeting",
            value=1.0,
            trace_id=get_current_trace_id(),
            metadata={"greeting_length": len(greeting_text)}
        )


class ShadowMonitorTracer:
    """
    Tracer for shadow monitor analysis.

    Tracks background LLM analysis calls and interventions.
    """

    @staticmethod
    def trace_analysis():
        """
        Decorator for shadow monitor analyze method.

        Usage:
            @ShadowMonitorTracer.trace_analysis()
            async def analyze(self, transcript_history, job_role, stage_type):
                ...
        """
        return trace_llm_call(
            component="shadow_monitor",
            capture_input=True,
            capture_output=True
        )

    async def log_intervention(
        self,
        intervention_type: str,
        intervention_text: str
    ):
        """Log when shadow monitor injects a runtime directive."""
        from .service import observability_service

        await observability_service.record_metric(
            metric_name="shadow_intervention",
            value=1.0,
            trace_id=get_current_trace_id(),
            metadata={
                "intervention_type": intervention_type,
                "intervention_length": len(intervention_text)
            }
        )


class AnalysisTracer:
    """
    Tracer for analysis service operations.

    Tracks resume analysis, feedback generation, and evaluations.
    """

    @staticmethod
    def trace_resume_analysis():
        """Decorator for resume analysis."""
        return trace_llm_call(
            component="resume_analysis",
            capture_input=True,
            capture_output=True
        )

    @staticmethod
    def trace_feedback_generation():
        """Decorator for feedback generation."""
        return trace_llm_call(
            component="feedback_generation",
            capture_input=True,
            capture_output=True
        )

    @staticmethod
    def trace_jd_generation():
        """Decorator for job description generation."""
        return trace_llm_call(
            component="jd_generation",
            capture_input=True,
            capture_output=True
        )

    async def log_analysis_result(
        self,
        analysis_type: str,
        score: float,
        metadata: Dict[str, Any] = None
    ):
        """Log analysis result metrics."""
        from .service import observability_service

        await observability_service.record_metric(
            metric_name=f"analysis_{analysis_type}_score",
            value=score,
            trace_id=get_current_trace_id(),
            metadata=metadata or {}
        )


class EvaluationTracer:
    """
    Tracer for evaluation operations.

    Tracks GEval and other evaluation metric computations.
    """

    async def start_evaluation(
        self,
        session_id: str,
        evaluator: str,
        transcript_length: int
    ):
        """Start tracing an evaluation."""
        return traced_span(
            name=f"evaluation_{evaluator}",
            span_type=SpanType.EVALUATION,
            input_data={
                "session_id": session_id,
                "transcript_length": transcript_length
            },
            component="evaluation"
        )

    async def log_metric_score(
        self,
        metric_name: str,
        score: float,
        reason: str = None
    ):
        """Log individual metric score."""
        from .service import observability_service

        await observability_service.record_metric(
            metric_name=f"eval_{metric_name}",
            value=score,
            trace_id=get_current_trace_id(),
            metadata={"reason": reason} if reason else {}
        )


# Singleton instances for convenience
interview_tracer = InterviewTracer()
shadow_monitor_tracer = ShadowMonitorTracer()
analysis_tracer = AnalysisTracer()
evaluation_tracer = EvaluationTracer()
