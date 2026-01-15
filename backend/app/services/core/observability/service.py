"""
Observability Service.

Facade pattern providing unified interface for all observability operations.
Singleton service matching existing patterns (like GamificationService).
"""
import logging
from typing import Any, Dict, List, Optional

from config.settings import get_settings

from .models import (
    EvaluationResult,
    SpanType,
    TraceMetadata,
)
from .provider import NullProvider, ObservabilityProvider

logger = logging.getLogger("observability.service")


class ObservabilityService:
    """
    Unified observability service facade.

    Provides a single point of access for all observability operations:
    - Trace management
    - Span management
    - LLM call logging
    - Metric recording
    - Evaluation submission

    Uses provider pattern to abstract the underlying observability backend.
    Gracefully handles all errors without crashing business logic.
    """

    def __init__(self):
        self.settings = get_settings()
        self._provider: Optional[ObservabilityProvider] = None
        self._initialized = False
        # Session registry: maps session_id → trace_id
        # Used because ContextVar doesn't propagate across LiveKit's async tasks
        self._session_traces: Dict[str, str] = {}

    def _ensure_initialized(self):
        """Lazy initialization of provider."""
        if self._initialized:
            return

        self._initialized = True

        # Check if Opik is enabled
        opik_enabled = getattr(self.settings, 'OPIK_ENABLED', False)

        if not opik_enabled:
            logger.info("Observability disabled (OPIK_ENABLED=False)")
            self._provider = NullProvider()
            return

        # Try to initialize Opik provider
        try:
            from .providers.opik_provider import OpikProvider
            self._provider = OpikProvider()

            if self._provider.is_enabled:
                logger.info("Observability initialized with OpikProvider")
            else:
                logger.warning("OpikProvider initialization failed, using NullProvider")
                self._provider = NullProvider()

        except ImportError as e:
            logger.warning(f"Opik SDK not available: {e}. Using NullProvider.")
            self._provider = NullProvider()
        except Exception as e:
            logger.error(f"Failed to initialize ObservabilityService: {e}")
            self._provider = NullProvider()

    @property
    def provider(self) -> ObservabilityProvider:
        """Get the current provider (lazy initialization)."""
        self._ensure_initialized()
        return self._provider

    @property
    def is_enabled(self) -> bool:
        """Check if observability is enabled and working."""
        return self.provider.is_enabled

    # ==================== Session Registry ====================

    def register_session_trace(self, session_id: str, trace_id: str):
        """Register a session_id → trace_id mapping."""
        if session_id and trace_id:
            self._session_traces[session_id] = trace_id
            logger.debug(f"Registered session trace: {session_id} → {trace_id}")

    def unregister_session_trace(self, session_id: str):
        """Remove a session from the registry."""
        if session_id in self._session_traces:
            del self._session_traces[session_id]
            logger.debug(f"Unregistered session trace: {session_id}")

    def get_trace_for_session(self, session_id: str) -> Optional[str]:
        """Get trace_id for a session_id."""
        return self._session_traces.get(session_id)

    # ==================== Trace Operations ====================

    async def start_trace(
        self,
        name: str,
        metadata: TraceMetadata
    ) -> Optional[str]:
        """
        Start a new trace.

        Args:
            name: Trace name
            metadata: Trace metadata

        Returns:
            Trace ID or None
        """
        try:
            return await self.provider.start_trace(name, metadata)
        except Exception as e:
            logger.error(f"start_trace failed: {e}")
            return None

    async def end_trace(
        self,
        trace_id: str,
        output: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """End an existing trace."""
        if not trace_id:
            return True

        try:
            return await self.provider.end_trace(trace_id, output, metadata, error)
        except Exception as e:
            logger.error(f"end_trace failed: {e}")
            return False

    # ==================== Span Operations ====================

    async def start_span(
        self,
        name: str,
        trace_id: Optional[str],
        span_type: SpanType,
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[TraceMetadata] = None
    ) -> Optional[str]:
        """Start a new span."""
        try:
            return await self.provider.start_span(
                name, trace_id, span_type, input_data, metadata
            )
        except Exception as e:
            logger.error(f"start_span failed: {e}")
            return None

    async def end_span(
        self,
        span_id: str,
        output_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """End an existing span."""
        if not span_id:
            return True

        try:
            return await self.provider.end_span(span_id, output_data, metadata, error)
        except Exception as e:
            logger.error(f"end_span failed: {e}")
            return False

    # ==================== LLM Logging ====================

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
        """Log an LLM call."""
        try:
            return await self.provider.log_llm_call(
                trace_id, model, input_prompt, output_response,
                metadata, latency_ms, tokens_used
            )
        except Exception as e:
            logger.error(f"log_llm_call failed: {e}")
            return None

    # ==================== Metrics ====================

    async def record_metric(
        self,
        metric_name: str,
        value: float,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record a metric value."""
        try:
            return await self.provider.record_metric(
                metric_name, value, trace_id, span_id, metadata
            )
        except Exception as e:
            logger.error(f"record_metric failed: {e}")
            return False

    # ==================== Evaluations ====================

    async def submit_evaluation(
        self,
        evaluation: EvaluationResult
    ) -> bool:
        """Submit an evaluation result."""
        try:
            return await self.provider.submit_evaluation(evaluation)
        except Exception as e:
            logger.error(f"submit_evaluation failed: {e}")
            return False

    # ==================== Lifecycle ====================

    async def flush(self) -> bool:
        """Flush pending data."""
        try:
            return await self.provider.flush()
        except Exception as e:
            logger.error(f"flush failed: {e}")
            return False

    async def shutdown(self) -> bool:
        """Shutdown the service."""
        try:
            return await self.provider.shutdown()
        except Exception as e:
            logger.error(f"shutdown failed: {e}")
            return False


# Singleton instance
observability_service = ObservabilityService()
