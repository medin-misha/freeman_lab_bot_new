"""add invisible diagnostic model

Revision ID: 6c4d6d9d0db8
Revises: 30d2cc3e4364
Create Date: 2026-05-14 16:20:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6c4d6d9d0db8"
down_revision: Union[str, Sequence[str], None] = "30d2cc3e4364"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "invisiblediagnostic",
        sa.Column("diagnostic_run_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["diagnostic_run_id"],
            ["diagnosticrun.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_invisiblediagnostic_diagnostic_run_id"),
        "invisiblediagnostic",
        ["diagnostic_run_id"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_invisiblediagnostic_diagnostic_run_id"),
        table_name="invisiblediagnostic",
    )
    op.drop_table("invisiblediagnostic")
