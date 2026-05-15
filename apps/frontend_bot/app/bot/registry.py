"""
Явный реестр модульных роутеров.

Все активные Telegram-модули подключаются здесь вручную, чтобы состав
приложения был прозрачен и легко отслеживался при отладке и развитии шаблона.
"""

from aiogram import Dispatcher

from app.modules.default_diagnostic_module.handlers import router as default_diagnostic_router
from app.modules.guide_module.handlers import router as guide_router
from app.modules.invisible_diagnostic_module.handlers import router as invisible_diagnostic_router
from app.modules.menu_module.handlers import router as menu_router
from app.modules.rmq_module.handlers import router as rmq_router
from app.modules.system.handlers import router as system_router


def register_routers(dispatcher: Dispatcher) -> None:
    """Подключает активные модульные роутеры к общему dispatcher."""

    dispatcher.include_router(system_router)
    dispatcher.include_router(rmq_router)
    dispatcher.include_router(menu_router)
    dispatcher.include_router(default_diagnostic_router)
    dispatcher.include_router(invisible_diagnostic_router)
    dispatcher.include_router(guide_router)
