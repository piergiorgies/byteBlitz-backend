"""empty message

Revision ID: 637f16ad0a53
Revises: 0284eb3a6e47, 62c27d68f2b9
Create Date: 2024-10-09 20:19:01.806595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '637f16ad0a53'
down_revision: Union[str, None] = ('0284eb3a6e47', '62c27d68f2b9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
