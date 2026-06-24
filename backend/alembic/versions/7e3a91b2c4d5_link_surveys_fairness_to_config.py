"""link surveys and add pilot_tag/baseline_s to configurations

Revision ID: 7e3a91b2c4d5
Revises: 1e24e5ba30b8
Create Date: 2026-03-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7e3a91b2c4d5'
down_revision: Union[str, None] = '1e24e5ba30b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Add configuration_id FK to surveys (idempotent)
    conn.execute(sa.text(
        "ALTER TABLE surveys ADD COLUMN IF NOT EXISTS configuration_id INTEGER"
    ))
    conn.execute(sa.text("""
        DO $fk$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'surveys_configuration_id_fkey'
            ) THEN
                ALTER TABLE surveys
                    ADD CONSTRAINT surveys_configuration_id_fkey
                    FOREIGN KEY (configuration_id)
                    REFERENCES configurations(id)
                    ON DELETE SET NULL;
            END IF;
        END $fk$;
    """))

    # Add pilot_tag and baseline_s to configurations (idempotent)
    conn.execute(sa.text(
        "ALTER TABLE configurations ADD COLUMN IF NOT EXISTS pilot_tag VARCHAR"
    ))
    conn.execute(sa.text(
        "ALTER TABLE configurations ADD COLUMN IF NOT EXISTS baseline_s FLOAT"
    ))


def downgrade() -> None:
    op.get_bind().execute(sa.text(
        "ALTER TABLE surveys DROP COLUMN IF EXISTS configuration_id"
    ))
    op.get_bind().execute(sa.text(
        "ALTER TABLE configurations DROP COLUMN IF EXISTS pilot_tag"
    ))
    op.get_bind().execute(sa.text(
        "ALTER TABLE configurations DROP COLUMN IF EXISTS baseline_s"
    ))
