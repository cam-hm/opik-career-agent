"""
Observability Provider Interface.

Abstract base class defining the contract for observability providers.
Allows swapping between Opik, LangSmith, or other observability backends.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .models import (
    TraceData,
    SpanData,
    MetricData,
    EvaluationResult,
    TraceMetadata,
    SpanType,
)


class ObservabilityProvider(ABC):
    """
    Abstract provider interface for observability operations.

    Implementations can integrate with various observability backends:
    - Opik Cloud (comet.com)
    - Self-hosted Opik
    - LangSmith
    - Custom solutions

    All methods should handle errors gracefully and never crash business logic.
    """

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if the provider is enabled and properly configured."""
        pass

    @abstractmethod
    async def start_trace(
        self,
        name: str,
        metadata: TraceMetadata
    ) -> Optional[str]:
        """
        Start a new trace (session-level).

        Args:
            name: Name of the trace (e.g., "interview_session_abc123")
            metadata: Metadata to attach to the trace

        Returns:
            Trace ID if successful, None if provider unavailable
        """
        pass

    @abstractmethod
    async def end_trace(
        self,
        trace_id: str,
        output: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        End an existing trace.

        Args:
            trace_id: ID of the trace to end
            output: Final output data
            metadata: Additional metadata to add
            error: Error message if trace ended with error

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def start_span(
        self,
        name: str,
        trace_id: Optional[str],
        span_type: SpanType,
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[TraceMetadata] = None
    ) -> Optional[str]:
        """
        Start a new span within a trace.

        Args:
            name: Name of the span (e.g., "llm_gemini_call")
            trace_id: Parent trace ID (None for standalone span)
            span_type: Type of span for categorization
            input_data: Input data for the span
            metadata: Metadata to attach

        Returns:
            Span ID if successful
        """
        pass

    @abstractmethod
    async def end_span(
        self,
        span_id: str,
        output_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        End an existing span.

        Args:
            span_id: ID of the span to end
            output_data: Output data from the operation
            metadata: Additional metadata
            error: Error message if span ended with error

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def log_llm_call(
        self,
        trace_id: Optional[str],
        model: str,
        input_prompt: str,
        output_response: str,
        metadata: Optional[Dict[str, Any]] = None,
        latency_ms: Optional[float] = None,
        tokens_used: Optional[int] = None
    ) -> Optional[str]:
        """
        Log an LLM call as a span.

        Convenience method for logging LLM interactions.

        Args:
            trace_id: Parent trace ID
            model: Model name (e.g., "gemini-2.5-flash")
            input_prompt: Input prompt/query
            output_response: Model response
            metadata: Additional metadata
            latency_ms: Call latency in milliseconds
            tokens_used: Token usage if available

        Returns:
            Span ID if successful
        """
        pass

    @abstractmethod
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a metric value.

        Args:
            metric_name: Name of the metric
            value: Metric value
            trace_id: Associated trace ID
            span_id: Associated span ID
            metadata: Additional context

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def submit_evaluation(
        self,
        evaluation: EvaluationResult
    ) -> bool:
        """
        Submit an evaluation result.

        Args:
            evaluation: Complete evaluation result

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def flush(self) -> bool:
        """
        Flush any pending data to the backend.

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """
        Gracefully shutdown the provider.

        Returns:
            True if successful
        """
        pass


class NullProvider(ObservabilityProvider):
    """
    Null implementation for when observability is disabled.

    All methods are no-ops that return success values.
    Useful for testing and when OPIK_ENABLED=false.
    """

    @property
    def is_enabled(self) -> bool:
        return False

    async def start_trace(self, name: str, metadata: TraceMetadata) -> Optional[str]:
        return None

    async def end_trace(
        self, trace_id: str, output: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None, error: Optional[str] = None
    ) -> bool:
        return True

    async def start_span(
        self, name: str, trace_id: Optional[str], span_type: SpanType,
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[TraceMetadata] = None
    ) -> Optional[str]:
        return None

    async def end_span(
        self, span_id: str, output_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None, error: Optional[str] = None
    ) -> bool:
        return True

    async def log_llm_call(
        self, trace_id: Optional[str], model: str, input_prompt: str,
        output_response: str, metadata: Optional[Dict[str, Any]] = None,
        latency_ms: Optional[float] = None, tokens_used: Optional[int] = None
    ) -> Optional[str]:
        return None

    async def record_metric(
        self, metric_name: str, value: float, trace_id: Optional[str] = None,
        span_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        return True

    async def submit_evaluation(self, evaluation: EvaluationResult) -> bool:
        return True

    async def flush(self) -> bool:
        return True

    async def shutdown(self) -> bool:
        return True
