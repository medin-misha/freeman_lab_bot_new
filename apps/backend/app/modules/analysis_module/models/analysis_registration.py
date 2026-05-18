from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.system import Base, TimestampMixin

if TYPE_CHECKING:
    from app.modules.telegram_module import TelegramUser


class AnalysisRegistration(Base, TimestampMixin):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("telegramuser.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["TelegramUser"] = relationship(lazy="selectin")
