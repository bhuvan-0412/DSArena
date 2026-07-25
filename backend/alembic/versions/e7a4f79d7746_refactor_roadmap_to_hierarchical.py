"""refactor_roadmap_to_hierarchical

Revision ID: e7a4f79d7746
Revises: 9f702f19f36d
Create Date: 2026-07-20 02:52:15.535931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7a4f79d7746'
down_revision: Union[str, None] = '9f702f19f36d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create base roadmap_nodes table
    try:
        op.create_table('roadmap_nodes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('parent_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('estimated_time', sa.Integer(), nullable=True),
        sa.Column('xp_reward', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['roadmap_nodes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_roadmap_nodes_id'), 'roadmap_nodes', ['id'], unique=False)
    except Exception:
        pass
    
    # 2. Create user_node_progress table
    try:
        op.create_table('user_node_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.String(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('progress_percentage', sa.Integer(), nullable=True),
        sa.Column('problems_solved', sa.Integer(), nullable=True),
        sa.Column('video_watched', sa.Boolean(), nullable=True),
        sa.Column('notes_read', sa.Boolean(), nullable=True),
        sa.Column('quiz_completed', sa.Boolean(), nullable=True),
        sa.Column('boss_battle_completed', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['node_id'], ['roadmap_nodes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'node_id', name='uq_user_node')
        )
        op.create_index(op.f('ix_user_node_progress_id'), 'user_node_progress', ['id'], unique=False)
    except Exception:
        pass

    # 3. Modify quizzes table to repoint foreign key to roadmap_nodes
    try:
        with op.batch_alter_table('quizzes', schema=None) as batch_op:
            batch_op.add_column(sa.Column('node_id', sa.String(), nullable=False, server_default=''))
            batch_op.create_unique_constraint('uq_quizzes_node_id', ['node_id'])
            batch_op.create_foreign_key('fk_quizzes_roadmap_nodes', 'roadmap_nodes', ['node_id'], ['id'], ondelete='CASCADE')
            batch_op.drop_column('topic_id')
    except Exception:
        pass

    # 4. Modify problems table to repoint foreign key to roadmap_nodes
    try:
        with op.batch_alter_table('problems', schema=None) as batch_op:
            batch_op.drop_column('title')
            batch_op.drop_column('topic_id')
            batch_op.drop_column('difficulty')
            batch_op.drop_column('xp_reward')
            batch_op.create_foreign_key('fk_problems_roadmap_nodes', 'roadmap_nodes', ['id'], ['id'], ondelete='CASCADE')
    except Exception:
        pass

    # 5. Drop user_topic_progress
    try:
        op.drop_table('user_topic_progress')
    except Exception:
        pass

    # 6. Drop topics table
    try:
        op.drop_table('topics')
    except Exception:
        pass


def downgrade() -> None:
    pass
