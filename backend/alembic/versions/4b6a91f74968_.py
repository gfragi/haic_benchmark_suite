"""empty message

Revision ID: 4b6a91f74968
Revises: 49d552833b91
Create Date: 2025-10-27 18:09:14.452653

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b6a91f74968'
down_revision: Union[str, None] = '49d552833b91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
