"""Модуль уведомлений о новых диагностиках для admin_bot."""

from . import client as _client
from . import rmq_consumers as _rmq_consumers
from .handlers import router
from .runtime import get_notification_bot

__all__ = [
    "get_notification_bot",
    "router",
]
