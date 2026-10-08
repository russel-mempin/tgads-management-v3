"""Added created_by and updated_by to misc_sales

Revision ID: 58dc02c8aa83
Revises: 9f17dd03853e
Create Date: 2026-10-08 19:53:19.974868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58dc02c8aa83'
down_revision: Union[str, Sequence[str], None] = '9f17dd03853e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
