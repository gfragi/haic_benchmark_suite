"""create survey_question_sets and schema_id on surveys

Revision ID: 033e6b4b44fe
Revises: 4b6a91f74968
Create Date: 2025-11-03 09:44:41.570014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '033e6b4b44fe'
down_revision: Union[str, None] = '4b6a91f74968'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "survey_question_sets",
        sa.Column("schema_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("pilot_tag", sa.String(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("questions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_sqs_pilot_active_ver", "survey_question_sets", ["pilot_tag", "active", "version"], unique=False)

    # if surveys.schema_id not added yet, add it now
    with op.batch_alter_table("surveys") as batch:
        batch.add_column(sa.Column("schema_id", postgresql.UUID(as_uuid=True), nullable=True))
        # optional FK to keep referential integrity (comment out if you don’t want it)
        # batch.create_foreign_key(
        #     "fk_surveys_schema",
        #     "survey_question_sets",
        #     ["schema_id"], ["schema_id"],
        #     ondelete="SET NULL",
        # )

def downgrade():
    with op.batch_alter_table("surveys") as batch:
        # batch.drop_constraint("fk_surveys_schema", type_="foreignkey")
        batch.drop_column("schema_id")
    op.drop_index("ix_sqs_pilot_active_ver", table_name="survey_question_sets")
    op.drop_table("survey_question_sets")
