from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class InterviewApplication(Base):
    __tablename__ = "interview_applications"

    id = Column(String, primary_key=True, index=True) # UUID
    user_id = Column(String, nullable=False, index=True)
    job_role = Column(String, nullable=False)
    # type: 'standard' (3-stage) or 'practice' (1-off session)
    type = Column(String, default="standard", nullable=False)
    status = Column(String, default="in_progress") # in_progress, completed, rejected
    current_stage = Column(Integer, default=1) # 1, 2, 3
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Context (Unified Source of Truth)
    job_description = Column(Text, nullable=True)
    resume_text = Column(Text, nullable=True)
    resume_analysis = Column(JSON, nullable=True) # Cached AI Analysis Result (Match %, Stage Hints)

    # Cross-Stage Intelligence Memory
    # Structure: {"hr": {"summary": "...", "verified_skills": [...], "red_flags": [...]}, ...}
    cross_stage_insights = Column(JSONB, nullable=True)

    sessions = relationship("InterviewSession", back_populates="application", cascade="all, delete-orphan")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True) # LiveKit Room Name

    # Link to Context
    application_id = Column(String, ForeignKey("interview_applications.id"), nullable=False, index=True)

    # Session Details
    stage_type = Column(String, nullable=False) # hr, technical, behavioral (or 'practice_round')
    status = Column(String, default="pending") # pending, active, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Execution Data
    candidate_name = Column(String, nullable=True)
    transcript = Column(Text, nullable=True) # JSON string of the conversation
    feedback_markdown = Column(Text, nullable=True)
    language = Column(String, nullable=True, default="en")  # en, vi
    overall_score = Column(Integer, nullable=True)  # 0-100 score
    node_id = Column(String, nullable=True) # Project Odyssey Node ID

    # Intelligence v2: Real-time Candidate Profiling
    # Structure: {"verified_skills": {"Python": {"depth": 4, "evidence": "..."}},
    #             "identified_gaps": [...], "red_flags": [...], "strengths": [...]}
    candidate_profile = Column(JSONB, nullable=True)

    # Intelligence v2: Per-turn Answer Scoring
    # Structure: [{"turn": 1, "score": 75, "dimension": "technical_depth", ...}, ...]
    skill_assessments = Column(JSONB, nullable=True)

    # Intelligence v2: Adaptive Difficulty Level
    # Values: foundational, intermediate, advanced, expert
    difficulty_level = Column(String(20), nullable=True, default="intermediate")

    # Intelligence v2: Final Competency Scores
    # Structure: {"technical_depth": {"score": 75, "rubric_level": "..."}, ...}
    competency_scores = Column(JSONB, nullable=True)

    # Intelligence v2: Question Tracking
    # Structure: [{"question": "...", "topic": "...", "difficulty": "..."}, ...]
    questions_asked = Column(JSONB, nullable=True)

    # Intelligence v2: Topics Covered (to avoid repetition)
    # Structure: ["career_history", "python_experience", "system_design", ...]
    topics_covered = Column(JSONB, nullable=True)

    # Opik Observability: Trace ID for linking to Opik Cloud dashboard
    opik_trace_id = Column(String, nullable=True)

    application = relationship("InterviewApplication", back_populates="sessions")

    @property
    def job_role(self):
        return self.application.job_role if self.application else None

    @property
    def resume_text(self):
        return self.application.resume_text if self.application else None

    @property
    def job_description(self):
        return self.application.job_description if self.application else None
