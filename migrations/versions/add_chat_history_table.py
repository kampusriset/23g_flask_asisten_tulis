"""create chat_history table with user_id foreign key

Revision ID: add_chat_history_table
Revises: c4ef74aa11b3
Create Date: 2025-12-17 07:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_chat_history_table'
down_revision = 'c4ef74aa11b3'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'chat_history',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('user_input', sa.Text(), nullable=False),
        sa.Column('ai_output', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )

def downgrade():
    op.drop_table('chat_history')
