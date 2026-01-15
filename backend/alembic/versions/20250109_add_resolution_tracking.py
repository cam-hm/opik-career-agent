"""Add resolution tracking tables for personal growth

Revision ID: 20250109_resolution
Revises: 20250108_opik
Create Date: 2025-01-09

Adds tables for:
- User resolutions (2026 career goals)
- Skill snapshots (weekly progress tracking)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250109_resolution'
down_revision: Union[str, None] = '20250108_opik'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_resolutions table
    op.create_table('user_resolutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('target_role', sa.String(), nullable=True),
        sa.Column('target_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('baseline_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('target_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user_progress.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_resolutions_user_id', 'user_resolutions', ['user_id'], unique=False)

    # Create skill_snapshots table
    op.create_table('skill_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('skill_levels', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('competency_averages', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('sessions_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('snapshot_type', sa.String(), nullable=False, server_default='weekly'),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user_progress.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_skill_snapshots_user_period', 'skill_snapshots', ['user_id', 'period_start'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_skill_snapshots_user_period', table_name='skill_snapshots')
    op.drop_table('skill_snapshots')
    op.drop_index('idx_user_resolutions_user_id', table_name='user_resolutions')
    op.drop_table('user_resolutions')
