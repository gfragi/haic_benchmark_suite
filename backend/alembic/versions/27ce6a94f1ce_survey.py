"""survey

Revision ID: 27ce6a94f1ce
Revises: 2b005c94ba11
Create Date: 2025-04-11 23:41:53.433757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27ce6a94f1ce'
down_revision: Union[str, None] = '2b005c94ba11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
