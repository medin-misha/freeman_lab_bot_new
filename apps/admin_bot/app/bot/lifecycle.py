"""
Lifecycle-хуки Telegram-приложения.

Файл отвечает за действия на startup/shutdown всего процесса: очистку webhook,
инициализацию системных runtime-ресурсов и корректное закрытие сетевых
подключений при остановке.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError

from app.core import MainSettings
from app.modules.analysis_admin_module.runtime import (
    shutdown_analysis_admin_runtime,
    startup_analysis_admin_runtime,
)
from app.modules.core_admin_module.runtime import (
    shutdown_core_admin_runtime,
    startup_core_admin_runtime,
)
from app.modules.diagnostic_admin_module.runtime import (
    shutdown_diagnostic_admin_runtime,
    startup_diagnostic_admin_runtime,
)
from app.modules.product_module.runtime import (
    shutdown_product_runtime,
    startup_product_runtime,
)
from app.modules.rmq_module.runtime import shutdown_rmq_runtime, startup_rmq_runtime
from app.modules.system.runtime import shutdown_system_runtime, startup_system_runtime

logger = logging.getLogger(__name__)
_TELEGRAM_STARTUP_ATTEMPTS = 10
_TELEGRAM_STARTUP_DELAY_SECONDS = 1.0


async def _delete_webhook_with_retry(bot: Bot, *, drop_pending_updates: bool) -> None:
    """Повторяет delete_webhook, если local Bot API ещё не успел подняться."""

    for attempt in range(1, _TELEGRAM_STARTUP_ATTEMPTS + 1):
        try:
            await bot.delete_webhook(drop_pending_updates=drop_pending_updates)
            return
        except TelegramNetworkError:
            if attempt == _TELEGRAM_STARTUP_ATTEMPTS:
                raise
            logger.warning(
                "Telegram Bot API is not ready yet, retrying delete_webhook "
                "(attempt %s/%s)",
                attempt,
                _TELEGRAM_STARTUP_ATTEMPTS,
            )
            await asyncio.sleep(_TELEGRAM_STARTUP_DELAY_SECONDS)


def register_lifecycle(dispatcher: Dispatcher, settings: MainSettings) -> None:
    """Регистрирует startup/shutdown callbacks для всего runtime бота."""

    async def on_startup(bot: Bot) -> None:
        """Подготавливает Telegram и системный runtime к старту polling."""

        await _delete_webhook_with_retry(
            bot,
            drop_pending_updates=settings.drop_pending_updates,
        )
        await startup_system_runtime(settings)
        await startup_analysis_admin_runtime(bot)
        await startup_core_admin_runtime(bot)
        await startup_diagnostic_admin_runtime(bot)
        await startup_product_runtime(bot)
        await startup_rmq_runtime(settings)
        logger.info("Bot %s started in polling mode", settings.project_name)

    async def on_shutdown(bot: Bot) -> None:
        """Корректно закрывает runtime-ресурсы при остановке процесса."""

        logger.info("Bot %s is shutting down", settings.project_name)
        await shutdown_rmq_runtime()
        await shutdown_product_runtime()
        await shutdown_diagnostic_admin_runtime()
        await shutdown_core_admin_runtime()
        await shutdown_analysis_admin_runtime()
        await shutdown_system_runtime()
        await bot.session.close()

    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)
