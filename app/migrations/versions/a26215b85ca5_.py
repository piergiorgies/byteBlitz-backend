"""empty message

Revision ID: a26215b85ca5
Revises: 9bd649b34176, ce238251199b
Create Date: 2024-12-05 22:23:47.234803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a26215b85ca5'
down_revision: Union[str, None] = ('9bd649b34176', 'ce238251199b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
