"""Add opik_trace_id to interview_sessions

Revision ID: 20250108_opik
Revises: 20250106_intelligence_v2
Create Date: 2025-01-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250108_opik'
down_revision: Union[str, None] = '20250106_intelligence_v2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add opik_trace_id column to interview_sessions
    op.add_column(
        'interview_sessions',
        sa.Column('opik_trace_id', sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('interview_sessions', 'opik_trace_id')
