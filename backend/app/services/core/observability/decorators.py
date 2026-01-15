"""
Observability Decorators and Context Managers.

Provides non-invasive integration utilities for tracing
without polluting business logic.
"""
import functools
import logging
import time
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any, Callable, Dict, Optional

from .models import SpanType, TraceMetadata

logger = logging.getLogger("observability")

# Context variables for propagating trace context
_current_trace_id: ContextVar[Optional[str]] = ContextVar('current_trace_id', default=None)
_current_span_id: ContextVar[Optional[str]] = ContextVar('current_span_id', default=None)


def get_current_trace_id() -> Optional[str]:
    """Get the current trace ID from context."""
    return _current_trace_id.get()


def get_current_span_id() -> Optional[str]:
    """Get the current span ID from context."""
    return _current_span_id.get()


@asynccontextmanager
async def traced_session(
    session_id: str,
    stage_type: str = None,
    job_role: str = None,
    language: str = None,
    **extra_metadata
):
    """
    Context manager for session-level tracing.

    Creates a trace that spans the entire interview session.
    All operations within the context are linked to this trace.

    Usage:
        async with traced_session("session_123", stage_type="technical"):
            # All LLM calls here are linked to the session trace
            await interview_agent.process()

    Args:
        session_id: Unique session identifier
        stage_type: Interview stage (hr, technical, behavioral)
        job_role: Target job role
        language: Interview language
        **extra_metadata: Additional metadata
    """
    # Import here to avoid circular dependency
    from .service import observability_service

    metadata = TraceMetadata(
        session_id=session_id,
        stage_type=stage_type,
        job_role=job_role,
        language=language,
        extra=extra_metadata
    )

    trace_id = await observability_service.start_trace(
        name=f"interview_session_{session_id}",
        metadata=metadata
    )

    token = _current_trace_id.set(trace_id)

    try:
        yield trace_id
    except Exception as e:
        # End trace with error
        if trace_id:
            await observability_service.end_trace(
                trace_id=trace_id,
                error=str(e)
            )
        raise
    finally:
        # End trace normally
        if trace_id:
            await observability_service.end_trace(trace_id=trace_id)
        _current_trace_id.reset(token)


@asynccontextmanager
async def traced_span(
    name: str,
    span_type: SpanType = SpanType.FUNCTION,
    input_data: Optional[Dict[str, Any]] = None,
    component: str = None,
    model: str = None,
    **extra_metadata
):
    """
    Context manager for span-level tracing.

    Creates a span within the current trace context.

    Usage:
        async with traced_span("process_resume", component="analysis"):
            result = await analyze_resume(resume_text)

    Args:
        name: Span name
        span_type: Type of span (LLM_CALL, FUNCTION, etc.)
        input_data: Input data for the span
        component: Component name (e.g., "shadow_monitor")
        model: Model name if LLM call
        **extra_metadata: Additional metadata
    """
    from .service import observability_service

    trace_id = get_current_trace_id()

    metadata = TraceMetadata(
        component=component,
        model=model,
        extra=extra_metadata
    )

    span_id = await observability_service.start_span(
        name=name,
        trace_id=trace_id,
        span_type=span_type,
        input_data=input_data,
        metadata=metadata
    )

    token = _current_span_id.set(span_id)
    start_time = time.time()

    try:
        yield span_id
    except Exception as e:
        if span_id:
            await observability_service.end_span(
                span_id=span_id,
                error=str(e)
            )
        raise
    finally:
        if span_id:
            duration_ms = (time.time() - start_time) * 1000
            await observability_service.end_span(
                span_id=span_id,
                metadata={"duration_ms": duration_ms}
            )
        _current_span_id.reset(token)


def trace_llm_call(
    component: str,
    model: str = None,
    capture_input: bool = True,
    capture_output: bool = True,
    max_content_length: int = 2000
):
    """
    Decorator to automatically trace LLM calls.

    Usage:
        @trace_llm_call(component="shadow_monitor", model="gemini-2.5-flash")
        async def analyze_conversation(transcript: list) -> str:
            response = await llm.generate(...)
            return response.text

    Args:
        component: Component name for categorization
        model: LLM model name (can also be extracted from settings)
        capture_input: Whether to capture input arguments
        capture_output: Whether to capture return value
        max_content_length: Max length for captured content
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            from .service import observability_service
            from config.settings import get_settings

            settings = get_settings()
            actual_model = model or getattr(settings, 'GEMINI_MODEL', 'unknown')

            # Capture input
            input_data = {}
            if capture_input:
                # Try to extract meaningful input from args/kwargs
                if args:
                    first_arg = args[0]
                    if isinstance(first_arg, str):
                        input_data["prompt"] = first_arg[:max_content_length]
                    elif isinstance(first_arg, list):
                        input_data["input_length"] = len(first_arg)
                if "prompt" in kwargs:
                    input_data["prompt"] = str(kwargs["prompt"])[:max_content_length]
                if "transcript" in kwargs or (args and isinstance(args[0], list)):
                    input_data["has_transcript"] = True

            trace_id = get_current_trace_id()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Log LLM call
                latency_ms = (time.time() - start_time) * 1000

                output_str = ""
                if capture_output and result is not None:
                    if isinstance(result, str):
                        output_str = result[:max_content_length]
                    elif isinstance(result, dict):
                        output_str = str(result)[:max_content_length]

                await observability_service.log_llm_call(
                    trace_id=trace_id,
                    model=actual_model,
                    input_prompt=input_data.get("prompt", str(input_data)),
                    output_response=output_str,
                    metadata={"component": component},
                    latency_ms=latency_ms
                )

                return result

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                await observability_service.log_llm_call(
                    trace_id=trace_id,
                    model=actual_model,
                    input_prompt=input_data.get("prompt", str(input_data)),
                    output_response=f"ERROR: {str(e)}",
                    metadata={"component": component, "error": True},
                    latency_ms=latency_ms
                )
                raise

        return wrapper
    return decorator


def trace_function(
    name: str = None,
    component: str = None,
    capture_args: bool = False
):
    """
    Decorator to trace any async function.

    Usage:
        @trace_function(component="analysis")
        async def process_resume(resume_text: str):
            ...

    Args:
        name: Custom span name (defaults to function name)
        component: Component name
        capture_args: Whether to capture function arguments
    """
    def decorator(func: Callable):
        span_name = name or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            input_data = {}
            if capture_args:
                # Capture safe args (no large objects)
                for i, arg in enumerate(args[:3]):  # Limit to first 3 args
                    if isinstance(arg, (str, int, float, bool)):
                        input_data[f"arg_{i}"] = arg
                for key, value in list(kwargs.items())[:5]:  # Limit kwargs
                    if isinstance(value, (str, int, float, bool)):
                        input_data[key] = value

            async with traced_span(
                name=span_name,
                span_type=SpanType.FUNCTION,
                input_data=input_data,
                component=component
            ):
                return await func(*args, **kwargs)

        return wrapper
    return decorator


async def log_turn_event(
    turn_index: int,
    role: str,
    content: str,
    response_time_ms: float = None
):
    """
    Log a conversation turn as an event.

    Args:
        turn_index: Turn number in conversation
        role: "user" or "assistant"
        content: Message content
        response_time_ms: Response latency if available
    """
    from .service import observability_service

    await observability_service.record_metric(
        metric_name=f"turn_{role}",
        value=float(turn_index),
        trace_id=get_current_trace_id(),
        metadata={
            "role": role,
            "content_length": len(content),
            "word_count": len(content.split()),
            "response_time_ms": response_time_ms
        }
    )
