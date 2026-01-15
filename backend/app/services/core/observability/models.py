"""
Observability Data Models.

Pydantic models for observability data structures used across
the tracing and evaluation system.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TraceStatus(str, Enum):
    """Status of a trace."""
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class SpanType(str, Enum):
    """Type of span for categorization."""
    LLM_CALL = "llm_call"
    FUNCTION = "function"
    SESSION = "session"
    EVALUATION = "evaluation"


class TraceMetadata(BaseModel):
    """Metadata attached to traces and spans."""
    session_id: Optional[str] = None
    stage_type: Optional[str] = None
    job_role: Optional[str] = None
    language: Optional[str] = None
    model: Optional[str] = None
    component: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class SpanData(BaseModel):
    """Data for a single span within a trace."""
    span_id: str
    trace_id: str
    name: str
    span_type: SpanType
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    metadata: TraceMetadata = Field(default_factory=TraceMetadata)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: TraceStatus = TraceStatus.RUNNING
    error_message: Optional[str] = None


class TraceData(BaseModel):
    """Data for a complete trace (session-level)."""
    trace_id: str
    name: str
    metadata: TraceMetadata = Field(default_factory=TraceMetadata)
    spans: List[SpanData] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: TraceStatus = TraceStatus.RUNNING


class MetricData(BaseModel):
    """Data for a recorded metric."""
    metric_name: str
    value: float
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EvaluationScore(BaseModel):
    """Score from an evaluation metric."""
    metric_name: str
    score: float  # 0.0 to 1.0
    reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    """Complete evaluation result for a session."""
    session_id: str
    trace_id: Optional[str] = None
    evaluator: str  # e.g., "g_eval", "answer_relevance"
    scores: List[EvaluationScore] = Field(default_factory=list)
    overall_score: Optional[float] = None
    summary: Optional[str] = None
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TurnMetrics(BaseModel):
    """Metrics for a single conversation turn."""
    turn_index: int
    role: str  # "user" or "assistant"
    content_length: int
    word_count: int
    response_time_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
