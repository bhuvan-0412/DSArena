"""add youtube and sequential progress to roadmap

Revision ID: a1b2c3d4e5f6
Revises: 2463fd29b9fe
Create Date: 2026-07-26 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '2463fd29b9fe'
branch_labels = None
depends_on = None

def upgrade():
    # Add YouTube & metadata columns to roadmap_nodes
    op.add_column('roadmap_nodes', sa.Column('youtube_url', sa.String(), nullable=True))
    op.add_column('roadmap_nodes', sa.Column('youtube_video_id', sa.String(), nullable=True))
    op.add_column('roadmap_nodes', sa.Column('thumbnail_url', sa.String(), nullable=True))
    op.add_column('roadmap_nodes', sa.Column('prerequisites', sa.JSON(), nullable=True))
    op.add_column('roadmap_nodes', sa.Column('metadata', sa.JSON(), nullable=True))

    # Add status and timestamps to user_node_progress
    op.add_column('user_node_progress', sa.Column('status', sa.String(), nullable=True, server_default='LOCKED'))
    op.add_column('user_node_progress', sa.Column('started_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('user_node_progress', 'started_at')
    op.drop_column('user_node_progress', 'status')
    op.drop_column('roadmap_nodes', 'metadata')
    op.drop_column('roadmap_nodes', 'prerequisites')
    op.drop_column('roadmap_nodes', 'thumbnail_url')
    op.drop_column('roadmap_nodes', 'youtube_video_id')
    op.drop_column('roadmap_nodes', 'youtube_url')
