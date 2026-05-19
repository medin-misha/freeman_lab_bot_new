"""add stats tables

Revision ID: 6f0d7f1f3eaa
Revises: be77a67bbd25
Create Date: 2026-05-19 18:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6f0d7f1f3eaa"
down_revision: Union[str, Sequence[str], None] = "be77a67bbd25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "userbotstats",
        sa.Column("telegram_user_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("current_branch", sa.String(length=255), nullable=True),
        sa.Column("channel_subscribe", sa.Boolean(), nullable=False),
        sa.Column("received_methodology", sa.Boolean(), nullable=False),
        sa.Column("received_methodology_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("core_application_submitted", sa.Boolean(), nullable=False),
        sa.Column("core_application_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("diagnostics_total", sa.Integer(), nullable=False),
        sa.Column("diagnostics_completed_total", sa.Integer(), nullable=False),
        sa.Column("last_diagnostic_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_link_clicked", sa.Boolean(), nullable=False),
        sa.Column("review_public_consent_given", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["telegram_user_id"], ["telegramuser.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_user_id"),
    )
    op.create_index(
        op.f("ix_userbotstats_telegram_user_id"),
        "userbotstats",
        ["telegram_user_id"],
        unique=True,
    )

    op.create_table(
        "userdiagnosticstats",
        sa.Column("telegram_user_id", sa.Integer(), nullable=False),
        sa.Column("diagnostic_code", sa.String(length=128), nullable=False),
        sa.Column("attempts_total", sa.Integer(), nullable=False),
        sa.Column("completed_total", sa.Integer(), nullable=False),
        sa.Column("last_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(length=32), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["telegram_user_id"], ["telegramuser.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "telegram_user_id",
            "diagnostic_code",
            name="uq_user_diagnostic_stats",
        ),
    )
    op.create_index(
        op.f("ix_userdiagnosticstats_diagnostic_code"),
        "userdiagnosticstats",
        ["diagnostic_code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_userdiagnosticstats_telegram_user_id"),
        "userdiagnosticstats",
        ["telegram_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_userdiagnosticstats_telegram_user_id"), table_name="userdiagnosticstats")
    op.drop_index(op.f("ix_userdiagnosticstats_diagnostic_code"), table_name="userdiagnosticstats")
    op.drop_table("userdiagnosticstats")

    op.drop_index(op.f("ix_userbotstats_telegram_user_id"), table_name="userbotstats")
    op.drop_table("userbotstats")
