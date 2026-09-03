"""create experiment_runs, experiment_models, experiment_results

Revision ID: aebdd300fef7
Revises: b330a482d650
Create Date: 2026-09-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'aebdd300fef7'
down_revision: Union[str, None] = 'b330a482d650'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # experiment_runs first - experiment_models/experiment_results FK into it.
    op.create_table(
        "experiment_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("source_model_id", sa.String(), nullable=False),
        sa.Column("n_sessions", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("n_items", sa.Integer(), nullable=False, server_default="164"),
        sa.Column("smooth_epsilon", sa.Float(), nullable=False, server_default="0.005"),
        sa.Column("status", sa.String(), nullable=False, server_default="created"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("sealed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revealed_at", sa.DateTime(timezone=True), nullable=True),
        # 'cancelled' added beyond the task's literal list so
        # DELETE /experiments/{id}'s soft-delete (status='cancelled') is a
        # legal value - the spec's own list omits it.
        sa.CheckConstraint(
            "status IN ('created','running','predicted','revealed','complete','cancelled')",
            name="ck_experiment_runs_status",
        ),
    )

    op.create_table(
        "experiment_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_id", sa.String(), nullable=False),
        sa.Column("model_label", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("log_file_path", sa.String(), nullable=True),
        sa.Column("fitted_model_path", sa.String(), nullable=True),
        sa.Column("ai_action_frequency", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="registered"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("role IN ('source','target')", name="ck_experiment_models_role"),
        sa.CheckConstraint(
            "status IN ('registered','ai_extracted','fitted','predicted','revealed')",
            name="ck_experiment_models_status",
        ),
    )
    op.create_index("ix_experiment_models_experiment_id", "experiment_models", ["experiment_id"], unique=False)

    op.create_table(
        "experiment_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_a_id", sa.String(), nullable=False),
        sa.Column("model_b_id", sa.String(), nullable=False),
        sa.Column("comparison_type", sa.String(), nullable=False),

        sa.Column("pred_Tr", sa.Float(), nullable=True),
        sa.Column("pred_Tr_std", sa.Float(), nullable=True),
        sa.Column("pred_HCL", sa.Float(), nullable=True),
        sa.Column("pred_HCL_std", sa.Float(), nullable=True),
        sa.Column("pred_EL", sa.Float(), nullable=True),
        sa.Column("pred_EL_std", sa.Float(), nullable=True),
        sa.Column("pred_F", sa.Float(), nullable=True),
        sa.Column("pred_F_std", sa.Float(), nullable=True),

        sa.Column("real_Tr", sa.Float(), nullable=True),
        sa.Column("real_HCL", sa.Float(), nullable=True),
        sa.Column("real_EL", sa.Float(), nullable=True),
        sa.Column("real_F", sa.Float(), nullable=True),

        sa.Column("err_Tr_pct", sa.Float(), nullable=True),
        sa.Column("err_HCL_pct", sa.Float(), nullable=True),
        sa.Column("err_EL_pct", sa.Float(), nullable=True),
        sa.Column("err_F_pct", sa.Float(), nullable=True),

        sa.Column("S_cross", sa.Float(), nullable=True),
        sa.Column("S_cross_per_action", postgresql.JSONB(astext_type=sa.Text()), nullable=True),

        sa.Column("h1_supported", sa.Boolean(), nullable=True),
        sa.Column("h2_supported", sa.Boolean(), nullable=True),
        sa.Column("h3_supported", sa.Boolean(), nullable=True),

        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),

        sa.CheckConstraint(
            "comparison_type IN ('predicted_vs_real','matrix_vs_matrix')",
            name="ck_experiment_results_comparison_type",
        ),
    )
    op.create_index("ix_experiment_results_experiment_id", "experiment_results", ["experiment_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_experiment_results_experiment_id", table_name="experiment_results")
    op.drop_table("experiment_results")
    op.drop_index("ix_experiment_models_experiment_id", table_name="experiment_models")
    op.drop_table("experiment_models")
    op.drop_table("experiment_runs")
