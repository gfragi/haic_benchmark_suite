"""add raw_filename/derived_filename columns to logs

Revision ID: a1c7f4e9d2b3
Revises: 7e3a91b2c4d5
Create Date: 2026-06-19 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1c7f4e9d2b3'
down_revision: Union[str, None] = '7e3a91b2c4d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "ALTER TABLE logs ADD COLUMN IF NOT EXISTS raw_filename VARCHAR"
    ))
    conn.execute(sa.text(
        "ALTER TABLE logs ADD COLUMN IF NOT EXISTS derived_filename VARCHAR"
    ))


def downgrade() -> None:
    op.get_bind().execute(sa.text(
        "ALTER TABLE logs DROP COLUMN IF EXISTS raw_filename"
    ))
    op.get_bind().execute(sa.text(
        "ALTER TABLE logs DROP COLUMN IF EXISTS derived_filename"
    ))
