"""Клавиатуры модуля админ-панели."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from .config import admin_panel_settings
from .messages import get_messages

_MESSAGES = get_messages()


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Возвращает inline-кнопку открытия Mini App админ-панели."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_MESSAGES["admin_panel_button"],
                    web_app=WebAppInfo(url=admin_panel_settings.admin_url),
                )
            ]
        ]
    )
