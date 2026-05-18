"""add product model

Revision ID: b1c2f9a2d4e5
Revises: 6c4d6d9d0db8
Create Date: 2026-05-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b1c2f9a2d4e5"
down_revision: Union[str, Sequence[str], None] = "6c4d6d9d0db8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "product",
        sa.Column("product_code", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["telegramuser.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_product_code"), "product", ["product_code"], unique=False)
    op.create_index(op.f("ix_product_user_id"), "product", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_product_user_id"), table_name="product")
    op.drop_index(op.f("ix_product_product_code"), table_name="product")
    op.drop_table("product")
