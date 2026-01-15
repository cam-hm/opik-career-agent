"""
Opik Provider Implementation.

Integrates with Opik Cloud (comet.com) for LLM observability.
Implements the ObservabilityProvider interface.
"""
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

from config.settings import get_settings

from ..models import (
    EvaluationResult,
    SpanType,
    TraceMetadata,
)
from ..provider import ObservabilityProvider

logger = logging.getLogger("opik-provider")


class OpikProvider(ObservabilityProvider):
    """
    Opik Cloud provider implementation.

    Features:
    - Session-level trace creation
    - LLM call span logging
    - Metric recording
    - Evaluation submission
    - Graceful error handling (never crashes business logic)
    """

    def __init__(self):
        self.settings = get_settings()
        self._enabled = False
        self._client = None
        self._project_name = None
        self._active_traces: Dict[str, Any] = {}  # trace_id -> trace object
        self._active_spans: Dict[str, Any] = {}   # span_id -> span object

        self._initialize()

    # ==================== Helper Methods ====================

    def _build_end_kwargs(
        self,
        output: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
        duration_ms: float,
        error: Optional[str],
        existing_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build kwargs for ending a trace/span. Reduces duplication."""
        end_kwargs = {}
        if output:
            end_kwargs["output"] = output
        if metadata or duration_ms:
            end_kwargs["metadata"] = {
                **(existing_metadata or {}),
                **(metadata or {}),
                "duration_ms": duration_ms
            }
        if error:
            end_kwargs["metadata"] = end_kwargs.get("metadata", {})
            end_kwargs["metadata"]["error"] = error
        return end_kwargs

    def _create_span(
        self,
        name: str,
        parent_trace: Optional[Any],
        opik_type: str,
        input_data: Dict[str, Any],
        meta_dict: Dict[str, Any]
    ) -> Any:
        """Create a span with or without parent trace. Reduces duplication."""
        if parent_trace:
            return parent_trace.span(
                name=name,
                type=opik_type,
                input=input_data,
                metadata=meta_dict
            )
        else:
            return self._client.span(
                name=name,
                type=opik_type,
                input=input_data,
                metadata=meta_dict
            )

    def _filter_none_values(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values from a dictionary."""
        return {k: v for k, v in d.items() if v is not None}

    def _initialize(self):
        """Initialize Opik client with configuration."""
        if not getattr(self.settings, 'OPIK_ENABLED', False):
            logger.info("Opik observability disabled (OPIK_ENABLED=False)")
            return

        api_key = getattr(self.settings, 'OPIK_API_KEY', '')
        if not api_key:
            logger.warning("Opik API key not configured. Tracing disabled.")
            return

        try:
            import opik

            # Configure Opik
            self._project_name = getattr(self.settings, 'OPIK_PROJECT_NAME', 'ai-interviewer')
            workspace = getattr(self.settings, 'OPIK_WORKSPACE', 'default')

            opik.configure(
                api_key=api_key,
                workspace=workspace
            )

            # Create client
            self._client = opik.Opik(project_name=self._project_name)
            self._enabled = True

            logger.info(f"Opik initialized: project={self._project_name}, workspace={workspace}")

        except ImportError:
            logger.warning("Opik SDK not installed. Run: pip install opik")
        except Exception as e:
            logger.error(f"Opik initialization failed: {e}")

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    async def start_trace(
        self,
        name: str,
        metadata: TraceMetadata
    ) -> Optional[str]:
        """Start a new trace (session-level)."""
        if not self._enabled:
            return None

        try:
            # Convert metadata to dict
            meta_dict = self._filter_none_values({
                "session_id": metadata.session_id,
                "stage_type": metadata.stage_type,
                "job_role": metadata.job_role,
                "language": metadata.language,
                "component": metadata.component,
                **metadata.extra
            })

            # Create tags from metadata
            tags = []
            if metadata.stage_type:
                tags.append(metadata.stage_type)
            if metadata.job_role:
                tags.append(metadata.job_role)
                tags.append(f"2026_resolution:{metadata.job_role}")
            if metadata.language:
                tags.append(f"lang:{metadata.language}")

            trace = self._client.trace(
                name=name,
                input={"session_id": metadata.session_id},
                metadata=meta_dict,
                tags=tags
            )

            trace_id = trace.id
            self._active_traces[trace_id] = {
                "trace": trace,
                "start_time": time.time()
            }

            logger.debug(f"Started trace: {trace_id} ({name})")
            return trace_id

        except Exception as e:
            logger.error(f"Failed to start trace '{name}': {e}")
            return None

    async def end_trace(
        self,
        trace_id: str,
        output: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """End an existing trace."""
        if not self._enabled:
            return True

        try:
            trace_data = self._active_traces.pop(trace_id, None)
            if not trace_data:
                logger.warning(f"Trace not found: {trace_id}")
                return False

            trace = trace_data["trace"]
            duration_ms = (time.time() - trace_data["start_time"]) * 1000

            end_kwargs = self._build_end_kwargs(
                output=output,
                metadata=metadata,
                duration_ms=duration_ms,
                error=error,
                existing_metadata=trace.metadata
            )

            trace.end(**end_kwargs) if end_kwargs else trace.end()

            logger.debug(f"Ended trace: {trace_id} (duration: {duration_ms:.0f}ms)")
            return True

        except Exception as e:
            logger.error(f"Failed to end trace '{trace_id}': {e}")
            return False

    async def start_span(
        self,
        name: str,
        trace_id: Optional[str],
        span_type: SpanType,
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[TraceMetadata] = None
    ) -> Optional[str]:
        """Start a new span within a trace."""
        if not self._enabled:
            return None

        try:
            # Get parent trace
            parent_trace = None
            if trace_id and trace_id in self._active_traces:
                parent_trace = self._active_traces[trace_id]["trace"]

            # Map span type to Opik type
            opik_type_map = {
                SpanType.LLM_CALL: "llm",
                SpanType.FUNCTION: "tool"
            }
            opik_type = opik_type_map.get(span_type, "general")

            # Prepare metadata
            meta_dict = {}
            if metadata:
                meta_dict = self._filter_none_values({
                    "component": metadata.component,
                    "model": metadata.model,
                    **metadata.extra
                })

            # Create span using helper
            span = self._create_span(
                name=name,
                parent_trace=parent_trace,
                opik_type=opik_type,
                input_data=input_data or {},
                meta_dict=meta_dict
            )

            span_id = span.id
            self._active_spans[span_id] = {
                "span": span,
                "start_time": time.time()
            }

            logger.debug(f"Started span: {span_id} ({name})")
            return span_id

        except Exception as e:
            logger.error(f"Failed to start span '{name}': {e}")
            return None

    async def end_span(
        self,
        span_id: str,
        output_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """End an existing span."""
        if not self._enabled:
            return True

        try:
            span_data = self._active_spans.pop(span_id, None)
            if not span_data:
                logger.warning(f"Span not found: {span_id}")
                return False

            span = span_data["span"]
            duration_ms = (time.time() - span_data["start_time"]) * 1000

            end_kwargs = self._build_end_kwargs(
                output=output_data,
                metadata=metadata,
                duration_ms=duration_ms,
                error=error
            )

            span.end(**end_kwargs)

            logger.debug(f"Ended span: {span_id} (duration: {duration_ms:.0f}ms)")
            return True

        except Exception as e:
            logger.error(f"Failed to end span '{span_id}': {e}")
            return False

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
        """Log an LLM call as a complete span."""
        if not self._enabled:
            return None

        try:
            # Get parent trace if available
            parent_trace = None
            if trace_id and trace_id in self._active_traces:
                parent_trace = self._active_traces[trace_id]["trace"]

            # Prepare metadata
            meta = {"model": model, **(metadata or {})}
            if latency_ms:
                meta["latency_ms"] = latency_ms

            # Truncation limit for Opik Cloud (generous limit, Opik handles large payloads)
            MAX_CONTENT_LENGTH = 10000  # 10KB per field

            # Create span using helper
            span = self._create_span(
                name=f"llm_call_{model.split('/')[-1]}",
                parent_trace=parent_trace,
                opik_type="llm",
                input_data={"prompt": input_prompt[:MAX_CONTENT_LENGTH]},
                meta_dict=meta
            )

            # Prepare usage data and end span
            usage = {"total_tokens": tokens_used} if tokens_used else None
            span.end(
                output={"response": output_response[:MAX_CONTENT_LENGTH]},
                usage=usage,
                model=model
            )

            logger.debug(f"Logged LLM call: {model}")
            return span.id

        except Exception as e:
            logger.error(f"Failed to log LLM call: {e}")
            return None

    async def record_metric(
        self,
        metric_name: str,
        value: float,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record a metric value."""
        if not self._enabled:
            return True

        try:
            # Opik uses feedback scores for metrics
            if trace_id:
                self._client.log_traces_feedback_scores(
                    scores=[{
                        "id": trace_id,
                        "name": metric_name,
                        "value": value,
                        "reason": metadata.get("reason") if metadata else None
                    }]
                )
                logger.debug(f"Recorded metric: {metric_name}={value} for trace {trace_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to record metric '{metric_name}': {e}")
            return False

    async def submit_evaluation(
        self,
        evaluation: EvaluationResult
    ) -> bool:
        """Submit an evaluation result."""
        if not self._enabled:
            return True

        try:
            # Convert scores to feedback scores
            scores = []
            for score in evaluation.scores:
                score_data = {
                    "name": score.metric_name,
                    "value": score.score,
                    "reason": score.reason
                }
                if evaluation.trace_id:
                    score_data["id"] = evaluation.trace_id
                scores.append(score_data)

            if scores and evaluation.trace_id:
                self._client.log_traces_feedback_scores(scores=scores)

            # Also add overall score if available
            if evaluation.overall_score is not None and evaluation.trace_id:
                self._client.log_traces_feedback_scores(
                    scores=[{
                        "id": evaluation.trace_id,
                        "name": f"{evaluation.evaluator}_overall",
                        "value": evaluation.overall_score,
                        "reason": evaluation.summary
                    }]
                )

            logger.info(f"Submitted evaluation for session {evaluation.session_id}: "
                       f"{len(scores)} scores, overall={evaluation.overall_score}")
            return True

        except Exception as e:
            logger.error(f"Failed to submit evaluation: {e}")
            return False

    async def flush(self) -> bool:
        """Flush any pending data to Opik."""
        if not self._enabled:
            return True

        try:
            self._client.flush(timeout=10)
            logger.debug("Flushed Opik client")
            return True
        except Exception as e:
            logger.error(f"Failed to flush Opik client: {e}")
            return False

    async def shutdown(self) -> bool:
        """Gracefully shutdown the provider."""
        if not self._enabled:
            return True

        try:
            # End any active traces/spans
            for trace_id in list(self._active_traces.keys()):
                await self.end_trace(trace_id, error="shutdown")

            for span_id in list(self._active_spans.keys()):
                await self.end_span(span_id, error="shutdown")

            # Flush remaining data
            await self.flush()

            logger.info("Opik provider shutdown complete")
            return True

        except Exception as e:
            logger.error(f"Error during Opik shutdown: {e}")
            return False
