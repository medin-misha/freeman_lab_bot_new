from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.system import Base, TimestampMixin

if TYPE_CHECKING:
    from app.modules.file_module import File
    from app.modules.telegram_module import TelegramUser


class DiagnosticRun(Base, TimestampMixin):
    user_id: Mapped[int] = mapped_column(
        ForeignKey("telegramuser.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    diagnostic_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    voice_file_id: Mapped[int | None] = mapped_column(
        ForeignKey("file.id", ondelete="SET NULL"),
        nullable=True,
    )
    result_file_id: Mapped[int | None] = mapped_column(
        ForeignKey("file.id", ondelete="SET NULL"),
        nullable=True,
    )
    transcribation_file_id: Mapped[int | None] = mapped_column(
        ForeignKey("file.id", ondelete="SET NULL"),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tag: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["TelegramUser"] = relationship(lazy="selectin")
    voice_file: Mapped["File | None"] = relationship(
        foreign_keys=[voice_file_id],
        lazy="selectin",
    )
    result_file: Mapped["File | None"] = relationship(
        foreign_keys=[result_file_id],
        lazy="selectin",
    )
    transcribation_file: Mapped["File | None"] = relationship(
        foreign_keys=[transcribation_file_id],
        lazy="selectin",
    )
