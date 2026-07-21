"""add minio_bucket source type to polled_log_sources

Revision ID: b6d4e8f01a3c
Revises: f3a8c1d92b7e
Create Date: 2026-07-22 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b6d4e8f01a3c'
down_revision: Union[str, None] = 'f3a8c1d92b7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "ALTER TABLE polled_log_sources ADD COLUMN IF NOT EXISTS source_type VARCHAR NOT NULL DEFAULT 'http_endpoint'"
    ))
    conn.execute(sa.text(
        "ALTER TABLE polled_log_sources ADD COLUMN IF NOT EXISTS minio_bucket VARCHAR"
    ))
    conn.execute(sa.text(
        "ALTER TABLE polled_log_sources ADD COLUMN IF NOT EXISTS minio_prefix VARCHAR"
    ))
    conn.execute(sa.text(
        "ALTER TABLE polled_log_sources ALTER COLUMN endpoint_url DROP NOT NULL"
    ))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE polled_log_sources DROP COLUMN IF EXISTS source_type"))
    conn.execute(sa.text("ALTER TABLE polled_log_sources DROP COLUMN IF EXISTS minio_bucket"))
    conn.execute(sa.text("ALTER TABLE polled_log_sources DROP COLUMN IF EXISTS minio_prefix"))
