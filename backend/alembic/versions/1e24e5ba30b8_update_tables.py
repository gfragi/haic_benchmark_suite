"""update tables

Revision ID: 1e24e5ba30b8
Revises: 033e6b4b44fe
Create Date: 2025-12-16 13:41:13.817869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1e24e5ba30b8'
down_revision: Union[str, None] = '033e6b4b44fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _exists(table_name: str) -> bool:
    result = op.get_bind().execute(
        sa.text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.tables"
            "  WHERE table_schema = 'public' AND table_name = :t"
            ")"
        ),
        {"t": table_name},
    )
    return result.scalar()


def _index_exists(index_name: str) -> bool:
    result = op.get_bind().execute(
        sa.text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM pg_indexes"
            "  WHERE schemaname = 'public' AND indexname = :i"
            ")"
        ),
        {"i": index_name},
    )
    return result.scalar()


def upgrade() -> None:
    if not _exists('metric_definitions'):
        op.create_table('metric_definitions',
        sa.Column('metric_id', sa.Text(), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('formula_tex', sa.Text(), nullable=False),
        sa.Column('required_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('example_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('metric_id')
        )
    if not _index_exists('ix_metric_definitions_metric_id'):
        op.create_index(op.f('ix_metric_definitions_metric_id'), 'metric_definitions', ['metric_id'], unique=False)

    if not _exists('metric_groups'):
        op.create_table('metric_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if not _index_exists('ix_metric_groups_id'):
        op.create_index(op.f('ix_metric_groups_id'), 'metric_groups', ['id'], unique=False)
    if not _index_exists('ix_metric_groups_name'):
        op.create_index(op.f('ix_metric_groups_name'), 'metric_groups', ['name'], unique=False)

    if not _exists('survey_question_sets'):
        op.create_table('survey_question_sets',
        sa.Column('schema_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('pilot_tag', sa.String(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('questions', sa.JSON(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('schema_id')
        )
    if not _index_exists('ix_survey_question_sets_pilot_tag'):
        op.create_index(op.f('ix_survey_question_sets_pilot_tag'), 'survey_question_sets', ['pilot_tag'], unique=False)

    if not _exists('surveys'):
        op.create_table('surveys',
        sa.Column('survey_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('pilot_tag', sa.String(), nullable=False),
        sa.Column('app_version', sa.String(), nullable=True),
        sa.Column('ai_model_version', sa.String(), nullable=True),
        sa.Column('schema_id', sa.UUID(), nullable=True),
        sa.Column('tam_sus_responses', sa.JSON(), nullable=True),
        sa.Column('ethics_responses', sa.JSON(), nullable=True),
        sa.Column('domain_specific', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('survey_id')
        )

    if not _exists('logs'):
        op.create_table('logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('ai_model_version', sa.String(), nullable=True),
        sa.Column('app_version', sa.String(), nullable=True),
        sa.Column('start_time', sa.String(), nullable=True),
        sa.Column('end_time', sa.String(), nullable=True),
        sa.Column('interaction_data', sa.JSON(), nullable=True),
        sa.Column('retrain_events', sa.JSON(), nullable=True),
        sa.Column('performance_infrastructure', sa.JSON(), nullable=True),
        sa.Column('performance_logs', sa.JSON(), nullable=True),
        sa.Column('ai_model_data', sa.JSON(), nullable=True),
        sa.Column('raw_filename', sa.String(), nullable=True),
        sa.Column('derived_filename', sa.String(), nullable=True),
        sa.Column('configuration_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.get_bind().execute(sa.text("""
        DO $fk$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'logs_configuration_id_fkey'
            ) THEN
                ALTER TABLE logs ADD CONSTRAINT logs_configuration_id_fkey
                    FOREIGN KEY (configuration_id) REFERENCES configurations(id);
            END IF;
        END $fk$;
    """))
    # Ensure raw_filename/derived_filename exist on pre-existing logs tables
    op.get_bind().execute(sa.text(
        "ALTER TABLE logs ADD COLUMN IF NOT EXISTS raw_filename VARCHAR"
    ))
    op.get_bind().execute(sa.text(
        "ALTER TABLE logs ADD COLUMN IF NOT EXISTS derived_filename VARCHAR"
    ))

    if not _index_exists('ix_logs_id'):
        op.create_index(op.f('ix_logs_id'), 'logs', ['id'], unique=False)
    if not _index_exists('ix_logs_session_id'):
        op.create_index(op.f('ix_logs_session_id'), 'logs', ['session_id'], unique=False)
    if not _index_exists('ix_logs_user_id'):
        op.create_index(op.f('ix_logs_user_id'), 'logs', ['user_id'], unique=False)

    if not _exists('metrics'):
        op.create_table('metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.get_bind().execute(sa.text("""
        DO $fk$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'metrics_group_id_fkey'
            ) THEN
                ALTER TABLE metrics ADD CONSTRAINT metrics_group_id_fkey
                    FOREIGN KEY (group_id) REFERENCES metric_groups(id);
            END IF;
        END $fk$;
    """))
    if not _index_exists('ix_metrics_id'):
        op.create_index(op.f('ix_metrics_id'), 'metrics', ['id'], unique=False)
    if not _index_exists('ix_metrics_name'):
        op.create_index(op.f('ix_metrics_name'), 'metrics', ['name'], unique=False)

    if not _exists('results'):
        op.create_table('results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('configuration_id', sa.Integer(), nullable=False),
        sa.Column('evaluation_date', sa.DateTime(), nullable=False),
        sa.Column('result_minio_path', sa.String(), nullable=False),
        sa.Column('app_version', sa.String(), nullable=True),
        sa.Column('ai_model_version', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    op.get_bind().execute(sa.text("""
        DO $fk$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'results_configuration_id_fkey'
            ) THEN
                ALTER TABLE results ADD CONSTRAINT results_configuration_id_fkey
                    FOREIGN KEY (configuration_id) REFERENCES configurations(id) ON DELETE CASCADE;
            END IF;
        END $fk$;
    """))
    if not _index_exists('ix_results_id'):
        op.create_index(op.f('ix_results_id'), 'results', ['id'], unique=False)

    if not _index_exists('ix_configurations_application_name'):
        op.create_index(op.f('ix_configurations_application_name'), 'configurations', ['application_name'], unique=False)
    if not _index_exists('ix_configurations_id'):
        op.create_index(op.f('ix_configurations_id'), 'configurations', ['id'], unique=False)


def downgrade() -> None:
    if _index_exists('ix_configurations_id'):
        op.drop_index(op.f('ix_configurations_id'), table_name='configurations')
    if _index_exists('ix_configurations_application_name'):
        op.drop_index(op.f('ix_configurations_application_name'), table_name='configurations')
    if _index_exists('ix_results_id'):
        op.drop_index(op.f('ix_results_id'), table_name='results')
    if _exists('results'):
        op.drop_table('results')
    if _index_exists('ix_metrics_name'):
        op.drop_index(op.f('ix_metrics_name'), table_name='metrics')
    if _index_exists('ix_metrics_id'):
        op.drop_index(op.f('ix_metrics_id'), table_name='metrics')
    if _exists('metrics'):
        op.drop_table('metrics')
    if _index_exists('ix_logs_user_id'):
        op.drop_index(op.f('ix_logs_user_id'), table_name='logs')
    if _index_exists('ix_logs_session_id'):
        op.drop_index(op.f('ix_logs_session_id'), table_name='logs')
    if _index_exists('ix_logs_id'):
        op.drop_index(op.f('ix_logs_id'), table_name='logs')
    if _exists('logs'):
        op.drop_table('logs')
    if _exists('surveys'):
        op.drop_table('surveys')
    if _index_exists('ix_survey_question_sets_pilot_tag'):
        op.drop_index(op.f('ix_survey_question_sets_pilot_tag'), table_name='survey_question_sets')
    if _exists('survey_question_sets'):
        op.drop_table('survey_question_sets')
    if _index_exists('ix_metric_groups_name'):
        op.drop_index(op.f('ix_metric_groups_name'), table_name='metric_groups')
    if _index_exists('ix_metric_groups_id'):
        op.drop_index(op.f('ix_metric_groups_id'), table_name='metric_groups')
    if _exists('metric_groups'):
        op.drop_table('metric_groups')
    if _index_exists('ix_metric_definitions_metric_id'):
        op.drop_index(op.f('ix_metric_definitions_metric_id'), table_name='metric_definitions')
    if _exists('metric_definitions'):
        op.drop_table('metric_definitions')
