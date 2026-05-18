"""add core request model

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-05-17 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "corerequest",
        sa.Column("activity", sa.Text(), nullable=True),
        sa.Column("request", sa.Text(), nullable=True),
        sa.Column("priorities", sa.JSON(), nullable=True),
        sa.Column("motivation", sa.Text(), nullable=True),
        sa.Column("difficulties", sa.Text(), nullable=True),
        sa.Column("readiness", sa.String(length=255), nullable=True),
        sa.Column("weekly_time", sa.String(length=255), nullable=True),
        sa.Column("rules", sa.String(length=255), nullable=True),
        sa.Column("payment", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["telegramuser.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_corerequest_user_id"),
        "corerequest",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_corerequest_user_id"), table_name="corerequest")
    op.drop_table("corerequest")
