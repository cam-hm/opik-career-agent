"""Add intelligence v2 fields for enhanced interview analysis

Revision ID: 20250106_intelligence_v2
Revises: 94ad92651926
Create Date: 2025-01-06

Adds fields for:
- Candidate profiling (real-time skill tracking)
- Answer scoring and assessments
- Adaptive difficulty tracking
- Cross-stage memory/insights
- Competency scores
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250106_intelligence_v2'
down_revision: Union[str, None] = '94ad92651926'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to interview_sessions
    op.add_column('interview_sessions',
        sa.Column('candidate_profile', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment='Real-time candidate profile: verified_skills, gaps, red_flags, strengths'))

    op.add_column('interview_sessions',
        sa.Column('skill_assessments', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment='Per-turn scoring data with dimensions'))

    op.add_column('interview_sessions',
        sa.Column('difficulty_level', sa.String(20), nullable=True, server_default='intermediate',
                  comment='Current adaptive difficulty: foundational/intermediate/advanced/expert'))

    op.add_column('interview_sessions',
        sa.Column('competency_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment='Final competency scores: technical_depth, communication, problem_solving, leadership'))

    op.add_column('interview_sessions',
        sa.Column('questions_asked', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment='List of questions asked with metadata for tracking'))

    op.add_column('interview_sessions',
        sa.Column('topics_covered', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment='Set of topics already covered to avoid repetition'))

    # Add cross-stage insights to interview_applications
    op.add_column('interview_applications',
        sa.Column('cross_stage_insights', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment='Insights from each completed stage for cross-stage memory'))


def downgrade() -> None:
    # Remove columns from interview_sessions
    op.drop_column('interview_sessions', 'candidate_profile')
    op.drop_column('interview_sessions', 'skill_assessments')
    op.drop_column('interview_sessions', 'difficulty_level')
    op.drop_column('interview_sessions', 'competency_scores')
    op.drop_column('interview_sessions', 'questions_asked')
    op.drop_column('interview_sessions', 'topics_covered')

    # Remove columns from interview_applications
    op.drop_column('interview_applications', 'cross_stage_insights')
