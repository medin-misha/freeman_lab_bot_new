"""
Доставка subscription-screen для menu-модуля.

Этот файл содержит отправку onboarding-экрана подписки, чтобы хендлеры
оставались тонкими и описывали только сценарные переходы.
"""

from __future__ import annotations

from aiogram.types import Message

from app.modules.menu_module.keyboards import get_subscription_keyboard
from app.modules.menu_module.messages import get_messages

_MESSAGES = get_messages()


async def send_subscription_prompt(message: Message) -> None:
    """Отправляет приветственный экран с кнопками подписки."""

    try:
        keyboard = get_subscription_keyboard()
    except ValueError:
        await message.answer(_MESSAGES["subscription_check_failed"])
        return

    await message.answer(_MESSAGES["subscription_welcome"], reply_markup=keyboard)

