"""Runtime-состояние модуля уведомлений о заявках на ядро."""

from __future__ import annotations

from aiogram import Bot

_notification_bot: Bot | None = None


async def startup_core_admin_runtime(bot: Bot) -> None:
    """Сохраняет bot instance для фоновых RMQ уведомлений."""

    global _notification_bot
    _notification_bot = bot


async def shutdown_core_admin_runtime() -> None:
    """Очищает bot instance модуля при остановке приложения."""

    global _notification_bot
    _notification_bot = None


def get_notification_bot() -> Bot:
    """Возвращает активный bot instance модуля."""

    if _notification_bot is None:
        raise RuntimeError("Core admin notification bot runtime is not initialized.")
    return _notification_bot
