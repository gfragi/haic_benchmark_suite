"""survey

Revision ID: 2b005c94ba11
Revises: adf24d090191
Create Date: 2025-04-11 23:25:05.392229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b005c94ba11'
down_revision: Union[str, None] = 'adf24d090191'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
