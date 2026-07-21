"""add polled_log_sources table

Revision ID: f3a8c1d92b7e
Revises: a1c7f4e9d2b3
Create Date: 2026-07-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f3a8c1d92b7e'
down_revision: Union[str, None] = 'a1c7f4e9d2b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "polled_log_sources",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("configuration_id", sa.Integer,
                  sa.ForeignKey("configurations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("endpoint_url", sa.String, nullable=False),
        sa.Column("auth_header", sa.String, nullable=True),
        sa.Column("poll_interval_seconds", sa.Integer, nullable=False, server_default="300"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_polled_at", sa.DateTime, nullable=True),
        sa.Column("last_success_at", sa.DateTime, nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("polled_log_sources")
