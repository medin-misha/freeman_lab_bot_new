"""
Модуль админ-панели.

Этот файл содержит обработчик команды /admin, которая предоставляет доступ
к Telegram Mini App админ-панели для доверенных администраторов.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core import settings
from .keyboards import get_admin_panel_keyboard
from .messages import get_messages

router = Router(name="admin_panel_module")
_MESSAGES = get_messages()


@router.message(Command("admin"))
async def open_admin_panel(message: Message) -> None:
    """Проверяет доступ администратора и отправляет кнопку запуска панели."""

    if message.from_user is None:
        return

    if message.from_user.id not in settings.admins_chat_ids:
        await message.answer(_MESSAGES["admin_access_denied"])
        return

    await message.answer(
        _MESSAGES["admin_panel_greeting"],
        reply_markup=get_admin_panel_keyboard(),
        parse_mode="Markdown",
    )
