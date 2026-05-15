"""
Inline-клавиатуры menu-модуля.

Этот файл хранит только Telegram UI-конструкции, чтобы хендлеры занимались
сценарием, а не сборкой кнопок.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.modules.menu_module.config import menu_settings
from app.modules.menu_module.service import build_channel_url


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Возвращает inline-клавиатуру для сценария обязательной подписки."""

    channel_url = build_channel_url(menu_settings.channel)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подписаться", url=channel_url)],
            [InlineKeyboardButton(text="Я подписался(ась)", callback_data="menu:check_subscription")],
        ]
    )

