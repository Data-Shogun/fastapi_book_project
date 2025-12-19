"""Add role column to the User model

Revision ID: 950b1f8d184e
Revises: dda687e43905
Create Date: 2025-12-19 20:24:52.925759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '950b1f8d184e'
down_revision: Union[str, Sequence[str], None] = 'dda687e43905'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
