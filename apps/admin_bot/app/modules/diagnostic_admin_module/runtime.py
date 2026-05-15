"""Runtime-состояние модуля уведомлений о диагностике."""

from __future__ import annotations

from aiogram import Bot

from .client import (
    shutdown_diagnostic_admin_backend_client,
    startup_diagnostic_admin_backend_client,
)

_notification_bot: Bot | None = None


async def startup_diagnostic_admin_runtime(bot: Bot) -> None:
    """Сохраняет bot instance для фоновых RMQ уведомлений."""

    global _notification_bot
    await startup_diagnostic_admin_backend_client()
    _notification_bot = bot


async def shutdown_diagnostic_admin_runtime() -> None:
    """Очищает bot instance модуля при остановке приложения."""

    global _notification_bot
    _notification_bot = None
    await shutdown_diagnostic_admin_backend_client()


def get_notification_bot() -> Bot:
    """Возвращает активный bot instance модуля."""

    if _notification_bot is None:
        raise RuntimeError("Diagnostic admin bot runtime is not initialized.")
    return _notification_bot
