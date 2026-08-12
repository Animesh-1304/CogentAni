"""add product timestamps and modernize models

Revision ID: 526815e09a3b
Revises:
Create Date: 2026-08-12 04:00:11.841371
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "526815e09a3b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "product",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.add_column(
        "product",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.alter_column(
        "product",
        "created_at",
        server_default=None,
    )

    op.alter_column(
        "product",
        "updated_at",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("product", "updated_at")
    op.drop_column("product", "created_at")