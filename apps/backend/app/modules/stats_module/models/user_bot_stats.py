from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules import Base, TimestampMixin

if TYPE_CHECKING:
    from app.modules.telegram_module import TelegramUser


class UserBotStats(Base, TimestampMixin):
    telegram_user_id: Mapped[int] = mapped_column(
        ForeignKey("telegramuser.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    channel_subscribe: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    received_methodology: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    received_methodology_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    core_application_submitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    core_application_submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    diagnostics_total: Mapped[int] = mapped_column(nullable=False, default=0)
    diagnostics_completed_total: Mapped[int] = mapped_column(nullable=False, default=0)
    last_diagnostic_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    review_link_clicked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    review_public_consent_given: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    telegram_user: Mapped["TelegramUser"] = relationship(lazy="selectin")

    def set_source(self, source: str | None) -> None:
        self.source = source

    def set_current_branch(self, current_branch: str | None) -> None:
        self.current_branch = current_branch

    def set_channel_subscribe(self, value: bool) -> None:
        self.channel_subscribe = value

    def mark_received_methodology(self, *, received: bool, at: datetime | None) -> None:
        self.received_methodology = received
        self.received_methodology_at = at if received else None

    def mark_review_link_clicked(self, value: bool) -> None:
        self.review_link_clicked = value

    def mark_review_public_consent_given(self, value: bool) -> None:
        self.review_public_consent_given = value

    def mark_core_application_submitted(self, *, submitted: bool, at: datetime | None) -> None:
        self.core_application_submitted = submitted
        self.core_application_submitted_at = at if submitted else None

    def set_diagnostics_totals(self, *, diagnostics_total: int, diagnostics_completed_total: int) -> None:
        self.diagnostics_total = diagnostics_total
        self.diagnostics_completed_total = diagnostics_completed_total

    def set_last_diagnostic_at(self, value: datetime | None) -> None:
        self.last_diagnostic_at = value
