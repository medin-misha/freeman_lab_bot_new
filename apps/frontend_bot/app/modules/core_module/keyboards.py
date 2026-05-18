"""Клавиатуры core-модуля."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from .config import core_settings
from .messages import get_messages

_MESSAGES = get_messages()


def get_core_keyboard() -> InlineKeyboardMarkup:
    """Возвращает inline-кнопку открытия mini app Ядра."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_MESSAGES["core_open_button"],
                    web_app=WebAppInfo(url=core_settings.core_url),
                )
            ]
        ]
    )
