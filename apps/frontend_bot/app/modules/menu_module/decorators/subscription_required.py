"""
Декоратор ограничения доступа по подписке на канал.

Декоратор использует общую сервисную функцию проверки подписки и поэтому
остаётся тонкой обёрткой, удобной для повторного применения в разных
хендлерах menu-модуля и будущих пользовательских модулей.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, cast

from aiogram.types import CallbackQuery, Message, TelegramObject

from app.modules.menu_module.messages import get_messages
from app.modules.menu_module.service import SubscriptionCheckError, is_user_subscribed

Handler = TypeVar("Handler", bound=Callable[..., Awaitable[Any]])


def subscription_required(handler: Handler) -> Handler:
    """Пускает хендлер дальше только если пользователь подписан на канал."""

    @wraps(handler)
    async def wrapper(event: TelegramObject, *args: Any, **kwargs: Any) -> Any:
        messages = get_messages()
        telegram_user = getattr(event, "from_user", None)
        if telegram_user is None:
            await _answer_event(event, messages["subscription_check_failed"])
            return None

        try:
            is_subscribed = await is_user_subscribed(event.bot, telegram_user.id)
        except (SubscriptionCheckError, ValueError):
            await _answer_event(event, messages["subscription_check_failed"])
            return None

        if not is_subscribed:
            await _answer_event(event, messages["subscription_still_missing"])
            return None

        return await handler(event, *args, **kwargs)

    return cast(Handler, wrapper)


async def _answer_event(event: TelegramObject, text: str) -> None:
    """Отвечает на update вне зависимости от его Telegram-типа."""

    if isinstance(event, Message):
        await event.answer(text)
        return

    if isinstance(event, CallbackQuery):
        await event.answer(text, show_alert=True)
        return

    answer = getattr(event, "answer", None)
    if callable(answer):
        await answer(text)
