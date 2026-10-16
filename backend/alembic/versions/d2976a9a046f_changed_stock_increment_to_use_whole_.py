"""Changed stock increment to use_whole_foot_width

Revision ID: d2976a9a046f
Revises: 13188f512e61
Create Date: 2026-10-16 16:17:24.922827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2976a9a046f'
down_revision: Union[str, Sequence[str], None] = '13188f512e61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "service_options",
        sa.Column(
            "use_whole_foot_width",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.execute("""
        UPDATE service_options
        SET use_whole_foot_width =
            COALESCE(stock_increment > 0, FALSE)
    """)

    op.drop_column("service_options", "stock_increment")


def downgrade() -> None:
    op.add_column(
        "service_options",
        sa.Column(
            "stock_increment",
            sa.Float(),
            nullable=True,
        ),
    )

    op.execute("""
        UPDATE service_options
        SET stock_increment =
            CASE WHEN use_whole_foot_width THEN 1.0 ELSE 0.0 END
    """)

    op.drop_column("service_options", "use_whole_foot_width")
