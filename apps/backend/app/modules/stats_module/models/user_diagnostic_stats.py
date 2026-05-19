from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules import Base, TimestampMixin

if TYPE_CHECKING:
    from app.modules.telegram_module import TelegramUser


class UserDiagnosticStats(Base, TimestampMixin):
    __table_args__ = (
        UniqueConstraint("telegram_user_id", "diagnostic_code", name="uq_user_diagnostic_stats"),
    )

    telegram_user_id: Mapped[int] = mapped_column(
        ForeignKey("telegramuser.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    diagnostic_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    attempts_total: Mapped[int] = mapped_column(nullable=False, default=0)
    completed_total: Mapped[int] = mapped_column(nullable=False, default=0)
    last_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(32), nullable=True)

    telegram_user: Mapped["TelegramUser"] = relationship(lazy="selectin")

    def increment_attempts(self, delta: int = 1) -> None:
        self.attempts_total += delta

    def increment_completed(self, delta: int = 1) -> None:
        self.completed_total += delta

    def set_totals(self, *, attempts_total: int, completed_total: int) -> None:
        self.attempts_total = attempts_total
        self.completed_total = completed_total

    def set_last_started_at(self, at: datetime | None) -> None:
        self.last_started_at = at

    def set_last_completed_at(self, at: datetime | None) -> None:
        self.last_completed_at = at

    def set_last_status(self, status: str | None) -> None:
        self.last_status = status
