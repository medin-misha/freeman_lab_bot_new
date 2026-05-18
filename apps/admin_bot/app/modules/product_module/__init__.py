"""Модуль уведомлений о новых продуктовых заявках для admin_bot."""

from . import rmq_consumers as _rmq_consumers
from .handlers import router
from .runtime import get_notification_bot

__all__ = [
    "get_notification_bot",
    "router",
]

