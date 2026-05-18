"""
Явный реестр модульных роутеров.

Все активные Telegram-модули подключаются здесь вручную, чтобы состав
приложения был прозрачен и легко отслеживался при отладке и развитии шаблона.
"""

from aiogram import Dispatcher

from app.modules.analysis_admin_module import router as analysis_admin_router
from app.modules.diagnostic_admin_module import router as diagnostic_admin_router
from app.modules.product_module import router as product_router
from app.modules.rmq_module.handlers import router as rmq_router
from app.modules.system.handlers import router as system_router


def register_routers(dispatcher: Dispatcher) -> None:
    """Подключает активные модульные роутеры к общему dispatcher."""

    dispatcher.include_router(system_router)
    dispatcher.include_router(analysis_admin_router)
    dispatcher.include_router(diagnostic_admin_router)
    dispatcher.include_router(product_router)
    dispatcher.include_router(rmq_router)
