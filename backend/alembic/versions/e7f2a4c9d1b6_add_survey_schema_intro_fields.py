"""add intro_title/intro_description columns to survey_question_sets

Revision ID: e7f2a4c9d1b6
Revises: d1a5e9c3f8b2
Create Date: 2026-09-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e7f2a4c9d1b6'
down_revision: Union[str, None] = 'd1a5e9c3f8b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "ALTER TABLE survey_question_sets ADD COLUMN IF NOT EXISTS intro_title VARCHAR"
    ))
    conn.execute(sa.text(
        "ALTER TABLE survey_question_sets ADD COLUMN IF NOT EXISTS intro_description VARCHAR"
    ))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "ALTER TABLE survey_question_sets DROP COLUMN IF EXISTS intro_description"
    ))
    conn.execute(sa.text(
        "ALTER TABLE survey_question_sets DROP COLUMN IF EXISTS intro_title"
    ))
