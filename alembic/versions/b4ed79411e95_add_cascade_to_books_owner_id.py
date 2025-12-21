"""Add cascade to books owner_id

Revision ID: b4ed79411e95
Revises: 950b1f8d184e
Create Date: 2025-12-20 12:32:44.833472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4ed79411e95'
down_revision: Union[str, Sequence[str], None] = '950b1f8d184e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    pass


def downgrade():
    pass