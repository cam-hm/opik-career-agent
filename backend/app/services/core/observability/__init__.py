"""
Observability Module.

Provides LLM observability, tracing, and evaluation capabilities
using Opik Cloud as the backend.

Usage:

    # Session-level tracing
    from app.services.core.observability import traced_session

    async with traced_session("session_123", stage_type="technical"):
        # All operations within are traced
        await process_interview()

    # LLM call tracing decorator
    from app.services.core.observability import trace_llm_call

    @trace_llm_call(component="shadow_monitor")
    async def analyze_conversation(transcript):
        return await llm.generate(...)

    # Post-session evaluation
    from app.services.core.observability import evaluate_session_post_completion

    result = await evaluate_session_post_completion(
        session_id="session_123",
        transcript=conversation_history,
        metadata={"stage_type": "technical"}
    )

Configuration (in .env):

    OPIK_ENABLED=true
    OPIK_API_KEY=your_api_key
    OPIK_WORKSPACE=your_workspace
    OPIK_PROJECT_NAME=ai-interviewer

"""
from .decorators import (
    get_current_trace_id,
    get_current_span_id,
    set_current_session_id,
    log_turn_event,
    trace_function,
    trace_llm_call,
    traced_session,
    traced_span,
)
from .evaluation import (
    EvaluationEngine,
    evaluate_session_post_completion,
    evaluation_engine,
)
from .models import (
    EvaluationResult,
    EvaluationScore,
    MetricData,
    SpanData,
    SpanType,
    TraceData,
    TraceMetadata,
    TraceStatus,
    TurnMetrics,
)
from .provider import NullProvider, ObservabilityProvider
from .service import ObservabilityService, observability_service
from .tracers import (
    AnalysisTracer,
    EvaluationTracer,
    InterviewTracer,
    ShadowMonitorTracer,
    analysis_tracer,
    evaluation_tracer,
    interview_tracer,
    shadow_monitor_tracer,
)

__all__ = [
    # Service
    "ObservabilityService",
    "observability_service",
    # Provider interface
    "ObservabilityProvider",
    "NullProvider",
    # Decorators & Context Managers
    "traced_session",
    "traced_span",
    "trace_llm_call",
    "trace_function",
    "log_turn_event",
    "get_current_trace_id",
    "get_current_span_id",
    "set_current_session_id",
    # Tracers
    "InterviewTracer",
    "ShadowMonitorTracer",
    "AnalysisTracer",
    "EvaluationTracer",
    "interview_tracer",
    "shadow_monitor_tracer",
    "analysis_tracer",
    "evaluation_tracer",
    # Evaluation
    "EvaluationEngine",
    "evaluation_engine",
    "evaluate_session_post_completion",
    # Models
    "TraceMetadata",
    "TraceData",
    "SpanData",
    "SpanType",
    "TraceStatus",
    "MetricData",
    "EvaluationScore",
    "EvaluationResult",
    "TurnMetrics",
]
