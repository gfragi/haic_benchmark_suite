"""add question_position column to survey_question_sets

Revision ID: c9e2f6a1b4d7
Revises: b6d4e8f01a3c
Create Date: 2026-07-22 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c9e2f6a1b4d7'
down_revision: Union[str, None] = 'b6d4e8f01a3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "ALTER TABLE survey_question_sets ADD COLUMN IF NOT EXISTS question_position VARCHAR NOT NULL DEFAULT 'last'"
    ))


def downgrade() -> None:
    op.get_bind().execute(sa.text(
        "ALTER TABLE survey_question_sets DROP COLUMN IF EXISTS question_position"
    ))
