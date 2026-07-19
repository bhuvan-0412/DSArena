"""Use_ProblemStatus_Enum

Revision ID: 8e7400666bdf
Revises: a8e0cfc86299
Create Date: 2026-07-20 02:18:44.100902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e7400666bdf'
down_revision: Union[str, None] = 'a8e0cfc86299'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE user_progress SET status = 'ATTEMPTED' WHERE status = 'Attempted'")
    op.execute("UPDATE user_progress SET status = 'SOLVED' WHERE status = 'Solved'")
    op.execute("UPDATE user_progress SET status = 'MASTERED' WHERE status = 'Mastered'")
    op.execute("UPDATE user_progress SET status = 'REVISION_DUE' WHERE status = 'Revision Due'")


def downgrade() -> None:
    op.execute("UPDATE user_progress SET status = 'Attempted' WHERE status = 'ATTEMPTED'")
    op.execute("UPDATE user_progress SET status = 'Solved' WHERE status = 'SOLVED'")
    op.execute("UPDATE user_progress SET status = 'Mastered' WHERE status = 'MASTERED'")
    op.execute("UPDATE user_progress SET status = 'Revision Due' WHERE status = 'REVISION_DUE'")
