"""empty message

Revision ID: a84a202cc1c1
Revises: 523294fab67e, 6b6e37b9d9bb
Create Date: 2025-02-24 22:35:40.306011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a84a202cc1c1'
down_revision: Union[str, None] = ('523294fab67e', '6b6e37b9d9bb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
