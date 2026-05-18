from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules import Base, TimestampMixin

if TYPE_CHECKING:
    from app.modules.telegram_module import TelegramUser


class CoreRequest(Base, TimestampMixin):
    activity: Mapped[str | None] = mapped_column(Text, nullable=True)
    request: Mapped[str | None] = mapped_column(Text, nullable=True)
    priorities: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    motivation: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulties: Mapped[str | None] = mapped_column(Text, nullable=True)
    readiness: Mapped[str | None] = mapped_column(String(255), nullable=True)
    weekly_time: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rules: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("telegramuser.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["TelegramUser"] = relationship(lazy="selectin")
