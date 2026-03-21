"""Initial

Revision ID: 49d552833b91
Revises: 
Create Date: 2025-06-28 22:15:26.467722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '49d552833b91'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _exists(table_name: str) -> bool:
    """Check via information_schema — reliable inside Alembic transaction context."""
    result = op.get_bind().execute(
        sa.text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.tables"
            "  WHERE table_schema = 'public'"
            "  AND table_name = :t"
            ")"
        ),
        {"t": table_name},
    )
    return result.scalar()


def upgrade() -> None:
    if not _exists('configurations'):
        op.create_table(
            'configurations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('application_name', sa.String(), nullable=True),
            sa.Column('ai_model_name', sa.String(), nullable=True),
            sa.Column('ai_model_type', sa.String(), nullable=True),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('metrics', sa.JSON(), nullable=True),
            sa.Column('evaluation_date', sa.DateTime(), nullable=False),
            sa.Column('config_type', sa.String(), nullable=True),
            sa.Column('evaluation_status', sa.String(), nullable=True),
            sa.Column('minio_path', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )

    if not _exists('metric_definitions'):
        op.create_table(
            'metric_definitions',
            sa.Column('metric_id', sa.Text(), nullable=False),
            sa.Column('display_name', sa.Text(), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('formula_tex', sa.Text(), nullable=False),
            sa.Column('required_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column('example_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint('metric_id'),
        )
        op.create_index(
            op.f('ix_metric_definitions_metric_id'),
            'metric_definitions', ['metric_id'], unique=False,
        )

    if not _exists('surveys'):
        op.create_table(
            'surveys',
            sa.Column('survey_id', sa.UUID(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('timestamp', sa.DateTime(), nullable=False),
            sa.Column('pilot_tag', sa.String(), nullable=False),
            sa.Column('app_version', sa.String(), nullable=True),
            sa.Column('ai_model_version', sa.String(), nullable=True),
            sa.Column('tam_sus_responses', sa.JSON(), nullable=True),
            sa.Column('ethics_responses', sa.JSON(), nullable=True),
            sa.Column('domain_specific', sa.JSON(), nullable=True),
            sa.PrimaryKeyConstraint('survey_id'),
        )


def downgrade() -> None:
    if _exists('configurations'):
        op.drop_table('configurations')

    if _exists('surveys'):
        op.drop_table('surveys')

    if _exists('metric_definitions'):
        op.drop_index(
            op.f('ix_metric_definitions_metric_id'),
            table_name='metric_definitions',
        )
        op.drop_table('metric_definitions')