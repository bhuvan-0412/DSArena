"""add_learning_content_models

Revision ID: f8b91a23c456
Revises: e7a4f79d7746
Create Date: 2026-07-25 13:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f8b91a23c456'
down_revision: Union[str, None] = 'e7a4f79d7746'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    try:
        op.create_table('learning_resources',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('node_id', sa.String(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('type', sa.String(), nullable=False),
            sa.Column('author', sa.String(), nullable=True),
            sa.Column('duration', sa.String(), nullable=True),
            sa.Column('difficulty', sa.String(), nullable=True),
            sa.Column('url', sa.String(), nullable=False),
            sa.Column('order_index', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['node_id'], ['roadmap_nodes.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_learning_resources_id'), 'learning_resources', ['id'], unique=False)
        op.create_index(op.f('ix_learning_resources_node_id'), 'learning_resources', ['node_id'], unique=False)
    except Exception:
        pass

    try:
        op.create_table('key_concepts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('node_id', sa.String(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('summary', sa.Text(), nullable=False),
            sa.Column('key_points', sa.JSON(), nullable=True),
            sa.Column('complexity_notes', sa.Text(), nullable=True),
            sa.Column('common_mistakes', sa.JSON(), nullable=True),
            sa.Column('best_practices', sa.JSON(), nullable=True),
            sa.Column('order_index', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['node_id'], ['roadmap_nodes.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_key_concepts_id'), 'key_concepts', ['id'], unique=False)
        op.create_index(op.f('ix_key_concepts_node_id'), 'key_concepts', ['node_id'], unique=False)
    except Exception:
        pass

    try:
        op.create_table('concept_notes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('node_id', sa.String(), nullable=False),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['node_id'], ['roadmap_nodes.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'node_id', name='uq_user_concept_note')
        )
        op.create_index(op.f('ix_concept_notes_id'), 'concept_notes', ['id'], unique=False)
    except Exception:
        pass

    try:
        op.create_table('bookmarks',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('target_type', sa.String(), nullable=False),
            sa.Column('target_id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'target_type', 'target_id', name='uq_user_target_bookmark')
        )
        op.create_index(op.f('ix_bookmarks_id'), 'bookmarks', ['id'], unique=False)
    except Exception:
        pass

    try:
        op.create_table('learning_checklists',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('node_id', sa.String(), nullable=False),
            sa.Column('watched_video', sa.Boolean(), nullable=True),
            sa.Column('read_notes', sa.Boolean(), nullable=True),
            sa.Column('understood_concepts', sa.Boolean(), nullable=True),
            sa.Column('completed_quiz', sa.Boolean(), nullable=True),
            sa.Column('solved_problems', sa.Boolean(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['node_id'], ['roadmap_nodes.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'node_id', name='uq_user_node_checklist')
        )
        op.create_index(op.f('ix_learning_checklists_id'), 'learning_checklists', ['id'], unique=False)
    except Exception:
        pass

def downgrade() -> None:
    pass
