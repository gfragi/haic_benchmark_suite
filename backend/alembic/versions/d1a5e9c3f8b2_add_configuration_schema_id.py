"""add schema_id column to configurations

Revision ID: d1a5e9c3f8b2
Revises: c9e2f6a1b4d7
Create Date: 2026-07-22 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1a5e9c3f8b2'
down_revision: Union[str, None] = 'c9e2f6a1b4d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(sa.text(
        "ALTER TABLE configurations ADD COLUMN IF NOT EXISTS schema_id VARCHAR"
    ))


def downgrade() -> None:
    op.get_bind().execute(sa.text(
        "ALTER TABLE configurations DROP COLUMN IF EXISTS schema_id"
    ))
