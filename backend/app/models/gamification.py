from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base

class CareerNode(Base):
    """
    Represents a node in the Career Tree dependencies.
    Defined via YAML, but mirrored here for referential integrity if needed,
    or purely purely logical. 
    Actually, per design, we might keep definitions in YAML, but storing status requires IDs.
    Let's store the node definition in DB for easier querying/joins, seeded from YAML.
    """
    __tablename__ = "career_nodes"

    id = Column(String, primary_key=True) # "node_101"
    title = Column(JSON, nullable=False) # e.g. {"en": "Fundamentals", "vi": "Cơ bản"}
    rank_required = Column(Integer, default=1)
    type = Column(String, default="interview") # interview, quiz, milestone
    parent_node_id = Column(String, ForeignKey("career_nodes.id"), nullable=True)
    
    # JSON for flexibility (criteria, unlock rewards)
    metadata_ = Column("metadata", JSON, default={}) 

class UserProgress(Base):
    """
    Singleton-per-user tracking XP, Level, and Stats.
    """
    __tablename__ = "user_progress"

    user_id = Column(String, primary_key=True) # Linked to Clerk ID (String)
    current_level = Column(Integer, default=1)
    current_xp = Column(Integer, default=0)
    daily_streak = Column(Integer, default=0)
    last_active_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # The Hex-Stat Radar Data
    # { "Communication": 85, "Technical": 70 ... }
    skill_stats = Column(JSON, default={}) 
    
    # Adaptive Theme
    target_role = Column(String, nullable=True) # e.g. "Senior Python Developer" 

class UserNode(Base):
    """
    Tracks which nodes a user has completed/unlocked.
    """
    __tablename__ = "user_nodes"

    user_id = Column(String, ForeignKey("user_progress.user_id"), primary_key=True)
    node_id = Column(String, ForeignKey("career_nodes.id"), primary_key=True)
    
    status = Column(String, default="locked") # locked, unlocked, completed
    high_score = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class Achievement(Base):
    """
    Badge definitions.
    """
    __tablename__ = "achievements"

    id = Column(String, primary_key=True) # "first_blood"
    name = Column(JSON, nullable=False) # {"en": "First Blood", "vi": "Chiến công đầu"}
    description = Column(JSON) # Localized description
    icon_url = Column(String)

    # Criteria DSL
    criteria = Column(JSON, default={})

class UserAchievement(Base):
    """
    Unlocked badges.
    """
    __tablename__ = "user_achievements"

    user_id = Column(String, ForeignKey("user_progress.user_id"), primary_key=True)
    achievement_id = Column(String, ForeignKey("achievements.id"), primary_key=True)

    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())


class UserResolution(Base):
    """
    2026 Career Resolution - User's career goals and milestones.
    Tracks progress towards personal growth objectives.
    """
    __tablename__ = "user_resolutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey("user_progress.user_id"), nullable=False, index=True)

    # Resolution details
    title = Column(String, nullable=False)  # e.g. "Become a Senior Backend Engineer"
    description = Column(String, nullable=True)  # Additional details
    target_role = Column(String, nullable=True)  # Specific role target

    # Goal metrics - what skill levels to achieve
    # Structure: {"technical_depth": 80, "communication": 75, "system_design": 70}
    target_skills = Column(JSON, default={})

    # Baseline when resolution was created
    # Structure: {"technical_depth": 50, "communication": 60, "system_design": 40}
    baseline_skills = Column(JSON, default={})

    # Deadline
    target_date = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(String, default="active")  # active, completed, abandoned

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class SkillSnapshot(Base):
    """
    Weekly/periodic snapshot of user's skill levels.
    Used for tracking progress over time and generating insights.
    """
    __tablename__ = "skill_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey("user_progress.user_id"), nullable=False, index=True)

    # Snapshot data
    # Structure: {"technical_depth": 65, "communication": 70, ...}
    skill_levels = Column(JSON, nullable=False, default={})

    # Aggregated competency scores from recent sessions
    # Structure: {"confidence": 0.75, "clarity": 0.80, "relevance": 0.85, "depth": 0.70}
    competency_averages = Column(JSON, default={})

    # Summary stats
    sessions_count = Column(Integer, default=0)  # Sessions in this period
    average_score = Column(Integer, default=0)  # Average session score

    # Period tracking
    snapshot_type = Column(String, default="weekly")  # weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
