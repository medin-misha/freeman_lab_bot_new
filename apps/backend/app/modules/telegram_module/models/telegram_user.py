from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules import Base, TimestampMixin

if TYPE_CHECKING:
    from .user_profile import UserProfile
    from app.modules.stats_module.models.user_bot_stats import UserBotStats
    from app.modules.base_diagnostic_module.models.diagnostic_run import DiagnosticRun
    from app.modules.core_request_module.models.core_request import CoreRequest


class TelegramUser(Base, TimestampMixin):
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_blocket_bot: Mapped[bool] = mapped_column(default=False)
    language_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    user_profile: Mapped["UserProfile | None"] = relationship(
        back_populates="telegram_user",
        uselist=False,
        lazy="selectin",
        passive_deletes="all",
    )
    bot_stats: Mapped["UserBotStats | None"] = relationship(
        uselist=False,
        lazy="selectin",
        foreign_keys="[UserBotStats.telegram_user_id]",
    )
    diagnostic_runs: Mapped[list["DiagnosticRun"]] = relationship(
        lazy="selectin",
        foreign_keys="[DiagnosticRun.user_id]",
    )
    core_request: Mapped["CoreRequest | None"] = relationship(
        uselist=False,
        lazy="selectin",
        foreign_keys="[CoreRequest.user_id]",
    )

