"""initial migration

Revision ID: 548bb7812174
Revises: 
Create Date: 2025-12-24 06:52:51.228415

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '548bb7812174'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Initial tables
    op.create_table('rapats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('topik', sa.String(length=200), nullable=False),
        sa.Column('catatan', sa.Text(), nullable=True),
        sa.Column('tanggal', sa.Date(), nullable=True),
        sa.Column('peserta', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=120), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('profile_pic', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_table('chat_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_input', sa.Text(), nullable=False),
        sa.Column('ai_output', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # b466d7ae20e0_add_deleted_at_to_notes.py
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))

    # 5da52af3e558_create_inbox_table.py
    op.create_table('inbox',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # d5a310fa40ef_add_deleted_at_to_rapats.py
    with op.batch_alter_table('rapats', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))

    # 2424a9447eb3_.py
    with op.batch_alter_table('rapats', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])

    # 7de138aba820_add_created_at_updated_at_to_rapats.py
    with op.batch_alter_table('rapats', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # 7de138aba820_add_created_at_updated_at_to_rapats.py
    with op.batch_alter_table('rapats', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')

    # 2424a9447eb3_.py
    with op.batch_alter_table('rapats', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # d5a310fa40ef_add_deleted_at_to_rapats.py
    with op.batch_alter_table('rapats', schema=None) as batch_op:
        batch_op.drop_column('deleted_at')

    # b466d7ae20e0_add_deleted_at_to_notes.py
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.drop_column('deleted_at')

    # 5da52af3e558_create_inbox_table.py
    op.drop_table('inbox')

    # Initial tables
    op.drop_table('notes')
    op.drop_table('chat_history')
    op.drop_table('users')
    op.drop_table('rapats')
    # ### end Alembic commands ###
